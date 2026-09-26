from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.relation_semantics import RelationInput, RelationState, assess_relation


class RelationSemanticsTests(unittest.TestCase):
    def test_unresolved_identity_blocks_relation_inference(self) -> None:
        result = assess_relation(RelationInput(False, True, True))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, RelationState.IDENTITY_RESOLUTION_GAP)

    def test_plain_a_to_b_link_is_static_only(self) -> None:
        result = assess_relation(RelationInput(True, True, True))
        self.assertEqual(result.state, RelationState.STATIC_RELATION_ONLY)
        self.assertIn("state", result.missing_dimensions)
        self.assertIn("time", result.missing_dimensions)
        self.assertIn("evidence", result.missing_dimensions)
        self.assertIn("effect", result.missing_dimensions)

    def test_relevant_dimensions_must_be_filled(self) -> None:
        result = assess_relation(
            RelationInput(
                True, True, True,
                reciprocity_relevant=True,
                state_defined=True,
                time_defined=True,
                evidence_defined=True,
                authority_relevant=True,
                effect_defined=True,
                return_path_relevant=True,
            )
        )
        self.assertEqual(result.state, RelationState.STATIC_RELATION_ONLY)
        self.assertIn("reciprocity", result.missing_dimensions)
        self.assertIn("authority", result.missing_dimensions)
        self.assertIn("return_path", result.missing_dimensions)

    def test_material_relation_passes_with_required_context(self) -> None:
        result = assess_relation(
            RelationInput(
                True, True, True,
                reciprocity_relevant=True,
                reciprocity_defined=True,
                state_defined=True,
                time_defined=True,
                evidence_defined=True,
                authority_relevant=True,
                authority_defined=True,
                cost_relevant=True,
                cost_defined=True,
                risk_relevant=True,
                risk_defined=True,
                effect_defined=True,
                reversibility_relevant=True,
                reversibility_defined=True,
                return_path_relevant=True,
                return_path_defined=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, RelationState.MATERIAL_RELATION)


if __name__ == "__main__":
    unittest.main()
