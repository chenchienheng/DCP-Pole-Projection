from __future__ import annotations

import unittest

from dcp_kernel.capability_activation import (
    CapabilityActivationNeed,
    CapabilityLineage,
    CapabilityProvider,
    ProviderKind,
    resolve_capability_activation,
    validate_provider_substitution,
)
from dcp_kernel.models import Decision


LINEAGES = (
    CapabilityLineage("capability-composition", "compose only affected capabilities", "DCP"),
    CapabilityLineage("current-resolution", "resolve current state and eligibility", "DCP"),
    CapabilityLineage("world-relation", "compile affected world relations", "GLMODEL"),
    CapabilityLineage("return-reconciliation", "return, disposition and rebuild", "DCP"),
    CapabilityLineage("historical-metabolism", "historical immunity and successor coverage", "DCP"),
)


def skill(
    provider_id: str,
    label: str,
    lineage_ids: tuple[str, ...],
    *,
    available: bool = True,
    authority: bool = True,
    rights: bool = True,
    current_effect_eligible: bool = True,
    return_targets: tuple[str, ...] = ("DCP",),
) -> CapabilityProvider:
    return CapabilityProvider(
        provider_id=provider_id,
        provider_kind=ProviderKind.SKILL,
        provider_label=label,
        capability_lineage_ids=lineage_ids,
        authority_scopes=("DCP_BOUNDED_WORK",) if authority else (),
        rights_allowed=rights,
        available=available,
        current_effect_eligible=current_effect_eligible,
        evidence_available=True,
        return_supported=True,
        privacy_allowed=True,
        reliability=0.95,
        estimated_cost=1.0,
        return_targets=return_targets,
        replacement_path_known=True,
        exit_condition_known=True,
    )


FIVE_SKILLS = (
    skill("skill-router", "xuanling-global-skill-router", ("capability-composition",)),
    skill("skill-current", "xuanling-current-life-resolver", ("current-resolution",)),
    skill("skill-world", "xuanling-world-relation-compiler", ("world-relation",)),
    skill("skill-return", "xuanling-return-rebuild", ("return-reconciliation",)),
    skill("skill-metabolism", "xuanling-metabolism-guardian", ("historical-metabolism",)),
)


