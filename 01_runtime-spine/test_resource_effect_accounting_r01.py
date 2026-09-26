import unittest

from resource_effect_accounting_r01 import (
    ResourceEffectDisposition,
    ResourceEffectObservation,
    assess_resource_effect,
)


def obs(oid="O1", **kw):
    base = dict(
        observation_id=oid,
        need_id="NEED-1",
        composition_id="COMP-1",
        qualification_sufficient=True,
        authority_valid=True,
        resource_units=1.0,
        evidence_gain=0.60,
        risk_before=0.50,
        risk_after=0.30,
        useful_effect=0.70,
        effect_observed=True,
        current_for_purpose=True,
    )
    base.update(kw)
    return ResourceEffectObservation(**base)


class ResourceEffectAccountingR01Tests(unittest.TestCase):
    def test_efficiency_cannot_override_failed_qualification(self):
        result = assess_resource_effect(
            obs(qualification_sufficient=False, resource_units=0.1, useful_effect=1.0)
        )
        self.assertEqual(result.disposition, ResourceEffectDisposition.QUALIFICATION_HOLD)

    def test_efficiency_cannot_override_invalid_authority(self):
        result = assess_resource_effect(
            obs(authority_valid=False, resource_units=0.1, useful_effect=1.0)
        )
        self.assertEqual(result.disposition, ResourceEffectDisposition.QUALIFICATION_HOLD)

    def test_resource_spend_without_observed_effect_is_not_value_proof(self):
        result = assess_resource_effect(obs(effect_observed=False, resource_units=10.0))
        self.assertEqual(result.disposition, ResourceEffectDisposition.EFFECT_UNPROVEN)

    def test_first_observation_is_baseline_not_quality_score(self):
        result = assess_resource_effect(obs())
        self.assertEqual(result.disposition, ResourceEffectDisposition.BASELINE)
        self.assertIsNone(result.marginal_resource)

    def test_more_resource_without_any_gain_is_dominated_candidate(self):
        baseline = obs("B", resource_units=1.0)
        candidate = obs(
            "C",
            composition_id="COMP-2",
            resource_units=10.0,
            evidence_gain=0.60,
            risk_after=0.30,
            useful_effect=0.70,
        )
        result = assess_resource_effect(candidate, baseline=baseline)
        self.assertEqual(result.disposition, ResourceEffectDisposition.DOMINATED_CANDIDATE)
        self.assertEqual(result.marginal_resource, 9.0)

    def test_more_resource_with_risk_reduction_is_not_automatically_dominated(self):
        baseline = obs("B", resource_units=1.0, risk_after=0.30)
        candidate = obs(
            "C",
            composition_id="COMP-2",
            resource_units=2.0,
            risk_after=0.10,
        )
        result = assess_resource_effect(candidate, baseline=baseline)
        self.assertEqual(result.disposition, ResourceEffectDisposition.MARGINAL_GAIN_CANDIDATE)
        self.assertGreater(result.marginal_risk_reduction, 0)

    def test_less_resource_same_effect_is_recorded_without_global_winner_claim(self):
        baseline = obs("B", resource_units=2.0)
        candidate = obs("C", composition_id="COMP-2", resource_units=1.0)
        result = assess_resource_effect(candidate, baseline=baseline)
        self.assertEqual(result.disposition, ResourceEffectDisposition.MARGINAL_GAIN_CANDIDATE)
        self.assertEqual(result.marginal_resource, -1.0)
        self.assertEqual(result.marginal_useful_effect, 0.0)

    def test_cross_need_baseline_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_resource_effect(
                obs("C"),
                baseline=obs("B", need_id="OTHER-NEED"),
            )


if __name__ == "__main__":
    unittest.main()
