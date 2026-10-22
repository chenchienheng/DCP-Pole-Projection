"""World carrier/mode observation resolver R0.1.

Models observed product-surface mode, execution entitlement and usage attribution as
separate dimensions. It diagnoses mismatches without inferring a provider-side cause.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CarrierModeDisposition(str, Enum):
    CONSISTENT_CHAT = "CONSISTENT_CHAT"
    CONSISTENT_WORK_OBSERVED = "CONSISTENT_WORK_OBSERVED"
    MODE_CAPABILITY_MISMATCH = "MODE_CAPABILITY_MISMATCH"
    USAGE_ATTRIBUTION_RISK = "USAGE_ATTRIBUTION_RISK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class CarrierModeObservation:
    conversation_id: str
    stable_responsibility: str
    observed_surface_mode: str
    cloud_browser_entitled: bool | None
    background_or_delegated_entitled: bool | None
    work_codex_usage_attributed: bool | None
    user_initiated_work_switch: bool | None
    same_conversation_lineage: bool | None


@dataclass(frozen=True)
class CarrierModeAssessment:
    disposition: CarrierModeDisposition
    reasons: tuple[str, ...]
    cause_proven: bool = False


def assess_carrier_mode(obs: CarrierModeObservation) -> CarrierModeAssessment:
    mode = obs.observed_surface_mode.upper()

    if obs.work_codex_usage_attributed is True and mode == "WORK":
        if obs.cloud_browser_entitled is False and obs.background_or_delegated_entitled is False:
            return CarrierModeAssessment(
                CarrierModeDisposition.USAGE_ATTRIBUTION_RISK,
                (
                    "WORK_SURFACE_AND_WORK_USAGE_OBSERVED",
                    "FULL_WORK_EXECUTION_ENTITLEMENT_NOT_OBSERVED",
                    "CAUSE_REQUIRES_PROVIDER_TRANSITION_TELEMETRY",
                ),
            )

    if mode == "WORK":
        if obs.cloud_browser_entitled is False and obs.background_or_delegated_entitled is False:
            return CarrierModeAssessment(
                CarrierModeDisposition.MODE_CAPABILITY_MISMATCH,
                (
                    "WORK_SURFACE_OBSERVED",
                    "FULL_WORK_EXECUTION_ENTITLEMENT_NOT_OBSERVED",
                    "USAGE_POOL_REMAINS_INDEPENDENT_EVIDENCE",
                ),
            )
        if obs.cloud_browser_entitled is True or obs.background_or_delegated_entitled is True:
            return CarrierModeAssessment(
                CarrierModeDisposition.CONSISTENT_WORK_OBSERVED,
                ("WORK_SURFACE_WITH_WORK_EXECUTION_CAPABILITY_OBSERVED",),
            )

    if mode == "CHAT":
        if obs.work_codex_usage_attributed is True:
            return CarrierModeAssessment(
                CarrierModeDisposition.USAGE_ATTRIBUTION_RISK,
                (
                    "CHAT_SURFACE_WITH_WORK_CODEX_USAGE_ATTRIBUTION",
                    "METERING_AND_SURFACE_MODE_DIVERGE",
                ),
            )
        if obs.work_codex_usage_attributed is False:
            return CarrierModeAssessment(
                CarrierModeDisposition.CONSISTENT_CHAT,
                ("CHAT_SURFACE_WITHOUT_WORK_CODEX_USAGE_ATTRIBUTION",),
            )

    return CarrierModeAssessment(
        CarrierModeDisposition.INSUFFICIENT_EVIDENCE,
        ("MODE_ENTITLEMENT_OR_USAGE_EVIDENCE_INCOMPLETE",),
    )
