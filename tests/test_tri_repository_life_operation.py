from __future__ import annotations

import json
import unittest
from pathlib import Path


class TriRepositoryLifeOperationTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "tri-repository-life-operation-compatibility.json").read_text())

    def test_three_repositories_remain_weighted_projections_not_authority_roots(self):
        payload = self.payload()
        repos = payload["repositories"]
        self.assertEqual(set(repos), {"Ideas-Pole-Projection", "DCP-Pole-Projection", "GLModel-Pole-Projection"})
        for state in repos.values():
            self.assertFalse(state["native_source_root"])
            self.assertFalse(state["repo_is_pole_authority"])
            self.assertTrue(state["tri_pole_architecture"])
            self.assertFalse(state["shared_belt_is_fourth_pole"])
            self.assertFalse(state["shared_belt_is_authority_root"])
            self.assertFalse(state["native_body_copy_default"])

    def test_outer_pole_inner_motion_does_not_create_repository_taxonomy(self):
        payload = self.payload()
        boundary = set(payload["claim_boundary"])
        self.assertIn("EIGHT_POLES_AND_EIGHT_MOTIONS_ARE_NOT_REPOSITORY_TAXONOMY", boundary)
        interpretation = payload["outer_pole_inner_motion_interpretation"]
        self.assertIn("not permanent repository owners", interpretation["outer_poles"])
        self.assertIn("not a second control plane", interpretation["inner_motions"])

    def test_cross_repository_alignment_does_not_claim_absorption_or_runtime(self):
        payload = self.payload()
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])
        self.assertFalse(payload["canon"])
        self.assertEqual(payload["authority_effect"], "none")
        self.assertIn("CROSS_REPOSITORY_COMPATIBILITY_DOES_NOT_PROVE_NATIVE_ABSORPTION", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
