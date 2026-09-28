"""Bounded public-entry semantic verifier R0.1.

This verifier intentionally avoids treating keyword presence as an asserted
current claim. It classifies a sentence-sized context before applying entry
surface consistency checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EntryDisposition(str, Enum):
    QUALIFIED_CANDIDATE = "QUALIFIED_CANDIDATE"
    HOLD = "HOLD"


class AssertionContext(str, Enum):
    CURRENT_ASSERTION = "CURRENT_ASSERTION"
    NEGATED = "NEGATED"
    HISTORICAL = "HISTORICAL"
    ABSENT = "ABSENT"


class SemanticBoundary(str, Enum):
    HISTORICAL_TO_CURRENT = "HISTORICAL_TO_CURRENT"
    CANDIDATE_TO_RUNTIME = "CANDIDATE_TO_RUNTIME"
    RECEIPT_TO_READBACK = "RECEIPT_TO_READBACK"
    DELIVERY_TO_USE = "DELIVERY_TO_USE"
    CAPABILITY_TO_AUTHORITY = "CAPABILITY_TO_AUTHORITY"
    ARTIFACT_TO_RETIRED = "ARTIFACT_TO_RETIRED"


@dataclass(frozen=True)
class EntrySurfaceEvidence:
    readme_human_orientation: bool
    manifest_current_resolution: bool
    status_runtime_established: bool
    status_native_authority_established: bool
    status_marks_historical_compatibility: bool


@dataclass(frozen=True)
class EntryAssessment:
    disposition: EntryDisposition
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SemanticPromotionEvidence:
    boundary: SemanticBoundary
    stable_binding: bool = False
    purpose_qualified: bool = False
    authority_qualified: bool = False
    evidence_observed: bool = False
    explicit_current_pointer: bool = False
    execution_observed: bool = False
    runtime_environment_observed: bool = False
    acceptance_observed: bool = False
    receipt_observed: bool = False
    discoverable_observed: bool = False
    readback_observed: bool = False
    delivery_observed: bool = False
    reader_observed: bool = False
    explicit_use_observed: bool = False
    capability_observed: bool = False
    data_boundary_qualified: bool = False
    unique_delta_inventoried: bool = False
    successor_coverage_observed: bool = False
    evidence_preserved: bool = False
    retirement_authority_qualified: bool = False


NEGATION_CUES = (
    "not establish", "does not establish", "do not establish", "cannot establish",
    "not runtime", "runtime evidence: not established", "not the", "不是", "不建立",
    "不能建立", "未建立", "不構成",
)
HISTORICAL_CUES = (
    "historical", "history", "earlier", "legacy", "compatibility", "historical phrase",
    "歷史", "早期", "舊", "相容",
)


def classify_claim_context(text: str, phrase: str) -> AssertionContext:
    """Classify phrase use from its local sentence/line, not raw document presence."""
    low = text.lower()
    target = phrase.lower()
    pos = low.find(target)
    if pos < 0:
        return AssertionContext.ABSENT

    start = max(low.rfind("\n", 0, pos), low.rfind(".", 0, pos), low.rfind("。", 0, pos)) + 1
    ends = [x for x in (low.find("\n", pos), low.find(".", pos), low.find("。", pos)) if x >= 0]
    end = min(ends) if ends else len(low)
    local = low[start:end]

    if any(cue in local for cue in NEGATION_CUES):
        return AssertionContext.NEGATED
    if any(cue in local for cue in HISTORICAL_CUES):
        return AssertionContext.HISTORICAL
    return AssertionContext.CURRENT_ASSERTION


def qualify_entry_surfaces(evidence: EntrySurfaceEvidence) -> EntryAssessment:
    reasons: list[str] = []
    if not evidence.readme_human_orientation:
        reasons.append("README_HUMAN_ORIENTATION_MISSING")
    if not evidence.manifest_current_resolution:
        reasons.append("MANIFEST_CURRENT_RESOLUTION_MISSING")
    if evidence.status_runtime_established:
        reasons.append("STATUS_RUNTIME_PROMOTION_CONFLICT")
    if evidence.status_native_authority_established:
        reasons.append("STATUS_NATIVE_AUTHORITY_PROMOTION_CONFLICT")
    if not evidence.status_marks_historical_compatibility:
        reasons.append("STATUS_HISTORICAL_BOUNDARY_MISSING")

    return EntryAssessment(
        EntryDisposition.HOLD if reasons else EntryDisposition.QUALIFIED_CANDIDATE,
        tuple(reasons) if reasons else ("README_MANIFEST_STATUS_ROLES_ARE_BOUNDED_AND_COMPATIBLE",),
    )


PROMOTION_REQUIREMENTS = {
    SemanticBoundary.HISTORICAL_TO_CURRENT: (
        "stable_binding", "purpose_qualified", "authority_qualified",
        "evidence_observed", "explicit_current_pointer",
    ),
    SemanticBoundary.CANDIDATE_TO_RUNTIME: (
        "stable_binding", "purpose_qualified", "authority_qualified",
        "execution_observed", "runtime_environment_observed", "acceptance_observed",
    ),
    SemanticBoundary.RECEIPT_TO_READBACK: (
        "stable_binding", "receipt_observed", "discoverable_observed", "readback_observed",
    ),
    SemanticBoundary.DELIVERY_TO_USE: (
        "stable_binding", "delivery_observed", "reader_observed", "explicit_use_observed",
    ),
    SemanticBoundary.CAPABILITY_TO_AUTHORITY: (
        "stable_binding", "purpose_qualified", "capability_observed",
        "authority_qualified", "data_boundary_qualified",
    ),
    SemanticBoundary.ARTIFACT_TO_RETIRED: (
        "stable_binding", "unique_delta_inventoried", "successor_coverage_observed",
        "evidence_preserved", "retirement_authority_qualified",
    ),
}


def qualify_semantic_promotion(evidence: SemanticPromotionEvidence) -> EntryAssessment:
    """Require boundary-specific evidence before one semantic state can promote to another."""
    required = PROMOTION_REQUIREMENTS[evidence.boundary]
    missing = tuple(name for name in required if getattr(evidence, name) is not True)
    if missing:
        return EntryAssessment(
            EntryDisposition.HOLD,
            tuple("MISSING_" + name.upper() for name in missing),
        )
    return EntryAssessment(
        EntryDisposition.QUALIFIED_CANDIDATE,
        ("SEMANTIC_PROMOTION_BOUNDARY_QUALIFIED:" + evidence.boundary.value,),
    )
