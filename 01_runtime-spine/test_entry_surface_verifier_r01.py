import unittest

from entry_surface_verifier_r01 import (
    AssertionContext,
    EntryDisposition,
    EntrySurfaceEvidence,
    classify_claim_context,
    qualify_entry_surfaces,
)


class EntrySurfaceVerifierR01Tests(unittest.TestCase):
    def test_raw_keyword_current_assertion_is_detected(self):
        self.assertEqual(
            classify_claim_context("Implementation status: M2 Runtime Spine partially implemented", "M2 Runtime Spine partially implemented"),
            AssertionContext.CURRENT_ASSERTION,
        )

    def test_same_keyword_inside_explicit_negation_is_not_current_assertion(self):
        self.assertEqual(
            classify_claim_context('Phrases such as “M2 Runtime Spine partially implemented” do not establish this repository\'s present Runtime.', "M2 Runtime Spine partially implemented"),
            AssertionContext.NEGATED,
        )

    def test_historical_context_is_not_current_assertion(self):
        self.assertEqual(
            classify_claim_context("Historical note: M2 Runtime Spine partially implemented", "M2 Runtime Spine partially implemented"),
            AssertionContext.HISTORICAL,
        )

    def test_absent_keyword_is_absent(self):
        self.assertEqual(
            classify_claim_context("Runtime evidence: Not established", "M2 Runtime Spine partially implemented"),
            AssertionContext.ABSENT,
        )

    def test_consistent_reader_manifest_status_roles_qualify(self):
        result = qualify_entry_surfaces(EntrySurfaceEvidence(True, True, False, False, True))
        self.assertEqual(result.disposition, EntryDisposition.QUALIFIED_CANDIDATE)

    def test_status_runtime_promotion_conflicts_with_public_entry_boundary(self):
        result = qualify_entry_surfaces(EntrySurfaceEvidence(True, True, True, False, True))
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("STATUS_RUNTIME_PROMOTION_CONFLICT", result.reasons)

    def test_missing_manifest_current_resolution_holds_only_entry_consistency(self):
        result = qualify_entry_surfaces(EntrySurfaceEvidence(True, False, False, False, True))
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("MANIFEST_CURRENT_RESOLUTION_MISSING", result.reasons)


if __name__ == "__main__":
    unittest.main()
