"""Small, testable transformations for research snapshots."""
import pandas as pd


def latest_by_symbol(rows):
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    frame['analysis_date'] = pd.to_datetime(frame['analysis_date'], errors='coerce')
    frame = frame.dropna(subset=['analysis_date', 'symbol'])
    return frame.sort_values('analysis_date').drop_duplicates('symbol', keep='last')


def outcome_summary(rows, horizon=5):
    """Summarize completed forward outcomes without treating missing as zero."""
    field = f'return_{horizon}d_pct'
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    if field not in frame or 'action' not in frame:
        return pd.DataFrame()
    frame[field] = pd.to_numeric(frame[field], errors='coerce')
    frame = frame.dropna(subset=[field])
    if frame.empty:
        return pd.DataFrame()
    result = frame.groupby('action', as_index=False)[field].agg(['count', 'mean', 'median'])
    result.columns = ['Action', 'Observations', 'Mean %', 'Median %']
    return result.round(2)
