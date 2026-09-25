"""Explainable, point-in-time technical signals used by the daily scan."""

import numpy as np
import pandas as pd


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    losses = -delta.clip(upper=0).ewm(alpha=1 / period, adjust=False).mean()
    relative_strength = gains / losses.replace(0, np.nan)
    return (100 - (100 / (1 + relative_strength))).fillna(50)


def analyze(df: pd.DataFrame) -> dict:
    """Evaluate independent strategies using only rows available at evaluation time.

    The returned ``strategies`` map is deliberately persisted/displayed so a score
    is never an unexplained black box. This function does not shift data backwards.
    """
    required = {"Close", "High", "Low", "Volume"}
    if df is None or df.empty or not required.issubset(df.columns) or len(df) < 55:
        return {"score": 0, "signals": ["Insufficient market history"], "strategies": {}, "valid": False}

    close = pd.to_numeric(df["Close"], errors="coerce").squeeze()
    volume = pd.to_numeric(df["Volume"], errors="coerce").squeeze()
    if close.isna().iloc[-1] or close.dropna().size < 55:
        return {"score": 0, "signals": ["Latest price is missing"], "strategies": {}, "valid": False}

    ema20, ema50 = close.ewm(span=20, adjust=False).mean(), close.ewm(span=50, adjust=False).mean()
    rsi = _rsi(close)
    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    middle = close.rolling(20).mean()
    lower = middle - 2 * close.rolling(20).std()
    prior_high = close.shift(1).rolling(20).max()
    average_volume = volume.shift(1).rolling(20).mean()

    strategies = {
        "ema_trend": bool(ema20.iloc[-1] > ema50.iloc[-1] and close.iloc[-1] > ema20.iloc[-1]),
        "rsi_macd": bool(45 <= rsi.iloc[-1] <= 70 and macd.iloc[-1] > macd_signal.iloc[-1]),
        "bollinger_recovery": bool(close.iloc[-2] <= lower.iloc[-2] and close.iloc[-1] > lower.iloc[-1]),
        "donchian_breakout": bool(close.iloc[-1] > prior_high.iloc[-1]),
        "volume_breakout": bool(close.iloc[-1] > prior_high.iloc[-1] and volume.iloc[-1] > 1.5 * average_volume.iloc[-1]),
        "rsi_trend_shift": bool(rsi.iloc[-2] <= 50 < rsi.iloc[-1]),
    }
    labels = {
        "ema_trend": "Price is above rising 20/50-day EMA trend",
        "rsi_macd": "RSI and MACD confirm positive momentum",
        "bollinger_recovery": "Price recovered inside the lower Bollinger Band",
        "donchian_breakout": "Close broke above the prior 20-day high",
        "volume_breakout": "Breakout volume is at least 1.5x its prior average",
        "rsi_trend_shift": "RSI crossed above its 50 midpoint",
    }
    active = [labels[name] for name, passed in strategies.items() if passed]
    # 40 is neutral; each independently confirmed strategy contributes 10.
    return {
        "score": min(100, 40 + 10 * len(active)),
        "signals": active or ["No bullish technical strategy confirmed"],
        "strategies": strategies,
        "indicators": {"rsi": round(float(rsi.iloc[-1]), 2), "ema20": round(float(ema20.iloc[-1]), 2), "ema50": round(float(ema50.iloc[-1]), 2)},
        "valid": True,
    }
