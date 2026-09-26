"""Single bounded execution entry for the NFN R2 candidate surfaces.

This runner does not deploy, merge, mutate external systems, or promote claims.
Exit code is non-zero when any bounded regression fails.
"""
from __future__ import annotations

import sys
import unittest


TEST_MODULES = (
    "test_nfn_resolver_r01",
    "test_field_feedback_r01",
    "test_qualification_budget_r01",
    "test_resource_effect_accounting_r01",
    "test_r2_operational_spine_r01",
    "test_carrier_current_resolver_r01",
    "test_environment_field_r01",
    "test_integration_drift_r01",
)


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite(loader.loadTestsFromName(name) for name in TEST_MODULES)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
