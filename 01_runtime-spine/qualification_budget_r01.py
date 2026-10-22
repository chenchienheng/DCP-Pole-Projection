"""Risk-scaled qualification budget R0.1.

Balances minimum-sufficient evidence/resource use against materiality, risk and
irreversibility. This is not a universal quality score and does not claim that
quality itself is a conserved quantity.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class QualificationDepth(IntEnum):
    LIGHT = 1
    STANDARD = 2
    DEEP = 3


@dataclass(frozen=True)
class ActionRiskProfile:
    action_id: str
    reversible: bool
    crosses_authority_boundary: bool
    touches_private_data: bool
    physical_world_intervention: bool
    financial_commitment: bool
    external_publication: bool
    safety_critical: bool
    materiality: float  # bounded candidate input: 0..1
    uncertainty: float  # bounded candidate input: 0..1


@dataclass(frozen=True)
class QualificationBudget:
    required_depth: QualificationDepth
    minimum_evidence_items: int
    independent_check_required: bool
    explicit_human_confirmation_required: bool
    reasons: tuple[str, ...]
    claim_ceiling: str = "QUALIFICATION_BUDGET_CANDIDATE"


@dataclass(frozen=True)
class QualificationExecution:
    depth_used: QualificationDepth
    evidence_items: int
    independent_check_observed: bool
    human_confirmation_observed: bool
    resource_units_used: float


@dataclass(frozen=True)
class QualificationAssessment:
    sufficient: bool
    reasons: tuple[str, ...]
    resource_units_used: float
    claim_ceiling: str = "BOUNDED_QUALIFICATION_ASSESSMENT"


def derive_qualification_budget(profile: ActionRiskProfile) -> QualificationBudget:
    if not 0.0 <= profile.materiality <= 1.0:
        raise ValueError("materiality must be within 0..1")
    if not 0.0 <= profile.uncertainty <= 1.0:
        raise ValueError("uncertainty must be within 0..1")

    hard_deep = (
        profile.safety_critical
        or profile.physical_world_intervention
        or profile.crosses_authority_boundary
    )
    confirmation = (
        profile.financial_commitment
        or profile.external_publication
        or profile.physical_world_intervention
        or profile.crosses_authority_boundary
    )

    if hard_deep:
        return QualificationBudget(
            QualificationDepth.DEEP,
            minimum_evidence_items=3,
            independent_check_required=True,
            explicit_human_confirmation_required=confirmation,
            reasons=("HARD_RISK_REQUIRES_DEEP_QUALIFICATION",),
        )

    if (
        profile.touches_private_data
        or profile.financial_commitment
        or profile.external_publication
        or profile.materiality >= 0.60
        or profile.uncertainty >= 0.60
        or not profile.reversible
    ):
        return QualificationBudget(
            QualificationDepth.STANDARD,
            minimum_evidence_items=2,
            independent_check_required=(
                not profile.reversible or profile.materiality >= 0.80
            ),
            explicit_human_confirmation_required=confirmation,
            reasons=("MATERIAL_OR_BOUNDARY_RISK_REQUIRES_STANDARD_QUALIFICATION",),
        )

    return QualificationBudget(
        QualificationDepth.LIGHT,
        minimum_evidence_items=1,
        independent_check_required=False,
        explicit_human_confirmation_required=False,
        reasons=("LOW_RISK_REVERSIBLE_ACTION_CAN_USE_MINIMUM_SUFFICIENT_QUALIFICATION",),
    )


def assess_qualification(
    budget: QualificationBudget,
    execution: QualificationExecution,
) -> QualificationAssessment:
    missing: list[str] = []
    if execution.depth_used < budget.required_depth:
        missing.append("QUALIFICATION_DEPTH_BELOW_REQUIRED")
    if execution.evidence_items < budget.minimum_evidence_items:
        missing.append("EVIDENCE_FLOOR_NOT_MET")
    if budget.independent_check_required and not execution.independent_check_observed:
        missing.append("INDEPENDENT_CHECK_REQUIRED")
    if (
        budget.explicit_human_confirmation_required
        and not execution.human_confirmation_observed
    ):
        missing.append("HUMAN_CONFIRMATION_REQUIRED")

    if missing:
        return QualificationAssessment(
            False,
            tuple(missing),
            execution.resource_units_used,
        )

    return QualificationAssessment(
        True,
        (
            "MINIMUM_SUFFICIENT_QUALIFICATION_MET",
            "EXTRA_RESOURCE_USE_IS_NOT_REQUIRED_BY_THIS_BUDGET",
        ),
        execution.resource_units_used,
    )
