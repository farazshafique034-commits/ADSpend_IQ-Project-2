import unittest
import pandas as pd

from utils.metrics import (
    calculate_kpis,
    platform_performance
)


class TestMarketingMetrics(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "platform": ["Google", "Google"],
            "impressions": [1000, 2000],
            "clicks": [100, 100],
            "spend": [500, 500],
            "conversions": [10, 20],
            "revenue": [2000, 3000]
        })

    def test_aggregated_kpis(self):
        kpis = calculate_kpis(self.df)

        self.assertEqual(kpis["impressions"], 3000)
        self.assertEqual(kpis["clicks"], 200)
        self.assertEqual(kpis["spend"], 1000)
        self.assertEqual(kpis["conversions"], 30)
        self.assertEqual(kpis["revenue"], 5000)

        self.assertAlmostEqual(kpis["ctr"], 6.67)
        self.assertAlmostEqual(kpis["cpc"], 5.00)
        self.assertAlmostEqual(kpis["roas"], 5.00)
        self.assertAlmostEqual(
            kpis["conversion_rate"], 15.00
        )

    def test_platform_aggregation(self):
        result = platform_performance(self.df)

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(
            result.iloc[0]["roas"], 5.0
        )


if __name__ == "__main__":
    unittest.main()
