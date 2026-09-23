def calculate_risk(drawdown):
    if drawdown>20:
        return "HIGH"
    if drawdown>10:
        return "MEDIUM"
    return "LOW"
