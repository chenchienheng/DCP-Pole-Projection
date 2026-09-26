from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.reality_intake import (
    ObservationState,
    RealityObservation,
    assess_reality_intake,
)


class RealityIntakeTests(unittest.TestCase):
    def test_mixed_chat_images_compile_without_inventing_withdrawn_body(self) -> None:
        result = assess_reality_intake(
            need_id="DOOR-WINDOW-CHECK",
            observations=(
                RealityObservation(
                    observation_id="MSG-WITHDRAWN-1",
                    carrier_id="LINE",
                    source_id="conversation",
                    source_revision=None,
                    observed_at="2026-09-20T18:54+08:00",
                    state=ObservationState.WITHDRAWN_UNKNOWN_BODY,
                    content_class="message",
                ),
                RealityObservation(
                    observation_id="IMG-SCHEDULE",
                    carrier_id="LINE",
                    source_id="door-window-schedule-image",
                    source_revision=None,
                    observed_at="2026-09-20T18:54+08:00",
                    state=ObservationState.OBSERVED,
                    content_class="table_image",
                    candidate_referents=("D1", "D2", "W1", "W10"),
                    uncertainty=("SOURCE_REVISION_UNKNOWN",),
                ),
                RealityObservation(
                    observation_id="IMG-PLAN",
                    carrier_id="LINE",
                    source_id="floor-plan-image",
                    source_revision=None,
                    observed_at="2026-09-20T18:54+08:00",
                    state=ObservationState.OBSERVED,
                    content_class="drawing_image",
                    candidate_relations=("TYPE_TO_OCCURRENCE_CANDIDATE",),
                    uncertainty=("SAME_REFERENT_NOT_PROVEN",),
                ),
            ),
            required_capabilities=(
                "visual_document_reading",
                "referent_correspondence",
                "door_window_domain_check",
            ),
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertIsNotNone(result.need)
        self.assertIn(
            "MSG-WITHDRAWN-1:WITHDRAWN_BODY_UNKNOWN",
            result.need.unknowns,
        )
        self.assertIn(
            "IMG-PLAN:SAME_REFERENT_NOT_PROVEN",
            result.need.unknowns,
        )

    def test_withdrawn_only_does_not_fabricate_need_body(self) -> None:
        result = assess_reality_intake(
            need_id="UNKNOWN",
            observations=(
                RealityObservation(
                    observation_id="MSG-WITHDRAWN",
                    carrier_id="LINE",
                    source_id="conversation",
                    source_revision=None,
                    observed_at="2026-09-20T18:54+08:00",
                    state=ObservationState.WITHDRAWN_UNKNOWN_BODY,
                    content_class="message",
                ),
            ),
            required_capabilities=("message_reading",),
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("NO_USABLE_OBSERVATION_BODY", result.reasons)

    def test_observation_does_not_require_clean_structured_source(self) -> None:
        result = assess_reality_intake(
            need_id="MESSY-INPUT",
            observations=(
                RealityObservation(
                    observation_id="SCREENSHOT",
                    carrier_id="chat-screenshot",
                    source_id="mixed-image",
                    source_revision="capture-1",
                    observed_at="2026-09-20T18:54+08:00",
                    state=ObservationState.OBSERVED,
                    content_class="mixed_ui_table_drawing",
                    uncertainty=("TEXT_PARTIALLY_LEGIBLE",),
                ),
            ),
            required_capabilities=("visual_document_reading",),
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertIn(
            "SCREENSHOT:TEXT_PARTIALLY_LEGIBLE",
            result.need.unknowns,
        )


if __name__ == "__main__":
    unittest.main()
