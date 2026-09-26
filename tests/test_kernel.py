from __future__ import annotations

import unittest

from dcp_kernel import (
    CapabilityBinding,
    ClaimCeiling,
    ClaimEvidence,
    CurrentCandidate,
    CurrentResolutionStatus,
    Decision,
    IllegalReturnTransition,
    InvariantCore,
    LifecycleState,
    LearningDisposition,
    LearningInput,
    Motion,
    Need,
    ReturnClosure,
    ReturnState,
    StableLife,
    Transition,
    TriRootState,
    assess_learning_input,
    compute_affected_cone,
    evaluate_claim_ceiling,
    evaluate_transition,
    resolve_capability_binding,
    resolve_current,
)


class DCPKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.life = StableLife(
            life_id="GUI-LU",
            invariant_core=InvariantCore(
                identity_anchor="GUI-LU",
                meaning_anchor="family-home-and-working-base",
                world_truth_id="WORLD-GUI-LU-001",
            ),
            native_owner="GLMODEL",
            current_revision="WORLD-R1",
            last_good_revision="WORLD-R1",
        )
        self.tri_root = TriRootState(
            meaning_preserved=True,
            dependencies_resolved=True,
            world_id="WORLD-GUI-LU-001",
            source_revision="WORLD-R1",
        )
        self.binding = CapabilityBinding(
            capability_id="render_world_projection",
            actor_id="renderer-01",
            carrier_id="render-service",
            authority_granted=True,
            rights_allowed=True,
            evidence_available=True,
            return_target="GLMODEL",
            native_internalized=False,
            actor_labels=("GLModel Render",),
        )

    def test_capability_resolution_ignores_pole_name_and_requires_authority(self) -> None:
        need = Need(
            need_id="N-001",
            required_capability="resolve_current",
            receiver="DCP",
        )
        named_but_unauthorized = CapabilityBinding(
            capability_id="resolve_current",
            actor_id="DCP-window",
            carrier_id="chat",
            authority_granted=False,
            rights_allowed=True,
            evidence_available=True,
            return_target="DCP",
            actor_labels=("DCP", "推理極"),
        )
        lawful_generic = CapabilityBinding(
            capability_id="resolve_current",
            actor_id="resolver-17",
            carrier_id="local-python",
            authority_granted=True,
            rights_allowed=True,
            evidence_available=True,
            return_target="DCP",
        )

        result = resolve_capability_binding(
            need,
            [named_but_unauthorized, lawful_generic],
        )

        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.binding, lawful_generic)
        self.assertIn("AUTHORITY_NOT_GRANTED", result.excluded["DCP-window@chat"])

    def test_capability_fail_severity_is_not_downgraded_by_hold_reason(self) -> None:
        binding = CapabilityBinding(
            capability_id="wrong_capability",
            actor_id="named-dcp-window",
            carrier_id="chat",
            authority_granted=False,
            rights_allowed=True,
            evidence_available=True,
            return_target="GLMODEL",
        )
        transition = Transition(
            transition_id="T-CAPABILITY-SEVERITY",
            stable_life_id="GUI-LU",
            need="render concept",
            state_before=LifecycleState.CURRENT,
            proposed_effect="wrong binding",
            capability_id="render_world_projection",
            source_revision="WORLD-R1",
            world_id_before="WORLD-GUI-LU-001",
            world_id_after="WORLD-GUI-LU-001",
        )

        result = evaluate_transition(self.life, self.tri_root, binding, transition)
        capability = next(
            item for item in result.observations if item.motion is Motion.CAPABILITY
        )
        self.assertEqual(capability.decision, Decision.FAIL)
        self.assertIn("CAPABILITY_BINDING_MISMATCH", capability.reasons)
        self.assertIn("AUTHORITY_NOT_GRANTED", capability.reasons)

    def test_equivalent_learning_receipt_is_reused_without_repropagation(self) -> None:
        result = assess_learning_input(
            LearningInput(
                source_id="IDEAS-RETURN-1",
                source_revision="R1",
                receiver="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                equivalent_receipt_exists=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(
            result.disposition,
            LearningDisposition.REUSE_NO_REPROPAGATION,
        )

    def test_historical_learning_requires_explicit_reentry_purpose(self) -> None:
        result = assess_learning_input(
            LearningInput(
                source_id="LEGACY-AXIS",
                source_revision="R0",
                receiver="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                historical=True,
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(result.disposition, LearningDisposition.HOLD_CONTAMINATION)

    def test_receiver_not_affected_does_not_broadcast_learning(self) -> None:
        result = assess_learning_input(
            LearningInput(
                source_id="GLMODEL-WORLD-RETURN",
                source_revision="R2",
                receiver="DCP",
                affected_receivers=("GLMODEL",),
                material_delta=True,
            )
        )
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(
            result.disposition,
            LearningDisposition.RECEIVER_NOT_AFFECTED,
        )

    def test_native_body_copy_request_is_rejected(self) -> None:
        result = assess_learning_input(
            LearningInput(
                source_id="IDEAS-NATIVE-BODY",
                source_revision="R5",
                receiver="DCP",
                affected_receivers=("DCP",),
                material_delta=True,
                native_body_copy_requested=True,
            )
        )
        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.disposition, LearningDisposition.HOLD_CONTAMINATION)

    def test_latest_timestamp_does_not_override_valid_successor(self) -> None:
        valid_successor = CurrentCandidate(
            stable_life_id="GUI-LU",
            revision="WORLD-R2",
            lifecycle_state=LifecycleState.CANDIDATE,
            successor_of="WORLD-R1",
            authority_valid=True,
            evidence_valid=True,
            receiver_reconciled=True,
            reader_eligible=True,
            timestamp="2026-08-20T00:00:00Z",
        )
        newer_but_invalid = CurrentCandidate(
            stable_life_id="GUI-LU",
            revision="WORLD-R3",
            lifecycle_state=LifecycleState.CANDIDATE,
            successor_of=None,
            authority_valid=False,
            evidence_valid=False,
            receiver_reconciled=False,
            reader_eligible=True,
            timestamp="2026-08-22T00:00:00Z",
        )

        result = resolve_current(
            stable_life_id="GUI-LU",
            last_good_revision="WORLD-R1",
            candidates=[newer_but_invalid, valid_successor],
        )

        self.assertEqual(result.status, CurrentResolutionStatus.CURRENT)
        self.assertEqual(result.selected_revision, "WORLD-R2")
        self.assertIn("AUTHORITY_INVALID", result.rejected["WORLD-R3"])

    def test_valid_transition_has_one_identity_and_eight_observations(self) -> None:
        transition = Transition(
            transition_id="T-VALID",
            stable_life_id="GUI-LU",
            need="render alternate camera",
            state_before=LifecycleState.CURRENT,
            proposed_effect="new camera projection only",
            capability_id="render_world_projection",
            source_revision="WORLD-R1",
            representation_only=True,
            requests_world_truth_mutation=False,
            world_id_before="WORLD-GUI-LU-001",
            world_id_after="WORLD-GUI-LU-001",
        )

        result = evaluate_transition(
            self.life,
            self.tri_root,
            self.binding,
            transition,
        )

        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(len(result.observations), 8)
        self.assertEqual(
            {item.transition_id for item in result.observations},
            {"T-VALID"},
        )
        self.assertEqual(
            {item.motion for item in result.observations},
            set(Motion),
        )

    def test_render_cannot_mutate_world_truth_directly(self) -> None:
        transition = Transition(
            transition_id="T-RENDER-MUTATION",
            stable_life_id="GUI-LU",
            need="render concept",
            state_before=LifecycleState.CURRENT,
            proposed_effect="invent new building geometry",
            capability_id="render_world_projection",
            source_revision="WORLD-R1",
            representation_only=True,
            requests_world_truth_mutation=True,
            world_receiver_authorized=False,
            world_id_before="WORLD-GUI-LU-001",
            world_id_after="WORLD-GUI-LU-001",
        )

        result = evaluate_transition(
            self.life,
            self.tri_root,
            self.binding,
            transition,
        )

        self.assertEqual(result.decision, Decision.FAIL)
        self.assertEqual(result.first_material_break.motion, Motion.REALITY)
        self.assertIn(
            "REPRESENTATION_IMPERSONATES_WORLD_TRUTH",
            result.first_material_break.reasons,
        )

    def test_parametric_divergent_world_id_is_second_truth_risk(self) -> None:
        binding = CapabilityBinding(
            capability_id="parametric_reconstruction",
            actor_id="parametric-01",
            carrier_id="bim",
            authority_granted=True,
            rights_allowed=True,
            evidence_available=True,
            return_target="GLMODEL",
            native_internalized=True,
        )
        transition = Transition(
            transition_id="T-PARAMETRIC-SECOND-TRUTH",
            stable_life_id="GUI-LU",
            need="rebuild driveway envelope",
            state_before=LifecycleState.CURRENT,
            proposed_effect="new BIM world",
            capability_id="parametric_reconstruction",
            source_revision="WORLD-R1",
            world_receiver_authorized=True,
            world_id_before="WORLD-GUI-LU-001",
            world_id_after="WORLD-GUI-LU-002",
        )

        result = evaluate_transition(self.life, self.tri_root, binding, transition)

        self.assertEqual(result.decision, Decision.FAIL)
        reality = next(item for item in result.observations if item.motion is Motion.REALITY)
        self.assertIn("SECOND_WORLD_TRUTH_RISK", reality.reasons)

    def test_external_capability_cannot_claim_native_internalization(self) -> None:
        transition = Transition(
            transition_id="T-CAPABILITY-PROMOTION",
            stable_life_id="GUI-LU",
            need="render concept",
            state_before=LifecycleState.CURRENT,
            proposed_effect="claim native render competence",
            capability_id="render_world_projection",
            source_revision="WORLD-R1",
            claims_native_capability=True,
            world_id_before="WORLD-GUI-LU-001",
            world_id_after="WORLD-GUI-LU-001",
        )

        result = evaluate_transition(
            self.life,
            self.tri_root,
            self.binding,
            transition,
        )

        self.assertEqual(result.decision, Decision.FAIL)
        capability = next(
            item for item in result.observations if item.motion is Motion.CAPABILITY
        )
        self.assertIn("EXTERNAL_CAPABILITY_NOT_NATIVE_INTERNALIZED", capability.reasons)

    def test_zombie_dependency_breaks_continuity(self) -> None:
        transition = Transition(
            transition_id="T-ZOMBIE",
            stable_life_id="GUI-LU",
            need="rebuild current",
            state_before=LifecycleState.CURRENT,
            proposed_effect="rebuild using retired AXIS body",
            capability_id="render_world_projection",
            source_revision="WORLD-R1",
            world_id_before="WORLD-GUI-LU-001",
            world_id_after="WORLD-GUI-LU-001",
            requires_retired_topology=True,
        )

        result = evaluate_transition(
            self.life,
            self.tri_root,
            self.binding,
            transition,
        )

        continuity = next(
            item for item in result.observations if item.motion is Motion.CONTINUITY
        )
        self.assertEqual(continuity.decision, Decision.FAIL)
        self.assertIn("ZOMBIE_ARCHITECTURE_DEPENDENCY", continuity.reasons)

    def test_return_state_machine_rejects_skips_and_exposes_debt(self) -> None:
        closure = ReturnClosure(return_id="RET-1", receiver="DCP")
        self.assertIn("READ_DEBT", closure.outstanding_debt)
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.ACTUAL_READ, receiver_actual_read=True)

        closure = closure.advance(ReturnState.ROUTED)
        with self.assertRaises(IllegalReturnTransition):
            closure.advance(ReturnState.ACTUAL_READ)

    def test_return_state_machine_reaches_a4_only_after_retest(self) -> None:
        closure = ReturnClosure(return_id="RET-2", receiver="GLMODEL")
        closure = closure.advance(ReturnState.ROUTED)
        closure = closure.advance(
            ReturnState.ACTUAL_READ,
            receiver_actual_read=True,
        )
        closure = closure.advance(ReturnState.MATERIALITY_RESOLVED)
        closure = closure.advance(
            ReturnState.RECEIVER_NATIVE_DISPOSITION,
            native_disposition="REBUILD_REQUIRED",
        )
        closure = closure.advance(ReturnState.RECONCILED)
        closure = closure.advance(
            ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON,
            rebuild_applied=True,
        )
        closure = closure.advance(
            ReturnState.BEHAVIOR_DELTA_OBSERVED,
            behavior_delta_observed=True,
        )
        self.assertEqual(closure.autonomy_level, "A3_BEHAVIOR_CHANGED")
        closure = closure.advance(ReturnState.RETESTED, retested=True)
        self.assertEqual(closure.autonomy_level, "A4_RETESTED")
        self.assertEqual(closure.outstanding_debt, ())

    def test_manual_intervention_blocks_autonomy_claim(self) -> None:
        closure = ReturnClosure(
            return_id="RET-3",
            receiver="GLMODEL",
            manual_interventions=("VITAS_REMINDER_FIND_RECEIVER",),
        )
        self.assertEqual(closure.autonomy_level, "A0_MANUAL_PROMPT_DEPENDENT")

    def test_affected_cone_is_bounded_to_eligible_receivers(self) -> None:
        graph = {
            "mobility-envelope": ("GLMODEL", "RENDER", "PARAMETRIC", "PUBLIC"),
            "PARAMETRIC": ("PROJECT_WORK",),
        }
        result = compute_affected_cone(
            changed_nodes=("mobility-envelope",),
            dependency_graph=graph,
            eligible_receivers={"GLMODEL", "PARAMETRIC", "PROJECT_WORK"},
        )
        self.assertEqual(
            result.affected,
            ("GLMODEL", "PARAMETRIC", "PROJECT_WORK"),
        )
        self.assertEqual(result.excluded["RENDER"], "RECEIVER_NOT_ELIGIBLE")
        self.assertEqual(result.excluded["PUBLIC"], "RECEIVER_NOT_ELIGIBLE")

    def test_claim_ceiling_uses_evidence_not_filename(self) -> None:
        self.assertEqual(
            evaluate_claim_ceiling(ClaimEvidence(machine_contract=True)),
            ClaimCeiling.MACHINE_CONTRACT,
        )
        self.assertEqual(
            evaluate_claim_ceiling(
                ClaimEvidence(machine_contract=True, executable_tests=True)
            ),
            ClaimCeiling.EXECUTABLE_CANDIDATE,
        )
        self.assertEqual(
            evaluate_claim_ceiling(
                ClaimEvidence(
                    machine_contract=True,
                    executable_tests=True,
                    end_to_end_platform_path=True,
                )
            ),
            ClaimCeiling.PLATFORM_SKELETON_CANDIDATE,
        )
        self.assertNotEqual(
            evaluate_claim_ceiling(
                ClaimEvidence(runtime_evidence=True, runtime_authority=False)
            ),
            ClaimCeiling.RUNTIME,
        )


if __name__ == "__main__":
    unittest.main()
