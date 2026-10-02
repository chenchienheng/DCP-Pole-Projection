import unittest

from dcp_kernel.models import ReturnState
from dcp_kernel.return_state import IllegalReturnTransition, ReturnClosure


class FalseCompletionGuardTests(unittest.TestCase):
    def test_output_only_remains_produced_with_receiver_debt(self):
        closure = ReturnClosure(return_id="RET-OUTPUT", receiver="NativeReceiver")
        self.assertEqual(closure.state, ReturnState.PRODUCED)
        self.assertIn("READ_DEBT", closure.outstanding_debt)
        self.assertIn("REBUILD_DEBT", closure.outstanding_debt)
        self.assertIn("RETEST_DEBT", closure.outstanding_debt)

    def test_pr_or_merge_metadata_cannot_skip_receiver_read(self):
        closure = ReturnClosure(return_id="RET-MERGE", receiver="NativeReceiver")
        routed = closure.advance(ReturnState.ROUTED)
        with self.assertRaises(IllegalReturnTransition):
            routed.advance(ReturnState.RECONCILED)

    def test_ledger_written_cannot_claim_actual_read_without_receiver_evidence(self):
        closure = ReturnClosure(return_id="RET-LEDGER", receiver="NativeReceiver")
        routed = closure.advance(ReturnState.ROUTED)
        with self.assertRaises(IllegalReturnTransition):
            routed.advance(ReturnState.ACTUAL_READ, receiver_actual_read=False)

    def test_rebuild_requires_applied_rebuild_or_explicit_reason(self):
        closure = ReturnClosure(return_id="RET-REBUILD", receiver="NativeReceiver")
        closure = closure.advance(ReturnState.ROUTED)
        closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        closure = closure.advance(ReturnState.RECEIVER_NATIVE_DISPOSITION, native_disposition="ABSORB")
        closure = closure.advance(ReturnState.RECONCILED)
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON)

    def test_behavior_and_retest_require_observed_evidence(self):
        closure = ReturnClosure(return_id="RET-BEHAVIOR", receiver="NativeReceiver")
        closure = closure.advance(ReturnState.ROUTED)
        closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        closure = closure.advance(ReturnState.RECEIVER_NATIVE_DISPOSITION, native_disposition="ABSORB")
        closure = closure.advance(ReturnState.RECONCILED)
        closure = closure.advance(
            ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
            rebuild_applied=True,
        )
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.BEHAVIOR_DELTA_OBSERVED, behavior_delta_observed=False)


if __name__ == "__main__":
    unittest.main()
