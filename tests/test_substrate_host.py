from __future__ import annotations

import unittest

from dcp_kernel.action_gate import EffectClass, RiskLevel
from dcp_kernel.models import CapabilityBinding, InvariantCore, Need, StableLife
from dcp_kernel.substrate_host import (
    EffectObservation,
    LocalExecutionRequest,
    run_local_cycle,
)


def executor_a(request, binding):
    return EffectObservation(
        effect_id="E-A",
        evidence_id="EV-A",
        source_id="LOCAL",
        source_revision=request.expected_source_revision,
        effectivity="CURRENT",
        observed_effect="LOCAL_COUNTER_ADVANCED",
        new_revision="r2",
    )


def executor_b(request, binding):
    return EffectObservation(
        effect_id="E-B",
        evidence_id="EV-B",
        source_id="LOCAL",
        source_revision=request.expected_source_revision,
        effectivity="CURRENT",
        observed_effect="LOCAL_COUNTER_ADVANCED",
        new_revision="r2",
    )


class MinimumSubstrateHostTests(unittest.TestCase):
    def setUp(self):
        self.life = StableLife(
            life_id="SUBJECT-1",
            invariant_core=InvariantCore("identity", "meaning"),
            native_owner="LOCAL",
            current_revision="r1",
            last_good_revision="r1",
        )
        self.need = Need("NEED-1", "advance", "LOCAL_RECEIVER")

    def binding(self, carrier):
        return CapabilityBinding(
            capability_id="advance",
            actor_id=f"actor-{carrier}",
            carrier_id=carrier,
            authority_granted=True,
            rights_allowed=True,
            evidence_available=True,
            return_target="LOCAL_RECEIVER",
            native_internalized=False,
        )

    def request(self, bindings, authority=True):
        return LocalExecutionRequest(
            need=self.need,
            stable_life=self.life,
            required_effect=EffectClass.BOUNDED_MUTATION,
            proposed_effect=EffectClass.BOUNDED_MUTATION,
            risk_level=RiskLevel.LOW,
            capability_candidates=bindings,
            responsibility_owner="LOCAL_OWNER",
            authority_valid=authority,
            expected_source_revision="r1",
        )

    def test_local_cycle_runs_without_external_lookup(self):
        result = run_local_cycle(
            self.request((self.binding("A"),)),
            {"A": executor_a},
        )
        self.assertEqual(result.decision.value, "PASS")
        self.assertEqual(result.stable_life.life_id, "SUBJECT-1")
        self.assertEqual(result.stable_life.current_revision, "r2")
        self.assertEqual(result.return_closure.state.value, "RETESTED")
        self.assertEqual(result.return_closure.outstanding_debt, ())

    def test_provider_replacement_preserves_subject_need_and_result_revision(self):
        a = run_local_cycle(self.request((self.binding("A"),)), {"A": executor_a})
        b = run_local_cycle(self.request((self.binding("B"),)), {"B": executor_b})
        self.assertEqual(a.decision, b.decision)
        self.assertEqual(a.stable_life.life_id, b.stable_life.life_id)
        self.assertEqual(a.stable_life.current_revision, b.stable_life.current_revision)
        self.assertEqual(a.return_closure.receiver, b.return_closure.receiver)
        self.assertNotEqual(a.selected_carrier, b.selected_carrier)

    def test_capability_does_not_create_effect_authority(self):
        result = run_local_cycle(
            self.request((self.binding("A"),), authority=False),
            {"A": executor_a},
        )
        self.assertEqual(result.decision.value, "HOLD")
        self.assertIsNone(result.effect)
        self.assertIn("MUTATION_AUTHORITY_MISSING", result.reasons)

    def test_stale_effect_evidence_cannot_advance_current(self):
        def stale(request, binding):
            return EffectObservation(
                effect_id="E-ST",
                evidence_id="EV-ST",
                source_id="LOCAL",
                source_revision="stale",
                effectivity="CURRENT",
                observed_effect="SHOULD_NOT_COMMIT",
                new_revision="r2",
            )

        result = run_local_cycle(
            self.request((self.binding("A"),)),
            {"A": stale},
        )
        self.assertEqual(result.decision.value, "HOLD")
        self.assertEqual(result.stable_life.current_revision, "r1")
        self.assertIn("EFFECT_SOURCE_REVISION_MISMATCH", result.reasons)


if __name__ == "__main__":
    unittest.main()
