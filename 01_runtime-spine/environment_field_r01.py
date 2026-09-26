"""Bounded XuanLing environment-field qualification R0.1.

An environment field is a Need-relative composition of replaceable carriers.
It is not a permanent topology and no carrier inherits Native Identity/Authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Sequence


class EnvironmentFieldDisposition(str, Enum):
    QUALIFIED_CANDIDATE = "QUALIFIED_CANDIDATE"
    HOLD = "HOLD"


@dataclass(frozen=True)
class EnvironmentCarrier:
    carrier_id: str
    capabilities: FrozenSet[str]
    authority_claim: bool = False


@dataclass(frozen=True)
class EnvironmentFieldCandidate:
    field_id: str
    stable_need: str
    carriers: tuple[EnvironmentCarrier, ...]
    claim_ceiling: FrozenSet[str]


@dataclass(frozen=True)
class EnvironmentFieldAssessment:
    disposition: EnvironmentFieldDisposition
    reasons: tuple[str, ...]
    covered_capabilities: FrozenSet[str]


@dataclass(frozen=True)
class CarrierReplacementEvidence:
    stable_need: str
    old_carrier_id: str
    new_carrier_id: str
    current_requalified: bool
    evidence_rebound: bool
    return_route_rebound: bool
    authority_requalified: bool


REQUIRED_FIELD_CAPABILITIES = frozenset({
    "CURRENT_RESOLUTION",
    "EXECUTABLE_EVIDENCE",
    "DURABLE_REENTRY",
    "RETURN",
})
REQUIRED_CEILINGS = frozenset({"NOT_RUNTIME", "NO_GLOBAL_TOPOLOGY"})


def qualify_environment_field(candidate: EnvironmentFieldCandidate) -> EnvironmentFieldAssessment:
    reasons: list[str] = []
    if not candidate.field_id.strip():
        reasons.append("FIELD_ID_MISSING")
    if not candidate.stable_need.strip():
        reasons.append("STABLE_NEED_MISSING")

    ids = [c.carrier_id for c in candidate.carriers]
    if len(ids) < 2:
        reasons.append("MULTI_CARRIER_COMPOSITION_NOT_PROVEN")
    if len(ids) != len(set(ids)):
        reasons.append("DUPLICATE_CARRIER_ID")
    if any(c.authority_claim for c in candidate.carriers):
        reasons.append("CARRIER_AUTHORITY_PROMOTION_PROHIBITED")

    covered = frozenset().union(*(c.capabilities for c in candidate.carriers)) if candidate.carriers else frozenset()
    missing = REQUIRED_FIELD_CAPABILITIES - covered
    if missing:
        reasons.append("MISSING_FIELD_CAPABILITIES:" + ",".join(sorted(missing)))

    if not REQUIRED_CEILINGS.issubset(candidate.claim_ceiling):
        reasons.append("CLAIM_CEILING_INSUFFICIENT")

    return EnvironmentFieldAssessment(
        EnvironmentFieldDisposition.HOLD if reasons else EnvironmentFieldDisposition.QUALIFIED_CANDIDATE,
        tuple(reasons) if reasons else ("BOUNDED_MULTI_CARRIER_FIELD_QUALIFIED_WITHOUT_RUNTIME_CLAIM",),
        covered,
    )


def qualify_carrier_replacement(
    evidence: CarrierReplacementEvidence,
    *,
    expected_stable_need: str,
) -> EnvironmentFieldAssessment:
    """A replacement is valid only if the Need and all live bindings survive."""
    reasons: list[str] = []
    if evidence.stable_need != expected_stable_need:
        reasons.append("STABLE_NEED_BINDING_MISMATCH")
    if evidence.old_carrier_id == evidence.new_carrier_id:
        reasons.append("REPLACEMENT_REQUIRES_DISTINCT_CARRIER")
    if not evidence.current_requalified:
        reasons.append("CURRENT_NOT_REQUALIFIED")
    if not evidence.evidence_rebound:
        reasons.append("EVIDENCE_NOT_REBOUND")
    if not evidence.return_route_rebound:
        reasons.append("RETURN_ROUTE_NOT_REBOUND")
    if not evidence.authority_requalified:
        reasons.append("AUTHORITY_NOT_REQUALIFIED")

    return EnvironmentFieldAssessment(
        EnvironmentFieldDisposition.HOLD if reasons else EnvironmentFieldDisposition.QUALIFIED_CANDIDATE,
        tuple(reasons) if reasons else ("CARRIER_REPLACEMENT_PRESERVES_NEED_AND_REQUALIFIED_BINDINGS",),
        frozenset(),
    )
