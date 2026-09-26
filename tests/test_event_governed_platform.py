import unittest

from dcp_kernel import (
    ActionGateInput, ActivationInput, CapabilityBinding, CoexistenceInput,
    CurrentCandidate, Decision, EffectClass, InvariantCore, JudgmentInput,
    LifecycleState, MeaningCompileInput, NativeModel, Need, PersistentState,
    RiskLevel, StableLife, Transition, TriRootState, assess_action_gate,
    assess_activation, assess_coexistence, assess_decision_chain, assess_judgment,
    compile_event_governed_work_contract, compile_meaning,
)


class EventGovernedPlatformTests(unittest.TestCase):
    def chain(self):
        meaning = compile_meaning(MeaningCompileInput(
            source_id="R1-04",
            meaning_statement="Persistent state, event-driven wake, judgment before action.",
            primitive="EVENT_DRIVEN_LIFE",
            relation="event activates bounded decision over persistent state",
            constraint="wake is not authority or execution",
            gate="activation then decision chain",
            action_delta="material events may wake candidate work only after gates",
            evidence_requirement="typed event/state evidence",
            return_target="Receiver",
            rebuild_effect="receiver result changes persistent state",
        ))
        judgment = assess_judgment(JudgmentInput(
            judgment_id="J-R1-04",
            source_classified=True,
            meaning_relevant=True,
            boundary_resolved=True,
            evidence_sufficient=True,
            alternatives_considered=True,
            consequence_assessed=True,
            responsibility_owner="DCP",
            return_target="Receiver",
            rebuild_path_present=True,
            authority_valid=True,
        ))
        coexistence = assess_coexistence(CoexistenceInput(
            left=NativeModel("A", "Ideas", "LIFE-1", "MEANING", "MEANING", "prose"),
            right=NativeModel("B", "DCP", "LIFE-1", "DEPENDENCY", "DEPENDENCY", "graph"),
            translation_available=True,
            compatibility_conditions_known=True,
            shared_evidence_interface=True,
        ))
        action_gate = assess_action_gate(ActionGateInput(
            transition_id="T-EVENT",
            required_effect=EffectClass.OBSERVE,
            proposed_effect=EffectClass.OBSERVE,
            risk_level=RiskLevel.LOW,
            authority_valid=True,
            affected_scope_resolved=True,
            evidence_sufficient=True,
            responsibility_owner="DCP",
            return_target="Receiver",
        ))
        return assess_decision_chain(
            meaning=meaning,
            judgment=judgment,
            coexistence=coexistence,
            action_gate=action_gate,
        )

    def platform_inputs(self):
        life = StableLife(
            life_id="LIFE-1",
            invariant_core=InvariantCore("LIFE-1", "Preserve meaning", "WORLD-1"),
            native_owner="Vitas",
            current_revision="R1",
            last_good_revision="R1",
        )
        tri = TriRootState(True, True, "WORLD-1", "R1")
        need = Need("N-EVENT", "MODEL", "Receiver")
        capability = CapabilityBinding("MODEL", "Actor", "Carrier", True, True, True, "Receiver", True)
        current = CurrentCandidate("LIFE-1", "R1", LifecycleState.CURRENT, None, True, True, True, True, "2026-08-23")
        transition = Transition(
            transition_id="T-EVENT",
            stable_life_id="LIFE-1",
            need="N-EVENT",
            state_before=LifecycleState.CURRENT,
            proposed_effect="observe",
            capability_id="MODEL",
            source_revision="R1",
            world_id_before="WORLD-1",
            world_id_after="WORLD-1",
        )
        return life, tri, need, capability, current, transition

    def activation(self, *, material):
        state = PersistentState(
            stable_life_id="LIFE-1",
            current_revision="R1",
            authority_ceiling="DCP_COMPILE_ONLY",
            last_good_revision="R1",
            active_need="N-EVENT",
        )
        return assess_activation(ActivationInput(
            event_id="EVENT-1",
            event_material=material,
            affected_stable_life_id="LIFE-1",
            state=state,
            identity_match=True,
            authority_available=True,
            gate_known=True,
            affected_scope_known=True,
            return_path_known=True,
        ))

    def compile(self, activation):
        life, tri, need, capability, current, transition = self.platform_inputs()
        return compile_event_governed_work_contract(
            activation=activation,
            decision_chain=self.chain(),
            stable_life=life,
            tri_root=tri,
            need=need,
            capability_candidates=[capability],
            current_candidates=[current],
            changed_nodes=["Source"],
            dependency_graph={"Source": ["Receiver"]},
            eligible_receivers={"Receiver"},
            transition=transition,
        )

    def test_sleep_does_not_compile_work_contract(self):
        result = self.compile(self.activation(material=False))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIsNone(result.work_contract)

    def test_material_event_wakes_governed_candidate_path(self):
        result = self.compile(self.activation(material=True))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertIsNotNone(result.work_contract)
        self.assertEqual(result.work_contract.state, "CANDIDATE")


if __name__ == "__main__":
    unittest.main()
