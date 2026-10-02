from __future__ import annotations

import unittest

from dcp_kernel.living_loop import LivingLoopBreak, LivingLoopInput, assess_living_loop
from dcp_kernel.models import Decision
from dcp_kernel.operable_birth import OperableBirthInput, assess_operable_birth
from dcp_kernel.public_encounter import PublicEncounterInput, assess_public_encounter
from dcp_kernel.reception_gateway import GatewayInput, assess_gateway_request
from dcp_kernel.relation_semantics import RelationInput, assess_relation


def gateway(**overrides):
    values = dict(
        request_id="REQ-1",
        source_identified=True,
        scope_bounded=True,
        rights_valid=True,
        material_event=True,
        affected_receivers=("DCP", "GLMODEL"),
    )
    values.update(overrides)
    return assess_gateway_request(GatewayInput(**values))


def relation(**overrides):
    values = dict(
        source_identity_resolved=True,
        target_identity_resolved=True,
        direction_known=True,
        state_defined=True,
        time_defined=True,
        evidence_defined=True,
        effect_defined=True,
        return_path_relevant=True,
        return_path_defined=True,
    )
    values.update(overrides)
    return assess_relation(RelationInput(**values))


def birth(**overrides):
    values = dict(
        existence_resolved=True,
        relation_resolved=True,
        event_materiality_resolved=True,
        judgment_before_capability=True,
        capability_bound=True,
        action_gated=True,
        evidence_recorded=True,
        receiver_disposition_observed=True,
        rebuild_applied=True,
        new_state_observed=True,
        retested=True,
    )
    values.update(overrides)
    return assess_operable_birth(OperableBirthInput(**values))


def encounter(**overrides):
    values = dict(
        capability_id="RELATION-VIEW",
        material_public_delta=True,
        native_capability_evidence_present=True,
        lawful_source_rights=True,
        privacy_boundary_preserved=True,
        native_body_exposed=False,
        bounded_scope=True,
        claim_within_capability_evidence=True,
        authority_transfer_implied=False,
        revocable=True,
        external_evidence_return_path=True,
        release_approved=False,
    )
    values.update(overrides)
    return assess_public_encounter(PublicEncounterInput(**values))


class LivingLoopTests(unittest.TestCase):
    def test_non_material_request_stops_without_wake(self) -> None:
        result = assess_living_loop(LivingLoopInput(gateway(material_event=False), relation(), birth()))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertFalse(result.operable_birth_delta)
        self.assertEqual(result.first_break, LivingLoopBreak.NONE)

    def test_gateway_break_is_first(self) -> None:
        result = assess_living_loop(LivingLoopInput(gateway(rights_valid=False), relation(), birth()))
        self.assertEqual(result.first_break, LivingLoopBreak.GATEWAY)

    def test_relation_gap_blocks_downstream_claims(self) -> None:
        result = assess_living_loop(LivingLoopInput(gateway(), relation(time_defined=False), birth()))
        self.assertEqual(result.first_break, LivingLoopBreak.RELATION)
        self.assertFalse(result.operable_birth_delta)

    def test_public_encounter_is_optional_for_internal_birth(self) -> None:
        result = assess_living_loop(LivingLoopInput(gateway(), relation(), birth()))
        self.assertTrue(result.operable_birth_delta)

    def test_public_projection_failure_blocks_external_slice_not_native_truth(self) -> None:
        result = assess_living_loop(
            LivingLoopInput(gateway(), relation(), birth(), encounter(native_body_exposed=True))
        )
        self.assertEqual(result.first_break, LivingLoopBreak.PUBLIC_ENCOUNTER)
        self.assertFalse(result.operable_birth_delta)

    def test_return_without_rebuild_is_not_birth(self) -> None:
        result = assess_living_loop(
            LivingLoopInput(gateway(), relation(), birth(receiver_disposition_observed=False, rebuild_applied=False))
        )
        self.assertEqual(result.first_break, LivingLoopBreak.RETURN_REBUILD)
        self.assertFalse(result.operable_birth_delta)

    def test_full_slice_reports_operable_birth_delta(self) -> None:
        result = assess_living_loop(LivingLoopInput(gateway(), relation(), birth(), encounter()))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.first_break, LivingLoopBreak.NONE)
        self.assertTrue(result.operable_birth_delta)


if __name__ == "__main__":
    unittest.main()
