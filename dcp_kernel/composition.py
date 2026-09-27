from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .models import Decision


class UnitState(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    HELD = "HELD"
    EXCLUDED = "EXCLUDED"


@dataclass(frozen=True)
class CompositionUnit:
    unit_id: str
    source_id: str
    lifecycle_state: str
    authority_allowed: bool
    rights_allowed: bool
    evidence_sufficient: bool
    compatible: bool
    fidelity_preserved: bool
    claim_ceiling: str


@dataclass(frozen=True)
class CompositionInput:
    composition_id: str
    required_effect: str
    receiver: str
    units: tuple[CompositionUnit, ...]


@dataclass(frozen=True)
class UnitDisposition:
    unit_id: str
    state: UnitState
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class CompositionAssessment:
    decision: Decision
    composition_id: str
    used_units: tuple[str, ...]
    held_units: tuple[str, ...]
    excluded_units: tuple[str, ...]
    dispositions: tuple[UnitDisposition, ...]
    reasons: tuple[str, ...]


def assess_composition(item: CompositionInput) -> CompositionAssessment:
    """Compose only eligible units without inflating authority or claim ceiling.

    The function filters units by rights/authority/evidence/compatibility/fidelity.
    It does not execute work, approve the result, or upgrade the composed claim.
    """

    dispositions: list[UnitDisposition] = []
    used: list[str] = []
    held: list[str] = []
    excluded: list[str] = []

    for unit in item.units:
        reasons: list[str] = []
        if not unit.rights_allowed:
            reasons.append("RIGHTS_NOT_ALLOWED")
        if not unit.authority_allowed:
            reasons.append("AUTHORITY_NOT_ALLOWED")

        if reasons:
            excluded.append(unit.unit_id)
            dispositions.append(UnitDisposition(unit.unit_id, UnitState.EXCLUDED, tuple(reasons)))
            continue

        if not unit.evidence_sufficient:
            reasons.append("EVIDENCE_INSUFFICIENT")
        if not unit.compatible:
            reasons.append("COMPATIBILITY_NOT_ESTABLISHED")
        if not unit.fidelity_preserved:
            reasons.append("FIDELITY_NOT_PRESERVED")
        if unit.lifecycle_state.upper() in {"PENDING", "HOLD", "CONFLICT", "HISTORICAL"}:
            reasons.append("LIFECYCLE_STATE_NOT_CURRENTLY_ELIGIBLE")

        if reasons:
            held.append(unit.unit_id)
            dispositions.append(UnitDisposition(unit.unit_id, UnitState.HELD, tuple(reasons)))
            continue

        used.append(unit.unit_id)
        dispositions.append(UnitDisposition(unit.unit_id, UnitState.ELIGIBLE, ("ELIGIBLE_FOR_BOUNDED_COMPOSITION",)))

    if not used:
        return CompositionAssessment(
            decision=Decision.HOLD,
            composition_id=item.composition_id,
            used_units=(),
            held_units=tuple(held),
            excluded_units=tuple(excluded),
            dispositions=tuple(dispositions),
            reasons=("NO_ELIGIBLE_UNITS_FOR_REQUIRED_EFFECT",),
        )

    return CompositionAssessment(
        decision=Decision.PASS,
        composition_id=item.composition_id,
        used_units=tuple(used),
        held_units=tuple(held),
        excluded_units=tuple(excluded),
        dispositions=tuple(dispositions),
        reasons=(
            "BOUNDED_COMPOSITION_CANDIDATE",
            "LOCAL_COMPOSITION_DOES_NOT_IMPLY_GLOBAL_CLOSURE",
            "OUTPUT_FORMAT_DOES_NOT_CHANGE_CLAIM_CEILING",
        ),
    )
