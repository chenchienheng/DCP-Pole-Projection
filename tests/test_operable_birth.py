from __future__ import annotations

import unittest

from dcp_kernel.models import Decision
from dcp_kernel.operable_birth import BirthDisposition, OperableBirthInput, assess_operable_birth


def full(**overrides):
    values = dict(
        existence_resolved=True,
        relation_resolved=True,
        event_materiality_resolved=True,
        judgment_before_capability=True,
        capability_bound=True,
        action_gated=True,
        evidence_recorded=True,
        receiver_disposition_observed=True,
        rebuild_applied=True,
        new_state_observed=True,
        retested=True,
    )
    values.update(overrides)
    return OperableBirthInput(**values)


class OperableBirthTests(unittest.TestCase):
    def test_missing_early_chain_is_no_birth_delta(self) -> None:
        result = assess_operable_birth(full(relation_resolved=False))
        self.assertEqual(result.disposition, BirthDisposition.NO_OPERABLE_BIRTH_DELTA)
        self.assertIn("relation", result.missing)

    def test_return_without_receiver_rebuild_is_not_closed(self) -> None:
        result = assess_operable_birth(full(receiver_disposition_observed=False, rebuild_applied=False))
        self.assertEqual(result.disposition, BirthDisposition.RETURN_NOT_REBUILT)

    def test_rebuild_without_new_state_and_retest_gets_no_birth_credit(self) -> None:
        result = assess_operable_birth(full(new_state_observed=False, retested=False))
        self.assertEqual(result.disposition, BirthDisposition.NO_OPERABLE_BIRTH_DELTA)

    def test_centralization_or_human_gateway_load_is_regression(self) -> None:
        result = assess_operable_birth(full(human_gateway_load_increased=True))
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.disposition, BirthDisposition.BIRTH_REGRESSION)

    def test_full_living_chain_is_operable_birth_delta(self) -> None:
        result = assess_operable_birth(full())
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.disposition, BirthDisposition.OPERABLE_BIRTH_DELTA)


if __name__ == "__main__":
    unittest.main()
