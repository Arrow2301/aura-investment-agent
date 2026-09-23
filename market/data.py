import yfinance as yf

def get(symbol):
    return yf.download(symbol, period="5y", progress=False)
