"""Cross-carrier Current resolver R0.1.

Prevents GitHub/Drive/Memory retrieval order or newest timestamp from silently
becoming Current. Memory is a resolver cue, not mutable Current/evidence/Authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CarrierKind(str, Enum):
    GITHUB = "GITHUB"
    DRIVE = "DRIVE"
    LIBRARY = "LIBRARY"
    MEMORY = "MEMORY"


class CurrentResolutionDisposition(str, Enum):
    RESOLVED = "RESOLVED"
    HOLD = "HOLD"


@dataclass(frozen=True)
class CarrierCurrentCandidate:
    carrier: CarrierKind
    locator: str
    stable_referent: str
    purpose: str
    declared_current_pointer: bool
    current_for_purpose: bool
    source_observed: bool
    mutable_current_authority: bool
    evidence_authority: bool
    observed_at: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.carrier, CarrierKind):
            raise TypeError("carrier must be CarrierKind")
        for field_name in ("locator", "stable_referent", "purpose"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise TypeError(f"{field_name} must be a non-empty string")
        for field_name in (
            "declared_current_pointer",
            "current_for_purpose",
            "source_observed",
            "mutable_current_authority",
            "evidence_authority",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} must be bool")
        if self.observed_at is not None and not isinstance(self.observed_at, str):
            raise TypeError("observed_at must be str or None")


@dataclass(frozen=True)
class CurrentResolution:
    disposition: CurrentResolutionDisposition
    locator: str | None
    carrier: CarrierKind | None
    reasons: tuple[str, ...]


def resolve_current(
    candidates: tuple[CarrierCurrentCandidate, ...],
    *,
    stable_referent: str,
    purpose: str,
) -> CurrentResolution:
    eligible = [
        c for c in candidates
        if c.stable_referent == stable_referent
        and c.purpose == purpose
        and c.declared_current_pointer
        and c.current_for_purpose
        and c.source_observed
        and c.mutable_current_authority
    ]

    # Memory can guide where to look, but cannot independently become mutable Current.
    eligible = [c for c in eligible if c.carrier is not CarrierKind.MEMORY]

    if not eligible:
        return CurrentResolution(
            CurrentResolutionDisposition.HOLD,
            None,
            None,
            ("NO_QUALIFIED_MUTABLE_CURRENT_POINTER",),
        )

    unique = {(c.carrier, c.locator) for c in eligible}
    if len(unique) != 1:
        return CurrentResolution(
            CurrentResolutionDisposition.HOLD,
            None,
            None,
            ("MULTIPLE_QUALIFIED_CURRENT_POINTERS_REQUIRE_RECONCILIATION",),
        )

    chosen = eligible[0]
    return CurrentResolution(
        CurrentResolutionDisposition.RESOLVED,
        chosen.locator,
        chosen.carrier,
        (
            "CURRENT_RESOLVED_BY_POINTER_AND_PURPOSE",
            "RETRIEVAL_ORDER_AND_TIMESTAMP_DO_NOT_GRANT_CURRENT_AUTHORITY",
        ),
    )


def qualify_evidence_source(candidate: CarrierCurrentCandidate) -> bool:
    """Current navigation and evidence authority remain separate claims."""
    return candidate.source_observed and candidate.evidence_authority
