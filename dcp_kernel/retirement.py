from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class RetirementState(str, Enum):
    ACTIVE_ARTIFACT = "ACTIVE_ARTIFACT"
    PHYSICALLY_RETIRED_PROVENANCE_RETAINED = "PHYSICALLY_RETIRED_PROVENANCE_RETAINED"
    STALE_REFERENCE_HOLD = "STALE_REFERENCE_HOLD"
    BROKEN_LIVE_REFERENCE = "BROKEN_LIVE_REFERENCE"
    RETIREMENT_AUDIT_INCOMPLETE = "RETIREMENT_AUDIT_INCOMPLETE"


@dataclass(frozen=True)
class RetirementInput:
    artifact_path: str
    artifact_present: bool
    provenance_retained: bool
    active_reference: bool = False
    rebuild_dependency: bool = False
    caller_audit_complete: bool = False
    rebuild_audit_complete: bool = False
    successor_pointer: str | None = None


@dataclass(frozen=True)
class RetirementAssessment:
    decision: Decision
    state: RetirementState
    normal_reader_eligible: bool
    destructive_action_authorized: bool
    reasons: tuple[str, ...]


def assess_retirement(item: RetirementInput) -> RetirementAssessment:
    """Keep physical absence, stale references and semantic retirement separate.

    A missing predecessor is not revived by an old register. A missing predecessor that
    still has a proven live caller/rebuild dependency is a broken live reference. Unknown
    caller/rebuild state remains HOLD rather than becoming fabricated failure evidence.
    """

    if item.artifact_present:
        return RetirementAssessment(
            decision=Decision.PASS,
            state=RetirementState.ACTIVE_ARTIFACT,
            normal_reader_eligible=False,
            destructive_action_authorized=False,
            reasons=("ARTIFACT_PHYSICALLY_PRESENT",),
        )

    if item.active_reference or item.rebuild_dependency:
        return RetirementAssessment(
            decision=Decision.FAIL,
            state=RetirementState.BROKEN_LIVE_REFERENCE,
            normal_reader_eligible=False,
            destructive_action_authorized=False,
            reasons=("MISSING_ARTIFACT_STILL_HAS_PROVEN_LIVE_DEPENDENCY",),
        )

    if not item.caller_audit_complete or not item.rebuild_audit_complete:
        return RetirementAssessment(
            decision=Decision.HOLD,
            state=RetirementState.RETIREMENT_AUDIT_INCOMPLETE,
            normal_reader_eligible=False,
            destructive_action_authorized=False,
            reasons=("CALLER_OR_REBUILD_AUDIT_INCOMPLETE",),
        )

    if item.provenance_retained and item.successor_pointer:
        return RetirementAssessment(
            decision=Decision.PASS,
            state=RetirementState.PHYSICALLY_RETIRED_PROVENANCE_RETAINED,
            normal_reader_eligible=False,
            destructive_action_authorized=False,
            reasons=(
                "PREDECESSOR_ABSENT_FROM_CURRENT_BRANCH",
                "PROVENANCE_RETAINED",
                "SUCCESSOR_POINTER_PRESENT",
            ),
        )

    return RetirementAssessment(
        decision=Decision.HOLD,
        state=RetirementState.STALE_REFERENCE_HOLD,
        normal_reader_eligible=False,
        destructive_action_authorized=False,
        reasons=("PHYSICAL_RETIREMENT_WITHOUT_SUFFICIENT_PROVENANCE_OR_SUCCESSOR",),
    )
