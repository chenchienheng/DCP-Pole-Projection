from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class FamilyMetabolismState(str, Enum):
    AUDIT_INCOMPLETE = "AUDIT_INCOMPLETE"
    SUCCESSOR_COVERAGE_PARTIAL = "SUCCESSOR_COVERAGE_PARTIAL"
    READER_WITHDRAWAL_PARTIAL = "READER_WITHDRAWAL_PARTIAL"
    UNIQUE_EVIDENCE_REVIEW_PENDING = "UNIQUE_EVIDENCE_REVIEW_PENDING"
    READY_FOR_POOLED_RECLAIM_REVIEW = "READY_FOR_POOLED_RECLAIM_REVIEW"


@dataclass(frozen=True)
class FamilyMetabolismInput:
    family: str
    artifact_count: int
    classified_count: int
    successor_covered_count: int
    caller_audit_complete: bool
    rebuild_audit_complete: bool
    normal_reader_wake: bool
    current_routing_reference: bool
    unique_evidence_unreviewed_count: int


@dataclass(frozen=True)
class FamilyMetabolismAssessment:
    decision: Decision
    state: FamilyMetabolismState
    destructive_action_authorized: bool
    reasons: tuple[str, ...]


def assess_family_metabolism(item: FamilyMetabolismInput) -> FamilyMetabolismAssessment:
    """Evaluate a legacy family without equating folder labels with completed metabolism."""

    if item.artifact_count < 0 or item.classified_count < 0 or item.successor_covered_count < 0:
        raise ValueError("FAMILY_COUNTS_MUST_BE_NON_NEGATIVE")
    if item.classified_count > item.artifact_count:
        raise ValueError("CLASSIFIED_COUNT_EXCEEDS_ARTIFACT_COUNT")
    if item.successor_covered_count > item.classified_count:
        raise ValueError("SUCCESSOR_COVERED_COUNT_EXCEEDS_CLASSIFIED_COUNT")

    if not item.caller_audit_complete or not item.rebuild_audit_complete:
        return FamilyMetabolismAssessment(
            decision=Decision.HOLD,
            state=FamilyMetabolismState.AUDIT_INCOMPLETE,
            destructive_action_authorized=False,
            reasons=("CALLER_OR_REBUILD_AUDIT_INCOMPLETE",),
        )

    if item.classified_count < item.artifact_count or item.successor_covered_count < item.classified_count:
        return FamilyMetabolismAssessment(
            decision=Decision.HOLD,
            state=FamilyMetabolismState.SUCCESSOR_COVERAGE_PARTIAL,
            destructive_action_authorized=False,
            reasons=("ARTIFACT_CLASSIFICATION_OR_SUCCESSOR_COVERAGE_INCOMPLETE",),
        )

    if item.normal_reader_wake or item.current_routing_reference:
        return FamilyMetabolismAssessment(
            decision=Decision.HOLD,
            state=FamilyMetabolismState.READER_WITHDRAWAL_PARTIAL,
            destructive_action_authorized=False,
            reasons=("LEGACY_FAMILY_STILL_ON_READER_OR_ROUTING_SURFACE",),
        )

    if item.unique_evidence_unreviewed_count > 0:
        return FamilyMetabolismAssessment(
            decision=Decision.HOLD,
            state=FamilyMetabolismState.UNIQUE_EVIDENCE_REVIEW_PENDING,
            destructive_action_authorized=False,
            reasons=("UNIQUE_EVIDENCE_REVIEW_PENDING",),
        )

    return FamilyMetabolismAssessment(
        decision=Decision.PASS,
        state=FamilyMetabolismState.READY_FOR_POOLED_RECLAIM_REVIEW,
        destructive_action_authorized=False,
        reasons=("FAMILY_SUCCESSOR_COVERED_AND_NORMAL_WAKE_WITHDRAWN",),
    )
