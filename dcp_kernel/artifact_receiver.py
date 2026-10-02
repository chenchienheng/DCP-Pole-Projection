"""A real, read-only receiver for byte-delivery verification.

This is a narrow local consumer, not a general Native acceptance policy. The
expected manifest must come from the caller's trusted source/transport context.
No supplied `read`, `verified`, or `retested` flag replaces filesystem reads.
The result accepts a verification result, not the document's semantic claims.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any

from .action_gate import EffectClass, RiskLevel
from .models import CapabilityBinding, Decision, InvariantCore, Need, ReturnState, StableLife
from .return_state import ReturnClosure
from .substrate_host import (
    EffectObservation, LocalExecutionRequest, LocalExecutionResult,
    reconcile_local_result, run_local_cycle,
)

_CAPABILITY = "verify-delivered-artifact-bytes"
_PROFILE = "LOCAL_BYTE_DELIVERY_VERIFICATION_V1"


@dataclass(frozen=True)
class ArtifactExpectation:
    path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class ArtifactDeliveryContract:
    delivery_id: str
    source_id: str
    source_revision: str
    receiver: str
    artifacts: tuple[ArtifactExpectation, ...]
    manual_interventions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArtifactDeliveryCheck:
    result: LocalExecutionResult
    observations: tuple[dict[str, Any], ...]
    scope: str = "BYTE_DELIVERY_ONLY_NOT_SEMANTIC_OR_NATIVE_ACCEPTANCE"


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate(contract: ArtifactDeliveryContract) -> None:
    if not isinstance(contract, ArtifactDeliveryContract):
        raise ValueError("DELIVERY_CONTRACT_REQUIRED")
    if not all(_nonempty(getattr(contract, f)) for f in ("delivery_id", "source_id", "source_revision", "receiver")):
        raise ValueError("DELIVERY_IDENTITY_MISSING")
    if not isinstance(contract.artifacts, tuple) or not contract.artifacts:
        raise ValueError("EXPLICIT_ARTIFACTS_REQUIRED")
    if not isinstance(contract.manual_interventions, tuple) or not all(_nonempty(x) for x in contract.manual_interventions):
        raise ValueError("INVALID_MANUAL_INTERVENTIONS")
    names: set[str] = set()
    for item in contract.artifacts:
        if not isinstance(item, ArtifactExpectation):
            raise ValueError("INVALID_ARTIFACT_EXPECTATION")
        p = PurePosixPath(item.path) if isinstance(item.path, str) else None
        if (not _nonempty(item.path) or p is None or p.is_absolute()
                or str(p) != item.path or ".." in p.parts or "\\" in item.path
                or "\x00" in item.path or not p.parts):
            raise ValueError("NONCANONICAL_ARTIFACT_PATH")
        if item.path in names:
            raise ValueError("DUPLICATE_ARTIFACT_PATH")
        names.add(item.path)
        if (not isinstance(item.sha256, str) or len(item.sha256) != 64
                or any(c not in "0123456789abcdef" for c in item.sha256)):
            raise ValueError("INVALID_EXPECTED_SHA256")
        if type(item.size_bytes) is not int or item.size_bytes < 0:
            raise ValueError("INVALID_EXPECTED_SIZE")


def _fingerprint(contract: ArtifactDeliveryContract) -> str:
    _validate(contract)
    return hashlib.sha256(_canonical(asdict(contract)).encode("utf-8")).hexdigest()


def _request(contract: ArtifactDeliveryContract) -> LocalExecutionRequest:
    # The life is the verification result; it is NOT the original artifact or
    # the user's global Current. The original source revision remains explicit.
    life = StableLife(f"{_PROFILE}:{contract.delivery_id}",
                      InvariantCore(contract.delivery_id, "byte-delivery verification"),
                      contract.receiver, contract.source_revision, contract.source_revision)
    binding = CapabilityBinding(_CAPABILITY, contract.receiver, "LOCAL_FILE_READBACK",
                                True, True, True, contract.receiver)
    return LocalExecutionRequest(
        Need(contract.delivery_id, _CAPABILITY, contract.receiver), life,
        EffectClass.OBSERVE, EffectClass.OBSERVE, RiskLevel.LOW, (binding,),
        contract.receiver, False, contract.source_revision, contract.source_id,
    )


def _read_hash(root: Path, item: ArtifactExpectation) -> dict[str, Any]:
    """Read a regular file using directory descriptors and no-follow opens.

    Unsupported platforms fail closed. The selected root's ancestors are a
    caller-controlled boundary. This does not create a hostile-user sandbox or
    an atomic multi-file snapshot. Concurrent changes observed on the open file
    descriptor fail validation rather than being declared absent.
    """
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise ValueError("NOFOLLOW_READ_UNSUPPORTED")
    dirs: list[int] = []
    fd: int | None = None
    try:
        dirs.append(os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        parts = PurePosixPath(item.path).parts
        for part in parts[:-1]:
            dirs.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirs[-1]))
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dirs[-1])
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("ARTIFACT_NOT_REGULAR_FILE")
        if before.st_size != item.size_bytes:
            raise ValueError("ARTIFACT_SIZE_MISMATCH")
        digest = hashlib.sha256()
        count = 0
        while True:
            block = os.read(fd, min(1024 * 1024, item.size_bytes + 1 - count))
            if not block:
                break
            count += len(block)
            if count > item.size_bytes:
                raise ValueError("ARTIFACT_CHANGED_DURING_READ")
            digest.update(block)
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after) or count != item.size_bytes:
            raise ValueError("ARTIFACT_CHANGED_DURING_READ")
        actual = digest.hexdigest()
        if actual != item.sha256:
            raise ValueError("ARTIFACT_HASH_MISMATCH")
        return {"path": item.path, "size_bytes": count, "sha256": actual}
    finally:
        if fd is not None:
            os.close(fd)
        for directory_fd in reversed(dirs):
            os.close(directory_fd)


def _observe(contract: ArtifactDeliveryContract, root: Path) -> tuple[dict[str, Any], ...]:
    _validate(contract)
    return tuple(_read_hash(root, item) for item in contract.artifacts)


def prepare_artifact_delivery(contract: ArtifactDeliveryContract, source_root: Path | str) -> LocalExecutionResult:
    """Read the expected source bytes and produce a pending verification result.

    Does not upload, deliver, authenticate a provider, or accept a receiver's
    result. I/O is read-only; the separate receiver will reopen received files.
    """
    digest = _fingerprint(contract)
    request = _request(contract)
    def observe(req: LocalExecutionRequest, binding: CapabilityBinding) -> EffectObservation:
        _observe(contract, Path(source_root))
        return EffectObservation(
            f"{contract.delivery_id}:verify:{digest}", f"sha256:{digest}",
            req.expected_source_id, req.expected_source_revision, _PROFILE,
            "EXPECTED_ARTIFACT_BYTES_READ", f"VERIFIED_BYTES:{digest}",
            provenance_verified=True,  # actual reads above; not provider authentication
        )
    return run_local_cycle(request, {"LOCAL_FILE_READBACK": observe})


def receive_artifact_delivery(
    contract: ArtifactDeliveryContract,
    pending: LocalExecutionResult,
    received_root: Path | str,
) -> ArtifactDeliveryCheck:
    """Accept only this byte-verification task after two actual readback passes.

    There is no caller-supplied receipt input or executor. Missing, swapped or
    modified files cannot be fixed by supplying `verified=True`. Expected
    identity/revision and hash authenticity still belong to the trusted intake.
    """
    digest = _fingerprint(contract)
    request = _request(contract)
    if (not isinstance(pending, LocalExecutionResult)
            or pending.execution_request != request or pending.effect is None
            or pending.effect.effectivity != _PROFILE
            or pending.effect.evidence_id != f"sha256:{digest}"
            or pending.effect.new_revision != f"VERIFIED_BYTES:{digest}"
            or pending.effect.observed_effect != "EXPECTED_ARTIFACT_BYTES_READ"
            or pending.return_closure is None):
        if not isinstance(pending, LocalExecutionResult):
            raise ValueError("INVALID_PENDING_RESULT")
        return ArtifactDeliveryCheck(replace(pending, decision=Decision.HOLD,
                                            reasons=("ARTIFACT_DELIVERY_BINDING_MISMATCH",)), ())
    try:
        first = _observe(contract, Path(received_root))
        second = _observe(contract, Path(received_root))
        if first != second:
            raise ValueError("ARTIFACT_READBACK_DRIFT")
    except (OSError, ValueError) as exc:
        # Do not persist OS error strings that could reveal a local path.
        reason = str(exc) if isinstance(exc, ValueError) else f"ARTIFACT_READ_FAILED_ERRNO_{exc.errno}"
        return ArtifactDeliveryCheck(replace(pending, decision=Decision.HOLD, reasons=(reason,)), ())
    receipt = ReturnClosure(pending.return_closure.return_id, contract.receiver,
                            manual_interventions=contract.manual_interventions)
    receipt = receipt.advance(ReturnState.ROUTED)
    receipt = receipt.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
    receipt = receipt.advance(ReturnState.MATERIALITY_RESOLVED)
    receipt = receipt.advance(ReturnState.RECEIVER_NATIVE_DISPOSITION, native_disposition="USE_LOCAL_EFFECT")
    receipt = receipt.advance(ReturnState.RECONCILED)
    receipt = receipt.advance(ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
                              no_rebuild_reason="Read-only byte-verification; original artifact is not rebuilt.")
    receipt = receipt.advance(ReturnState.BEHAVIOR_DELTA_OBSERVED, behavior_delta_observed=True)
    receipt = receipt.advance(ReturnState.RETESTED, retested=True)
    result = reconcile_local_result(request, pending, receipt)
    return ArtifactDeliveryCheck(result, first)


def contract_from_dict(data: dict[str, Any]) -> ArtifactDeliveryContract:
    d = dict(data)
    if not isinstance(d.get("artifacts"), list) or not isinstance(d.get("manual_interventions", []), list):
        raise ValueError("CONTRACT_LIST_FIELDS_REQUIRED")
    d["artifacts"] = tuple(ArtifactExpectation(**x) for x in d["artifacts"])
    d["manual_interventions"] = tuple(d.get("manual_interventions", []))
    result = ArtifactDeliveryContract(**d)
    _validate(result)
    return result


def pending_to_dict(pending: LocalExecutionResult) -> dict[str, Any]:
    """Portable JSON data only; no pickle or dynamically selected classes."""
    return asdict(pending)


def pending_from_dict(data: dict[str, Any]) -> LocalExecutionResult:
    def life(d: dict[str, Any]) -> StableLife:
        d = dict(d); d["invariant_core"] = InvariantCore(**d["invariant_core"])
        return StableLife(**d)
    d = dict(data)
    req = dict(d["execution_request"])
    if any(type(req.get(k)) is not int for k in ("required_effect", "proposed_effect")):
        raise ValueError("INVALID_EFFECT_ENUM_REPRESENTATION")
    if not isinstance(req.get("capability_candidates"), list):
        raise ValueError("CAPABILITY_LIST_REQUIRED")
    req["need"] = Need(**req["need"])
    req["stable_life"] = life(req["stable_life"])
    bindings = []
    for b in req["capability_candidates"]:
        b = dict(b)
        if not isinstance(b.get("actor_labels"), list):
            raise ValueError("ACTOR_LABEL_LIST_REQUIRED")
        b["actor_labels"] = tuple(b["actor_labels"])
        bindings.append(CapabilityBinding(**b))
    req["capability_candidates"] = tuple(bindings)
    req["required_effect"] = EffectClass(req["required_effect"])
    req["proposed_effect"] = EffectClass(req["proposed_effect"])
    req["risk_level"] = RiskLevel(req["risk_level"])
    d["execution_request"] = LocalExecutionRequest(**req)
    d["stable_life"] = life(d["stable_life"])
    d["decision"] = Decision(d["decision"])
    d["effect"] = EffectObservation(**d["effect"]) if d["effect"] is not None else None
    if d["return_closure"] is not None:
        receipt = dict(d["return_closure"])
        if not isinstance(receipt.get("manual_interventions"), list):
            raise ValueError("MANUAL_INTERVENTION_LIST_REQUIRED")
        receipt["state"] = ReturnState(receipt["state"])
        receipt["manual_interventions"] = tuple(receipt["manual_interventions"])
        d["return_closure"] = ReturnClosure(**receipt)
    if not isinstance(d.get("reasons"), list):
        raise ValueError("REASON_LIST_REQUIRED")
    d["reasons"] = tuple(d["reasons"])
    return LocalExecutionResult(**d)
