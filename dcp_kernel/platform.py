from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Mapping, Sequence

from .action_gate import EffectClass
from .activation import ActivationAssessment, ActivationState
from .decision_chain import DecisionChainAssessment
from .models import (
    AffectedCone,
    CapabilityBinding,
    CapabilityResolution,
    CurrentCandidate,
    CurrentResolution,
    CurrentResolutionStatus,
    Decision,
    Need,
    ReentryState,
    ReturnState,
    StableLife,
    Transition,
    TransitionEvaluation,
    TriRootState,
)
from .resolution import compute_affected_cone, resolve_capability_binding, resolve_current
from .return_state import ReturnClosure
from .transition import evaluate_transition
from .write_intent import WriteIntentAssessment


@dataclass(frozen=True)
class WorkContract:
    contract_id: str
    stable_life_id: str
    transition_id: str
    capability_id: str
    actor_id: str
    carrier_id: str
    receiver: str
    affected_receivers: tuple[str, ...]
    state: str = "CANDIDATE"


@dataclass(frozen=True)
class PlatformPlan:
    decision: Decision
    current: CurrentResolution
    capability: CapabilityResolution
    affected_cone: AffectedCone
    transition: TransitionEvaluation | None
    work_contract: WorkContract | None
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlatformLoopResult:
    decision: Decision
    plan: PlatformPlan
    closure: ReturnClosure
    reentry: ReentryState | None
    reasons: tuple[str, ...] = ()


def compile_work_contract(
    *,
    stable_life: StableLife,
    tri_root: TriRootState,
    need: Need,
    capability_candidates: Iterable[CapabilityBinding],
    current_candidates: Sequence[CurrentCandidate],
    changed_nodes: Iterable[str],
    dependency_graph: Mapping[str, Sequence[str]],
    eligible_receivers: set[str],
    transition: Transition,
) -> PlatformPlan:
    """Compatibility compiler for bounded candidate work.

    This path never executes or approves work. New mutation-oriented callers should
    prefer compile_governed_work_contract(), which also enforces pre-action judgment
    and write-intent boundaries.
    """

    current = resolve_current(
        stable_life_id=stable_life.life_id,
        last_good_revision=stable_life.last_good_revision,
        candidates=current_candidates,
    )
    empty_capability = CapabilityResolution(
        decision=Decision.HOLD,
        binding=None,
        reasons=("CURRENT_NOT_RESOLVED",),
    )
    empty_cone = AffectedCone(affected=(), excluded={})

    if current.status is not CurrentResolutionStatus.CURRENT:
        return PlatformPlan(Decision.HOLD, current, empty_capability, empty_cone, None, None, ("CURRENT_NOT_RESOLVED",))

    capability = resolve_capability_binding(need, capability_candidates)
    if capability.decision is not Decision.PASS or capability.binding is None:
        return PlatformPlan(capability.decision, current, capability, empty_cone, None, None, capability.reasons)

    affected_cone = compute_affected_cone(
        changed_nodes=changed_nodes,
        dependency_graph=dependency_graph,
        eligible_receivers=eligible_receivers,
    )
    if need.receiver not in affected_cone.affected:
        return PlatformPlan(
            Decision.HOLD,
            current,
            capability,
            affected_cone,
            None,
            None,
            ("RETURN_RECEIVER_NOT_IN_AFFECTED_CONE",),
        )

    effective_life = replace(stable_life, current_revision=current.selected_revision or stable_life.current_revision)
    transition_evaluation = evaluate_transition(effective_life, tri_root, capability.binding, transition)
    if transition_evaluation.decision is not Decision.PASS:
        return PlatformPlan(
            transition_evaluation.decision,
            current,
            capability,
            affected_cone,
            transition_evaluation,
            None,
            (
                transition_evaluation.first_material_break.motion.value
                if transition_evaluation.first_material_break
                else "TRANSITION_NOT_PASS",
            ),
        )

    contract = WorkContract(
        contract_id=f"WORK-{transition.transition_id}",
        stable_life_id=stable_life.life_id,
        transition_id=transition.transition_id,
        capability_id=capability.binding.capability_id,
        actor_id=capability.binding.actor_id,
        carrier_id=capability.binding.carrier_id,
        receiver=need.receiver,
        affected_receivers=affected_cone.affected,
    )
    return PlatformPlan(Decision.PASS, current, capability, affected_cone, transition_evaluation, contract)


