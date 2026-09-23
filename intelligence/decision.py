def decide(technical, fundamental=50, sentiment=50):
    score = (technical + fundamental + sentiment)/3

    if score >= 75:
        action="BUY_CANDIDATE"
    elif score >= 50:
        action="WATCH"
    else:
        action="AVOID"

    return {
        "score": score,
        "action": action
    }
