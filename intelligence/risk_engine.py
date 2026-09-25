"""Risk estimates from prior price levels or a labelled ATR breakout projection."""

import pandas as pd


def analyze(df: pd.DataFrame, minimum_reward_risk: float = 1.5) -> dict:
    required = {"Close", "High", "Low"}
    if df is None or len(df) < 21 or not required.issubset(df.columns):
        return {"score": 0, "risk": "UNKNOWN", "eligible": False, "reason": "Insufficient data for risk levels"}

    close, high, low = (pd.to_numeric(df[c], errors="coerce").squeeze() for c in ("Close", "High", "Low"))
    previous_close = close.shift(1)
    true_range = pd.concat([(high - low), (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    atr = true_range.rolling(14).mean().iloc[-1]
    entry = close.iloc[-1]
    support = low.iloc[-21:-1].min()
    resistance = high.iloc[-21:-1].max()
    if pd.isna(atr) or pd.isna(entry) or atr <= 0 or entry <= 0:
        return {"score": 0, "risk": "UNKNOWN", "eligible": False, "reason": "Invalid price or volatility data"}

    stop = max(float(support), float(entry - 1.5 * atr))
    # A breakout has no overhead resistance in the lookback window. Use a
    # predeclared 3-ATR projection, explicitly labelled as a model estimate.
    breakout = float(entry) > float(resistance)
    target = float(entry + 3 * atr) if breakout else float(resistance)
    basis = '3-ATR projection after breakout' if breakout else 'prior 20-session resistance'
    risk_amount, reward_amount = float(entry - stop), float(target - entry)
    ratio = reward_amount / risk_amount if risk_amount > 0 and reward_amount > 0 else 0.0
    eligible = ratio >= minimum_reward_risk
    risk_pct = risk_amount / float(entry) * 100 if risk_amount > 0 else 0.0
    return {
        "score": round(max(0, min(100, 80 - risk_pct * 5 + (10 if eligible else -20))), 2),
        "risk": "LOW" if risk_pct <= 3 else "MEDIUM" if risk_pct <= 6 else "HIGH",
        "entry": round(float(entry), 2), "stop": round(stop, 2), "target": round(target, 2),
        "target_basis": basis,
        "risk_pct": round(risk_pct, 2), "reward_pct": round(max(0, reward_amount / float(entry) * 100), 2),
        "reward_risk": round(ratio, 2), "eligible": eligible,
        "reason": f"{basis}: estimated reward/risk {ratio:.2f} is {'at or above' if eligible else 'below'} the {minimum_reward_risk:.2f} minimum",
    }
