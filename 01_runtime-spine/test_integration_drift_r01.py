import unittest

from integration_drift_r01 import (
    DriftDisposition,
    IntegrationDriftEvidence,
    qualify_integration_drift,
)


class IntegrationDriftR01Tests(unittest.TestCase):
    def test_clean_current_base_qualifies(self):
        result = qualify_integration_drift(
            IntegrationDriftEvidence(0, False, False, False, True)
        )
        self.assertEqual(result.disposition, DriftDisposition.QUALIFIED_CANDIDATE)

    def test_path_overlap_holds_even_if_git_may_report_mergeable_elsewhere(self):
        result = qualify_integration_drift(
            IntegrationDriftEvidence(2, True, False, True, True)
        )
        self.assertEqual(result.disposition, DriftDisposition.HOLD)
        self.assertIn("CHANGED_PATH_OVERLAP_REQUIRES_RECONCILIATION", result.reasons)

    def test_instruction_drift_requires_requalification(self):
        result = qualify_integration_drift(
            IntegrationDriftEvidence(8, False, True, False, True)
        )
        self.assertEqual(result.disposition, DriftDisposition.HOLD)
        self.assertIn("INSTRUCTION_DRIFT_NOT_REQUALIFIED", result.reasons)

    def test_base_drift_requires_fresh_regression_evidence(self):
        result = qualify_integration_drift(
            IntegrationDriftEvidence(8, False, False, True, False)
        )
        self.assertEqual(result.disposition, DriftDisposition.HOLD)
        self.assertIn("BASE_DRIFT_REGRESSION_NOT_OBSERVED", result.reasons)

    def test_non_overlapping_requalified_drift_can_remain_candidate(self):
        result = qualify_integration_drift(
            IntegrationDriftEvidence(8, False, True, True, True)
        )
        self.assertEqual(result.disposition, DriftDisposition.QUALIFIED_CANDIDATE)


if __name__ == "__main__":
    unittest.main()
