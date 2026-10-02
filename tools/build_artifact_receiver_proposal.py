"""Export the existing byte receiver as an inactive, portable skill proposal.

No OpenClaw installation, Gateway call, model call, or live-skill write occurs.
An independently acquired source archive and its expected revision/hash are inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

MAX_RECEIPT_BYTES = 64 * 1024
MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_PAYLOAD_BYTES = 16 * 1024 * 1024
MAX_MEMBERS = 2000
NAME = "xuanling-artifact-delivery"
SOURCE_REPOSITORY = "chenchienheng/DCP-Pole-Projection"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def _json(raw: bytes):
    def bad_constant(value):
        raise ValueError("NON_FINITE_JSON")
    result = json.loads(raw, object_pairs_hook=_unique, parse_constant=bad_constant)
    if not isinstance(result, dict):
        raise ValueError("RECEIPT_OBJECT_REQUIRED")
    return result


def _path(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if (not name or "\\" in name or "\x00" in name or p.is_absolute()
            or any(part in ("", ".", "..") for part in name.rstrip("/").split("/"))
            or p.as_posix() != name.rstrip("/")):
        raise ValueError("UNSAFE_ARCHIVE_PATH")
    return p


def build_proposal(source_archive: Path, source_receipt: Path, output: Path,
                   expected_checkout: str, expected_archive_sha256: str) -> dict:
    """Build a new directory, not a registered/applied Workshop proposal.

    The expected values must come from trusted acquisition. Matching a supplied
    digest establishes byte binding, not provider authentication or approval.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", expected_checkout):
        raise ValueError("EXACT_CHECKOUT_REQUIRED")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_archive_sha256):
        raise ValueError("EXPECTED_SOURCE_HASH_REQUIRED")
    if output.exists() or output.is_symlink():
        raise ValueError("OUTPUT_EXISTS")
    if source_archive.is_symlink() or source_receipt.is_symlink():
        raise ValueError("SOURCE_SYMLINK_REJECTED")
    if not source_archive.is_file() or not source_receipt.is_file():
        raise ValueError("REGULAR_SOURCE_FILES_REQUIRED")
    if source_archive.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("SOURCE_ARCHIVE_TOO_LARGE")
    raw = source_archive.read_bytes()
    if len(raw) > MAX_ARCHIVE_BYTES or _sha(raw) != expected_archive_sha256:
        raise ValueError("SOURCE_ARCHIVE_HASH_MISMATCH")
    if source_receipt.stat().st_size > MAX_RECEIPT_BYTES:
        raise ValueError("RECEIPT_SIZE_LIMIT")
    receipt_raw = source_receipt.read_bytes()
    if len(receipt_raw) > MAX_RECEIPT_BYTES:
        raise ValueError("RECEIPT_SIZE_LIMIT")
    receipt = _json(receipt_raw)
    if (receipt.get("checkout") != expected_checkout
            or receipt.get("sha256") != expected_archive_sha256
            or type(receipt.get("size_bytes")) is not int
            or receipt["size_bytes"] != len(raw)
            or receipt.get("scope") != "TRACKED_SOURCE_CHECKOUT_NOT_RELEASE_APPROVAL"):
        raise ValueError("SOURCE_RECEIPT_BINDING_MISMATCH")
    # Reopen the bytes already checked, never the potentially changed input path.
    from io import BytesIO
    sources: dict[str, bytes] = {}
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBERS:
            raise ValueError("SOURCE_MEMBER_LIMIT")
        seen: set[str] = set()
        selected_size = 0
        for item in infos:
            path = _path(item.filename)
            key = path.as_posix()
            if key in seen:
                raise ValueError("DUPLICATE_ARCHIVE_PATH")
            seen.add(key)
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("SOURCE_SYMLINK_REJECTED")
            wanted = ((path.parts[0] == "dcp_kernel" and path.suffix == ".py")
                      or key in ("tools/verify_artifact_delivery.py", "README.md"))
            if item.is_dir() or not wanted:
                continue
            if any(part.startswith(".") for part in path.parts):
                raise ValueError("HIDDEN_PAYLOAD_PATH")
            mode = item.external_attr >> 16
            if mode & 0o111:
                raise ValueError("EXECUTABLE_PAYLOAD_MODE_REJECTED")
            selected_size += item.file_size
            if selected_size > MAX_PAYLOAD_BYTES:
                raise ValueError("PAYLOAD_SIZE_LIMIT")
            content = archive.read(item)
            content.decode("utf-8", errors="strict")
            if b"\x00" in content:
                raise ValueError("PAYLOAD_NULL_BYTE")
            sources[key] = content
    required = {"dcp_kernel/__init__.py", "dcp_kernel/artifact_receiver.py",
                "dcp_kernel/substrate_host.py", "tools/verify_artifact_delivery.py", "README.md"}
    if not required.issubset(sources):
        raise ValueError("REQUIRED_SOURCE_MISSING")
    payload = {"scripts/" + key: value for key, value in sources.items() if key != "README.md"}
    payload["references/source-readme.md"] = sources["README.md"]
    payload["scripts/tools/__init__.py"] = b'"""Packaged CLI namespace; upstream CLI bytes are unchanged."""\n'
    payload["scripts/verify_delivery.py"] = b'''"""Explicit local invocation only; no service or auto-install."""\nfrom pathlib import Path\nimport sys\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nfrom tools.verify_artifact_delivery import main\nif __name__ == "__main__":\n    raise SystemExit(main())\n'''
    payload["PROPOSAL.md"] = (f'''---
name: "{NAME}"
description: "Verify named file deliveries and resume saved checks without uploading or replaying completed actions."
status: proposal
version: "v1"
---

# Artifact delivery verification

This is a proposed procedure, not an installed capability or an approval to act.
Use it only for a named file-integrity task, inside the operator's authorized file
scope. It does not certify the document's meaning, safety, engineering validity,
identity authority, or another person's acceptance.

Resolve the same Need and the exact source, revision and receiver. Obtain expected
sizes and SHA256 values from the approved source record, not arbitrary received
bytes. Preserve human intervention and source provenance in the contract.

Run the bundled, unchanged receiver using Python 3.11+ on a supported POSIX host:

```sh
python -I {{baseDir}}/scripts/verify_delivery.py prepare --contract expected.json --root ./source --output pending.json
python -I {{baseDir}}/scripts/verify_delivery.py receive --contract expected.json --root ./received --pending pending.json --output checked.json
```

A prepare exit 0 is still pending. Receive exit 0 accepts byte verification only;
3 is an unresolved check; 2 is invalid input or an I/O error. Inspect the result,
not only the exit code. Existing outputs are protected by default. After a lost
reply, use the saved result, fresh file reads and `--resume`; do not upload or run
the original action again. A previous checked.json can be `--pending` input. To
reuse an identical existing output, use its saved predecessor as input and add
`--resume`; never make `--output` the same file as `--pending`. Keep an earlier
HOLD result; write a new result after its specific missing file arrives.

The bundled source is fixed at {expected_checkout}. New source requires a new
proposal revision and review, not silent replacement in a running session.
Read references/operation.md before first use. Do not execute scripts received
inside the files being checked. Do not install software, grant permissions,
change schedules, write a live skill, or expose private inputs from this task.
''').encode()
    payload["references/operation.md"] = b'''# Scope and host admission

Input contract: delivery_id, source_id, source_revision, receiver, artifacts.
Each artifact has path, sha256 and size_bytes; manual_interventions records
operator assistance. Use the exact source-owned version and lawful file roots.

The receiver checks regular files twice using directory-relative no-follow opens.
It does not make an atomic multi-file snapshot or authenticate a remote account.
The supplied expected digest is not a signature. Preserve the host's path and
execution policy; do not widen access merely to make a check pass.

This directory is an export payload, not an OpenClaw proposal record. On an
already authorized host, import through its documented Skill Workshop path:
openclaw skills workshop propose-create --name xuanling-artifact-delivery --description "Verify named file deliveries and resume saved checks without replay." --proposal-dir ./proposal --agent EXACT_AGENT --json
Resolve EXACT_AGENT from the intended operator-owned workspace; do not default
across tenants. This command is documentation, not executed by the exporter.
Review the exact proposal id/revision/support files and host scanner output.
No apply is requested or executed here. A file named PROPOSAL.md is not a hard
sandbox: direct script execution must still require appropriate host authority.

OpenClaw approvalPolicy=pending and autonomous.mode=propose are configuration
candidates for operator-reviewed work, not settings applied by this package.
Upstream defaults must not be mistaken for a universal human approval gate.
Skill Workshop only writes workspace skills, not existing plugin-owned skills.
Unrelated clients/companies require separately qualified security boundaries;
shared-agent creator labels or sidebar filters do not isolate their authority.

Procedure rollback: use the same Workshop proposal history and stored baseline
on the authorized host. Never overwrite an independently changed live target.
This export does not register, apply, reject, quarantine or curate any skill.
'''
    payload["references/upstream-methods.md"] = b'''# Source-bound method uptake

Reviewed documentation: OpenClaw release family v2026.8.1 and living documentation
retrieved 2026-09-29 Asia/Taipei. The Workshop page labels itself Status: proposal;
its present documentation is not proof of execution on a particular host/version.
No upstream implementation source is vendored in this package.

https://docs.openclaw.ai/tools/skill-workshop
Reuse proposal/support-file review, exact revision checks, and rollback metadata.
Apply policy is host-dependent; agent lifecycle actions do not always prompt.
Do not port its age-based autocapture curation as NFN retirement authority.

https://docs.openclaw.ai/concepts/session-attachment
Use canonical session resolution under a specific Gateway origin; a changed client
must not clone the same task or borrow another origin's credentials.

https://docs.openclaw.ai/concepts/session-state
Coalesced notices/cursors are useful for affected-only catch-up. historyGap needs
resynchronization. Its log is best-effort, not transactional CDC or global proof.

https://docs.openclaw.ai/concepts/multi-user
Shared-agent ownership/presence is coordination, not tenant security isolation.

https://docs.openclaw.ai/releases/2026.8.2
Settled tool work can finish its human reply without replaying completed actions.
That recovery is useful but does not verify every external channel delivery.
'''
    source_map = [{"source_path": key, "sha256": _sha(value), "size_bytes": len(value)}
                  for key, value in sorted(sources.items())]
    manifest = {
        "name": NAME, "state": "PREPARED_NOT_IMPORTED_OR_APPLIED",
        "source_repository": SOURCE_REPOSITORY, "source_checkout": expected_checkout,
        "source_archive_sha256": expected_archive_sha256,
        "source_scope": receipt["scope"], "source_files": source_map,
        "payload_files": [{"path": key, "sha256": _sha(value), "size_bytes": len(value)}
                          for key, value in sorted(payload.items())],
        "host_import_tested": False, "host_apply_requested": False,
        "network_install": False, "runtime_service_deployed": False,
        "claim": "EXPORTED_PROCEDURE_AND_FIXED_EXISTING_RECEIVER_NOT_PLATFORM_RUNTIME",
    }
    payload["references/source-manifest.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    # Create-only output. Failure leaves a clearly incomplete export, never an
    # active SKILL.md. Callers retain/inspect it rather than auto-delete history.
    output.mkdir(parents=False, exist_ok=False)
    for key, content in sorted(payload.items()):
        path = output / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
        path.chmod(0o644)
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--expected-checkout", required=True)
    parser.add_argument("--expected-archive-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_proposal(args.source_archive, args.source_receipt, args.output,
                                args.expected_checkout, args.expected_archive_sha256)
        print(json.dumps({"output": str(args.output), "state": result["state"],
                          "source_files": len(result["source_files"]),
                          "payload_files": len(result["payload_files"]) + 1}, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, zipfile.BadZipFile) as exc:
        print(f"PROPOSAL_EXPORT_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
