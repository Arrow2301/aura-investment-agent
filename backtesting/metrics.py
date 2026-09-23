def calculate_metrics(results):
    return {
        "trades":len(results),
        "max_drawdown":0,
        "win_rate":0
    }
