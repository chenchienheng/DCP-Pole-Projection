import unittest

from dcp_kernel.activation import ActivationInput, ActivationState, PersistentState, assess_activation
from dcp_kernel.models import Decision


class ActivationTests(unittest.TestCase):
    def state(self):
        return PersistentState(
            stable_life_id="GUI-LU",
            current_revision="R1",
            authority_ceiling="DCP_COMPILE_ONLY",
            last_good_revision="R0",
            active_need="mobility-envelope",
            pending_return_debt=("GLMODEL_NATIVE_READ",),
            cursor="RETURN-ROUTED",
        )

    def test_non_material_event_stays_asleep(self):
        result = assess_activation(ActivationInput(
            event_id="E-1",
            event_material=False,
            affected_stable_life_id="GUI-LU",
            state=self.state(),
            identity_match=True,
            authority_available=True,
            gate_known=True,
            affected_scope_known=True,
            return_path_known=True,
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.activation_state, ActivationState.SLEEP)
        self.assertFalse(result.persistent_agent_required)

    def test_material_event_without_authority_holds(self):
        result = assess_activation(ActivationInput(
            event_id="E-2",
            event_material=True,
            affected_stable_life_id="GUI-LU",
            state=self.state(),
            identity_match=True,
            authority_available=False,
            gate_known=True,
            affected_scope_known=True,
            return_path_known=True,
        ))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.activation_state, ActivationState.HOLD)
        self.assertFalse(result.wake_permitted_as_candidate)

    def test_material_event_can_wake_bounded_chain_without_persistent_agent(self):
        result = assess_activation(ActivationInput(
            event_id="E-3",
            event_material=True,
            affected_stable_life_id="GUI-LU",
            state=self.state(),
            identity_match=True,
            authority_available=True,
            gate_known=True,
            affected_scope_known=True,
            return_path_known=True,
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.activation_state, ActivationState.WAKE_CANDIDATE)
        self.assertTrue(result.wake_permitted_as_candidate)
        self.assertFalse(result.persistent_agent_required)


if __name__ == "__main__":
    unittest.main()
