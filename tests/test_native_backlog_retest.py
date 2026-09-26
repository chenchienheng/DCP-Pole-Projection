from __future__ import annotations

import unittest

from dcp_kernel.models import (
    CurrentCandidate,
    CurrentResolutionStatus,
    LifecycleState,
    ReturnState,
)
from dcp_kernel.resolution import compute_affected_cone, resolve_current
from dcp_kernel.return_state import IllegalReturnTransition, ReturnClosure


class CurrentResolverRetest(unittest.TestCase):
    def candidate(
        self,
        revision: str,
        *,
        lifecycle: LifecycleState = LifecycleState.CANDIDATE,
        successor_of: str | None = "r1",
        authority: bool = True,
        evidence: bool = True,
        reconciled: bool = True,
        reader: bool = True,
        timestamp: str = "2026-08-28T00:00:00Z",
    ) -> CurrentCandidate:
        return CurrentCandidate(
            stable_life_id="XUANLING",
            revision=revision,
            lifecycle_state=lifecycle,
            successor_of=successor_of,
            authority_valid=authority,
            evidence_valid=evidence,
            receiver_reconciled=reconciled,
            reader_eligible=reader,
            timestamp=timestamp,
        )

    def test_newer_timestamp_cannot_beat_valid_successor(self) -> None:
        valid = self.candidate("r2", timestamp="2026-01-01T00:00:00Z")
        newer_but_invalid = self.candidate(
            "r999",
            successor_of=None,
            timestamp="2099-01-01T00:00:00Z",
        )
        result = resolve_current("XUANLING", "r1", (newer_but_invalid, valid))
        self.assertEqual(result.status, CurrentResolutionStatus.CURRENT)
        self.assertEqual(result.selected_revision, "r2")
        self.assertIn("SUCCESSOR_RELATION_MISSING", result.rejected["r999"])

    def test_unreconciled_successor_cannot_become_current(self) -> None:
        result = resolve_current(
            "XUANLING",
            "r1",
            (self.candidate("r2", reconciled=False),),
        )
        self.assertEqual(result.status, CurrentResolutionStatus.HOLD)
        self.assertIsNone(result.selected_revision)
        self.assertIn("RECEIVER_RECONCILIATION_MISSING", result.rejected["r2"])

    def test_two_valid_direct_successors_conflict(self) -> None:
        result = resolve_current(
            "XUANLING",
            "r1",
            (self.candidate("r2a"), self.candidate("r2b")),
        )
        self.assertEqual(result.status, CurrentResolutionStatus.CONFLICT)
        self.assertIsNone(result.selected_revision)
        self.assertIn("MULTIPLE_VALID_DIRECT_SUCCESSORS", result.reasons)


class AffectedConeRetest(unittest.TestCase):
    def test_only_dependency_reachable_eligible_receivers_wake(self) -> None:
        graph = {
            "signal": ("dep-a", "visible-only"),
            "dep-a": ("receiver-dcp", "dep-b"),
            "dep-b": ("receiver-glmodel", "signal"),
            "visible-only": (),
        }
        result = compute_affected_cone(
            ("signal",),
            graph,
            {"receiver-dcp", "receiver-glmodel"},
        )
        self.assertEqual(result.affected, ("receiver-dcp", "receiver-glmodel"))
        self.assertEqual(result.excluded["dep-a"], "RECEIVER_NOT_ELIGIBLE")
        self.assertEqual(result.excluded["dep-b"], "RECEIVER_NOT_ELIGIBLE")
        self.assertEqual(result.excluded["visible-only"], "RECEIVER_NOT_ELIGIBLE")

    def test_unrelated_eligible_receiver_is_not_broadcast(self) -> None:
        result = compute_affected_cone(
            ("signal",),
            {"signal": ("receiver-dcp",)},
            {"receiver-dcp", "receiver-ideas"},
        )
        self.assertEqual(result.affected, ("receiver-dcp",))
        self.assertNotIn("receiver-ideas", result.affected)


class ReturnClosureRetest(unittest.TestCase):
    def test_illegal_skip_is_rejected(self) -> None:
        closure = ReturnClosure(return_id="RET-1", receiver="DCP")
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)

    def test_receiver_read_and_disposition_are_required(self) -> None:
        closure = ReturnClosure(return_id="RET-2", receiver="DCP")
        closure = closure.advance(ReturnState.ROUTED)
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.ACTUAL_READ)

        closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.RECEIVER_NATIVE_DISPOSITION)

    def test_full_closure_reaches_retested_without_debt(self) -> None:
        closure = ReturnClosure(return_id="RET-3", receiver="DCP")
        closure = closure.advance(ReturnState.ROUTED)
        closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        closure = closure.advance(
            ReturnState.RECEIVER_NATIVE_DISPOSITION,
            native_disposition="ABSORBABLE_MATERIAL_DELTA",
        )
        closure = closure.advance(ReturnState.RECONCILED)
        closure = closure.advance(
            ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
            rebuild_applied=True,
        )
        closure = closure.advance(
            ReturnState.BEHAVIOR_DELTA_OBSERVED,
            behavior_delta_observed=True,
        )
        closure = closure.advance(ReturnState.RETESTED, retested=True)

        self.assertEqual(closure.outstanding_debt, ())
        self.assertEqual(closure.autonomy_level, "A4_RETESTED")

    def test_manual_intervention_remains_visible_after_retest(self) -> None:
        closure = ReturnClosure(
            return_id="RET-4",
            receiver="DCP",
            manual_interventions=("OWNER_ROUTED_RECEIVER",),
        )
        closure = closure.advance(ReturnState.ROUTED)
        closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        closure = closure.advance(
            ReturnState.RECEIVER_NATIVE_DISPOSITION,
            native_disposition="NO_NATIVE_DELTA",
        )
        closure = closure.advance(ReturnState.RECONCILED)
        closure = closure.advance(
            ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
            no_rebuild_reason="NO_NATIVE_DELTA",
        )
        closure = closure.advance(
            ReturnState.BEHAVIOR_DELTA_OBSERVED,
            behavior_delta_observed=True,
        )
        closure = closure.advance(ReturnState.RETESTED, retested=True)
        self.assertEqual(closure.autonomy_level, "A0_MANUAL_PROMPT_DEPENDENT")


if __name__ == "__main__":
    unittest.main()
