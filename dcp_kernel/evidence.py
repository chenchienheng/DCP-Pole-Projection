from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class EvidenceMode(str, Enum):
    SYNTHETIC_FIXTURE = "SYNTHETIC_FIXTURE"
    OBSERVED_PROJECTION = "OBSERVED_PROJECTION"
    RECEIVER_NATIVE = "RECEIVER_NATIVE"


@dataclass(frozen=True)
class OwnerExitEvidence:
    evidence_id: str
    receiver: str
    mode: EvidenceMode
    receiver_actual_read: bool = False
    native_disposition_recorded: bool = False
    rebuild_applied_or_reasoned: bool = False
    behavior_delta_observed: bool = False
    retested: bool = False
    manual_interventions: tuple[str, ...] = ()


@dataclass(frozen=True)
class OwnerExitAssessment:
    decision: Decision
    evidence_mode: EvidenceMode
    autonomy_level: str
    proves_receiver_absorption: bool
    proves_behavior_change: bool
    proves_retest: bool
    reasons: tuple[str, ...] = ()


def assess_owner_exit_evidence(evidence: OwnerExitEvidence) -> OwnerExitAssessment:
    """Classify owner-exit evidence without allowing fixtures to impersonate reality.

    Synthetic fixtures can prove only executable protocol behavior.  Projection-level
    observations can prove bounded transport/observation facts.  Receiver absorption,
    behavior change and retest require RECEIVER_NATIVE evidence.
    """

    if evidence.manual_interventions:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A0_MANUAL_PROMPT_DEPENDENT",
            proves_receiver_absorption=False,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("MANUAL_INTERVENTION_PRESENT",),
        )

    if evidence.mode is EvidenceMode.SYNTHETIC_FIXTURE:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="SIMULATION_ONLY",
            proves_receiver_absorption=False,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("SYNTHETIC_FIXTURE_CANNOT_PROVE_RECEIVER_BEHAVIOR",),
        )

    if evidence.mode is EvidenceMode.OBSERVED_PROJECTION:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A1_ROUTED" if evidence.receiver_actual_read else "A0_NOT_READ",
            proves_receiver_absorption=False,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("PROJECTION_OBSERVATION_IS_NOT_NATIVE_DISPOSITION",),
        )

    # Native evidence path.  Missing stages remain explicit debt; they are never
    # inferred from later filenames, branch activity or producer claims.
    if not evidence.receiver_actual_read:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A1_ROUTED",
            proves_receiver_absorption=False,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("RECEIVER_ACTUAL_READ_MISSING",),
        )
    if not evidence.native_disposition_recorded:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A1_ROUTED",
            proves_receiver_absorption=False,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("RECEIVER_NATIVE_DISPOSITION_MISSING",),
        )
    if not evidence.rebuild_applied_or_reasoned:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A2_ABSORBED",
            proves_receiver_absorption=True,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("REBUILD_RESOLUTION_MISSING",),
        )
    if not evidence.behavior_delta_observed:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A2_ABSORBED",
            proves_receiver_absorption=True,
            proves_behavior_change=False,
            proves_retest=False,
            reasons=("BEHAVIOR_DELTA_NOT_OBSERVED",),
        )
    if not evidence.retested:
        return OwnerExitAssessment(
            decision=Decision.HOLD,
            evidence_mode=evidence.mode,
            autonomy_level="A3_BEHAVIOR_CHANGED",
            proves_receiver_absorption=True,
            proves_behavior_change=True,
            proves_retest=False,
            reasons=("RETEST_MISSING",),
        )

    return OwnerExitAssessment(
        decision=Decision.PASS,
        evidence_mode=evidence.mode,
        autonomy_level="A4_RETESTED",
        proves_receiver_absorption=True,
        proves_behavior_change=True,
        proves_retest=True,
        reasons=("BOUNDED_RECEIVER_NATIVE_LOOP_EVIDENCED",),
    )
