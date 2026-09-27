from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum

from .models import Decision


class EffectClass(IntEnum):
    NO_ACTION = 0
    OBSERVE = 1
    PREPARE = 2
    BOUNDED_MUTATION = 3
    HIGH_RISK_MUTATION = 4


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ActionGateInput:
    transition_id: str
    required_effect: EffectClass
    proposed_effect: EffectClass
    risk_level: RiskLevel
    authority_valid: bool
    explicit_high_risk_authority: bool = False
    reversible: bool = True
    recovery_path_present: bool = True
    affected_scope_resolved: bool = True
    evidence_sufficient: bool = True
    responsibility_owner: str | None = None
    return_target: str | None = None


@dataclass(frozen=True)
class ActionGateAssessment:
    decision: Decision
    transition_id: str
    proposed_effect: EffectClass
    permitted_effect_ceiling: EffectClass
    execution_authorized: bool
    reasons: tuple[str, ...]


def assess_action_gate(item: ActionGateInput) -> ActionGateAssessment:
    """Bound candidate action to the minimum necessary effect.

    This evaluator never grants execution authority. It only decides whether a
    proposed effect stays inside the evidence/authority/responsibility envelope.
    """

    reasons: list[str] = []

    if item.proposed_effect > item.required_effect:
        reasons.append("ACTION_EXCEEDS_MINIMUM_NECESSARY_EFFECT")

    mutation_requested = item.proposed_effect >= EffectClass.BOUNDED_MUTATION
    high_risk_action = (
        item.proposed_effect >= EffectClass.HIGH_RISK_MUTATION
        or item.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    )

    if mutation_requested and not item.authority_valid:
        reasons.append("MUTATION_AUTHORITY_MISSING")
    if high_risk_action and not item.explicit_high_risk_authority:
        reasons.append("HIGH_RISK_ACTION_REQUIRES_EXPLICIT_AUTHORITY")
    if mutation_requested and not item.affected_scope_resolved:
        reasons.append("AFFECTED_SCOPE_UNRESOLVED")
    if mutation_requested and not item.evidence_sufficient:
        reasons.append("EVIDENCE_INSUFFICIENT_FOR_MUTATION")
    if mutation_requested and not item.responsibility_owner:
        reasons.append("RESPONSIBILITY_OWNER_MISSING")
    if mutation_requested and not item.return_target:
        reasons.append("RETURN_TARGET_MISSING")
    if not item.reversible and not item.recovery_path_present:
        reasons.append("IRREVERSIBLE_ACTION_WITHOUT_RECOVERY_PATH")

    if reasons:
        return ActionGateAssessment(
            decision=Decision.HOLD,
            transition_id=item.transition_id,
            proposed_effect=item.proposed_effect,
            permitted_effect_ceiling=item.required_effect,
            execution_authorized=False,
            reasons=tuple(reasons),
        )

    return ActionGateAssessment(
        decision=Decision.PASS,
        transition_id=item.transition_id,
        proposed_effect=item.proposed_effect,
        permitted_effect_ceiling=item.required_effect,
        execution_authorized=False,
        reasons=(
            "MINIMUM_NECESSARY_EFFECT_PRESERVED",
            "RESTRAINT_IS_CAPABILITY",
        ),
    )
