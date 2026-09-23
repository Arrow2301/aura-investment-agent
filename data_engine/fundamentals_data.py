import yfinance as yf

def get_fundamentals(symbol):
    info=yf.Ticker(symbol).info
    return {
        'revenue_growth': info.get('revenueGrowth',0) or 0,
        'profit_margin': info.get('profitMargins',0) or 0,
        'roe': info.get('returnOnEquity',0) or 0,
        'debt_equity': info.get('debtToEquity',0) or 0,
        'pe': info.get('trailingPE',0) or 0,
        'pb': info.get('priceToBook',0) or 0,
    }
