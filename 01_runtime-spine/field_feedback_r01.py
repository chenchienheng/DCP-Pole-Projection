"""External-use field feedback projection R0.1.

Turns local Reality histories into bounded generalized nutrient candidates without
requiring raw user/customer histories to leave their Native domains.

This module does not authorize telemetry collection, upload, product changes,
safety intervention, or manufacturer acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FeedbackDisposition(str, Enum):
    GENERALIZABLE_CANDIDATE = "GENERALIZABLE_CANDIDATE"
    LOCAL_ONLY = "LOCAL_ONLY"
    CONFLICT_HOLD = "CONFLICT_HOLD"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class LocalFieldObservation:
    observation_id: str
    local_subject_id: str
    product_family: str
    configuration_class: str
    environment_class: str
    effect_name: str
    effect_value: float | None
    effect_unit: str | None
    outcome_class: str
    evidence_method: str
    confidence: float
    current_for_purpose: bool
    return_authorized: bool
    contains_raw_private_payload: bool = False


@dataclass(frozen=True)
class GeneralizedFieldNutrient:
    product_family: str
    configuration_class: str
    environment_class: str
    effect_name: str
    effect_unit: str | None
    outcome_class: str
    sample_count: int
    mean_effect_value: float | None
    min_confidence: float
    claim_ceiling: str = "GENERALIZED_FIELD_NUTRIENT_CANDIDATE"


@dataclass(frozen=True)
class FieldFeedbackAssessment:
    disposition: FeedbackDisposition
    nutrient: GeneralizedFieldNutrient | None
    reasons: tuple[str, ...]


def project_field_feedback(
    observations: tuple[LocalFieldObservation, ...],
    *,
    min_samples: int = 2,
    min_confidence: float = 0.80,
) -> FieldFeedbackAssessment:
    if not observations:
        return FieldFeedbackAssessment(
            FeedbackDisposition.INSUFFICIENT_EVIDENCE,
            None,
            ("NO_FIELD_OBSERVATIONS",),
        )

    if any(x.contains_raw_private_payload for x in observations):
        return FieldFeedbackAssessment(
            FeedbackDisposition.LOCAL_ONLY,
            None,
            ("RAW_PRIVATE_PAYLOAD_MUST_REMAIN_LOCAL",),
        )

    if any(not x.return_authorized for x in observations):
        return FieldFeedbackAssessment(
            FeedbackDisposition.LOCAL_ONLY,
            None,
            ("GENERALIZED_RETURN_NOT_AUTHORIZED",),
        )

    if any(not x.current_for_purpose for x in observations):
        return FieldFeedbackAssessment(
            FeedbackDisposition.INSUFFICIENT_EVIDENCE,
            None,
            ("OBSERVATION_NOT_CURRENT_FOR_PURPOSE",),
        )

    keys = {
        (
            x.product_family,
            x.configuration_class,
            x.environment_class,
            x.effect_name,
            x.effect_unit,
            x.outcome_class,
        )
        for x in observations
    }
    if len(keys) != 1:
        return FieldFeedbackAssessment(
            FeedbackDisposition.CONFLICT_HOLD,
            None,
            ("INCOMPATIBLE_FIELD_COHORT",),
        )

    if any(x.confidence < min_confidence for x in observations):
        return FieldFeedbackAssessment(
            FeedbackDisposition.INSUFFICIENT_EVIDENCE,
            None,
            ("FIELD_EVIDENCE_BELOW_CONFIDENCE_FLOOR",),
        )

    if len(observations) < min_samples:
        return FieldFeedbackAssessment(
            FeedbackDisposition.INSUFFICIENT_EVIDENCE,
            None,
            ("FIELD_SAMPLE_FLOOR_NOT_MET",),
        )

    values = [x.effect_value for x in observations if x.effect_value is not None]
    mean_value = sum(values) / len(values) if values else None
    key = next(iter(keys))

    nutrient = GeneralizedFieldNutrient(
        product_family=key[0],
        configuration_class=key[1],
        environment_class=key[2],
        effect_name=key[3],
        effect_unit=key[4],
        outcome_class=key[5],
        sample_count=len(observations),
        mean_effect_value=mean_value,
        min_confidence=min(x.confidence for x in observations),
    )
    return FieldFeedbackAssessment(
        FeedbackDisposition.GENERALIZABLE_CANDIDATE,
        nutrient,
        (
            "LOCAL_IDENTIFIERS_EXCLUDED_FROM_NUTRIENT",
            "RAW_CUSTOMER_HISTORY_NOT_REQUIRED",
            "DOWNSTREAM_APPLICABILITY_AND_ADMISSION_REMAIN_SEPARATE",
        ),
    )
