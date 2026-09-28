"""Evidence-to-world compilation R0.1.

Compiles heterogeneous drawing/model evidence into bounded object candidates without
promoting extraction output to engineering truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceKind(str, Enum):
    SCHEDULE = "SCHEDULE"
    PLAN = "PLAN"
    DETAIL = "DETAIL"
    MODEL = "MODEL"
    IMAGE = "IMAGE"
    OTHER = "OTHER"


class EvidenceWorldDisposition(str, Enum):
    CANDIDATE_LINKED = "CANDIDATE_LINKED"
    TO_VERIFY = "TO_VERIFY"
    CONFLICT_HOLD = "CONFLICT_HOLD"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class EvidenceObservation:
    evidence_id: str
    source_identity: str
    source_revision: str | None
    kind: EvidenceKind
    object_stable_id: str | None
    object_class: str | None
    type_mark: str | None
    occurrence_location: str | None
    quantity: int | None
    dimension_value: float | None
    dimension_unit: str | None
    relation_or_host: str | None
    extraction_method: str
    confidence: float
    authority_scope: str
    current_for_purpose: bool
    engineering_accepted: bool = False


@dataclass(frozen=True)
class EvidenceWorldAssessment:
    disposition: EvidenceWorldDisposition
    stable_object_id: str | None
    reasons: tuple[str, ...]
    claim_ceiling: str = "EVIDENCE_BOUND_OBJECT_CANDIDATE"


def compile_evidence_to_world(
    observations: tuple[EvidenceObservation, ...],
) -> EvidenceWorldAssessment:
    if not observations:
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.INSUFFICIENT_EVIDENCE,
            None,
            ("NO_EVIDENCE_OBSERVATION",),
        )

    ids = {x.object_stable_id for x in observations if x.object_stable_id}
    if len(ids) > 1:
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.CONFLICT_HOLD,
            None,
            ("MULTIPLE_STABLE_OBJECT_IDENTITIES",),
        )
    stable_id = next(iter(ids), None)

    if any(not x.source_revision for x in observations):
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.TO_VERIFY,
            stable_id,
            ("SOURCE_REVISION_UNRESOLVED",),
        )

    if any(not x.current_for_purpose for x in observations):
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.TO_VERIFY,
            stable_id,
            ("SOURCE_NOT_CURRENT_FOR_PURPOSE",),
        )

    dimensions = {
        (x.dimension_value, x.dimension_unit)
        for x in observations
        if x.dimension_value is not None
    }
    if any(value is not None and not unit for value, unit in dimensions):
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.TO_VERIFY,
            stable_id,
            ("DIMENSION_UNIT_MISSING",),
        )
    if len(dimensions) > 1:
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.CONFLICT_HOLD,
            stable_id,
            ("DIMENSION_EVIDENCE_CONFLICT",),
        )

    schedule_quantities = {
        x.quantity for x in observations
        if x.kind is EvidenceKind.SCHEDULE and x.quantity is not None
    }
    plan_occurrences = {
        x.occurrence_location for x in observations
        if x.kind is EvidenceKind.PLAN and x.occurrence_location
    }
    if len(schedule_quantities) > 1:
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.CONFLICT_HOLD,
            stable_id,
            ("SCHEDULE_QUANTITY_CONFLICT",),
        )
    if schedule_quantities and plan_occurrences:
        scheduled = next(iter(schedule_quantities))
        if scheduled != len(plan_occurrences):
            return EvidenceWorldAssessment(
                EvidenceWorldDisposition.CONFLICT_HOLD,
                stable_id,
                ("SCHEDULE_OCCURRENCE_COUNT_MISMATCH",),
            )

    if any(x.confidence < 0.80 for x in observations):
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.TO_VERIFY,
            stable_id,
            ("LOW_CONFIDENCE_EXTRACTION",),
        )

    if stable_id is None:
        return EvidenceWorldAssessment(
            EvidenceWorldDisposition.TO_VERIFY,
            None,
            ("STABLE_OBJECT_ID_UNRESOLVED",),
        )

    return EvidenceWorldAssessment(
        EvidenceWorldDisposition.CANDIDATE_LINKED,
        stable_id,
        (
            "MULTI_SOURCE_EVIDENCE_LINKED_WITHOUT_TRUTH_PROMOTION",
            "ENGINEERING_ACCEPTANCE_REMAINS_NATIVE",
        ),
    )
