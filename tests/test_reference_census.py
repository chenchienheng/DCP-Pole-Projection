from __future__ import annotations

import unittest
import json
from pathlib import Path
import tempfile
import contextlib
import io
import shutil
import sys
from unittest import mock

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




class CensusSnapshotBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.outer = Path(self.temp.name)
        self.root = self.outer / "repo"
        self.root.mkdir()
        (self.root / "reader.md").write_text("03_field-governance/ historical mention\n", encoding="utf-8")
        (self.root / "CURRENT-SURFACE-MANIFEST.json").write_text(
            json.dumps({"reader_priority": ["reader.md"]}), encoding="utf-8")

    def assert_no_negative_claim(self, payload) -> None:
        for summary in payload["summary"].values():
            for key in ("caller_absence_on_scanned_text_surface",
                        "rebuild_withdrawal_candidate_on_scanned_text_surface",
                        "wake_routing_withdrawal_candidate_on_scanned_text_surface",
                        "reclaim_ready"):
                self.assertFalse(summary[key], key)

    def test_parent_names_cannot_hide_selected_repository(self) -> None:
        from tools.census_legacy_references import SKIP_DIRS, build_payload
        expected = build_payload(self.root)
        for ancestor in sorted(SKIP_DIRS):
            with self.subTest(ancestor=ancestor):
                relocated = self.outer / ancestor / "copy"
                shutil.copytree(self.root, relocated)
                actual = build_payload(relocated)
                self.assertEqual(expected, actual)

    def test_declared_reader_inside_excluded_directory_cannot_prove_absence(self) -> None:
        from tools.census_legacy_references import build_payload
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts" / "reader.md").write_text("01_runtime-spine/", encoding="utf-8")
        (self.root / "CURRENT-SURFACE-MANIFEST.json").write_text(
            json.dumps({"reader_priority": ["artifacts/reader.md"]}), encoding="utf-8")
        payload = build_payload(self.root)
        self.assertEqual(payload["source_snapshot"]["missing_declared_readers"], ["artifacts/reader.md"])
        self.assert_no_negative_claim(payload)

    def test_non_text_declared_reader_is_reported_not_treated_as_scanned(self) -> None:
        from tools.census_legacy_references import build_payload
        (self.root / "reader.bin").write_bytes(b"01_runtime-spine/")
        (self.root / "CURRENT-SURFACE-MANIFEST.json").write_text(
            json.dumps({"reader_priority": ["reader.bin"]}), encoding="utf-8")
        payload = build_payload(self.root)
        self.assertEqual(payload["source_snapshot"]["missing_declared_readers"], ["reader.bin"])
        self.assert_no_negative_claim(payload)

    def test_symlink_file_never_imports_outside_content(self) -> None:
        from tools.census_legacy_references import build_payload
        sentinel = "SYNTHETIC_OUTSIDE_CONTENT 01_runtime-spine/"
        outside = self.outer / "outside.md"
        outside.write_text(sentinel, encoding="utf-8")
        (self.root / "linked.md").symlink_to(outside)
        payload = build_payload(self.root)
        self.assertNotIn(sentinel, json.dumps(payload))
        self.assertNotIn(str(outside), json.dumps(payload))
        self.assertIn({"path": "linked.md", "reason": "SYMLINK_FILE_NOT_SCANNED"},
                      payload["source_snapshot"]["collection"]["gaps"])
        self.assert_no_negative_claim(payload)

    def test_symlink_directory_gap_is_visible_without_following_it(self) -> None:
        from tools.census_legacy_references import build_payload
        outside = self.outer / "outside"
        outside.mkdir()
        (outside / "private.md").write_text("SYNTHETIC_DIRECTORY_SENTINEL 00_meta/", encoding="utf-8")
        (self.root / "linked_dir").symlink_to(outside, target_is_directory=True)
        payload = build_payload(self.root)
        self.assertNotIn("SYNTHETIC_DIRECTORY_SENTINEL", json.dumps(payload))
        self.assertIn({"path": "linked_dir", "reason": "SYMLINK_DIRECTORY_NOT_SCANNED"},
                      payload["source_snapshot"]["collection"]["gaps"])
        self.assert_no_negative_claim(payload)

    def test_internal_symlink_remains_an_explicit_unscanned_alias(self) -> None:
        from tools.census_legacy_references import build_payload
        (self.root / "alias.md").symlink_to(self.root / "reader.md")
        payload = build_payload(self.root)
        paths = {item["path"] for item in payload["source_snapshot"]["files"]}
        self.assertIn("reader.md", paths)
        self.assertNotIn("alias.md", paths)
        self.assert_no_negative_claim(payload)

    def test_undecodable_text_blocks_absence_but_keeps_other_observations(self) -> None:
        from tools.census_legacy_references import build_payload
        (self.root / "bad.md").write_bytes(b"\xff 01_runtime-spine/")
        payload = build_payload(self.root)
        self.assertGreater(payload["summary"]["03_field-governance"]["live_caller_count"], 0)
        self.assertIn({"path": "bad.md", "reason": "NON_UTF8_TEXT_NOT_SCANNED"},
                      payload["source_snapshot"]["collection"]["gaps"])
        self.assert_no_negative_claim(payload)

    def test_read_error_is_scoped_and_does_not_erase_other_sources(self) -> None:
        from tools import census_legacy_references as module
        path = self.root / "unreadable.md"
        path.write_text("01_runtime-spine/", encoding="utf-8")
        real_open = module.os.open
        def controlled_open(requested, *args, **kwargs):
            if Path(requested) == path:
                raise PermissionError("synthetic read denial")
            return real_open(requested, *args, **kwargs)
        with mock.patch.object(module.os, "open", side_effect=controlled_open):
            payload = module.build_payload(self.root)
        self.assertIn({"path": "unreadable.md", "reason": "TEXT_READ_ERROR"},
                      payload["source_snapshot"]["collection"]["gaps"])
        self.assertIn("reader.md", {item["path"] for item in payload["source_snapshot"]["files"]})
        self.assert_no_negative_claim(payload)

    def test_manifest_drift_between_collection_and_basis_read_blocks_negative_claims(self) -> None:
        from tools import census_legacy_references as module
        real_read = module.read_manifest_basis
        def changed_basis(*args, **kwargs):
            data, readers, metadata = real_read(*args, **kwargs)
            metadata = dict(metadata, sha256="0" * 64)
            return data, readers, metadata
        with mock.patch.object(module, "read_manifest_basis", side_effect=changed_basis):
            payload = module.build_payload(self.root)
        self.assertFalse(payload["source_snapshot"]["manifest_matches_snapshot"])
        self.assert_no_negative_claim(payload)

    def test_cli_output_is_excluded_on_first_run_and_repeat(self) -> None:
        from tools import census_legacy_references as module
        output = self.root / "report.json"
        fake_location = self.root / "tools" / "census_legacy_references.py"
        with mock.patch.object(module, "__file__", str(fake_location)), \
                mock.patch.object(sys, "argv", ["census", "--output", str(output)]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(module.main(), 0)
            first = output.read_bytes()
            self.assertEqual(module.main(), 0)
            second = output.read_bytes()
        self.assertEqual(first, second)
        payload = json.loads(second)
        self.assertNotIn("report.json", {item["path"] for item in payload["source_snapshot"]["files"]})
        self.assertEqual(payload["source_snapshot"]["collection"]["explicit_output_exclusions"], ["report.json"])

    def test_output_exclusion_does_not_silently_exclude_other_json_sources(self) -> None:
        from tools.census_legacy_references import build_payload, collect_text_files
        (self.root / "other.json").write_text('{"source":"01_runtime-spine/"}', encoding="utf-8")
        payload = build_payload(self.root, excluded_paths=(Path("report.json"),))
        self.assertIn("other.json", {item["path"] for item in payload["source_snapshot"]["files"]})
        self.assertIsInstance(collect_text_files(self.root), dict)
        self.assertTrue(payload["source_snapshot"]["negative_evidence_eligible"])
        self.assertTrue(payload["summary"]["05_topology"]["caller_absence_on_scanned_text_surface"])
        self.assertFalse(payload["summary"]["01_runtime-spine"]["caller_absence_on_scanned_text_surface"])

    def test_later_matching_lines_preserve_both_dependency_signals(self) -> None:
        text = ("03_field-governance/history.md\n"
                "unrelated context\n"
                "restore from 03_field-governance/source.md\n"
                "route to 03_field-governance/receiver.md\n")
        rows = scan_text_map({"dcp_kernel/consumer.py": text}, ("03_field-governance",))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].dependency_signal, DependencySignal.REBUILD_AND_WAKE_RELEVANT)
        self.assertEqual(rows[0].matched_line_numbers, (1, 3, 4))
        self.assertEqual(rows[0].excerpt, "03_field-governance/history.md")
        reverse = "\n".join(reversed(text.splitlines()))
        other = scan_text_map({"dcp_kernel/consumer.py": reverse}, ("03_field-governance",))
        self.assertEqual(other[0].dependency_signal, rows[0].dependency_signal)

    def test_all_line_scan_keeps_audit_lineage_and_unknown_boundaries(self) -> None:
        text = "03_field-governance/history.md\nrestore route 03_field-governance/source.md\n"
        for caller, expected in (
            ("tools/census_legacy_references.py", DependencySignal.NONE),
            ("04_adapter-layer/optional.md", DependencySignal.NONE),
            ("misc/unknown.md", DependencySignal.UNKNOWN),
        ):
            with self.subTest(caller=caller):
                rows = scan_text_map({caller: text}, ("03_field-governance",))
                self.assertEqual(rows[0].dependency_signal, expected)
                self.assertEqual(rows[0].matched_line_numbers, (1, 2))


if __name__ == "__main__":
    unittest.main()
