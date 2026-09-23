import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import streamlit as st
from data_engine.universe import SYMBOLS

st.title('AURA India Investment Intelligence')
st.subheader('NSE Market Scanner')
for s in SYMBOLS:
    st.write(s)
