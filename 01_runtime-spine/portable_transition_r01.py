"""Portable carrier transition resolver R0.1.

A stable responsibility may move between carriers without becoming a new life.
Relocation is a pointer update only when the bindings that determine meaning,
authority, state, return/re-entry and execution/resource semantics remain stable.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PortableTransitionDisposition(str, Enum):
    POINTER_UPDATE_ONLY = "POINTER_UPDATE_ONLY"
    RECOMPOSE_REQUIRED = "RECOMPOSE_REQUIRED"
    HOLD_UNRESOLVED = "HOLD_UNRESOLVED"
    FAIL_IDENTITY_DRIFT = "FAIL_IDENTITY_DRIFT"


@dataclass(frozen=True)
class PortableTransitionInput:
    stable_id_before: str
    stable_id_after: str
    carrier_before: str
    carrier_after: str
    authority_preserved: bool
    state_preserved: bool
    evidence_lineage_preserved: bool
    return_target_preserved: bool
    reentry_binding_preserved: bool
    capability_semantics_preserved: bool | None
    resource_semantics_preserved: bool | None


@dataclass(frozen=True)
class PortableTransitionAssessment:
    disposition: PortableTransitionDisposition
    reasons: tuple[str, ...]
    rebuild_required: bool
    identity_preserved: bool


def assess_portable_transition(x: PortableTransitionInput) -> PortableTransitionAssessment:
    if x.stable_id_before != x.stable_id_after:
        return PortableTransitionAssessment(
            PortableTransitionDisposition.FAIL_IDENTITY_DRIFT,
            ("STABLE_IDENTITY_CHANGED_BY_CARRIER_TRANSITION",),
            rebuild_required=True,
            identity_preserved=False,
        )

    hard_breaks = []
    if not x.authority_preserved:
        hard_breaks.append("AUTHORITY_BINDING_CHANGED")
    if not x.state_preserved:
        hard_breaks.append("STATE_BINDING_CHANGED")
    if not x.evidence_lineage_preserved:
        hard_breaks.append("EVIDENCE_LINEAGE_CHANGED")
    if not x.return_target_preserved:
        hard_breaks.append("RETURN_TARGET_CHANGED")
    if not x.reentry_binding_preserved:
        hard_breaks.append("REENTRY_BINDING_CHANGED")
    if hard_breaks:
        return PortableTransitionAssessment(
            PortableTransitionDisposition.RECOMPOSE_REQUIRED,
            tuple(hard_breaks),
            rebuild_required=True,
            identity_preserved=True,
        )

    if x.capability_semantics_preserved is None or x.resource_semantics_preserved is None:
        return PortableTransitionAssessment(
            PortableTransitionDisposition.HOLD_UNRESOLVED,
            ("CAPABILITY_OR_RESOURCE_SEMANTICS_UNRESOLVED",),
            rebuild_required=False,
            identity_preserved=True,
        )

    if not x.capability_semantics_preserved or not x.resource_semantics_preserved:
        reasons = []
        if not x.capability_semantics_preserved:
            reasons.append("CAPABILITY_SEMANTICS_CHANGED")
        if not x.resource_semantics_preserved:
            reasons.append("RESOURCE_SEMANTICS_CHANGED")
        return PortableTransitionAssessment(
            PortableTransitionDisposition.RECOMPOSE_REQUIRED,
            tuple(reasons),
            rebuild_required=True,
            identity_preserved=True,
        )

    return PortableTransitionAssessment(
        PortableTransitionDisposition.POINTER_UPDATE_ONLY,
        ("CARRIER_CHANGED_WITH_STABLE_BINDINGS",),
        rebuild_required=False,
        identity_preserved=True,
    )
