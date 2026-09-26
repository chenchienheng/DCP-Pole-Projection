from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class CompatibilityState(str, Enum):
    COEXIST = "COEXIST"
    TRANSLATION_REQUIRED = "TRANSLATION_REQUIRED"
    CONTRADICTION_BOUNDARY = "CONTRADICTION_BOUNDARY"
    FORCED_MERGE_REJECTED = "FORCED_MERGE_REJECTED"


@dataclass(frozen=True)
class NativeModel:
    model_id: str
    native_owner: str
    identity: str
    logic_id: str
    authority_domain: str
    representation: str


@dataclass(frozen=True)
class CoexistenceInput:
    left: NativeModel
    right: NativeModel
    common_source_id: str | None = None
    shared_evidence_interface: bool = False
    translation_available: bool = False
    compatibility_conditions_known: bool = False
    contradiction_identified: bool = False
    forced_identity_merge_requested: bool = False
    authority_merge_requested: bool = False


@dataclass(frozen=True)
class CoexistenceAssessment:
    decision: Decision
    state: CompatibilityState
    preserve_native_models: bool
    reasons: tuple[str, ...]


def assess_coexistence(item: CoexistenceInput) -> CoexistenceAssessment:
    """Allow heterogeneous Native logics to coexist without identity/authority collapse."""

    if item.forced_identity_merge_requested or item.authority_merge_requested:
        return CoexistenceAssessment(
            decision=Decision.FAIL,
            state=CompatibilityState.FORCED_MERGE_REJECTED,
            preserve_native_models=True,
            reasons=("COMMON_ORIGIN_DOES_NOT_AUTHORIZE_IDENTITY_OR_AUTHORITY_MERGE",),
        )

    if item.contradiction_identified:
        return CoexistenceAssessment(
            decision=Decision.HOLD,
            state=CompatibilityState.CONTRADICTION_BOUNDARY,
            preserve_native_models=True,
            reasons=("CONTRADICTION_MUST_REMAIN_EXPLICIT_UNTIL_RESOLVED_OR_SCOPED",),
        )

    same_logic = item.left.logic_id == item.right.logic_id
    same_identity = item.left.identity == item.right.identity

    if same_logic and same_identity:
        return CoexistenceAssessment(
            decision=Decision.PASS,
            state=CompatibilityState.COEXIST,
            preserve_native_models=True,
            reasons=("COMPATIBLE_WITHOUT_FORCED_COLLAPSE",),
        )

    if not item.translation_available or not item.compatibility_conditions_known:
        return CoexistenceAssessment(
            decision=Decision.HOLD,
            state=CompatibilityState.TRANSLATION_REQUIRED,
            preserve_native_models=True,
            reasons=(
                "DIFFERENT_NATIVE_LOGIC_REQUIRES_EXPLICIT_TRANSLATION",
                "SAME_SOURCE_DOES_NOT_PROVE_EQUIVALENCE",
            ),
        )

    if not item.shared_evidence_interface:
        return CoexistenceAssessment(
            decision=Decision.HOLD,
            state=CompatibilityState.TRANSLATION_REQUIRED,
            preserve_native_models=True,
            reasons=("SHARED_EVIDENCE_INTERFACE_REQUIRED_FOR_CROSS_MODEL_CLAIMS",),
        )

    return CoexistenceAssessment(
        decision=Decision.PASS,
        state=CompatibilityState.COEXIST,
        preserve_native_models=True,
        reasons=(
            "NATIVE_LOGICS_REMAIN_DISTINCT",
            "TRANSLATION_AND_COMPATIBILITY_BOUNDARY_ESTABLISHED",
        ),
    )
