import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

from automation.notify import digest_text, exit_reason, send_once, monitor_portfolio, IST
from datetime import datetime, timedelta
from automation.backtest_run import historical_signals, evaluate
from backtesting.engine import run as simulate
from intelligence.exit_engine import analyze as exit_analyze
from intelligence.risk_engine import analyze as risk_analyze
from intelligence.technical_engine import analyze as technical_analyze
from intelligence.fundamental_engine import analyze as fundamental_analyze
from intelligence.quality_engine import analyze as quality_analyze
from intelligence.decision_brain import calculate_aura_score
from portfolio.ledger import summarize


def prices(n=400):
    dates = pd.bdate_range('2024-01-01', periods=n)
    close = pd.Series(100 + np.linspace(0, 30, n) + np.sin(np.arange(n) / 7) * 6, index=dates)
    return pd.DataFrame({'Open': close, 'High': close + 2, 'Low': close - 2,
                         'Close': close, 'Volume': 1000}, index=dates)


class AutomationTests(unittest.TestCase):
    def test_exit_is_not_derived_from_future(self):
        bars = prices()
        prior = exit_analyze(bars.iloc[:300])
        later = bars.copy()
        later.iloc[300:, later.columns.get_loc('Close')] = 1
        self.assertEqual(prior, exit_analyze(later.iloc[:300]))

    def test_heldout_backtest_uses_next_session_and_handles_sparse_trades(self):
        bars = prices()
        before = historical_signals(bars.iloc[:300], 'ema_trend')
        modified = bars.copy()
        modified.loc[modified.index[300:], 'Close'] = 1000
        self.assertTrue(before.equals(historical_signals(modified.iloc[:300], 'ema_trend')))
        result = evaluate(bars, 'ema_trend')
        self.assertEqual(result['tested_bars'], 120)
        self.assertIn(result['status'], ('OK', 'INSUFFICIENT'))

    def test_open_trade_not_counted_as_a_win_and_gap_fills_at_open(self):
        dates = pd.bdate_range('2026-01-01', periods=3)
        candles = pd.DataFrame({'Open':[100,100,90], 'High':[101,101,91],
                                'Low':[99,99,89], 'Close':[100,100,90]}, index=dates)
        result = simulate(candles, pd.Series(['BUY','HOLD','HOLD'], index=dates),
                          fee_bps=0, slippage_bps=0)
        self.assertEqual(result['trades'][0]['exit_reason'], 'stop_gap')
        self.assertEqual(result['trades'][0]['exit_price'], 90)
        candles.loc[dates[2], ['Open','High','Low','Close']] = [100,101,99,100]
        result = simulate(candles, pd.Series(['BUY','HOLD','HOLD'], index=dates),
                          fee_bps=0, slippage_bps=0)
        self.assertEqual(result['metrics']['trade_count'], 0)
        self.assertIsNotNone(result['open_position'])

    def test_fifo_lots_keep_remaining_stop_after_partial_sale(self):
        rows = [dict(id=1, symbol='A.NS', side='BUY', quantity=1, price=100,
                     stop_price=90, target_price=120, traded_at='1'),
                dict(id=2, symbol='A.NS', side='BUY', quantity=2, price=110,
                     stop_price=100, target_price=130, traded_at='2'),
                dict(id=3, symbol='A.NS', side='SELL', quantity=1, price=120,
                     traded_at='3')]
        position = summarize(rows)['A.NS']
        self.assertEqual(position['stop'], 100)
        self.assertEqual(position['target'], 130)
        self.assertEqual(position['closed_exits'], 1)
        self.assertEqual(position['winning_exits'], 1)
        self.assertEqual(exit_reason(position, 99, 'WATCH'), 'STOP LEVEL REACHED')

    @patch('automation.notify.send_telegram')
    def test_alert_not_resent_after_stored_delivery(self, send):
        client = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [{'event_key':'existing'}]
        sent = send_once(client, 'existing', 'POSITION_EXIT', 'A.NS', '2026-09-25',
                         'test', {'AURA_USER_ID':'u', 'TELEGRAM_CHAT_ID':'c', 'TELEGRAM_BOT_TOKEN':'token'})
        self.assertFalse(sent)
        send.assert_not_called()

    def test_digest_distinguishes_entry_exit(self):
        message = digest_text([{'symbol':'A.NS','action':'BUY_CANDIDATE','aura_score':80,'price':100},
                               {'symbol':'B.NS','action':'EXIT_CANDIDATE','aura_score':20,'price':50}],
                              '2026-09-25','SUCCESS')
        self.assertIn('A.NS', message)
        self.assertIn('B.NS', message)
        self.assertIn('Paper research only', message)

    @patch('automation.notify.send_once')
    @patch('automation.notify.get_client')
    @patch('automation.notify.credentials')
    def test_stale_after_close_cannot_alert_or_overwrite_portfolio(self, credentials, get_client, send):
        credentials.return_value = {'AURA_USER_ID': 'test-id', 'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': 'chat'}
        trades = MagicMock()
        trades.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {'symbol':'A.NS','side':'BUY','quantity':1,'price':100,'traded_at':'2026-09-20'}]
        signals = MagicMock()
        yesterday = (datetime.now(IST).date() - timedelta(days=1)).isoformat()
        signals.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {'symbol':'A.NS','action':'EXIT_CANDIDATE','price':80,'analysis_date':yesterday}]
        get_client.return_value.table.side_effect = lambda name: trades if name == 'paper_trades' else signals
        result = monitor_portfolio(intraday=False)
        self.assertIn('skipped', result)
        send.assert_not_called()
        self.assertNotIn('portfolio_daily', [call.args[0] for call in get_client.return_value.table.call_args_list])

    def test_breakout_candidate_is_possible_but_missing_fundamentals_suppress_buy(self):
        close = [100 + i * .1 for i in range(79)] + [112]
        bars = pd.DataFrame({'Open':close, 'High':[x+1 for x in close],
                             'Low':[x-1 for x in close], 'Close':close,
                             'Volume':[1000]*79+[2000]})
        risk = risk_analyze(bars)
        self.assertEqual(risk['target_basis'], '3-ATR projection after breakout')
        self.assertTrue(risk['eligible'])
        info = {'roe':.2,'profit_margin':.15,'revenue_growth':.15,'debt_equity':50}
        technical = technical_analyze(bars)
        self.assertEqual(calculate_aura_score(technical, fundamental_analyze(info),
                                               quality_analyze(info), risk)['action'], 'BUY_CANDIDATE')
        self.assertNotEqual(calculate_aura_score(technical, fundamental_analyze({}),
                                                  quality_analyze({}), risk)['action'], 'BUY_CANDIDATE')


if __name__ == '__main__':
    unittest.main()
