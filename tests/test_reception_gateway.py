from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.reception_gateway import GatewayDisposition, GatewayInput, assess_gateway_request


class ReceptionGatewayTests(unittest.TestCase):
    def test_unqualified_external_request_is_held(self) -> None:
        result = assess_gateway_request(GatewayInput("R1", False, True, True, True, ("DCP",)))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, GatewayDisposition.HOLD_SCOPE_IDENTITY_RIGHTS)

    def test_non_material_request_does_not_wake_receivers(self) -> None:
        result = assess_gateway_request(GatewayInput("R2", True, True, True, False, ("DCP",)))
        self.assertEqual(result.disposition, GatewayDisposition.OBSERVE_ONLY)
        self.assertEqual(result.routed_receivers, ())

    def test_material_request_routes_without_owner_gateway(self) -> None:
        result = assess_gateway_request(GatewayInput("R3", True, True, True, True, ("DCP", "GLMODEL")))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.disposition, GatewayDisposition.ROUTE)
        self.assertFalse(result.escalate_to_owner)

    def test_irreversible_request_escalates(self) -> None:
        result = assess_gateway_request(GatewayInput("R4", True, True, True, True, ("DCP",), irreversible=True))
        self.assertEqual(result.disposition, GatewayDisposition.ESCALATE_OWNER_DECISION)
        self.assertTrue(result.escalate_to_owner)

    def test_authority_change_escalates(self) -> None:
        result = assess_gateway_request(GatewayInput("R5", True, True, True, True, ("DCP",), authority_change_requested=True))
        self.assertTrue(result.escalate_to_owner)


if __name__ == "__main__":
    unittest.main()
