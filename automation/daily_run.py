import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from data_engine.universe import SYMBOLS
from data_engine.market_data import get_history
from data_engine.fundamentals_data import get_fundamentals

from intelligence.technical_engine import analyze as technical_analyze
from intelligence.fundamental_engine import analyze as fundamental_analyze
from intelligence.quality_engine import analyze as quality_analyze
from intelligence.risk_engine import analyze as risk_analyze
from intelligence.decision_brain import calculate_aura_score

from database.supabase_client import (
    save_signal,
    save_analysis
)


def run():

    results = []

    for symbol in SYMBOLS:

        try:
            print(f"\nProcessing {symbol}")

            history = get_history(symbol)

            technical = technical_analyze(history)

            fundamentals = get_fundamentals(symbol)

            fundamental = fundamental_analyze(
                fundamentals
            )

            quality = quality_analyze(
                fundamentals
            )

            risk = risk_analyze(
                history
            )

            aura = calculate_aura_score(
                technical,
                fundamental,
                quality,
                risk
            )
            result = {
            
                "symbol": symbol,
            
                "current_price":
                    float(
                        history["Close"].iloc[-1]
                    ),
            
                "technical": technical,
            
                "fundamental": fundamental,
            
                "quality": quality,
            
                "risk": risk,
            
                "aura": aura,
            
                "explanation":
                    f"{symbol} has an AURA score of {aura['aura_score']} with action {aura['action']}."
            
            }


            print(result)

            results.append(result)

            save_signal(result)
            save_analysis(result)


        except Exception as e:

            print(
                f"Error processing {symbol}: {e}"
            )


    return results


if __name__ == "__main__":
    run()
