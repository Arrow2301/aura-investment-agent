def calculate(features):
    weights={
        "technical":0.25,
        "fundamental":0.25,
        "quality":0.20,
        "risk":0.15,
        "valuation":0.15
    }

    total=sum(features.get(k,0)*w for k,w in weights.items())

    action="AVOID"
    if total>=75:
        action="BUY_CANDIDATE"
    elif total>=50:
        action="WATCH"

    return {
        "score":round(total,2),
        "action":action
    }
