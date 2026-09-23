from data_engine.universe import SYMBOLS
from intelligence.decision_brain import calculate

for symbol in SYMBOLS:
    print(symbol, calculate(75,75,70,80,70,70))
