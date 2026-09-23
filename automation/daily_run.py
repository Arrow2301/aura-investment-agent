import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from data_engine.universe import SYMBOLS
from data_engine.market_data import get_history
from intelligence.technical_engine import analyze
for s in SYMBOLS:
    print(s, analyze(get_history(s)))
