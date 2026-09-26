"""NFN R2 bounded operational spine R0.1.

Integrates route qualification, risk-scaled qualification, resource/effect
accounting and local-to-generalized field feedback without making any one of
those surfaces a mandatory global workflow.

Discovery is not authorization. Efficiency is not authority. Feedback is not
admission. This module is a bounded integration specimen, not Runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from field_feedback_r01 import FieldFeedbackAssessment, LocalFieldObservation, project_field_feedback
from qualification_budget_r01 import (
    ActionRiskProfile,
    QualificationAssessment,
    QualificationExecution,
    assess_qualification,
    derive_qualification_budget,
)
from resource_effect_accounting_r01 import (
    ResourceEffectAssessment,
    ResourceEffectObservation,
    assess_resource_effect,
)


class RouteDisposition(str, Enum):
    EXECUTABLE_CANDIDATE = "EXECUTABLE_CANDIDATE"
    HOLD = "HOLD"


@dataclass(frozen=True)
class RouteCandidate:
    route_id: str
    capability_fit: bool
    authority_valid: bool
    red_line_hit: bool
    data_boundary_valid: bool
    resource_feasible: bool
    reality_applicable: bool


@dataclass(frozen=True)
class RouteAssessment:
    route_id: str
    disposition: RouteDisposition
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PreActionAssessment:
    route: RouteAssessment
    qualification: QualificationAssessment | None
    executable: bool
    reasons: tuple[str, ...]


def qualify_route(route: RouteCandidate) -> RouteAssessment:
    reasons: list[str] = []
    if not route.capability_fit:
        reasons.append("CAPABILITY_NOT_FIT")
    if not route.authority_valid:
        reasons.append("AUTHORITY_NOT_VALID")
    if route.red_line_hit:
        reasons.append("RED_LINE_HIT")
    if not route.data_boundary_valid:
        reasons.append("DATA_BOUNDARY_NOT_VALID")
    if not route.resource_feasible:
        reasons.append("RESOURCE_NOT_FEASIBLE")
    if not route.reality_applicable:
        reasons.append("REALITY_NOT_APPLICABLE")

    if reasons:
        return RouteAssessment(route.route_id, RouteDisposition.HOLD, tuple(reasons))
    return RouteAssessment(
        route.route_id,
        RouteDisposition.EXECUTABLE_CANDIDATE,
        ("ROUTE_QUALIFIED_WITHOUT_EXECUTION_CLAIM",),
    )


def pre_action_gate(
    route: RouteCandidate,
    risk: ActionRiskProfile,
    execution: QualificationExecution,
) -> PreActionAssessment:
    route_result = qualify_route(route)
    if route_result.disposition is RouteDisposition.HOLD:
        return PreActionAssessment(
            route_result,
            None,
            False,
            ("PATH_DISCOVERY_DOES_NOT_OVERRIDE_ROUTE_QUALIFICATION",),
        )

    budget = derive_qualification_budget(risk)
    qualification = assess_qualification(budget, execution)
    if not qualification.sufficient:
        return PreActionAssessment(
            route_result,
            qualification,
            False,
            ("ROUTE_IS_LEGAL_CANDIDATE_BUT_QUALIFICATION_IS_INSUFFICIENT",),
        )

    return PreActionAssessment(
        route_result,
        qualification,
        True,
        ("ROUTE_AND_MINIMUM_SUFFICIENT_QUALIFICATION_MET",),
    )


def post_action_account(
    observation: ResourceEffectObservation,
    *,
    baseline: ResourceEffectObservation | None = None,
) -> ResourceEffectAssessment:
    return assess_resource_effect(observation, baseline=baseline)


def metabolize_field_feedback(
    observations: tuple[LocalFieldObservation, ...],
) -> FieldFeedbackAssessment:
    return project_field_feedback(observations)
