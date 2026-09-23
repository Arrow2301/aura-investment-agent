def score(features):
    total=0

    for value in features.values():
        total += value

    return total/len(features)

def action(score):
    if score>=75:
        return "BUY_CANDIDATE"
    elif score>=50:
        return "WATCH"
    return "AVOID"