def _blocked_pre_action_plan(
    *,
    decision: Decision,
    reason_prefix: str,
    reasons: tuple[str, ...],
) -> PlatformPlan:
    current = CurrentResolution(
        status=CurrentResolutionStatus.HOLD,
        selected_revision=None,
        reasons=(reason_prefix,),
    )
    capability = CapabilityResolution(
        decision=Decision.HOLD,
        binding=None,
        reasons=reasons,
    )
    return PlatformPlan(
        decision=decision,
        current=current,
        capability=capability,
        affected_cone=AffectedCone(affected=(), excluded={}),
        transition=None,
        work_contract=None,
        reasons=(reason_prefix,) + reasons,
    )


def _no_action_plan(*, stable_life: StableLife) -> PlatformPlan:
    """Represent a deliberate no-action judgment without creating work.

    Choosing not to act is a valid governed outcome. It does not require a
    capability lease, carrier binding, mutation intent, or WorkContract.
    """

    current = CurrentResolution(
        status=CurrentResolutionStatus.CURRENT,
        selected_revision=stable_life.current_revision,
        reasons=("NO_ACTION_SELECTED_CURRENT_PRESERVED",),
    )
    capability = CapabilityResolution(
        decision=Decision.PASS,
        binding=None,
        reasons=("NO_CAPABILITY_LEASE_REQUIRED_FOR_NO_ACTION",),
    )
    return PlatformPlan(
        decision=Decision.PASS,
        current=current,
        capability=capability,
        affected_cone=AffectedCone(affected=(), excluded={}),
        transition=None,
        work_contract=None,
        reasons=(
            "NO_ACTION_SELECTED",
            "RESTRAINT_PRESERVED_WITHOUT_CREATING_WORK",
        ),
    )


def compile_governed_work_contract(
    *,
    decision_chain: DecisionChainAssessment,
    stable_life: StableLife,
    tri_root: TriRootState,
    need: Need,
    capability_candidates: Iterable[CapabilityBinding],
    current_candidates: Sequence[CurrentCandidate],
    changed_nodes: Iterable[str],
    dependency_graph: Mapping[str, Sequence[str]],
    eligible_receivers: set[str],
    transition: Transition,
    write_intent: WriteIntentAssessment | None = None,
) -> PlatformPlan:
    """Preferred successor compiler with judgment and mutation boundaries.

    Meaning, judgment, coexistence/translation and restraint must pass first.
    A carrier-neutral WriteIntent is required only when the *proposed* effect is
    an actual mutation. If the chosen action is NO_ACTION, the valid result is a
    PASS with no capability lease and no WorkContract.

    Neither DecisionChain PASS nor WriteIntent PASS grants execution authority.
    """

    if decision_chain.decision is not Decision.PASS:
        return _blocked_pre_action_plan(
            decision=decision_chain.decision,
            reason_prefix=f"PRE_ACTION_{decision_chain.first_break or 'CHAIN'}_NOT_PASS",
            reasons=decision_chain.reasons,
        )

    if decision_chain.action_gate.proposed_effect == EffectClass.NO_ACTION:
        return _no_action_plan(stable_life=stable_life)

    mutation_requested = (
        decision_chain.action_gate.proposed_effect >= EffectClass.BOUNDED_MUTATION
    )
    if mutation_requested:
        if write_intent is None:
            return _blocked_pre_action_plan(
                decision=Decision.HOLD,
                reason_prefix="PRE_ACTION_WRITE_INTENT_MISSING",
                reasons=("MUTATION_REQUIRES_CARRIER_NEUTRAL_WRITE_INTENT",),
            )
        if write_intent.decision is not Decision.PASS or not write_intent.mutation_allowed_as_candidate:
            return _blocked_pre_action_plan(
                decision=write_intent.decision,
                reason_prefix="PRE_ACTION_WRITE_INTENT_NOT_PASS",
                reasons=write_intent.reasons,
            )

    return compile_work_contract(
        stable_life=stable_life,
        tri_root=tri_root,
        need=need,
        capability_candidates=capability_candidates,
        current_candidates=current_candidates,
        changed_nodes=changed_nodes,
        dependency_graph=dependency_graph,
        eligible_receivers=eligible_receivers,
        transition=transition,
    )


