"""Forward closed-bar returns of stored daily signals, for evaluation only."""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from data_engine.market_data import get_history
from database.supabase_client import get_client

LOG = logging.getLogger(__name__)


def realized_returns(history, market_date, horizons=(5, 20)):
    close = history['Close'].copy()
    close.index = pd.to_datetime(close.index).normalize()
    anchor = pd.Timestamp(market_date)
    if anchor not in close.index:
        return {}
    i = close.index.get_loc(anchor)
    if not isinstance(i, int):
        return {}
    return {f'return_{days}d_pct': round((float(close.iloc[i + days]) / float(close.iloc[i]) - 1) * 100, 4)
            for days in horizons if i + days < len(close) and float(close.iloc[i]) > 0}


def run():
    client = get_client(write=True)
    rows = []
    # Explicit pagination: Supabase defaults to a 1,000-row cap.
    offset = 0
    while True:
        batch = client.table('signals').select('symbol,analysis_date,market_date,return_5d_pct,return_20d_pct').is_('return_20d_pct', 'null').order('analysis_date').range(offset, offset + 499).execute().data or []
        rows.extend(batch)
        if len(batch) < 500:
            break
        offset += 500
    for symbol in sorted({row['symbol'] for row in rows}):
        try:
            history = get_history(symbol, period='5y')
            for row in (r for r in rows if r['symbol'] == symbol):
                values = realized_returns(history, row.get('market_date') or row['analysis_date'])
                values = {k: v for k, v in values.items() if row.get(k) is None}
                if values:
                    for table in ('signals', 'stock_analysis'):
                        client.table(table).update(values).eq('symbol', symbol).eq('analysis_date', row['analysis_date']).execute()
        except Exception:
            LOG.exception('Outcome update failed for %s', symbol)
            raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
