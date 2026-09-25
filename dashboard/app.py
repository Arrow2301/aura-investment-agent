"""AURA's end-of-day research workspace."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.view_models import outcome_summary
from database.supabase_client import get_client

IST = timezone(timedelta(hours=5, minutes=30))
st.set_page_config(page_title='AURA | Research desk', page_icon='📈', layout='wide')
st.markdown('''<style>
.block-container {padding-top: 2rem; max-width: 1450px;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.18); border-radius: 12px; padding: 16px;}
</style>''', unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner=False)
def load_snapshots():
    client = get_client()
    runs = client.table('scan_runs').select('*').order('started_at', desc=True).limit(1).execute().data or []
    rows = client.table('signals').select('*').order('analysis_date', desc=True).limit(1000).execute().data or []
    return runs, rows


st.title('AURA · Research desk')
st.caption('Indian equities · completed daily market bars · paper research only')
try:
    runs, rows = load_snapshots()
except Exception as exc:
    st.error(f'Database unavailable: {exc}')
    st.stop()

latest_run = runs[0] if runs else None
with st.sidebar:
    st.header('AURA')
    if latest_run:
        status = latest_run['status']
        message = f"Scan {status} · {latest_run['success_count']}/{latest_run['universe_count']}"
        (st.success if status == 'SUCCESS' else st.error)(message)
        st.caption(f"Started: {latest_run['started_at']}")
        if latest_run.get('errors'):
            with st.expander('Scan errors'):
                st.json(latest_run['errors'])
    else:
        st.warning('No scan runs yet')
    if st.button('↻ Refresh data', use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.page_link('pages/1_Stock_Intelligence.py', label='Stock intelligence', icon='🔎')
    st.page_link('pages/2_Portfolio.py', label='Paper portfolio', icon='💼')
    st.page_link('pages/3_Backtesting.py', label='Historical backtest', icon='📈')
    st.page_link('pages/4_AI_Reports.py', label='Research brief', icon='📝')
    st.page_link('pages/5_Strategy_Performance.py', label='Strategy performance', icon='📊')
    st.caption('Closing prices are not live quotes. Scores are not probabilities.')

if not rows:
    st.info('No signals saved. Run the end-of-day scan in GitHub Actions.')
    st.stop()

frame = pd.DataFrame(rows)
frame['analysis_date'] = pd.to_datetime(frame['analysis_date'], errors='coerce')
frame = frame.dropna(subset=['analysis_date'])
frame['aura_score'] = pd.to_numeric(frame['aura_score'], errors='coerce')
dates = sorted(frame['analysis_date'].dt.date.unique(), reverse=True)
if not dates:
    st.info('No dated signals saved.')
    st.stop()
if len(rows) == 1000:
    st.info('History shows the most recent 1,000 rows. Older records are outside this view.')

date_choice = st.selectbox('Market snapshot', dates, format_func=lambda d: d.strftime('%a, %d %b %Y'))
if (datetime.now(IST).date() - dates[0]).days > 4:
    st.warning(f'Latest stored snapshot is {dates[0]}; check that the scheduled scan is running.')
if latest_run and latest_run['status'] != 'SUCCESS':
    st.warning('The most recent scan was incomplete. This date may contain only some symbols.')
selected = frame[frame['analysis_date'].dt.date == date_choice].copy()
tab_scan, tab_stock, tab_history = st.tabs(['📊 Market scan', '🔎 Stock detail', '📅 Track record'])

with tab_scan:
    counts = selected['action'].value_counts()
    a, b, c, d, e = st.columns(5)
    a.metric('Stocks scanned', len(selected))
    b.metric('Buy candidates', int(counts.get('BUY_CANDIDATE', 0)))
    c.metric('Watch', int(counts.get('WATCH', 0)))
    d.metric('Exit candidates', int(counts.get('EXIT_CANDIDATE', 0)))
    e.metric('Avoid', int(counts.get('AVOID', 0)))
    st.caption('A buy candidate is a research flag subject to its displayed risk setup.')
    left, right, search_col = st.columns([1, 1, 1.5])
    action = left.selectbox('Action', ['All', 'BUY_CANDIDATE', 'WATCH', 'EXIT_CANDIDATE', 'AVOID'])
    minimum = right.slider('Minimum AURA score', 0, 100, 0)
    query = search_col.text_input('Find ticker', placeholder='e.g. TCS')
    filtered = selected[selected['aura_score'].fillna(0) >= minimum]
    if action != 'All':
        filtered = filtered[filtered['action'] == action]
    if query:
        filtered = filtered[filtered['symbol'].str.contains(query.strip(), case=False, regex=False, na=False)]
    filtered = filtered.sort_values('aura_score', ascending=False)
    if filtered.empty:
        st.info('No stocks match these filters.')
    else:
        board = filtered.copy()
        for col in ('price', 'aura_score', 'technical_score', 'fundamental_score', 'quality_score', 'risk_score'):
            board[col] = pd.to_numeric(board.get(col), errors='coerce').round(2)
        board = board.rename(columns={'symbol': 'Stock', 'action': 'Action', 'price': 'Last close ₹',
                                      'aura_score': 'AURA / 100', 'technical_score': 'Technical',
                                      'fundamental_score': 'Fundamental', 'quality_score': 'Quality',
                                      'risk_score': 'Risk'})
        cols = ['Stock', 'Action', 'AURA / 100', 'Last close ₹', 'Technical', 'Fundamental', 'Quality', 'Risk']
        st.dataframe(board[cols], use_container_width=True, hide_index=True)
        st.caption('Open Stock detail to inspect the evidence and observed risk levels.')

with tab_stock:
    stocks = selected.sort_values('aura_score', ascending=False)['symbol'].dropna().tolist()
    if not stocks:
        st.info('No stock detail on this date.')
    else:
        symbol = st.selectbox('Stock', stocks, key='detail_symbol')
        row = selected[selected['symbol'] == symbol].iloc[0]
        st.subheader(f"{symbol} · {row['action']}")
        c1, c2, c3 = st.columns(3)
        c1.metric('AURA score', f"{row['aura_score']:.1f} / 100")
        c2.metric('Closing price', f"₹{float(row['price']):,.2f}" if pd.notna(row.get('price')) else '—')
        c3.metric('Market date', str(row.get('market_date') or date_choice))
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown('#### Why this classification')
            explanation = row.get('explanation') or {}
            if isinstance(explanation, dict):
                st.write(explanation.get('decision') or 'No explanation saved.')
                strategies = explanation.get('strategies') or {}
                if strategies:
                    st.write('Technical checks')
                    for name, passed in strategies.items():
                        st.write(('✓' if passed else '○') + ' ' + name.replace('_', ' ').title())
            else:
                st.write(explanation)
            components = {label: pd.to_numeric(row.get(field), errors='coerce')
                          for label, field in [('Technical', 'technical_score'), ('Fundamental', 'fundamental_score'),
                                               ('Quality', 'quality_score'), ('Risk', 'risk_score')]}
            chart = pd.DataFrame({'Component': list(components), 'Score': list(components.values())}).dropna()
            if not chart.empty:
                fig = px.bar(chart, x='Score', y='Component', orientation='h', range_x=[0, 100],
                             color='Score', color_continuous_scale='Blues', height=270)
                fig.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(l=0, r=0, t=8, b=0))
                st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown('#### Observed risk setup')
            risk = row.get('risk_setup') or {}
            if isinstance(risk, dict) and risk:
                r1, r2 = st.columns(2)
                r1.metric('Entry reference', f"₹{risk['entry']:,.2f}" if risk.get('entry') is not None else '—')
                r2.metric('Stop', f"₹{risk['stop']:,.2f}" if risk.get('stop') is not None else '—')
                r3, r4 = st.columns(2)
                r3.metric('Resistance target', f"₹{risk['target']:,.2f}" if risk.get('target') is not None else '—')
                r4.metric('Reward / risk', risk.get('reward_risk', '—'))
                st.info(risk.get('reason') or 'No risk commentary saved.')
            else:
                st.info('Risk setup unavailable for this snapshot.')
            st.caption('These are historical observations, not live orders or guaranteed exit prices.')

with tab_history:
    st.markdown('#### Signal history')
    count_by_date = frame.groupby([frame['analysis_date'].dt.date, 'action']).size().unstack(fill_value=0)
    if not count_by_date.empty:
        history = count_by_date.tail(40).rename_axis('Market date').reset_index().melt(
            id_vars='Market date', var_name='Action', value_name='Stocks')
        fig = px.bar(history, x='Market date', y='Stocks', color='Action', barmode='stack',
                     color_discrete_map={'BUY_CANDIDATE': '#35aa8d', 'WATCH': '#dda54a',
                                         'EXIT_CANDIDATE': '#d97878', 'AVOID': '#a0a6b1'})
        fig.update_layout(legend_title_text='Action', margin=dict(l=0, r=0, t=12, b=0))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('#### Measured outcomes')
    st.caption('Forward close-to-close returns after 5 or 20 completed trading sessions. Descriptive signal tracking; no fees, position sizing, or benchmark adjustment.')
    horizon = st.radio('Horizon', [5, 20], horizontal=True, format_func=lambda x: f'{x} sessions')
    summary = outcome_summary(rows, horizon)
    if summary.empty:
        st.info(f'No completed {horizon}-session outcomes yet. The outcome workflow will fill these as trading sessions pass.')
    else:
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.caption('Small samples can be misleading; compare observations and dates before drawing conclusions.')
