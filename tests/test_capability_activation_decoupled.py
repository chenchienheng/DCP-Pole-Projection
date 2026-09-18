from __future__ import annotations

import unittest

from dcp_kernel.capability_activation_decoupled import (
    ActionAuthorityLease,
    CapabilityActivationNeed,
    CapabilityLineage,
    CapabilityProvider,
    CapabilityStewardship,
    ProviderKind,
    authorize_capability_action,
    resolve_capability_activation,
    validate_lineage_and_stewardship,
    validate_provider_substitution,
)
from dcp_kernel.models import Decision


LINEAGES = (
    CapabilityLineage("capability-composition", "compose only affected capabilities"),
    CapabilityLineage("current-resolution", "resolve current state and eligibility"),
    CapabilityLineage("return-reconciliation", "return, disposition and rebuild"),
)


def provider(
    provider_id: str,
    lineage_ids: tuple[str, ...],
    *,
    available: bool = True,
    current_effect_eligible: bool = True,
    rights_allowed: bool = True,
    return_target: str = "DCP",
) -> CapabilityProvider:
    return CapabilityProvider(
        provider_id=provider_id,
        provider_kind=ProviderKind.SKILL,
        provider_label=provider_id,
        capability_lineage_ids=lineage_ids,
        rights_allowed=rights_allowed,
        available=available,
        current_effect_eligible=current_effect_eligible,
        evidence_available=True,
        return_supported=True,
        privacy_allowed=True,
        reliability=0.95,
        estimated_cost=1.0,
        return_targets=(return_target,),
        replacement_path_known=True,
        exit_condition_known=True,
    )


def need(*lineage_ids: str) -> CapabilityActivationNeed:
    return CapabilityActivationNeed(
        need_id="need-1",
        stable_life_id="XUANLING",
        required_lineage_ids=tuple(lineage_ids),
        return_target="DCP",
    )


