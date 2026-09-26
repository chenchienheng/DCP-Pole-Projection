import unittest

from field_feedback_r01 import FeedbackDisposition, LocalFieldObservation
from qualification_budget_r01 import ActionRiskProfile, QualificationDepth, QualificationExecution
from resource_effect_accounting_r01 import ResourceEffectDisposition, ResourceEffectObservation
from r2_operational_spine_r01 import (
    CarrierContinuityDisposition,
    CarrierObservation,
    RouteCandidate,
    RouteDisposition,
    assess_carrier_continuity,
    metabolize_field_feedback,
    post_action_account,
    pre_action_gate,
    qualify_route,
)


def route(**kw):
    base = dict(
        route_id="R1",
        capability_fit=True,
        authority_valid=True,
        red_line_hit=False,
        data_boundary_valid=True,
        resource_feasible=True,
        reality_applicable=True,
    )
    base.update(kw)
    return RouteCandidate(**base)


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


class R2OperationalSpineR01Tests(unittest.TestCase):
    def test_ui_work_label_does_not_replace_stable_native_identity(self):
        result = assess_carrier_continuity(
            CarrierObservation(
                stable_identity="QINYI_WORLD_MODELING_CONTINUITY",
                observed_title="World 建造 Chat",
                observed_ui_mode="Work",
                backend_mode_proven=False,
            )
        )
        self.assertEqual(
            result.disposition,
            CarrierContinuityDisposition.IDENTITY_CONTINUES,
        )
        self.assertEqual(result.stable_identity, "QINYI_WORLD_MODELING_CONTINUITY")
        self.assertIn(
            "CARRIER_OR_TITLE_CHANGE_DOES_NOT_RENAME_NATIVE_IDENTITY",
            result.reasons,
        )

    def test_title_change_without_identity_transition_evidence_keeps_identity(self):
        result = assess_carrier_continuity(
            CarrierObservation(
                stable_identity="QINYI_WORLD_MODELING_CONTINUITY",
                observed_title="Gmail 自動整理",
                observed_ui_mode=None,
                backend_mode_proven=False,
            )
        )
        self.assertEqual(
            result.disposition,
            CarrierContinuityDisposition.IDENTITY_CONTINUES,
        )

    def test_discovered_route_hitting_red_line_is_not_executable(self):
        result = qualify_route(route(red_line_hit=True))
        self.assertEqual(result.disposition, RouteDisposition.HOLD)
        self.assertIn("RED_LINE_HIT", result.reasons)

    def test_capable_but_unauthorized_route_holds(self):
        result = qualify_route(route(authority_valid=False))
        self.assertEqual(result.disposition, RouteDisposition.HOLD)

    def test_low_risk_legal_route_can_pass_with_light_minimum(self):
        result = pre_action_gate(
            route(),
            risk(),
            QualificationExecution(
                depth_used=QualificationDepth.LIGHT,
                evidence_items=1,
                independent_check_observed=False,
                human_confirmation_observed=False,
                resource_units_used=1.0,
            ),
        )
        self.assertTrue(result.executable)

    def test_physical_intervention_does_not_pass_with_light_budget(self):
        result = pre_action_gate(
            route(),
            risk(physical_world_intervention=True),
            QualificationExecution(
                depth_used=QualificationDepth.LIGHT,
                evidence_items=1,
                independent_check_observed=False,
                human_confirmation_observed=False,
                resource_units_used=0.1,
            ),
        )
        self.assertFalse(result.executable)
        self.assertIsNotNone(result.qualification)

    def test_post_action_more_resource_without_gain_is_dominated(self):
        baseline = ResourceEffectObservation(
            "B", "N1", "C1", True, True, 1.0, 0.6, 0.5, 0.3, 0.7, True, True
        )
        candidate = ResourceEffectObservation(
            "C", "N1", "C2", True, True, 5.0, 0.6, 0.5, 0.3, 0.7, True, True
        )
        result = post_action_account(candidate, baseline=baseline)
        self.assertEqual(result.disposition, ResourceEffectDisposition.DOMINATED_CANDIDATE)

    def test_authorized_local_histories_can_metabolize_without_identity_return(self):
        observations = (
            LocalFieldObservation(
                "O1", "LOCAL-A", "FAMILY-X", "CFG-1", "ENV-1",
                "wear", 0.9, "unit", "NORMAL", "LOCAL", 0.9, True, True, False
            ),
            LocalFieldObservation(
                "O2", "LOCAL-B", "FAMILY-X", "CFG-1", "ENV-1",
                "wear", 1.1, "unit", "NORMAL", "LOCAL", 0.9, True, True, False
            ),
        )
        result = metabolize_field_feedback(observations)
        self.assertEqual(result.disposition, FeedbackDisposition.GENERALIZABLE_CANDIDATE)
        self.assertFalse(hasattr(result.nutrient, "local_subject_id"))


if __name__ == "__main__":
    unittest.main()
