def get_fundamentals(symbol):
    import yfinance as yf
    info=yf.Ticker(symbol).info or {}
    return {
        'revenue_growth': info.get('revenueGrowth'),
        'profit_margin': info.get('profitMargins'),
        'roe': info.get('returnOnEquity'),
        'debt_equity': info.get('debtToEquity'),
        'pe': info.get('trailingPE'),
        'pb': info.get('priceToBook'),
    }
