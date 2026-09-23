def risk_score(drawdown):
    if drawdown > 20:
        return 20
    if drawdown > 10:
        return 50
    return 80
