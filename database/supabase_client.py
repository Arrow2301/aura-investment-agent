import os
from datetime import date

def get_client(write=False):

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") if write else os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

    if not write and (not url or not key):
        try:
            import streamlit as st
            url = url or st.secrets.get('SUPABASE_URL')
            key = key or st.secrets.get('SUPABASE_ANON_KEY')
        except (ImportError, FileNotFoundError, KeyError):
            pass

    if not url or not key:
        raise Exception(
            "Missing SUPABASE_URL or matching Supabase key"
        )

    from supabase import create_client
    return create_client(url, key)



def save_signal(result):

    supabase = get_client(write=True)

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

        "analysis_date": result.get("analysis_date", date.today().isoformat()),
        "market_date": result.get("market_date"),
        "price": result.get("current_price"),

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

    supabase = get_client(write=True)

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

        "analysis_date": result.get("analysis_date", date.today().isoformat()),
        "market_date": result.get("market_date"),

        "risk_setup": result.get("risk", {})
    }


    return (
        supabase
        .table("stock_analysis")
        .upsert(data, on_conflict="symbol,analysis_date")
        .execute()
    )
