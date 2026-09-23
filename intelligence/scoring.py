def score(features):
    weights={
        "technical":0.30,
        "momentum":0.20,
        "fundamental":0.20,
        "risk":0.15,
        "regime":0.15
    }

    value=sum(features.get(k,0)*v for k,v in weights.items())

    action="AVOID"
    if value>=75:
        action="BUY_CANDIDATE"
    elif value>=50:
        action="WATCH"

    return {
        "score":round(value,2),
        "action":action
    }
