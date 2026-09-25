import unittest

from nfn_resolver_r01 import (
    Current,
    Disposition,
    Event,
    InteractionEvidence,
    Need,
    ProviderCandidate,
    ResourceReleaseEvidence,
    SourceClosureEvidence,
    qualify_interaction,
    qualify_resource_release,
    qualify_source_closure,
    resolve_event,
    route_provider,
)


class NFNResolverR01Tests(unittest.TestCase):
    def setUp(self):
        self.current = Current("OBJ-PUMP-001", "Need-A", "SRC-v1", "CURRENT-v1")

    def test_a_duplicate_is_quiet(self):
        event = Event("EV-A-DUP", "RETURN_DUPLICATE", "OBJ-PUMP-001", "Need-A", "SRC-v1", "CANDIDATE", duplicate_of="EV-A")
        result = resolve_event(event, self.current)
        self.assertEqual(result.disposition, Disposition.QUIET)
        self.assertEqual(result.current, self.current)

    def test_b_latest_not_applicable_does_not_replace_current(self):
        event = Event("EV-B", "SOURCE_UPDATE", "OBJ-PUMP-001", "Need-A", "SRC-v2", "SOURCE_ONLY", ("Engineering",), applicable=False)
        result = resolve_event(event, self.current, relevant_receivers=("Engineering",))
        self.assertEqual(result.disposition, Disposition.REVIEW)
        self.assertEqual(result.current.source_version, "SRC-v1")

    def test_c_affected_set_excludes_unrelated_receiver(self):
        event = Event("EV-C", "REALITY_DELTA", "OBJ-PUMP-001", "Need-C", "SITE-1", "OBSERVATION", ("GLModel", "Engineering", "Cost", "Unrelated-HR"))
        result = resolve_event(event, self.current, relevant_receivers=("GLModel", "Engineering", "Cost"))
        self.assertEqual(result.disposition, Disposition.AFFECTED)
        self.assertNotIn("Unrelated-HR", result.executable_affected)

    def test_d_cross_authority_race_holds_conflicting_edge(self):
        eng = Event("EV-D-ENG", "NATIVE_CANDIDATE", "OBJ-PUMP-001", "Need-D", "ENG-v3", "ENGINEERING", ("GLModel", "Procurement"), conflicts_with="EV-D-PROC")
        proc = Event("EV-D-PROC", "NATIVE_CANDIDATE", "OBJ-PUMP-001", "Need-D", "PROC-v1", "PROCUREMENT", ("GLModel", "Engineering"), conflicts_with="EV-D-ENG")
        result = resolve_event(eng, self.current, relevant_receivers=("GLModel", "Procurement"), concurrent_events=(proc,))
        self.assertEqual(result.disposition, Disposition.CONFLICT_HOLD)
        self.assertEqual(result.current, self.current)

    def test_e_survival_floor_rejects_text_provider_for_3d(self):
        need = Need("Need-E", "3D_GENERATION", survival_floor=frozenset({"3D_GENERATION"}))
        providers = (
            ProviderCandidate("Provider-A", False, frozenset({"3D_GENERATION"})),
            ProviderCandidate("Provider-B-text", True, frozenset({"TEXT_SUMMARY"})),
        )
        result = route_provider(need, providers, self.current)
        self.assertEqual(result.disposition, Disposition.CANNOT_HOLD)
        self.assertIsNone(result.selected_provider)

    def test_f_variable_gear_recomposition_keeps_need_identity(self):
        current = Current("CAP-TEXT-SUMMARY", "Need-F", "SOURCE-v1", "SUMMARY_PENDING")
        need = Need("Need-F", "TEXT_SUMMARY", survival_floor=frozenset({"TEXT_SUMMARY"}))
        providers = (
            ProviderCandidate("Provider-A", False, frozenset({"TEXT_SUMMARY", "DEEP"})),
            ProviderCandidate("Provider-B-small", True, frozenset({"TEXT_SUMMARY"})),
        )
        result = route_provider(need, providers, current)
        self.assertEqual(result.disposition, Disposition.RECOMPOSE)
        self.assertEqual(result.selected_provider, "Provider-B-small")
        self.assertEqual(result.current.need_id, "Need-F")

    def test_every_resolution_has_three_pole_projection(self):
        event = Event("EV-C", "REALITY_DELTA", "OBJ-PUMP-001", "Need-C", "SITE-1", "OBSERVATION", ("GLModel",))
        result = resolve_event(event, self.current, relevant_receivers=("GLModel",))
        self.assertEqual(set(result.tri_pole), {"Ideas", "DCP", "GLModel"})


