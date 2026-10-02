import unittest

from dcp_kernel.meaning_compile import MeaningCompileInput, MeaningLevel, compile_meaning
from dcp_kernel.models import Decision


class MeaningCompileTests(unittest.TestCase):
    def test_abstract_meaning_remains_human_meaning(self):
        result = compile_meaning(MeaningCompileInput(
            source_id="玄意-001",
            meaning_statement="同源可以分化，道可容道。",
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.level, MeaningLevel.HUMAN_MEANING)
        self.assertFalse(result.capability_claim_allowed)

    def test_structure_without_behavior_difference_holds(self):
        result = compile_meaning(MeaningCompileInput(
            source_id="玄意-002",
            meaning_statement="能容異道而不吞。",
            primitive="COEXISTENCE_WITH_BOUNDARY",
            relation="A and B retain Native identity",
            constraint="coexistence must not merge authority",
        ))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertFalse(result.capability_claim_allowed)

    def test_complete_path_is_only_capability_candidate(self):
        result = compile_meaning(MeaningCompileInput(
            source_id="玄意-003",
            meaning_statement="玄意必須凝成現實差異。",
            primitive="OBSERVABLE_DIFFERENCE",
            relation="meaning source constrains proposed action",
            constraint="no capability claim without observable delta",
            gate="meaning compilation gate",
            action_delta="hold action when no measurable next behavior exists",
            evidence_requirement="fixture or world evidence of changed decision",
            return_target="Native Receiver",
            rebuild_effect="next condition changes resolver input",
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.level, MeaningLevel.OBSERVABLE_CAPABILITY_CANDIDATE)
        self.assertTrue(result.capability_claim_allowed)


if __name__ == "__main__":
    unittest.main()
