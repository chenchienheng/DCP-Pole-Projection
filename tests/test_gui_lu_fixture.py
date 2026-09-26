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


if __name__ == "__main__":
    unittest.main()
