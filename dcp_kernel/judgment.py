from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class KnowledgeState(str, Enum):
    KNOWN = "KNOWN"
    INFERRED = "INFERRED"
    SUSPECTED = "SUSPECTED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


class DimensionState(str, Enum):
    SATISFIED = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class JudgmentInput:
    judgment_id: str
    source_classified: bool
    meaning_relevant: bool
    boundary_resolved: bool
    evidence_sufficient: bool
    alternatives_considered: bool
    consequence_assessed: bool
    responsibility_owner: str | None
    return_target: str | None
    rebuild_path_present: bool
    authority_valid: bool
    recommendation_present: bool = False
    expert_confidence: float | None = None
    model_confidence: float | None = None
    majority_agreement: bool = False
    counterexample_channel_open: bool = True
    execution_available: bool = False
    execution_requested: bool = False
    truth_state: DimensionState = DimensionState.UNKNOWN
    scope_state: DimensionState = DimensionState.UNKNOWN
    context_state: DimensionState = DimensionState.UNKNOWN
    goal_state: DimensionState = DimensionState.UNKNOWN
    cost_state: DimensionState = DimensionState.UNKNOWN
    risk_state: DimensionState = DimensionState.UNKNOWN
    relationship_state: DimensionState = DimensionState.NOT_APPLICABLE
    time_state: DimensionState = DimensionState.UNKNOWN
    consequence_state: DimensionState = DimensionState.UNKNOWN


@dataclass(frozen=True)
class JudgmentAssessment:
    decision: Decision
    knowledge_state: KnowledgeState
    execution_permitted_by_judgment: bool
    recommendation_is_decision: bool
    dimension_states: tuple[tuple[str, DimensionState], ...]
    reasons: tuple[str, ...]


def _dimensions(item: JudgmentInput) -> tuple[tuple[str, DimensionState], ...]:
    return (
        ("truth", item.truth_state),
        ("scope", item.scope_state),
        ("context", item.context_state),
        ("goal", item.goal_state),
        ("authority", DimensionState.SATISFIED if item.authority_valid else DimensionState.UNSATISFIED),
        ("cost", item.cost_state),
        ("risk", item.risk_state),
        ("relationship", item.relationship_state),
        ("time", item.time_state),
        ("consequence", item.consequence_state),
    )


def assess_judgment(item: JudgmentInput) -> JudgmentAssessment:
    """Assess judgment without collapsing truth, scope, context or authority.

    A proposition can be true yet unauthorized, locally valid yet globally unsafe,
    or legally allowed yet too risky/costly. The evaluator preserves those
    dimensions instead of forcing them into one RIGHT/WRONG label.
    """

    reasons: list[str] = []
    dimensions = _dimensions(item)

    if not item.source_classified:
        reasons.append("SOURCE_NOT_CLASSIFIED")
    if not item.meaning_relevant:
        reasons.append("MEANING_RELEVANCE_UNRESOLVED")
    if not item.boundary_resolved:
        reasons.append("BOUNDARY_UNRESOLVED")
    if not item.evidence_sufficient:
        reasons.append("EVIDENCE_INSUFFICIENT")
    if not item.alternatives_considered:
        reasons.append("ALTERNATIVES_NOT_CONSIDERED")
    if not item.consequence_assessed:
        reasons.append("CONSEQUENCE_NOT_ASSESSED")
    if not item.responsibility_owner:
        reasons.append("RESPONSIBILITY_OWNER_MISSING")
    if not item.return_target:
        reasons.append("RETURN_TARGET_MISSING")
    if not item.rebuild_path_present:
        reasons.append("REBUILD_PATH_MISSING")
    if not item.authority_valid:
        reasons.append("AUTHORITY_MISSING")
    if item.majority_agreement and not item.counterexample_channel_open:
        reasons.append("MAJORITY_WITHOUT_COUNTEREXAMPLE_CHANNEL")
    if item.execution_requested and not item.execution_available:
        reasons.append("EXECUTION_CAPABILITY_UNAVAILABLE")

    for name, state in dimensions:
        if name == "relationship" and state == DimensionState.NOT_APPLICABLE:
            continue
        if state == DimensionState.UNSATISFIED:
            reasons.append(f"DIMENSION_{name.upper()}_UNSATISFIED")

    if not item.evidence_sufficient or item.truth_state == DimensionState.UNKNOWN:
        knowledge = KnowledgeState.UNKNOWN
    elif not item.source_classified or not item.boundary_resolved:
        knowledge = KnowledgeState.INFERRED
    else:
        knowledge = KnowledgeState.KNOWN

    if reasons:
        return JudgmentAssessment(
            decision=Decision.HOLD,
            knowledge_state=knowledge,
            execution_permitted_by_judgment=False,
            recommendation_is_decision=False,
            dimension_states=dimensions,
            reasons=tuple(dict.fromkeys(reasons)),
        )

    return JudgmentAssessment(
        decision=Decision.PASS,
        knowledge_state=knowledge,
        execution_permitted_by_judgment=item.execution_requested,
        recommendation_is_decision=False,
        dimension_states=dimensions,
        reasons=(
            "MULTIDIMENSIONAL_JUDGMENT_CHAIN_COMPLETE",
            "EXPERTISE_CONFIDENCE_AND_RECOMMENDATION_DID_NOT_CREATE_AUTHORITY",
            "TRUTH_SCOPE_CONTEXT_AUTHORITY_AND_CONSEQUENCE_REMAIN_SEPARATE",
        ),
    )
