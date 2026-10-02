from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.public_encounter import (
    PublicEncounterDisposition,
    PublicEncounterInput,
    assess_public_encounter,
)


def base(**overrides):
    values = dict(
        capability_id="CAP-1",
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
    return PublicEncounterInput(**values)


class PublicEncounterTests(unittest.TestCase):
    def test_unaffected_capability_stays_without_public_surface(self) -> None:
        result = assess_public_encounter(base(material_public_delta=False))
        self.assertEqual(result.disposition, PublicEncounterDisposition.NO_PUBLIC_ENCOUNTER_DELTA)
        self.assertFalse(result.projection_candidate)

    def test_unevidenced_native_capability_stays_internal(self) -> None:
        result = assess_public_encounter(base(native_capability_evidence_present=False))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, PublicEncounterDisposition.INTERNAL_ONLY)

    def test_native_body_exposure_fails(self) -> None:
        result = assess_public_encounter(base(native_body_exposed=True))
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.disposition, PublicEncounterDisposition.HOLD_NATIVE_EXPOSURE)

    def test_authority_transfer_is_not_capability_demo(self) -> None:
        result = assess_public_encounter(base(authority_transfer_implied=True))
        self.assertEqual(result.disposition, PublicEncounterDisposition.HOLD_CLAIM_INFLATION)

    def test_first_projection_must_be_revocable(self) -> None:
        result = assess_public_encounter(base(revocable=False))
        self.assertEqual(result.disposition, PublicEncounterDisposition.HOLD_IRREVERSIBLE_PROJECTION)

    def test_external_encounter_requires_return_path(self) -> None:
        result = assess_public_encounter(base(external_evidence_return_path=False))
        self.assertEqual(result.disposition, PublicEncounterDisposition.HOLD_RETURN_PATH)

    def test_candidate_does_not_equal_release_approval(self) -> None:
        result = assess_public_encounter(base())
        self.assertEqual(result.decision, Decision.PASS)
        self.assertTrue(result.projection_candidate)
        self.assertFalse(result.release_authorized)
        self.assertIn("PUBLIC_CANDIDATE_IS_NOT_PUBLIC_APPROVED", result.reasons)

    def test_release_approval_does_not_validate_architecture(self) -> None:
        result = assess_public_encounter(base(release_approved=True))
        self.assertTrue(result.release_authorized)
        self.assertIn("EXTERNAL_ADOPTION_DOES_NOT_VALIDATE_WHOLE_ARCHITECTURE", result.reasons)


if __name__ == "__main__":
    unittest.main()
