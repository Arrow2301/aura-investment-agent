import yfinance as yf

def download(symbol):
    return yf.download(symbol, period="1y", progress=False)
