import yfinance as yf

def get_history(symbol, period='2y'):
    return yf.download(symbol, period=period, auto_adjust=True, progress=False)
