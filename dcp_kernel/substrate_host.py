from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Mapping

from .action_gate import ActionGateInput, EffectClass, RiskLevel, assess_action_gate
from .models import (
    CapabilityBinding,
    Decision,
    Need,
    ReturnState,
    StableLife,
)
from .resolution import resolve_capability_binding
from .return_state import ReturnClosure


@dataclass(frozen=True)
class EffectObservation:
    """Named local effect evidence carried by the host, not a second evidence engine."""

    effect_id: str
    evidence_id: str
    source_id: str
    source_revision: str
    effectivity: str
    observed_effect: str
    new_revision: str
    provenance_verified: bool = True
    revoked: bool = False


@dataclass(frozen=True)
class LocalExecutionRequest:
    need: Need
    stable_life: StableLife
    required_effect: EffectClass
    proposed_effect: EffectClass
    risk_level: RiskLevel
    capability_candidates: tuple[CapabilityBinding, ...]
    responsibility_owner: str
    authority_valid: bool
    expected_source_revision: str


@dataclass(frozen=True)
class LocalExecutionResult:
    decision: Decision
    stable_life: StableLife
    selected_capability: str | None
    selected_carrier: str | None
    effect: EffectObservation | None
    return_closure: ReturnClosure | None
    reasons: tuple[str, ...]


LocalExecutor = Callable[[LocalExecutionRequest, CapabilityBinding], EffectObservation]


def _close_local_return(return_id: str, receiver: str) -> ReturnClosure:
    """Exercise the existing ReturnClosure protocol for a local receiver specimen."""

    closure = ReturnClosure(return_id=return_id, receiver=receiver)
    closure = closure.advance(ReturnState.ROUTED)
    closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
    closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
    closure = closure.advance(
        ReturnState.RECEIVER_NATIVE_DISPOSITION,
        native_disposition="USE_LOCAL_EFFECT",
    )
    closure = closure.advance(ReturnState.RECONCILED)
    closure = closure.advance(
        ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
        rebuild_applied=True,
    )
    closure = closure.advance(
        ReturnState.BEHAVIOR_DELTA_OBSERVED,
        behavior_delta_observed=True,
    )
    return closure.advance(ReturnState.RETESTED, retested=True)


def run_local_cycle(
    request: LocalExecutionRequest,
    executors: Mapping[str, LocalExecutor],
) -> LocalExecutionResult:
    """Run one minimum self-operating cycle without an external carrier lookup.

    This host deliberately composes existing primitives.  It does not discover
    providers, grant authority, create a registry, or claim Runtime.  All
    capability candidates and executors are supplied by the caller.
    """

    if request.expected_source_revision != request.stable_life.current_revision:
        return LocalExecutionResult(
            Decision.HOLD,
            request.stable_life,
            None,
            None,
            None,
            None,
            ("SOURCE_REVISION_IS_NOT_CURRENT",),
        )

    capability = resolve_capability_binding(
        request.need,
        request.capability_candidates,
    )
    if capability.decision is not Decision.PASS or capability.binding is None:
        return LocalExecutionResult(
            capability.decision,
            request.stable_life,
            None,
            None,
            None,
            None,
            capability.reasons or ("NO_ELIGIBLE_CAPABILITY_BINDING",),
        )

    binding = capability.binding
    executor = executors.get(binding.carrier_id)
    if executor is None:
        return LocalExecutionResult(
            Decision.HOLD,
            request.stable_life,
            binding.capability_id,
            binding.carrier_id,
            None,
            None,
            ("SELECTED_CARRIER_HAS_NO_LOCAL_EXECUTOR",),
        )

    gate = assess_action_gate(
        ActionGateInput(
            transition_id=f"{request.need.need_id}:effect",
            required_effect=request.required_effect,
            proposed_effect=request.proposed_effect,
            risk_level=request.risk_level,
            authority_valid=request.authority_valid,
            responsibility_owner=request.responsibility_owner,
            return_target=request.need.receiver,
        )
    )
    if gate.decision is not Decision.PASS:
        return LocalExecutionResult(
            gate.decision,
            request.stable_life,
            binding.capability_id,
            binding.carrier_id,
            None,
            None,
            gate.reasons,
        )

    effect = executor(request, binding)

    evidence_reasons: list[str] = []
    if not effect.evidence_id:
        evidence_reasons.append("EFFECT_EVIDENCE_ID_MISSING")
    if not effect.source_id:
        evidence_reasons.append("EFFECT_SOURCE_ID_MISSING")
    if effect.source_revision != request.expected_source_revision:
        evidence_reasons.append("EFFECT_SOURCE_REVISION_MISMATCH")
    if not effect.effectivity:
        evidence_reasons.append("EFFECT_EFFECTIVITY_MISSING")
    if not effect.provenance_verified:
        evidence_reasons.append("EFFECT_PROVENANCE_NOT_VERIFIED")
    if effect.revoked:
        evidence_reasons.append("EFFECT_EVIDENCE_REVOKED")
    if not effect.observed_effect:
        evidence_reasons.append("OBSERVED_EFFECT_MISSING")
    if not effect.new_revision:
        evidence_reasons.append("SUCCESSOR_REVISION_MISSING")

    if evidence_reasons:
        return LocalExecutionResult(
            Decision.HOLD,
            request.stable_life,
            binding.capability_id,
            binding.carrier_id,
            effect,
            None,
            tuple(evidence_reasons),
        )

    successor = replace(
        request.stable_life,
        current_revision=effect.new_revision,
        last_good_revision=effect.new_revision,
    )
    closure = _close_local_return(
        return_id=f"{effect.effect_id}:return",
        receiver=request.need.receiver,
    )

    return LocalExecutionResult(
        Decision.PASS,
        successor,
        binding.capability_id,
        binding.carrier_id,
        effect,
        closure,
        (
            "LOCAL_SELF_OPERATING_CYCLE_COMPLETE",
            "CARRIER_DID_NOT_GRANT_AUTHORITY",
            "EXTERNAL_LOOKUP_NOT_REQUIRED",
        ),
    )
