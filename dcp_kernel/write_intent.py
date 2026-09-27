from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class MutationKind(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPEND = "APPEND"
    SYNC_STATE = "SYNC_STATE"


@dataclass(frozen=True)
class WriteIntentInput:
    intent_id: str
    stable_life_id: str
    source_identity: str
    target_carrier_id: str
    mutation_kind: MutationKind
    authority_valid: bool
    rights_valid: bool
    purpose_valid: bool
    affected_scope_resolved: bool
    expected_revision: str | None
    fidelity_check_present: bool
    evidence_plan_present: bool
    responsibility_owner: str | None
    rollback_or_recovery_present: bool
    return_target: str | None
    target_exists: bool | None = None


@dataclass(frozen=True)
class WriteIntentAssessment:
    decision: Decision
    intent_id: str
    mutation_allowed_as_candidate: bool
    reasons: tuple[str, ...]


def assess_write_intent(item: WriteIntentInput) -> WriteIntentAssessment:
    """Assess a carrier-neutral mutation intent without granting execution authority.

    Repository, platform, agent or tool identity never creates permission to write.
    A PASS means only that a bounded mutation candidate may proceed to the legal
    execution surface; it does not prove execution, absorption, Current or release.
    """

    reasons: list[str] = []

    if not item.stable_life_id:
        reasons.append("STABLE_LIFE_ID_MISSING")
    if not item.source_identity:
        reasons.append("SOURCE_IDENTITY_MISSING")
    if not item.target_carrier_id:
        reasons.append("TARGET_CARRIER_MISSING")
    if not item.authority_valid:
        reasons.append("MUTATION_AUTHORITY_MISSING")
    if not item.rights_valid:
        reasons.append("RIGHTS_INVALID")
    if not item.purpose_valid:
        reasons.append("PURPOSE_INVALID")
    if not item.affected_scope_resolved:
        reasons.append("AFFECTED_SCOPE_UNRESOLVED")
    if not item.fidelity_check_present:
        reasons.append("FIDELITY_CHECK_MISSING")
    if not item.evidence_plan_present:
        reasons.append("EVIDENCE_PLAN_MISSING")
    if not item.responsibility_owner:
        reasons.append("RESPONSIBILITY_OWNER_MISSING")
    if not item.return_target:
        reasons.append("RETURN_TARGET_MISSING")

    revision_sensitive = item.mutation_kind in {
        MutationKind.UPDATE,
        MutationKind.DELETE,
        MutationKind.APPEND,
        MutationKind.SYNC_STATE,
    }
    if revision_sensitive and not item.expected_revision:
        reasons.append("EXPECTED_REVISION_MISSING")

    if item.mutation_kind in {MutationKind.UPDATE, MutationKind.DELETE}:
        if item.target_exists is not True:
            reasons.append("TARGET_EXISTENCE_NOT_PROVEN")

    if item.mutation_kind in {MutationKind.UPDATE, MutationKind.DELETE, MutationKind.SYNC_STATE}:
        if not item.rollback_or_recovery_present:
            reasons.append("ROLLBACK_OR_RECOVERY_MISSING")

    if reasons:
        return WriteIntentAssessment(
            decision=Decision.HOLD,
            intent_id=item.intent_id,
            mutation_allowed_as_candidate=False,
            reasons=tuple(reasons),
        )

    return WriteIntentAssessment(
        decision=Decision.PASS,
        intent_id=item.intent_id,
        mutation_allowed_as_candidate=True,
        reasons=(
            "BOUNDED_WRITE_INTENT_COMPLETE",
            "PASS_DOES_NOT_GRANT_EXECUTION_OR_NATIVE_ABSORPTION",
        ),
    )
