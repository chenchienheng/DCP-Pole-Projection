from __future__ import annotations

from dataclasses import dataclass

from .models import Decision
from .reality_intake import ObservationState, RealityObservation


@dataclass(frozen=True)
class VisionFragment:
    fragment_id: str
    source_id: str
    source_revision: str | None
    local_locator: str
    content_class: str
    extracted_text: str | None = None
    candidate_labels: tuple[str, ...] = ()
    confidence: float | None = None
    unknowns: tuple[str, ...] = ()


@dataclass(frozen=True)
class VisionProviderResult:
    provider_id: str
    source_id: str
    source_revision: str | None
    observed_at: str
    fragments: tuple[VisionFragment, ...]
    source_rights_valid: bool
    provider_output_is_projection: bool = True


@dataclass(frozen=True)
class VisionObservationAssessment:
    decision: Decision
    observations: tuple[RealityObservation, ...]
    reasons: tuple[str, ...]


def adapt_vision_provider_result(item: VisionProviderResult) -> VisionObservationAssessment:
    """Adapt replaceable vision/OCR output into Reality observations.

    Provider output remains a projection. Confidence is not engineering truth,
    and missing revision/locator/confidence remains explicit uncertainty.
    """

    if not item.source_rights_valid:
        return VisionObservationAssessment(
            Decision.HOLD,
            (),
            ("VISION_SOURCE_RIGHTS_NOT_VALID",),
        )
    if not item.provider_output_is_projection:
        return VisionObservationAssessment(
            Decision.HOLD,
            (),
            ("VISION_PROVIDER_OUTPUT_MUST_REMAIN_PROJECTION",),
        )
    if not item.fragments:
        return VisionObservationAssessment(
            Decision.HOLD,
            (),
            ("VISION_PROVIDER_RETURNED_NO_FRAGMENTS",),
        )

    observations: list[RealityObservation] = []
    for fragment in item.fragments:
        unknowns = list(fragment.unknowns)
        if not fragment.local_locator.strip():
            unknowns.append("LOCAL_LOCATOR_UNKNOWN")
        if item.source_revision is None:
            unknowns.append("SOURCE_REVISION_UNKNOWN")
        if fragment.confidence is None:
            unknowns.append("CONFIDENCE_UNKNOWN")
        elif not 0.0 <= fragment.confidence <= 1.0:
            return VisionObservationAssessment(
                Decision.HOLD,
                (),
                (f"{fragment.fragment_id}:INVALID_CONFIDENCE",),
            )
        elif fragment.confidence < 1.0:
            unknowns.append("EXTRACTION_REQUIRES_VERIFICATION")

        candidate_referents = tuple(
            dict.fromkeys(label for label in fragment.candidate_labels if label.strip())
        )
        observations.append(
            RealityObservation(
                observation_id=fragment.fragment_id,
                carrier_id=item.provider_id,
                source_id=item.source_id,
                source_revision=item.source_revision,
                observed_at=item.observed_at,
                state=ObservationState.OBSERVED,
                content_class=fragment.content_class,
                candidate_referents=candidate_referents,
                uncertainty=tuple(dict.fromkeys(unknowns)),
            )
        )

    return VisionObservationAssessment(
        Decision.PASS,
        tuple(observations),
        (
            "VISION_PROVIDER_OUTPUT_ADAPTED_AS_OBSERVATION_PROJECTION",
            "EXTRACTION_CONFIDENCE_DOES_NOT_GRANT_DOMAIN_TRUTH",
        ),
    )
