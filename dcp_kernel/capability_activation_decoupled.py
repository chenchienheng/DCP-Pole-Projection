from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Mapping

from .models import Decision


class ProviderKind(str, Enum):
    HUMAN = "HUMAN"
    SKILL = "SKILL"
    AI_MODEL = "AI_MODEL"
    AGENT = "AGENT"
    SOFTWARE = "SOFTWARE"
    EQUIPMENT = "EQUIPMENT"
    SUPPLIER = "SUPPLIER"
    CLOUD = "CLOUD"
    LOCAL_COMPUTE = "LOCAL_COMPUTE"
    API = "API"


@dataclass(frozen=True)
class CapabilityLineage:
    lineage_id: str
    invariant_meaning: str


@dataclass(frozen=True)
class CapabilityStewardship:
    lineage_id: str
    native_home: str
    relation: str = "STEWARDED_BY"
    provenance_ref: str | None = None


@dataclass(frozen=True)
class CapabilityActivationNeed:
    need_id: str
    stable_life_id: str
    required_lineage_ids: tuple[str, ...]
    return_target: str
    privacy_required: bool = False
    minimum_reliability: float = 0.0
    max_total_cost: float | None = None


@dataclass(frozen=True)
class CapabilityProvider:
    provider_id: str
    provider_kind: ProviderKind
    provider_label: str
    capability_lineage_ids: tuple[str, ...]
    rights_allowed: bool
    available: bool
    current_effect_eligible: bool
    evidence_available: bool
    return_supported: bool
    privacy_allowed: bool
    reliability: float
    estimated_cost: float = 0.0
    return_targets: tuple[str, ...] = ()
    replacement_path_known: bool = True
    exit_condition_known: bool = True


@dataclass(frozen=True)
class ProviderBinding:
    provider_id: str
    provider_kind: ProviderKind
    provider_label: str
    activated_lineage_ids: tuple[str, ...]
    estimated_cost: float
    reliability: float


@dataclass(frozen=True)
class CapabilityActivationAssessment:
    decision: Decision
    need_id: str
    stable_life_id: str
    return_target: str
    bindings: tuple[ProviderBinding, ...]
    activated_lineage_ids: tuple[str, ...]
    unresolved_lineage_ids: tuple[str, ...]
    over_activation: bool
    excluded: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActionAuthorityLease:
    lease_id: str
    event_id: str
    stable_life_id: str
    action_scope: str
    authorized_provider_ids: tuple[str, ...]
    return_target: str
    evidence_ref: str
    active: bool = True


@dataclass(frozen=True)
class ActionAuthorityAssessment:
    decision: Decision
    lease_id: str | None
    action_scope: str
    authorized_provider_ids: tuple[str, ...]
    reasons: tuple[str, ...]


