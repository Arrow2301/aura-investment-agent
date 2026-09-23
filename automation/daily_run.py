from config.settings import UNIVERSE
from data.market import get_market_data
from data.fundamentals import get_fundamentals
from intelligence.technical import analyze
from intelligence.scoring import calculate

def run():
    for symbol in UNIVERSE:
        df=get_market_data(symbol)
        tech=analyze(df)
        fund=get_fundamentals(symbol)

        result=calculate({
            "technical":tech["score"],
            "fundamental":fund["quality"],
            "quality":fund["quality"],
            "risk":70,
            "valuation":fund["valuation"]
        })

        print(symbol,result)

if __name__=="__main__":
    run()
