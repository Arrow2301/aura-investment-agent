import yfinance as yf

def get_history(symbol):
    return yf.download(symbol, period='5y', auto_adjust=True)
