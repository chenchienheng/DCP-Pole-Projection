from __future__ import annotations

import hashlib
import json

from dataclasses import asdict, dataclass, replace
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
    provenance_verified: bool = False
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
    expected_source_id: str | None = None


@dataclass(frozen=True)
class LocalExecutionResult:
    decision: Decision
    stable_life: StableLife
    selected_capability: str | None
    selected_carrier: str | None
    effect: EffectObservation | None
    return_closure: ReturnClosure | None
    reasons: tuple[str, ...]
    execution_request: LocalExecutionRequest | None = None


LocalExecutor = Callable[[LocalExecutionRequest, CapabilityBinding], EffectObservation]


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _request_reasons(request: LocalExecutionRequest) -> tuple[str, ...]:
    """Validate this local execution profile, not real provider permission."""
    reasons = []
    if not all(_text(value) for value in (
        request.need.need_id, request.need.required_capability, request.need.receiver,
        request.stable_life.life_id, request.stable_life.native_owner,
        request.stable_life.current_revision, request.stable_life.last_good_revision,
        request.responsibility_owner,
    )):
        reasons.append("LOCAL_REQUEST_IDENTITY_INCOMPLETE")
    if not _text(request.expected_source_id):
        reasons.append("EXPECTED_EFFECT_SOURCE_ID_MISSING")
    if not _text(request.expected_source_revision):
        reasons.append("EXPECTED_EFFECT_SOURCE_REVISION_MISSING")
    if type(request.authority_valid) is not bool:
        reasons.append("ACTION_AUTHORITY_NOT_BOOLEAN")
    if not isinstance(request.required_effect, EffectClass) or not isinstance(
        request.proposed_effect, EffectClass
    ) or not isinstance(request.risk_level, RiskLevel):
        reasons.append("ACTION_PROFILE_INVALID")
    for binding in request.capability_candidates:
        if any(type(getattr(binding, field)) is not bool for field in (
            "authority_granted", "rights_allowed", "evidence_available",
            "native_internalized",
        )):
            reasons.append("CAPABILITY_DECLARATION_NOT_BOOLEAN")
            break
    return tuple(reasons)


def _effect_reasons(
    request: LocalExecutionRequest, effect: EffectObservation,
) -> tuple[str, ...]:
    reasons = []
    for field, code in (
        ("effect_id", "EFFECT_ID_MISSING"),
        ("evidence_id", "EFFECT_EVIDENCE_ID_MISSING"),
        ("source_id", "EFFECT_SOURCE_ID_MISSING"),
        ("effectivity", "EFFECT_EFFECTIVITY_MISSING"),
        ("observed_effect", "OBSERVED_EFFECT_MISSING"),
        ("new_revision", "SUCCESSOR_REVISION_MISSING"),
    ):
        if not _text(getattr(effect, field)):
            reasons.append(code)
    if effect.source_id != request.expected_source_id:
        reasons.append("EFFECT_SOURCE_ID_MISMATCH")
    if effect.source_revision != request.expected_source_revision:
        reasons.append("EFFECT_SOURCE_REVISION_MISMATCH")
    if effect.provenance_verified is not True:
        reasons.append("EFFECT_PROVENANCE_NOT_VERIFIED")
    if effect.revoked is not False:
        reasons.append("EFFECT_EVIDENCE_REVOKED_OR_UNRESOLVED")
    return tuple(reasons)