class CapabilityActivationTests(unittest.TestCase):
    def test_affected_slice_does_not_wake_all_five_skills(self) -> None:
        need = CapabilityActivationNeed(
            need_id="resolve-and-return",
            stable_life_id="XUANLING",
            required_lineage_ids=("current-resolution", "return-reconciliation"),
            required_authority_scope="DCP_BOUNDED_WORK",
            return_target="DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, FIVE_SKILLS)
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.activated_lineage_ids, ("current-resolution", "return-reconciliation"))
        self.assertEqual({item.provider_id for item in result.bindings}, {"skill-current", "skill-return"})
        self.assertFalse(result.over_activation)
        self.assertLess(len(result.bindings), len(FIVE_SKILLS))

    def test_one_provider_may_cover_multiple_lineages_without_new_pole(self) -> None:
        combined_human = CapabilityProvider(
            provider_id="engineer-01",
            provider_kind=ProviderKind.HUMAN,
            provider_label="eligible engineer",
            capability_lineage_ids=("current-resolution", "capability-composition"),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.99,
            estimated_cost=0.5,
            return_targets=("DCP",),
        )
        need = CapabilityActivationNeed(
            "compose-current",
            "XUANLING",
            ("current-resolution", "capability-composition"),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, FIVE_SKILLS + (combined_human,))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(len(result.bindings), 1)
        self.assertEqual(result.bindings[0].provider_id, "engineer-01")

    def test_provider_removal_reresolves_same_lineage(self) -> None:
        unavailable = skill(
            "skill-current",
            "xuanling-current-life-resolver",
            ("current-resolution",),
            available=False,
        )
        fallback = CapabilityProvider(
            provider_id="model-current-fallback",
            provider_kind=ProviderKind.AI_MODEL,
            provider_label="provider-neutral current resolver",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.92,
            estimated_cost=2.0,
            return_targets=("DCP",),
        )
        providers = tuple(item for item in FIVE_SKILLS if item.provider_id != "skill-current") + (unavailable, fallback)
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, providers)
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.bindings[0].provider_id, "model-current-fallback")
        self.assertIn("PROVIDER_UNAVAILABLE", result.excluded["skill-current"])

    def test_skill_rename_does_not_change_capability_lineage(self) -> None:
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        before = resolve_capability_activation(
            need,
            LINEAGES,
            (skill("provider-v1", "xuanling-current-life-resolver", ("current-resolution",)),),
        )
        after = resolve_capability_activation(
            need,
            LINEAGES,
            (skill("provider-v2", "renamed-current-provider", ("current-resolution",)),),
        )
        decision, reasons = validate_provider_substitution(before, after)
        self.assertEqual(decision, Decision.PASS)
        self.assertIn("PROVIDER_NAME_NOT_PART_OF_CAPABILITY_IDENTITY", reasons)

    def test_missing_authority_holds_without_birthing_significance_skill(self) -> None:
        need = CapabilityActivationNeed(
            "material-decision",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        unauthorized = skill(
            "skill-current",
            "xuanling-current-life-resolver",
            ("current-resolution",),
            authority=False,
        )
        result = resolve_capability_activation(need, LINEAGES, (unauthorized,))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("AUTHORITY_SCOPE_NOT_ALLOWED", result.excluded["skill-current"])
        self.assertNotIn("significance-decision", result.activated_lineage_ids)

    def test_no_capability_need_stays_quiet(self) -> None:
        need = CapabilityActivationNeed(
            "local-chat",
            "XUANLING",
            (),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, FIVE_SKILLS)
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.bindings, ())
        self.assertIn("NO_CAPABILITY_ACTIVATION_REQUIRED", result.reasons)

    def test_unknown_lineage_holds_before_provider_selection(self) -> None:
        need = CapabilityActivationNeed(
            "unknown-capability",
            "XUANLING",
            ("significance-decision",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, FIVE_SKILLS)
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.unresolved_lineage_ids, ("significance-decision",))
        self.assertIn("CAPABILITY_LINEAGE_UNKNOWN", result.reasons)

    def test_historical_provider_cannot_self_reactivate(self) -> None:
        historical = skill(
            "historical-current-skill",
            "retired current resolver",
            ("current-resolution",),
            current_effect_eligible=False,
        )
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, (historical,))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn(
            "PROVIDER_NOT_CURRENT_EFFECT_ELIGIBLE",
            result.excluded["historical-current-skill"],
        )

    def test_replacement_and_exit_conditions_are_admission_gates(self) -> None:
        unbounded = CapabilityProvider(
            provider_id="unbounded-provider",
            provider_kind=ProviderKind.SKILL,
            provider_label="skill without lifecycle contract",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.99,
            return_targets=("DCP",),
            replacement_path_known=False,
            exit_condition_known=False,
        )
        fallback = skill(
            "bounded-provider",
            "bounded current resolver",
            ("current-resolution",),
        )
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, (unbounded, fallback))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.bindings[0].provider_id, "bounded-provider")
        self.assertIn("REPLACEMENT_PATH_UNKNOWN", result.excluded["unbounded-provider"])
        self.assertIn("EXIT_CONDITION_UNKNOWN", result.excluded["unbounded-provider"])

    def test_privacy_and_reliability_filter_provider(self) -> None:
        privacy_fail = CapabilityProvider(
            provider_id="privacy-fail",
            provider_kind=ProviderKind.CLOUD,
            provider_label="external cloud model",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=False,
            reliability=0.99,
            estimated_cost=0.1,
            return_targets=("DCP",),
        )
        reliability_fail = CapabilityProvider(
            provider_id="reliability-fail",
            provider_kind=ProviderKind.AI_MODEL,
            provider_label="unstable model",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.5,
            estimated_cost=0.1,
            return_targets=("DCP",),
        )
        eligible = CapabilityProvider(
            provider_id="eligible-local",
            provider_kind=ProviderKind.LOCAL_COMPUTE,
            provider_label="local bounded resolver",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.95,
            estimated_cost=1.0,
            return_targets=("DCP",),
        )
        need = CapabilityActivationNeed(
            "private-current",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
            privacy_required=True,
            minimum_reliability=0.9,
        )
        result = resolve_capability_activation(
            need,
            LINEAGES,
            (privacy_fail, reliability_fail, eligible),
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.bindings[0].provider_id, "eligible-local")
        self.assertIn("PRIVACY_REQUIREMENT_NOT_MET", result.excluded["privacy-fail"])
        self.assertIn("RELIABILITY_BELOW_THRESHOLD", result.excluded["reliability-fail"])

    def test_cost_limit_holds_without_falsely_marking_lineage_unresolved(self) -> None:
        expensive = CapabilityProvider(
            provider_id="expensive-provider",
            provider_kind=ProviderKind.HUMAN,
            provider_label="consultant",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.99,
            estimated_cost=10.0,
            return_targets=("DCP",),
        )
        need = CapabilityActivationNeed(
            "cost-bounded-current",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
            max_total_cost=1.0,
        )
        result = resolve_capability_activation(need, LINEAGES, (expensive,))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.unresolved_lineage_ids, ())
        self.assertIn("NO_CONFIGURATION_WITHIN_COST_LIMIT", result.reasons)

    def test_conflicting_lineage_definitions_hold(self) -> None:
        conflicting = LINEAGES + (
            CapabilityLineage("current-resolution", "different meaning", "IDEAS"),
        )
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, conflicting, FIVE_SKILLS)
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.unresolved_lineage_ids, ("current-resolution",))
        self.assertIn("CAPABILITY_LINEAGE_CONFLICT", result.reasons)

    def test_duplicate_provider_identity_holds(self) -> None:
        duplicate = (
            skill("same-provider", "provider A", ("current-resolution",)),
            skill("same-provider", "provider B", ("current-resolution",)),
        )
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, duplicate)
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("PROVIDER_ID_CONFLICT", result.reasons)
        self.assertIn("PROVIDER_ID_CONFLICT", result.excluded["same-provider"])

    def test_rights_and_return_target_are_admission_gates(self) -> None:
        rights_fail = skill(
            "rights-fail",
            "readable but unauthorized provider",
            ("current-resolution",),
            rights=False,
        )
        target_fail = skill(
            "target-fail",
            "wrong return route",
            ("current-resolution",),
            return_targets=("GLMODEL",),
        )
        eligible = skill(
            "eligible-provider",
            "bounded provider",
            ("current-resolution",),
        )
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, (rights_fail, target_fail, eligible))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.bindings[0].provider_id, "eligible-provider")
        self.assertIn("RIGHTS_NOT_ALLOWED", result.excluded["rights-fail"])
        self.assertIn("RETURN_TARGET_UNSUPPORTED", result.excluded["target-fail"])

    def test_invalid_provider_metrics_are_rejected(self) -> None:
        invalid_reliability = CapabilityProvider(
            provider_id="invalid-reliability",
            provider_kind=ProviderKind.AI_MODEL,
            provider_label="invalid reliability",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=1.5,
            estimated_cost=0.0,
            return_targets=("DCP",),
        )
        invalid_cost = CapabilityProvider(
            provider_id="invalid-cost",
            provider_kind=ProviderKind.SOFTWARE,
            provider_label="invalid cost",
            capability_lineage_ids=("current-resolution",),
            authority_scopes=("DCP_BOUNDED_WORK",),
            rights_allowed=True,
            available=True,
            current_effect_eligible=True,
            evidence_available=True,
            return_supported=True,
            privacy_allowed=True,
            reliability=0.9,
            estimated_cost=-1.0,
            return_targets=("DCP",),
        )
        need = CapabilityActivationNeed(
            "current-only",
            "XUANLING",
            ("current-resolution",),
            "DCP_BOUNDED_WORK",
            "DCP",
        )
        result = resolve_capability_activation(need, LINEAGES, (invalid_reliability, invalid_cost))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("RELIABILITY_VALUE_INVALID", result.excluded["invalid-reliability"])
        self.assertIn("ESTIMATED_COST_INVALID", result.excluded["invalid-cost"])


if __name__ == "__main__":
    unittest.main()
