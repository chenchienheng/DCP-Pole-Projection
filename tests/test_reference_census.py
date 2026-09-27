from __future__ import annotations

import unittest
import json
from pathlib import Path
import tempfile

from dcp_kernel.reference_census import (
    DependencySignal,
    ReferenceClass,
    classify_dependency_signal,
    classify_reference,
    has_proven_live_caller,
    has_rebuild_relevant_reference,
    has_unknown_hold,
    has_wake_routing_relevant_reference,
    scan_text_map,
)


class ReferenceCensusTests(unittest.TestCase):
    def test_current_surface_reference_is_live(self) -> None:
        self.assertEqual(
            classify_reference(
                "CURRENT-SURFACE-MANIFEST.json", "01_runtime-spine",
                current_reader_paths=("CURRENT-SURFACE-MANIFEST.json",)),
            ReferenceClass.LIVE_CALLER,
        )

    def test_operational_kernel_reference_is_live(self) -> None:
        self.assertEqual(
            classify_reference("dcp_kernel/platform.py", "03_field-governance"),
            ReferenceClass.LIVE_CALLER,
        )

    def test_audit_tool_reference_is_not_live_caller(self) -> None:
        self.assertEqual(
            classify_reference("tools/census_legacy_references.py", "03_field-governance"),
            ReferenceClass.AUDIT_REFERENCE,
        )

    def test_audit_fixture_reference_is_not_live_caller(self) -> None:
        self.assertEqual(
            classify_reference("fixtures/repository/03-field-governance-review.json", "03_field-governance"),
            ReferenceClass.AUDIT_REFERENCE,
        )

    def test_implementation_manifest_is_audit_reference(self) -> None:
        self.assertEqual(
            classify_reference("contracts/implementation-manifest.json", "04_adapter-layer"),
            ReferenceClass.AUDIT_REFERENCE,
        )

    def test_audit_reference_cannot_create_rebuild_or_wake_dependency(self) -> None:
        signal = classify_dependency_signal(
            caller_path="tools/census_legacy_references.py",
            classification=ReferenceClass.AUDIT_REFERENCE,
            excerpt="rebuild wake 01_runtime-spine/",
        )
        self.assertEqual(signal, DependencySignal.NONE)

    def test_legacy_family_self_reference_is_not_live_caller(self) -> None:
        self.assertEqual(
            classify_reference("04_adapter-layer/README.md", "04_adapter-layer"),
            ReferenceClass.SELF_REFERENCE,
        )

    def test_historical_index_reference_is_lineage_pointer(self) -> None:
        self.assertEqual(
            classify_reference("REPOSITORY_CORPUS_INDEX.md", "04_adapter-layer"),
            ReferenceClass.LINEAGE_POINTER,
        )

    def test_unknown_surface_stays_hold(self) -> None:
        self.assertEqual(
            classify_reference("misc/unclassified-map.md", "03_field-governance"),
            ReferenceClass.UNKNOWN_HOLD,
        )

    def test_search_hit_is_not_implicitly_live(self) -> None:
        files = {
            "REPOSITORY_CORPUS_INDEX.md": "legacy path: 01_runtime-spine/",
            "CURRENT-SURFACE-MANIFEST.json": "no legacy reference here",
        }
        observations = scan_text_map(files, ("01_runtime-spine",))
        self.assertFalse(has_proven_live_caller(observations, "01_runtime-spine"))
        self.assertFalse(has_unknown_hold(observations, "01_runtime-spine"))
        self.assertFalse(has_rebuild_relevant_reference(observations, "01_runtime-spine"))
        self.assertFalse(has_wake_routing_relevant_reference(observations, "01_runtime-spine"))

    def test_audit_only_mentions_do_not_block_scanned_text_withdrawal(self) -> None:
        files = {
            "tools/census_legacy_references.py": "FAMILIES = ('01_runtime-spine/',)",
            "contracts/implementation-manifest.json": '"01_runtime-spine/": ["successor"]',
            "fixtures/repository/family-caller-rebuild-census-observations.json": '"01_runtime-spine/"',
        }
        observations = scan_text_map(files, ("01_runtime-spine",))
        self.assertFalse(has_proven_live_caller(observations, "01_runtime-spine"))
        self.assertFalse(has_unknown_hold(observations, "01_runtime-spine"))
        self.assertFalse(has_rebuild_relevant_reference(observations, "01_runtime-spine"))
        self.assertFalse(has_wake_routing_relevant_reference(observations, "01_runtime-spine"))

    def test_unknown_reference_blocks_clean_audit_and_dependency_withdrawal(self) -> None:
        files = {"misc/map.md": "03_field-governance/CO_FIELD_DEPENDENCY_MODEL_v0_1.md"}
        observations = scan_text_map(files, ("03_field-governance",))
        self.assertTrue(has_unknown_hold(observations, "03_field-governance"))
        self.assertTrue(has_rebuild_relevant_reference(observations, "03_field-governance"))
        self.assertTrue(has_wake_routing_relevant_reference(observations, "03_field-governance"))

    def test_live_rebuild_reference_is_flagged_for_bounded_review(self) -> None:
        files = {
            "dcp_kernel/platform.py": "legacy fallback rebuild from 03_field-governance/RECOMPOSITION_ENGINE_v0_1.md"
        }
        observations = scan_text_map(files, ("03_field-governance",))
        self.assertTrue(has_proven_live_caller(observations, "03_field-governance"))
        self.assertTrue(has_rebuild_relevant_reference(observations, "03_field-governance"))
        self.assertEqual(observations[0].dependency_signal, DependencySignal.REBUILD_RELEVANT)

    def test_live_wake_reference_is_flagged_for_bounded_review(self) -> None:
        signal = classify_dependency_signal(
            caller_path="CURRENT-SURFACE-MANIFEST.json",
            classification=ReferenceClass.LIVE_CALLER,
            excerpt="reader routing points to 04_adapter-layer/activation_order.md",
        )
        self.assertEqual(signal, DependencySignal.WAKE_ROUTING_RELEVANT)

    def test_lineage_pointer_does_not_create_rebuild_or_wake_dependency(self) -> None:
        signal = classify_dependency_signal(
            caller_path="REPOSITORY_CORPUS_INDEX.md",
            classification=ReferenceClass.LINEAGE_POINTER,
            excerpt="rebuild history 01_runtime-spine/window_linking_logic_01_07.md",
        )
        self.assertEqual(signal, DependencySignal.NONE)


    def test_census_implementation_is_audit_not_live_caller(self) -> None:
        self.assertEqual(
            classify_reference("dcp_kernel/reference_census.py", "01_runtime-spine"),
            ReferenceClass.AUDIT_REFERENCE,
        )

    def test_legacy_current_filename_without_basis_stays_unknown(self) -> None:
        self.assertEqual(
            classify_reference("LIFECYCLE_DEPENDENCY_CHAIN_KERNEL.md", "01_runtime-spine"),
            ReferenceClass.UNKNOWN_HOLD,
        )

    def test_new_reader_is_recognized_from_explicit_basis(self) -> None:
        self.assertEqual(
            classify_reference("new/reader.md", "01_runtime-spine",
                               current_reader_paths=("new/reader.md",)),
            ReferenceClass.LIVE_CALLER,
        )

    def test_noncanonical_caller_cannot_be_normalized_into_reader(self) -> None:
        for caller in ("../README.md", "./README.md", "/README.md"):
            with self.subTest(caller=caller):
                self.assertEqual(
                    classify_reference(caller, "01_runtime-spine",
                                       current_reader_paths=("README.md",)),
                    ReferenceClass.UNKNOWN_HOLD,
                )

    def test_explicit_basis_iterator_is_reused_for_all_references(self) -> None:
        rows = scan_text_map(
            {"one.md": "01_runtime-spine/", "two.md": "01_runtime-spine/"},
            ("01_runtime-spine",), current_reader_paths=iter(("one.md", "two.md")),
        )
        self.assertTrue(all(row.classification is ReferenceClass.LIVE_CALLER for row in rows))

    def test_invalid_basis_is_not_silently_accepted(self) -> None:
        with self.assertRaises((TypeError, ValueError)):
            scan_text_map({"README.md": "01_runtime-spine/"},
                          ("01_runtime-spine",), current_reader_paths="README.md")


class CensusReaderIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "reader.md").write_text("01_runtime-spine/ entry", encoding="utf-8")
        self.manifest_path = self.root / "CURRENT-SURFACE-MANIFEST.json"
        self.manifest_path.write_text(
            json.dumps({"reader_priority": ["reader.md"]}), encoding="utf-8")

    def payload(self):
        from tools.census_legacy_references import build_payload
        return build_payload(self.root)

    def test_real_caller_uses_shared_parser_and_explicit_reader(self) -> None:
        payload = self.payload()
        self.assertEqual(payload["reader_basis"]["status"],
                         "LOCAL_DECLARATION_VALID_NOT_NATIVE_ADMISSION")
        self.assertEqual(payload["summary"]["01_runtime-spine"]["live_caller_count"], 1)
        self.assertFalse(payload["summary"]["01_runtime-spine"]["reclaim_ready"])

    def test_missing_basis_never_claims_absence_or_withdrawal(self) -> None:
        self.manifest_path.unlink()
        payload = self.payload()
        self.assertEqual(payload["reader_basis"]["status"], "UNRESOLVED_NO_READER_ELIGIBILITY")
        for summary in payload["summary"].values():
            for key in ("caller_absence_on_scanned_text_surface",
                        "rebuild_withdrawal_candidate_on_scanned_text_surface",
                        "wake_routing_withdrawal_candidate_on_scanned_text_surface",
                        "reclaim_ready"):
                self.assertFalse(summary[key], key)

    def test_duplicate_manifest_keys_do_not_choose_a_reader(self) -> None:
        self.manifest_path.write_text(
            '{"reader_priority":["reader.md"],"reader_priority":["reader.md"]}',
            encoding="utf-8")
        payload = self.payload()
        self.assertEqual(payload["reader_basis"]["status"], "UNRESOLVED_NO_READER_ELIGIBILITY")
        self.assertEqual(payload["summary"]["01_runtime-spine"]["live_caller_count"], 0)
        self.assertEqual(payload["summary"]["01_runtime-spine"]["unknown_hold_count"], 1)

    def test_snapshot_is_reproducible_and_tracks_changed_source(self) -> None:
        first = self.payload()["source_snapshot"]
        second = self.payload()["source_snapshot"]
        self.assertEqual(first, second)
        (self.root / "reader.md").write_text("changed source", encoding="utf-8")
        third = self.payload()["source_snapshot"]
        self.assertEqual(first["file_count"], third["file_count"])
        self.assertNotEqual(first["manifest_of_hashes_sha256"], third["manifest_of_hashes_sha256"])

    def test_census_inventory_does_not_create_twelve_live_dependencies(self) -> None:
        from tools.census_legacy_references import FAMILIES
        (self.root / "reader.md").write_text("no legacy use", encoding="utf-8")
        module = self.root / "dcp_kernel" / "reference_census.py"
        module.parent.mkdir()
        module.write_text("\n".join(f'"{family}/"' for family in FAMILIES), encoding="utf-8")
        payload = self.payload()
        self.assertEqual(len(payload["observations"]), len(FAMILIES))
        for summary in payload["summary"].values():
            self.assertEqual(summary["audit_reference_count"], 1)
            self.assertEqual(summary["live_caller_count"], 0)
            self.assertFalse(summary["reclaim_ready"])


if __name__ == "__main__":
    unittest.main()
