import pandas as pd
import ta

def analyse(data):

    close=data["Close"]

    if isinstance(close,pd.DataFrame):
        close=close.iloc[:,0]

    close=close.dropna()

    if len(close)<200:
        return {"score":0,"reason":"Insufficient data"}

    rsi=ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    macd=ta.trend.MACD(close).macd_diff().iloc[-1]

    score=0
    reasons=[]

    if rsi>50:
        score+=25
        reasons.append("RSI positive")

    if macd>0:
        score+=25
        reasons.append("MACD positive")

    if close.iloc[-1]>close.rolling(50).mean().iloc[-1]:
        score+=25
        reasons.append("Above 50 DMA")

    if close.iloc[-1]>close.rolling(200).mean().iloc[-1]:
        score+=25
        reasons.append("Above 200 DMA")

    return {
        "score":score,
        "reason":", ".join(reasons)
    }
