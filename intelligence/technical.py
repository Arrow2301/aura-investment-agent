import ta

def analyze(df):
    close=df["Close"].squeeze()

    rsi=ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    ma=close.rolling(50).mean().iloc[-1]
    last=close.iloc[-1]

    score=50
    reasons=[]

    if last > ma:
        score += 25
        reasons.append("above moving average")

    if rsi > 50:
        score += 25
        reasons.append("positive momentum")

    return {
        "technical": min(score,100),
        "reasons": reasons
    }
