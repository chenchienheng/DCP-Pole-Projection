import unittest

from dcp_kernel.judgment import DimensionState, JudgmentInput, KnowledgeState, assess_judgment
from dcp_kernel.models import Decision


class JudgmentTests(unittest.TestCase):
    def base(self, **changes):
        data = dict(
            judgment_id="J-1",
            source_classified=True,
            meaning_relevant=True,
            boundary_resolved=True,
            evidence_sufficient=True,
            alternatives_considered=True,
            consequence_assessed=True,
            responsibility_owner="DCP",
            return_target="Native Receiver",
            rebuild_path_present=True,
            authority_valid=True,
            recommendation_present=True,
            expert_confidence=0.99,
            model_confidence=0.99,
            majority_agreement=False,
            counterexample_channel_open=True,
            execution_available=True,
            execution_requested=False,
            truth_state=DimensionState.SATISFIED,
            scope_state=DimensionState.SATISFIED,
            context_state=DimensionState.SATISFIED,
            goal_state=DimensionState.SATISFIED,
            cost_state=DimensionState.SATISFIED,
            risk_state=DimensionState.SATISFIED,
            relationship_state=DimensionState.NOT_APPLICABLE,
            time_state=DimensionState.SATISFIED,
            consequence_state=DimensionState.SATISFIED,
        )
        data.update(changes)
        return JudgmentInput(**data)

    def test_high_confidence_does_not_replace_evidence(self):
        result = assess_judgment(self.base(evidence_sufficient=False))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.knowledge_state, KnowledgeState.UNKNOWN)

    def test_expertise_does_not_replace_authority(self):
        result = assess_judgment(self.base(authority_valid=False, expert_confidence=1.0))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertFalse(result.execution_permitted_by_judgment)

    def test_majority_must_keep_counterexample_channel(self):
        result = assess_judgment(self.base(majority_agreement=True, counterexample_channel_open=False))
        self.assertEqual(result.decision, Decision.HOLD)

    def test_recommendation_is_never_decision(self):
        result = assess_judgment(self.base())
        self.assertEqual(result.decision, Decision.PASS)
        self.assertFalse(result.recommendation_is_decision)

    def test_execution_can_be_delegated_after_judgment_without_sovereignty_transfer(self):
        result = assess_judgment(self.base(execution_requested=True, execution_available=True))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertTrue(result.execution_permitted_by_judgment)
        self.assertFalse(result.recommendation_is_decision)

    def test_true_but_unauthorized_is_preserved_as_hold(self):
        result = assess_judgment(self.base(authority_valid=False))
        states = dict(result.dimension_states)
        self.assertEqual(states["truth"], DimensionState.SATISFIED)
        self.assertEqual(states["authority"], DimensionState.UNSATISFIED)
        self.assertEqual(result.decision, Decision.HOLD)

    def test_locally_valid_but_globally_unsafe_does_not_collapse_to_wrong(self):
        result = assess_judgment(self.base(risk_state=DimensionState.UNSATISFIED))
        states = dict(result.dimension_states)
        self.assertEqual(states["truth"], DimensionState.SATISFIED)
        self.assertEqual(states["scope"], DimensionState.SATISFIED)
        self.assertEqual(states["risk"], DimensionState.UNSATISFIED)
        self.assertEqual(result.decision, Decision.HOLD)

    def test_unknown_truth_is_preserved_even_when_other_dimensions_satisfy(self):
        result = assess_judgment(self.base(truth_state=DimensionState.UNKNOWN))
        states = dict(result.dimension_states)
        self.assertEqual(states["truth"], DimensionState.UNKNOWN)
        self.assertEqual(result.knowledge_state, KnowledgeState.UNKNOWN)
        self.assertEqual(result.decision, Decision.PASS)


if __name__ == "__main__":
    unittest.main()
