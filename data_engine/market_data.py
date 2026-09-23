import yfinance as yf

def get_history(symbol, period='5y'):
    return yf.download(symbol, period=period, auto_adjust=True, progress=False)

def get_quote(symbol):
    return yf.Ticker(symbol).info
