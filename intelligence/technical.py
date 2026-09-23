import pandas as pd
import ta

def analyse(data):
    close = data["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:,0]

    close = close.dropna()

    if len(close) < 200:
        return 0

    score = 0

    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    macd = ta.trend.MACD(close).macd_diff().iloc[-1]

    if rsi > 50:
        score += 25

    if macd > 0:
        score += 25

    if close.iloc[-1] > close.rolling(50).mean().iloc[-1]:
        score += 25

    if close.iloc[-1] > close.rolling(200).mean().iloc[-1]:
        score += 25

    return score
