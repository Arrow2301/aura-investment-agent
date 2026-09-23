from market.universe import SYMBOLS
from market.data import get
from intelligence.technical import score as technical
from intelligence.fundamental import score as fundamental
from intelligence.sentiment import score as sentiment
from decision.engine import decide

def run():
    for s in SYMBOLS:
        data=get(s)
        result=decide(
            technical(data),
            fundamental(s),
            sentiment(s)
        )
        print(s,result)

if __name__=='__main__':
    run()
