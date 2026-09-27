import unittest

from dcp_kernel.coexistence import (
    CoexistenceInput,
    CompatibilityState,
    NativeModel,
    assess_coexistence,
)
from dcp_kernel.models import Decision


class CoexistenceTests(unittest.TestCase):
    def setUp(self):
        self.a = NativeModel("A", "Ideas", "LIFE-1", "MEANING-LOGIC", "MEANING", "prose")
        self.b = NativeModel("B", "DCP", "LIFE-1", "DEPENDENCY-LOGIC", "DEPENDENCY", "graph")

    def test_common_source_does_not_authorize_merge(self):
        result = assess_coexistence(CoexistenceInput(
            left=self.a,
            right=self.b,
            common_source_id="SOURCE-1",
            forced_identity_merge_requested=True,
        ))
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, CompatibilityState.FORCED_MERGE_REJECTED)
        self.assertTrue(result.preserve_native_models)

    def test_different_logic_without_translation_holds(self):
        result = assess_coexistence(CoexistenceInput(
            left=self.a,
            right=self.b,
            common_source_id="SOURCE-1",
        ))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, CompatibilityState.TRANSLATION_REQUIRED)

    def test_translation_allows_coexistence_without_identity_merge(self):
        result = assess_coexistence(CoexistenceInput(
            left=self.a,
            right=self.b,
            common_source_id="SOURCE-1",
            translation_available=True,
            compatibility_conditions_known=True,
            shared_evidence_interface=True,
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, CompatibilityState.COEXIST)
        self.assertTrue(result.preserve_native_models)


if __name__ == "__main__":
    unittest.main()
