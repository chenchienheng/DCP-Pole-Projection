from __future__ import annotations

import json
import unittest
from pathlib import Path


class LegacyFamilyWithdrawalReadinessTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "legacy-family-withdrawal-readiness.json").read_text())

    def test_all_three_families_have_closed_body_and_provenance_review(self):
        payload = self.payload()
        for state in payload["families"].values():
            self.assertTrue(state["body_review_complete"])
            self.assertTrue(state["successor_review_complete"])
            self.assertEqual(state["unique_provenance_debt_count"], 0)
            self.assertFalse(state["current_reader_role"])

    def test_no_family_is_reclaim_ready_before_caller_rebuild_and_wake_close(self):
        payload = self.payload()
        for state in payload["families"].values():
            self.assertFalse(state["caller_census_complete"])
            self.assertFalse(state["rebuild_dependency_census_complete"])
            self.assertFalse(state["wake_routing_withdrawal_proven"])
            self.assertEqual(state["state"], "CALLER_REBUILD_WAKE_PENDING")
        self.assertFalse(payload["destructive_reclaim_authorized"])

    def test_legacy_qinyi_template_is_not_silently_treated_as_withdrawn(self):
        payload = self.payload()
        debt = payload["known_wake_debt"][0]
        self.assertEqual(debt["semantic_authority"], "none")
        self.assertFalse(debt["physical_wake_withdrawal_proven"])
        self.assertEqual(debt["action"], "HOLD_FOR_STRUCTURAL_RECLAIM_REVIEW")


if __name__ == "__main__":
    unittest.main()
