from __future__ import annotations

from dataclasses import replace
import unittest

from dcp_kernel.action_gate import EffectClass, RiskLevel
from dcp_kernel.models import CapabilityBinding, Decision, InvariantCore, Need, ReturnState, StableLife
from dcp_kernel.return_state import ReturnClosure
from dcp_kernel.substrate_host import (
    EffectObservation, LocalExecutionRequest, reconcile_local_result, run_local_cycle,
)


def executor_a(request, binding):
    return EffectObservation(
        effect_id="E-A", evidence_id="EV-A", source_id="LOCAL",
        source_revision=request.expected_source_revision, effectivity="CURRENT",
        observed_effect="LOCAL_COUNTER_ADVANCED", new_revision="r2",
        provenance_verified=True,
    )


def executor_b(request, binding):
    return replace(executor_a(request, binding), effect_id="E-B", evidence_id="EV-B")


def supplied_return(pending, *, disposition="USE_LOCAL_EFFECT", manual=()):
    """Explicit synthetic receipt control; not a real receiver/transport claim."""
    return replace(pending.return_closure, state=ReturnState.RETESTED,
                   receiver_actual_read=True, native_disposition=disposition,
                   rebuild_applied=True, behavior_delta_observed=True,
                   retested=True, manual_interventions=manual)


