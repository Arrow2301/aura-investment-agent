import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from data_engine.universe import SYMBOLS
st.title('AURA Investment Intelligence')
st.write('Live market scanner')
for s in SYMBOLS: st.write(s)
