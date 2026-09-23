import streamlit as st

st.title("AURA V6.1 Command Center")

sections=[
"Market Scanner",
"Signals",
"Portfolio",
"Risk",
"Backtesting",
"Learning"
]

for s in sections:
    st.write(s)
