from market.universe import SYMBOLS
from intelligence.engine import score,action

def run():
    for symbol in SYMBOLS:
        result=score({
            "technical":70,
            "quality":60,
            "momentum":65,
            "risk":70,
            "regime":60
        })

        print(symbol,result,action(result))

if __name__=="__main__":
    run()
