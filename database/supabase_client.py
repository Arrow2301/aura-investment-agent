import os
from datetime import date

from supabase import create_client


def get_client():

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception(
            "Missing SUPABASE_URL or SUPABASE_KEY"
        )

    return create_client(url, key)



def save_signal(result):

    supabase = get_client()

    aura = result["aura"]

    data = {

        "symbol": result["symbol"],

        "technical_score":
            result["technical"].get("score", 0),

        "fundamental_score":
            result["fundamental"].get("score", 0),

        "quality_score":
            result["quality"].get("score", 0),

        "risk_score":
            result["risk"].get("score", 0),

        "aura_score":
            aura.get("aura_score", 0),

        "action":
            aura.get("action", "WATCH"),

        "confidence":
            aura.get("confidence", 0),

        "analysis_date": date.today().isoformat(),

        "explanation": {
            "signals": result["technical"].get("signals", []),
            "strategies": result["technical"].get("strategies", {}),
            "decision": result.get("explanation", "")
        },

        "risk_setup": result.get("risk", {})

    }


    return (
        supabase
        .table("signals")
        .upsert(data, on_conflict="symbol,analysis_date")
        .execute()
    )



def save_analysis(result):

    supabase = get_client()

    aura = result["aura"]

    data = {

        "symbol": result["symbol"],

        "current_price":
            result.get(
                "current_price",
                0
            ),

        "technical_score":
            result["technical"].get(
                "score",
                0
            ),

        "fundamental_score":
            result["fundamental"].get(
                "score",
                0
            ),

        "quality_score":
            result["quality"].get(
                "score",
                0
            ),

        "risk_score":
            result["risk"].get(
                "score",
                0
            ),

        "technical_signals":
            result["technical"].get(
                "signals",
                []
            ),

        "fundamental_signals":
            result["fundamental"].get(
                "signals",
                []
            ),

        "quality_signals":
            result["quality"].get(
                "signals",
                []
            ),

        "risk_notes":
            result["risk"].get(
                "risk",
                ""
            ),

        "aura_score":
            aura.get(
                "aura_score",
                0
            ),

        "action":
            aura.get(
                "action",
                "WATCH"
            ),

        "confidence":
            aura.get(
                "confidence",
                0
            ),

        "explanation":
            result.get(
                "explanation",
                ""
            ),

        "analysis_date": date.today().isoformat(),

        "risk_setup": result.get("risk", {})
    }


    return (
        supabase
        .table("stock_analysis")
        .upsert(data, on_conflict="symbol,analysis_date")
        .execute()
    )
