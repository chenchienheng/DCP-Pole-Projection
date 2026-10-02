import json
import unittest
from pathlib import Path


class TopologyMetabolismReviewTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "05-topology-metabolism-review.json").read_text())

    def test_topology_does_not_become_world_truth_or_authority(self):
        payload = self.payload()
        self.assertFalse(payload["topology_is_world_truth"])
        self.assertFalse(payload["topology_is_authority"])
        self.assertFalse(payload["fixed_topology_required_for_rebuild"])

    def test_fixed_ten_ring_is_retired(self):
        payload = self.payload()
        ten_ring = next(item for item in payload["observed_dispositions"] if item["path"].endswith("ten-ring-definition-v0-1.md"))
        self.assertEqual(ten_ring["state"], "RETIRED_ABSENT")

    def test_retained_primitives_do_not_recreate_fixed_layers(self):
        payload = self.payload()
        rules = set(payload["current_interpretation"])
        self.assertIn("TOPOLOGY_IS_RELATION_PROJECTION_NOT_WORLD_TRUTH", rules)
        self.assertIn("RELATION_CAN_BE_N_NODE_AND_HETEROGENEOUS", rules)
        self.assertIn("REBUILD_MUST_NOT_REQUIRE_RETIRED_TOPOLOGY", rules)
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])


if __name__ == "__main__":
    unittest.main()
