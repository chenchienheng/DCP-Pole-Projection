"""Resource-to-effect accounting R0.1.

Tracks bounded resource cost against observed evidence gain, risk reduction and
useful effect after qualification gates are satisfied.

This is not a universal quality score, does not price human worth, and cannot
override Authority, safety, privacy, or required qualification.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResourceEffectDisposition(str, Enum):
    QUALIFICATION_HOLD = "QUALIFICATION_HOLD"
    EFFECT_UNPROVEN = "EFFECT_UNPROVEN"
    BASELINE = "BASELINE"
    DOMINATED_CANDIDATE = "DOMINATED_CANDIDATE"
    MARGINAL_GAIN_CANDIDATE = "MARGINAL_GAIN_CANDIDATE"


@dataclass(frozen=True)
class ResourceEffectObservation:
    observation_id: str
    need_id: str
    composition_id: str
    qualification_sufficient: bool
    authority_valid: bool
    resource_units: float
    evidence_gain: float       # bounded 0..1, claim-specific
    risk_before: float         # bounded 0..1, same risk claim
    risk_after: float          # bounded 0..1, same risk claim
    useful_effect: float       # bounded 0..1, claim-specific
    effect_observed: bool
    current_for_purpose: bool


@dataclass(frozen=True)
class ResourceEffectAssessment:
    disposition: ResourceEffectDisposition
    resource_units: float
    evidence_gain: float
    risk_reduction: float
    useful_effect: float
    marginal_resource: float | None
    marginal_evidence_gain: float | None
    marginal_risk_reduction: float | None
    marginal_useful_effect: float | None
    reasons: tuple[str, ...]
    claim_ceiling: str = "RESOURCE_EFFECT_ACCOUNTING_CANDIDATE"


def _bounded(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be within 0..1")


def assess_resource_effect(
    observation: ResourceEffectObservation,
    *,
    baseline: ResourceEffectObservation | None = None,
) -> ResourceEffectAssessment:
    if observation.resource_units < 0:
        raise ValueError("resource_units must be non-negative")
    for name in ("evidence_gain", "risk_before", "risk_after", "useful_effect"):
        _bounded(name, getattr(observation, name))

    risk_reduction = observation.risk_before - observation.risk_after

    if not observation.authority_valid or not observation.qualification_sufficient:
        return ResourceEffectAssessment(
            ResourceEffectDisposition.QUALIFICATION_HOLD,
            observation.resource_units,
            observation.evidence_gain,
            risk_reduction,
            observation.useful_effect,
            None, None, None, None,
            ("RESOURCE_EFFICIENCY_CANNOT_OVERRIDE_AUTHORITY_OR_QUALIFICATION",),
        )

    if not observation.current_for_purpose or not observation.effect_observed:
        return ResourceEffectAssessment(
            ResourceEffectDisposition.EFFECT_UNPROVEN,
            observation.resource_units,
            observation.evidence_gain,
            risk_reduction,
            observation.useful_effect,
            None, None, None, None,
            ("RESOURCE_SPEND_WITHOUT_CURRENT_OBSERVED_EFFECT_CANNOT_PROVE_VALUE",),
        )

    if baseline is None:
        return ResourceEffectAssessment(
            ResourceEffectDisposition.BASELINE,
            observation.resource_units,
            observation.evidence_gain,
            risk_reduction,
            observation.useful_effect,
            None, None, None, None,
            ("BASELINE_RECORDED_WITHOUT_UNIVERSAL_QUALITY_SCORE",),
        )

    if baseline.need_id != observation.need_id:
        raise ValueError("baseline must belong to the same Need")
    if not baseline.effect_observed or not baseline.current_for_purpose:
        raise ValueError("baseline effect must be current and observed")

    baseline_risk_reduction = baseline.risk_before - baseline.risk_after
    d_resource = observation.resource_units - baseline.resource_units
    d_evidence = observation.evidence_gain - baseline.evidence_gain
    d_risk = risk_reduction - baseline_risk_reduction
    d_effect = observation.useful_effect - baseline.useful_effect

    dominated = (
        d_resource > 0
        and d_evidence <= 0
        and d_risk <= 0
        and d_effect <= 0
    )
    disposition = (
        ResourceEffectDisposition.DOMINATED_CANDIDATE
        if dominated
        else ResourceEffectDisposition.MARGINAL_GAIN_CANDIDATE
    )
    reasons = (
        ("MORE_RESOURCE_WITHOUT_OBSERVED_GAIN_IS_DOMINATED_CANDIDATE",)
        if dominated
        else ("MARGINAL_RESOURCE_AND_EFFECT_RECORDED_FOR_LOCAL_COMPARISON",)
    )

    return ResourceEffectAssessment(
        disposition,
        observation.resource_units,
        observation.evidence_gain,
        risk_reduction,
        observation.useful_effect,
        d_resource,
        d_evidence,
        d_risk,
        d_effect,
        reasons,
    )