def compile_event_governed_work_contract(
    *,
    activation: ActivationAssessment,
    decision_chain: DecisionChainAssessment,
    stable_life: StableLife,
    tri_root: TriRootState,
    need: Need,
    capability_candidates: Iterable[CapabilityBinding],
    current_candidates: Sequence[CurrentCandidate],
    changed_nodes: Iterable[str],
    dependency_graph: Mapping[str, Sequence[str]],
    eligible_receivers: set[str],
    transition: Transition,
    write_intent: WriteIntentAssessment | None = None,
) -> PlatformPlan:
    """Compile bounded work only after a material event legitimately wakes state.

    Persistent state is sufficient; a persistent agent is not required. Sleep,
    HOLD, or unresolved wake signals cannot produce a WorkContract candidate.
    """

    if (
        activation.decision is not Decision.PASS
        or activation.activation_state is not ActivationState.WAKE_CANDIDATE
        or not activation.wake_permitted_as_candidate
    ):
        return _blocked_pre_action_plan(
            decision=activation.decision if activation.decision is not Decision.PASS else Decision.HOLD,
            reason_prefix="EVENT_ACTIVATION_NOT_WAKE_CANDIDATE",
            reasons=activation.reasons,
        )

    return compile_governed_work_contract(
        decision_chain=decision_chain,
        stable_life=stable_life,
        tri_root=tri_root,
        need=need,
        capability_candidates=capability_candidates,
        current_candidates=current_candidates,
        changed_nodes=changed_nodes,
        dependency_graph=dependency_graph,
        eligible_receivers=eligible_receivers,
        transition=transition,
        write_intent=write_intent,
    )


def build_reentry_state(
    *,
    stable_life: StableLife,
    tri_root: TriRootState,
    closure: ReturnClosure,
    receiver_rebuild_revision: str,
    receiver_tri_root_revision: str | None = None,
    last_good_revision: str | None = None,
    active_need: str | None = None,
    blockers: tuple[str, ...] = (),
    cursor: str | None = None,
    ack_owner: str | None = None,
) -> ReentryState:
    """Build typed re-entry only after receiver-owned rebuild resolution exists."""

    rebuild_resolved_states = {
        ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
        ReturnState.BEHAVIOR_DELTA_OBSERVED,
        ReturnState.RETESTED,
    }
    if closure.state not in rebuild_resolved_states:
        raise ValueError("REENTRY_REQUIRES_RECEIVER_REBUILD_RESOLUTION")

    unresolved_after_rebuild = closure.outstanding_debt
    return ReentryState(
        stable_life_id=stable_life.life_id,
        invariant_core_id=stable_life.invariant_core.identity_anchor,
        tri_root_revision=receiver_tri_root_revision or tri_root.source_revision,
        current_revision=receiver_rebuild_revision,
        last_good_revision=last_good_revision or receiver_rebuild_revision,
        active_need=active_need,
        blockers=tuple(dict.fromkeys(blockers + unresolved_after_rebuild)),
        pending_returns=(),
        cursor=cursor,
        ack_owner=ack_owner or closure.receiver,
    )


def complete_fixture_loop(
    *,
    plan: PlatformPlan,
    return_id: str,
    receiver: str,
    stable_life: StableLife,
    tri_root: TriRootState,
    rebuilt_revision: str,
) -> PlatformLoopResult:
    """Deterministically simulate a full closure for fixtures/tests only.

    This helper is evidence for platform semantics, not evidence of a real receiver
    reading or applying a Return in a live system.
    """

    if plan.decision is not Decision.PASS or plan.work_contract is None:
        closure = ReturnClosure(return_id=return_id, receiver=receiver)
        return PlatformLoopResult(plan.decision, plan, closure, None, ("WORK_CONTRACT_NOT_AVAILABLE",))

    closure = ReturnClosure(return_id=return_id, receiver=receiver)
    closure = closure.advance(ReturnState.ROUTED)
    closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
    closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
    closure = closure.advance(
        ReturnState.RECEIVER_NATIVE_DISPOSITION,
        native_disposition="FIXTURE_ACCEPTED",
    )
    closure = closure.advance(ReturnState.RECONCILED)
    closure = closure.advance(
        ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
        rebuild_applied=True,
    )
    closure = closure.advance(
        ReturnState.BEHAVIOR_DELTA_OBSERVED,
        behavior_delta_observed=True,
    )
    closure = closure.advance(ReturnState.RETESTED, retested=True)

    reentry = build_reentry_state(
        stable_life=stable_life,
        tri_root=tri_root,
        closure=closure,
        receiver_rebuild_revision=rebuilt_revision,
    )
    return PlatformLoopResult(Decision.PASS, plan, closure, reentry)
