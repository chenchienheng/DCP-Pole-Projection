from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class Decision(str, Enum):
    PASS = "PASS"
    HOLD = "HOLD"
    FAIL = "FAIL"


class Motion(str, Enum):
    IDENTITY = "IDENTITY"
    MEANING = "MEANING"
    DEPENDENCY = "DEPENDENCY"
    STATE = "STATE"
    REALITY = "REALITY"
    CAPABILITY = "CAPABILITY"
    RETURN = "RETURN"
    CONTINUITY = "CONTINUITY"


class LifecycleState(str, Enum):
    CANDIDATE = "CANDIDATE"
    CURRENT = "CURRENT"
    HISTORICAL = "HISTORICAL"
    FAILURE = "FAILURE"
    RETURN = "RETURN"
    STALE_PENDING_REVIEW = "STALE_PENDING_REVIEW"
    CONFLICT = "CONFLICT"
    HOLD = "HOLD"


class CurrentResolutionStatus(str, Enum):
    CURRENT = "CURRENT"
    STALE_PENDING_REVIEW = "STALE_PENDING_REVIEW"
    CONFLICT = "CONFLICT"
    HOLD = "HOLD"


class ReturnState(str, Enum):
    PRODUCED = "PRODUCED"
    ROUTED = "ROUTED"
    ACTUAL_READ = "ACTUAL_READ"
    MATERIALITY_RESOLVED = "MATERIALITY_RESOLVED"
    RECEIVER_NATIVE_DISPOSITION = "RECEIVER_NATIVE_DISPOSITION"
    RECONCILED = "RECONCILED"
    REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON = "REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON"
    BEHAVIOR_DELTA_OBSERVED = "BEHAVIOR_DELTA_OBSERVED"
    RETESTED = "RETESTED"


class ClaimCeiling(str, Enum):
    DESCRIPTIVE = "DESCRIPTIVE"
    MACHINE_CONTRACT = "MACHINE_CONTRACT"
    EXECUTABLE_CANDIDATE = "EXECUTABLE_CANDIDATE"
    PLATFORM_SKELETON_CANDIDATE = "PLATFORM_SKELETON_CANDIDATE"
    BUILD_READY = "BUILD_READY"
    RUNTIME = "RUNTIME"


class LearningDisposition(str, Enum):
    READ_AFFECTED_SLICE = "READ_AFFECTED_SLICE"
    REUSE_NO_REPROPAGATION = "REUSE_NO_REPROPAGATION"
    NO_MATERIAL_DELTA = "NO_MATERIAL_DELTA"
    RECEIVER_NOT_AFFECTED = "RECEIVER_NOT_AFFECTED"
    HOLD_CONTAMINATION = "HOLD_CONTAMINATION"


@dataclass(frozen=True)
class InvariantCore:
    identity_anchor: str
    meaning_anchor: str
    world_truth_id: str | None = None


@dataclass(frozen=True)
class StableLife:
    life_id: str
    invariant_core: InvariantCore
    native_owner: str
    current_revision: str
    last_good_revision: str


@dataclass(frozen=True)
class TriRootState:
    meaning_preserved: bool
    dependencies_resolved: bool
    world_id: str | None
    source_revision: str


@dataclass(frozen=True)
class Need:
    need_id: str
    required_capability: str
    receiver: str


@dataclass(frozen=True)
class CapabilityBinding:
    capability_id: str
    actor_id: str
    carrier_id: str
    authority_granted: bool
    rights_allowed: bool
    evidence_available: bool
    return_target: str | None
    native_internalized: bool = False
    actor_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityResolution:
    decision: Decision
    binding: CapabilityBinding | None
    reasons: tuple[str, ...] = ()
    excluded: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class Transition:
    transition_id: str
    stable_life_id: str
    need: str
    state_before: LifecycleState
    proposed_effect: str
    capability_id: str
    source_revision: str
    meaning_preserved: bool = True
    dependencies_resolved: bool = True
    representation_only: bool = False
    requests_world_truth_mutation: bool = False
    world_receiver_authorized: bool = False
    world_id_before: str | None = None
    world_id_after: str | None = None
    claims_native_capability: bool = False
    successor_rebuild_possible: bool = True
    requires_retired_topology: bool = False


@dataclass(frozen=True)
class MotionObservation:
    transition_id: str
    motion: Motion
    decision: Decision
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransitionEvaluation:
    transition_id: str
    decision: Decision
    observations: tuple[MotionObservation, ...]
    first_material_break: MotionObservation | None = None


@dataclass(frozen=True)
class CurrentCandidate:
    stable_life_id: str
    revision: str
    lifecycle_state: LifecycleState
    successor_of: str | None
    authority_valid: bool
    evidence_valid: bool
    receiver_reconciled: bool
    reader_eligible: bool
    timestamp: str


@dataclass(frozen=True)
class CurrentResolution:
    status: CurrentResolutionStatus
    selected_revision: str | None
    reasons: tuple[str, ...] = ()
    rejected: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class AffectedCone:
    affected: tuple[str, ...]
    excluded: Mapping[str, str]


@dataclass(frozen=True)
class ClaimEvidence:
    machine_contract: bool = False
    executable_tests: bool = False
    end_to_end_platform_path: bool = False
    build_ready_evidence: bool = False
    runtime_evidence: bool = False
    runtime_authority: bool = False


@dataclass(frozen=True)
class ReentryState:
    stable_life_id: str
    invariant_core_id: str
    tri_root_revision: str
    current_revision: str
    last_good_revision: str
    active_need: str | None
    blockers: tuple[str, ...]
    pending_returns: tuple[str, ...]
    cursor: str | None
    ack_owner: str | None


@dataclass(frozen=True)
class LearningInput:
    source_id: str
    source_revision: str
    receiver: str
    affected_receivers: tuple[str, ...]
    material_delta: bool
    equivalent_receipt_exists: bool = False
    historical: bool = False
    reentry_purpose: str | None = None
    native_body_copy_requested: bool = False
    authority_in_scope: bool = True


@dataclass(frozen=True)
class LearningAssessment:
    decision: Decision
    disposition: LearningDisposition
    reasons: tuple[str, ...] = ()
