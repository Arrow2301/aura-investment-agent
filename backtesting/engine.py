"""Long-only event backtester with explicit next-bar execution."""

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class Trade:
    signal_time: object
    entry_time: object
    exit_time: object
    entry_price: float
    exit_price: float
    return_pct: float
    exit_reason: str


def run(data: pd.DataFrame, signals: pd.Series, stop_pct=0.05, target_pct=0.10,
        fee_bps=10.0, slippage_bps=5.0, initial_capital=100_000.0) -> dict:
    """Backtest BUY/EXIT signals, filled at the *following* bar's open.

    Stops and targets are checked from the entry bar onward. If both occur in one
    candle, the stop wins (a deliberately conservative assumption). EXIT closes a
    long and never creates a short position.
    """
    required = {"Open", "High", "Low", "Close"}
    if data is None or data.empty or not required.issubset(data.columns):
        return {"trades": [], "metrics": _metrics([], initial_capital, initial_capital), "error": "Missing OHLC market data"}
    frame = data.sort_index().copy()
    aligned = signals.reindex(frame.index).fillna("HOLD").astype(str).str.upper()
    cost = (fee_bps + slippage_bps) / 10_000
    trades, position, equity = [], None, float(initial_capital)
    daily_curve = [equity]

    for i in range(1, len(frame)):
        previous_signal = aligned.iloc[i - 1]
        bar = frame.iloc[i]
        if position is None and previous_signal == "BUY":
            entry = float(bar["Open"]) * (1 + cost)
            position = {"signal_time": frame.index[i - 1], "entry_time": frame.index[i], "entry": entry}
        if position is None:
            daily_curve.append(equity)
            continue

        stop, target = position["entry"] * (1 - stop_pct), position["entry"] * (1 + target_pct)
        reason, raw_exit = None, None
        if previous_signal == "EXIT" and frame.index[i] != position["entry_time"]:
            reason, raw_exit = "signal", float(bar["Open"])
        elif float(bar["Open"]) <= stop:
            reason, raw_exit = "stop_gap", float(bar["Open"])
        elif float(bar["Low"]) <= stop:
            reason, raw_exit = "stop", stop
        elif float(bar["High"]) >= target:
            reason, raw_exit = "target", target
        if reason:
            exit_price = raw_exit * (1 - cost)
            trade_return = exit_price / position["entry"] - 1
            equity *= 1 + trade_return
            trades.append(Trade(position["signal_time"], position["entry_time"], frame.index[i],
                                round(position["entry"], 4), round(exit_price, 4),
                                round(trade_return * 100, 4), reason))
            position = None
        daily_curve.append(equity * float(bar['Close']) / position['entry'] if position else equity)

    open_position = None
    if position is not None:
        open_position = {'entry_time': position['entry_time'], 'entry_price': position['entry'],
                         'last_close': float(frame['Close'].iloc[-1])}
        equity = daily_curve[-1]  # mark the open trade; it is not counted as a realized win

    records = [asdict(t) for t in trades]
    result = {"trades": records, "open_position": open_position,
              "metrics": _metrics(records, initial_capital, equity, daily_curve)}
    if len(frame) > 1:
        result["benchmark_return_pct"] = round((float(frame["Close"].iloc[-1]) / float(frame["Open"].iloc[0]) - 1) * 100, 2)
    return result


def _metrics(trades, initial, final, daily_curve=None):
    returns = [t["return_pct"] / 100 for t in trades]
    wins = [value for value in returns if value > 0]
    losses = [value for value in returns if value < 0]
    peak, max_drawdown = initial, 0.0
    for value in daily_curve or [initial, final]:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, value / peak - 1)
    return {
        "trade_count": len(trades), "win_rate_pct": round(100 * len(wins) / len(trades), 2) if trades else 0,
        "return_pct": round((final / initial - 1) * 100, 2),
        "profit_factor": round(sum(wins) / abs(sum(losses)), 2) if losses else (float("inf") if wins else 0),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
    }
