from __future__ import annotations

from .models import (
    CapabilityBinding,
    Decision,
    Motion,
    MotionObservation,
    StableLife,
    Transition,
    TransitionEvaluation,
    TriRootState,
)

_MOTION_ORDER = (
    Motion.IDENTITY,
    Motion.MEANING,
    Motion.DEPENDENCY,
    Motion.STATE,
    Motion.REALITY,
    Motion.CAPABILITY,
    Motion.RETURN,
    Motion.CONTINUITY,
)


def _observation(
    transition: Transition,
    motion: Motion,
    decision: Decision,
    *reasons: str,
) -> MotionObservation:
    return MotionObservation(
        transition_id=transition.transition_id,
        motion=motion,
        decision=decision,
        reasons=tuple(reasons),
    )


def evaluate_transition(
    stable_life: StableLife,
    tri_root: TriRootState,
    binding: CapabilityBinding,
    transition: Transition,
) -> TransitionEvaluation:
    """Evaluate one transition through eight observations of one inner motion."""

    observations: list[MotionObservation] = []

    if transition.stable_life_id != stable_life.life_id:
        observations.append(
            _observation(
                transition,
                Motion.IDENTITY,
                Decision.FAIL,
                "STABLE_LIFE_ID_MISMATCH",
            )
        )
    elif (
        stable_life.invariant_core.world_truth_id is not None
        and transition.world_id_before is not None
        and transition.world_id_before
        != stable_life.invariant_core.world_truth_id
    ):
        observations.append(
            _observation(
                transition,
                Motion.IDENTITY,
                Decision.FAIL,
                "WORLD_ID_DOES_NOT_BACKMAP_TO_INVARIANT_CORE",
            )
        )
    else:
        observations.append(_observation(transition, Motion.IDENTITY, Decision.PASS))

    if not tri_root.meaning_preserved or not transition.meaning_preserved:
        observations.append(
            _observation(
                transition,
                Motion.MEANING,
                Decision.FAIL,
                "MEANING_INVARIANT_BROKEN",
            )
        )
    else:
        observations.append(_observation(transition, Motion.MEANING, Decision.PASS))

    if not tri_root.dependencies_resolved or not transition.dependencies_resolved:
        observations.append(
            _observation(
                transition,
                Motion.DEPENDENCY,
                Decision.HOLD,
                "AFFECTED_DEPENDENCY_UNRESOLVED",
            )
        )
    else:
        observations.append(_observation(transition, Motion.DEPENDENCY, Decision.PASS))

    if transition.source_revision != stable_life.current_revision:
        observations.append(
            _observation(
                transition,
                Motion.STATE,
                Decision.HOLD,
                "SOURCE_REVISION_IS_NOT_RESOLVED_CURRENT",
            )
        )
    else:
        observations.append(_observation(transition, Motion.STATE, Decision.PASS))

    reality_reasons: list[str] = []
    if (
        transition.world_id_before is not None
        and transition.world_id_after is not None
        and transition.world_id_before != transition.world_id_after
    ):
        reality_reasons.append("SECOND_WORLD_TRUTH_RISK")
    if (
        transition.requests_world_truth_mutation
        and not transition.world_receiver_authorized
    ):
        reality_reasons.append("WORLD_MUTATION_WITHOUT_RECEIVER_AUTHORITY")
    if transition.representation_only and transition.requests_world_truth_mutation:
        reality_reasons.append("REPRESENTATION_IMPERSONATES_WORLD_TRUTH")

    if reality_reasons:
        observations.append(
            _observation(
                transition,
                Motion.REALITY,
                Decision.FAIL,
                *reality_reasons,
            )
        )
    else:
        observations.append(_observation(transition, Motion.REALITY, Decision.PASS))

    capability_reasons: list[str] = []
    capability_fail = False
    capability_hold = False
    if binding.capability_id != transition.capability_id:
        capability_reasons.append("CAPABILITY_BINDING_MISMATCH")
        capability_fail = True
    if not binding.authority_granted:
        capability_reasons.append("AUTHORITY_NOT_GRANTED")
        capability_hold = True
    if not binding.rights_allowed:
        capability_reasons.append("RIGHTS_NOT_ALLOWED")
        capability_fail = True
    if not binding.evidence_available:
        capability_reasons.append("CAPABILITY_EVIDENCE_MISSING")
        capability_hold = True
    if transition.claims_native_capability and not binding.native_internalized:
        capability_reasons.append("EXTERNAL_CAPABILITY_NOT_NATIVE_INTERNALIZED")
        capability_fail = True

    capability_decision = (
        Decision.FAIL
        if capability_fail
        else Decision.HOLD
        if capability_hold
        else Decision.PASS
    )

    observations.append(
        _observation(
            transition,
            Motion.CAPABILITY,
            capability_decision,
            *capability_reasons,
        )
    )

    if binding.return_target is None:
        observations.append(
            _observation(
                transition,
                Motion.RETURN,
                Decision.HOLD,
                "RETURN_TARGET_MISSING",
            )
        )
    else:
        observations.append(_observation(transition, Motion.RETURN, Decision.PASS))

    if transition.requires_retired_topology:
        observations.append(
            _observation(
                transition,
                Motion.CONTINUITY,
                Decision.FAIL,
                "ZOMBIE_ARCHITECTURE_DEPENDENCY",
            )
        )
    elif not transition.successor_rebuild_possible:
        observations.append(
            _observation(
                transition,
                Motion.CONTINUITY,
                Decision.HOLD,
                "SUCCESSOR_REBUILD_NOT_PROVEN",
            )
        )
    else:
        observations.append(_observation(transition, Motion.CONTINUITY, Decision.PASS))

    by_motion = {item.motion: item for item in observations}
    ordered = tuple(by_motion[motion] for motion in _MOTION_ORDER)
    first_break = next(
        (item for item in ordered if item.decision is Decision.FAIL),
        None,
    )
    if first_break is not None:
        decision = Decision.FAIL
    else:
        first_break = next(
            (item for item in ordered if item.decision is Decision.HOLD),
            None,
        )
        decision = Decision.HOLD if first_break is not None else Decision.PASS

    return TransitionEvaluation(
        transition_id=transition.transition_id,
        decision=decision,
        observations=ordered,
        first_material_break=first_break,
    )