class MinimumSubstrateHostTests(unittest.TestCase):
    def setUp(self):
        self.life = StableLife("SUBJECT-1", InvariantCore("identity", "meaning"),
                               "LOCAL", "r1", "r1")
        self.need = Need("NEED-1", "advance", "LOCAL_RECEIVER")

    def binding(self, carrier):
        return CapabilityBinding("advance", f"actor-{carrier}", carrier,
                                 True, True, True, "LOCAL_RECEIVER", False)

    def request(self, bindings=None, authority=True):
        return LocalExecutionRequest(
            need=self.need, stable_life=self.life,
            required_effect=EffectClass.BOUNDED_MUTATION,
            proposed_effect=EffectClass.BOUNDED_MUTATION, risk_level=RiskLevel.LOW,
            capability_candidates=bindings or (self.binding("A"),),
            responsibility_owner="LOCAL_OWNER", authority_valid=authority,
            expected_source_revision="r1", expected_source_id="LOCAL",
        )

    def pending(self, request=None):
        return run_local_cycle(request or self.request(), {"A": executor_a})

    def test_local_cycle_runs_without_external_lookup(self):
        request = self.request()
        pending = self.pending(request)
        self.assertEqual(pending.decision, Decision.HOLD)
        self.assertEqual(pending.stable_life, self.life)
        self.assertEqual(pending.return_closure.state, ReturnState.PRODUCED)
        self.assertFalse(pending.return_closure.receiver_actual_read)
        self.assertFalse(pending.return_closure.retested)
        self.assertIn("READ_DEBT", pending.return_closure.outstanding_debt)
        result = reconcile_local_result(request, pending, supplied_return(pending))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.stable_life.life_id, "SUBJECT-1")
        self.assertEqual(result.stable_life.current_revision, "r2")
        self.assertEqual(result.return_closure.outstanding_debt, ())

    def test_provider_replacement_preserves_subject_need_and_result_revision(self):
        ra = self.request((self.binding("A"),))
        rb = self.request((self.binding("B"),))
        a = run_local_cycle(ra, {"A": executor_a})
        b = run_local_cycle(rb, {"B": executor_b})
        a = reconcile_local_result(ra, a, supplied_return(a))
        b = reconcile_local_result(rb, b, supplied_return(b))
        self.assertEqual(a.decision, b.decision)
        self.assertEqual(a.stable_life, b.stable_life)
        self.assertEqual(a.return_closure.receiver, b.return_closure.receiver)
        self.assertNotEqual(a.selected_carrier, b.selected_carrier)

    def test_capability_does_not_create_effect_authority(self):
        calls = []
        result = run_local_cycle(self.request(authority=False),
                                 {"A": lambda *args: calls.append(args)})
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIsNone(result.effect)
        self.assertEqual(calls, [])
        self.assertIn("MUTATION_AUTHORITY_MISSING", result.reasons)

    def test_stale_effect_evidence_cannot_advance_current(self):
        result = run_local_cycle(self.request(),
                                 {"A": lambda r,b: replace(executor_a(r,b), source_revision="stale")})
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.stable_life, self.life)
        self.assertIn("EFFECT_SOURCE_REVISION_MISMATCH", result.reasons)

    def test_missing_or_wrong_source_binding_is_not_adopted(self):
        calls = []
        request = replace(self.request(), expected_source_id=None)
        result = run_local_cycle(request, {"A": lambda *a: calls.append(a)})
        self.assertEqual(calls, [])
        self.assertIn("EXPECTED_EFFECT_SOURCE_ID_MISSING", result.reasons)
        result = run_local_cycle(self.request(),
                                 {"A": lambda r,b: replace(executor_a(r,b), source_id="OTHER")})
        self.assertIn("EFFECT_SOURCE_ID_MISMATCH", result.reasons)
        self.assertEqual(result.stable_life, self.life)

    def test_truthy_authority_and_capability_declarations_do_not_execute(self):
        for field in ("authority_granted", "rights_allowed", "evidence_available", "native_internalized"):
            with self.subTest(field=field):
                calls = []
                request = self.request((replace(self.binding("A"), **{field: "false"}),))
                result = run_local_cycle(request, {"A": lambda *a: calls.append(a)})
                self.assertEqual(calls, [])
                self.assertEqual(result.decision, Decision.HOLD)
        result = self.pending(self.request(authority="false"))
        self.assertIn("ACTION_AUTHORITY_NOT_BOOLEAN", result.reasons)

    def test_no_action_does_not_invoke_executor(self):
        calls = []
        request = replace(self.request(), proposed_effect=EffectClass.NO_ACTION,
                          required_effect=EffectClass.NO_ACTION)
        result = run_local_cycle(request, {"A": lambda *a: calls.append(a)})
        self.assertEqual(calls, [])
        self.assertEqual(result.stable_life, self.life)
        self.assertIsNone(result.return_closure)
        self.assertEqual(result.reasons, ("NO_ACTION_SELECTED",))

    def test_bad_effect_shape_and_provenance_remain_visible_without_adoption(self):
        changes = ({"effect_id":" "}, {"new_revision":7}, {"evidence_id":None},
                   {"provenance_verified":"true"}, {"provenance_verified":False},
                   {"revoked":"false"}, {"revoked":True})
        for change in changes:
            with self.subTest(change=change):
                result = run_local_cycle(self.request(),
                                         {"A": lambda r,b: replace(executor_a(r,b), **change)})
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertIsNotNone(result.effect)
                self.assertIsNone(result.return_closure)
                self.assertEqual(result.stable_life, self.life)
        effect = EffectObservation("e", "ev", "s", "r1", "now", "observed", "r2")
        self.assertFalse(effect.provenance_verified)

    def test_executor_error_after_effect_does_not_retry_or_claim_rollback(self):
        counter = [0]
        def fails(request, binding):
            counter[0] += 1
            raise OSError("synthetic failure after effect")
        result = run_local_cycle(self.request(), {"A": fails})
        self.assertEqual(counter, [1])
        self.assertIn("LOCAL_EXECUTOR_ERROR_EFFECT_UNKNOWN", result.reasons)
        self.assertIsNone(result.return_closure)
        self.assertEqual(result.stable_life, self.life)

    def test_invalid_executor_return_remains_unknown_not_completed(self):
        result = run_local_cycle(self.request(), {"A": lambda *_: {"done": True}})
        self.assertIn("EXECUTOR_RETURN_TYPE_INVALID_EFFECT_UNKNOWN", result.reasons)
        self.assertIsNone(result.return_closure)

    def test_wrong_receiver_or_return_identity_is_rejected(self):
        pending = self.pending()
        for change in ({"receiver":"OTHER"}, {"return_id":"OTHER"}):
            with self.subTest(change=change):
                result = reconcile_local_result(self.request(), pending,
                                                replace(supplied_return(pending), **change))
                self.assertIn("RECEIVER_RETURN_BINDING_MISMATCH", result.reasons)
                self.assertEqual(result.stable_life, self.life)

    def test_other_need_or_subject_cannot_resume_the_saved_execution(self):
        request = self.request();pending = self.pending(request)
        variants = (replace(request, need=replace(request.need, need_id="OTHER")),
                    replace(request, stable_life=replace(self.life, life_id="OTHER")),
                    replace(request, expected_source_id="OTHER"),
                    replace(request, stable_life=replace(self.life, current_revision="r3")))
        for other in variants:
            with self.subTest(other=other):
                result = reconcile_local_result(other, pending, supplied_return(pending))
                self.assertIn("EXECUTION_REQUEST_BINDING_MISMATCH", result.reasons)
                self.assertEqual(result.stable_life, self.life)

    def test_reused_effect_id_receipt_is_bound_to_need_and_successor(self):
        request = self.request();pending = self.pending(request)
        other = replace(request, need=replace(request.need, need_id="OTHER"))
        other_pending = self.pending(other)
        self.assertNotEqual(pending.return_closure.return_id, other_pending.return_closure.return_id)
        result = reconcile_local_result(other, other_pending, supplied_return(pending))
        self.assertIn("RECEIVER_RETURN_BINDING_MISMATCH", result.reasons)
        tampered = replace(pending, effect=replace(pending.effect, new_revision="r99"))
        result = reconcile_local_result(request, tampered, supplied_return(pending))
        self.assertIn("SAVED_EFFECT_RETURN_BINDING_MISMATCH", result.reasons)

    def test_terminal_label_cannot_hide_missing_earlier_receiver_evidence(self):
        pending = self.pending()
        for change in ({"receiver_actual_read":False}, {"native_disposition":None},
                       {"rebuild_applied":False}, {"behavior_delta_observed":False},
                       {"retested":False}):
            with self.subTest(change=change):
                result = reconcile_local_result(self.request(), pending,
                                                replace(supplied_return(pending), **change))
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertEqual(result.stable_life, self.life)

    def test_truthy_receiver_evidence_and_invalid_state_do_not_close(self):
        pending = self.pending()
        for change in ({"receiver_actual_read":"false"}, {"retested":1},
                       {"state":"RETESTED"}, {"manual_interventions":["manual"]}):
            with self.subTest(change=change):
                result = reconcile_local_result(self.request(), pending,
                                                replace(supplied_return(pending), **change))
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertEqual(result.stable_life, self.life)

    def test_partial_receipt_is_preserved_and_can_resume_without_executor(self):
        calls=[]
        def counted(r,b):
            calls.append(1)
            return executor_a(r,b)
        request = self.request()
        pending = run_local_cycle(request, {"A":counted})
        partial = replace(pending.return_closure, state=ReturnState.ACTUAL_READ,
                          receiver_actual_read=True)
        pending = reconcile_local_result(request, pending, partial)
        self.assertEqual(pending.return_closure, partial)
        self.assertIn("RETEST_DEBT", pending.reasons)
        result = reconcile_local_result(request, pending, supplied_return(pending))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(calls,[1])

    def test_duplicate_complete_return_is_idempotent_and_manual_evidence_survives(self):
        request=self.request();pending=self.pending(request)
        receipt=supplied_return(pending,manual=("synthetic human confirmation",))
        complete=reconcile_local_result(request,pending,receipt)
        again=reconcile_local_result(request,complete,receipt)
        self.assertIs(again,complete)
        self.assertEqual(again.return_closure.autonomy_level,"A0_MANUAL_PROMPT_DEPENDENT")
        changed=replace(receipt,native_disposition="REJECT")
        conflict=reconcile_local_result(request,complete,changed)
        self.assertEqual(conflict.stable_life,complete.stable_life)
        self.assertNotEqual(conflict.decision,Decision.PASS)

    def test_rejected_disposition_never_advances_current(self):
        pending=self.pending()
        result=reconcile_local_result(self.request(),pending,
                                      supplied_return(pending,disposition="REJECT"))
        self.assertIn("RECEIVER_DID_NOT_ACCEPT_LOCAL_EFFECT",result.reasons)
        self.assertEqual(result.stable_life,self.life)
        self.assertIsNotNone(result.effect)

    def test_explicit_no_rebuild_reason_is_supported(self):
        pending=self.pending();receipt=supplied_return(pending)
        receipt=replace(receipt,rebuild_applied=False,no_rebuild_reason="No dependent view for this fixture")
        result=reconcile_local_result(self.request(),pending,receipt)
        self.assertEqual(result.decision,Decision.PASS)

    def test_receipt_regression_and_old_unbound_results_are_held(self):
        request=self.request();pending=self.pending(request)
        partial=replace(pending.return_closure,state=ReturnState.ACTUAL_READ,receiver_actual_read=True)
        progressed=reconcile_local_result(request,pending,partial)
        result=reconcile_local_result(request,progressed,pending.return_closure)
        self.assertIn("RECEIVER_RETURN_STATE_REGRESSION",result.reasons)
        result=reconcile_local_result(request,replace(pending,execution_request=None),supplied_return(pending))
        self.assertIn("EXECUTION_REQUEST_BINDING_MISMATCH",result.reasons)


if __name__ == "__main__":
    unittest.main()
