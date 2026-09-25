import streamlit as st

st.title("📈 Backtesting")
st.markdown("""
The Phase 1 engine is available for research runs through `backtesting.engine.run`.

It enforces:
- signals calculated on one bar and execution at the next bar's open;
- long-only BUY/EXIT semantics;
- configurable fees and slippage;
- conservative stop handling when a stop and target occur in the same bar; and
- trade count, win rate, return, profit factor, drawdown, and buy-and-hold comparison.

Interactive strategy selection and persisted research runs are deferred until the
signal history contains enough point-in-time observations for an honest comparison.
""")
