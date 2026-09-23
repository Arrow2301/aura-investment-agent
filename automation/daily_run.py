from data.universe import SYMBOLS
from data.market_data import download
from intelligence.technical import analyze
from intelligence.scoring import calculate

def run():
    for symbol in SYMBOLS:
        df=download(symbol)

        if df.empty:
            continue

        tech=analyze(df)

        result=calculate({
            "technical":tech["technical"]
        })

        print(symbol,result)

if __name__=="__main__":
    run()
