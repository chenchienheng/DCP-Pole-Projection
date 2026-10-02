from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class FeedbackDisposition(str, Enum):
    STAY_LOCAL = "STAY_LOCAL"
    NO_MATERIAL_CONFLICT = "NO_MATERIAL_CONFLICT"
    READ_AFFECTED_SLICE = "READ_AFFECTED_SLICE"
    REBUILD_REQUIRED = "REBUILD_REQUIRED"
    HOLD_REPRESENTATION_DRIFT = "HOLD_REPRESENTATION_DRIFT"
    HOLD_AUTHORITY_INFLATION = "HOLD_AUTHORITY_INFLATION"
    HOLD_NATIVE_BODY_COPY = "HOLD_NATIVE_BODY_COPY"


@dataclass(frozen=True)
class CrossPoleFeedbackInput:
    source_pole: str
    receiver_pole: str
    affected_receivers: tuple[str, ...]
    material_delta: bool
    counterexample_present: bool = False
    representation_backmap_preserved: bool = True
    native_body_copy_requested: bool = False
    authority_transfer_requested: bool = False
    receiver_native_disposition_observed: bool = False
    behavior_delta_observed: bool = False
    repeat_failure_suppressed: bool = False
    retested: bool = False


@dataclass(frozen=True)
class CrossPoleFeedbackAssessment:
    decision: Decision
    disposition: FeedbackDisposition
    reasons: tuple[str, ...]
    local_rebuild_required: bool
    maturity_credit: bool


def assess_cross_pole_feedback(item: CrossPoleFeedbackInput) -> CrossPoleFeedbackAssessment:
    """Turn another pole's material feedback into bounded DCP reasoning input.

    This gate deliberately separates learning from copying, understanding from
    authority transfer, and successful output from demonstrated behavior change.
    """

    if item.native_body_copy_requested:
        return CrossPoleFeedbackAssessment(
            decision=Decision.FAIL,
            disposition=FeedbackDisposition.HOLD_NATIVE_BODY_COPY,
            reasons=("READ_AFFECTED_SLICE_NOT_NATIVE_BODY",),
            local_rebuild_required=False,
            maturity_credit=False,
        )

    if item.authority_transfer_requested:
        return CrossPoleFeedbackAssessment(
            decision=Decision.FAIL,
            disposition=FeedbackDisposition.HOLD_AUTHORITY_INFLATION,
            reasons=("UNDERSTANDING_DOES_NOT_TRANSFER_AUTHORITY",),
            local_rebuild_required=False,
            maturity_credit=False,
        )

    if item.receiver_pole not in item.affected_receivers:
        return CrossPoleFeedbackAssessment(
            decision=Decision.PASS,
            disposition=FeedbackDisposition.STAY_LOCAL,
            reasons=("RECEIVER_NOT_MATERIALLY_AFFECTED",),
            local_rebuild_required=False,
            maturity_credit=False,
        )

    if not item.material_delta:
        return CrossPoleFeedbackAssessment(
            decision=Decision.PASS,
            disposition=FeedbackDisposition.NO_MATERIAL_CONFLICT,
            reasons=("NO_MATERIAL_DELTA_STOP_PROPAGATION",),
            local_rebuild_required=False,
            maturity_credit=False,
        )

    if not item.representation_backmap_preserved:
        return CrossPoleFeedbackAssessment(
            decision=Decision.HOLD,
            disposition=FeedbackDisposition.HOLD_REPRESENTATION_DRIFT,
            reasons=("REPRESENTATION_NO_LONGER_BACKMAPS_TO_SAME_EXISTENCE",),
            local_rebuild_required=True,
            maturity_credit=False,
        )

    if item.counterexample_present:
        return CrossPoleFeedbackAssessment(
            decision=Decision.HOLD,
            disposition=FeedbackDisposition.REBUILD_REQUIRED,
            reasons=("COUNTEREXAMPLE_INVALIDATES_AFFECTED_ASSUMPTION",),
            local_rebuild_required=True,
            maturity_credit=False,
        )

    maturity_credit = all(
        (
            item.receiver_native_disposition_observed,
            item.behavior_delta_observed,
            item.repeat_failure_suppressed,
            item.retested,
        )
    )

    reasons = ["MATERIAL_RECEIVER_SPECIFIC_FEEDBACK"]
    if not maturity_credit:
        reasons.append("SINGLE_SUCCESS_OR_RETURN_IS_NOT_MATURITY_PROOF")

    return CrossPoleFeedbackAssessment(
        decision=Decision.PASS,
        disposition=FeedbackDisposition.READ_AFFECTED_SLICE,
        reasons=tuple(reasons),
        local_rebuild_required=True,
        maturity_credit=maturity_credit,
    )
