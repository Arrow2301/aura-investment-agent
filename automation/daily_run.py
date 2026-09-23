from config.universe import NIFTY_SYMBOLS
from data.market_data import get_prices
from analysis.scoring import calculate_score

def run():
    results=[]

    for symbol in NIFTY_SYMBOLS:
        data=get_prices(symbol)
        if data is not None:
            results.append({
                "symbol":symbol,
                "score":calculate_score(data)
            })

    results.sort(key=lambda x:x["score"], reverse=True)

    print(results)

if __name__=="__main__":
    run()
