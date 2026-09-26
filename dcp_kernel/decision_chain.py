from __future__ import annotations

from dataclasses import dataclass

from .action_gate import ActionGateAssessment
from .coexistence import CoexistenceAssessment
from .judgment import JudgmentAssessment
from .meaning_compile import MeaningCompileAssessment
from .models import Decision


@dataclass(frozen=True)
class DecisionChainAssessment:
    decision: Decision
    meaning: MeaningCompileAssessment
    judgment: JudgmentAssessment
    coexistence: CoexistenceAssessment | None
    action_gate: ActionGateAssessment
    first_break: str | None
    reasons: tuple[str, ...]


def assess_decision_chain(
    *,
    meaning: MeaningCompileAssessment,
    judgment: JudgmentAssessment,
    action_gate: ActionGateAssessment,
    coexistence: CoexistenceAssessment | None = None,
) -> DecisionChainAssessment:
    """Compose abstract-to-concrete, judgment, coexistence and restraint into one pre-action chain.

    The chain does not execute, approve or mutate authority. It only determines
    whether a work-contract candidate may be compiled without outsourcing judgment,
    forcing model identity merge, or acting before meaning/evidence boundaries exist.
    """

    stages = (
        ("MEANING", meaning.decision, meaning.reasons),
        ("JUDGMENT", judgment.decision, judgment.reasons),
        ("COEXISTENCE", coexistence.decision, coexistence.reasons) if coexistence else None,
        ("ACTION_GATE", action_gate.decision, action_gate.reasons),
    )

    for stage in stages:
        if stage is None:
            continue
        name, decision, reasons = stage
        if decision is not Decision.PASS:
            return DecisionChainAssessment(
                decision=decision,
                meaning=meaning,
                judgment=judgment,
                coexistence=coexistence,
                action_gate=action_gate,
                first_break=name,
                reasons=tuple(reasons),
            )

    if not meaning.capability_claim_allowed:
        return DecisionChainAssessment(
            decision=Decision.HOLD,
            meaning=meaning,
            judgment=judgment,
            coexistence=coexistence,
            action_gate=action_gate,
            first_break="MEANING",
            reasons=("MEANING_NOT_COMPILED_TO_OBSERVABLE_CAPABILITY_CANDIDATE",),
        )

    if judgment.recommendation_is_decision:
        return DecisionChainAssessment(
            decision=Decision.FAIL,
            meaning=meaning,
            judgment=judgment,
            coexistence=coexistence,
            action_gate=action_gate,
            first_break="JUDGMENT",
            reasons=("RECOMMENDATION_IMPERSONATED_DECISION",),
        )

    return DecisionChainAssessment(
        decision=Decision.PASS,
        meaning=meaning,
        judgment=judgment,
        coexistence=coexistence,
        action_gate=action_gate,
        first_break=None,
        reasons=(
            "MEANING_JUDGMENT_COEXISTENCE_AND_RESTRAINT_ALIGNED",
            "WORK_CONTRACT_COMPILATION_MAY_PROCEED_BUT_EXECUTION_AUTHORITY_IS_NOT_GRANTED",
        ),
    )
