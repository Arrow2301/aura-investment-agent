def score(data):
    latest=data.iloc[-1]
    result=0
    if latest["Close"] > data["Close"].rolling(50).mean().iloc[-1]:
        result += 50
    if latest["Close"] > data["Close"].rolling(200).mean().iloc[-1]:
        result += 50
    return result
