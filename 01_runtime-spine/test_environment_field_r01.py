import unittest

from environment_field_r01 import (
    CarrierReplacementEvidence,
    EnvironmentCarrier,
    EnvironmentFieldCandidate,
    EnvironmentFieldDisposition,
    qualify_carrier_replacement,
    qualify_environment_field,
)


def field(**changes):
    values = dict(
        field_id="FIELD-1",
        stable_need="NEED-1",
        carriers=(
            EnvironmentCarrier("DRIVE", frozenset({"CURRENT_RESOLUTION", "RETURN"})),
            EnvironmentCarrier("GITHUB", frozenset({"EXECUTABLE_EVIDENCE"})),
            EnvironmentCarrier("LIBRARY", frozenset({"DURABLE_REENTRY"})),
        ),
        claim_ceiling=frozenset({"CANDIDATE", "NOT_RUNTIME", "NO_GLOBAL_TOPOLOGY"}),
    )
    values.update(changes)
    return EnvironmentFieldCandidate(**values)


class EnvironmentFieldR01Tests(unittest.TestCase):
    def test_complementary_multi_carrier_field_qualifies(self):
        result = qualify_environment_field(field())
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.QUALIFIED_CANDIDATE)

    def test_one_carrier_is_not_an_environment_field(self):
        result = qualify_environment_field(field(carriers=(
            EnvironmentCarrier("ONE", frozenset({
                "CURRENT_RESOLUTION", "RETURN", "EXECUTABLE_EVIDENCE", "DURABLE_REENTRY"
            })),
        )))
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.HOLD)
        self.assertIn("MULTI_CARRIER_COMPOSITION_NOT_PROVEN", result.reasons)

    def test_carrier_cannot_promote_itself_to_authority(self):
        carriers = field().carriers + (
            EnvironmentCarrier("CLOUD", frozenset(), authority_claim=True),
        )
        result = qualify_environment_field(field(carriers=carriers))
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.HOLD)
        self.assertIn("CARRIER_AUTHORITY_PROMOTION_PROHIBITED", result.reasons)

    def test_missing_return_capability_holds(self):
        carriers = (
            EnvironmentCarrier("A", frozenset({"CURRENT_RESOLUTION"})),
            EnvironmentCarrier("B", frozenset({"EXECUTABLE_EVIDENCE", "DURABLE_REENTRY"})),
        )
        result = qualify_environment_field(field(carriers=carriers))
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.HOLD)
        self.assertTrue(any("RETURN" in reason for reason in result.reasons))

    def test_runtime_or_topology_ceiling_cannot_be_omitted(self):
        result = qualify_environment_field(field(claim_ceiling=frozenset({"CANDIDATE"})))
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.HOLD)
        self.assertIn("CLAIM_CEILING_INSUFFICIENT", result.reasons)

    def test_replacement_holds_until_all_live_bindings_are_requalified(self):
        evidence = CarrierReplacementEvidence(
            "NEED-1", "DRIVE", "OTHER",
            current_requalified=True,
            evidence_rebound=True,
            return_route_rebound=False,
            authority_requalified=True,
        )
        result = qualify_carrier_replacement(evidence, expected_stable_need="NEED-1")
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.HOLD)
        self.assertIn("RETURN_ROUTE_NOT_REBOUND", result.reasons)

    def test_replacement_cannot_change_stable_need(self):
        evidence = CarrierReplacementEvidence(
            "OTHER-NEED", "DRIVE", "OTHER",
            True, True, True, True,
        )
        result = qualify_carrier_replacement(evidence, expected_stable_need="NEED-1")
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.HOLD)
        self.assertIn("STABLE_NEED_BINDING_MISMATCH", result.reasons)

    def test_distinct_replacement_with_requalified_bindings_is_candidate(self):
        evidence = CarrierReplacementEvidence(
            "NEED-1", "DRIVE", "OTHER",
            True, True, True, True,
        )
        result = qualify_carrier_replacement(evidence, expected_stable_need="NEED-1")
        self.assertEqual(result.disposition, EnvironmentFieldDisposition.QUALIFIED_CANDIDATE)


if __name__ == "__main__":
    unittest.main()
