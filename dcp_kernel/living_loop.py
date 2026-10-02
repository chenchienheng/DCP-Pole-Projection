from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision
from .operable_birth import BirthDisposition, OperableBirthAssessment
from .public_encounter import PublicEncounterAssessment
from .reception_gateway import GatewayAssessment, GatewayDisposition
from .relation_semantics import RelationAssessment, RelationState


class LivingLoopBreak(str, Enum):
    NONE = "NONE"
    GATEWAY = "GATEWAY"
    RELATION = "RELATION"
    PUBLIC_ENCOUNTER = "PUBLIC_ENCOUNTER"
    RETURN_REBUILD = "RETURN_REBUILD"
    BIRTH_REGRESSION = "BIRTH_REGRESSION"


@dataclass(frozen=True)
class LivingLoopInput:
    gateway: GatewayAssessment
    relation: RelationAssessment
    birth: OperableBirthAssessment
    public_encounter: PublicEncounterAssessment | None = None


@dataclass(frozen=True)
class LivingLoopAssessment:
    decision: Decision
    first_break: LivingLoopBreak
    operable_birth_delta: bool
    routed_receivers: tuple[str, ...]
    reasons: tuple[str, ...]


def assess_living_loop(item: LivingLoopInput) -> LivingLoopAssessment:
    """Compose existing gates without inventing a second policy layer.

    Component modules remain the source of their own judgment. This function only
    preserves execution order and exposes the first material break across the
    minimal external-request-to-rebuild slice.
    """

    if item.gateway.decision is not Decision.PASS:
        return LivingLoopAssessment(
            item.gateway.decision,
            LivingLoopBreak.GATEWAY,
            False,
            item.gateway.routed_receivers,
            item.gateway.reasons,
        )

    if item.gateway.disposition is GatewayDisposition.OBSERVE_ONLY:
        return LivingLoopAssessment(
            Decision.PASS,
            LivingLoopBreak.NONE,
            False,
            (),
            ("NON_MATERIAL_REQUEST_STOPS_WITHOUT_NATIVE_WAKE",),
        )

    if item.relation.decision is not Decision.PASS or item.relation.state is not RelationState.MATERIAL_RELATION:
        return LivingLoopAssessment(
            item.relation.decision,
            LivingLoopBreak.RELATION,
            False,
            item.gateway.routed_receivers,
            item.relation.reasons + item.relation.missing_dimensions,
        )

    if item.public_encounter is not None and item.public_encounter.decision is not Decision.PASS:
        return LivingLoopAssessment(
            item.public_encounter.decision,
            LivingLoopBreak.PUBLIC_ENCOUNTER,
            False,
            item.gateway.routed_receivers,
            item.public_encounter.reasons,
        )

    if item.birth.disposition is BirthDisposition.BIRTH_REGRESSION:
        return LivingLoopAssessment(
            item.birth.decision,
            LivingLoopBreak.BIRTH_REGRESSION,
            False,
            item.gateway.routed_receivers,
            item.birth.reasons,
        )

    if item.birth.disposition is BirthDisposition.RETURN_NOT_REBUILT:
        return LivingLoopAssessment(
            item.birth.decision,
            LivingLoopBreak.RETURN_REBUILD,
            False,
            item.gateway.routed_receivers,
            item.birth.reasons + item.birth.missing,
        )

    return LivingLoopAssessment(
        item.birth.decision,
        LivingLoopBreak.NONE if item.birth.decision is Decision.PASS else LivingLoopBreak.RETURN_REBUILD,
        item.birth.disposition is BirthDisposition.OPERABLE_BIRTH_DELTA,
        item.gateway.routed_receivers,
        item.birth.reasons,
    )
