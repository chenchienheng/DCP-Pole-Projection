from __future__ import annotations

import unittest

from dcp_kernel.metabolism import (
    ArtifactRole,
    NameRisk,
    ProposedDisposition,
    assess_artifact,
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
            "CURRENT-SURFACE-MANIFEST.json"
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


if __name__ == "__main__":
    unittest.main()
