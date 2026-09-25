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
st.caption(f"Account ID for one-time alert setup: `{session.user.id}`")
if st.button('Sign out'):
    client.auth.sign_out()
    st.rerun()
try:
    try:
        rows = client.table('paper_trades').select('id,symbol,side,quantity,price,traded_at,notes,stop_price,target_price').order('traded_at').limit(1000).execute().data or []
        phase3_ready = True
    except Exception:
        rows = client.table('paper_trades').select('id,symbol,side,quantity,price,traded_at,notes').order('traded_at').limit(1000).execute().data or []
        phase3_ready = False
    positions = summarize(rows)
except Exception as exc:
    st.error(f'Cannot read the journal: {exc}')
    st.stop()
if len(rows) == 1000:
    st.warning('Showing only the first 1,000 trades; export/archive before adding more.')
if not phase3_ready:
    st.warning('Apply database/phase3_automation.sql to enable stop/target alerts and daily P&L history.')
with st.form('trade'):
    symbol = st.text_input('NSE symbol', placeholder='RELIANCE.NS').strip().upper()
    side = st.selectbox('Side', ['BUY', 'SELL'])
    quantity = st.number_input('Shares', min_value=0.01, value=1.0)
    price = st.number_input('Execution price (₹)', min_value=0.01, value=100.0)
    stop_price = st.number_input('Stop price ₹ (optional)', min_value=0.0, value=0.0)
    target_price = st.number_input('Target price ₹ (optional)', min_value=0.0, value=0.0)
    notes = st.text_input('Notes')
    submitted = st.form_submit_button('Add paper trade')
if submitted:
    available = positions.get(symbol, {}).get('quantity', 0)
    if not symbol.endswith('.NS') or len(symbol) > 30:
        st.error('Use an NSE ticker such as RELIANCE.NS.')
    elif side == 'SELL' and quantity > available + 1e-9:
        st.error(f'Open quantity is {available:.2f}; this sale would exceed it.')
    elif side == 'BUY' and ((stop_price and stop_price >= price) or (target_price and target_price <= price)):
        st.error('For a buy, set the optional stop below entry and target above entry.')
    else:
        try:
            payload = {'symbol': symbol, 'side': side, 'quantity': quantity,
                       'price': price, 'notes': notes}
            if phase3_ready:
                payload.update({'stop_price': (stop_price or None) if side == 'BUY' else None,
                                'target_price': (target_price or None) if side == 'BUY' else None})
            client.table('paper_trades').insert(payload).execute()
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
                        'realized_pnl': item['realized_pnl'], 'stop': item['stop'], 'target': item['target'],
                        'closed_exits': item['closed_exits'], 'winning_exits': item['winning_exits']})
    positions_frame = pd.DataFrame(display)
    open_positions = positions_frame[positions_frame['open_shares'] > 1e-9]
    a, b, c, d = st.columns(4)
    a.metric('Open positions', len(open_positions))
    b.metric('Unrealized P&L at saved closes', f"₹{open_positions['unrealized_pnl'].sum():+,.2f}")
    c.metric('Realized P&L', f"₹{positions_frame['realized_pnl'].sum():+,.2f}")
    closed = int(positions_frame['closed_exits'].sum())
    d.metric('Closed-exit win rate', f"{100 * positions_frame['winning_exits'].sum() / closed:.1f}%" if closed else '—')
    st.caption('Unrealized P&L omits positions with no saved close; these are not live prices. Fees and taxes are excluded.')
    st.subheader('Open positions')
    if open_positions.empty:
        st.info('No open paper positions.')
    else:
        st.dataframe(open_positions, use_container_width=True, hide_index=True)
    st.subheader('Journal')
    st.dataframe(pd.DataFrame(rows).sort_values('traded_at', ascending=False), use_container_width=True, hide_index=True)
    try:
        snapshots = client.table('portfolio_daily').select('*').order('market_date').limit(500).execute().data or []
        if snapshots:
            st.subheader('Portfolio P&L history')
            daily = pd.DataFrame(snapshots).set_index('market_date')
            st.line_chart(daily[['unrealized_pnl', 'realized_pnl']].astype(float))
        alerts = client.table('alert_events').select('event_type,symbol,market_date,message,sent_at').order('sent_at', desc=True).limit(50).execute().data or []
        if alerts:
            with st.expander('Recent Telegram alerts'):
                st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)
    except Exception:
        st.caption('Automated tracking appears after the Phase 3 migration and the alert workflows run.')
