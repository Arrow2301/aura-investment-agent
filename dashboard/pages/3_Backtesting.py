"""Interactive historical technical-only research simulation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import streamlit as st
from backtesting.engine import run
from data_engine.market_data import get_history
from data_engine.universe import SYMBOLS
from intelligence.technical_engine import analyze

st.title('Historical technical backtest')
st.caption('Technical EMA trend only. Fundamentals are excluded because their historical publication timestamps are unavailable. Next-session fills include fees and slippage.')
symbol = st.selectbox('NSE ticker', SYMBOLS)
period = st.selectbox('History', ['2y', '5y'], index=0)
fee = st.number_input('Fee per fill (basis points)', 0.0, 100.0, 10.0)
slippage = st.number_input('Slippage per fill (basis points)', 0.0, 100.0, 5.0)
stop = st.slider('Stop (%)', 1, 25, 5) / 100
target = st.slider('Target (%)', 1, 50, 10) / 100

@st.cache_data(ttl=3600)
def history(ticker, lookback):
    return get_history(ticker, period=lookback)

if st.button('Run backtest', type='primary'):
    try:
        df = history(symbol, period)
        # Reuse the production technical evaluation on each historical prefix.
        # Only the EMA trend is selected, with a state transition to avoid daily re-entry.
        active = pd.Series([False] * len(df), index=df.index)
        for i in range(55, len(df)):
            active.iloc[i] = analyze(df.iloc[:i + 1])['strategies']['ema_trend']
        signals = pd.Series('HOLD', index=df.index)
        signals.loc[active & ~active.shift(1, fill_value=False)] = 'BUY'
        signals.loc[~active & active.shift(1, fill_value=False)] = 'EXIT'
        result = run(df, signals, stop_pct=stop, target_pct=target, fee_bps=fee, slippage_bps=slippage)
        st.write('Results', result['metrics'])
        st.metric('Same-stock buy and hold (%)', result.get('benchmark_return_pct', '—'))
        st.dataframe(pd.DataFrame(result['trades']), use_container_width=True, hide_index=True)
        st.caption('Single-stock, in-sample simulation. Stops are checked with daily bars; intraday order is unknown. Remaining positions are valued at the last close.')
    except Exception as exc:
        st.error(f'Backtest failed: {exc}')
