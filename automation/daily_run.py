"""Scheduled end-of-day research scan; fails visibly on missing persistence."""
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data_engine.universe import SYMBOLS
from data_engine.market_data import get_history
from data_engine.fundamentals_data import get_fundamentals
from intelligence.technical_engine import analyze as technical_analyze
from intelligence.fundamental_engine import analyze as fundamental_analyze
from intelligence.quality_engine import analyze as quality_analyze
from intelligence.risk_engine import analyze as risk_analyze
from intelligence.decision_brain import calculate_aura_score
from database.supabase_client import get_client, save_signal, save_analysis

LOG = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))


def analyze_symbol(symbol, now=None):
    now = now or datetime.now(IST)
    history = get_history(symbol)
    # A manual intraday run must never interpret a partial daily candle as final.
    last_day = history.index[-1].date()
    if last_day == now.date() and now.hour < 16:
        history = history.iloc[:-1]
    if len(history) < 55:
        raise ValueError('Not enough completed price bars')
    market_date = history.index[-1].date()
    if (now.date() - market_date).days > 5:
        raise ValueError(f'Stale market bar: {market_date}')
    technical = technical_analyze(history)
    fundamentals = get_fundamentals(symbol)
    fundamental = fundamental_analyze(fundamentals)
    quality = quality_analyze(fundamentals)
    risk = risk_analyze(history)
    aura = calculate_aura_score(technical, fundamental, quality, risk)
    return {
        'symbol': symbol, 'analysis_date': market_date.isoformat(),
        'market_date': market_date.isoformat(),
        'current_price': float(history['Close'].iloc[-1]),
        'technical': technical, 'fundamental': fundamental,
        'quality': quality, 'risk': risk, 'aura': aura,
        'explanation': (
            f"AURA {aura['aura_score']}: {aura['action']}. "
            f"{risk.get('reason', 'Risk/reward unavailable')}. "
            f"Technical: {', '.join(technical.get('signals', []))}. "
            f"Fundamental coverage: {fundamental['coverage']}/4; "
            f"quality coverage: {quality['coverage']}/3."
        ),
    }


def run(symbols=None):
    symbols = list(SYMBOLS if symbols is None else symbols)
    client = get_client(write=True)  # Preflight before accepting a successful run.
    run_id = str(uuid4())
    client.table('scan_runs').insert({'id': run_id, 'status': 'RUNNING',
                                      'universe_count': len(symbols)}).execute()
    successes, errors = 0, []
    for symbol in symbols:
        try:
            result = analyze_symbol(symbol)
            save_signal(result)
            save_analysis(result)
            successes += 1
            LOG.info('%s %s %s', symbol, result['market_date'], result['aura']['action'])
        except Exception as exc:
            LOG.exception('Failed to process %s', symbol)
            errors.append({'symbol': symbol, 'error': str(exc)[:300]})
    status = 'SUCCESS' if not errors else 'PARTIAL' if successes else 'FAILED'
    client.table('scan_runs').update({
        'finished_at': datetime.now(timezone.utc).isoformat(), 'status': status,
        'success_count': successes, 'failure_count': len(errors), 'errors': errors,
    }).eq('id', run_id).execute()
    LOG.info('Scan %s: %s/%s succeeded', status, successes, len(symbols))
    if errors:
        raise RuntimeError(f'Scan {status}: {len(errors)} symbols failed; see scan_runs and logs')
    return successes


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
