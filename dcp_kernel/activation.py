from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class ActivationState(str, Enum):
    SLEEP = "SLEEP"
    WAKE_CANDIDATE = "WAKE_CANDIDATE"
    HOLD = "HOLD"


@dataclass(frozen=True)
class PersistentState:
    stable_life_id: str
    current_revision: str
    authority_ceiling: str
    last_good_revision: str | None
    active_need: str | None
    pending_return_debt: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    cursor: str | None = None


@dataclass(frozen=True)
class ActivationInput:
    event_id: str
    event_material: bool
    affected_stable_life_id: str | None
    state: PersistentState
    identity_match: bool
    authority_available: bool
    gate_known: bool
    affected_scope_known: bool
    return_path_known: bool


@dataclass(frozen=True)
class ActivationAssessment:
    decision: Decision
    activation_state: ActivationState
    wake_permitted_as_candidate: bool
    persistent_agent_required: bool
    reasons: tuple[str, ...]


def assess_activation(item: ActivationInput) -> ActivationAssessment:
    """Wake bounded work from persistent state without requiring a persistent agent.

    An event is only a wake signal. It does not grant authority or execution.
    Non-material events leave the life object asleep. Material events with missing
    identity/scope/authority/gate/return conditions remain HOLD.
    """

    if not item.event_material:
        return ActivationAssessment(
            decision=Decision.PASS,
            activation_state=ActivationState.SLEEP,
            wake_permitted_as_candidate=False,
            persistent_agent_required=False,
            reasons=("NON_MATERIAL_EVENT_DOES_NOT_WAKE_WORK",),
        )

    reasons: list[str] = []
    if item.affected_stable_life_id != item.state.stable_life_id or not item.identity_match:
        reasons.append("STABLE_IDENTITY_NOT_RESOLVED")
    if not item.authority_available:
        reasons.append("AUTHORITY_NOT_AVAILABLE")
    if not item.gate_known:
        reasons.append("WAKE_GATE_UNKNOWN")
    if not item.affected_scope_known:
        reasons.append("AFFECTED_SCOPE_UNKNOWN")
    if not item.return_path_known:
        reasons.append("RETURN_PATH_UNKNOWN")

    if reasons:
        return ActivationAssessment(
            decision=Decision.HOLD,
            activation_state=ActivationState.HOLD,
            wake_permitted_as_candidate=False,
            persistent_agent_required=False,
            reasons=tuple(reasons),
        )

    return ActivationAssessment(
        decision=Decision.PASS,
        activation_state=ActivationState.WAKE_CANDIDATE,
        wake_permitted_as_candidate=True,
        persistent_agent_required=False,
        reasons=(
            "PERSISTENT_STATE_RESOLVED_FOR_EVENT",
            "EVENT_MAY_WAKE_BOUNDED_DECISION_CHAIN",
            "WAKE_DOES_NOT_GRANT_EXECUTION_AUTHORITY",
        ),
    )
