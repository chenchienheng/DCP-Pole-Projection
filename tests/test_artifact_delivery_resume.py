"""Regression coverage for saved-check and interrupted CLI delivery recovery."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from dcp_kernel.artifact_receiver import ArtifactDeliveryContract, ArtifactExpectation
from tools.verify_artifact_delivery import main


class ArtifactDeliveryResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.source = self.home / "source"
        self.received = self.home / "received"
        self.source.mkdir()
        self.received.mkdir()
        self.data = b"bound delivery bytes\n"
        for root in (self.source, self.received):
            (root / "report.txt").write_bytes(self.data)
        contract = ArtifactDeliveryContract(
            "resume-delivery", "source", "revision-1", "receiver",
            (ArtifactExpectation("report.txt", hashlib.sha256(self.data).hexdigest(), len(self.data)),),
            ("user-requested verification",),
        )
        self.contract = self.home / "contract.json"
        self.contract.write_text(json.dumps(asdict(contract)), encoding="utf-8")
        self.pending = self.home / "pending.json"
        self.result = self.home / "received.json"
        self.prepare = ["prepare", "--contract", str(self.contract),
                        "--root", str(self.source), "--output", str(self.pending)]
        self.receive = ["receive", "--contract", str(self.contract),
                        "--root", str(self.received), "--pending", str(self.pending),
                        "--output", str(self.result)]

    def invoke(self, args):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return main(args)

    def test_explicit_prepare_resume_keeps_existing_pending_bytes_and_mtime(self):
        self.assertEqual(self.invoke(self.prepare), 0)
        old = self.pending.read_bytes(), self.pending.stat().st_mtime_ns
        self.assertEqual(self.invoke(self.prepare + ["--resume"]), 0)
        self.assertEqual((self.pending.read_bytes(), self.pending.stat().st_mtime_ns), old)

    def test_explicit_receive_resume_reuses_only_identical_output(self):
        self.assertEqual(self.invoke(self.prepare), 0)
        self.assertEqual(self.invoke(self.receive), 0)
        old = self.result.read_bytes(), self.result.stat().st_mtime_ns
        self.assertEqual(self.invoke(self.receive), 2)  # original create-only behavior
        self.assertEqual(self.invoke(self.receive + ["--resume"]), 0)
        self.assertEqual((self.result.read_bytes(), self.result.stat().st_mtime_ns), old)
        self.assertFalse(list(self.home.glob(".delivery-*")))

    def test_saved_success_envelope_is_a_valid_reentry_not_a_receipt_shortcut(self):
        self.invoke(self.prepare)
        self.assertEqual(self.invoke(self.receive), 0)
        args = self.receive.copy()
        args[args.index("--pending") + 1] = str(self.result)
        again = self.home / "again.json"
        args[-1] = str(again)
        self.assertEqual(self.invoke(args), 0)
        self.assertEqual(again.read_bytes(), self.result.read_bytes())
        (self.received / "report.txt").write_bytes(b"X" + self.data[1:])
        args[-1] = str(self.home / "rejected.json")
        self.assertEqual(self.invoke(args), 3)
        self.assertEqual(json.loads((self.home / "rejected.json").read_text())["result"]["decision"], "HOLD")

    def test_saved_hold_can_resume_after_missing_file_is_received(self):
        self.invoke(self.prepare)
        (self.received / "report.txt").unlink()
        self.assertEqual(self.invoke(self.receive), 3)
        original_hold = self.result.read_bytes()
        (self.received / "report.txt").write_bytes(self.data)
        args = self.receive.copy()
        args[args.index("--pending") + 1] = str(self.result)
        args[-1] = str(self.home / "recovered.json")
        self.assertEqual(self.invoke(args), 0)
        self.assertEqual(self.result.read_bytes(), original_hold)
        self.assertEqual((self.source / "report.txt").read_bytes(), self.data)

    def test_different_existing_output_is_not_overwritten_by_resume(self):
        self.invoke(self.prepare)
        self.result.write_text('{"different":"prior evidence"}\n')
        old = self.result.read_bytes()
        self.assertEqual(self.invoke(self.receive + ["--resume"]), 2)
        self.assertEqual(self.result.read_bytes(), old)
        self.assertFalse(list(self.home.glob(".delivery-*")))

    def test_input_overlap_is_blocked_even_during_resume(self):
        self.invoke(self.prepare)
        args = self.receive.copy()
        args[-1] = str(self.received / "report.txt")
        self.assertEqual(self.invoke(args + ["--resume"]), 2)
        self.assertEqual((self.received / "report.txt").read_bytes(), self.data)

    def test_unrecognized_saved_check_scope_or_fields_are_rejected(self):
        self.invoke(self.prepare)
        self.invoke(self.receive)
        saved = json.loads(self.result.read_text())
        for update in ({"scope": "SEMANTIC_APPROVED"}, {"approval": True}):
            with self.subTest(update=update):
                malformed = self.home / "malformed.json"
                malformed.write_text(json.dumps(dict(saved, **update)))
                args = self.receive.copy()
                args[args.index("--pending") + 1] = str(malformed)
                args[-1] = str(self.home / "must-not-exist.json")
                self.assertEqual(self.invoke(args), 2)
                self.assertFalse(Path(args[-1]).exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_existing_output_symlink_is_not_followed_on_resume(self):
        self.invoke(self.prepare)
        self.invoke(self.receive)
        other = self.home / "other.json"
        other.write_bytes(self.result.read_bytes())
        self.result.unlink()
        self.result.symlink_to(other)
        old = other.read_bytes(), other.stat().st_mtime_ns
        self.assertEqual(self.invoke(self.receive + ["--resume"]), 2)
        self.assertEqual((other.read_bytes(), other.stat().st_mtime_ns), old)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_existing_fifo_output_never_blocks_resume(self):
        self.invoke(self.prepare)
        os.mkfifo(self.result)
        self.assertEqual(self.invoke(self.receive + ["--resume"]), 2)

    def test_fresh_process_cli_loads_saved_check_and_preserves_manual_evidence(self):
        root = Path(__file__).resolve().parents[1]
        def run(args):
            env = dict(os.environ)
            env.pop("PYTHONPATH", None)
            return subprocess.run([sys.executable, "-m", "tools.verify_artifact_delivery", *args],
                                  cwd=root, env=env, text=True, capture_output=True, timeout=10)
        self.assertEqual(run(self.prepare).returncode, 0)
        pending_bytes = self.pending.read_bytes()
        self.assertEqual(run(self.receive).returncode, 0)
        args = self.receive.copy()
        args[args.index("--pending") + 1] = str(self.result)
        again = self.home / "fresh.json"
        args[-1] = str(again)
        proc = run(args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(run(args + ["--resume"]).returncode, 0)
        result = json.loads(again.read_text())["result"]
        self.assertEqual(result["return_closure"]["manual_interventions"],
                         ["user-requested verification"])
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(self.pending.read_bytes(), pending_bytes)
        self.assertEqual((self.received / "report.txt").read_bytes(), self.data)


if __name__ == "__main__":
    unittest.main()
