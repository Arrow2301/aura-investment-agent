def calculate(features):
    score=sum(features.values())/len(features)

    action="AVOID"
    if score >= 75:
        action="BUY_CANDIDATE"
    elif score >= 50:
        action="WATCH"

    return {
        "score":round(score,2),
        "action":action
    }
