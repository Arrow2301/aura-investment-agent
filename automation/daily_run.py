from market.universe import SYMBOLS
from market.data import get_data
from intelligence.technical import technical_score
from intelligence.decision import decide

def run():
    for symbol in SYMBOLS:
        data=get_data(symbol)
        if data is not None:
            tech=technical_score(data)
            decision=decide(tech)
            print(symbol, decision)

if __name__=="__main__":
    run()
