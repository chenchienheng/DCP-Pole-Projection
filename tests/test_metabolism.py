from __future__ import annotations

import unittest
import json
import tempfile
import hashlib
from pathlib import Path

from dcp_kernel.metabolism import (
    ArtifactRole,
    NameRisk,
    ProposedDisposition,
    assess_artifact,
    assess_paths,
)


class RepositoryMetabolismTests(unittest.TestCase):
    def test_markdown_engine_name_does_not_gain_executable_status(self) -> None:
        item = assess_artifact(
            "03_field-governance/RECOMPOSITION_ENGINE_v0_1.md"
        )
        self.assertEqual(item.role, ArtifactRole.DESCRIPTIVE)
        self.assertIn(
            NameRisk.MATURITY_IMPLICATION,
            item.name_risks,
        )
        self.assertEqual(
            item.proposed_disposition,
            ProposedDisposition.SUCCESSOR_COVERAGE_REVIEW,
        )
        self.assertFalse(item.destructive_action_authorized)

    def test_commander_and_registry_names_are_authority_risks(self) -> None:
        commander = assess_artifact(
            "03_field-governance/COMMANDER_CARD_v0_1.md"
        )
        registry = assess_artifact(
            "SCHEDULING_EFFECT_REGISTER.md"
        )
        self.assertIn(
            NameRisk.AUTHORITY_IMPLICATION,
            commander.name_risks,
        )
        self.assertIn(
            NameRisk.REGISTRY_TRUTH,
            registry.name_risks,
        )

    def test_code_schema_test_and_fixture_have_distinct_roles(self) -> None:
        self.assertEqual(
            assess_artifact("dcp_kernel/platform.py").role,
            ArtifactRole.EXECUTABLE_CANDIDATE,
        )
        self.assertEqual(
            assess_artifact("contracts/reentry.schema.json").role,
            ArtifactRole.MACHINE_CONTRACT,
        )
        self.assertEqual(
            assess_artifact("tests/test_kernel.py").role,
            ArtifactRole.TEST_EVIDENCE,
        )
        self.assertEqual(
            assess_artifact(
                "fixtures/gui-lu/mobility-envelope-intrusion.json"
            ).role,
            ArtifactRole.FIXTURE_EVIDENCE,
        )

    def test_archive_is_evidence_only_and_not_normal_wake(self) -> None:
        item = assess_artifact("archive/legacy-seed/README.md")
        self.assertEqual(
            item.role,
            ArtifactRole.HISTORICAL_LINEAGE,
        )
        self.assertEqual(
            item.proposed_disposition,
            ProposedDisposition.EVIDENCE_ONLY,
        )
        self.assertFalse(item.normal_reader_eligible)

    def test_current_projection_list_is_explicit_not_name_inferred(self) -> None:
        current = assess_artifact(
            "CURRENT-SURFACE-MANIFEST.json",
            current_reader_paths=["CURRENT-SURFACE-MANIFEST.json"],
        )
        similarly_named = assess_artifact(
            "OLD-CURRENT-MASTER.md"
        )
        self.assertEqual(
            current.role,
            ArtifactRole.CURRENT_PROJECTION,
        )
        self.assertEqual(
            similarly_named.role,
            ArtifactRole.DESCRIPTIVE,
        )
        self.assertNotEqual(
            similarly_named.proposed_disposition,
            ProposedDisposition.KEEP_CURRENT_PROJECTION,
        )


    def test_old_current_filenames_without_basis_grant_nothing(self):
        for path in ("README.md", "CURRENT-SURFACE-MANIFEST.json", "STATUS.md",
                     "PUBLIC-SURFACE-POLICY.md", "LIFECYCLE_DEPENDENCY_CHAIN_KERNEL.md"):
            with self.subTest(path=path):
                self.assertFalse(assess_artifact(path).normal_reader_eligible)

    def test_missing_legacy_kernel_is_not_a_current_reader(self):
        item = assess_artifact("LIFECYCLE_DEPENDENCY_CHAIN_KERNEL.md",
                               current_reader_paths=["README.md"])
        self.assertEqual(item.role, ArtifactRole.DESCRIPTIVE)
        self.assertFalse(item.normal_reader_eligible)

    def test_newly_declared_filename_can_be_a_reader(self):
        item = assess_artifact("FAILURE-EVOLUTION-POLICY.md",
                               current_reader_paths=["FAILURE-EVOLUTION-POLICY.md"])
        self.assertTrue(item.normal_reader_eligible)
        self.assertFalse(item.destructive_action_authorized)
        self.assertIn("NOT_NATIVE_ADMISSION", item.claim_ceiling)

    def test_reader_basis_is_reused_for_a_one_shot_iterator(self):
        rows = assess_paths(["a.md", "b.md"],
                            current_reader_paths=(x for x in ["a.md", "b.md"]))
        self.assertTrue(all(x.normal_reader_eligible for x in rows))

    def test_no_substring_membership_from_string_input(self):
        for invalid in ("README.md", b"README.md", [None], [True]):
            with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                assess_artifact("README.md", current_reader_paths=invalid)

    def test_reader_paths_reject_escape_and_ambiguous_paths(self):
        for invalid in ("../x", "/tmp/x", "a/../x", "a\\x", "https://x", "", "./a", "a//b"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                assess_artifact("README.md", current_reader_paths=[invalid])


class LocalManifestReaderBasisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "entry.md").write_text("entry", encoding="utf-8")

    def load(self, content=None):
        from tools.scan_repository_metabolism import load_reader_basis
        path = Path("CURRENT-SURFACE-MANIFEST.json")
        if content is not None:
            (self.root / path).write_text(content, encoding="utf-8")
        return load_reader_basis(self.root, path)

    def test_local_reader_declaration_and_hash_are_bound(self):
        text = json.dumps({"reader_priority": ["entry.md"]})
        paths, meta = self.load(text)
        self.assertEqual(paths, frozenset(["entry.md"]))
        self.assertEqual(meta["sha256"], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(meta["status"], "LOCAL_DECLARATION_VALID_NOT_NATIVE_ADMISSION")

    def test_absent_manifest_does_not_use_old_filenames(self):
        paths, meta = self.load()
        self.assertFalse(paths)
        self.assertEqual(meta["status"], "UNRESOLVED_NO_READER_ELIGIBILITY")

    def test_malformed_and_wrong_shape_manifests_fail_closed(self):
        for text in ("{", "[]", "{}", '{"reader_priority":"entry.md"}',
                     '{"reader_priority":[true]}', '{"reader_priority":[]}'):
            with self.subTest(text=text):
                paths, meta = self.load(text)
                self.assertFalse(paths)
                self.assertEqual(meta["status"], "UNRESOLVED_NO_READER_ELIGIBILITY")

    def test_duplicate_json_keys_or_reader_paths_fail_closed(self):
        for text in ('{"reader_priority":[],"reader_priority":["entry.md"]}',
                     '{"reader_priority":["entry.md","entry.md"]}'):
            with self.subTest(text=text):
                self.assertFalse(self.load(text)[0])

    def test_missing_declared_target_cannot_gain_reader_eligibility(self):
        self.assertFalse(self.load('{"reader_priority":["absent.md"]}')[0])

    def test_external_manifest_path_and_target_symlink_fail_closed(self):
        from tools.scan_repository_metabolism import load_reader_basis
        with tempfile.TemporaryDirectory() as directory:
            external = Path(directory) / "outside.json"
            external.write_text('{"reader_priority":["entry.md"]}', encoding="utf-8")
            self.assertFalse(load_reader_basis(self.root, external)[0])
            (self.root / "outside.json").symlink_to(external)
            self.assertFalse(self.load('{"reader_priority":["outside.json"]}')[0])


if __name__ == "__main__":
    unittest.main()
