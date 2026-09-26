"""Bounded public-entry semantic verifier R0.1.

This verifier intentionally avoids treating keyword presence as an asserted
current claim. It classifies a sentence-sized context before applying entry
surface consistency checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class EntryDisposition(str, Enum):
    QUALIFIED_CANDIDATE = "QUALIFIED_CANDIDATE"
    HOLD = "HOLD"


class AssertionContext(str, Enum):
    CURRENT_ASSERTION = "CURRENT_ASSERTION"
    NEGATED = "NEGATED"
    HISTORICAL = "HISTORICAL"
    ABSENT = "ABSENT"


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
