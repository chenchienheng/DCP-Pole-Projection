import unittest

from portable_transition_r01 import (
    PortableTransitionDisposition,
    PortableTransitionInput,
    assess_portable_transition,
)


class PortableTransitionR01Tests(unittest.TestCase):
    def test_location_change_alone_is_pointer_update(self):
        result = assess_portable_transition(PortableTransitionInput(
            stable_id_before="SUBJECT-1",
            stable_id_after="SUBJECT-1",
            carrier_before="Drive",
            carrier_after="GitHub",
            authority_preserved=True,
            state_preserved=True,
            evidence_lineage_preserved=True,
            return_target_preserved=True,
            reentry_binding_preserved=True,
            capability_semantics_preserved=True,
            resource_semantics_preserved=True,
        ))
        self.assertEqual(result.disposition, PortableTransitionDisposition.POINTER_UPDATE_ONLY)
        self.assertFalse(result.rebuild_required)

    def test_world_chat_to_work_like_holds_when_resource_semantics_unknown(self):
        result = assess_portable_transition(PortableTransitionInput(
            stable_id_before="QINYI_WORLD_MODELING_CONTINUITY",
            stable_id_after="QINYI_WORLD_MODELING_CONTINUITY",
            carrier_before="Chat",
            carrier_after="Work-like",
            authority_preserved=True,
            state_preserved=True,
            evidence_lineage_preserved=True,
            return_target_preserved=True,
            reentry_binding_preserved=True,
            capability_semantics_preserved=None,
            resource_semantics_preserved=None,
        ))
        self.assertEqual(result.disposition, PortableTransitionDisposition.HOLD_UNRESOLVED)
        self.assertTrue(result.identity_preserved)
        self.assertFalse(result.rebuild_required)

    def test_resource_change_requires_recomposition_not_new_identity(self):
        result = assess_portable_transition(PortableTransitionInput(
            stable_id_before="WORLD",
            stable_id_after="WORLD",
            carrier_before="Chat",
            carrier_after="Work",
            authority_preserved=True,
            state_preserved=True,
            evidence_lineage_preserved=True,
            return_target_preserved=True,
            reentry_binding_preserved=True,
            capability_semantics_preserved=False,
            resource_semantics_preserved=False,
        ))
        self.assertEqual(result.disposition, PortableTransitionDisposition.RECOMPOSE_REQUIRED)
        self.assertTrue(result.identity_preserved)
        self.assertTrue(result.rebuild_required)

    def test_carrier_must_not_create_new_life(self):
        result = assess_portable_transition(PortableTransitionInput(
            stable_id_before="WORLD",
            stable_id_after="WORLD-COPY",
            carrier_before="A",
            carrier_after="B",
            authority_preserved=True,
            state_preserved=True,
            evidence_lineage_preserved=True,
            return_target_preserved=True,
            reentry_binding_preserved=True,
            capability_semantics_preserved=True,
            resource_semantics_preserved=True,
        ))
        self.assertEqual(result.disposition, PortableTransitionDisposition.FAIL_IDENTITY_DRIFT)


if __name__ == "__main__":
    unittest.main()
