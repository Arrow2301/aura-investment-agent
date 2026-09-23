import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_engine.universe import SYMBOLS
from data_engine.market_data import get_history
from data_engine.fundamentals_data import get_fundamentals

from intelligence.technical_engine import analyze as technical_analyze
from intelligence.fundamental_engine import analyze as fundamental_analyze
from intelligence.quality_engine import analyze as quality_analyze
from intelligence.risk_engine import analyze as risk_analyze
from intelligence.decision_brain import calculate_aura_score

from database.supabase_client import save_signal


for symbol in SYMBOLS:

    print(f"Processing {symbol}")

    history = get_history(symbol)

    technical = technical_analyze(history)

    fundamentals = get_fundamentals(symbol)

    fundamental_score = fundamental_analyze(fundamentals)

    quality = quality_analyze(fundamentals)

    risk = risk_analyze(history)

    aura = calculate_aura_score(
        technical,
        fundamental_score,
        quality,
        risk
    )

    print(symbol, aura)

    save_signal(
        symbol,
        aura
    )
