import json
import unittest
from pathlib import Path


class TranslationMetabolismReviewTests(unittest.TestCase):
    def payload(self):
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / "fixtures" / "repository" / "02-translation-metabolism-review.json").read_text())

    def test_translation_is_not_a_permanent_layer(self):
        payload = self.payload()
        self.assertEqual(payload["current_architecture_role"], "NONE_AS_PERMANENT_LAYER")
        self.assertFalse(payload["normal_reader_required"])

    def test_retired_fixed_relay_roles_do_not_return(self):
        payload = self.payload()
        retired = {item["path"] for item in payload["observed_dispositions"] if item["state"] == "RETIRED_ABSENT"}
        self.assertIn("02_translation-layer/CLOUD_OVER_CLOUD_CONTROL_CENTER_SPEC.md", retired)
        self.assertIn("02_translation-layer/BRIDGE_DRILL_TEMPLATE_v0_1.md", retired)

    def test_translation_retains_only_carrier_neutral_primitives(self):
        payload = self.payload()
        rules = set(payload["invariants"])
        self.assertIn("TRANSLATION_SUCCESS_DOES_NOT_PROVE_FIDELITY", rules)
        self.assertIn("TRANSLATION_CAPABILITY_DOES_NOT_REQUIRE_A_PERMANENT_TRANSLATION_LAYER", rules)
        self.assertIn("RETURN_TARGET_IS_RECEIVER_SPECIFIC_NOT_MOTHERTREE_OR_CORETRI_BY_DEFAULT", rules)
        self.assertFalse(payload["runtime"])
        self.assertFalse(payload["promotion"])


if __name__ == "__main__":
    unittest.main()
