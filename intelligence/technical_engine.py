import pandas as pd

def analyze(df):
    close=df['Close'].squeeze()
    sma50=close.rolling(50).mean().iloc[-1]
    sma200=close.rolling(200).mean().iloc[-1]
    rsi=100-(100/(1+(close.diff().clip(lower=0).rolling(14).mean()/(-close.diff().clip(upper=0).rolling(14).mean()))))
    score=50
    signals=[]
    if close.iloc[-1]>sma200: score+=20; signals.append('Above 200 DMA')
    if close.iloc[-1]>sma50: score+=10; signals.append('Positive trend')
    if rsi.iloc[-1] < 70: score+=5
    return {'score':min(round(score),100),'signals':signals}
