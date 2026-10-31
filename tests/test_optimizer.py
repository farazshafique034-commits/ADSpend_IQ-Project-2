import unittest
import numpy as np

from utils.data_generator import generate_ad_data
from utils.optimizer import (
    optimize_budget,
    build_scenarios
)


class TestBudgetOptimizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = generate_ad_data(
            n_records=2000,
            seed=42
        )

    def test_full_budget_allocated(self):
        result, summary = optimize_budget(
            self.df, budget=1_000_000
        )

        self.assertAlmostEqual(
            result["recommended_budget"].sum(),
            1_000_000,
            places=2
        )

        self.assertAlmostEqual(
            result["allocation_pct"].sum(),
            100.0,
            places=3
        )

    def test_allocation_constraints(self):
        result, _ = optimize_budget(
            self.df,
            budget=1_000_000,
            min_share=0.05,
            max_share=0.45
        )

        shares = result["allocation_pct"] / 100

        self.assertTrue(
            np.all(shares >= 0.05 - 1e-6)
        )

        self.assertTrue(
            np.all(shares <= 0.45 + 1e-6)
        )

    def test_positive_estimated_revenue(self):
        result, summary = optimize_budget(
            self.df, budget=1_000_000
        )

        self.assertGreater(
            summary["estimated_revenue"], 0
        )

        self.assertTrue(
            np.isfinite(
                result["estimated_revenue"]
            ).all()
        )

    def test_invalid_budget(self):
        with self.assertRaises(ValueError):
            optimize_budget(
                self.df, budget=-100
            )

    def test_scenario_generation(self):
        scenarios = build_scenarios(
            self.df, budget=1_000_000
        )

        self.assertEqual(len(scenarios), 3)


if __name__ == "__main__":
    unittest.main()
