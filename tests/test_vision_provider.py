from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.reality_intake import assess_reality_intake
from dcp_kernel.vision_provider import VisionFragment, VisionProviderResult, adapt_vision_provider_result


class VisionProviderTests(unittest.TestCase):
    def test_provider_output_remains_projection_and_preserves_uncertainty(self) -> None:
        adapted = adapt_vision_provider_result(
            VisionProviderResult(
                provider_id="VISION-PROVIDER-A",
                source_id="line-door-window-screenshot",
                source_revision=None,
                observed_at="2026-09-20T18:54+08:00",
                source_rights_valid=True,
                fragments=(
                    VisionFragment(
                        fragment_id="schedule-row-w1",
                        source_id="line-door-window-screenshot",
                        source_revision=None,
                        local_locator="image-1/table/row-W1",
                        content_class="table_row",
                        extracted_text="W1",
                        candidate_labels=("W1",),
                        confidence=0.92,
                    ),
                    VisionFragment(
                        fragment_id="plan-tag-w1",
                        source_id="line-door-window-screenshot",
                        source_revision=None,
                        local_locator="image-2/plan/tag-W1",
                        content_class="drawing_tag",
                        extracted_text="W1",
                        candidate_labels=("W1",),
                        confidence=0.84,
                    ),
                ),
            )
        )
        self.assertEqual(adapted.decision, Decision.PASS)
        self.assertIn("SOURCE_REVISION_UNKNOWN", adapted.observations[0].uncertainty)
        self.assertIn("EXTRACTION_REQUIRES_VERIFICATION", adapted.observations[0].uncertainty)

        intake = assess_reality_intake(
            need_id="DOOR-WINDOW-CORRESPONDENCE",
            observations=adapted.observations,
            required_capabilities=("referent_correspondence", "door_window_domain_check"),
        )
        self.assertEqual(intake.decision, Decision.PASS)
        self.assertIn("W1", adapted.observations[0].candidate_referents)
        self.assertIn("W1", adapted.observations[1].candidate_referents)
        self.assertIn(
            "schedule-row-w1:EXTRACTION_REQUIRES_VERIFICATION",
            intake.need.unknowns,
        )

    def test_invalid_confidence_holds_whole_provider_result(self) -> None:
        result = adapt_vision_provider_result(
            VisionProviderResult(
                provider_id="VISION-PROVIDER-A",
                source_id="image",
                source_revision="R1",
                observed_at="2026-09-20T18:54+08:00",
                source_rights_valid=True,
                fragments=(
                    VisionFragment(
                        fragment_id="bad",
                        source_id="image",
                        source_revision="R1",
                        local_locator="region-1",
                        content_class="text",
                        confidence=1.2,
                    ),
                ),
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("bad:INVALID_CONFIDENCE", result.reasons)

    def test_missing_rights_blocks_provider_adaptation(self) -> None:
        result = adapt_vision_provider_result(
            VisionProviderResult(
                provider_id="VISION-PROVIDER-A",
                source_id="image",
                source_revision="R1",
                observed_at="2026-09-20T18:54+08:00",
                source_rights_valid=False,
                fragments=(
                    VisionFragment(
                        fragment_id="region-1",
                        source_id="image",
                        source_revision="R1",
                        local_locator="region-1",
                        content_class="text",
                    ),
                ),
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("VISION_SOURCE_RIGHTS_NOT_VALID", result.reasons)


if __name__ == "__main__":
    unittest.main()
