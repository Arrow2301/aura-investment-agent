import unittest

import pandas as pd

from backtesting.engine import run


class BacktestTests(unittest.TestCase):
    def test_entry_and_exit_execute_on_next_open_with_costs(self):
        dates = pd.date_range("2025-01-01", periods=4)
        data = pd.DataFrame({"Open": [100, 110, 120, 130], "High": [101, 111, 121, 131],
                             "Low": [99, 109, 119, 129], "Close": [100, 110, 120, 130]}, index=dates)
        signals = pd.Series(["BUY", "EXIT", "HOLD", "HOLD"], index=dates)
        result = run(data, signals, stop_pct=.5, target_pct=.5, fee_bps=10, slippage_bps=0)
        trade = result["trades"][0]
        self.assertEqual(trade["entry_time"], dates[1])
        self.assertEqual(trade["exit_time"], dates[2])
        self.assertAlmostEqual(trade["entry_price"], 110.11)
        self.assertAlmostEqual(trade["exit_price"], 119.88)

    def test_same_bar_stop_wins_over_target(self):
        dates = pd.date_range("2025-01-01", periods=2)
        data = pd.DataFrame({"Open": [100, 100], "High": [101, 120], "Low": [99, 80], "Close": [100, 100]}, index=dates)
        result = run(data, pd.Series(["BUY", "HOLD"], index=dates), fee_bps=0, slippage_bps=0)
        self.assertEqual(result["trades"][0]["exit_reason"], "stop")

    def test_exit_without_position_does_not_short(self):
        dates = pd.date_range("2025-01-01", periods=2)
        data = pd.DataFrame({"Open": [100, 90], "High": [101, 91], "Low": [99, 89], "Close": [100, 90]}, index=dates)
        result = run(data, pd.Series(["EXIT", "HOLD"], index=dates))
        self.assertEqual(result["metrics"]["trade_count"], 0)

    def test_missing_ohlc_returns_clear_error(self):
        result = run(pd.DataFrame({"Close": [1]}), pd.Series(["BUY"]))
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
