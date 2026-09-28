import unittest

from evidence_to_world_r01 import (
    EvidenceKind,
    EvidenceObservation,
    EvidenceWorldDisposition,
    compile_evidence_to_world,
)


def obs(eid, kind, **kw):
    base = dict(
        evidence_id=eid,
        source_identity="DRAWING-SET-A",
        source_revision="REV-A",
        kind=kind,
        object_stable_id="OPENING-W1",
        object_class="OPENING",
        type_mark="W1",
        occurrence_location=None,
        quantity=None,
        dimension_value=180.0,
        dimension_unit="cm",
        relation_or_host="WALL-UNKNOWN",
        extraction_method="VISION_OR_VECTOR_PARSER",
        confidence=0.95,
        authority_scope="EVIDENCE_ONLY",
        current_for_purpose=True,
        engineering_accepted=False,
    )
    base.update(kw)
    return EvidenceObservation(**base)


class EvidenceToWorldR01Tests(unittest.TestCase):
    def test_schedule_plan_detail_can_link_without_acceptance_claim(self):
        result = compile_evidence_to_world((
            obs("S1", EvidenceKind.SCHEDULE, quantity=2),
            obs("P1", EvidenceKind.PLAN, occurrence_location="2F-A"),
            obs("P2", EvidenceKind.PLAN, occurrence_location="2F-B"),
            obs("D1", EvidenceKind.DETAIL),
        ))
        self.assertEqual(result.disposition, EvidenceWorldDisposition.CANDIDATE_LINKED)
        self.assertIn("ENGINEERING_ACCEPTANCE_REMAINS_NATIVE", result.reasons)

    def test_quantity_mismatch_holds_only_the_evidence_link(self):
        result = compile_evidence_to_world((
            obs("S1", EvidenceKind.SCHEDULE, quantity=3),
            obs("P1", EvidenceKind.PLAN, occurrence_location="2F-A"),
            obs("P2", EvidenceKind.PLAN, occurrence_location="2F-B"),
        ))
        self.assertEqual(result.disposition, EvidenceWorldDisposition.CONFLICT_HOLD)
        self.assertIn("SCHEDULE_OCCURRENCE_COUNT_MISMATCH", result.reasons)

    def test_low_confidence_screenshot_stays_to_verify(self):
        result = compile_evidence_to_world((
            obs("IMG1", EvidenceKind.IMAGE, confidence=0.55),
        ))
        self.assertEqual(result.disposition, EvidenceWorldDisposition.TO_VERIFY)

    def test_missing_revision_stays_to_verify(self):
        result = compile_evidence_to_world((
            obs("IMG1", EvidenceKind.IMAGE, source_revision=None),
        ))
        self.assertEqual(result.disposition, EvidenceWorldDisposition.TO_VERIFY)

    def test_carrier_method_does_not_define_object_identity(self):
        result = compile_evidence_to_world((
            obs("VEC", EvidenceKind.DETAIL, extraction_method="VECTOR_PDF"),
            obs("VIS", EvidenceKind.IMAGE, extraction_method="VISION"),
        ))
        self.assertEqual(result.stable_object_id, "OPENING-W1")
        self.assertEqual(result.disposition, EvidenceWorldDisposition.CANDIDATE_LINKED)


if __name__ == "__main__":
    unittest.main()
