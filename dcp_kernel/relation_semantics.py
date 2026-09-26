from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class RelationState(str, Enum):
    MATERIAL_RELATION = "MATERIAL_RELATION"
    STATIC_RELATION_ONLY = "STATIC_RELATION_ONLY"
    IDENTITY_RESOLUTION_GAP = "IDENTITY_RESOLUTION_GAP"


@dataclass(frozen=True)
class RelationInput:
    source_identity_resolved: bool
    target_identity_resolved: bool
    direction_known: bool
    reciprocity_relevant: bool = False
    reciprocity_defined: bool = False
    state_defined: bool = False
    time_defined: bool = False
    evidence_defined: bool = False
    authority_relevant: bool = False
    authority_defined: bool = False
    cost_relevant: bool = False
    cost_defined: bool = False
    risk_relevant: bool = False
    risk_defined: bool = False
    effect_defined: bool = False
    reversibility_relevant: bool = False
    reversibility_defined: bool = False
    return_path_relevant: bool = False
    return_path_defined: bool = False


@dataclass(frozen=True)
class RelationAssessment:
    decision: Decision
    state: RelationState
    missing_dimensions: tuple[str, ...]
    reasons: tuple[str, ...]


def assess_relation(item: RelationInput) -> RelationAssessment:
    if not item.source_identity_resolved or not item.target_identity_resolved:
        return RelationAssessment(
            Decision.HOLD,
            RelationState.IDENTITY_RESOLUTION_GAP,
            (),
            ("RELATION_ENDPOINT_IDENTITY_MUST_RESOLVE_BEFORE_RELATION_INFERENCE",),
        )

    missing: list[str] = []
    if not item.direction_known:
        missing.append("direction")
    if item.reciprocity_relevant and not item.reciprocity_defined:
        missing.append("reciprocity")
    if not item.state_defined:
        missing.append("state")
    if not item.time_defined:
        missing.append("time")
    if not item.evidence_defined:
        missing.append("evidence")
    if item.authority_relevant and not item.authority_defined:
        missing.append("authority")
    if item.cost_relevant and not item.cost_defined:
        missing.append("cost")
    if item.risk_relevant and not item.risk_defined:
        missing.append("risk")
    if not item.effect_defined:
        missing.append("effect")
    if item.reversibility_relevant and not item.reversibility_defined:
        missing.append("reversibility")
    if item.return_path_relevant and not item.return_path_defined:
        missing.append("return_path")

    if missing:
        return RelationAssessment(
            Decision.HOLD,
            RelationState.STATIC_RELATION_ONLY,
            tuple(missing),
            ("A_TO_B_LINK_IS_NOT_SUFFICIENT_FOR_MATERIAL_RELATION",),
        )

    return RelationAssessment(
        Decision.PASS,
        RelationState.MATERIAL_RELATION,
        (),
        ("RELATION_HAS_REQUIRED_LIFECYCLE_CONTEXT",),
    )
