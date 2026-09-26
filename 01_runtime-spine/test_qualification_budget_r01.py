import unittest

from qualification_budget_r01 import (
    ActionRiskProfile,
    QualificationDepth,
    QualificationExecution,
    assess_qualification,
    derive_qualification_budget,
)


def risk(**kw):
    base = dict(
        action_id="A1",
        reversible=True,
        crosses_authority_boundary=False,
        touches_private_data=False,
        physical_world_intervention=False,
        financial_commitment=False,
        external_publication=False,
        safety_critical=False,
        materiality=0.20,
        uncertainty=0.20,
    )
    base.update(kw)
    return ActionRiskProfile(**base)


class QualificationBudgetR01Tests(unittest.TestCase):
    def test_low_risk_reversible_action_uses_light_minimum(self):
        budget = derive_qualification_budget(risk())
        self.assertEqual(budget.required_depth, QualificationDepth.LIGHT)
        self.assertEqual(budget.minimum_evidence_items, 1)

    def test_physical_intervention_cannot_be_downgraded_for_cost(self):
        budget = derive_qualification_budget(
            risk(physical_world_intervention=True, materiality=0.10)
        )
        self.assertEqual(budget.required_depth, QualificationDepth.DEEP)
        self.assertTrue(budget.independent_check_required)
        self.assertTrue(budget.explicit_human_confirmation_required)

    def test_authority_boundary_requires_deep_qualification(self):
        budget = derive_qualification_budget(risk(crosses_authority_boundary=True))
        self.assertEqual(budget.required_depth, QualificationDepth.DEEP)

    def test_material_irreversible_action_requires_more_than_light(self):
        budget = derive_qualification_budget(
            risk(reversible=False, materiality=0.75)
        )
        self.assertEqual(budget.required_depth, QualificationDepth.STANDARD)

    def test_saving_resources_cannot_make_insufficient_execution_sufficient(self):
        budget = derive_qualification_budget(risk(safety_critical=True))
        execution = QualificationExecution(
            depth_used=QualificationDepth.LIGHT,
            evidence_items=1,
            independent_check_observed=False,
            human_confirmation_observed=False,
            resource_units_used=0.1,
        )
        result = assess_qualification(budget, execution)
        self.assertFalse(result.sufficient)
        self.assertIn("QUALIFICATION_DEPTH_BELOW_REQUIRED", result.reasons)

    def test_extra_resource_is_not_required_after_minimum_sufficient_gate(self):
        budget = derive_qualification_budget(risk())
        execution = QualificationExecution(
            depth_used=QualificationDepth.LIGHT,
            evidence_items=1,
            independent_check_observed=False,
            human_confirmation_observed=False,
            resource_units_used=1.0,
        )
        result = assess_qualification(budget, execution)
        self.assertTrue(result.sufficient)
        self.assertIn("EXTRA_RESOURCE_USE_IS_NOT_REQUIRED_BY_THIS_BUDGET", result.reasons)

    def test_private_data_raises_qualification_without_implying_authority(self):
        budget = derive_qualification_budget(risk(touches_private_data=True))
        self.assertEqual(budget.required_depth, QualificationDepth.STANDARD)
        self.assertFalse(budget.explicit_human_confirmation_required)


if __name__ == "__main__":
    unittest.main()
