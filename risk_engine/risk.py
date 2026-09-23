def analyze(volatility=0.02):
    return {'score':80,'position_size':round(max(1,5/volatility),2),'stop_loss_pct':8}
