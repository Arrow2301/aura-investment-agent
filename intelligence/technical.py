import pandas as pd

def analyse(data):
    close=data["Close"]
    if isinstance(close,pd.DataFrame):
        close=close.iloc[:,0]

    if len(close)<200:
        return 0

    score=0
    if close.iloc[-1] > close.rolling(50).mean().iloc[-1]:
        score += 50
    if close.iloc[-1] > close.rolling(200).mean().iloc[-1]:
        score += 50

    return score
