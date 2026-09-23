import yfinance as yf

def fetch(symbol):
    return yf.download(symbol, period="2y", progress=False)
