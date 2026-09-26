from __future__ import annotations

from dataclasses import dataclass

from .models import Decision, ReturnState
from .platform import PlatformPlan


@dataclass(frozen=True)
class ActionResponsibilityContract:
    transition_id: str
    stable_life_id: str
    actor_id: str
    responsibility_owner: str
    consequence_summary: str
    blast_radius: tuple[str, ...]
    return_target: str
    rebuild_target: str
    state: str = "CANDIDATE"


@dataclass(frozen=True)
class ConsequenceInput:
    transition_id: str
    observed_effect: str | None
    impact: tuple[str, ...] = ()
    cost: tuple[str, ...] = ()
    side_effects: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    affected_receivers: tuple[str, ...] = ()
    responsibility_owner: str | None = None
    return_state: ReturnState = ReturnState.PRODUCED
    receiver_disposition: str | None = None
    rebuild_revision: str | None = None
    behavior_delta: str | None = None
    retest_result: str | None = None
    material_gap_after_return: bool | None = None


@dataclass(frozen=True)
class ConsequenceAssessment:
    decision: Decision
    transition_id: str
    next_condition_ready: bool
    next_dependencies: tuple[str, ...]
    next_need_required: bool | None
    reasons: tuple[str, ...]


def compile_action_responsibility(plan: PlatformPlan) -> ActionResponsibilityContract:
    """Bind action rights to consequence responsibility for the same transition."""

    if plan.decision is not Decision.PASS or plan.work_contract is None:
        raise ValueError("RESPONSIBILITY_CONTRACT_REQUIRES_COMPILED_WORK_CONTRACT")
    if plan.capability.binding is None:
        raise ValueError("RESPONSIBILITY_CONTRACT_REQUIRES_CAPABILITY_BINDING")
    if not plan.capability.binding.return_target:
        raise ValueError("RESPONSIBILITY_CONTRACT_REQUIRES_RETURN_TARGET")
    if plan.transition is None:
        raise ValueError("RESPONSIBILITY_CONTRACT_REQUIRES_TRANSITION")

    return ActionResponsibilityContract(
        transition_id=plan.work_contract.transition_id,
        stable_life_id=plan.work_contract.stable_life_id,
        actor_id=plan.work_contract.actor_id,
        responsibility_owner=plan.work_contract.actor_id,
        consequence_summary="OBSERVE_ACTUAL_EFFECT_AND_CONSEQUENCES",
        blast_radius=plan.affected_cone.affected,
        return_target=plan.capability.binding.return_target,
        rebuild_target=plan.work_contract.receiver,
    )


def derive_next_condition(item: ConsequenceInput) -> ConsequenceAssessment:
    """Treat result as the next condition rather than an terminal effect report."""

    reasons: list[str] = []
    next_dependencies: list[str] = []

    if not item.observed_effect:
        reasons.append("OBSERVED_EFFECT_MISSING")
    if not item.responsibility_owner:
        reasons.append("RESPONSIBILITY_OWNER_MISSING")
    if not item.evidence_refs:
        reasons.append("CONSEQUENCE_EVIDENCE_MISSING")
    if not item.affected_receivers:
        reasons.append("AFFECTED_RECEIVER_MISSING")

    if item.return_state.value in {
        ReturnState.PRODUCED.value,
        ReturnState.ROUTED.value,
        ReturnState.ACTUAL_READ.value,
        ReturnState.MATERIALITY_RESOLVED.value,
    }:
        reasons.append("RETURN_NOT_AT_NATIVE_DISPOSITION")
    if not item.receiver_disposition:
        reasons.append("RECEIVER_DISPOSITION_MISSING")
    if not item.rebuild_revision:
        reasons.append("REBUILD_REVISION_MISSING")
    if not item.behavior_delta:
        reasons.append("BEHAVIOR_DELTA_NOT_OBSERVED")
    if not item.retest_result:
        reasons.append("RETEST_NOT_OBSERVED")

    for receiver in item.affected_receivers:
        next_dependencies.append(f"receiver:{receiver}")
    for impact in item.impact:
        next_dependencies.append(f"impact:{impact}")
    for side_effect in item.side_effects:
        next_dependencies.append(f"side_effect:{side_effect}")
    for cost in item.cost:
        next_dependencies.append(f"cost:{cost}")

    if reasons:
        return ConsequenceAssessment(
            decision=Decision.HOLD,
            transition_id=item.transition_id,
            next_condition_ready=False,
            next_dependencies=tuple(dict.fromkeys(next_dependencies)),
            next_need_required=None,
            reasons=tuple(reasons),
        )

    if item.material_gap_after_return is True:
        next_need_required: bool | None = True
        terminal_reason = "MATERIAL_GAP_REQUIRES_NEXT_NEED"
    elif item.material_gap_after_return is False:
        next_need_required = False
        terminal_reason = "RETURN_CLOSED_NO_NEXT_NEED"
    else:
        next_need_required = None
        terminal_reason = "NEXT_NEED_MATERIALITY_UNKNOWN"

    return ConsequenceAssessment(
        decision=Decision.PASS,
        transition_id=item.transition_id,
        next_condition_ready=True,
        next_dependencies=tuple(dict.fromkeys(next_dependencies)),
        next_need_required=next_need_required,
        reasons=(
            "RESULT_COMPILED_AS_NEXT_CONDITION",
            terminal_reason,
        ),
    )
