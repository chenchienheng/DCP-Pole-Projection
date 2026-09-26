from __future__ import annotations

import json
import unittest
from pathlib import Path


class LegacyRoutingControlRetirementTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "legacy-routing-control-retirement.json").read_text())

    def test_retired_routing_controls_are_successor_bound(self):
        payload = self.payload()
        self.assertEqual(len(payload["retired_absent"]), 4)
        for item in payload["retired_absent"]:
            self.assertTrue(item["retired_semantics"])
            self.assertTrue(item["successor"])

    def test_retained_intake_specimen_is_deentitled(self):
        payload = self.payload()
        self.assertEqual(len(payload["retained_deentitled"]), 1)
        item = payload["retained_deentitled"][0]
        self.assertFalse(item["current_authority"])
        self.assertFalse(item["normal_reader_required"])
        self.assertIn("Gmail as mother gate", item["retired_assumptions"])

    def test_routing_retirement_does_not_grant_reclaim_or_runtime(self):
        payload = self.payload()
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])
        self.assertFalse(payload["destructive_reclaim_authorized"])
        self.assertIn("REBUILD_DEPENDENCY_WITHDRAWAL", payload["remaining_debt"])


if __name__ == "__main__":
    unittest.main()
