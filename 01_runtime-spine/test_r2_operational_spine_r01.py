import unittest

from carrier_current_resolver_r01 import CarrierCurrentCandidate, CarrierKind, CurrentResolutionDisposition
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
    resolve_reentry_current,
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


def execution():
    return QualificationExecution(
        depth_used=QualificationDepth.LIGHT,
        evidence_items=1,
        independent_check_observed=False,
        human_confirmation_observed=False,
        resource_units_used=1.0,
    )


def current_candidate(carrier=CarrierKind.DRIVE, locator="world-thin"):
    return CarrierCurrentCandidate(
        carrier, locator, "WORLD", "CONSTRUCTION_CURRENT",
        True, True, True, True, True, "2026-09-26T18:00:00+08:00"
    )


class R2OperationalSpineR01Tests(unittest.TestCase):
    def test_reentry_uses_qualified_drive_current_not_memory_retrieval_order(self):
        memory = CarrierCurrentCandidate(
            CarrierKind.MEMORY, "memory-cue", "WORLD", "CONSTRUCTION_CURRENT",
            True, True, True, False, False, "2026-09-26T15:00:00+08:00"
        )
        drive = CarrierCurrentCandidate(
            CarrierKind.DRIVE, "world-thin", "WORLD", "CONSTRUCTION_CURRENT",
            True, True, True, True, True, "2026-09-26T14:00:00+08:00"
        )
        result = resolve_reentry_current(
            (memory, drive),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        self.assertEqual(result.disposition, CurrentResolutionDisposition.RESOLVED)
        self.assertEqual(result.locator, "world-thin")

    def test_reentry_holds_when_two_mutable_current_pointers_compete(self):
        drive = CarrierCurrentCandidate(
            CarrierKind.DRIVE, "world-thin", "WORLD", "CONSTRUCTION_CURRENT",
            True, True, True, True, True
        )
        github = CarrierCurrentCandidate(
            CarrierKind.GITHUB, "pr391", "WORLD", "CONSTRUCTION_CURRENT",
            True, True, True, True, True
        )
        result = resolve_reentry_current(
            (drive, github),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        self.assertEqual(result.disposition, CurrentResolutionDisposition.HOLD)

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
                observed_title="Automation result title",
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
        result = pre_action_gate(route(), risk(), execution())
        self.assertTrue(result.executable)

    def test_current_hold_blocks_same_dependent_action(self):
        current = resolve_reentry_current(
            (
                current_candidate(CarrierKind.DRIVE, "world-thin"),
                current_candidate(CarrierKind.GITHUB, "pr391"),
            ),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        result = pre_action_gate(
            route(), risk(), execution(), current=current, require_current=True
        )
        self.assertFalse(result.executable)
        self.assertIn("CURRENT_HOLD_BLOCKS_DEPENDENT_ACTION", result.reasons)

    def test_required_current_missing_blocks_dependent_action(self):
        result = pre_action_gate(
            route(), risk(), execution(), require_current=True
        )
        self.assertFalse(result.executable)
        self.assertIn("CURRENT_REQUIRED_BUT_NOT_RESOLVED", result.reasons)

    def test_resolved_current_allows_qualified_dependent_action(self):
        current = resolve_reentry_current(
            (current_candidate(),),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        result = pre_action_gate(
            route(), risk(), execution(), current=current, require_current=True
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
