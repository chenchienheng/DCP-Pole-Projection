from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .models import (
    CapabilityBinding,
    CurrentCandidate,
    InvariantCore,
    LifecycleState,
    Need,
    ReturnState,
    StableLife,
    Transition,
    TriRootState,
)
from .platform import (
    PlatformLoopResult,
    PlatformPlan,
    compile_work_contract,
    complete_fixture_loop,
)
from .return_state import ReturnClosure


@dataclass(frozen=True)
class FixtureRun:
    fixture_id: str
    plan: PlatformPlan
    loop: PlatformLoopResult


def _stable_life(data: Mapping[str, Any]) -> StableLife:
    core = data["invariant_core"]
    return StableLife(
        life_id=data["life_id"],
        invariant_core=InvariantCore(
            identity_anchor=core["identity_anchor"],
            meaning_anchor=core["meaning_anchor"],
            world_truth_id=core.get("world_truth_id"),
        ),
        native_owner=data["native_owner"],
        current_revision=data["current_revision"],
        last_good_revision=data["last_good_revision"],
    )


def _tri_root(data: Mapping[str, Any]) -> TriRootState:
    return TriRootState(
        meaning_preserved=data["meaning_preserved"],
        dependencies_resolved=data["dependencies_resolved"],
        world_id=data.get("world_id"),
        source_revision=data["source_revision"],
    )


def _binding(data: Mapping[str, Any]) -> CapabilityBinding:
    return CapabilityBinding(
        capability_id=data["capability_id"],
        actor_id=data["actor_id"],
        carrier_id=data["carrier_id"],
        authority_granted=data["authority_granted"],
        rights_allowed=data["rights_allowed"],
        evidence_available=data["evidence_available"],
        return_target=data.get("return_target"),
        native_internalized=data.get("native_internalized", False),
        actor_labels=tuple(data.get("actor_labels", ())),
    )


def _candidate(data: Mapping[str, Any]) -> CurrentCandidate:
    return CurrentCandidate(
        stable_life_id=data["stable_life_id"],
        revision=data["revision"],
        lifecycle_state=LifecycleState(data["lifecycle_state"]),
        successor_of=data.get("successor_of"),
        authority_valid=data["authority_valid"],
        evidence_valid=data["evidence_valid"],
        receiver_reconciled=data["receiver_reconciled"],
        reader_eligible=data["reader_eligible"],
        timestamp=data["timestamp"],
    )


def _transition(data: Mapping[str, Any]) -> Transition:
    return Transition(
        transition_id=data["transition_id"],
        stable_life_id=data["stable_life_id"],
        need=data["need"],
        state_before=LifecycleState(data["state_before"]),
        proposed_effect=data["proposed_effect"],
        capability_id=data["capability_id"],
        source_revision=data["source_revision"],
        meaning_preserved=data.get("meaning_preserved", True),
        dependencies_resolved=data.get("dependencies_resolved", True),
        representation_only=data.get("representation_only", False),
        requests_world_truth_mutation=data.get(
            "requests_world_truth_mutation",
            False,
        ),
        world_receiver_authorized=data.get("world_receiver_authorized", False),
        world_id_before=data.get("world_id_before"),
        world_id_after=data.get("world_id_after"),
        claims_native_capability=data.get("claims_native_capability", False),
        successor_rebuild_possible=data.get("successor_rebuild_possible", True),
        requires_retired_topology=data.get("requires_retired_topology", False),
    )


def run_platform_fixture(payload: Mapping[str, Any]) -> FixtureRun:
    """Run a deterministic fixture; never impersonate external work or Runtime."""

    stable_life = _stable_life(payload["stable_life"])
    tri_root = _tri_root(payload["tri_root_state"])
    need_data = payload["need"]
    need = Need(
        need_id=need_data["need_id"],
        required_capability=need_data["required_capability"],
        receiver=need_data["receiver"],
    )
    bindings = tuple(
        _binding(item) for item in payload["capability_candidates"]
    )
    candidates = tuple(
        _candidate(item) for item in payload["current_candidates"]
    )
    transition = _transition(payload["transition"])

    plan = compile_work_contract(
        stable_life=stable_life,
        tri_root=tri_root,
        need=need,
        capability_candidates=bindings,
        current_candidates=candidates,
        changed_nodes=tuple(payload["changed_nodes"]),
        dependency_graph={
            key: tuple(value)
            for key, value in payload["dependency_graph"].items()
        },
        eligible_receivers=set(payload["eligible_receivers"]),
        transition=transition,
    )

    return_data = payload["return"]
    closure = ReturnClosure(
        return_id=return_data["return_id"],
        receiver=return_data["receiver"],
        manual_interventions=tuple(
            return_data.get("manual_interventions", ())
        ),
    )
    for step in return_data["progression"]:
        updates = dict(step.get("updates", {}))
        closure = closure.advance(ReturnState(step["state"]), **updates)

    rebuild = payload["rebuild"]
    loop = complete_fixture_loop(
        plan=plan,
        stable_life=stable_life,
        tri_root=tri_root,
        closure=closure,
        receiver_rebuild_revision=rebuild["receiver_rebuild_revision"],
        receiver_tri_root_revision=rebuild["receiver_tri_root_revision"],
        cursor=rebuild["cursor"],
        ack_owner=rebuild["ack_owner"],
    )
    return FixtureRun(
        fixture_id=payload["fixture_id"],
        plan=plan,
        loop=loop,
    )