def _return_id(
    request: LocalExecutionRequest, binding: CapabilityBinding, effect: EffectObservation,
) -> str:
    # Scope binding only, not a signature, external proof, registry or global ID.
    fields = {"request": asdict(request), "binding": asdict(binding), "effect": asdict(effect)}
    digest = hashlib.sha256(json.dumps(fields, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()
    return f"{effect.effect_id}:return:{digest}"


def _receipt_reasons(
    pending: LocalExecutionResult, receipt: ReturnClosure,
) -> tuple[str, ...]:
    """Check a supplied local receipt; no receiver events are manufactured.

    Field consistency cannot authenticate who supplied the evidence. The caller
    must obtain it from the actual authorized receiver and retain that evidence.
    """
    produced = pending.return_closure
    if produced is None:
        return ("NO_PRODUCED_RETURN_TO_RECONCILE",)
    if not isinstance(receipt, ReturnClosure):
        return ("RECEIVER_RETURN_TYPE_INVALID",)
    if receipt.return_id != produced.return_id or receipt.receiver != produced.receiver:
        return ("RECEIVER_RETURN_BINDING_MISMATCH",)
    if not isinstance(receipt.state, ReturnState):
        return ("RECEIVER_RETURN_STATE_INVALID",)
    if any(type(getattr(receipt, field)) is not bool for field in (
        "receiver_actual_read", "rebuild_applied", "behavior_delta_observed", "retested",
    )):
        return ("RECEIVER_RETURN_EVIDENCE_NOT_BOOLEAN",)
    if (not isinstance(receipt.manual_interventions, tuple)
            or not all(_text(item) for item in receipt.manual_interventions)):
        return ("RECEIVER_INTERVENTION_RECORD_INVALID",)
    order = tuple(ReturnState)
    if order.index(receipt.state) < order.index(produced.state):
        return ("RECEIVER_RETURN_STATE_REGRESSION",)
    required = (
        (ReturnState.ACTUAL_READ, receipt.receiver_actual_read, "READ_EVIDENCE_MISSING"),
        (ReturnState.RECEIVER_NATIVE_DISPOSITION,
         _text(receipt.native_disposition), "NATIVE_DISPOSITION_MISSING"),
        (ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
         receipt.rebuild_applied or _text(receipt.no_rebuild_reason), "REBUILD_EVIDENCE_MISSING"),
        (ReturnState.BEHAVIOR_DELTA_OBSERVED,
         receipt.behavior_delta_observed, "BEHAVIOR_EVIDENCE_MISSING"),
        (ReturnState.RETESTED, receipt.retested, "RETEST_EVIDENCE_MISSING"),
    )
    return tuple(code for state, present, code in required
                 if order.index(receipt.state) >= order.index(state) and not present)


def reconcile_local_result(
    request: LocalExecutionRequest,
    pending: LocalExecutionResult,
    receiver_return: ReturnClosure,
) -> LocalExecutionResult:
    """Adopt an already-produced local effect using a receiver-supplied return.

    This function has no executor or I/O: resuming a missing return cannot repeat
    the original action. ``request`` must be freshly applicable and identical to
    the saved execution binding. A HOLD does not undo an already-produced effect.
    Receipts are caller-supplied evidence, not cryptographic or provider proof.
    """
    if pending.execution_request != request:
        return replace(pending, decision=Decision.HOLD,
                       reasons=("EXECUTION_REQUEST_BINDING_MISMATCH",))
    if pending.effect is None:
        return replace(pending, decision=Decision.HOLD,
                       reasons=("NO_QUALIFIED_EFFECT_TO_RECONCILE",))
    reasons = _request_reasons(request) + _effect_reasons(request, pending.effect)
    selected = resolve_capability_binding(request.need, request.capability_candidates)
    if (selected.binding is None
            or selected.binding.capability_id != pending.selected_capability
            or selected.binding.carrier_id != pending.selected_carrier):
        reasons += ("SAVED_CAPABILITY_BINDING_MISMATCH",)
    elif (pending.return_closure is None
          or pending.return_closure.return_id != _return_id(request, selected.binding, pending.effect)):
        reasons += ("SAVED_EFFECT_RETURN_BINDING_MISMATCH",)
    reasons += _receipt_reasons(pending, receiver_return)
    if reasons:
        return replace(pending, decision=Decision.HOLD, reasons=reasons)
    if pending.decision is Decision.PASS:
        if receiver_return == pending.return_closure:
            return pending
        return replace(pending, decision=Decision.HOLD,
                       reasons=("ALREADY_ADOPTED_RETURN_CONFLICT",))
    if pending.stable_life != request.stable_life:
        return replace(pending, decision=Decision.HOLD,
                       reasons=("PENDING_LIFE_STATE_MISMATCH",))
    if receiver_return.outstanding_debt:
        return replace(pending, decision=Decision.HOLD, return_closure=receiver_return,
                       reasons=("RECEIVER_RETURN_PENDING",) + receiver_return.outstanding_debt)
    if receiver_return.native_disposition != "USE_LOCAL_EFFECT":
        return replace(pending, decision=Decision.HOLD, return_closure=receiver_return,
                       reasons=("RECEIVER_DID_NOT_ACCEPT_LOCAL_EFFECT",))
    successor = replace(request.stable_life,
                        current_revision=pending.effect.new_revision,
                        last_good_revision=pending.effect.new_revision)
    return replace(pending, decision=Decision.PASS, stable_life=successor,
                   return_closure=receiver_return,
                   reasons=("LOCAL_EFFECT_AND_RECEIVER_RETURN_RECONCILED",
                            "RECEIVER_EVIDENCE_SUPPLIED_NOT_AUTHENTICATED",
                            "NO_EXECUTOR_REPLAY"))


def run_local_cycle(
    request: LocalExecutionRequest,
    executors: Mapping[str, LocalExecutor],
) -> LocalExecutionResult:
    """Run one minimum self-operating cycle without an external carrier lookup.

    This host deliberately composes existing primitives.  It does not discover
    providers, grant authority, create a registry, or claim Runtime. All
    capability candidates and executors are supplied by the caller. A qualified
    effect stops at PRODUCED; use reconcile_local_result with receiver evidence.
    Current/last-good remain unadopted while the effect itself remains visible.
    """

    reasons = _request_reasons(request)
    if reasons:
        return LocalExecutionResult(Decision.HOLD, request.stable_life,
                                    None, None, None, None, reasons)
    if request.proposed_effect is EffectClass.NO_ACTION:
        return LocalExecutionResult(Decision.PASS, request.stable_life,
                                    None, None, None, None, ("NO_ACTION_SELECTED",))

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

    try:
        effect = executor(request, binding)
    except Exception as exc:
        # The action may already have happened. Do not retry or claim rollback.
        return LocalExecutionResult(
            Decision.HOLD, request.stable_life, binding.capability_id,
            binding.carrier_id, None, None,
            ("LOCAL_EXECUTOR_ERROR_EFFECT_UNKNOWN", type(exc).__name__,
             "INSPECT_EFFECT_BEFORE_RETRY"), request,
        )
    if not isinstance(effect, EffectObservation):
        return LocalExecutionResult(
            Decision.HOLD, request.stable_life, binding.capability_id,
            binding.carrier_id, None, None,
            ("EXECUTOR_RETURN_TYPE_INVALID_EFFECT_UNKNOWN", "INSPECT_EFFECT_BEFORE_RETRY"),
            request,
        )
    reasons = _effect_reasons(request, effect)
    if reasons:
        return LocalExecutionResult(
            Decision.HOLD, request.stable_life, binding.capability_id,
            binding.carrier_id, effect, None, reasons, request,
        )
    # Producing an effect establishes none of the receiver-owned transitions.
    closure = ReturnClosure(return_id=_return_id(request, binding, effect),
                            receiver=request.need.receiver)
    return LocalExecutionResult(
        Decision.HOLD, request.stable_life, binding.capability_id,
        binding.carrier_id, effect, closure,
        ("EFFECT_PRODUCED_RECEIVER_RETURN_PENDING", "DO_NOT_REEXECUTE_FOR_RETURN"),
        request,
    )
