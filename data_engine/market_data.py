import pandas as pd

def get_history(symbol, period='2y'):
    import yfinance as yf
    frame = yf.download(symbol, period=period, auto_adjust=True, progress=False, threads=False)
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.loc[:, ~frame.columns.duplicated()]
    required = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if frame.empty or not required.issubset(frame.columns):
        raise ValueError(f'{symbol}: missing OHLCV history')
    frame = frame.sort_index().dropna(subset=['Open', 'High', 'Low', 'Close'])
    if len(frame) < 55:
        raise ValueError(f'{symbol}: fewer than 55 valid daily bars')
    return frame
