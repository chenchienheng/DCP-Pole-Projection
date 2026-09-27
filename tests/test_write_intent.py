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


    def test_unknown_action_cannot_bypass_revision_and_recovery(self):
        result = assess_write_intent(self.base(
            mutation_kind="UPSERT", expected_revision=None,
            rollback_or_recovery_present=False, target_exists=None))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("MUTATION_KIND_INVALID", result.reasons)

    def test_malformed_action_is_held_without_exception(self):
        for value in (None, "", "update", 1, True, [], {}, ["UPDATE"]):
            with self.subTest(value=value):
                result = assess_write_intent(self.base(mutation_kind=value))
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertFalse(result.mutation_allowed_as_candidate)

    def test_truthy_values_cannot_substitute_for_boolean_evidence(self):
        fields = ("authority_valid", "rights_valid", "purpose_valid",
                  "affected_scope_resolved", "fidelity_check_present",
                  "evidence_plan_present", "rollback_or_recovery_present")
        for field in fields:
            for value in ("false", "true", 1, 0, [], {}, None):
                with self.subTest(field=field, value=value):
                    result = assess_write_intent(self.base(**{field: value}))
                    self.assertEqual(result.decision, Decision.HOLD)
                    self.assertIn(f"{field.upper()}_INVALID_TYPE", result.reasons)

    def test_missing_or_wrong_type_intent_identity_is_held(self):
        for field in ("intent_id", "stable_life_id", "source_identity", "target_carrier_id"):
            for value in (None, "", 42, True, ["id"], {"id": "value"}):
                with self.subTest(field=field, value=value):
                    result = assess_write_intent(self.base(**{field: value}))
                    self.assertEqual(result.decision, Decision.HOLD)
                    self.assertIsInstance(result.intent_id, str)

    def test_optional_text_fields_do_not_accept_objects(self):
        for field in ("expected_revision", "responsibility_owner", "return_target"):
            for value in (True, 42, ["value"], {"value": "x"}):
                with self.subTest(field=field, value=value):
                    result = assess_write_intent(self.base(**{field: value}))
                    self.assertEqual(result.decision, Decision.HOLD)
                    self.assertIn(f"{field.upper()}_INVALID_TYPE", result.reasons)

    def test_target_existence_does_not_coerce_non_booleans(self):
        for value in ("true", "false", 1, 0, [], {}):
            with self.subTest(value=value):
                result = assess_write_intent(self.base(target_exists=value))
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertIn("TARGET_EXISTS_INVALID_TYPE", result.reasons)

    def test_valid_enum_and_json_action_strings_remain_compatible(self):
        for kind in MutationKind:
            for value in (kind, kind.value):
                with self.subTest(kind=kind, value=value):
                    result = assess_write_intent(self.base(mutation_kind=value))
                    self.assertEqual(result.decision, Decision.PASS)
                    self.assertIn("PASS_DOES_NOT_GRANT_EXECUTION_OR_NATIVE_ABSORPTION", result.reasons)

    def test_all_revision_sensitive_kinds_still_require_revision(self):
        for kind in (MutationKind.UPDATE, MutationKind.DELETE, MutationKind.APPEND, MutationKind.SYNC_STATE):
            with self.subTest(kind=kind):
                result = assess_write_intent(self.base(mutation_kind=kind.value, expected_revision=None))
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertIn("EXPECTED_REVISION_MISSING", result.reasons)

    def test_create_does_not_require_existing_target_or_revision(self):
        result = assess_write_intent(self.base(
            mutation_kind="CREATE", expected_revision=None,
            target_exists=False, rollback_or_recovery_present=False))
        self.assertEqual(result.decision, Decision.PASS)

    def test_false_boolean_evidence_preserves_existing_semantic_holds(self):
        result = assess_write_intent(self.base(authority_valid=False))
        self.assertIn("MUTATION_AUTHORITY_MISSING", result.reasons)
        self.assertNotIn("AUTHORITY_VALID_INVALID_TYPE", result.reasons)

    def test_revision_and_candidate_semantics_are_not_external_verification(self):
        item = self.base(expected_revision="caller-declared-not-looked-up")
        before = item.__dict__.copy()
        result = assess_write_intent(item)
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(item.__dict__, before)
        self.assertIn("PASS_DOES_NOT_GRANT_EXECUTION_OR_NATIVE_ABSORPTION", result.reasons)


if __name__ == "__main__":
    unittest.main()
