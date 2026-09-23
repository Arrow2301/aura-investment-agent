import os
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
            aura.get("confidence", 0)

    }


    response = (
        supabase
        .table("signals")
        .insert(data)
        .execute()
    )


    return response
