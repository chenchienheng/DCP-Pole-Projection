from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.schedule_effect import (
    ScheduleEffectInput,
    ScheduleEffectState,
    TriggerClass,
    assess_schedule_effect,
)


class ScheduleEffectTests(unittest.TestCase):
    def test_named_periodic_schedule_without_effect_evidence_is_hold(self) -> None:
        result = assess_schedule_effect(
            ScheduleEffectInput(
                schedule_id="SCH-1",
                trigger_class=TriggerClass.PERIODIC,
                receiver="DCP",
                expected_effect="produce bounded reconciliation check",
                effect_evidence_present=False,
                return_target="DCP",
                return_reconciled=False,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(
            result.state,
            ScheduleEffectState.HOLD_MISSING_EFFECT_EVIDENCE,
        )

    def test_output_without_return_reconciliation_is_incomplete(self) -> None:
        result = assess_schedule_effect(
            ScheduleEffectInput(
                schedule_id="SCH-2",
                trigger_class=TriggerClass.EVENT_DRIVEN,
                receiver="GLMODEL",
                expected_effect="route mobility failure",
                effect_evidence_present=True,
                return_target="GLMODEL",
                return_reconciled=False,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, ScheduleEffectState.HOLD_RETURN_INCOMPLETE)

    def test_trigger_class_does_not_grant_mutation_authority(self) -> None:
        result = assess_schedule_effect(
            ScheduleEffectInput(
                schedule_id="SCH-3",
                trigger_class=TriggerClass.CONDITION_WATCH,
                receiver="DCP",
                expected_effect="update state",
                effect_evidence_present=True,
                mutation_requested=True,
                action_authority_valid=False,
                return_target="DCP",
                return_reconciled=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, ScheduleEffectState.HOLD_ACTION_AUTHORITY)

    def test_carrier_replacement_may_preserve_same_schedule_identity(self) -> None:
        result = assess_schedule_effect(
            ScheduleEffectInput(
                schedule_id="SCH-4",
                trigger_class=TriggerClass.PERIODIC,
                receiver="DCP",
                expected_effect="produce evidence",
                effect_evidence_present=True,
                mutation_requested=False,
                return_target="DCP",
                return_reconciled=True,
                prior_carrier_id="calendar-a",
                carrier_id="workflow-b",
                stable_schedule_identity_preserved=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, ScheduleEffectState.EFFECTIVE)
        self.assertTrue(result.effective)

    def test_carrier_change_that_breaks_identity_fails(self) -> None:
        result = assess_schedule_effect(
            ScheduleEffectInput(
                schedule_id="SCH-5",
                trigger_class=TriggerClass.MANUAL_GATED,
                receiver="DCP",
                expected_effect="review",
                effect_evidence_present=True,
                return_target="DCP",
                return_reconciled=True,
                prior_carrier_id="carrier-a",
                carrier_id="carrier-b",
                stable_schedule_identity_preserved=False,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, ScheduleEffectState.FAIL_IDENTITY_DRIFT)

    def test_mutation_outside_scope_fails_even_with_authority(self) -> None:
        result = assess_schedule_effect(
            ScheduleEffectInput(
                schedule_id="SCH-6",
                trigger_class=TriggerClass.EVENT_DRIVEN,
                receiver="DCP",
                expected_effect="bounded mutation",
                effect_evidence_present=True,
                mutation_requested=True,
                action_authority_valid=True,
                action_within_scope=False,
                return_target="DCP",
                return_reconciled=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, ScheduleEffectState.FAIL_SCOPE_VIOLATION)


if __name__ == "__main__":
    unittest.main()
