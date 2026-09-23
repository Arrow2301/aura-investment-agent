def run(returns):
    import numpy as np
    equity=(1+returns).cumprod()
    return {'cagr':float(equity.iloc[-1]**(252/len(equity))-1),'max_drawdown':float((equity/equity.cummax()-1).min())}
