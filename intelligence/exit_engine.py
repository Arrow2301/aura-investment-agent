"""Rules for exiting an existing long; never a short-selling instruction."""
import pandas as pd


def analyze(history: pd.DataFrame) -> dict:
    if history is None or len(history) < 55 or 'Close' not in history:
        return {'exit': False, 'reason': 'Insufficient completed daily bars'}
    close = pd.to_numeric(history['Close'], errors='coerce')
    if pd.isna(close.iloc[-1]):
        return {'exit': False, 'reason': 'Latest close unavailable'}
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    # Exit if the close crosses below the long trend, or an established downtrend persists.
    breakdown = close.iloc[-2] >= ema50.iloc[-2] and close.iloc[-1] < ema50.iloc[-1]
    downtrend = close.iloc[-1] < ema50.iloc[-1] and ema20.iloc[-1] < ema50.iloc[-1]
    if breakdown:
        return {'exit': True, 'reason': 'Close crossed below the 50-session EMA'}
    if downtrend:
        return {'exit': True, 'reason': 'Close below the 50-session EMA with a bearish 20/50 EMA trend'}
    return {'exit': False, 'reason': 'Long-trend exit rule not triggered'}
