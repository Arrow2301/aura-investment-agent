"""Read-only scheduled strategy evaluation and sample-size context."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import plotly.express as px
import streamlit as st
from database.supabase_client import get_client

st.title('Strategy performance')
st.caption('Weekly held-out tests use the last 30% of historical daily bars. Fees and slippage are included; results do not predict future returns.')
try:
    records = get_client().table('strategy_backtests').select('*').order('as_of', desc=True).limit(1000).execute().data or []
except Exception as exc:
    st.error(f'Cannot load backtests: {exc}')
    st.stop()
if not records:
    st.info('Run the weekly held-out backtest workflow. Results will appear here automatically afterward.')
    st.stop()

frame = pd.DataFrame(records)
date = frame['as_of'].max()
latest = frame[frame['as_of'] == date].copy()
st.caption(f'Latest evaluation: {date} · {len(latest)} stock/strategy pairs')
for name in ('return_pct', 'benchmark_return_pct', 'win_rate_pct', 'trade_count', 'max_drawdown_pct', 'profit_factor'):
    latest[name] = pd.to_numeric(latest[name], errors='coerce')
eligible = latest[(latest['status'] == 'OK') & (latest['trade_count'] >= 5)]
one, two, three = st.columns(3)
one.metric('Eligible tests', len(eligible))
two.metric('Median tested return', f"{eligible['return_pct'].median():+.1f}%" if not eligible.empty else '—')
three.metric('Median same-stock hold', f"{eligible['benchmark_return_pct'].median():+.1f}%" if not eligible.empty else '—')
if eligible.empty:
    st.warning('No backtest has at least five closed trades. Win rates are too sparse to summarize.')
else:
    breakdown = eligible.groupby('strategy').agg(symbols=('symbol', 'nunique'),
        closed_trades=('trade_count', 'sum'), median_win_rate=('win_rate_pct', 'median'),
        median_test_return=('return_pct', 'median'), median_hold_return=('benchmark_return_pct', 'median')).reset_index()
    st.subheader('By strategy')
    st.dataframe(breakdown.round(2), use_container_width=True, hide_index=True)
    fig = px.scatter(eligible, x='benchmark_return_pct', y='return_pct', color='strategy',
                     hover_name='symbol', size='trade_count', labels={
                         'benchmark_return_pct': 'Same-stock hold %', 'return_pct': 'Strategy %'})
    fig.add_shape(type='line', x0=-100, y0=-100, x1=100, y1=100,
                  line=dict(color='gray', dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
st.subheader('All latest results')
st.dataframe(latest[['symbol','strategy','status','tested_bars','trade_count',
                     'win_rate_pct','return_pct','benchmark_return_pct','max_drawdown_pct',
                     'profit_factor','notes']].sort_values(['strategy','symbol']),
             use_container_width=True, hide_index=True)
st.caption('In-sample parameter tuning is not automated. A winning historical test does not validate an investment strategy.')
