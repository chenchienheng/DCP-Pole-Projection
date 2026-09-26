import unittest

from dcp_kernel.action_gate import ActionGateInput, EffectClass, RiskLevel, assess_action_gate
from dcp_kernel.coexistence import CoexistenceInput, NativeModel, assess_coexistence
from dcp_kernel.decision_chain import assess_decision_chain
from dcp_kernel.judgment import JudgmentInput, assess_judgment
from dcp_kernel.meaning_compile import MeaningCompileInput, compile_meaning
from dcp_kernel.models import Decision


class DecisionChainTests(unittest.TestCase):
    def meaning(self):
        return compile_meaning(MeaningCompileInput(
            source_id="R1-00/02",
            meaning_statement="抽象必須凝成可觀測差異",
            primitive="OBSERVABLE_DIFFERENCE",
            relation="meaning constrains action",
            constraint="no capability claim without material delta",
            gate="meaning gate",
            action_delta="hold if no observable next behavior",
            evidence_requirement="receiver-observable evidence",
            return_target="Receiver",
            rebuild_effect="next decision input changes",
        ))

    def judgment(self, **changes):
        data = dict(
            judgment_id="J-CHAIN",
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
            counterexample_channel_open=True,
            execution_available=True,
            execution_requested=False,
        )
        data.update(changes)
        return assess_judgment(JudgmentInput(**data))

    def action(self, **changes):
        data = dict(
            transition_id="T-CHAIN",
            required_effect=EffectClass.BOUNDED_MUTATION,
            proposed_effect=EffectClass.BOUNDED_MUTATION,
            risk_level=RiskLevel.MEDIUM,
            authority_valid=True,
            affected_scope_resolved=True,
            evidence_sufficient=True,
            responsibility_owner="DCP",
            return_target="Receiver",
        )
        data.update(changes)
        return assess_action_gate(ActionGateInput(**data))

    def coexistence(self, **changes):
        left = NativeModel("A", "Ideas", "LIFE-1", "MEANING", "MEANING", "prose")
        right = NativeModel("B", "DCP", "LIFE-1", "DEPENDENCY", "DEPENDENCY", "graph")
        data = dict(
            left=left,
            right=right,
            common_source_id="SHARED-R1",
            translation_available=True,
            compatibility_conditions_known=True,
            shared_evidence_interface=True,
        )
        data.update(changes)
        return assess_coexistence(CoexistenceInput(**data))

    def test_complete_chain_allows_contract_compilation_candidate_only(self):
        result = assess_decision_chain(
            meaning=self.meaning(),
            judgment=self.judgment(),
            coexistence=self.coexistence(),
            action_gate=self.action(),
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertIsNone(result.first_break)

    def test_weak_evidence_stops_before_action(self):
        result = assess_decision_chain(
            meaning=self.meaning(),
            judgment=self.judgment(evidence_sufficient=False),
            coexistence=self.coexistence(),
            action_gate=self.action(),
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.first_break, "JUDGMENT")

    def test_forced_merge_stops_before_action(self):
        result = assess_decision_chain(
            meaning=self.meaning(),
            judgment=self.judgment(),
            coexistence=self.coexistence(forced_identity_merge_requested=True),
            action_gate=self.action(),
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.first_break, "COEXISTENCE")

    def test_maximum_available_action_is_restrained(self):
        result = assess_decision_chain(
            meaning=self.meaning(),
            judgment=self.judgment(),
            coexistence=self.coexistence(),
            action_gate=self.action(proposed_effect=EffectClass.HIGH_RISK_MUTATION),
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.first_break, "ACTION_GATE")


if __name__ == "__main__":
    unittest.main()
