"""Scheduled out-of-sample technical-only strategy evaluation."""
import logging
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from backtesting.engine import run as simulate
from data_engine.market_data import get_history
from data_engine.universe import SYMBOLS
from database.supabase_client import get_client

LOG = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))
STRATEGIES = ('ema_trend', 'donchian_breakout')


def historical_signals(frame, strategy):
    """All indicators are causal; breakout bands exclude today's high."""
    close = pd.to_numeric(frame['Close'])
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    if strategy == 'ema_trend':
        active = (close > ema20) & (ema20 > ema50)
        buy = active & ~active.shift(1, fill_value=False)
        exit_now = ~active & active.shift(1, fill_value=False)
    elif strategy == 'donchian_breakout':
        buy = close > close.shift(1).rolling(20).max()
        exit_now = close < ema20
    else:
        raise ValueError('Unknown strategy')
    signals = pd.Series('HOLD', index=frame.index)
    signals.loc[buy] = 'BUY'
    signals.loc[exit_now] = 'EXIT'
    signals.iloc[:55] = 'HOLD'
    return signals


def evaluate(frame, strategy, fee_bps=10, slippage_bps=5):
    if len(frame) < 320:
        return {'status': 'INSUFFICIENT', 'notes': 'At least 320 completed bars required', 'tested_bars': 0}
    split = int(len(frame) * .7)
    test = frame.iloc[split:].copy()
    if len(test) < 90:
        return {'status': 'INSUFFICIENT', 'notes': 'Test window too short', 'tested_bars': len(test)}
    # Compute features from past bars, then evaluate only the held-out last 30%.
    signals = historical_signals(frame, strategy).iloc[split:]
    result = simulate(test, signals, fee_bps=fee_bps, slippage_bps=slippage_bps)
    metrics = result['metrics']
    profit = metrics['profit_factor']
    return {'status': 'OK' if metrics['trade_count'] >= 5 else 'INSUFFICIENT',
            'notes': 'Held-out last 30%; at least five closed trades needed for interpretation'
                     if metrics['trade_count'] < 5 else 'Held-out last 30%; no parameter tuning',
            'train_start': frame.index[0].date().isoformat(),
            'test_start': test.index[0].date().isoformat(), 'tested_bars': len(test),
            'trade_count': metrics['trade_count'], 'win_rate_pct': metrics['win_rate_pct'],
            'return_pct': metrics['return_pct'], 'benchmark_return_pct': result.get('benchmark_return_pct'),
            'max_drawdown_pct': metrics['max_drawdown_pct'],
            'profit_factor': profit if math.isfinite(profit) else None,
            'fee_bps': fee_bps, 'slippage_bps': slippage_bps}


def run(symbols=None):
    symbols = SYMBOLS if symbols is None else symbols
    client = get_client(write=True)
    run_date = datetime.now(IST).date().isoformat()
    failures = []
    for symbol in symbols:
        try:
            history = get_history(symbol, period='5y')
            # Strip any partial current session before the test is produced.
            if history.index[-1].date().isoformat() == run_date and datetime.now(IST).hour < 16:
                history = history.iloc[:-1]
            for strategy in STRATEGIES:
                data = evaluate(history, strategy)
                client.table('strategy_backtests').upsert(
                    {'symbol': symbol, 'strategy': strategy, 'as_of': run_date,
                     'fee_bps': 10, 'slippage_bps': 5, **data},
                    on_conflict='symbol,strategy,as_of').execute()
        except Exception as exc:
            failures.append(f'{symbol}: {str(exc)[:120]}')
            LOG.exception('Backtest failed for %s', symbol)
    if failures:
        raise RuntimeError(f'{len(failures)} stock backtests failed; ' + '; '.join(failures[:5]))
    return len(symbols) * len(STRATEGIES)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
