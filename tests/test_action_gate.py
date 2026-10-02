from __future__ import annotations

import unittest

from dcp_kernel.action_gate import (
    ActionGateInput,
    EffectClass,
    RiskLevel,
    assess_action_gate,
)
from dcp_kernel.models import Decision


class ActionGateTests(unittest.TestCase):
    def test_available_power_cannot_exceed_required_effect(self) -> None:
        result = assess_action_gate(
            ActionGateInput(
                transition_id="T-OBSERVE",
                required_effect=EffectClass.OBSERVE,
                proposed_effect=EffectClass.BOUNDED_MUTATION,
                risk_level=RiskLevel.LOW,
                authority_valid=True,
                responsibility_owner="ACTOR",
                return_target="DCP",
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("ACTION_EXCEEDS_MINIMUM_NECESSARY_EFFECT", result.reasons)
        self.assertFalse(result.execution_authorized)

    def test_observation_does_not_require_mutation_authority(self) -> None:
        result = assess_action_gate(
            ActionGateInput(
                transition_id="T-READ",
                required_effect=EffectClass.OBSERVE,
                proposed_effect=EffectClass.OBSERVE,
                risk_level=RiskLevel.LOW,
                authority_valid=False,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertIn("RESTRAINT_IS_CAPABILITY", result.reasons)
        self.assertFalse(result.execution_authorized)

    def test_bounded_mutation_requires_responsibility_and_return(self) -> None:
        result = assess_action_gate(
            ActionGateInput(
                transition_id="T-MUTATE",
                required_effect=EffectClass.BOUNDED_MUTATION,
                proposed_effect=EffectClass.BOUNDED_MUTATION,
                risk_level=RiskLevel.MEDIUM,
                authority_valid=True,
                responsibility_owner=None,
                return_target=None,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("RESPONSIBILITY_OWNER_MISSING", result.reasons)
        self.assertIn("RETURN_TARGET_MISSING", result.reasons)

    def test_high_risk_capability_requires_explicit_authority(self) -> None:
        result = assess_action_gate(
            ActionGateInput(
                transition_id="T-HIGH",
                required_effect=EffectClass.HIGH_RISK_MUTATION,
                proposed_effect=EffectClass.HIGH_RISK_MUTATION,
                risk_level=RiskLevel.HIGH,
                authority_valid=True,
                explicit_high_risk_authority=False,
                responsibility_owner="ACTOR",
                return_target="OWNER",
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("HIGH_RISK_ACTION_REQUIRES_EXPLICIT_AUTHORITY", result.reasons)

    def test_irreversible_action_requires_recovery_path(self) -> None:
        result = assess_action_gate(
            ActionGateInput(
                transition_id="T-IRREV",
                required_effect=EffectClass.BOUNDED_MUTATION,
                proposed_effect=EffectClass.BOUNDED_MUTATION,
                risk_level=RiskLevel.MEDIUM,
                authority_valid=True,
                reversible=False,
                recovery_path_present=False,
                responsibility_owner="ACTOR",
                return_target="OWNER",
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("IRREVERSIBLE_ACTION_WITHOUT_RECOVERY_PATH", result.reasons)

    def test_gate_pass_never_itself_authorizes_execution(self) -> None:
        result = assess_action_gate(
            ActionGateInput(
                transition_id="T-PASS",
                required_effect=EffectClass.BOUNDED_MUTATION,
                proposed_effect=EffectClass.BOUNDED_MUTATION,
                risk_level=RiskLevel.LOW,
                authority_valid=True,
                responsibility_owner="ACTOR",
                return_target="OWNER",
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertFalse(result.execution_authorized)


if __name__ == "__main__":
    unittest.main()
