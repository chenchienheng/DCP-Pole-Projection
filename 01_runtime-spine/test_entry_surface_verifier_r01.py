import unittest

from entry_surface_verifier_r01 import (
    AssertionContext,
    EntryDisposition,
    EntrySurfaceEvidence,
    SemanticBoundary,
    SemanticPromotionEvidence,
    classify_claim_context,
    qualify_entry_surfaces,
    qualify_semantic_promotion,
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


class SemanticPromotionBatchTests(unittest.TestCase):
    def qualify(self, boundary, **changes):
        values = dict(
            boundary=boundary,
            stable_binding=True,
            purpose_qualified=True,
            authority_qualified=True,
            evidence_observed=True,
            explicit_current_pointer=True,
            execution_observed=True,
            runtime_environment_observed=True,
            acceptance_observed=True,
            receipt_observed=True,
            discoverable_observed=True,
            readback_observed=True,
            delivery_observed=True,
            reader_observed=True,
            explicit_use_observed=True,
            capability_observed=True,
            data_boundary_qualified=True,
        )
        values.update(changes)
        return qualify_semantic_promotion(SemanticPromotionEvidence(**values))

    def test_historical_does_not_become_current_from_recency_alone(self):
        result = self.qualify(SemanticBoundary.HISTORICAL_TO_CURRENT, explicit_current_pointer=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("MISSING_EXPLICIT_CURRENT_POINTER", result.reasons)

    def test_historical_to_current_requires_authority(self):
        result = self.qualify(SemanticBoundary.HISTORICAL_TO_CURRENT, authority_qualified=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)

    def test_historical_to_current_can_qualify_with_full_binding(self):
        self.assertEqual(
            self.qualify(SemanticBoundary.HISTORICAL_TO_CURRENT).disposition,
            EntryDisposition.QUALIFIED_CANDIDATE,
        )

    def test_candidate_definitions_do_not_become_runtime_without_execution(self):
        result = self.qualify(SemanticBoundary.CANDIDATE_TO_RUNTIME, execution_observed=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("MISSING_EXECUTION_OBSERVED", result.reasons)

    def test_candidate_execution_alone_does_not_establish_runtime(self):
        result = self.qualify(SemanticBoundary.CANDIDATE_TO_RUNTIME, acceptance_observed=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)

    def test_candidate_to_runtime_can_only_qualify_with_runtime_and_acceptance_evidence(self):
        self.assertEqual(
            self.qualify(SemanticBoundary.CANDIDATE_TO_RUNTIME).disposition,
            EntryDisposition.QUALIFIED_CANDIDATE,
        )

    def test_write_receipt_does_not_equal_readback(self):
        result = self.qualify(SemanticBoundary.RECEIPT_TO_READBACK, readback_observed=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("MISSING_READBACK_OBSERVED", result.reasons)

    def test_discoverability_is_required_between_receipt_and_readback(self):
        result = self.qualify(SemanticBoundary.RECEIPT_TO_READBACK, discoverable_observed=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)

    def test_receipt_to_readback_can_qualify_after_delayed_convergence(self):
        self.assertEqual(
            self.qualify(SemanticBoundary.RECEIPT_TO_READBACK).disposition,
            EntryDisposition.QUALIFIED_CANDIDATE,
        )

    def test_delivery_and_read_do_not_force_use(self):
        result = self.qualify(SemanticBoundary.DELIVERY_TO_USE, explicit_use_observed=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("MISSING_EXPLICIT_USE_OBSERVED", result.reasons)

    def test_delivery_to_use_requires_reader_observation(self):
        result = self.qualify(SemanticBoundary.DELIVERY_TO_USE, reader_observed=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)

    def test_delivery_to_use_can_qualify_only_with_explicit_use(self):
        self.assertEqual(
            self.qualify(SemanticBoundary.DELIVERY_TO_USE).disposition,
            EntryDisposition.QUALIFIED_CANDIDATE,
        )

    def test_capability_does_not_grant_authority(self):
        result = self.qualify(SemanticBoundary.CAPABILITY_TO_AUTHORITY, authority_qualified=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)
        self.assertIn("MISSING_AUTHORITY_QUALIFIED", result.reasons)

    def test_capability_authority_requires_data_boundary(self):
        result = self.qualify(SemanticBoundary.CAPABILITY_TO_AUTHORITY, data_boundary_qualified=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)

    def test_capability_authority_can_qualify_only_for_bound_purpose(self):
        result = self.qualify(SemanticBoundary.CAPABILITY_TO_AUTHORITY, purpose_qualified=False)
        self.assertEqual(result.disposition, EntryDisposition.HOLD)

    def test_capability_to_authority_can_qualify_with_all_scoped_evidence(self):
        self.assertEqual(
            self.qualify(SemanticBoundary.CAPABILITY_TO_AUTHORITY).disposition,
            EntryDisposition.QUALIFIED_CANDIDATE,
        )


if __name__ == "__main__":
    unittest.main()
