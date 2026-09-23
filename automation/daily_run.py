from data.universe import SYMBOLS
from data.market import get_market_data
from intelligence.technical import analyze as technical
from intelligence.fundamentals import analyze as fundamental
from intelligence.scoring import calculate

def run():
    for symbol in SYMBOLS:
        df=get_market_data(symbol)

        tech=technical(df)
        fund=fundamental()

        result=calculate({
            "technical":tech["score"],
            **fund,
            "risk":70
        })

        print(symbol,result)

if __name__=="__main__":
    run()
