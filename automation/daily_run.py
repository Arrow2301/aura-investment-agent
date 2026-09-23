from market.universe import SYMBOLS
from market.data import fetch
from intelligence.engine import score
def run():
    for s in SYMBOLS:
        print(s,score({'trend':60,'momentum':70,'quality':65}))
if __name__=='__main__': run()
