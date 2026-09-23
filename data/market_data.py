import yfinance as yf

def download(symbol, period="1y"):
    return yf.download(symbol, period=period, auto_adjust=True)
