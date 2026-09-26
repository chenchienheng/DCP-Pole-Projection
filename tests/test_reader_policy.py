from __future__ import annotations

import unittest

from dcp_kernel.reader_policy import (
    ReaderDisposition,
    ReaderRequest,
    assess_reader_request,
)
from dcp_kernel.models import Decision


class ReaderPolicyTests(unittest.TestCase):
    def test_current_surface_reads_without_historical_path(self) -> None:
        result = assess_reader_request(
            ReaderRequest(
                stable_identity_known=True,
                authority_scope_known=True,
                lifecycle_state_known=True,
                receiver_affected=True,
                material_delta=True,
                current_surface=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.disposition, ReaderDisposition.READ_CURRENT)
        self.assertFalse(result.whole_body_read_allowed)

    def test_no_material_delta_does_not_wake_receiver(self) -> None:
        result = assess_reader_request(
            ReaderRequest(
                stable_identity_known=True,
                authority_scope_known=True,
                lifecycle_state_known=True,
                receiver_affected=True,
                material_delta=False,
            )
        )
        self.assertEqual(result.disposition, ReaderDisposition.NO_WAKE)

    def test_conflict_escalates_bounded_only(self) -> None:
        result = assess_reader_request(
            ReaderRequest(
                stable_identity_known=True,
                authority_scope_known=True,
                lifecycle_state_known=True,
                receiver_affected=True,
                material_delta=True,
                conflict=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, ReaderDisposition.ESCALATE_BOUNDED)
        self.assertFalse(result.whole_body_read_allowed)

    def test_historical_reentry_requires_explicit_purpose(self) -> None:
        result = assess_reader_request(
            ReaderRequest(
                stable_identity_known=True,
                authority_scope_known=True,
                lifecycle_state_known=True,
                receiver_affected=True,
                material_delta=True,
                historical=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, ReaderDisposition.HOLD)

    def test_native_body_copy_is_contamination_failure(self) -> None:
        result = assess_reader_request(
            ReaderRequest(
                stable_identity_known=True,
                authority_scope_known=True,
                lifecycle_state_known=True,
                receiver_affected=True,
                material_delta=True,
                native_body_copy_requested=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)


if __name__ == "__main__":
    unittest.main()
