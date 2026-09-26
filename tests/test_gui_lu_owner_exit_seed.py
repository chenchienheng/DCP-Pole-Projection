import json
import unittest
from pathlib import Path

from dcp_kernel import Decision, EvidenceMode, OwnerExitEvidence, assess_owner_exit_evidence


FIXTURE = Path(__file__).parents[1] / "fixtures" / "gui-lu" / "mobility-envelope-owner-exit-observation.json"


class GuiLuOwnerExitSeedTests(unittest.TestCase):
    def load_evidence(self, **changes):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload = dict(
            evidence_id=data["evidence_id"],
            receiver=data["receiver"],
            mode=EvidenceMode(data["mode"]),
            receiver_actual_read=data["receiver_actual_read"],
            native_disposition_recorded=data["native_disposition_recorded"],
            rebuild_applied_or_reasoned=data["rebuild_applied_or_reasoned"],
            behavior_delta_observed=data["behavior_delta_observed"],
            retested=data["retested"],
            manual_interventions=tuple(data["manual_interventions"]),
        )
        payload.update(changes)
        return OwnerExitEvidence(**payload)

    def test_projection_seed_cannot_prove_absorption(self):
        result = assess_owner_exit_evidence(self.load_evidence())
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "A0_NOT_READ")
        self.assertFalse(result.proves_receiver_absorption)
        self.assertFalse(result.proves_behavior_change)
        self.assertFalse(result.proves_retest)

    def test_projection_mode_cannot_impersonate_native_even_if_flags_are_true(self):
        result = assess_owner_exit_evidence(self.load_evidence(
            receiver_actual_read=True,
            native_disposition_recorded=True,
            rebuild_applied_or_reasoned=True,
            behavior_delta_observed=True,
            retested=True,
        ))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.autonomy_level, "A1_ROUTED")
        self.assertFalse(result.proves_receiver_absorption)


if __name__ == "__main__":
    unittest.main()
