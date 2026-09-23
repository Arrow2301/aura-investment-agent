import streamlit as st
from data_engine.universe import SYMBOLS
st.title('AURA Investment Intelligence')
st.write('Live market scanner')
for s in SYMBOLS: st.write(s)
