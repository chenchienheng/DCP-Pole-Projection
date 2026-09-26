"""NFN Event→Current→Affected Execution resolver R0.1.

Bounded executable specimen. It does not claim global Runtime, professional
approval, provider SLA, or world authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence


class Disposition(str, Enum):
    QUIET = "QUIET"
    REVIEW = "STALE_PENDING_REVIEW"
    AFFECTED = "AFFECTED_RESOLUTION_REQUIRED"
    CONFLICT_HOLD = "CONFLICT/HOLD"
    CANNOT_HOLD = "CANNOT/HOLD"
    RECOMPOSE = "RECOMPOSE/EXECUTE_CANDIDATE"


@dataclass(frozen=True)
class ProviderCandidate:
    provider_id: str
    available: bool
    capabilities: frozenset[str]
    authority_ok: bool = True
    data_boundary_ok: bool = True


@dataclass(frozen=True)
class Need:
    need_id: str
    required_capability: str | None = None
    acceptance_floor: frozenset[str] = frozenset()
    survival_floor: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    stable_subject: str
    need_id: str
    source_version: str
    authority_scope: str
    affected_candidates: tuple[str, ...] = ()
    duplicate_of: str | None = None
    applicable: bool = True
    conflicts_with: str | None = None


@dataclass(frozen=True)
class Current:
    subject_id: str
    need_id: str
    source_version: str
    state: str


@dataclass(frozen=True)
class InteractionEvidence:
    """Pre-effect/return evidence for one real caller interaction.

    effect_observed is tri-state: True=observed, False=checked absent,
    None=unknown. Unknown effects must never be replayed speculatively.
    """
    caller_id: str
    need_id: str
    interaction_id: str
    caller_qualified: bool
    independent_interaction: bool = True
    committed_effect_id: str | None = None
    effect_observed: bool | None = None
    return_kind: str | None = None
    material_delta: bool = False


@dataclass(frozen=True)
class SourceClosureEvidence:
    """Evidence that a reconciled cross-Native subject actually reached its source.

    A human-carried copy can prove content availability/read, but it must not be
    upgraded into proof of a direct Root→source wake/delivery edge.
    """
    source_id: str
    closure_id: str
    closure_created: bool
    direct_delivery_observed: bool
    source_read_observed: bool
    via_human_courier: bool = False
    need_id: str | None = None
    source_endpoint_observed: bool | None = None


@dataclass(frozen=True)
class CallerReturnEvidence:
    """Evidence that an observed effect actually returned to the original caller.

    Native completion, persistence, or Root reconciliation cannot substitute for
    caller delivery/read. Caller Use remains a separate disposition claim.
    """
    caller_id: str
    need_id: str
    return_id: str
    effect_observed: bool | None
    return_delivered_observed: bool | None
    caller_read_observed: bool | None
    caller_endpoint_observed: bool | None = None
    caller_use_observed: bool | None = None


@dataclass(frozen=True)
class ResourceReleaseEvidence:
    """Evidence required before a temporary resource may be released/reallocated.

    Believed completion is insufficient. Required effects, deliveries, and
    persistence must be observed before release becomes eligible.
    """
    resource_id: str
    action_id: str
    effect_required: bool = True
    effect_observed: bool | None = None
    delivery_required: bool = False
    delivery_observed: bool | None = None
    persistence_required: bool = False
    persistence_observed: bool | None = None
    need_id: str | None = None
    allocation_id: str | None = None


@dataclass(frozen=True)
class Resolution:
    disposition: Disposition
    current: Current
    executable_affected: tuple[str, ...] = ()
    selected_provider: str | None = None
    reasons: tuple[str, ...] = ()
    tri_pole: Mapping[str, str] = field(default_factory=dict)


def _tri(ideas: str, dcp: str, glmodel: str) -> Mapping[str, str]:
    return {"Ideas": ideas, "DCP": dcp, "GLModel": glmodel}


def resolve_event(
    event: Event,
    current: Current,
    *,
    relevant_receivers: Iterable[str] = (),
    concurrent_events: Sequence[Event] = (),
) -> Resolution:
    """Resolve one bounded event without treating arrival order as truth."""
    if event.duplicate_of:
        return Resolution(
            Disposition.QUIET,
            current,
            reasons=("duplicate receipt does not create a second world change",),
            tri_pole=_tri(
                "Carrier replay does not create a second identity or meaning.",
                "Duplicate event gains no new state or authority.",
                "World state remains unchanged.",
            ),
        )

    # Snapshot one-shot iterables once, without reading unused receivers.
    receiver_set = frozenset(relevant_receivers) if event.affected_candidates else frozenset()

    if not event.applicable:
        return Resolution(
            Disposition.REVIEW,
            current,
            executable_affected=tuple(r for r in event.affected_candidates if r in receiver_set),
            reasons=("newer source is a freshness signal, not Current-for-purpose",),
            tri_pole=_tri(
                "Latest source does not replace the Need's intended use.",
                "Applicability/authority gate blocks automatic promotion.",
                "The world may know the newer source exists while retaining lawful Current.",
            ),
        )

    conflicting = [
        other for other in concurrent_events
        if other.stable_subject == event.stable_subject
        and other.need_id == event.need_id
        and other.authority_scope != event.authority_scope
        and (other.conflicts_with == event.event_id or event.conflicts_with == other.event_id)
    ]
    if conflicting:
        return Resolution(
            Disposition.CONFLICT_HOLD,
            current,
            executable_affected=tuple(r for r in event.affected_candidates if r in receiver_set),
            reasons=("cross-authority candidates coexist; last-write-wins is prohibited",),
            tri_pole=_tri(
                "One stable object keeps one identity while candidate meanings remain distinct.",
                "Authority scopes coexist; the conflicting edge is held for a compatibility gate.",
                "Effective world state is not overwritten by arrival order.",
            ),
        )

    affected = tuple(r for r in event.affected_candidates if r in receiver_set)
    return Resolution(
        Disposition.AFFECTED,
        current,
        executable_affected=affected,
        reasons=("only receivers with a proven affected relation are executable",),
        tri_pole=_tri(
            "Reader relevance follows the Need, not global broadcast.",
            "Dependency/authority/precondition narrow the executable set.",
            "Only affected object/relation edges require revalidation.",
        ),
    )


def qualify_interaction(evidence: InteractionEvidence, current: Current) -> Resolution:
    """Qualify caller/effect/return evidence before any repeated side effect."""
    if evidence.need_id != current.need_id or not evidence.caller_qualified:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("caller/Need qualification is not proven",),
            tri_pole=_tri(
                "An unqualified caller cannot redefine the active Need.",
                "Authority/admission is missing, so no effect is eligible.",
                "World state remains unchanged.",
            ),
        )

    if not evidence.independent_interaction:
        return Resolution(
            Disposition.QUIET,
            current,
            reasons=("same interaction lineage does not create a second action",),
            tri_pole=_tri(
                "Repeated carrier contact does not create a new human/world intent.",
                "Interaction identity deduplicates before execution.",
                "No duplicate world effect is emitted.",
            ),
        )

    if evidence.committed_effect_id:
        if evidence.effect_observed is True:
            return Resolution(
                Disposition.QUIET,
                current,
                reasons=("committed effect is already observed; replay is prohibited",),
                tri_pole=_tri(
                    "The Need keeps one consequence rather than duplicating it.",
                    "Idempotency closes the already-effective action edge.",
                    "Observed effect is retained without a second mutation.",
                ),
            )
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("committed effect exists but its actual effect is not proven",),
            tri_pole=_tri(
                "Uncertain consequence is not treated as a new request.",
                "Unknown/contradictory effect state holds replay until evidence resolves it.",
                "World refuses speculative duplicate mutation.",
            ),
        )

    if (evidence.return_kind or "").upper() == "ACK" and not evidence.material_delta:
        return Resolution(
            Disposition.QUIET,
            current,
            reasons=("pure ACK carries no material Need/effect delta",),
            tri_pole=_tri(
                "Acknowledgement alone does not change meaning or intent.",
                "Receipt visibility is not dispatch or new work.",
                "World state remains unchanged.",
            ),
        )

    return Resolution(
        Disposition.AFFECTED,
        current,
        reasons=(
            "material Return re-enters affected resolution"
            if evidence.material_delta
            else "qualified independent interaction has no committed effect yet"
        ,),
        tri_pole=_tri(
            "A qualified interaction may affect the same Need without changing its identity.",
            "Admission/effect/idempotency gates passed; downstream execution still needs its own authority.",
            "Only the affected consequence edge may proceed or revalidate.",
        ),
    )


def qualify_source_acquisition(
    evidence: SourceClosureEvidence,
    current: Current,
    *,
    expected_source_id: str,
    expected_closure_id: str,
) -> Resolution:
    """Prove source acquisition/read without overclaiming the transport actor/path."""
    binding_errors: list[str] = []
    if evidence.source_id != expected_source_id:
        binding_errors.append("source binding mismatch")
    if evidence.need_id != current.need_id:
        binding_errors.append("Need binding mismatch")
    if evidence.closure_id != expected_closure_id:
        binding_errors.append("closure binding mismatch")
    if binding_errors:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=tuple(binding_errors),
            tri_pole=_tri(
                "Another occurrence cannot satisfy this source acquisition.",
                "Exact source/Need/closure binding precedes acquisition qualification.",
                "The intended source acquisition remains open.",
            ),
        )

    if not evidence.closure_created:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("source closure has not been created",),
        )
    if evidence.source_endpoint_observed is not True:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("message at exact source endpoint is not proven",),
        )
    if not evidence.source_read_observed:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("source read is not proven",),
        )
    return Resolution(
        Disposition.QUIET,
        current,
        reasons=("exact source acquisition and read are proven; transport attribution remains a separate claim",),
        tri_pole=_tri(
            "Source awareness can close without inventing a transport actor.",
            "Acquisition/read evidence is separated from direct-route attribution.",
            "World records receipt without overclaiming the carrier path.",
        ),
    )


def qualify_source_closure(
    evidence: SourceClosureEvidence,
    current: Current,
    *,
    expected_source_id: str,
    expected_closure_id: str,
) -> Resolution:
    """Require exact source/Need/closure binding before accepting closure evidence."""
    binding_errors: list[str] = []
    if evidence.source_id != expected_source_id:
        binding_errors.append("source binding mismatch")
    if evidence.need_id != current.need_id:
        binding_errors.append("Need binding mismatch")
    if evidence.closure_id != expected_closure_id:
        binding_errors.append("closure binding mismatch")
    if binding_errors:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=tuple(binding_errors),
            tri_pole=_tri(
                "Another occurrence cannot close this source relation.",
                "Exact source/Need/closure binding precedes closure qualification.",
                "The intended source closure remains open.",
            ),
        )

    if not evidence.closure_created:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("source closure has not been created",),
            tri_pole=_tri(
                "The source cannot metabolize a closure that does not yet exist.",
                "Return-path completion is not inferred from receiver reconciliation.",
                "World/source state remains open for closure.",
            ),
        )

    if evidence.via_human_courier or not evidence.direct_delivery_observed:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("direct source delivery is not proven; relayed content is not a wake/delivery receipt",),
            tri_pole=_tri(
                "Content identity can survive relay without proving the transport edge.",
                "Human courier use cannot be upgraded into direct delivery authority/evidence.",
                "Source awareness may exist while the direct routing edge remains open.",
            ),
        )

    if not evidence.source_read_observed:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("direct delivery occurred but source read is not proven",),
            tri_pole=_tri(
                "Arrival alone does not prove source assimilation.",
                "Delivery and Read/Use remain distinct stages.",
                "Closure remains pending at the source endpoint.",
            ),
        )

    return Resolution(
        Disposition.QUIET,
        current,
        reasons=("direct source closure delivery and source read are proven",),
        tri_pole=_tri(
            "The source receives the reconciled consequence without changing identity.",
            "The bounded return path is closed without creating a new dispatch.",
            "No extra world mutation is implied by closure receipt.",
        ),
    )


def qualify_caller_return(
    evidence: CallerReturnEvidence,
    current: Current,
    *,
    expected_caller_id: str,
    expected_return_id: str,
) -> Resolution:
    """Close a bounded Need only when its effect has returned to the real caller."""
    binding_errors: list[str] = []
    if evidence.caller_id != expected_caller_id:
        binding_errors.append("caller binding mismatch")
    if evidence.need_id != current.need_id:
        binding_errors.append("Need binding mismatch")
    if evidence.return_id != expected_return_id:
        binding_errors.append("return binding mismatch")
    if binding_errors:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=tuple(binding_errors),
            tri_pole=_tri(
                "Another caller/Need cannot inherit this Return closure.",
                "Exact caller/Need/return binding precedes closure.",
                "The original caller Return remains open.",
            ),
        )

    missing: list[str] = []
    if evidence.effect_observed is not True:
        missing.append("effect is not observed")
    if evidence.caller_endpoint_observed is not True:
        missing.append("exact caller endpoint is not observed")
    if evidence.return_delivered_observed is not True:
        missing.append("caller Return delivery is not observed")
    if evidence.caller_read_observed is not True:
        missing.append("caller read is not observed")
    if missing:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=tuple(missing),
            tri_pole=_tri(
                "Native completion does not equal caller receipt.",
                "Persistence/reconciliation cannot substitute for caller delivery/read.",
                "The Need stays open only on the missing Return edge.",
            ),
        )

    return Resolution(
        Disposition.QUIET,
        current,
        reasons=("effect and exact caller Return delivery/read are proven; caller Use remains separate",),
        tri_pole=_tri(
            "The caller receives the consequence without creating a new Need.",
            "Bounded caller Return closes without forcing adoption.",
            "No extra world mutation is implied by caller receipt.",
        ),
    )


def qualify_resource_release(
    evidence: ResourceReleaseEvidence,
    current: Current,
    *,
    expected_resource_id: str,
    expected_action_id: str,
    expected_allocation_id: str,
) -> Resolution:
    """Bind release evidence to this Need/action/resource/allocation before release."""
    binding_errors: list[str] = []
    if evidence.need_id != current.need_id:
        binding_errors.append("Need binding mismatch")
    if evidence.resource_id != expected_resource_id:
        binding_errors.append("resource binding mismatch")
    if evidence.action_id != expected_action_id:
        binding_errors.append("action binding mismatch")
    if evidence.allocation_id != expected_allocation_id:
        binding_errors.append("allocation binding mismatch")
    if binding_errors:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=tuple(binding_errors),
            tri_pole=_tri(
                "Evidence from another occurrence cannot release this resource.",
                "Exact Need/action/resource/allocation binding precedes release eligibility.",
                "The current allocation remains held.",
            ),
        )

    missing: list[str] = []
    if evidence.effect_required and evidence.effect_observed is not True:
        missing.append("required effect is not observed")
    if evidence.delivery_required and evidence.delivery_observed is not True:
        missing.append("required delivery is not observed")
    if evidence.persistence_required and evidence.persistence_observed is not True:
        missing.append("required persistence/readback is not observed")

    if missing:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=tuple(missing),
            tri_pole=_tri(
                "Believed completion does not equal completed consequence.",
                "Resource release is gated by observed required effects, not task narration.",
                "The resource remains eligible to stay allocated until the evidence gate closes.",
            ),
        )

    return Resolution(
        Disposition.RECOMPOSE,
        current,
        reasons=("all required release evidence is observed; release/reallocation is eligible",),
        tri_pole=_tri(
            "Resource identity is not tied to one task after its required consequence closes.",
            "Release eligibility permits bounded recomposition without claiming provider release receipt.",
            "The world may reallocate capacity while preserving the completed effect evidence.",
        ),
    )


def route_provider(need: Need, providers: Sequence[ProviderCandidate], current: Current) -> Resolution:
    """Capability-first/provider-second routing with a survival-floor guard."""
    if not need.required_capability:
        raise ValueError("provider routing requires a required_capability")

    available = [p for p in providers if p.available and p.authority_ok and p.data_boundary_ok]
    eligible = [
        p for p in available
        if need.required_capability in p.capabilities
        and need.survival_floor.issubset(p.capabilities)
    ]
    if not eligible:
        return Resolution(
            Disposition.CANNOT_HOLD,
            current,
            reasons=("no provider is above the Resource Survival Floor",),
            tri_pole=_tri(
                "A reply from the wrong capability cannot redefine the Need as completed.",
                "Work Eligibility is false; routing authority cannot invent missing capability.",
                "No fake world delta is emitted.",
            ),
        )

    selected = eligible[0]
    return Resolution(
        Disposition.RECOMPOSE,
        current,
        selected_provider=selected.provider_id,
        reasons=("eligible provider selected after capability/authority/data-boundary checks",),
        tri_pole=_tri(
            "Provider changes without changing Need identity.",
            "Capability-first binding permits bounded recomposition.",
            "World records a composition change; effectiveness awaits execution evidence.",
        ),
    )
