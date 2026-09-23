from core.config import UNIVERSE
from data.market_data import get_data
from intelligence.scoring import score

def run():
    for symbol in UNIVERSE:
        data=get_data(symbol)

        features={
            "technical":60,
            "momentum":60,
            "fundamental":60,
            "risk":70,
            "regime":60
        }

        print(symbol, score(features))

if __name__=="__main__":
    run()
