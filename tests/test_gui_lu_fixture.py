from __future__ import annotations

import json
import unittest
from pathlib import Path

from dcp_kernel import Decision
from dcp_kernel.fixtures import run_platform_fixture


class GuiLuFixtureTests(unittest.TestCase):
    def test_mobility_envelope_fixture_completes_same_life_loop(self) -> None:
        path = (
            Path(__file__).resolve().parents[1]
            / "fixtures"
            / "gui-lu"
            / "mobility-envelope-intrusion.json"
        )
        payload = json.loads(path.read_text())
        result = run_platform_fixture(payload)
        expected = payload["expected"]

        self.assertEqual(
            result.plan.decision.value,
            expected["plan_decision"],
        )
        self.assertEqual(
            result.loop.decision.value,
            expected["loop_decision"],
        )
        self.assertEqual(
            result.plan.current.selected_revision,
            expected["selected_current_revision"],
        )
        self.assertEqual(result.loop.decision, Decision.PASS)
        self.assertIsNotNone(result.loop.reentry)
        self.assertEqual(
            result.loop.reentry.current_revision,
            expected["reentry_current_revision"],
        )
        self.assertEqual(
            result.loop.reentry.last_good_revision,
            expected["reentry_last_good_revision"],
        )
        self.assertEqual(
            list(result.loop.reentry.pending_returns),
            expected["pending_returns"],
        )
        self.assertEqual(result.loop.closure.manual_interventions, ())


    def _payload(self) -> dict:
        path = (Path(__file__).resolve().parents[1] / "fixtures" / "gui-lu"
                / "mobility-envelope-intrusion.json")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_supplied_progression_and_reentry_metadata_are_preserved(self) -> None:
        payload = self._payload()
        payload["return"]["manual_interventions"] = ["FIXTURE_MANUAL_STEP"]
        result = run_platform_fixture(payload)
        self.assertEqual(result.loop.closure.return_id, payload["return"]["return_id"])
        self.assertEqual(result.loop.closure.native_disposition, "REBUILD_REQUIRED")
        self.assertEqual(result.loop.closure.manual_interventions, ("FIXTURE_MANUAL_STEP",))
        self.assertEqual(result.loop.closure.autonomy_level, "A0_MANUAL_PROMPT_DEPENDENT")
        self.assertEqual(result.loop.reentry.tri_root_revision, "WORLD-R3")
        self.assertEqual(result.loop.reentry.cursor, "GUI-LU-CURSOR-R3")
        self.assertEqual(result.loop.reentry.ack_owner, "GLMODEL")

    def test_missing_rebuild_is_not_synthesized(self) -> None:
        payload = self._payload()
        payload["return"]["progression"] = payload["return"]["progression"][:5]
        with self.assertRaisesRegex(ValueError, "REENTRY_REQUIRES_RECEIVER_REBUILD_RESOLUTION"):
            run_platform_fixture(payload)

    def test_missing_retest_remains_hold_with_reentry_debt(self) -> None:
        payload = self._payload()
        payload["return"]["progression"].pop()
        result = run_platform_fixture(payload)
        self.assertEqual(result.loop.decision, Decision.HOLD)
        self.assertFalse(result.loop.closure.retested)
        self.assertIn("RETEST_DEBT", result.loop.reasons)
        self.assertIn("RETEST_DEBT", result.loop.reentry.blockers)

    def test_failed_plan_cannot_produce_reentry(self) -> None:
        payload = self._payload()
        payload["capability_candidates"][0]["authority_granted"] = False
        result = run_platform_fixture(payload)
        self.assertNotEqual(result.plan.decision, Decision.PASS)
        self.assertEqual(result.loop.decision, result.plan.decision)
        self.assertIsNone(result.loop.reentry)
        self.assertIn("WORK_CONTRACT_NOT_AVAILABLE", result.loop.reasons)


if __name__ == "__main__":
    unittest.main()
