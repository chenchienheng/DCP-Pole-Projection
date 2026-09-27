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
    meaning: str
    native_home: str


@dataclass(frozen=True)
class CapabilityActivationNeed:
    need_id: str
    stable_life_id: str
    required_lineage_ids: tuple[str, ...]
    required_authority_scope: str
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
    authority_scopes: tuple[str, ...]
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


def _unique_in_order(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def resolve_capability_activation(
    need: CapabilityActivationNeed,
    lineages: tuple[CapabilityLineage, ...],
    providers: tuple[CapabilityProvider, ...],
) -> CapabilityActivationAssessment:
    """Resolve the smallest lawful provider configuration by CapabilityLineageID.

    Provider labels, Skill names, vendor names and historical activation order are
    evidence only. They are never dependency keys and never grant Authority.
    """

    required = _unique_in_order(need.required_lineage_ids)
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

    lineage_definitions: dict[str, tuple[str, str]] = {}
    lineage_conflicts: set[str] = set()
    for lineage in lineages:
        definition = (lineage.meaning, lineage.native_home)
        previous = lineage_definitions.get(lineage.lineage_id)
        if previous is not None and previous != definition:
            lineage_conflicts.add(lineage.lineage_id)
        else:
            lineage_definitions[lineage.lineage_id] = definition

    if lineage_conflicts:
        conflicts = tuple(sorted(lineage_conflicts))
        return CapabilityActivationAssessment(
            decision=Decision.HOLD,
            need_id=need.need_id,
            stable_life_id=need.stable_life_id,
            return_target=need.return_target,
            bindings=(),
            activated_lineage_ids=(),
            unresolved_lineage_ids=conflicts,
            over_activation=False,
            reasons=("CAPABILITY_LINEAGE_CONFLICT",),
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
            excluded={
                provider_id: ("PROVIDER_ID_CONFLICT",)
                for provider_id in duplicate_provider_ids
            },
            reasons=("PROVIDER_ID_CONFLICT",),
        )

    known_lineages = set(lineage_definitions)
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
        if need.required_authority_scope not in provider.authority_scopes:
            reasons.append("AUTHORITY_SCOPE_NOT_ALLOWED")
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
        total_cost = sum(item.estimated_cost for item in combo)
        minimum_reliability = min(item.reliability for item in combo)
        return (total_cost, -minimum_reliability, tuple(sorted(item.provider_id for item in combo)))

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
    over_activation = any(
        lineage_id not in required_set
        for binding in bindings
        for lineage_id in binding.activated_lineage_ids
    )

    reasons = [
        "CAPABILITY_LINEAGE_BOUNDING_APPLIED",
        "MINIMAL_PROVIDER_CONFIGURATION_SELECTED",
        "PROVIDER_LABEL_NOT_USED_AS_DEPENDENCY_KEY",
    ]
    if over_activation:
        reasons.append("OVER_ACTIVATION")

    return CapabilityActivationAssessment(
        decision=Decision.FAIL if over_activation else Decision.PASS,
        need_id=need.need_id,
        stable_life_id=need.stable_life_id,
        return_target=need.return_target,
        bindings=bindings,
        activated_lineage_ids=activated,
        unresolved_lineage_ids=(),
        over_activation=over_activation,
        excluded=dict(sorted(excluded.items())),
        reasons=tuple(reasons),
    )


def validate_provider_substitution(
    before: CapabilityActivationAssessment,
    after: CapabilityActivationAssessment,
) -> tuple[Decision, tuple[str, ...]]:
    """Verify that provider rename/replacement does not rewrite capability identity."""

    reasons: list[str] = []
    if before.decision is not Decision.PASS or after.decision is not Decision.PASS:
        reasons.append("SUBSTITUTION_PLAN_NOT_PASS")
    if before.stable_life_id != after.stable_life_id:
        reasons.append("STABLE_IDENTITY_CHANGED_BY_PROVIDER_SUBSTITUTION")
    if before.return_target != after.return_target:
        reasons.append("RETURN_TARGET_CHANGED_BY_PROVIDER_SUBSTITUTION")
    if before.activated_lineage_ids != after.activated_lineage_ids:
        reasons.append("CAPABILITY_LINEAGE_CHANGED_BY_PROVIDER_SUBSTITUTION")
    if before.over_activation or after.over_activation:
        reasons.append("OVER_ACTIVATION_PRESENT")

    if reasons:
        return Decision.FAIL, tuple(reasons)
    return Decision.PASS, (
        "PROVIDER_CHANGE_PRESERVES_CAPABILITY_LINEAGE",
        "PROVIDER_NAME_NOT_PART_OF_CAPABILITY_IDENTITY",
    )
