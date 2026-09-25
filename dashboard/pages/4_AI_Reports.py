from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import streamlit as st
from database.supabase_client import get_client

st.title('Daily research brief')
st.caption('Generated from stored scores and explanations; no language model or news claims.')
try:
    data = get_client().table('stock_analysis').select('*').order('analysis_date', desc=True).limit(1000).execute().data or []
except Exception as exc:
    st.error(str(exc))
    st.stop()
if not data:
    st.info('No analysis has been saved yet.')
else:
    frame = pd.DataFrame(data)
    as_of = frame['analysis_date'].max()
    current = frame[frame['analysis_date'] == as_of].sort_values('aura_score', ascending=False)
    st.subheader(f'As of {as_of}')
    st.write(current['action'].value_counts().to_dict())
    for _, row in current.iterrows():
        with st.expander(f"{row['symbol']} · {row['action']} · {row['aura_score']}"):
            st.write(row.get('explanation') or 'No explanation stored')
            st.write('Risk setup:', row.get('risk_setup') or {})
