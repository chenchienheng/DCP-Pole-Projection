from __future__ import annotations

from .models import (
    Decision,
    LearningAssessment,
    LearningDisposition,
    LearningInput,
)

_ALLOWED_REENTRY_PURPOSES = {
    "PROVENANCE",
    "AUDIT",
    "FAILURE_LEARNING",
    "REGRESSION",
    "REBUILD",
    "SUCCESSOR_VALIDATION",
}


def assess_learning_input(item: LearningInput) -> LearningAssessment:
    """Admit only receiver-specific learning without copying another Native Body."""

    if item.native_body_copy_requested:
        return LearningAssessment(
            decision=Decision.FAIL,
            disposition=LearningDisposition.HOLD_CONTAMINATION,
            reasons=("NATIVE_BODY_COPY_PROHIBITED",),
        )

    if not item.authority_in_scope:
        return LearningAssessment(
            decision=Decision.HOLD,
            disposition=LearningDisposition.HOLD_CONTAMINATION,
            reasons=("AUTHORITY_OUT_OF_SCOPE",),
        )

    if item.historical and item.reentry_purpose not in _ALLOWED_REENTRY_PURPOSES:
        return LearningAssessment(
            decision=Decision.HOLD,
            disposition=LearningDisposition.HOLD_CONTAMINATION,
            reasons=("HISTORICAL_REENTRY_REQUIRES_EXPLICIT_PURPOSE",),
        )

    if item.receiver not in item.affected_receivers:
        return LearningAssessment(
            decision=Decision.PASS,
            disposition=LearningDisposition.RECEIVER_NOT_AFFECTED,
            reasons=("NO_RECEIVER_WAKE",),
        )

    if not item.material_delta:
        return LearningAssessment(
            decision=Decision.PASS,
            disposition=LearningDisposition.NO_MATERIAL_DELTA,
            reasons=("STOP_WITHOUT_PROPAGATION",),
        )

    if item.equivalent_receipt_exists:
        return LearningAssessment(
            decision=Decision.PASS,
            disposition=LearningDisposition.REUSE_NO_REPROPAGATION,
            reasons=("UNCHANGED_SOURCE_AND_AFFECTED_EDGE_REUSE_RECEIPT",),
        )

    return LearningAssessment(
        decision=Decision.PASS,
        disposition=LearningDisposition.READ_AFFECTED_SLICE,
        reasons=("MATERIAL_RECEIVER_SPECIFIC_DELTA",),
    )
