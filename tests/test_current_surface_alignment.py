from __future__ import annotations

import json
import unittest
from pathlib import Path


class CurrentSurfaceAlignmentTests(unittest.TestCase):
    def _manifest(self) -> dict:
        return json.loads(Path("CURRENT-SURFACE-MANIFEST.json").read_text(encoding="utf-8"))

    def test_legacy_families_are_not_current_reader_surfaces(self) -> None:
        manifest = self._manifest()
        legacy_prefixes = (
            "00_meta/",
            "00_mother-law/",
            "01_native-board/",
            "01_runtime-spine/",
            "02_runtime-ops/",
            "02_translation-layer/",
            "03_board-orchestration/",
            "03_field-governance/",
            "04_adapter-layer/",
            "04_interface-layer/",
            "05_XLEN_Reserve_Unenabled/",
            "05_topology/",
        )

        surfaces: list[str] = list(manifest["reader_priority"])
        optional_public_surfaces = manifest.get("current_public_surfaces", {})
        if isinstance(optional_public_surfaces, dict):
            for values in optional_public_surfaces.values():
                surfaces.extend(values)

        for surface in surfaces:
            self.assertFalse(
                surface.startswith(legacy_prefixes),
                f"legacy surface unexpectedly Current-readable: {surface}",
            )

    def _assert_carrier_and_location_guards(self, manifest: dict) -> None:
        # Current main expresses these guards here, not in the retired
        # classification_model/carrier_model fields. Never revive old controls.
        continuity = manifest["continuity_semantics"]
        self.assertEqual(continuity["topology"], "NEED_RELATIVE_NOT_PERMANENT")
        self.assertEqual(continuity["carriers"], "REPLACEABLE_NOT_IDENTITY_OR_AUTHORITY")
        self.assertIn("CARRIER_TO_IDENTITY",
                      manifest["semantic_control_plane"]["forbidden_inference"])
        self.assertEqual(
            manifest["promotion_rule"],
            "REPOSITORY_LOCATION_NAME_OR_RECENCY_DOES_NOT_ESTABLISH_CURRENT_OR_AUTHORITY",
        )
        self.assertTrue({"stable_identity_or_existence", "need_or_purpose",
                         "current_requalification", "authority_requalification",
                         "evidence_scope", "return_or_rebuild"}.issubset(
                             continuity["continuity_requires"]))

    def _assert_historical_reader_guards(self, manifest: dict) -> None:
        self.assertEqual(
            manifest["legacy_interpretation"],
            "HISTORICAL_OR_COMPATIBILITY_UNLESS_EXPLICITLY_RE-ADMITTED",
        )
        self.assertIn("HISTORICAL_TO_CURRENT",
                      manifest["semantic_control_plane"]["forbidden_inference"])
        gate = manifest["semantic_promotion_gates"]["HISTORICAL_TO_CURRENT"]
        self.assertTrue({"stable_binding", "purpose_qualified", "authority_qualified",
                         "evidence_observed", "explicit_current_pointer"}.issubset(
                             gate["requires"]))
        self.assertTrue({"recency", "search_hit", "readability", "repository_location"}
                        .issubset(gate["does_not_promote"]))

    def test_manifest_declares_carrier_and_folder_non_ontology(self) -> None:
        self._assert_carrier_and_location_guards(self._manifest())

    def test_historical_reader_shield_blocks_stale_reactivation(self) -> None:
        self._assert_historical_reader_guards(self._manifest())

    def test_weakened_carrier_guard_is_rejected(self) -> None:
        manifest = self._manifest()
        manifest["continuity_semantics"]["carriers"] = "CARRIER_IS_IDENTITY"
        with self.assertRaises(AssertionError):
            self._assert_carrier_and_location_guards(manifest)

    def test_missing_historical_authority_guard_is_rejected(self) -> None:
        manifest = self._manifest()
        manifest["semantic_promotion_gates"]["HISTORICAL_TO_CURRENT"]["requires"].remove(
            "authority_qualified")
        with self.assertRaises(AssertionError):
            self._assert_historical_reader_guards(manifest)

    def test_living_loop_is_not_second_control_plane(self) -> None:
        # Composition belongs to the candidate implementation manifest, not the
        # public Current resolver. Runtime behavior is covered by test_living_loop.
        public = self._manifest()
        for key in ("runtime", "native_source_root", "repo_is_pole_authority"):
            self.assertIs(public[key], False)
        implementation = json.loads(
            Path("contracts/implementation-manifest.json").read_text(encoding="utf-8"))
        for key in ("runtime", "promotion", "native_source_root", "repo_is_authority_root"):
            self.assertIs(implementation[key], False)
        self.assertIs(implementation["verification"]["living_loop_composed"], True)
        self.assertEqual(
            implementation["canonical_model"]["living_loop"],
            "external request -> bounded gateway -> resolved relation -> judgment/capability/action"
            " -> evidence -> return -> receiver rebuild -> new state -> retest",
        )
        modules = implementation["modules"]["world_relation_and_birth"]
        self.assertTrue({"dcp_kernel/relation_semantics.py", "dcp_kernel/reception_gateway.py",
                         "dcp_kernel/public_encounter.py", "dcp_kernel/operable_birth.py",
                         "dcp_kernel/living_loop.py"}.issubset(modules))
        for path in modules:
            self.assertTrue(Path(path).is_file(), path)
        gates = implementation["current_behavioral_gates"]
        self.assertEqual(gates["return_without_rebuild"], "RETURN_NOT_REBUILT")
        self.assertEqual(gates["thin_relation"], "STATIC_RELATION_ONLY")
        self.assertEqual(gates["birth_regression"], "BIRTH_REGRESSION")


if __name__ == "__main__":
    unittest.main()
