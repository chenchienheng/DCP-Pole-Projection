from __future__ import annotations

from collections import deque
from typing import Iterable, Mapping, Sequence

from .models import (
    AffectedCone,
    CapabilityBinding,
    CapabilityResolution,
    ClaimCeiling,
    ClaimEvidence,
    CurrentCandidate,
    CurrentResolution,
    CurrentResolutionStatus,
    Decision,
    LifecycleState,
    Need,
)


def resolve_capability_binding(
    need: Need,
    candidates: Iterable[CapabilityBinding],
) -> CapabilityResolution:
    """Resolve by capability, authority, rights, evidence and return path.

    Actor labels and pole/window/persona names are intentionally ignored.
    """

    eligible: list[CapabilityBinding] = []
    excluded: dict[str, tuple[str, ...]] = {}

    for candidate in candidates:
        reasons: list[str] = []
        if candidate.capability_id != need.required_capability:
            reasons.append("CAPABILITY_MISMATCH")
        if not candidate.authority_granted:
            reasons.append("AUTHORITY_NOT_GRANTED")
        if not candidate.rights_allowed:
            reasons.append("RIGHTS_NOT_ALLOWED")
        if not candidate.evidence_available:
            reasons.append("CAPABILITY_EVIDENCE_MISSING")
        if candidate.return_target != need.receiver:
            reasons.append("RETURN_TARGET_MISMATCH")

        key = f"{candidate.actor_id}@{candidate.carrier_id}"
        if reasons:
            excluded[key] = tuple(reasons)
        else:
            eligible.append(candidate)

    if not eligible:
        return CapabilityResolution(
            decision=Decision.HOLD,
            binding=None,
            reasons=("NO_ELIGIBLE_CAPABILITY_BINDING",),
            excluded=excluded,
        )

    eligible.sort(
        key=lambda item: (
            not item.native_internalized,
            item.capability_id,
            item.actor_id,
            item.carrier_id,
        )
    )
    return CapabilityResolution(
        decision=Decision.PASS,
        binding=eligible[0],
        excluded=excluded,
    )


def resolve_current(
    stable_life_id: str,
    last_good_revision: str,
    candidates: Sequence[CurrentCandidate],
) -> CurrentResolution:
    """Resolve Current without using timestamp, filename or placement as proof."""

    eligible: list[CurrentCandidate] = []
    rejected: dict[str, tuple[str, ...]] = {}

    for candidate in candidates:
        reasons: list[str] = []
        if candidate.stable_life_id != stable_life_id:
            reasons.append("STABLE_IDENTITY_MISMATCH")
        if candidate.lifecycle_state not in {LifecycleState.CURRENT, LifecycleState.CANDIDATE}:
            reasons.append("LIFECYCLE_STATE_NOT_CURRENT_ELIGIBLE")
        if not candidate.authority_valid:
            reasons.append("AUTHORITY_INVALID")
        if not candidate.evidence_valid:
            reasons.append("EVIDENCE_INVALID")
        if not candidate.receiver_reconciled:
            reasons.append("RECEIVER_RECONCILIATION_MISSING")
        if not candidate.reader_eligible:
            reasons.append("READER_NOT_ELIGIBLE")

        is_current_body = (
            candidate.lifecycle_state is LifecycleState.CURRENT
            and candidate.revision == last_good_revision
        )
        is_direct_successor = candidate.successor_of == last_good_revision
        if not (is_current_body or is_direct_successor):
            reasons.append("SUCCESSOR_RELATION_MISSING")

        if reasons:
            rejected[candidate.revision] = tuple(reasons)
        else:
            eligible.append(candidate)

    if not eligible:
        return CurrentResolution(
            status=CurrentResolutionStatus.HOLD,
            selected_revision=None,
            reasons=("NO_CURRENT_ELIGIBLE_REVISION",),
            rejected=rejected,
        )

    direct_successors = [item for item in eligible if item.successor_of == last_good_revision]
    if len(direct_successors) > 1:
        return CurrentResolution(
            status=CurrentResolutionStatus.CONFLICT,
            selected_revision=None,
            reasons=("MULTIPLE_VALID_DIRECT_SUCCESSORS",),
            rejected=rejected,
        )

    if len(direct_successors) == 1:
        selected = direct_successors[0]
    else:
        current_bodies = [
            item
            for item in eligible
            if item.lifecycle_state is LifecycleState.CURRENT
            and item.revision == last_good_revision
        ]
        if len(current_bodies) != 1:
            return CurrentResolution(
                status=CurrentResolutionStatus.CONFLICT,
                selected_revision=None,
                reasons=("CURRENT_BODY_AMBIGUOUS",),
                rejected=rejected,
            )
        selected = current_bodies[0]

    return CurrentResolution(
        status=CurrentResolutionStatus.CURRENT,
        selected_revision=selected.revision,
        rejected=rejected,
    )


def compute_affected_cone(
    changed_nodes: Iterable[str],
    dependency_graph: Mapping[str, Sequence[str]],
    eligible_receivers: set[str],
) -> AffectedCone:
    """Return a bounded reachable receiver set; shared visibility is not enough."""

    queue: deque[str] = deque(changed_nodes)
    visited: set[str] = set(changed_nodes)
    affected: set[str] = set()
    excluded: dict[str, str] = {}

    while queue:
        node = queue.popleft()
        for target in dependency_graph.get(node, ()):
            if target in visited:
                continue
            visited.add(target)
            queue.append(target)
            if target in eligible_receivers:
                affected.add(target)
            else:
                excluded[target] = "RECEIVER_NOT_ELIGIBLE"

    return AffectedCone(
        affected=tuple(sorted(affected)),
        excluded=dict(sorted(excluded.items())),
    )


def evaluate_claim_ceiling(evidence: ClaimEvidence) -> ClaimCeiling:
    """Classify maturity from evidence only; filenames and activity are not inputs."""

    if evidence.runtime_evidence and evidence.runtime_authority:
        return ClaimCeiling.RUNTIME
    if evidence.build_ready_evidence:
        return ClaimCeiling.BUILD_READY
    if evidence.end_to_end_platform_path:
        return ClaimCeiling.PLATFORM_SKELETON_CANDIDATE
    if evidence.executable_tests:
        return ClaimCeiling.EXECUTABLE_CANDIDATE
    if evidence.machine_contract:
        return ClaimCeiling.MACHINE_CONTRACT
    return ClaimCeiling.DESCRIPTIVE
