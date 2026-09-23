import streamlit as st
import pandas as pd
import sys
import os


sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../.."
        )
    )
)


from database.supabase_client import get_client


st.title("🔍 Stock Intelligence")


supabase = get_client()


data = (
    supabase
    .table("signals")
    .select("*")
    .order(
        "created_at",
        desc=True
    )
    .execute()
    .data
)


df = pd.DataFrame(data)


stock = st.selectbox(
    "Select Stock",
    df["symbol"].unique()
)


row = df[
    df["symbol"] == stock
].iloc[0]


c1,c2,c3 = st.columns(3)


with c1:
    st.metric(
        "AURA Score",
        row["aura_score"]
    )

with c2:
    st.metric(
        "Action",
        row["action"]
    )

with c3:
    st.metric(
        "Confidence",
        f"{row['confidence']}%"
    )


st.subheader(
    "Component Scores"
)


scores = {

"Technical":
row["technical_score"],

"Fundamental":
row["fundamental_score"],

"Quality":
row["quality_score"],

"Risk":
row["risk_score"]

}


st.bar_chart(scores)


st.subheader(
    "AURA Analysis"
)


if row["aura_score"] >= 80:

    st.success(
        "Strong AURA signal."
    )

elif row["aura_score"] >= 65:

    st.warning(
        "Watch candidate."
    )

else:

    st.error(
        "Weak signal."
    )
