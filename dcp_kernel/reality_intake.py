from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class ObservationState(str, Enum):
    OBSERVED = "OBSERVED"
    WITHDRAWN_UNKNOWN_BODY = "WITHDRAWN_UNKNOWN_BODY"
    UNREADABLE = "UNREADABLE"


@dataclass(frozen=True)
class RealityObservation:
    observation_id: str
    carrier_id: str
    source_id: str
    source_revision: str | None
    observed_at: str
    state: ObservationState
    content_class: str
    candidate_referents: tuple[str, ...] = ()
    candidate_relations: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntakeNeed:
    need_id: str
    required_capabilities: tuple[str, ...]
    evidence_pointers: tuple[str, ...]
    unknowns: tuple[str, ...]
    preserved_observations: tuple[str, ...]


@dataclass(frozen=True)
class RealityIntakeAssessment:
    decision: Decision
    need: IntakeNeed | None
    reasons: tuple[str, ...]


def assess_reality_intake(
    *,
    need_id: str,
    observations: tuple[RealityObservation, ...],
    required_capabilities: tuple[str, ...],
) -> RealityIntakeAssessment:
    """Compile messy carrier observations into a bounded Need candidate.

    This layer preserves what was actually observed and what remains unknown.
    It does not OCR missing text, assert same-referent identity, admit engineering
    truth, or grant any downstream capability/authority.
    """

    if not observations:
        return RealityIntakeAssessment(
            Decision.HOLD,
            None,
            ("NO_REALITY_OBSERVATION",),
        )

    observed = [item for item in observations if item.state is ObservationState.OBSERVED]
    if not observed:
        return RealityIntakeAssessment(
            Decision.HOLD,
            None,
            ("NO_USABLE_OBSERVATION_BODY",),
        )

    evidence: list[str] = []
    unknowns: list[str] = []
    preserved: list[str] = []

    for item in observations:
        preserved.append(item.observation_id)
        if item.state is ObservationState.OBSERVED:
            evidence.append(
                f"{item.carrier_id}:{item.source_id}@{item.source_revision or 'REVISION_UNKNOWN'}"
            )
        elif item.state is ObservationState.WITHDRAWN_UNKNOWN_BODY:
            unknowns.append(f"{item.observation_id}:WITHDRAWN_BODY_UNKNOWN")
        else:
            unknowns.append(f"{item.observation_id}:UNREADABLE")

        unknowns.extend(f"{item.observation_id}:{value}" for value in item.uncertainty)

    if not required_capabilities:
        return RealityIntakeAssessment(
            Decision.HOLD,
            None,
            ("REQUIRED_CAPABILITY_NOT_RESOLVED",),
        )

    return RealityIntakeAssessment(
        Decision.PASS,
        IntakeNeed(
            need_id=need_id,
            required_capabilities=tuple(dict.fromkeys(required_capabilities)),
            evidence_pointers=tuple(dict.fromkeys(evidence)),
            unknowns=tuple(dict.fromkeys(unknowns)),
            preserved_observations=tuple(dict.fromkeys(preserved)),
        ),
        (
            "MESSY_REALITY_COMPILED_TO_BOUNDED_NEED_CANDIDATE",
            "OBSERVATION_DOES_NOT_IMPLY_SAME_REFERENT_OR_DOMAIN_TRUTH",
        ),
    )
