import pandas as pd


def calculate_score(data):

    score = 0

    # Handle Yahoo Finance multi-level columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)


    latest = data.iloc[-1]


    close = float(latest["Close"])
    volume = float(latest["Volume"])


    ma50 = float(
        data["Close"]
        .rolling(50)
        .mean()
        .iloc[-1]
    )


    ma200 = float(
        data["Close"]
        .rolling(200)
        .mean()
        .iloc[-1]
    )


    avg_volume = float(
        data["Volume"]
        .mean()
    )


    if close > ma50:
        score += 50


    if volume > avg_volume:
        score += 25


    if close > ma200:
        score += 25


    return score
