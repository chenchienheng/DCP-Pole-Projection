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
