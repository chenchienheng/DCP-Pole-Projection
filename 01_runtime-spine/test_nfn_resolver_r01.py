import unittest

from nfn_resolver_r01 import (
    Current,
    Disposition,
    Event,
    Need,
    ProviderCandidate,
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
