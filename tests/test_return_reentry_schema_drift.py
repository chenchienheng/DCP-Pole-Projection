from __future__ import annotations

import unittest

from dcp_kernel.models import (
    AffectedCone,
    CapabilityResolution,
    CurrentResolution,
    CurrentResolutionStatus,
    Decision,
    InvariantCore,
    ReturnState,
    StableLife,
    TriRootState,
)
from dcp_kernel.platform import (
    PlatformPlan,
    WorkContract,
    build_reentry_state,
    complete_fixture_loop,
)
from dcp_kernel.return_state import ReturnClosure


class ReturnReentrySchemaDriftTests(unittest.TestCase):
    def life(self) -> StableLife:
        return StableLife(
            life_id="SUBJECT-1",
            invariant_core=InvariantCore("SUBJECT-1", "preserve subject", "WORLD-1"),
            native_owner="Receiver",
            current_revision="R1",
            last_good_revision="R1",
        )

    def tri(self) -> TriRootState:
        return TriRootState(
            meaning_preserved=True,
            dependencies_resolved=True,
            world_id="WORLD-1",
            source_revision="R1",
        )

    def test_build_reentry_uses_current_model_schema(self) -> None:
        closure = ReturnClosure(return_id="RET-1", receiver="Receiver")
        closure = closure.advance(ReturnState.ROUTED)
        closure = closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        closure = closure.advance(
            ReturnState.RECEIVER_NATIVE_DISPOSITION,
            native_disposition="USE",
        )
        closure = closure.advance(ReturnState.RECONCILED)
        closure = closure.advance(
            ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
            rebuild_applied=True,
        )

        reentry = build_reentry_state(
            stable_life=self.life(),
            tri_root=self.tri(),
            closure=closure,
            receiver_rebuild_revision="R2",
        )

        self.assertEqual(reentry.tri_root_revision, "R1")
        self.assertEqual(reentry.current_revision, "R2")
        self.assertEqual(reentry.ack_owner, "Receiver")
        self.assertIn("BEHAVIOR_DELTA_DEBT", reentry.blockers)
        self.assertIn("RETEST_DEBT", reentry.blockers)

    def test_complete_fixture_loop_reaches_retested_and_reentry(self) -> None:
        plan = PlatformPlan(
            decision=Decision.PASS,
            current=CurrentResolution(
                status=CurrentResolutionStatus.CURRENT,
                selected_revision="R1",
            ),
            capability=CapabilityResolution(
                decision=Decision.PASS,
                binding=None,
            ),
            affected_cone=AffectedCone(affected=("Receiver",), excluded={}),
            transition=None,
            work_contract=WorkContract(
                contract_id="WORK-1",
                stable_life_id="SUBJECT-1",
                transition_id="T-1",
                capability_id="CAP-1",
                actor_id="Actor",
                carrier_id="Carrier",
                receiver="Receiver",
                affected_receivers=("Receiver",),
            ),
        )

        result = complete_fixture_loop(
            plan=plan,
            return_id="RET-2",
            receiver="Receiver",
            stable_life=self.life(),
            tri_root=self.tri(),
            rebuilt_revision="R2",
        )

        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.closure.state, ReturnState.RETESTED)
        self.assertEqual(result.closure.outstanding_debt, ())
        self.assertIsNotNone(result.reentry)
        self.assertEqual(result.reentry.current_revision, "R2")
        self.assertEqual(result.reentry.blockers, ())


if __name__ == "__main__":
    unittest.main()
