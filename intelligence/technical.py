import pandas as pd

def score(data):
    close=data['Close']
    if isinstance(close,pd.DataFrame):
        close=close.iloc[:,0]

    if len(close)<200:
        return 0

    s=0
    if close.iloc[-1]>close.rolling(50).mean().iloc[-1]:
        s+=50
    if close.iloc[-1]>close.rolling(200).mean().iloc[-1]:
        s+=50
    return s
