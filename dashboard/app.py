import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from database.supabase_client import get_client


st.set_page_config(
    page_title="AURA Investment Intelligence",
    layout="wide"
)


st.title("🚀 AURA India Investment Intelligence")


supabase = get_client()


response = (
    supabase
    .table("signals")
    .select("*")
    .order(
        "created_at",
        desc=True
    )
    .execute()
)


data = response.data


if not data:

    st.warning(
        "No AURA signals available."
    )

else:

    df = pd.DataFrame(data)


    st.subheader(
        "📊 Market Scanner"
    )


    st.dataframe(
        df[
            [
                "symbol",
                "aura_score",
                "action",
                "confidence",
                "technical_score",
                "fundamental_score",
                "quality_score",
                "risk_score"
            ]
        ],
        use_container_width=True
    )


    st.subheader(
        "🏆 Top AURA Opportunities"
    )


    top = (
        df
        .sort_values(
            "aura_score",
            ascending=False
        )
        .head(5)
    )


    for _, row in top.iterrows():

        st.success(
            f"""
{row['symbol']}

AURA Score: {row['aura_score']}

Action: {row['action']}

Confidence: {row['confidence']}%
"""
        )
