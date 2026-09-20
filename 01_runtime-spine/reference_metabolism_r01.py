"""Reference-aware metabolism R0.1.

Separates live caller/wake dependencies from audit, self and lineage references so an
old path can leave the normal reader surface without erasing provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReferenceRole(str, Enum):
    LIVE = "LIVE"
    LINEAGE = "LINEAGE"
    SELF = "SELF"
    AUDIT = "AUDIT"
    UNKNOWN = "UNKNOWN"


class MetabolismDisposition(str, Enum):
    KEEP_CURRENT_FACING = "KEEP_CURRENT_FACING"
    WITHDRAW_NORMAL_WAKE = "WITHDRAW_NORMAL_WAKE"
    RETAIN_EVIDENCE_ONLY = "RETAIN_EVIDENCE_ONLY"
    SUCCESSOR_REVIEW = "SUCCESSOR_REVIEW"
    HOLD_UNKNOWN = "HOLD_UNKNOWN"


@dataclass(frozen=True)
class ReferenceEvidence:
    caller_path: str
    target_path: str
    role: ReferenceRole


@dataclass(frozen=True)
class ArtifactMetabolismInput:
    artifact_path: str
    successor_pointer: str | None
    successor_machine_or_executable: bool
    unique_lineage_evidence: bool
    normal_reader_wake: bool
    references: tuple[ReferenceEvidence, ...]


@dataclass(frozen=True)
class ArtifactMetabolismAssessment:
    disposition: MetabolismDisposition
    reasons: tuple[str, ...]
    destructive_action_authorized: bool = False


def assess_artifact_transition(x: ArtifactMetabolismInput) -> ArtifactMetabolismAssessment:
    live = tuple(r for r in x.references if r.role is ReferenceRole.LIVE)
    unknown = tuple(r for r in x.references if r.role is ReferenceRole.UNKNOWN)

    if unknown:
        return ArtifactMetabolismAssessment(
            MetabolismDisposition.HOLD_UNKNOWN,
            ("UNKNOWN_REFERENCE_MAY_STILL_BE_OPERATIONAL",),
        )

    if live and not x.successor_pointer:
        return ArtifactMetabolismAssessment(
            MetabolismDisposition.KEEP_CURRENT_FACING,
            ("LIVE_CALLER_EXISTS_WITHOUT_SUCCESSOR",),
        )

    if live and not x.successor_machine_or_executable:
        return ArtifactMetabolismAssessment(
            MetabolismDisposition.SUCCESSOR_REVIEW,
            ("LIVE_CALLER_SUCCESSOR_BEHAVIOR_NOT_PROVEN",),
        )

    if x.successor_pointer and x.successor_machine_or_executable:
        if x.normal_reader_wake:
            return ArtifactMetabolismAssessment(
                MetabolismDisposition.WITHDRAW_NORMAL_WAKE,
                ("SUCCESSOR_EXISTS_BUT_PREDECESSOR_STILL_WAKES_NORMAL_READER",),
            )
        if x.unique_lineage_evidence:
            return ArtifactMetabolismAssessment(
                MetabolismDisposition.RETAIN_EVIDENCE_ONLY,
                ("SUCCESSOR_COVERS_BEHAVIOR_UNIQUE_LINEAGE_RETAINED",),
            )
        return ArtifactMetabolismAssessment(
            MetabolismDisposition.WITHDRAW_NORMAL_WAKE,
            ("SUCCESSOR_COVERS_BEHAVIOR_PREDECESSOR_NOT_CURRENT_FACING",),
        )

    if x.unique_lineage_evidence:
        return ArtifactMetabolismAssessment(
            MetabolismDisposition.RETAIN_EVIDENCE_ONLY,
            ("NO_LIVE_CALLER_UNIQUE_LINEAGE_RETAINED",),
        )

    return ArtifactMetabolismAssessment(
        MetabolismDisposition.SUCCESSOR_REVIEW,
        ("NO_LIVE_CALLER_BUT_SUCCESSOR_COVERAGE_UNRESOLVED",),
    )
