from __future__ import annotations

import unittest

from dcp_kernel.feedback_synthesis import (
    CrossPoleFeedbackInput,
    FeedbackDisposition,
    assess_cross_pole_feedback,
)
from dcp_kernel.models import Decision


class CrossPoleFeedbackTests(unittest.TestCase):
    def test_unaffected_receiver_stays_local(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="GLMODEL",
                receiver_pole="DCP",
                affected_receivers=("IDEAS",),
                material_delta=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.disposition, FeedbackDisposition.STAY_LOCAL)
        self.assertFalse(result.local_rebuild_required)

    def test_no_material_delta_does_not_propagate(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="OBSERVATORY",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=False,
            )
        )
        self.assertEqual(result.disposition, FeedbackDisposition.NO_MATERIAL_CONFLICT)
        self.assertFalse(result.maturity_credit)

    def test_counterexample_requires_local_rebuild(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="VIRTUAL_LAB",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                counterexample_present=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, FeedbackDisposition.REBUILD_REQUIRED)
        self.assertTrue(result.local_rebuild_required)

    def test_representation_drift_is_not_same_world_learning(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="RENDER",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                representation_backmap_preserved=False,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, FeedbackDisposition.HOLD_REPRESENTATION_DRIFT)
        self.assertTrue(result.local_rebuild_required)

    def test_understanding_cannot_transfer_authority(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="EXTERNAL_REFERENCE",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                authority_transfer_requested=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.disposition, FeedbackDisposition.HOLD_AUTHORITY_INFLATION)

    def test_native_body_copy_is_contamination(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="IDEAS",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                native_body_copy_requested=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.disposition, FeedbackDisposition.HOLD_NATIVE_BODY_COPY)

    def test_single_success_does_not_create_maturity_credit(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="VERIFICATION",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                receiver_native_disposition_observed=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertFalse(result.maturity_credit)
        self.assertIn("SINGLE_SUCCESS_OR_RETURN_IS_NOT_MATURITY_PROOF", result.reasons)

    def test_maturity_credit_requires_behavior_suppression_and_retest(self) -> None:
        result = assess_cross_pole_feedback(
            CrossPoleFeedbackInput(
                source_pole="OBSERVATORY",
                receiver_pole="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                receiver_native_disposition_observed=True,
                behavior_delta_observed=True,
                repeat_failure_suppressed=True,
                retested=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.disposition, FeedbackDisposition.READ_AFFECTED_SLICE)
        self.assertTrue(result.maturity_credit)


if __name__ == "__main__":
    unittest.main()
