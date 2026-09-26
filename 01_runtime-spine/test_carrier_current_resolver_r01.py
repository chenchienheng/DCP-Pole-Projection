import unittest

from carrier_current_resolver_r01 import (
    CarrierCurrentCandidate,
    CarrierKind,
    CurrentResolutionDisposition,
    qualify_evidence_source,
    resolve_current,
)


def candidate(carrier=CarrierKind.DRIVE, locator="thin", **changes):
    values = dict(
        carrier=carrier,
        locator=locator,
        stable_referent="WORLD",
        purpose="CONSTRUCTION_CURRENT",
        declared_current_pointer=True,
        current_for_purpose=True,
        source_observed=True,
        mutable_current_authority=True,
        evidence_authority=True,
        observed_at="2026-09-26T13:52:00+08:00",
    )
    values.update(changes)
    return CarrierCurrentCandidate(**values)


class CarrierCurrentResolverTests(unittest.TestCase):
    def test_pointer_resolves(self):
        result = resolve_current(
            (candidate(),), stable_referent="WORLD", purpose="CONSTRUCTION_CURRENT"
        )
        self.assertEqual(result.disposition, CurrentResolutionDisposition.RESOLVED)

    def test_memory_only_holds(self):
        result = resolve_current(
            (candidate(CarrierKind.MEMORY, "memory"),),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        self.assertEqual(result.disposition, CurrentResolutionDisposition.HOLD)

    def test_newer_history_without_pointer_does_not_replace_current(self):
        current = candidate(observed_at="2026-09-26T10:00:00+08:00")
        history = candidate(
            CarrierKind.LIBRARY,
            "history",
            declared_current_pointer=False,
            observed_at="2026-09-26T14:00:00+08:00",
        )
        result = resolve_current(
            (history, current), stable_referent="WORLD", purpose="CONSTRUCTION_CURRENT"
        )
        self.assertEqual(result.locator, "thin")

    def test_order_does_not_change_resolution(self):
        cue = candidate(CarrierKind.MEMORY, "cue", mutable_current_authority=False)
        current = candidate()
        a = resolve_current((cue, current), stable_referent="WORLD", purpose="CONSTRUCTION_CURRENT")
        b = resolve_current((current, cue), stable_referent="WORLD", purpose="CONSTRUCTION_CURRENT")
        self.assertEqual(a.locator, b.locator)

    def test_multiple_current_pointers_hold(self):
        result = resolve_current(
            (candidate(), candidate(CarrierKind.GITHUB, "pr391")),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        self.assertEqual(result.disposition, CurrentResolutionDisposition.HOLD)

    def test_wrong_purpose_holds(self):
        result = resolve_current(
            (candidate(purpose="HISTORY"),),
            stable_referent="WORLD",
            purpose="CONSTRUCTION_CURRENT",
        )
        self.assertEqual(result.disposition, CurrentResolutionDisposition.HOLD)

    def test_navigation_and_evidence_are_separate(self):
        self.assertFalse(qualify_evidence_source(candidate(evidence_authority=False)))

    def test_raw_string_carrier_is_rejected_at_input_boundary(self):
        with self.assertRaises(TypeError):
            candidate("MEMORY", "raw-string")

    def test_string_boolean_is_rejected_at_input_boundary(self):
        with self.assertRaises(TypeError):
            candidate(mutable_current_authority="false")

    def test_empty_locator_is_rejected_at_input_boundary(self):
        with self.assertRaises(TypeError):
            candidate(locator="   ")


if __name__ == "__main__":
    unittest.main()
