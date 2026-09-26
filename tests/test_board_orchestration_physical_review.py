import json
import unittest
from pathlib import Path


class BoardOrchestrationPhysicalReviewTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "03-board-orchestration-physical-review.json").read_text())

    def test_family_is_not_current_control_plane(self):
        payload = self.payload()
        self.assertEqual(payload["current_architecture_role"], "NONE_AS_ORCHESTRATION_FAMILY")
        self.assertFalse(payload["normal_reader_required"])

    def test_only_lineage_body_remains(self):
        payload = self.payload()
        self.assertEqual(len(payload["remaining_live_body"]), 1)
        item = payload["remaining_live_body"][0]
        self.assertFalse(item["current_eligibility"])
        self.assertFalse(item["executable_authority"])

    def test_reclaim_is_still_gated(self):
        payload = self.payload()
        debt = set(payload["remaining_debt"])
        self.assertIn("FULL_BRANCH_CALLER_CENSUS", debt)
        self.assertIn("REBUILD_DEPENDENCY_WITHDRAWAL", debt)
        self.assertIn("POOLED_RECLAIM_REVIEW", debt)
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])


if __name__ == "__main__":
    unittest.main()
