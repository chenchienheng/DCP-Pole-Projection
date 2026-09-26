from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class MeaningLevel(str, Enum):
    HUMAN_MEANING = "HUMAN_MEANING"
    PRIMITIVE_CANDIDATE = "PRIMITIVE_CANDIDATE"
    STRUCTURED_CANDIDATE = "STRUCTURED_CANDIDATE"
    OBSERVABLE_CAPABILITY_CANDIDATE = "OBSERVABLE_CAPABILITY_CANDIDATE"


@dataclass(frozen=True)
class MeaningCompileInput:
    source_id: str
    meaning_statement: str
    primitive: str | None = None
    relation: str | None = None
    constraint: str | None = None
    gate: str | None = None
    action_delta: str | None = None
    evidence_requirement: str | None = None
    return_target: str | None = None
    rebuild_effect: str | None = None


@dataclass(frozen=True)
class MeaningCompileAssessment:
    decision: Decision
    source_id: str
    level: MeaningLevel
    capability_claim_allowed: bool
    reasons: tuple[str, ...]


def compile_meaning(item: MeaningCompileInput) -> MeaningCompileAssessment:
    """Compile abstract meaning only as far as observable behavior permits.

    Human meaning is a valid Source but never a Runtime instruction by itself.
    A capability claim requires a complete path to observable action/evidence/
    return/rebuild difference. This function does not approve or execute action.
    """

    if not item.meaning_statement.strip():
        return MeaningCompileAssessment(
            decision=Decision.HOLD,
            source_id=item.source_id,
            level=MeaningLevel.HUMAN_MEANING,
            capability_claim_allowed=False,
            reasons=("MEANING_SOURCE_EMPTY",),
        )

    if not item.primitive:
        return MeaningCompileAssessment(
            decision=Decision.PASS,
            source_id=item.source_id,
            level=MeaningLevel.HUMAN_MEANING,
            capability_claim_allowed=False,
            reasons=("ABSTRACT_MEANING_RETAINED_WITHOUT_CAPABILITY_CLAIM",),
        )

    if not item.relation or not item.constraint:
        return MeaningCompileAssessment(
            decision=Decision.HOLD,
            source_id=item.source_id,
            level=MeaningLevel.PRIMITIVE_CANDIDATE,
            capability_claim_allowed=False,
            reasons=("RELATION_OR_CONSTRAINT_NOT_COMPILED",),
        )

    if not item.gate or not item.action_delta:
        return MeaningCompileAssessment(
            decision=Decision.HOLD,
            source_id=item.source_id,
            level=MeaningLevel.STRUCTURED_CANDIDATE,
            capability_claim_allowed=False,
            reasons=("NO_OBSERVABLE_NEXT_BEHAVIOR_DIFFERENCE",),
        )

    if not item.evidence_requirement or not item.return_target or not item.rebuild_effect:
        return MeaningCompileAssessment(
            decision=Decision.HOLD,
            source_id=item.source_id,
            level=MeaningLevel.STRUCTURED_CANDIDATE,
            capability_claim_allowed=False,
            reasons=("EVIDENCE_RETURN_REBUILD_CHAIN_INCOMPLETE",),
        )

    return MeaningCompileAssessment(
        decision=Decision.PASS,
        source_id=item.source_id,
        level=MeaningLevel.OBSERVABLE_CAPABILITY_CANDIDATE,
        capability_claim_allowed=True,
        reasons=(
            "MEANING_COMPILED_TO_OBSERVABLE_BEHAVIOR_DIFFERENCE",
            "CAPABILITY_REMAINS_CANDIDATE_UNTIL_WORLD_EVIDENCE_AND_REBUILD",
        ),
    )
