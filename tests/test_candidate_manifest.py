from __future__ import annotations

import json
import unittest
from pathlib import Path


class CandidateManifestTests(unittest.TestCase):
    def test_manifest_and_cross_pole_contract_preserve_claim_boundaries(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads(
            (root / "contracts" / "implementation-manifest.json").read_text()
        )
        learning_schema = json.loads(
            (root / "contracts" / "cross-pole-learning.schema.json").read_text()
        )

        self.assertEqual(manifest["lifecycle_state"], "CANDIDATE")
        self.assertFalse(manifest["runtime"])
        self.assertFalse(manifest["promotion"])
        self.assertFalse(manifest["native_source_root"])
        self.assertFalse(manifest["repo_is_authority_root"])
        self.assertEqual(
            manifest["canonical_model"]["inner_motion_interpretation"],
            "eight observations of one transition; not eight independent controllers",
        )
        self.assertIn(
            "contracts/cross-pole-learning.schema.json",
            manifest["machine_contracts"],
        )
        self.assertIn(
            "native_body_copy_requested",
            learning_schema["properties"],
        )
        self.assertIn(
            "equivalent_receipt_exists",
            learning_schema["properties"],
        )
        self.assertIn(
            "reentry_purpose",
            learning_schema["properties"],
        )


if __name__ == "__main__":
    unittest.main()
