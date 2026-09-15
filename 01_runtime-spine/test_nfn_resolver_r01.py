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


if __name__ == "__main__":
    unittest.main()
