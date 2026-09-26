from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class PublicEncounterDisposition(str, Enum):
    NO_PUBLIC_ENCOUNTER_DELTA = "NO_PUBLIC_ENCOUNTER_DELTA"
    INTERNAL_ONLY = "INTERNAL_ONLY"
    PUBLIC_PROJECTION_CANDIDATE = "PUBLIC_PROJECTION_CANDIDATE"
    HOLD_RIGHTS_PRIVACY = "HOLD_RIGHTS_PRIVACY"
    HOLD_NATIVE_EXPOSURE = "HOLD_NATIVE_EXPOSURE"
    HOLD_CLAIM_INFLATION = "HOLD_CLAIM_INFLATION"
    HOLD_IRREVERSIBLE_PROJECTION = "HOLD_IRREVERSIBLE_PROJECTION"
    HOLD_RETURN_PATH = "HOLD_RETURN_PATH"


@dataclass(frozen=True)
class PublicEncounterInput:
    capability_id: str
    material_public_delta: bool
    native_capability_evidence_present: bool
    lawful_source_rights: bool
    privacy_boundary_preserved: bool
    native_body_exposed: bool
    bounded_scope: bool
    claim_within_capability_evidence: bool
    authority_transfer_implied: bool
    revocable: bool
    external_evidence_return_path: bool
    release_approved: bool = False


@dataclass(frozen=True)
class PublicEncounterAssessment:
    decision: Decision
    disposition: PublicEncounterDisposition
    projection_candidate: bool
    release_authorized: bool
    reasons: tuple[str, ...]


def assess_public_encounter(item: PublicEncounterInput) -> PublicEncounterAssessment:
    """Assess whether a Native capability has a lawful bounded encounter projection.

    Passing this gate only identifies a projection candidate. It never publishes,
    transfers authority, exposes the Native body, or validates the whole architecture.
    """

    if not item.material_public_delta:
        return PublicEncounterAssessment(
            Decision.PASS,
            PublicEncounterDisposition.NO_PUBLIC_ENCOUNTER_DELTA,
            False,
            False,
            ("NO_MATERIAL_PUBLIC_ENCOUNTER_NEED",),
        )

    if not item.native_capability_evidence_present:
        return PublicEncounterAssessment(
            Decision.HOLD,
            PublicEncounterDisposition.INTERNAL_ONLY,
            False,
            False,
            ("DO_NOT_PROJECT_A_CAPABILITY_NOT_YET_EVIDENCED_NATIVELY",),
        )

    if not item.lawful_source_rights or not item.privacy_boundary_preserved:
        return PublicEncounterAssessment(
            Decision.HOLD,
            PublicEncounterDisposition.HOLD_RIGHTS_PRIVACY,
            False,
            False,
            ("PUBLIC_ENCOUNTER_REQUIRES_LAWFUL_RIGHTS_AND_PRIVACY_BOUNDARY",),
        )

    if item.native_body_exposed:
        return PublicEncounterAssessment(
            Decision.FAIL,
            PublicEncounterDisposition.HOLD_NATIVE_EXPOSURE,
            False,
            False,
            ("PUBLIC_ENCOUNTER_IS_NOT_NATIVE_EXPOSURE",),
        )

    if not item.bounded_scope or not item.claim_within_capability_evidence or item.authority_transfer_implied:
        return PublicEncounterAssessment(
            Decision.HOLD,
            PublicEncounterDisposition.HOLD_CLAIM_INFLATION,
            False,
            False,
            ("CAPABILITY_DEMO_CANNOT_INFLATE_SCOPE_CLAIM_OR_AUTHORITY",),
        )

    if not item.revocable:
        return PublicEncounterAssessment(
            Decision.HOLD,
            PublicEncounterDisposition.HOLD_IRREVERSIBLE_PROJECTION,
            False,
            False,
            ("FIRST_ENCOUNTER_PROJECTION_MUST_BE_REVOCABLE",),
        )

    if not item.external_evidence_return_path:
        return PublicEncounterAssessment(
            Decision.HOLD,
            PublicEncounterDisposition.HOLD_RETURN_PATH,
            False,
            False,
            ("EXTERNAL_ENCOUNTER_WITHOUT_EVIDENCE_RETURN_CANNOT_FEED_NATIVE_REBUILD",),
        )

    return PublicEncounterAssessment(
        Decision.PASS,
        PublicEncounterDisposition.PUBLIC_PROJECTION_CANDIDATE,
        True,
        item.release_approved,
        (
            "BOUNDED_LAWFUL_REVOCABLE_PROJECTION_CANDIDATE",
            "PUBLIC_CANDIDATE_IS_NOT_PUBLIC_APPROVED" if not item.release_approved else "EXPLICIT_RELEASE_APPROVAL_RECORDED",
            "EXTERNAL_ADOPTION_DOES_NOT_VALIDATE_WHOLE_ARCHITECTURE",
        ),
    )
