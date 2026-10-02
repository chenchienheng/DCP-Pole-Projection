import json
import unittest
from pathlib import Path


class TaskBoardControlRetirementTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "task-board-control-retirement.json").read_text())

    def test_taskboard_and_pulse_do_not_create_authority(self):
        payload = self.payload()
        self.assertFalse(payload["taskboard_is_current_authority"])
        self.assertFalse(payload["pulse_is_scheduler_authority"])
        self.assertFalse(payload["blocker_board_is_global_state"])

    def test_retired_control_surfaces_are_not_current(self):
        payload = self.payload()
        states = {item["path"]: item["state"] for item in payload["observed_dispositions"]}
        self.assertEqual(states["02_runtime-ops/task_follow_up.md"], "RETIRED_ABSENT")
        self.assertEqual(states["01_native-board/pulse_rollup.md"], "RETIRED_ABSENT")
        self.assertEqual(states["01_native-board/blockers.md"], "RETIRED_ABSENT")

    def test_current_rules_preserve_receiver_owned_closure(self):
        payload = self.payload()
        rules = set(payload["current_interpretation"])
        self.assertIn("WORK_ITEM_CARRIER_DOES_NOT_CREATE_CURRENT_OR_AUTHORITY", rules)
        self.assertIn("NO_ACTION_IS_A_LEGITIMATE_DECISION_AND_DOES_NOT_REQUIRE_WORK_CONTRACT", rules)
        self.assertIn("OUTPUT_OR_MERGE_OR_LEDGER_DOES_NOT_CLOSE_RECEIVER_DEBT", rules)
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])


if __name__ == "__main__":
    unittest.main()
