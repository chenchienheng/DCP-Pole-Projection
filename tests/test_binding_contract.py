from __future__ import annotations

import unittest

from dcp_kernel.binding_contract import (
    AuthorityBasis,
    AuthorityLeaseState,
    BindingContractInput,
    BindingProgressState,
    TrianglePole,
    assess_binding_contract,
)
from dcp_kernel.models import CurrentResolutionStatus, Decision
from dcp_kernel.reader_policy import ReaderDisposition
from dcp_kernel.schedule_effect import ScheduleEffectState
from dcp_kernel.successor import CoverageState


def ready(**overrides: object) -> BindingContractInput:
    values: dict[str, object] = {
        "source_identity": "SHARED-NFN-CONTRACT",
        "source_version": "2026-10-01T02:00:47.139Z",
        "stable_referent": "QINYI-NFN-BINDING",
        "receiver": "QINYI_ARCHITECTURE",
        "purpose": "TRIANGLE_AND_SCHEDULED_EFFECT_LOCK",
        "effect_id": "EFFECT-1",
        "receiver_affected": True,
        "material_delta": True,
        "ideas_meaning_preserved": True,
        "dcp_action_authority_valid": True,
        "glmodel_effect_observed": True,
        "current_status": CurrentResolutionStatus.CURRENT,
        "carrier_decision": Decision.PASS,
        "successor_state": CoverageState.COVERED,
        "reader_disposition": ReaderDisposition.READ_AFFECTED_SLICE,
        "schedule_state": ScheduleEffectState.EFFECTIVE,
        "metabolism_disposition": "KEEP_EXECUTABLE_CANDIDATE",
        "durable_persisted": True,
        "durable_readback": True,
    }
    values.update(overrides)
    return BindingContractInput(**values)


class BindingContractTests(unittest.TestCase):
    def test_authority_fields_reject_untyped_strings(self) -> None:
        with self.assertRaisesRegex(TypeError, "authority_basis"):
            ready(authority_basis="AUTHENTICATION_ONLY")
        with self.assertRaisesRegex(TypeError, "authority_lease_state"):
            ready(authority_lease_state="REVOKED")

    def test_unaffected_or_nonmaterial_edge_is_not_applicable(self) -> None:
        result = assess_binding_contract(ready(receiver_affected=False))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, BindingProgressState.NOT_APPLICABLE)
        self.assertFalse(result.write_required)

    def test_world_effect_cannot_override_meaning_failure(self) -> None:
        result = assess_binding_contract(ready(ideas_meaning_preserved=False))
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.first_unresolved_pole, TrianglePole.IDEAS_MEANING)
        self.assertFalse(result.locked)

    def test_world_effect_cannot_override_missing_action_authority(self) -> None:
        result = assess_binding_contract(ready(dcp_action_authority_valid=False))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, BindingProgressState.PARTIAL)
        self.assertEqual(result.first_unresolved_pole, TrianglePole.DCP_AUTHORITY)

    def test_unobserved_world_effect_is_partial(self) -> None:
        result = assess_binding_contract(ready(glmodel_effect_observed=False))
        self.assertEqual(result.state, BindingProgressState.PARTIAL)
        self.assertEqual(result.first_unresolved_pole, TrianglePole.GLMODEL_EFFECT)

    def test_authenticated_carrier_does_not_transitively_grant_authority(self) -> None:
        result = assess_binding_contract(
            ready(authority_basis=AuthorityBasis.AUTHENTICATION_ONLY)
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, BindingProgressState.FAILED)
        self.assertEqual(result.first_unresolved_pole, TrianglePole.DCP_AUTHORITY)
        self.assertIn("AUTHORITY_IS_NON_TRANSITIVE_AUTHENTICATION_ONLY", result.reasons)

    def test_expired_bounded_lease_holds_only_authority_edge(self) -> None:
        result = assess_binding_contract(
            ready(authority_lease_state=AuthorityLeaseState.EXPIRED)
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, BindingProgressState.PARTIAL)
        self.assertEqual(result.first_unresolved_pole, TrianglePole.DCP_AUTHORITY)
        self.assertIn("AUTHORITY_LEASE_EXPIRED", result.reasons)

    def test_required_release_and_recovery_must_be_observed(self) -> None:
        result = assess_binding_contract(
            ready(release_required=True, recovery_required=True)
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, BindingProgressState.PARTIAL)
        self.assertIn("BOUNDED_LEASE_RELEASE_UNVERIFIED", result.reasons)
        self.assertIn("RECOVERY_UNVERIFIED", result.reasons)

    def test_required_release_and_recovery_can_lock_when_observed(self) -> None:
        result = assess_binding_contract(
            ready(
                release_required=True,
                release_observed=True,
                recovery_required=True,
                recovery_observed=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, BindingProgressState.LOCKED)

    def test_existing_primitive_hold_remains_partial(self) -> None:
        result = assess_binding_contract(
            ready(
                current_status=CurrentResolutionStatus.HOLD,
                successor_state=CoverageState.AUDIT_INCOMPLETE,
                reader_disposition=ReaderDisposition.ESCALATE_BOUNDED,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, BindingProgressState.PARTIAL)
        self.assertIn("CURRENT_HOLD", result.reasons)
        self.assertIn("SUCCESSOR_AUDIT_INCOMPLETE", result.reasons)
        self.assertIn("READER_ESCALATE_BOUNDED", result.reasons)

    def test_scope_failure_is_not_downgraded_to_partial(self) -> None:
        result = assess_binding_contract(
            ready(schedule_state=ScheduleEffectState.FAIL_SCOPE_VIOLATION)
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, BindingProgressState.FAILED)

    def test_effect_without_durable_readback_is_unverified(self) -> None:
        result = assess_binding_contract(ready(durable_readback=False))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.state, BindingProgressState.PERSISTENCE_UNVERIFIED)
        self.assertFalse(result.locked)

    def test_complete_bounded_contract_locks(self) -> None:
        result = assess_binding_contract(ready())
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.state, BindingProgressState.LOCKED)
        self.assertTrue(result.locked)
        self.assertFalse(result.write_required)

    def test_exact_duplicate_converges_without_second_write(self) -> None:
        first = assess_binding_contract(ready())
        duplicate = assess_binding_contract(
            ready(
                duplicate_receipt=True,
                prior_locked_binding_key=first.binding_key,
            )
        )
        self.assertEqual(duplicate.state, BindingProgressState.DUPLICATE_CONVERGED)
        self.assertTrue(duplicate.locked)
        self.assertFalse(duplicate.write_required)

    def test_duplicate_key_mismatch_fails_closed(self) -> None:
        result = assess_binding_contract(
            ready(
                duplicate_receipt=True,
                prior_locked_binding_key="sha256:not-the-same-binding",
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.state, BindingProgressState.FAILED)

    def test_exact_duplicate_cannot_bypass_revoked_lease(self) -> None:
        first = assess_binding_contract(ready())
        duplicate = assess_binding_contract(
            ready(
                duplicate_receipt=True,
                prior_locked_binding_key=first.binding_key,
                authority_lease_state=AuthorityLeaseState.REVOKED,
            )
        )
        self.assertEqual(duplicate.decision, Decision.HOLD)
        self.assertEqual(duplicate.state, BindingProgressState.PARTIAL)
        self.assertFalse(duplicate.locked)
        self.assertIn("AUTHORITY_LEASE_REVOKED", duplicate.reasons)


if __name__ == "__main__":
    unittest.main()
