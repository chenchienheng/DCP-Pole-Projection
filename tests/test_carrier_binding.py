from __future__ import annotations

import unittest

from dcp_kernel.carrier_binding import (
    CarrierCandidate,
    CarrierClass,
    CarrierNeed,
    resolve_carrier_binding,
    validate_carrier_substitution,
)
from dcp_kernel.models import Decision


class CarrierBindingTests(unittest.TestCase):
    def test_vendor_order_does_not_grant_selection(self) -> None:
        need = CarrierNeed(
            stable_life_id="GUI-LU",
            required_effect="persist evidence",
            required_capability="store_projection",
            return_target="GLMODEL",
        )
        named_first_but_unauthorized = CarrierCandidate(
            carrier_id="Drive",
            carrier_class=CarrierClass.STORAGE,
            capabilities=("store_projection",),
            authority_valid=False,
            rights_valid=True,
            evidence_available=True,
            return_supported=True,
            fidelity_supported=True,
            risk_allowed=True,
            vendor_labels=("Google Drive",),
        )
        lawful_generic = CarrierCandidate(
            carrier_id="object-store-02",
            carrier_class=CarrierClass.STORAGE,
            capabilities=("store_projection",),
            authority_valid=True,
            rights_valid=True,
            evidence_available=True,
            return_supported=True,
            fidelity_supported=True,
            risk_allowed=True,
        )
        result = resolve_carrier_binding(
            need,
            (named_first_but_unauthorized, lawful_generic),
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.carrier.carrier_id, "object-store-02")
        self.assertIn("AUTHORITY_INVALID", result.excluded["Drive"])

    def test_available_tool_without_return_or_fidelity_is_held(self) -> None:
        need = CarrierNeed("GUI-LU", "render", "visual_projection", "GLMODEL")
        candidate = CarrierCandidate(
            carrier_id="visual-tool",
            carrier_class=CarrierClass.REPRESENTATION,
            capabilities=("visual_projection",),
            authority_valid=True,
            rights_valid=True,
            evidence_available=True,
            return_supported=False,
            fidelity_supported=False,
            risk_allowed=True,
            available=True,
        )
        result = resolve_carrier_binding(need, (candidate,))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("RETURN_PATH_UNSUPPORTED", result.excluded["visual-tool"])
        self.assertIn("FIDELITY_NOT_PROVEN", result.excluded["visual-tool"])

    def test_multiple_eligible_carriers_remain_unselected_without_need_policy(self) -> None:
        need = CarrierNeed("GUI-LU", "store", "store_projection", "GLMODEL")
        a = CarrierCandidate(
            carrier_id="chat-carrier",
            carrier_class=CarrierClass.INTERACTIVE_EXECUTION,
            capabilities=("store_projection",),
            authority_valid=True,
            rights_valid=True,
            evidence_available=True,
            return_supported=True,
            fidelity_supported=True,
            risk_allowed=True,
        )
        b = CarrierCandidate(
            carrier_id="work-carrier",
            carrier_class=CarrierClass.INTERACTIVE_EXECUTION,
            capabilities=("store_projection",),
            authority_valid=True,
            rights_valid=True,
            evidence_available=True,
            return_supported=True,
            fidelity_supported=True,
            risk_allowed=True,
        )
        result = resolve_carrier_binding(need, (a, b))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIsNone(result.carrier)
        self.assertIn(
            "MULTIPLE_ELIGIBLE_CARRIERS_REQUIRE_EXPLICIT_SELECTION_POLICY",
            result.reasons,
        )

    def test_carrier_substitution_preserves_same_life(self) -> None:
        decision, reasons = validate_carrier_substitution(
            stable_life_id_before="GUI-LU",
            stable_life_id_after="GUI-LU",
            source_identity_preserved=True,
            evidence_lineage_preserved=True,
            return_target_preserved=True,
        )
        self.assertEqual(decision, Decision.PASS)
        self.assertIn("CARRIER_SUBSTITUTION_PRESERVES_STABLE_LIFE", reasons)

    def test_carrier_substitution_cannot_create_new_identity(self) -> None:
        decision, reasons = validate_carrier_substitution(
            stable_life_id_before="GUI-LU",
            stable_life_id_after="GUI-LU-COPY",
            source_identity_preserved=False,
            evidence_lineage_preserved=True,
            return_target_preserved=True,
        )
        self.assertEqual(decision, Decision.FAIL)
        self.assertIn("STABLE_IDENTITY_CHANGED_BY_CARRIER_SUBSTITUTION", reasons)


if __name__ == "__main__":
    unittest.main()
