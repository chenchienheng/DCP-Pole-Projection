from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json

from .models import CurrentResolutionStatus, Decision
from .reader_policy import ReaderDisposition
from .schedule_effect import ScheduleEffectState
from .successor import CoverageState


class TrianglePole(str, Enum):
    IDEAS_MEANING = "IDEAS_MEANING"
    DCP_AUTHORITY = "DCP_AUTHORITY"
    GLMODEL_EFFECT = "GLMODEL_EFFECT"


class BindingProgressState(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    PERSISTENCE_UNVERIFIED = "PERSISTENCE_UNVERIFIED"
    LOCKED = "LOCKED"
    DUPLICATE_CONVERGED = "DUPLICATE_CONVERGED"


@dataclass(frozen=True)
class BindingContractInput:
    source_identity: str
    source_version: str
    stable_referent: str
    receiver: str
    purpose: str
    effect_id: str
    receiver_affected: bool
    material_delta: bool
    ideas_meaning_preserved: bool
    dcp_action_authority_valid: bool
    glmodel_effect_observed: bool
    current_status: CurrentResolutionStatus
    carrier_decision: Decision
    successor_state: CoverageState
    reader_disposition: ReaderDisposition
    schedule_state: ScheduleEffectState
    metabolism_disposition: str
    durable_persisted: bool
    durable_readback: bool
    duplicate_receipt: bool = False
    prior_locked_binding_key: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "source_identity",
            "source_version",
            "stable_referent",
            "receiver",
            "purpose",
            "effect_id",
            "metabolism_disposition",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise TypeError(f"{field_name} must be a non-empty string")
        for field_name in (
            "receiver_affected",
            "material_delta",
            "ideas_meaning_preserved",
            "dcp_action_authority_valid",
            "glmodel_effect_observed",
            "durable_persisted",
            "durable_readback",
            "duplicate_receipt",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} must be bool")

    @property
    def binding_key(self) -> str:
        canonical = json.dumps(
            [
                self.source_identity,
                self.source_version,
                self.stable_referent,
                self.receiver,
                self.purpose,
                self.effect_id,
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"sha256:{sha256(canonical).hexdigest()}"


@dataclass(frozen=True)
class BindingContractAssessment:
    decision: Decision
    state: BindingProgressState
    binding_key: str
    locked: bool
    write_required: bool
    first_unresolved_pole: TrianglePole | None
    reasons: tuple[str, ...]


_READY_SUCCESSOR_STATES = {
    CoverageState.COVERED,
    CoverageState.COVERED_EVIDENCE_ONLY,
}
_READY_READER_DISPOSITIONS = {
    ReaderDisposition.READ_CURRENT,
    ReaderDisposition.READ_AFFECTED_SLICE,
}
_READY_METABOLISM_DISPOSITIONS = {
    "KEEP_MACHINE_CONTRACT",
    "KEEP_EXECUTABLE_CANDIDATE",
}
_FAIL_SCHEDULE_STATES = {
    ScheduleEffectState.FAIL_SCOPE_VIOLATION,
    ScheduleEffectState.FAIL_IDENTITY_DRIFT,
}


def assess_binding_contract(item: BindingContractInput) -> BindingContractAssessment:
    """Converge existing resolver outputs into one durable, bounded progress lock.

    Triangle precedence is explicit: preserved meaning precedes action authority,
    and authority precedes observed world effect. Later-pole evidence never repairs
    an earlier-pole failure. A lock additionally requires the existing Current,
    carrier, successor, reader, schedule-effect, and metabolism assessments plus
    durable persistence and readback.
    """

    key = item.binding_key

    if item.duplicate_receipt:
        if item.prior_locked_binding_key == key:
            return BindingContractAssessment(
                decision=Decision.PASS,
                state=BindingProgressState.DUPLICATE_CONVERGED,
                binding_key=key,
                locked=True,
                write_required=False,
                first_unresolved_pole=None,
                reasons=("EXACT_SOURCE_VERSION_RECEIVER_PURPOSE_EFFECT_ALREADY_LOCKED",),
            )
        return BindingContractAssessment(
            decision=Decision.FAIL,
            state=BindingProgressState.FAILED,
            binding_key=key,
            locked=False,
            write_required=False,
            first_unresolved_pole=None,
            reasons=("DUPLICATE_CLAIM_DOES_NOT_MATCH_PRIOR_LOCKED_BINDING_KEY",),
        )

    if not item.receiver_affected or not item.material_delta:
        return BindingContractAssessment(
            decision=Decision.PASS,
            state=BindingProgressState.NOT_APPLICABLE,
            binding_key=key,
            locked=False,
            write_required=False,
            first_unresolved_pole=None,
            reasons=("NO_MATERIAL_AFFECTED_RECEIVER_EDGE",),
        )

    if not item.ideas_meaning_preserved:
        return BindingContractAssessment(
            decision=Decision.FAIL,
            state=BindingProgressState.FAILED,
            binding_key=key,
            locked=False,
            write_required=False,
            first_unresolved_pole=TrianglePole.IDEAS_MEANING,
            reasons=("IDEAS_MEANING_PRECEDENCE_FAILED",),
        )

    if not item.dcp_action_authority_valid:
        return BindingContractAssessment(
            decision=Decision.HOLD,
            state=BindingProgressState.PARTIAL,
            binding_key=key,
            locked=False,
            write_required=True,
            first_unresolved_pole=TrianglePole.DCP_AUTHORITY,
            reasons=("DCP_ACTION_AUTHORITY_UNRESOLVED",),
        )

    if not item.glmodel_effect_observed:
        return BindingContractAssessment(
            decision=Decision.HOLD,
            state=BindingProgressState.PARTIAL,
            binding_key=key,
            locked=False,
            write_required=True,
            first_unresolved_pole=TrianglePole.GLMODEL_EFFECT,
            reasons=("GLMODEL_WORLD_EFFECT_UNOBSERVED",),
        )

    if item.schedule_state in _FAIL_SCHEDULE_STATES:
        return BindingContractAssessment(
            decision=Decision.FAIL,
            state=BindingProgressState.FAILED,
            binding_key=key,
            locked=False,
            write_required=False,
            first_unresolved_pole=None,
            reasons=(f"SCHEDULE_EFFECT_{item.schedule_state.value}",),
        )

    missing: list[str] = []
    if item.current_status is not CurrentResolutionStatus.CURRENT:
        missing.append(f"CURRENT_{item.current_status.value}")
    if item.carrier_decision is not Decision.PASS:
        missing.append(f"CARRIER_{item.carrier_decision.value}")
    if item.successor_state not in _READY_SUCCESSOR_STATES:
        missing.append(f"SUCCESSOR_{item.successor_state.value}")
    if item.reader_disposition not in _READY_READER_DISPOSITIONS:
        missing.append(f"READER_{item.reader_disposition.value}")
    if item.schedule_state is not ScheduleEffectState.EFFECTIVE:
        missing.append(f"SCHEDULE_EFFECT_{item.schedule_state.value}")
    if item.metabolism_disposition not in _READY_METABOLISM_DISPOSITIONS:
        missing.append(f"METABOLISM_{item.metabolism_disposition}")

    if missing:
        return BindingContractAssessment(
            decision=Decision.HOLD,
            state=BindingProgressState.PARTIAL,
            binding_key=key,
            locked=False,
            write_required=True,
            first_unresolved_pole=None,
            reasons=tuple(missing),
        )

    if not item.durable_persisted or not item.durable_readback:
        reasons: list[str] = []
        if not item.durable_persisted:
            reasons.append("DURABLE_PERSISTENCE_UNVERIFIED")
        if not item.durable_readback:
            reasons.append("DURABLE_READBACK_UNVERIFIED")
        return BindingContractAssessment(
            decision=Decision.HOLD,
            state=BindingProgressState.PERSISTENCE_UNVERIFIED,
            binding_key=key,
            locked=False,
            write_required=True,
            first_unresolved_pole=None,
            reasons=tuple(reasons),
        )

    return BindingContractAssessment(
        decision=Decision.PASS,
        state=BindingProgressState.LOCKED,
        binding_key=key,
        locked=True,
        write_required=False,
        first_unresolved_pole=None,
        reasons=("BOUNDED_EFFECT_AND_DURABLE_READBACK_LOCKED",),
    )
