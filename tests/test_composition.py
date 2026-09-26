import unittest

from dcp_kernel.composition import CompositionInput, CompositionUnit, UnitState, assess_composition
from dcp_kernel.models import Decision


class CompositionTests(unittest.TestCase):
    def test_excludes_rights_or_authority_violations(self):
        result = assess_composition(CompositionInput(
            composition_id="C1",
            required_effect="REPORT",
            receiver="R",
            units=(
                CompositionUnit("u1", "s1", "CURRENT", False, True, True, True, True, "DESCRIPTIVE"),
                CompositionUnit("u2", "s2", "CURRENT", True, True, True, True, True, "DESCRIPTIVE"),
            ),
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.used_units, ("u2",))
        self.assertEqual(result.excluded_units, ("u1",))

    def test_holds_insufficient_or_incompatible_units(self):
        result = assess_composition(CompositionInput(
            composition_id="C2",
            required_effect="MODEL",
            receiver="R",
            units=(
                CompositionUnit("u1", "s1", "CURRENT", True, True, False, True, True, "CANDIDATE"),
                CompositionUnit("u2", "s2", "CURRENT", True, True, True, False, True, "CANDIDATE"),
            ),
        ))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(set(result.held_units), {"u1", "u2"})

    def test_historical_unit_is_not_silently_promoted(self):
        result = assess_composition(CompositionInput(
            composition_id="C3",
            required_effect="ANALYSIS",
            receiver="R",
            units=(
                CompositionUnit("u1", "s1", "HISTORICAL", True, True, True, True, True, "DESCRIPTIVE"),
                CompositionUnit("u2", "s2", "CURRENT", True, True, True, True, True, "DESCRIPTIVE"),
            ),
        ))
        self.assertEqual(result.decision, Decision.PASS)
        self.assertEqual(result.used_units, ("u2",))
        self.assertEqual(result.held_units, ("u1",))


if __name__ == "__main__":
    unittest.main()
