from universe.nse import SYMBOLS
from data.market import fetch
from intelligence.technical import analyse
from intelligence.fundamental import analyse as fundamental
from intelligence.sentiment import analyse as sentiment
from decision.engine import decide

def run():
    for symbol in SYMBOLS:
        data=fetch(symbol)
        t=analyse(data)
        f=fundamental(symbol)
        s=sentiment(symbol)
        print(symbol, decide(t,f,s))

if __name__=="__main__":
    run()
