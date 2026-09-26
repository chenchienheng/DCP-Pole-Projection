from __future__ import annotations

import json
import unittest
from pathlib import Path


class RootSurfaceClassificationTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "root-surface-classification.json").read_text())

    def test_retired_and_retained_surfaces_are_distinct(self):
        payload = self.payload()
        retired = set(payload["retired_absent"])
        retained = {item["path"] for item in payload["retained_deentitled"]}
        self.assertEqual(len(retired), 19)
        self.assertEqual(len(retained), 4)
        self.assertTrue(retired.isdisjoint(retained))

    def test_retained_surfaces_are_explicitly_deentitled(self):
        payload = self.payload()
        for item in payload["retained_deentitled"]:
            self.assertFalse(item["current_authority"])
            self.assertFalse(item["normal_reader_required"])
            self.assertTrue(item["reason"])

    def test_classification_preserves_non_destructive_boundary(self):
        payload = self.payload()
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])
        self.assertFalse(payload["destructive_reclaim_authorized"])
        self.assertIn("FULL_BRANCH_CALLER_CENSUS", payload["remaining_debt"])
        self.assertIn("REBUILD_DEPENDENCY_WITHDRAWAL", payload["remaining_debt"])


if __name__ == "__main__":
    unittest.main()
