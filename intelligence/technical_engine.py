import ta

def analyze(df):
    close=df['Close'].squeeze()
    volume=df['Volume'].squeeze()
    score=50
    reasons=[]
    sma200=close.rolling(200).mean().iloc[-1]
    sma50=close.rolling(50).mean().iloc[-1]
    rsi=ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    if close.iloc[-1]>sma200: score+=15; reasons.append('Above 200 DMA')
    if sma50>sma200: score+=10; reasons.append('Long term trend positive')
    if rsi>50: score+=8; reasons.append('Momentum positive')
    if volume.iloc[-1]>volume.rolling(20).mean().iloc[-1]: score+=5; reasons.append('Volume confirmation')
    return {'score':min(score,100),'rsi':round(float(rsi),2),'signals':reasons}
