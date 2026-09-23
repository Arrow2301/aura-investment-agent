import yfinance as yf

def get_market_data(symbol):
    return yf.download(symbol, period="2y", auto_adjust=True)
