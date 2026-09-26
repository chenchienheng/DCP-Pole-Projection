"""Bounded integration-drift qualification R0.1.

A branch can be Git-mergeable while its base has advanced. Path cleanliness and
semantic/instruction currency are separate claims.
"""
from dataclasses import dataclass
from enum import Enum


class DriftDisposition(str, Enum):
    QUALIFIED_CANDIDATE = "QUALIFIED_CANDIDATE"
    HOLD = "HOLD"


@dataclass(frozen=True)
class IntegrationDriftEvidence:
    base_behind_by: int
    changed_path_overlap: bool
    instruction_surface_changed: bool
    instruction_requalified: bool
    exact_head_regression_observed: bool


@dataclass(frozen=True)
class IntegrationDriftAssessment:
    disposition: DriftDisposition
    reasons: tuple[str, ...]


def qualify_integration_drift(evidence: IntegrationDriftEvidence) -> IntegrationDriftAssessment:
    reasons: list[str] = []
    if evidence.base_behind_by < 0:
        reasons.append("INVALID_BASE_BEHIND_COUNT")
    if evidence.changed_path_overlap:
        reasons.append("CHANGED_PATH_OVERLAP_REQUIRES_RECONCILIATION")
    if evidence.base_behind_by > 0 and evidence.instruction_surface_changed and not evidence.instruction_requalified:
        reasons.append("INSTRUCTION_DRIFT_NOT_REQUALIFIED")
    if evidence.base_behind_by > 0 and not evidence.exact_head_regression_observed:
        reasons.append("BASE_DRIFT_REGRESSION_NOT_OBSERVED")

    return IntegrationDriftAssessment(
        DriftDisposition.HOLD if reasons else DriftDisposition.QUALIFIED_CANDIDATE,
        tuple(reasons) if reasons else ("BASE_DRIFT_REQUALIFIED_WITHOUT_CONFLICT_INFERENCE",),
    )
