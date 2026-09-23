from market.universe import SYMBOLS
from market.data import fetch
from intelligence.technical import analyse as technical
from intelligence.fundamental import analyse as fundamental
from intelligence.sentiment import analyse as sentiment
from decision.engine import decide

def run():
    for symbol in SYMBOLS:
        data = fetch(symbol)

        result = decide(
            technical(data),
            fundamental(symbol),
            sentiment(symbol)
        )

        print(symbol, result)

if __name__ == "__main__":
    run()