def _unique_in_order(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def validate_lineage_and_stewardship(
    lineages: tuple[CapabilityLineage, ...],
    stewardships: tuple[CapabilityStewardship, ...],
) -> tuple[Decision, tuple[str, ...]]:
    meanings: dict[str, str] = {}
    conflicts: set[str] = set()
    for lineage in lineages:
        previous = meanings.get(lineage.lineage_id)
        if previous is not None and previous != lineage.invariant_meaning:
            conflicts.add(lineage.lineage_id)
        else:
            meanings[lineage.lineage_id] = lineage.invariant_meaning

    unknown_stewardship = sorted(
        {item.lineage_id for item in stewardships if item.lineage_id not in meanings}
    )
    if conflicts:
        return Decision.HOLD, tuple(
            ["CAPABILITY_LINEAGE_MEANING_CONFLICT"]
            + [f"CONFLICT:{item}" for item in sorted(conflicts)]
        )
    if unknown_stewardship:
        return Decision.HOLD, tuple(
            ["STEWARDSHIP_REFERENCES_UNKNOWN_LINEAGE"]
            + [f"UNKNOWN:{item}" for item in unknown_stewardship]
        )
    return Decision.PASS, (
        "CAPABILITY_IDENTITY_USES_INVARIANT_MEANING_ONLY",
        "STEWARDSHIP_IS_RELATION_NOT_IDENTITY",
    )


def resolve_capability_activation(
    need: CapabilityActivationNeed,
    lineages: tuple[CapabilityLineage, ...],
    providers: tuple[CapabilityProvider, ...],
    stewardships: tuple[CapabilityStewardship, ...] = (),
) -> CapabilityActivationAssessment:
    """Resolve the smallest eligible provider configuration.

    This function resolves provider eligibility only. It does not grant action
    authority. Action authority is evaluated separately by an event-specific
    ActionAuthorityLease.
    """
    required = _unique_in_order(need.required_lineage_ids)
    lineage_decision, lineage_reasons = validate_lineage_and_stewardship(
        lineages, stewardships
    )
    if lineage_decision is not Decision.PASS:
        unresolved = tuple(
            sorted({r.split(":", 1)[1] for r in lineage_reasons if ":" in r})
        )
        return CapabilityActivationAssessment(
            decision=Decision.HOLD,
            need_id=need.need_id,
            stable_life_id=need.stable_life_id,
            return_target=need.return_target,
            bindings=(),
            activated_lineage_ids=(),
            unresolved_lineage_ids=unresolved,
            over_activation=False,
            reasons=lineage_reasons,
        )

    if not required:
        return CapabilityActivationAssessment(
            decision=Decision.PASS,
            need_id=need.need_id,
            stable_life_id=need.stable_life_id,
            return_target=need.return_target,
            bindings=(),
            activated_lineage_ids=(),
            unresolved_lineage_ids=(),
            over_activation=False,
            reasons=("NO_CAPABILITY_ACTIVATION_REQUIRED",),
        )

    known_lineages = {item.lineage_id for item in lineages}
    unknown = tuple(item for item in required if item not in known_lineages)
    if unknown:
        return CapabilityActivationAssessment(
            decision=Decision.HOLD,
            need_id=need.need_id,
            stable_life_id=need.stable_life_id,
            return_target=need.return_target,
            bindings=(),
            activated_lineage_ids=(),
            unresolved_lineage_ids=unknown,
            over_activation=False,
            reasons=("CAPABILITY_LINEAGE_UNKNOWN",),
        )

    provider_id_counts = Counter(item.provider_id for item in providers)
    duplicate_provider_ids = tuple(
        sorted(provider_id for provider_id, count in provider_id_counts.items() if count > 1)
    )
    if duplicate_provider_ids:
        return CapabilityActivationAssessment(
            decision=Decision.HOLD,
            need_id=need.need_id,
            stable_life_id=need.stable_life_id,
            return_target=need.return_target,
            bindings=(),
            activated_lineage_ids=(),
            unresolved_lineage_ids=(),
            over_activation=False,
            excluded={item: ("PROVIDER_ID_CONFLICT",) for item in duplicate_provider_ids},
            reasons=("PROVIDER_ID_CONFLICT",),
        )

    required_set = set(required)
    eligible: list[CapabilityProvider] = []
    excluded: dict[str, tuple[str, ...]] = {}

    for provider in providers:
        reasons: list[str] = []
        offered_required = required_set.intersection(provider.capability_lineage_ids)
        if not offered_required:
            reasons.append("NO_REQUIRED_CAPABILITY_OFFERED")
        if not provider.available:
            reasons.append("PROVIDER_UNAVAILABLE")
        if not provider.current_effect_eligible:
            reasons.append("PROVIDER_NOT_CURRENT_EFFECT_ELIGIBLE")
        if not provider.rights_allowed:
            reasons.append("RIGHTS_NOT_ALLOWED")
        if not provider.evidence_available:
            reasons.append("CAPABILITY_EVIDENCE_MISSING")
        if not provider.return_supported:
            reasons.append("RETURN_PATH_UNSUPPORTED")
        elif provider.return_targets and need.return_target not in provider.return_targets:
            reasons.append("RETURN_TARGET_UNSUPPORTED")
        if need.privacy_required and not provider.privacy_allowed:
            reasons.append("PRIVACY_REQUIREMENT_NOT_MET")
        if not 0.0 <= provider.reliability <= 1.0:
            reasons.append("RELIABILITY_VALUE_INVALID")
        elif provider.reliability < need.minimum_reliability:
            reasons.append("RELIABILITY_BELOW_THRESHOLD")
        if provider.estimated_cost < 0:
            reasons.append("ESTIMATED_COST_INVALID")
        if not provider.replacement_path_known:
            reasons.append("REPLACEMENT_PATH_UNKNOWN")
        if not provider.exit_condition_known:
            reasons.append("EXIT_CONDITION_UNKNOWN")

        if reasons:
            excluded[provider.provider_id] = tuple(reasons)
        else:
            eligible.append(provider)

    covering: list[tuple[CapabilityProvider, ...]] = []
    cost_limited = False
    for size in range(1, len(eligible) + 1):
        for combo in combinations(eligible, size):
            offered = set().union(*(set(item.capability_lineage_ids) for item in combo))
            if not required_set.issubset(offered):
                continue
            total_cost = sum(item.estimated_cost for item in combo)
            if need.max_total_cost is not None and total_cost > need.max_total_cost:
                cost_limited = True
                continue
            covering.append(combo)
        if covering:
            break

    if not covering:
        covered = set().union(*(set(item.capability_lineage_ids) for item in eligible)) if eligible else set()
        unresolved = tuple(item for item in required if item not in covered)
        reasons = ["NO_ELIGIBLE_CAPABILITY_CONFIGURATION"]
        if cost_limited and not unresolved:
            reasons.append("NO_CONFIGURATION_WITHIN_COST_LIMIT")
        return CapabilityActivationAssessment(
            decision=Decision.HOLD,
            need_id=need.need_id,
            stable_life_id=need.stable_life_id,
            return_target=need.return_target,
            bindings=(),
            activated_lineage_ids=(),
            unresolved_lineage_ids=unresolved,
            over_activation=False,
            excluded=dict(sorted(excluded.items())),
            reasons=tuple(reasons),
        )

    def score(combo: tuple[CapabilityProvider, ...]) -> tuple[float, float, tuple[str, ...]]:
        return (
            sum(item.estimated_cost for item in combo),
            -min(item.reliability for item in combo),
            tuple(sorted(item.provider_id for item in combo)),
        )

    selected = min(covering, key=score)
    assignments: dict[str, list[str]] = {item.provider_id: [] for item in selected}
    for lineage_id in required:
        capable = [item for item in selected if lineage_id in item.capability_lineage_ids]
        capable.sort(key=lambda item: (item.estimated_cost, -item.reliability, item.provider_id))
        assignments[capable[0].provider_id].append(lineage_id)

    bindings = tuple(
        ProviderBinding(
            provider_id=item.provider_id,
            provider_kind=item.provider_kind,
            provider_label=item.provider_label,
            activated_lineage_ids=tuple(assignments[item.provider_id]),
            estimated_cost=item.estimated_cost,
            reliability=item.reliability,
        )
        for item in sorted(selected, key=lambda provider: provider.provider_id)
        if assignments[item.provider_id]
    )
    activated = tuple(
        lineage_id
        for lineage_id in required
        if any(lineage_id in binding.activated_lineage_ids for binding in bindings)
    )

    return CapabilityActivationAssessment(
        decision=Decision.PASS,
        need_id=need.need_id,
        stable_life_id=need.stable_life_id,
        return_target=need.return_target,
        bindings=bindings,
        activated_lineage_ids=activated,
        unresolved_lineage_ids=(),
        over_activation=False,
        excluded=dict(sorted(excluded.items())),
        reasons=(
            "PROVIDER_ELIGIBILITY_RESOLVED",
            "MINIMAL_PROVIDER_CONFIGURATION_SELECTED",
            "ACTION_AUTHORITY_NOT_GRANTED_BY_PROVIDER_ELIGIBILITY",
        ),
    )


def authorize_capability_action(
    activation: CapabilityActivationAssessment,
    lease: ActionAuthorityLease | None,
    required_action_scope: str,
) -> ActionAuthorityAssessment:
    selected_provider_ids = tuple(sorted(item.provider_id for item in activation.bindings))
    if activation.decision is not Decision.PASS:
        return ActionAuthorityAssessment(
            decision=Decision.HOLD,
            lease_id=None if lease is None else lease.lease_id,
            action_scope=required_action_scope,
            authorized_provider_ids=(),
            reasons=("PROVIDER_ELIGIBILITY_NOT_PASS",),
        )
    if not selected_provider_ids:
        return ActionAuthorityAssessment(
            decision=Decision.PASS,
            lease_id=None,
            action_scope=required_action_scope,
            authorized_provider_ids=(),
            reasons=("NO_ACTION_PROVIDER_REQUIRED",),
        )
    if lease is None:
        return ActionAuthorityAssessment(
            decision=Decision.HOLD,
            lease_id=None,
            action_scope=required_action_scope,
            authorized_provider_ids=(),
            reasons=("ACTION_AUTHORITY_LEASE_MISSING",),
        )

    reasons: list[str] = []
    if not lease.active:
        reasons.append("ACTION_AUTHORITY_LEASE_INACTIVE")
    if lease.stable_life_id != activation.stable_life_id:
        reasons.append("ACTION_AUTHORITY_STABLE_LIFE_MISMATCH")
    if lease.return_target != activation.return_target:
        reasons.append("ACTION_AUTHORITY_RETURN_TARGET_MISMATCH")
    if lease.action_scope != required_action_scope:
        reasons.append("ACTION_AUTHORITY_SCOPE_MISMATCH")
    if not lease.evidence_ref:
        reasons.append("ACTION_AUTHORITY_EVIDENCE_MISSING")
    missing_provider_authority = sorted(
        set(selected_provider_ids).difference(lease.authorized_provider_ids)
    )
    if missing_provider_authority:
        reasons.append("ACTION_AUTHORITY_PROVIDER_BINDING_MISSING")

    if reasons:
        return ActionAuthorityAssessment(
            decision=Decision.HOLD,
            lease_id=lease.lease_id,
            action_scope=required_action_scope,
            authorized_provider_ids=tuple(sorted(lease.authorized_provider_ids)),
            reasons=tuple(reasons),
        )

    return ActionAuthorityAssessment(
        decision=Decision.PASS,
        lease_id=lease.lease_id,
        action_scope=required_action_scope,
        authorized_provider_ids=selected_provider_ids,
        reasons=(
            "EVENT_SPECIFIC_ACTION_AUTHORITY_LEASE_VALID",
            "PROVIDER_ELIGIBILITY_AND_ACTION_AUTHORITY_SEPARATED",
        ),
    )


def validate_provider_substitution(
    before: CapabilityActivationAssessment,
    after: CapabilityActivationAssessment,
) -> tuple[Decision, tuple[str, ...]]:
    reasons: list[str] = []
    if before.decision is not Decision.PASS or after.decision is not Decision.PASS:
        reasons.append("SUBSTITUTION_PLAN_NOT_PASS")
    if before.stable_life_id != after.stable_life_id:
        reasons.append("STABLE_IDENTITY_CHANGED_BY_PROVIDER_SUBSTITUTION")
    if before.return_target != after.return_target:
        reasons.append("RETURN_TARGET_CHANGED_BY_PROVIDER_SUBSTITUTION")
    if before.activated_lineage_ids != after.activated_lineage_ids:
        reasons.append("CAPABILITY_LINEAGE_CHANGED_BY_PROVIDER_SUBSTITUTION")
    if reasons:
        return Decision.FAIL, tuple(reasons)
    return Decision.PASS, (
        "PROVIDER_CHANGE_PRESERVES_CAPABILITY_LINEAGE",
        "PROVIDER_NAME_NOT_PART_OF_CAPABILITY_IDENTITY",
    )
