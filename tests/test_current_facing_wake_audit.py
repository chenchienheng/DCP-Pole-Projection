from __future__ import annotations

import json
import unittest
from pathlib import Path


class CurrentFacingWakeAuditTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "current-facing-wake-audit.json").read_text())

    def test_current_facing_surfaces_do_not_normally_wake_legacy_families(self):
        payload = self.payload()
        for surface in payload["observed_surfaces"]:
            self.assertFalse(surface["normal_legacy_family_wake_observed"])
        for state in payload["legacy_family_state"].values():
            self.assertEqual(state, "CURRENT_FACING_WAKE_NOT_OBSERVED")

    def test_qinyi_template_physical_wake_debt_remains_explicit(self):
        payload = self.payload()
        debt = payload["known_physical_wake_debt"][0]
        self.assertEqual(debt["semantic_authority"], "none")
        self.assertTrue(debt["physical_presence_in_issue_template_directory"])
        self.assertFalse(debt["physical_wake_withdrawal_proven"])

    def test_audit_never_authorizes_reclaim(self):
        payload = self.payload()
        self.assertFalse(payload["destructive_reclaim_authorized"])
        self.assertIn(
            "THIS_AUDIT_DOES_NOT_AUTHORIZE_DELETE_MOVE_MERGE_PROMOTION_OR_RUNTIME",
            payload["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
