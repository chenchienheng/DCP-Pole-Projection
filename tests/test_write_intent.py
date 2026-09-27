import unittest

from dcp_kernel.models import Decision
from dcp_kernel.write_intent import MutationKind, WriteIntentInput, assess_write_intent


class WriteIntentTests(unittest.TestCase):
    def base(self, **changes):
        data = dict(
            intent_id="W-1",
            stable_life_id="GUI-LU",
            source_identity="WORLD-R2",
            target_carrier_id="github",
            mutation_kind=MutationKind.UPDATE,
            authority_valid=True,
            rights_valid=True,
            purpose_valid=True,
            affected_scope_resolved=True,
            expected_revision="abc123",
            fidelity_check_present=True,
            evidence_plan_present=True,
            responsibility_owner="DCP",
            rollback_or_recovery_present=True,
            return_target="GLMODEL",
            target_exists=True,
        )
        data.update(changes)
        return WriteIntentInput(**data)

    def test_platform_name_does_not_replace_authority(self):
        result = assess_write_intent(self.base(authority_valid=False, target_carrier_id="github"))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertFalse(result.mutation_allowed_as_candidate)

    def test_revision_sensitive_write_requires_revision(self):
        result = assess_write_intent(self.base(expected_revision=None))
        self.assertEqual(result.decision, Decision.HOLD)

    def test_update_requires_target_existence(self):
        result = assess_write_intent(self.base(target_exists=False))
        self.assertEqual(result.decision, Decision.HOLD)

    def test_pass_is_only_mutation_candidate(self):
        result = assess_write_intent(self.base())
        self.assertEqual(result.decision, Decision.PASS)
        self.assertTrue(result.mutation_allowed_as_candidate)
        self.assertIn("PASS_DOES_NOT_GRANT_EXECUTION_OR_NATIVE_ABSORPTION", result.reasons)


if __name__ == "__main__":
    unittest.main()
