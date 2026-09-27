from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class TriggerClass(str, Enum):
    EVENT_DRIVEN = "EVENT_DRIVEN"
    PERIODIC = "PERIODIC"
    CONDITION_WATCH = "CONDITION_WATCH"
    MANUAL_GATED = "MANUAL_GATED"


class ScheduleEffectState(str, Enum):
    EFFECTIVE = "EFFECTIVE"
    HOLD_MISSING_EFFECT_EVIDENCE = "HOLD_MISSING_EFFECT_EVIDENCE"
    HOLD_RETURN_INCOMPLETE = "HOLD_RETURN_INCOMPLETE"
    HOLD_STALE_OR_MISSED = "HOLD_STALE_OR_MISSED"
    HOLD_RECEIVER_UNRESOLVED = "HOLD_RECEIVER_UNRESOLVED"
    HOLD_ACTION_AUTHORITY = "HOLD_ACTION_AUTHORITY"
    FAIL_SCOPE_VIOLATION = "FAIL_SCOPE_VIOLATION"
    FAIL_IDENTITY_DRIFT = "FAIL_IDENTITY_DRIFT"


@dataclass(frozen=True)
class ScheduleEffectInput:
    schedule_id: str
    trigger_class: TriggerClass
    receiver: str | None
    expected_effect: str
    effect_evidence_present: bool
    mutation_requested: bool = False
    action_authority_valid: bool = False
    action_within_scope: bool = True
    return_target: str | None = None
    return_reconciled: bool = False
    stale_or_missed: bool = False
    carrier_id: str | None = None
    prior_carrier_id: str | None = None
    stable_schedule_identity_preserved: bool = True


@dataclass(frozen=True)
class ScheduleEffectAssessment:
    decision: Decision
    state: ScheduleEffectState
    effective: bool
    reasons: tuple[str, ...]


def assess_schedule_effect(item: ScheduleEffectInput) -> ScheduleEffectAssessment:
    """Evaluate schedule effect evidence without turning cadence or tool names into Runtime.

    Trigger class determines when evaluation may occur, not who is authorized to mutate.
    Carrier replacement is allowed only when stable schedule identity is preserved.
    """

    if not item.stable_schedule_identity_preserved:
        return ScheduleEffectAssessment(
            decision=Decision.FAIL,
            state=ScheduleEffectState.FAIL_IDENTITY_DRIFT,
            effective=False,
            reasons=("CARRIER_CHANGE_BROKE_STABLE_SCHEDULE_IDENTITY",),
        )

    if item.receiver is None:
        return ScheduleEffectAssessment(
            decision=Decision.HOLD,
            state=ScheduleEffectState.HOLD_RECEIVER_UNRESOLVED,
            effective=False,
            reasons=("RECEIVER_UNRESOLVED",),
        )

    if item.mutation_requested and not item.action_authority_valid:
        return ScheduleEffectAssessment(
            decision=Decision.HOLD,
            state=ScheduleEffectState.HOLD_ACTION_AUTHORITY,
            effective=False,
            reasons=("MUTATION_REQUIRES_ACTION_AUTHORITY",),
        )

    if item.mutation_requested and not item.action_within_scope:
        return ScheduleEffectAssessment(
            decision=Decision.FAIL,
            state=ScheduleEffectState.FAIL_SCOPE_VIOLATION,
            effective=False,
            reasons=("MUTATION_OUTSIDE_ALLOWED_SCOPE",),
        )

    if item.stale_or_missed:
        return ScheduleEffectAssessment(
            decision=Decision.HOLD,
            state=ScheduleEffectState.HOLD_STALE_OR_MISSED,
            effective=False,
            reasons=("SCHEDULE_EFFECT_STALE_OR_MISSED",),
        )

    if not item.effect_evidence_present:
        return ScheduleEffectAssessment(
            decision=Decision.HOLD,
            state=ScheduleEffectState.HOLD_MISSING_EFFECT_EVIDENCE,
            effective=False,
            reasons=("CADENCE_OR_TRIGGER_DOES_NOT_PROVE_EFFECT",),
        )

    if item.return_target != item.receiver or not item.return_reconciled:
        return ScheduleEffectAssessment(
            decision=Decision.HOLD,
            state=ScheduleEffectState.HOLD_RETURN_INCOMPLETE,
            effective=False,
            reasons=("EFFECT_OUTPUT_EXISTS_BUT_RETURN_RECONCILIATION_INCOMPLETE",),
        )

    return ScheduleEffectAssessment(
        decision=Decision.PASS,
        state=ScheduleEffectState.EFFECTIVE,
        effective=True,
        reasons=("BOUNDED_EFFECT_EVIDENCED_AND_RETURN_RECONCILED",),
    )
