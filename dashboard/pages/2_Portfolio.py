"""Authenticated paper-trade journal. It never routes real orders."""

import pandas as pd
import streamlit as st

from database.supabase_client import get_client

st.title("💼 Paper Portfolio")
st.caption("Research journal only — no broker connection or real order execution.")

if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = get_client()
supabase = st.session_state.supabase_client
session = supabase.auth.get_session()
if not session:
    st.info("Sign in with your Supabase account. Credentials remain in this session and are never stored by AURA.")
    with st.form("paper_sign_in"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        sign_in = st.form_submit_button("Sign in")
    if sign_in:
        try:
            supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.rerun()
        except Exception:
            st.error("Sign-in failed. Check your credentials and Supabase authentication configuration.")
    st.stop()

with st.form("paper_trade"):
    symbol = st.text_input("NSE symbol", placeholder="RELIANCE.NS").strip().upper()
    side = st.selectbox("Side", ["BUY", "SELL"])
    quantity = st.number_input("Quantity", min_value=0.01, value=1.0)
    price = st.number_input("Paper execution price (₹)", min_value=0.01, value=100.0)
    notes = st.text_input("Notes")
    submitted = st.form_submit_button("Add paper trade")
if submitted:
    if not symbol or len(symbol) > 30:
        st.error("Enter a valid symbol of at most 30 characters.")
    else:
        supabase.table("paper_trades").insert({"symbol": symbol, "side": side, "quantity": quantity, "price": price, "notes": notes}).execute()
        st.success("Paper trade recorded.")

rows = supabase.table("paper_trades").select("symbol,side,quantity,price,traded_at,notes").order("traded_at", desc=True).execute().data
if not rows:
    st.info("No paper trades yet.")
else:
    trades = pd.DataFrame(rows)
    trades["signed_quantity"] = trades["quantity"] * trades["side"].map({"BUY": 1, "SELL": -1})
    positions = trades.groupby("symbol", as_index=False)["signed_quantity"].sum().rename(columns={"signed_quantity": "open_quantity"})
    st.subheader("Open quantities")
    st.dataframe(positions, use_container_width=True)
    st.subheader("Entry and exit history")
    st.dataframe(trades.drop(columns="signed_quantity"), use_container_width=True)
