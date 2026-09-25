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

    for i in range(1, len(frame)):
        previous_signal = aligned.iloc[i - 1]
        bar = frame.iloc[i]
        if position is None and previous_signal == "BUY":
            entry = float(bar["Open"]) * (1 + cost)
            position = {"signal_time": frame.index[i - 1], "entry_time": frame.index[i], "entry": entry}
        if position is None:
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

    if position is not None:  # mark the remaining paper position to the last close
        exit_price = float(frame["Close"].iloc[-1]) * (1 - cost)
        trade_return = exit_price / position["entry"] - 1
        equity *= 1 + trade_return
        trades.append(Trade(position["signal_time"], position["entry_time"], frame.index[-1],
                            round(position["entry"], 4), round(exit_price, 4),
                            round(trade_return * 100, 4), "end_of_data"))

    records = [asdict(t) for t in trades]
    result = {"trades": records, "metrics": _metrics(records, initial_capital, equity)}
    if len(frame) > 1:
        result["benchmark_return_pct"] = round((float(frame["Close"].iloc[-1]) / float(frame["Open"].iloc[0]) - 1) * 100, 2)
    return result


def _metrics(trades, initial, final):
    returns = [t["return_pct"] / 100 for t in trades]
    wins = [value for value in returns if value > 0]
    losses = [value for value in returns if value < 0]
    curve, peak, max_drawdown = initial, initial, 0.0
    for value in returns:
        curve *= 1 + value
        peak = max(peak, curve)
        max_drawdown = min(max_drawdown, curve / peak - 1)
    return {
        "trade_count": len(trades), "win_rate_pct": round(100 * len(wins) / len(trades), 2) if trades else 0,
        "return_pct": round((final / initial - 1) * 100, 2),
        "profit_factor": round(sum(wins) / abs(sum(losses)), 2) if losses else (float("inf") if wins else 0),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
    }
