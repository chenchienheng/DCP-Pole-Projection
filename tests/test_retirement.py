from __future__ import annotations

import json
import unittest
from pathlib import Path

from dcp_kernel.models import Decision
from dcp_kernel.retirement import (
    RetirementInput,
    RetirementState,
    assess_retirement,
)


class RetirementTests(unittest.TestCase):
    def test_absent_predecessor_with_successor_and_provenance_is_not_revived(self) -> None:
        result = assess_retirement(
            RetirementInput(
                artifact_path="WORLD_CHAIN_MASTER_AXIS.md",
                artifact_present=False,
                provenance_retained=True,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
                successor_pointer="WORLD_RELATION_LINEAGE_SPECIMEN.md+dcp_kernel/transition.py",
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(
            result.state,
            RetirementState.PHYSICALLY_RETIRED_PROVENANCE_RETAINED,
        )
        self.assertFalse(result.normal_reader_eligible)
        self.assertFalse(result.destructive_action_authorized)

    def test_absent_predecessor_with_proven_live_reference_is_failure(self) -> None:
        result = assess_retirement(
            RetirementInput(
                artifact_path="legacy-runtime.md",
                artifact_present=False,
                provenance_retained=True,
                active_reference=True,
                caller_audit_complete=True,
                rebuild_audit_complete=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, RetirementState.BROKEN_LIVE_REFERENCE)

    def test_unknown_retirement_dependencies_remain_hold(self) -> None:
        result = assess_retirement(
            RetirementInput(
                artifact_path="legacy-unknown.md",
                artifact_present=False,
                provenance_retained=True,
                caller_audit_complete=False,
                rebuild_audit_complete=False,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, RetirementState.RETIREMENT_AUDIT_INCOMPLETE)

    def test_present_artifact_is_not_claimed_retired(self) -> None:
        result = assess_retirement(
            RetirementInput(
                artifact_path="SCHEDULING_EFFECT_REGISTER.md",
                artifact_present=True,
                provenance_retained=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, RetirementState.ACTIVE_ARTIFACT)

    def test_branch_observation_fixture_matches_retirement_states(self) -> None:
        payload = json.loads(
            Path("fixtures/repository/physical-retirement-observations.json").read_text(
                encoding="utf-8"
            )
        )
        for raw in payload["items"]:
            item = dict(raw)
            expected = item.pop("expected_state")
            result = assess_retirement(RetirementInput(**item))
            self.assertEqual(result.state.value, expected, raw["artifact_path"])
            self.assertFalse(result.destructive_action_authorized)


if __name__ == "__main__":
    unittest.main()
