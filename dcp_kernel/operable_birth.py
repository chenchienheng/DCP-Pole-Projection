from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class BirthDisposition(str, Enum):
    OPERABLE_BIRTH_DELTA = "OPERABLE_BIRTH_DELTA"
    NO_OPERABLE_BIRTH_DELTA = "NO_OPERABLE_BIRTH_DELTA"
    BIRTH_REGRESSION = "BIRTH_REGRESSION"
    RETURN_NOT_REBUILT = "RETURN_NOT_REBUILT"


@dataclass(frozen=True)
class OperableBirthInput:
    existence_resolved: bool
    relation_resolved: bool
    event_materiality_resolved: bool
    judgment_before_capability: bool
    capability_bound: bool
    action_gated: bool
    evidence_recorded: bool
    receiver_disposition_observed: bool
    rebuild_applied: bool
    new_state_observed: bool
    retested: bool
    centralization_increased: bool = False
    carrier_dependency_increased: bool = False
    second_truth_created: bool = False
    human_gateway_load_increased: bool = False


@dataclass(frozen=True)
class OperableBirthAssessment:
    decision: Decision
    disposition: BirthDisposition
    missing: tuple[str, ...]
    reasons: tuple[str, ...]


def assess_operable_birth(item: OperableBirthInput) -> OperableBirthAssessment:
    if any(
        (
            item.centralization_increased,
            item.carrier_dependency_increased,
            item.second_truth_created,
            item.human_gateway_load_increased,
        )
    ):
        return OperableBirthAssessment(
            Decision.FAIL,
            BirthDisposition.BIRTH_REGRESSION,
            (),
            ("WORK_INCREASED_CENTRALIZATION_CARRIER_DEPENDENCY_SECOND_TRUTH_OR_HUMAN_GATEWAY_LOAD",),
        )

    before_return = {
        "existence": item.existence_resolved,
        "relation": item.relation_resolved,
        "event": item.event_materiality_resolved,
        "judgment": item.judgment_before_capability,
        "capability": item.capability_bound,
        "action": item.action_gated,
        "evidence": item.evidence_recorded,
    }
    missing_before = tuple(name for name, present in before_return.items() if not present)
    if missing_before:
        return OperableBirthAssessment(
            Decision.HOLD,
            BirthDisposition.NO_OPERABLE_BIRTH_DELTA,
            missing_before,
            ("MINIMUM_OPERABLE_CHAIN_NOT_YET_PRESENT",),
        )

    if not item.receiver_disposition_observed or not item.rebuild_applied:
        missing = []
        if not item.receiver_disposition_observed:
            missing.append("receiver_disposition")
        if not item.rebuild_applied:
            missing.append("rebuild")
        return OperableBirthAssessment(
            Decision.HOLD,
            BirthDisposition.RETURN_NOT_REBUILT,
            tuple(missing),
            ("RETURN_EXISTS_WITHOUT_RECEIVER_OWNED_REBUILD",),
        )

    missing_after = []
    if not item.new_state_observed:
        missing_after.append("new_state")
    if not item.retested:
        missing_after.append("retest")
    if missing_after:
        return OperableBirthAssessment(
            Decision.HOLD,
            BirthDisposition.NO_OPERABLE_BIRTH_DELTA,
            tuple(missing_after),
            ("REBUILD_REQUIRES_OBSERVABLE_NEW_STATE_AND_RETEST_FOR_BIRTH_CREDIT",),
        )

    return OperableBirthAssessment(
        Decision.PASS,
        BirthDisposition.OPERABLE_BIRTH_DELTA,
        (),
        ("FULL_MINIMUM_LIVING_CHAIN_OBSERVED",),
    )