class InteractionQualificationTests(unittest.TestCase):
    def setUp(self):
        self.current = Current("OBJECT-1", "NEED-1", "SOURCE-1", "UNCHANGED")

    def test_unqualified_caller_holds(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", False)
        self.assertEqual(qualify_interaction(evidence, self.current).disposition, Disposition.CANNOT_HOLD)

    def test_same_interaction_lineage_is_quiet(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", True, independent_interaction=False)
        self.assertEqual(qualify_interaction(evidence, self.current).disposition, Disposition.QUIET)

    def test_observed_committed_effect_is_not_replayed(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", True, committed_effect_id="E-1", effect_observed=True)
        self.assertEqual(qualify_interaction(evidence, self.current).disposition, Disposition.QUIET)

    def test_unknown_committed_effect_holds(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", True, committed_effect_id="E-1", effect_observed=None)
        self.assertEqual(qualify_interaction(evidence, self.current).disposition, Disposition.CANNOT_HOLD)

    def test_pure_ack_is_quiet(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", True, return_kind="ACK")
        self.assertEqual(qualify_interaction(evidence, self.current).disposition, Disposition.QUIET)

    def test_material_return_reenters_resolution(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", True, return_kind="RETURN", material_delta=True)
        self.assertEqual(qualify_interaction(evidence, self.current).disposition, Disposition.AFFECTED)

    def test_qualified_pre_effect_interaction_is_affected(self):
        evidence = InteractionEvidence("caller", "NEED-1", "I-1", True)
        result = qualify_interaction(evidence, self.current)
        self.assertEqual(result.disposition, Disposition.AFFECTED)
        self.assertEqual(set(result.tri_pole), {"Ideas", "DCP", "GLModel"})


class SourceClosureAndReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.current = Current("WORLD-1", "NEED-1", "SOURCE-1", "UNCHANGED")

    def test_human_courier_does_not_prove_direct_source_delivery(self):
        evidence = SourceClosureEvidence(
            "World", "CLOSE-1", True, False, True, via_human_courier=True
        )
        result = qualify_source_closure(evidence, self.current)
        self.assertEqual(result.disposition, Disposition.CANNOT_HOLD)
        self.assertIn("direct source delivery is not proven", result.reasons[0])

    def test_direct_delivery_without_source_read_holds(self):
        evidence = SourceClosureEvidence(
            "World", "CLOSE-2", True, True, False
        )
        self.assertEqual(
            qualify_source_closure(evidence, self.current).disposition,
            Disposition.CANNOT_HOLD,
        )

    def test_direct_delivery_and_source_read_close_without_new_work(self):
        evidence = SourceClosureEvidence(
            "World", "CLOSE-3", True, True, True
        )
        self.assertEqual(
            qualify_source_closure(evidence, self.current).disposition,
            Disposition.QUIET,
        )

    def test_resource_release_holds_before_required_effect(self):
        evidence = ResourceReleaseEvidence(
            "browser-tab-1", "ACTION-1", effect_observed=None
        )
        self.assertEqual(
            qualify_resource_release(evidence, self.current).disposition,
            Disposition.CANNOT_HOLD,
        )

    def test_resource_release_holds_when_delivery_is_required_but_unobserved(self):
        evidence = ResourceReleaseEvidence(
            "browser-tab-2", "ACTION-2",
            effect_observed=True,
            delivery_required=True,
            delivery_observed=False,
        )
        result = qualify_resource_release(evidence, self.current)
        self.assertEqual(result.disposition, Disposition.CANNOT_HOLD)
        self.assertIn("required delivery is not observed", result.reasons)

    def test_resource_release_becomes_recompose_candidate_after_all_required_evidence(self):
        evidence = ResourceReleaseEvidence(
            "browser-tab-3", "ACTION-3",
            effect_observed=True,
            delivery_required=True,
            delivery_observed=True,
            persistence_required=True,
            persistence_observed=True,
        )
        result = qualify_resource_release(evidence, self.current)
        self.assertEqual(result.disposition, Disposition.RECOMPOSE)


class ReceiverIterableRegressionTests(unittest.TestCase):
    """The receiver representation must not change the selected receiver set."""

    def setUp(self):
        self.current = Current("OBJECT-1", "NEED-1", "SOURCE-1", "UNCHANGED")
        self.candidates = ("Reader-A", "Reader-B", "Unrelated")
        self.receivers = ("Reader-A", "Reader-B")

    def assert_receiver_equivalence(self, event, **kwargs):
        expected = resolve_event(
            event, self.current, relevant_receivers=self.receivers, **kwargs
        )
        actual = resolve_event(
            event, self.current,
            relevant_receivers=(item for item in self.receivers), **kwargs
        )
        self.assertEqual(expected.executable_affected, self.receivers)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.current, self.current)

    def test_generator_receivers_preserve_affected_branch(self):
        event = Event("EVENT-1", "RETURN", "OBJECT-1", "NEED-1", "SOURCE-1",
                      "SCOPE-A", self.candidates)
        self.assert_receiver_equivalence(event)

    def test_generator_receivers_preserve_review_branch(self):
        event = Event("EVENT-2", "RETURN", "OBJECT-1", "NEED-1", "SOURCE-2",
                      "SCOPE-A", self.candidates, applicable=False)
        self.assert_receiver_equivalence(event)

    def test_generator_receivers_preserve_conflict_branch(self):
        event = Event("EVENT-3", "CANDIDATE", "OBJECT-1", "NEED-1", "SOURCE-1",
                      "SCOPE-A", self.candidates, conflicts_with="EVENT-4")
        peer = Event("EVENT-4", "CANDIDATE", "OBJECT-1", "NEED-1", "SOURCE-1",
                     "SCOPE-B", conflicts_with="EVENT-3")
        self.assert_receiver_equivalence(event, concurrent_events=(peer,))

    def test_duplicate_does_not_consume_receiver_iterator(self):
        def forbidden():
            raise AssertionError("duplicate must remain an early no-op")
            yield "never"
        event = Event("EVENT-5", "RETURN", "OBJECT-1", "NEED-1", "SOURCE-1",
                      "SCOPE-A", self.candidates, duplicate_of="EVENT-1")
        actual = resolve_event(event, self.current, relevant_receivers=forbidden())
        self.assertEqual(actual.disposition, Disposition.QUIET)
        self.assertEqual(actual.current, self.current)

    def test_empty_candidates_do_not_consume_receiver_iterator(self):
        def forbidden():
            raise AssertionError("empty candidates must not read receivers")
            yield "never"
        event = Event("EVENT-6", "RETURN", "OBJECT-1", "NEED-1", "SOURCE-1",
                      "SCOPE-A")
        actual = resolve_event(event, self.current, relevant_receivers=forbidden())
        self.assertEqual(actual.executable_affected, ())
        self.assertEqual(actual.current, self.current)


if __name__ == "__main__":
    unittest.main()
