import pandas as pd


def technical_score(data):

    close = data["Close"]

    # Handle yfinance multi-column format
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = close.dropna()

    if len(close) < 200:
        return 0

    latest = float(close.iloc[-1])

    ma50 = float(
        close.rolling(50).mean().iloc[-1]
    )

    ma200 = float(
        close.rolling(200).mean().iloc[-1]
    )

    score = 0

    if latest > ma50:
        score += 50

    if latest > ma200:
        score += 50

    return scoredef technical_score(data):
    close = data["Close"]
    if hasattr(close, "iloc") and len(close) > 200:
        latest=float(close.iloc[-1])
        ma50=float(close.rolling(50).mean().iloc[-1])
        ma200=float(close.rolling(200).mean().iloc[-1])
        score=0
        if latest > ma50: score += 50
        if latest > ma200: score += 50
        return score
    return 0
