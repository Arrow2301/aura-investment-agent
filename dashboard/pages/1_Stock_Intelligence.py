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
    .table("stock_analysis")
    .select("*")
    .order(
        "analysis_date",
        desc=True
    )
    .execute()
    .data
)


df = pd.DataFrame(data)


if df.empty:

    st.warning(
        "No analysis available. Run daily pipeline."
    )

    st.stop()



symbol = st.selectbox(
    "Select Stock",
    df["symbol"].unique()
)


stock = df[
    df["symbol"] == symbol
].iloc[0]



c1,c2,c3,c4 = st.columns(4)


with c1:
    st.metric(
        "AURA Score",
        stock["aura_score"]
    )

with c2:
    st.metric(
        "Action",
        stock["action"]
    )

with c3:
    st.metric(
        "Score proxy",
        f"{stock['confidence']} / 100"
    )

with c4:
    st.metric(
        "Price",
        stock["current_price"]
    )



st.divider()


st.subheader(
    "Score Breakdown"
)


scores = {

"Technical":
stock["technical_score"],

"Fundamental":
stock["fundamental_score"],

"Quality":
stock["quality_score"],

"Risk":
stock["risk_score"]

}


st.bar_chart(scores)



st.subheader(
    "Technical Signals"
)


for x in stock["technical_signals"]:

    st.success(x)



st.subheader(
    "Fundamental Signals"
)


for x in stock["fundamental_signals"]:

    st.success(x)



st.subheader(
    "AURA Investment Thesis"
)


st.info(
    stock["explanation"]
)


risk_setup = stock.get("risk_setup") or {}
if risk_setup:
    st.subheader("Observed Risk / Reward")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Entry", risk_setup.get("entry", "—"))
    r2.metric("Stop", risk_setup.get("stop", "—"))
    r3.metric("Resistance target", risk_setup.get("target", "—"))
    r4.metric("Reward / risk", risk_setup.get("reward_risk", "—"))
    if risk_setup.get("eligible"):
        st.success(risk_setup.get("reason", "Risk/reward threshold met."))
    else:
        st.warning(risk_setup.get("reason", "Setup does not meet the risk/reward threshold."))
