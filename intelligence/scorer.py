def score(data):

    # Handle yfinance multi-column format
    if hasattr(data.columns, "levels"):
        close = data["Close"].iloc[:, 0]
    else:
        close = data["Close"]


    latest = float(close.iloc[-1])

    sma50 = float(
        close.rolling(50).mean().iloc[-1]
    )

    sma200 = float(
        close.rolling(200).mean().iloc[-1]
    )


    result = 0


    if latest > sma50:
        result += 50


    if latest > sma200:
        result += 50


    return result
