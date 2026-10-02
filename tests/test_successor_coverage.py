from __future__ import annotations

import json
import unittest
from pathlib import Path

from dcp_kernel import (
    CoverageState,
    Decision,
    SuccessorCoverageInput,
    assess_successor_coverage,
)


class SuccessorCoverageTests(unittest.TestCase):
    def test_unknown_dependency_audit_is_hold_not_failure(self) -> None:
        result = assess_successor_coverage(
            SuccessorCoverageInput(
                artifact_path="WORLD_CHAIN_MASTER_AXIS.md",
                successor_id=None,
                successor_executable_or_machine=False,
                caller_audit_complete=False,
                rebuild_audit_complete=False,
                unique_evidence=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, CoverageState.AUDIT_INCOMPLETE)
        self.assertFalse(result.destructive_action_authorized)

    def test_proven_live_dependency_without_successor_is_zombie(self) -> None:
        result = assess_successor_coverage(
            SuccessorCoverageInput(
                artifact_path="legacy-runtime.md",
                successor_id=None,
                successor_executable_or_machine=False,
                active_callers=("current-reader",),
                caller_audit_complete=True,
                rebuild_audit_complete=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, CoverageState.ZOMBIE_DEPENDENCY)
        self.assertTrue(result.normal_reader_eligible)
        self.assertFalse(result.destructive_action_authorized)

    def test_successor_exists_but_reader_wake_remains_partial(self) -> None:
        result = assess_successor_coverage(
            SuccessorCoverageInput(
                artifact_path="LIFECYCLE_DEPENDENCY_CHAIN_KERNEL.md",
                successor_id="dcp_kernel/platform.py",
                successor_executable_or_machine=True,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                unique_evidence=True,
                normal_reader_wake=True,
                current_routing_reference=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, CoverageState.PARTIAL_READER_WITHDRAWAL)
        self.assertTrue(result.normal_reader_eligible)

    def test_evidence_without_successor_is_not_called_covered(self) -> None:
        result = assess_successor_coverage(
            SuccessorCoverageInput(
                artifact_path="COMMANDER_CARD_v0_1.md",
                successor_id=None,
                successor_executable_or_machine=False,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                unique_evidence=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, CoverageState.EVIDENCE_ONLY_NO_SUCCESSOR)
        self.assertFalse(result.normal_reader_eligible)

    def test_covered_unique_evidence_keeps_lineage_without_reader_wake(self) -> None:
        result = assess_successor_coverage(
            SuccessorCoverageInput(
                artifact_path="RECOMPOSITION_ENGINE_v0_1.md",
                successor_id="dcp_kernel/platform.py",
                successor_executable_or_machine=True,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                unique_evidence=True,
                normal_reader_wake=False,
                current_routing_reference=False,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, CoverageState.COVERED_EVIDENCE_ONLY)
        self.assertFalse(result.normal_reader_eligible)
        self.assertFalse(result.destructive_action_authorized)

    def test_seed_fixture_expected_states(self) -> None:
        path = Path("fixtures/repository/legacy-successor-coverage-seed.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload["items"]:
            expected = item.pop("expected_state")
            result = assess_successor_coverage(
                SuccessorCoverageInput(**item)
            )
            self.assertEqual(result.state.value, expected, item["artifact_path"])
            self.assertFalse(result.destructive_action_authorized)


if __name__ == "__main__":
    unittest.main()
