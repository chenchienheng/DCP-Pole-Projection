from __future__ import annotations

import unittest

from dcp_kernel.family_metabolism import (
    FamilyMetabolismInput,
    FamilyMetabolismState,
    assess_family_metabolism,
)
from dcp_kernel.models import Decision


class FamilyMetabolismTests(unittest.TestCase):
    def test_legacy_folder_label_alone_never_completes_metabolism(self) -> None:
        result = assess_family_metabolism(
            FamilyMetabolismInput(
                family="04_adapter-layer",
                artifact_count=10,
                classified_count=4,
                successor_covered_count=4,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                normal_reader_wake=False,
                current_routing_reference=False,
                unique_evidence_unreviewed_count=0,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, FamilyMetabolismState.SUCCESSOR_COVERAGE_PARTIAL)
        self.assertFalse(result.destructive_action_authorized)

    def test_reader_withdrawal_is_required_after_successor_coverage(self) -> None:
        result = assess_family_metabolism(
            FamilyMetabolismInput(
                family="01_runtime-spine",
                artifact_count=5,
                classified_count=5,
                successor_covered_count=5,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                normal_reader_wake=True,
                current_routing_reference=False,
                unique_evidence_unreviewed_count=0,
            )
        )
        self.assertEqual(result.state, FamilyMetabolismState.READER_WITHDRAWAL_PARTIAL)

    def test_unique_evidence_blocks_reclaim_even_after_reader_withdrawal(self) -> None:
        result = assess_family_metabolism(
            FamilyMetabolismInput(
                family="03_field-governance",
                artifact_count=12,
                classified_count=12,
                successor_covered_count=12,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                normal_reader_wake=False,
                current_routing_reference=False,
                unique_evidence_unreviewed_count=2,
            )
        )
        self.assertEqual(result.state, FamilyMetabolismState.UNIQUE_EVIDENCE_REVIEW_PENDING)

    def test_ready_for_reclaim_review_is_not_delete_authority(self) -> None:
        result = assess_family_metabolism(
            FamilyMetabolismInput(
                family="legacy-family",
                artifact_count=3,
                classified_count=3,
                successor_covered_count=3,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                normal_reader_wake=False,
                current_routing_reference=False,
                unique_evidence_unreviewed_count=0,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, FamilyMetabolismState.READY_FOR_POOLED_RECLAIM_REVIEW)
        self.assertFalse(result.destructive_action_authorized)


if __name__ == "__main__":
    unittest.main()
