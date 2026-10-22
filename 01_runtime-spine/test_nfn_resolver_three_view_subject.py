import json
import unittest
from pathlib import Path

from nfn_resolver_r01 import Current, Disposition, Event, resolve_event


FIXTURE = Path(__file__).with_name("fixtures") / "multi_view_nfn_native_return_20260920.json"


class ThreeViewCarrierHandoffTests(unittest.TestCase):
    """Real-subject regression for MULTI_VIEW_NFN_NATIVE_RETURN_20260920.

    The fixture is the machine-readable handoff surface. This test proves only
    stable identity preservation and affected-receiver narrowing. It does not
    claim receiver execution, Runtime, merge approval, or Root dispatch.
    """

    def test_machine_handoff_from_fixture_targets_architecture_without_root_wake(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        subject = payload["subject_id"]
        need_id = payload["need_id"]
        current = Current(
            subject,
            need_id,
            payload["current"]["source_version"],
            payload["current"]["state"],
        )
        event_data = payload["event"]
        event = Event(
            event_data["event_id"],
            event_data["event_type"],
            subject,
            need_id,
            event_data["source_version"],
            event_data["authority_scope"],
            tuple(event_data["affected_candidates"]),
        )

        result = resolve_event(
            event,
            current,
            relevant_receivers=tuple(payload["relevant_receivers"]),
        )

        expected = payload["expected"]
        self.assertEqual(result.disposition.value, expected["disposition"])
        self.assertEqual(result.current.subject_id, subject)
        self.assertEqual(result.current.need_id, need_id)
        self.assertEqual(result.executable_affected, tuple(expected["executable_affected"]))
        for receiver in expected["excluded_from_execution"]:
            self.assertNotIn(receiver, result.executable_affected)
        self.assertFalse(expected["runtime_claim"])
        self.assertFalse(expected["receiver_acceptance_claim"])


if __name__ == "__main__":
    unittest.main()
