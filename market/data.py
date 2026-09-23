import yfinance as yf

def get_data(symbol):
    return yf.download(symbol, period="2y", progress=False)
