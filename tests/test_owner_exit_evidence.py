from __future__ import annotations

import unittest

from dcp_kernel import (
    Decision,
    EvidenceMode,
    OwnerExitEvidence,
    assess_owner_exit_evidence,
)


class OwnerExitEvidenceTests(unittest.TestCase):
    def test_synthetic_fixture_never_proves_receiver_behavior(self) -> None:
        result = assess_owner_exit_evidence(
            OwnerExitEvidence(
                evidence_id="SYN-1",
                receiver="GLMODEL",
                mode=EvidenceMode.SYNTHETIC_FIXTURE,
                receiver_actual_read=True,
                native_disposition_recorded=True,
                rebuild_applied_or_reasoned=True,
                behavior_delta_observed=True,
                retested=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "SIMULATION_ONLY")
        self.assertFalse(result.proves_receiver_absorption)
        self.assertFalse(result.proves_behavior_change)
        self.assertFalse(result.proves_retest)

    def test_projection_observation_cannot_promote_native_absorption(self) -> None:
        result = assess_owner_exit_evidence(
            OwnerExitEvidence(
                evidence_id="OBS-1",
                receiver="GLMODEL",
                mode=EvidenceMode.OBSERVED_PROJECTION,
                receiver_actual_read=True,
                native_disposition_recorded=True,
                rebuild_applied_or_reasoned=True,
                behavior_delta_observed=True,
                retested=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "A1_ROUTED")
        self.assertFalse(result.proves_receiver_absorption)

    def test_native_evidence_stops_at_first_missing_stage(self) -> None:
        result = assess_owner_exit_evidence(
            OwnerExitEvidence(
                evidence_id="NATIVE-1",
                receiver="GLMODEL",
                mode=EvidenceMode.RECEIVER_NATIVE,
                receiver_actual_read=True,
                native_disposition_recorded=True,
                rebuild_applied_or_reasoned=True,
                behavior_delta_observed=False,
                retested=False,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "A2_ABSORBED")
        self.assertTrue(result.proves_receiver_absorption)
        self.assertFalse(result.proves_behavior_change)
        self.assertIn("BEHAVIOR_DELTA_NOT_OBSERVED", result.reasons)

    def test_complete_native_loop_reaches_a4_not_a5(self) -> None:
        result = assess_owner_exit_evidence(
            OwnerExitEvidence(
                evidence_id="NATIVE-2",
                receiver="GLMODEL",
                mode=EvidenceMode.RECEIVER_NATIVE,
                receiver_actual_read=True,
                native_disposition_recorded=True,
                rebuild_applied_or_reasoned=True,
                behavior_delta_observed=True,
                retested=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.autonomy_level, "A4_RETESTED")
        self.assertTrue(result.proves_receiver_absorption)
        self.assertTrue(result.proves_behavior_change)
        self.assertTrue(result.proves_retest)

    def test_manual_intervention_forces_a0(self) -> None:
        result = assess_owner_exit_evidence(
            OwnerExitEvidence(
                evidence_id="NATIVE-3",
                receiver="GLMODEL",
                mode=EvidenceMode.RECEIVER_NATIVE,
                receiver_actual_read=True,
                native_disposition_recorded=True,
                rebuild_applied_or_reasoned=True,
                behavior_delta_observed=True,
                retested=True,
                manual_interventions=("VITAS_REMINDER_READ_RETURN",),
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "A0_MANUAL_PROMPT_DEPENDENT")


if __name__ == "__main__":
    unittest.main()
