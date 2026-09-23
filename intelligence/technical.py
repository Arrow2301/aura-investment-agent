import ta

def analyze(df):
    close=df["Close"].squeeze()
    last=float(close.iloc[-1])
    ma=float(close.rolling(200).mean().iloc[-1])

    score=50
    reasons=[]

    if last > ma:
        score+=25
        reasons.append("above_200dma")

    rsi=float(ta.momentum.RSIIndicator(close).rsi().iloc[-1])

    if rsi>50:
        score+=25
        reasons.append("positive_momentum")

    return {"score":min(score,100),"reasons":reasons}
