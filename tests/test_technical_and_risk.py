import unittest

import numpy as np
import pandas as pd

from intelligence.risk_engine import analyze as analyze_risk
from intelligence.technical_engine import analyze as analyze_technical


def market(rows=80):
    close = pd.Series(np.linspace(100, 140, rows))
    return pd.DataFrame({"Open": close, "High": close + 2, "Low": close - 2, "Close": close, "Volume": 1_000})


class TechnicalAndRiskTests(unittest.TestCase):
    def test_missing_market_data_is_rejected(self):
        self.assertFalse(analyze_technical(pd.DataFrame({"Close": [1]}))["valid"])
        self.assertFalse(analyze_risk(pd.DataFrame())["eligible"])

    def test_signal_does_not_look_into_future_rows(self):
        history = market()
        before = analyze_technical(history.iloc[:70])
        changed_future = history.copy()
        changed_future.loc[70:, "Close"] = 10_000
        after = analyze_technical(changed_future.iloc[:70])
        self.assertEqual(before, after)

    def test_target_is_observed_resistance_not_inflated(self):
        history = market()
        setup = analyze_risk(history, minimum_reward_risk=50)
        self.assertEqual(setup["target"], round(float(history["High"].iloc[-21:-1].max()), 2))
        self.assertFalse(setup["eligible"])


if __name__ == "__main__":
    unittest.main()
