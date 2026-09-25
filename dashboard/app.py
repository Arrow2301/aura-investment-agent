"""AURA research dashboard entry point."""
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from database.supabase_client import get_client

st.set_page_config(page_title='AURA | India equities', layout='wide')
st.title('AURA | India Investment Intelligence')
st.caption('End-of-day research and paper tracking. Prices are historical closes, not live quotes. Score proxy is not a probability.')
try:
    client = get_client()
    runs = client.table('scan_runs').select('*').order('started_at', desc=True).limit(1).execute().data or []
    rows = client.table('signals').select('*').order('analysis_date', desc=True).limit(1000).execute().data or []
except Exception as exc:
    st.error(f'Database unavailable: {exc}')
    st.stop()

if runs:
    run = runs[0]
    st.caption(f"Last scan: {run['status']} · {run['success_count']}/{run['universe_count']} symbols · started {run['started_at']}")
    if run['status'] != 'SUCCESS':
        st.warning('The latest scan was incomplete. Check the Actions run and the scan error log.')
else:
    st.warning('No scan has completed. Run the daily workflow after database setup.')

if not rows:
    st.info('No signal snapshots yet.')
    st.stop()

df = pd.DataFrame(rows)
as_of = df['analysis_date'].max()
latest = df[df['analysis_date'] == as_of].copy()
st.subheader(f'Market scan · {as_of}')
if (datetime.now().date() - pd.Timestamp(as_of).date()) > timedelta(days=4):
    st.warning('Latest stored market snapshot is more than four calendar days old.')
col1, col2, col3 = st.columns(3)
col1.metric('Symbols scanned', len(latest))
col2.metric('Buy candidates', int((latest['action'] == 'BUY_CANDIDATE').sum()))
col3.metric('Average AURA score', f"{pd.to_numeric(latest['aura_score']).mean():.1f}")
columns = ['symbol', 'market_date', 'price', 'aura_score', 'action', 'confidence',
           'technical_score', 'fundamental_score', 'quality_score', 'risk_score']
st.dataframe(latest[[c for c in columns if c in latest]].sort_values('aura_score', ascending=False),
             use_container_width=True, hide_index=True)
st.caption('A candidate is a research flag, not a trade instruction. Confirm market price and liquidity independently.')

st.subheader('Measured signal outcomes')
st.caption('Close-to-close forward returns over 5 and 20 trading sessions, where enough subsequent history exists. Includes all signal actions; no trading costs.')
for horizon in (5, 20):
    col = f'return_{horizon}d_pct'
    if col in df:
        outcome = df.dropna(subset=[col])
        if not outcome.empty:
            summary = outcome.groupby('action')[col].agg(['count', 'mean', 'median']).reset_index()
            st.write(f'{horizon} sessions')
            st.dataframe(summary, use_container_width=True, hide_index=True)
