from __future__ import annotations

import json
import unittest
from pathlib import Path

from dcp_kernel import Decision, EvidenceMode, OwnerExitEvidence, assess_owner_exit_evidence


class GuiLuProducerReturnTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "gui-lu" / "mobility-envelope-producer-return.json").read_text())

    def test_producer_fixture_exposes_receiver_debt(self):
        payload = self.payload()
        assertions = payload["producer_can_assert"]
        self.assertTrue(assertions["return_produced"])
        self.assertTrue(assertions["receiver_routed"])
        self.assertFalse(assertions["receiver_actual_read"])
        self.assertFalse(assertions["native_disposition_recorded"])
        self.assertFalse(assertions["behavior_delta_observed"])
        self.assertFalse(payload["autonomy_proven"])
        self.assertIn("RETESTED", payload["receiver_native_debt"])

    def test_producer_projection_cannot_prove_native_absorption(self):
        payload = self.payload()
        assertions = payload["producer_can_assert"]
        result = assess_owner_exit_evidence(OwnerExitEvidence(
            evidence_id=payload["return_id"],
            receiver=payload["receiver"],
            mode=EvidenceMode.OBSERVED_PROJECTION,
            receiver_actual_read=assertions["receiver_actual_read"],
            native_disposition_recorded=assertions["native_disposition_recorded"],
            rebuild_applied_or_reasoned=assertions["rebuild_applied_or_reasoned"],
            behavior_delta_observed=assertions["behavior_delta_observed"],
            retested=assertions["retested"],
            manual_interventions=tuple(payload["manual_interventions"]),
        ))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "A0_NOT_READ")
        self.assertFalse(result.proves_receiver_absorption)
        self.assertFalse(result.proves_behavior_change)
        self.assertFalse(result.proves_retest)


if __name__ == "__main__":
    unittest.main()
