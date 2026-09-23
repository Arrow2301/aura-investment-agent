def calculate(technical, momentum, risk, regime, quality):
    score = (
        technical * 0.30 +
        momentum * 0.20 +
        risk * 0.15 +
        regime * 0.15 +
        quality * 0.20
    )

    if score >= 75:
        action = "BUY_CANDIDATE"
    elif score >= 50:
        action = "WATCH"
    else:
        action = "AVOID"

    return {
        "score": score,
        "action": action
    }
