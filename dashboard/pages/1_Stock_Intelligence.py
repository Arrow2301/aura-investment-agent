"""Ticker research detail and historical snapshot trend."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_engine.market_data import get_history
from database.supabase_client import get_client

st.title('Stock intelligence')
st.caption('Saved daily research. Select a ticker to see the newest snapshot and its history.')
try:
    client = get_client()
    rows = client.table('stock_analysis').select('*').order('analysis_date', desc=True).limit(1000).execute().data or []
except Exception as exc:
    st.error(f'Cannot load stock research: {exc}')
    st.stop()
if not rows:
    st.info('Run the end-of-day scan to populate this page.')
    st.stop()

frame = pd.DataFrame(rows)
symbol = st.selectbox('Select NSE ticker', sorted(frame['symbol'].dropna().unique()))
history = frame[frame['symbol'] == symbol].sort_values('analysis_date')
stock = history.iloc[-1]
st.caption(f"Latest stored market bar: {stock.get('market_date') or stock['analysis_date']}")

c1, c2, c3, c4 = st.columns(4)
c1.metric('AURA score', f"{float(stock['aura_score']):.1f} / 100")
c2.metric('Classification', stock['action'])
c3.metric('Last close', f"₹{float(stock['current_price']):,.2f}")
c4.metric('Observed reward / risk', (stock.get('risk_setup') or {}).get('reward_risk', '—'))

left, right = st.columns([1.1, 1])
with left:
    st.markdown('#### Investment thesis')
    st.info(stock.get('explanation') or 'No explanation saved.')
    with st.expander('Confirmed factors', expanded=True):
        for title, field in [('Technical', 'technical_signals'), ('Fundamental', 'fundamental_signals'),
                             ('Quality', 'quality_signals')]:
            st.markdown(f'**{title}**')
            for item in (stock.get(field) or []):
                st.write('• ' + str(item))
    scores = pd.DataFrame({'Component': ['Technical', 'Fundamental', 'Quality', 'Risk'],
                           'Score': [stock.get(k) for k in ('technical_score', 'fundamental_score', 'quality_score', 'risk_score')]})
    scores['Score'] = pd.to_numeric(scores['Score'], errors='coerce')
    fig = px.bar(scores.dropna(), x='Score', y='Component', orientation='h', range_x=[0, 100],
                 color='Score', color_continuous_scale='Blues', height=270)
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown('#### Observed risk setup')
    risk = stock.get('risk_setup') or {}
    if risk:
        a, b = st.columns(2)
        a.metric('Entry reference', f"₹{risk['entry']:,.2f}" if risk.get('entry') is not None else '—')
        b.metric('Stop', f"₹{risk['stop']:,.2f}" if risk.get('stop') is not None else '—')
        c, d = st.columns(2)
        c.metric('Resistance target', f"₹{risk['target']:,.2f}" if risk.get('target') is not None else '—')
        d.metric('Reward / risk', risk.get('reward_risk', '—'))
        st.caption(risk.get('reason') or '')
    else:
        st.info('Risk levels unavailable for this date.')
    st.caption('Levels are derived from old daily bars; check current prices independently.')

st.divider()
a, b = st.columns(2)
with a:
    st.markdown('#### AURA score history')
    if len(history) > 1:
        timeline = history[['analysis_date', 'aura_score']].copy()
        timeline['aura_score'] = pd.to_numeric(timeline['aura_score'], errors='coerce')
        st.line_chart(timeline.set_index('analysis_date')['aura_score'])
    else:
        st.info('The trend appears after multiple daily scans.')
with b:
    st.markdown('#### Price history')
    if st.button('Load daily candles', key='candles'):
        try:
            prices = get_history(symbol, period='6mo')
            fig = go.Figure(data=[go.Candlestick(x=prices.index, open=prices['Open'],
                                                  high=prices['High'], low=prices['Low'],
                                                  close=prices['Close'])])
            fig.update_layout(xaxis_rangeslider_visible=False, height=360,
                              margin=dict(l=0, r=0, t=12, b=0))
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Yahoo Finance daily candles can be delayed or adjusted. This chart is not a live price feed.')
        except Exception as exc:
            st.warning(f'Price chart unavailable: {exc}')
