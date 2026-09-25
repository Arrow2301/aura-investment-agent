import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pandas as pd
from automation.daily_run import analyze_symbol, run
from automation.outcomes import realized_returns
from portfolio.ledger import summarize


class PipelineTests(unittest.TestCase):
    @patch('automation.daily_run.get_client')
    @patch('automation.daily_run.analyze_symbol')
    @patch('automation.daily_run.save_signal')
    @patch('automation.daily_run.save_analysis')
    def test_partial_run_persists_failure_and_fails_action(self, save_analysis, save_signal, analyze, client):
        analyze.side_effect = [dict(symbol='A', market_date='2026-09-25', aura={'action': 'WATCH'}),
                               RuntimeError('vendor timeout')]
        client.return_value = MagicMock()
        with self.assertRaises(RuntimeError):
            run(['A', 'B'])
        record = client.return_value.table.return_value.update.call_args.args[0]
        self.assertEqual(record['status'], 'PARTIAL')
        self.assertEqual(record['failure_count'], 1)
        self.assertEqual(save_signal.call_count, 1)

    def test_outcomes_wait_for_complete_trading_sessions(self):
        dates = pd.bdate_range('2026-01-01', periods=8)
        df = pd.DataFrame({'Close': range(100, 108)}, index=dates)
        outcomes = realized_returns(df, dates[0].date().isoformat())
        self.assertAlmostEqual(outcomes['return_5d_pct'], 5.0)
        self.assertNotIn('return_20d_pct', outcomes)

    @patch('automation.daily_run.get_history')
    @patch('automation.daily_run.get_fundamentals')
    def test_intraday_bar_is_excluded(self, info, get_history):
        now = datetime(2026, 9, 25, 12, tzinfo=timezone(timedelta(hours=5, minutes=30)))
        dates = pd.bdate_range(end='2026-09-25', periods=70)
        close = pd.Series(range(100, 170), index=dates)
        get_history.return_value = pd.DataFrame({'Open': close, 'High': close + 2,
                                                    'Low': close - 2, 'Close': close,
                                                    'Volume': 10000}, index=dates)
        info.return_value = {}
        result = analyze_symbol('TEST.NS', now)
        self.assertEqual(result['market_date'], '2026-09-24')
        self.assertEqual(result['current_price'], 168.0)
        self.assertNotEqual(result['aura']['action'], 'BUY_CANDIDATE')


class LedgerTests(unittest.TestCase):
    def test_partial_sale_average_cost_and_realized_pnl(self):
        trades = [{'symbol': 'ABC.NS', 'side': side, 'quantity': qty, 'price': price,
                   'traded_at': str(i)} for i, (side, qty, price) in
                  enumerate([('BUY', 2, 100), ('BUY', 2, 200), ('SELL', 1, 180)])]
        result = summarize(trades)['ABC.NS']
        self.assertEqual(result['quantity'], 3)
        self.assertEqual(result['cost'], 450)
        self.assertEqual(result['realized_pnl'], 30)
        with self.assertRaises(ValueError):
            summarize(trades + [{'symbol': 'ABC.NS', 'side': 'SELL', 'quantity': 4,
                                 'price': 200, 'traded_at': '3'}])
