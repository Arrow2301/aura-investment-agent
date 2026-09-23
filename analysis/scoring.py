def calculate_score(data):
    score = 0

    latest = data.iloc[-1]

    if latest['Close'] > data['Close'].rolling(50).mean().iloc[-1]:
        score += 50

    if latest['Volume'] > data['Volume'].mean():
        score += 25

    if latest['Close'] > data['Close'].rolling(200).mean().iloc[-1]:
        score += 25

    return score
