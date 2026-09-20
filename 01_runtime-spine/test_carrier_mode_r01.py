import unittest

from carrier_mode_r01 import (
    CarrierModeDisposition,
    CarrierModeObservation,
    assess_carrier_mode,
)


class CarrierModeR01Tests(unittest.TestCase):
    def test_world_observation_is_mismatch_not_cause_claim(self):
        obs = CarrierModeObservation(
            conversation_id="6aaec0ac-0a44-83ee-8121-568cb66d83ac",
            stable_responsibility="QINYI_WORLD_MODELING_CONTINUITY",
            observed_surface_mode="WORK",
            cloud_browser_entitled=False,
            background_or_delegated_entitled=False,
            work_codex_usage_attributed=None,
            user_initiated_work_switch=False,
            same_conversation_lineage=True,
        )
        result = assess_carrier_mode(obs)
        self.assertEqual(result.disposition, CarrierModeDisposition.MODE_CAPABILITY_MISMATCH)
        self.assertFalse(result.cause_proven)
        self.assertIn("USAGE_POOL_REMAINS_INDEPENDENT_EVIDENCE", result.reasons)

    def test_work_metering_without_full_entitlement_is_usage_risk(self):
        obs = CarrierModeObservation(
            conversation_id="specimen",
            stable_responsibility="WORLD",
            observed_surface_mode="WORK",
            cloud_browser_entitled=False,
            background_or_delegated_entitled=False,
            work_codex_usage_attributed=True,
            user_initiated_work_switch=False,
            same_conversation_lineage=True,
        )
        result = assess_carrier_mode(obs)
        self.assertEqual(result.disposition, CarrierModeDisposition.USAGE_ATTRIBUTION_RISK)
        self.assertFalse(result.cause_proven)

    def test_chat_without_work_metering_is_consistent(self):
        obs = CarrierModeObservation(
            conversation_id="specimen",
            stable_responsibility="WORLD",
            observed_surface_mode="CHAT",
            cloud_browser_entitled=None,
            background_or_delegated_entitled=None,
            work_codex_usage_attributed=False,
            user_initiated_work_switch=None,
            same_conversation_lineage=True,
        )
        result = assess_carrier_mode(obs)
        self.assertEqual(result.disposition, CarrierModeDisposition.CONSISTENT_CHAT)


if __name__ == "__main__":
    unittest.main()
