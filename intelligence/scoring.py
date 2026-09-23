def calculate(features):
    weights = {
        "technical":0.25,
        "fundamental":0.25,
        "quality":0.20,
        "risk":0.15,
        "valuation":0.15
    }

    score=sum(features.get(k,0)*v for k,v in weights.items())

    confidence=min(0.95, max(0.50, score/100))

    if score >= 75:
        action="BUY_CANDIDATE"
    elif score >= 50:
        action="WATCH"
    else:
        action="AVOID"

    return {
        "score":round(score,2),
        "confidence":round(confidence,2),
        "action":action
    }
