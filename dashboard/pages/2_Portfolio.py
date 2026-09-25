"""Authenticated paper journal, with historical snapshot marks."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import streamlit as st
from database.supabase_client import get_client
from portfolio.ledger import summarize

st.title('Paper portfolio')
st.caption('Paper entries are manual; marks use stored end-of-day closes. No broker connection.')
if 'supabase_client' not in st.session_state:
    st.session_state.supabase_client = get_client()
client = st.session_state.supabase_client
try:
    session = client.auth.get_session()
except Exception:
    session = None
if not session:
    with st.form('sign_in'):
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        submitted = st.form_submit_button('Sign in')
    if submitted:
        try:
            client.auth.sign_in_with_password({'email': email, 'password': password})
            st.rerun()
        except Exception:
            st.error('Sign-in failed. Check credentials and Supabase authentication settings.')
    st.stop()
if st.button('Sign out'):
    client.auth.sign_out()
    st.rerun()
try:
    rows = client.table('paper_trades').select('id,symbol,side,quantity,price,traded_at,notes').order('traded_at').limit(1000).execute().data or []
    positions = summarize(rows)
except Exception as exc:
    st.error(f'Cannot read the journal: {exc}')
    st.stop()
if len(rows) == 1000:
    st.warning('Showing only the first 1,000 trades; export/archive before adding more.')
with st.form('trade'):
    symbol = st.text_input('NSE symbol', placeholder='RELIANCE.NS').strip().upper()
    side = st.selectbox('Side', ['BUY', 'SELL'])
    quantity = st.number_input('Shares', min_value=0.01, value=1.0)
    price = st.number_input('Execution price (₹)', min_value=0.01, value=100.0)
    notes = st.text_input('Notes')
    submitted = st.form_submit_button('Add paper trade')
if submitted:
    available = positions.get(symbol, {}).get('quantity', 0)
    if not symbol.endswith('.NS') or len(symbol) > 30:
        st.error('Use an NSE ticker such as RELIANCE.NS.')
    elif side == 'SELL' and quantity > available + 1e-9:
        st.error(f'Open quantity is {available:.2f}; this sale would exceed it.')
    else:
        try:
            client.table('paper_trades').insert({'symbol': symbol, 'side': side, 'quantity': quantity,
                                                  'price': price, 'notes': notes}).execute()
            st.rerun()
        except Exception as exc:
            st.error(f'Could not save trade: {exc}')

if rows:
    symbols = list(positions)
    marks = {}
    try:
        snapshots = client.table('stock_analysis').select('symbol,current_price,market_date').in_('symbol', symbols).order('analysis_date', desc=True).limit(1000).execute().data or []
        marks = {r['symbol']: r for r in reversed(snapshots)}
    except Exception as exc:
        st.warning(f'Historical marks unavailable: {exc}')
    display = []
    for ticker, item in positions.items():
        mark = marks.get(ticker)
        close = float(mark['current_price']) if mark and mark.get('current_price') is not None else None
        display.append({'symbol': ticker, 'open_shares': item['quantity'],
                        'average_cost': item['cost'] / item['quantity'] if item['quantity'] else None,
                        'last_close': close, 'close_date': mark.get('market_date') if mark else None,
                        'unrealized_pnl': item['quantity'] * close - item['cost'] if close is not None else None,
                        'realized_pnl': item['realized_pnl']})
    st.subheader('Positions and P&L (₹)')
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
    st.subheader('Journal')
    st.dataframe(pd.DataFrame(rows).sort_values('traded_at', ascending=False), use_container_width=True, hide_index=True)
