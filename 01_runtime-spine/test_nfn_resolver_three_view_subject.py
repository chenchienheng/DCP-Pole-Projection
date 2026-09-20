import unittest

from nfn_resolver_r01 import Current, Disposition, Event, resolve_event


class ThreeViewCarrierHandoffTests(unittest.TestCase):
    """Real-subject regression for MULTI_VIEW_NFN_NATIVE_RETURN_20260920.

    This test binds the current three-view Subject to the existing bounded resolver.
    It proves only receiver narrowing and stable identity preservation; it does not
    claim receiver execution, Runtime, merge approval, or Root dispatch.
    """

    def test_machine_handoff_targets_architecture_without_root_wake(self):
        subject = "MULTI_VIEW_NFN_NATIVE_RETURN_20260920"
        need_id = f"{subject}::CARRIER_HANDOFF_01"
        current = Current(
            subject,
            need_id,
            "DRIVE-SUBJECT-REV-20260920",
            "PEER_CROSS_READ_PROVEN_BOUNDED",
        )
        event = Event(
            "CARRIER-HANDOFF",
            "MACHINE_HANDOFF",
            subject,
            need_id,
            "DRIVE-SUBJECT-REV-20260920",
            "SHARED-SUBJECT",
            ("Qinyi-Architecture",),
        )

        result = resolve_event(
            event,
            current,
            relevant_receivers=("Qinyi-Architecture", "Root"),
        )

        self.assertEqual(result.disposition, Disposition.AFFECTED)
        self.assertEqual(result.current.subject_id, subject)
        self.assertEqual(result.current.need_id, need_id)
        self.assertEqual(result.executable_affected, ("Qinyi-Architecture",))
        self.assertNotIn("Root", result.executable_affected)


if __name__ == "__main__":
    unittest.main()