class CapabilityAuthorityDecouplingTests(unittest.TestCase):
    def test_provider_eligibility_passes_without_action_authority(self) -> None:
        activation = resolve_capability_activation(
            need("current-resolution"),
            LINEAGES,
            (provider("eligible", ("current-resolution",)),),
        )
        self.assertEqual(activation.decision, Decision.PASS)
        authority = authorize_capability_action(
            activation,
            None,
            "DCP_BOUNDED_MUTATION",
        )
        self.assertEqual(authority.decision, Decision.HOLD)
        self.assertIn("ACTION_AUTHORITY_LEASE_MISSING", authority.reasons)

    def test_event_specific_lease_authorizes_selected_binding_only(self) -> None:
        activation = resolve_capability_activation(
            need("current-resolution"),
            LINEAGES,
            (
                provider("selected", ("current-resolution",)),
                provider("other", ("return-reconciliation",)),
            ),
        )
        lease = ActionAuthorityLease(
            lease_id="lease-1",
            event_id="evt-1",
            stable_life_id="XUANLING",
            action_scope="DCP_BOUNDED_MUTATION",
            authorized_provider_ids=("selected",),
            return_target="DCP",
            evidence_ref="receipt:authority-1",
        )
        result = authorize_capability_action(
            activation,
            lease,
            "DCP_BOUNDED_MUTATION",
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.authorized_provider_ids, ("selected",))

    def test_lease_for_wrong_provider_holds(self) -> None:
        activation = resolve_capability_activation(
            need("current-resolution"),
            LINEAGES,
            (provider("selected", ("current-resolution",)),),
        )
        lease = ActionAuthorityLease(
            lease_id="lease-2",
            event_id="evt-2",
            stable_life_id="XUANLING",
            action_scope="DCP_BOUNDED_MUTATION",
            authorized_provider_ids=("someone-else",),
            return_target="DCP",
            evidence_ref="receipt:authority-2",
        )
        result = authorize_capability_action(
            activation,
            lease,
            "DCP_BOUNDED_MUTATION",
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("ACTION_AUTHORITY_PROVIDER_BINDING_MISSING", result.reasons)

    def test_stewardship_change_does_not_fork_lineage_identity(self) -> None:
        before = (
            CapabilityStewardship("current-resolution", "DCP"),
        )
        after = (
            CapabilityStewardship("current-resolution", "DCP"),
            CapabilityStewardship("current-resolution", "IDEAS", relation="PROVENANCE_FROM"),
        )
        self.assertEqual(validate_lineage_and_stewardship(LINEAGES, before)[0], Decision.PASS)
        self.assertEqual(validate_lineage_and_stewardship(LINEAGES, after)[0], Decision.PASS)
        activation_before = resolve_capability_activation(
            need("current-resolution"), LINEAGES, (provider("p", ("current-resolution",)),), before
        )
        activation_after = resolve_capability_activation(
            need("current-resolution"), LINEAGES, (provider("p", ("current-resolution",)),), after
        )
        self.assertEqual(activation_before.activated_lineage_ids, activation_after.activated_lineage_ids)

    def test_invariant_meaning_conflict_holds_even_if_stewardship_is_valid(self) -> None:
        conflicting = LINEAGES + (
            CapabilityLineage("current-resolution", "different invariant meaning"),
        )
        decision, reasons = validate_lineage_and_stewardship(
            conflicting,
            (CapabilityStewardship("current-resolution", "DCP"),),
        )
        self.assertEqual(decision, Decision.HOLD)
        self.assertIn("CAPABILITY_LINEAGE_MEANING_CONFLICT", reasons)

    def test_unknown_stewardship_lineage_holds(self) -> None:
        decision, reasons = validate_lineage_and_stewardship(
            LINEAGES,
            (CapabilityStewardship("unknown-capability", "DCP"),),
        )
        self.assertEqual(decision, Decision.HOLD)
        self.assertIn("STEWARDSHIP_REFERENCES_UNKNOWN_LINEAGE", reasons)

    def test_historical_provider_cannot_self_reactivate(self) -> None:
        activation = resolve_capability_activation(
            need("current-resolution"),
            LINEAGES,
            (provider("historical", ("current-resolution",), current_effect_eligible=False),),
        )
        self.assertEqual(activation.decision, Decision.HOLD)
        self.assertIn(
            "PROVIDER_NOT_CURRENT_EFFECT_ELIGIBLE",
            activation.excluded["historical"],
        )

    def test_provider_replacement_preserves_capability_lineage(self) -> None:
        before = resolve_capability_activation(
            need("current-resolution"), LINEAGES, (provider("v1", ("current-resolution",)),)
        )
        after = resolve_capability_activation(
            need("current-resolution"), LINEAGES, (provider("v2", ("current-resolution",)),)
        )
        decision, reasons = validate_provider_substitution(before, after)
        self.assertEqual(decision, Decision.PASS)
        self.assertIn("PROVIDER_NAME_NOT_PART_OF_CAPABILITY_IDENTITY", reasons)

    def test_no_need_stays_quiet_without_lease(self) -> None:
        activation = resolve_capability_activation(need(), LINEAGES, ())
        self.assertEqual(activation.decision, Decision.PASS)
        self.assertIn("NO_CAPABILITY_ACTIVATION_REQUIRED", activation.reasons)
        authority = authorize_capability_action(activation, None, "DCP_BOUNDED_MUTATION")
        self.assertEqual(authority.decision, Decision.PASS)
        self.assertIn("NO_ACTION_PROVIDER_REQUIRED", authority.reasons)

    def test_activation_pass_does_not_claim_runtime_or_native_adoption(self) -> None:
        activation = resolve_capability_activation(
            need("current-resolution"),
            LINEAGES,
            (provider("eligible", ("current-resolution",)),),
        )
        self.assertEqual(activation.decision, Decision.PASS)
        serialized_reasons = " ".join(activation.reasons)
        self.assertNotIn("RUNTIME", serialized_reasons)
        self.assertNotIn("NATIVE_ADOPTION", serialized_reasons)
        self.assertIn("ACTION_AUTHORITY_NOT_GRANTED_BY_PROVIDER_ELIGIBILITY", activation.reasons)


if __name__ == "__main__":
    unittest.main()
