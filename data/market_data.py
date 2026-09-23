import yfinance as yf

def get_prices(symbol, period="1y"):
    data = yf.download(symbol, period=period, progress=False)
    if data.empty:
        return None
    return data.reset_index()
