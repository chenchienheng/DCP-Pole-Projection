from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .models import Decision


class CarrierClass(str, Enum):
    STORAGE = "STORAGE"
    TEMPORAL = "TEMPORAL"
    MESSAGE_EVENT = "MESSAGE_EVENT"
    REPRESENTATION = "REPRESENTATION"
    INTERACTIVE_EXECUTION = "INTERACTIVE_EXECUTION"
    API_SERVICE = "API_SERVICE"
    MODEL_GEOMETRY = "MODEL_GEOMETRY"
    OTHER = "OTHER"


@dataclass(frozen=True)
class CarrierCandidate:
    carrier_id: str
    carrier_class: CarrierClass
    capabilities: tuple[str, ...]
    authority_valid: bool
    rights_valid: bool
    evidence_available: bool
    return_supported: bool
    fidelity_supported: bool
    risk_allowed: bool
    available: bool = True
    vendor_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class CarrierNeed:
    stable_life_id: str
    required_effect: str
    required_capability: str
    return_target: str


@dataclass(frozen=True)
class CarrierResolution:
    decision: Decision
    carrier: CarrierCandidate | None
    reasons: tuple[str, ...] = ()
    excluded: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


def resolve_carrier_binding(
    need: CarrierNeed,
    candidates: tuple[CarrierCandidate, ...],
) -> CarrierResolution:
    """Select a replaceable carrier by capability and boundary, never by vendor order."""

    eligible: list[CarrierCandidate] = []
    excluded: dict[str, tuple[str, ...]] = {}

    for item in candidates:
        reasons: list[str] = []
        if not item.available:
            reasons.append("CARRIER_UNAVAILABLE")
        if need.required_capability not in item.capabilities:
            reasons.append("REQUIRED_CAPABILITY_MISSING")
        if not item.authority_valid:
            reasons.append("AUTHORITY_INVALID")
        if not item.rights_valid:
            reasons.append("RIGHTS_INVALID")
        if not item.evidence_available:
            reasons.append("CAPABILITY_EVIDENCE_MISSING")
        if not item.return_supported:
            reasons.append("RETURN_PATH_UNSUPPORTED")
        if not item.fidelity_supported:
            reasons.append("FIDELITY_NOT_PROVEN")
        if not item.risk_allowed:
            reasons.append("RISK_NOT_ALLOWED")

        if reasons:
            excluded[item.carrier_id] = tuple(reasons)
        else:
            eligible.append(item)

    if not eligible:
        return CarrierResolution(
            decision=Decision.HOLD,
            carrier=None,
            reasons=("NO_ELIGIBLE_CARRIER_BINDING",),
            excluded=excluded,
        )

    # Capability/boundary eligibility does not itself define a preference policy.
    # Choosing the lexicographically first carrier would silently turn carrier identity
    # into routing authority.  Multiple lawful options therefore remain Freedom until a
    # Need-specific selection policy (resource, cost, locality, fidelity, etc.) resolves
    # the tie in a higher layer.
    if len(eligible) > 1:
        return CarrierResolution(
            decision=Decision.HOLD,
            carrier=None,
            reasons=("MULTIPLE_ELIGIBLE_CARRIERS_REQUIRE_EXPLICIT_SELECTION_POLICY",),
            excluded=excluded,
        )

    return CarrierResolution(
        decision=Decision.PASS,
        carrier=eligible[0],
        reasons=("SOLE_ELIGIBLE_CARRIER_SELECTED_BY_CAPABILITY_AND_BOUNDARY",),
        excluded=excluded,
    )


def validate_carrier_substitution(
    *,
    stable_life_id_before: str,
    stable_life_id_after: str,
    source_identity_preserved: bool,
    evidence_lineage_preserved: bool,
    return_target_preserved: bool,
) -> tuple[Decision, tuple[str, ...]]:
    reasons: list[str] = []
    if stable_life_id_before != stable_life_id_after:
        reasons.append("STABLE_IDENTITY_CHANGED_BY_CARRIER_SUBSTITUTION")
    if not source_identity_preserved:
        reasons.append("SOURCE_IDENTITY_NOT_PRESERVED")
    if not evidence_lineage_preserved:
        reasons.append("EVIDENCE_LINEAGE_NOT_PRESERVED")
    if not return_target_preserved:
        reasons.append("RETURN_TARGET_NOT_PRESERVED")

    if reasons:
        return Decision.FAIL, tuple(reasons)
    return Decision.PASS, ("CARRIER_SUBSTITUTION_PRESERVES_STABLE_LIFE",)
