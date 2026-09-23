from data_engine.universe import SYMBOLS
from data_engine.market_data import get_history,get_quote
from intelligence.technical_engine import analyze as tech
from intelligence.fundamental_engine import analyze as fund
from intelligence.decision_brain import calculate
for s in SYMBOLS:
    try:
        t=tech(get_history(s)); f=fund(get_quote(s))
        print(s, calculate(t['score'],f['score'],70,80,70,70))
    except Exception as e:
        print(s,e)
