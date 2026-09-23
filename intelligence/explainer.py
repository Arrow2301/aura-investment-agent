def explain(features):
    reasons=[]

    for key,value in features.items():
        if value >= 70:
            reasons.append(f"{key} positive")
        elif value < 40:
            reasons.append(f"{key} weak")

    return reasons
