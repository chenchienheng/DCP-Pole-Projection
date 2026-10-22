import unittest

from field_feedback_r01 import (
    FeedbackDisposition,
    LocalFieldObservation,
    project_field_feedback,
)


def field_obs(oid, subject, **kw):
    base = dict(
        observation_id=oid,
        local_subject_id=subject,
        product_family="TIRE-FAMILY-X",
        configuration_class="SIZE-A/PRESSURE-BAND-1",
        environment_class="WET/URBAN/MODERATE-TEMP",
        effect_name="wear_rate",
        effect_value=1.0,
        effect_unit="mm_per_10000km",
        outcome_class="NORMAL_WEAR",
        evidence_method="LOCAL_SENSOR_PLUS_INSPECTION",
        confidence=0.92,
        current_for_purpose=True,
        return_authorized=True,
        contains_raw_private_payload=False,
    )
    base.update(kw)
    return LocalFieldObservation(**base)


class FieldFeedbackR01Tests(unittest.TestCase):
    def test_two_different_local_histories_can_form_generalized_candidate(self):
        result = project_field_feedback((
            field_obs("O1", "USER-LOCAL-A", effect_value=0.9),
            field_obs("O2", "USER-LOCAL-B", effect_value=1.1),
        ))
        self.assertEqual(result.disposition, FeedbackDisposition.GENERALIZABLE_CANDIDATE)
        self.assertEqual(result.nutrient.sample_count, 2)
        self.assertAlmostEqual(result.nutrient.mean_effect_value, 1.0)
        self.assertFalse(hasattr(result.nutrient, "local_subject_id"))
        self.assertIn("RAW_CUSTOMER_HISTORY_NOT_REQUIRED", result.reasons)

    def test_raw_private_payload_stays_local_even_when_return_is_authorized(self):
        result = project_field_feedback((
            field_obs("O1", "USER-LOCAL-A", contains_raw_private_payload=True),
            field_obs("O2", "USER-LOCAL-B"),
        ))
        self.assertEqual(result.disposition, FeedbackDisposition.LOCAL_ONLY)
        self.assertIsNone(result.nutrient)

    def test_no_return_authority_stays_local(self):
        result = project_field_feedback((
            field_obs("O1", "USER-LOCAL-A", return_authorized=False),
            field_obs("O2", "USER-LOCAL-B"),
        ))
        self.assertEqual(result.disposition, FeedbackDisposition.LOCAL_ONLY)

    def test_different_environment_cohorts_do_not_get_averaged_together(self):
        result = project_field_feedback((
            field_obs("O1", "USER-LOCAL-A"),
            field_obs("O2", "USER-LOCAL-B", environment_class="DRY/HIGHWAY/HOT"),
        ))
        self.assertEqual(result.disposition, FeedbackDisposition.CONFLICT_HOLD)

    def test_low_confidence_field_observation_does_not_promote(self):
        result = project_field_feedback((
            field_obs("O1", "USER-LOCAL-A", confidence=0.60),
            field_obs("O2", "USER-LOCAL-B"),
        ))
        self.assertEqual(result.disposition, FeedbackDisposition.INSUFFICIENT_EVIDENCE)

    def test_one_user_history_is_not_generalized_by_default(self):
        result = project_field_feedback((
            field_obs("O1", "USER-LOCAL-A"),
        ))
        self.assertEqual(result.disposition, FeedbackDisposition.INSUFFICIENT_EVIDENCE)


if __name__ == "__main__":
    unittest.main()
