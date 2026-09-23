def calculate(features):
    weights = {
        "technical":0.30,
        "momentum":0.20,
        "quality":0.20,
        "risk":0.15,
        "regime":0.15
    }

    score = sum(features.get(k,0)*v for k,v in weights.items())

    if score >= 75:
        action="BUY_CANDIDATE"
    elif score >= 50:
        action="WATCH"
    else:
        action="AVOID"

    return {
        "score":round(score,2),
        "action":action
    }
