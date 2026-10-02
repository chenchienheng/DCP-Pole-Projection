from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class ReaderDisposition(str, Enum):
    READ_CURRENT = "READ_CURRENT"
    READ_AFFECTED_SLICE = "READ_AFFECTED_SLICE"
    ESCALATE_BOUNDED = "ESCALATE_BOUNDED"
    HISTORICAL_REENTRY = "HISTORICAL_REENTRY"
    NO_WAKE = "NO_WAKE"
    HOLD = "HOLD"


@dataclass(frozen=True)
class ReaderRequest:
    stable_identity_known: bool
    authority_scope_known: bool
    lifecycle_state_known: bool
    receiver_affected: bool
    material_delta: bool
    current_surface: bool = False
    conflict: bool = False
    missing_evidence: bool = False
    historical: bool = False
    reentry_purpose: str | None = None
    native_body_copy_requested: bool = False


@dataclass(frozen=True)
class ReaderAssessment:
    decision: Decision
    disposition: ReaderDisposition
    whole_body_read_allowed: bool
    reasons: tuple[str, ...]


_ALLOWED_REENTRY_PURPOSES = {
    "PROVENANCE",
    "AUDIT",
    "FAILURE_LEARNING",
    "REGRESSION",
    "REBUILD",
    "SUCCESSOR_VALIDATION",
}


def assess_reader_request(item: ReaderRequest) -> ReaderAssessment:
    """Resolve bounded reader eligibility without reconstructing a fixed window order."""

    if item.native_body_copy_requested:
        return ReaderAssessment(
            Decision.FAIL,
            ReaderDisposition.HOLD,
            False,
            ("NATIVE_BODY_COPY_PROHIBITED",),
        )

    if not item.stable_identity_known:
        return ReaderAssessment(
            Decision.HOLD,
            ReaderDisposition.HOLD,
            False,
            ("STABLE_IDENTITY_UNRESOLVED",),
        )
    if not item.authority_scope_known:
        return ReaderAssessment(
            Decision.HOLD,
            ReaderDisposition.HOLD,
            False,
            ("AUTHORITY_SCOPE_UNRESOLVED",),
        )
    if not item.lifecycle_state_known:
        return ReaderAssessment(
            Decision.HOLD,
            ReaderDisposition.HOLD,
            False,
            ("LIFECYCLE_STATE_UNRESOLVED",),
        )

    if item.historical:
        if item.reentry_purpose not in _ALLOWED_REENTRY_PURPOSES:
            return ReaderAssessment(
                Decision.HOLD,
                ReaderDisposition.HOLD,
                False,
                ("HISTORICAL_REENTRY_REQUIRES_EXPLICIT_PURPOSE",),
            )
        return ReaderAssessment(
            Decision.PASS,
            ReaderDisposition.HISTORICAL_REENTRY,
            False,
            ("BOUNDED_HISTORICAL_REENTRY",),
        )

    if item.current_surface and not item.conflict and not item.missing_evidence:
        return ReaderAssessment(
            Decision.PASS,
            ReaderDisposition.READ_CURRENT,
            False,
            ("CURRENT_SURFACE_ELIGIBLE",),
        )

    if not item.receiver_affected or not item.material_delta:
        return ReaderAssessment(
            Decision.PASS,
            ReaderDisposition.NO_WAKE,
            False,
            ("NO_MATERIAL_RECEIVER_WAKE",),
        )

    if item.conflict or item.missing_evidence:
        return ReaderAssessment(
            Decision.HOLD,
            ReaderDisposition.ESCALATE_BOUNDED,
            False,
            ("BOUNDED_ESCALATION_REQUIRED",),
        )

    return ReaderAssessment(
        Decision.PASS,
        ReaderDisposition.READ_AFFECTED_SLICE,
        False,
        ("AFFECTED_SLICE_ONLY",),
    )
