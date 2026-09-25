"""Idempotent Telegram digests and user-scoped paper-position alerts."""
import argparse
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.supabase_client import get_client
from portfolio.ledger import summarize

IST = timezone(timedelta(hours=5, minutes=30))
LOG = logging.getLogger(__name__)


def credentials():
    values = {name: os.getenv(name) for name in ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'AURA_USER_ID')}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError('Missing alert secrets: ' + ', '.join(missing))
    return values


def send_telegram(message, token, chat_id):
    import requests
    try:
        response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
                                 json={'chat_id': chat_id, 'text': message}, timeout=15)
        response.raise_for_status()
        if not response.json().get('ok'):
            raise RuntimeError('Telegram rejected the message')
    except Exception:
        # Requests exceptions can include the bot token in the URL.
        raise RuntimeError('Telegram delivery failed; check bot configuration privately') from None


def send_once(client, event_key, kind, symbol, market_date, message, settings):
    prior = client.table('alert_events').select('event_key').eq('event_key', event_key).limit(1).execute().data or []
    if prior:
        return False
    send_telegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID'])
    client.table('alert_events').insert({'event_key': event_key, 'event_type': kind,
        'symbol': symbol, 'market_date': market_date, 'message': message,
        'user_id': settings['AURA_USER_ID']}).execute()
    return True


def digest_text(rows, market_date, status):
    entries = sorted((r for r in rows if r['action'] == 'BUY_CANDIDATE'),
                     key=lambda r: float(r.get('aura_score') or 0), reverse=True)
    exits = sorted(r['symbol'] for r in rows if r['action'] == 'EXIT_CANDIDATE')
    lines = [f'AURA daily research · {market_date}',
             f'Scan: {status} · {len(rows)} stocks',
             f'Entry candidates: {len(entries)} · Exit candidates: {len(exits)}',
             '', 'Entry candidates:']
    lines += [f"• {r['symbol']}: score {r['aura_score']}/100 · close ₹{float(r.get('price') or 0):,.2f}"
              for r in entries[:12]] or ['• None today']
    lines += ['', 'Exit candidates (for existing longs):']
    lines += [f'• {s}' for s in exits[:12]] or ['• None today']
    if len(entries) > 12 or len(exits) > 12:
        lines.append('More tickers are in the dashboard.')
    lines += ['', 'Prices are last daily closes. Review risk and current price before acting. Paper research only.']
    return '\n'.join(lines)


def daily_digest():
    settings = credentials()
    client = get_client(write=True)
    latest = client.table('scan_runs').select('status').order('started_at', desc=True).limit(1).execute().data or []
    if not latest or latest[0]['status'] not in ('SUCCESS', 'PARTIAL'):
        raise RuntimeError('No completed scan available for the digest')
    records = client.table('signals').select('symbol,action,aura_score,price,analysis_date').order('analysis_date', desc=True).limit(200).execute().data or []
    if not records:
        raise RuntimeError('No signals available for the digest')
    date = str(records[0]['analysis_date'])
    rows = [row for row in records if row['analysis_date'] == date]
    if date != datetime.now(IST).date().isoformat():
        LOG.info('No new completed market session; skipping stale daily digest (%s)', date)
        return False
    if (datetime.now(IST).date() - datetime.fromisoformat(date).date()).days > 5:
        raise RuntimeError('Latest signals are too old for a daily alert')
    text = digest_text(rows, date, latest[0]['status'])
    send_once(client, f"digest:{settings['AURA_USER_ID']}:{date}", 'DAILY', None,
              date, text, settings)


def exit_reason(position, last_price, action):
    """Return a reason for reviewing a held long; never place an order."""
    if position['quantity'] <= 0:
        return None
    if position.get('stop') is not None and last_price <= position['stop']:
        return 'STOP LEVEL REACHED'
    if action == 'EXIT_CANDIDATE':
        return 'TREND EXIT CANDIDATE'
    if position.get('target') is not None and last_price >= position['target']:
        return 'TARGET LEVEL REACHED'
    return None


def intraday_quote(symbol, now):
    import pandas as pd
    import yfinance as yf
    frame = yf.download(symbol, period='1d', interval='5m', auto_adjust=True,
                        threads=False, progress=False)
    if frame.empty:
        return None
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    timestamp = pd.Timestamp(frame.index[-1])
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(IST)
    age = (now - timestamp.to_pydatetime().astimezone(IST)).total_seconds()
    if age < -300 or age > 3600 or timestamp.tz_convert(IST).date() != now.date():
        return None
    value = float(frame['Close'].iloc[-1])
    return (value, timestamp.isoformat()) if value > 0 else None


def monitor_portfolio(intraday=False):
    settings = credentials()
    now = datetime.now(IST)
    client = get_client(write=True)
    # The service key bypasses RLS, so scope every personal query to this account.
    rows = client.table('paper_trades').select('*').eq('user_id', settings['AURA_USER_ID']).order('traded_at').limit(1000).execute().data or []
    if len(rows) == 1000:
        raise RuntimeError('Trade journal exceeded 1,000 rows; refusing incomplete portfolio analysis')
    positions = summarize(rows)
    latest = client.table('signals').select('symbol,price,action,analysis_date').order('analysis_date', desc=True).limit(200).execute().data or []
    signals = {r['symbol']: r for r in reversed(latest)}
    open_cost = marked = marked_cost = realized = covered = missing = 0.0
    for symbol, position in positions.items():
        realized += position['realized_pnl']
        if position['quantity'] <= 0:
            continue
        open_cost += position['cost']
        snap = signals.get(symbol)
        if not snap:
            missing += 1
            continue
        date = str(snap['analysis_date'])
        if (now.date() - datetime.fromisoformat(date).date()).days > 5:
            missing += 1
            continue
        quote = intraday_quote(symbol, now) if intraday else None
        if intraday and quote is None:
            LOG.warning('Skipping stale/unavailable intraday quote for %s', symbol)
            missing += 1
            continue
        value = quote[0] if quote else float(snap['price'])
        if not intraday:
            marked += value * position['quantity']
            marked_cost += position['cost']
            covered += 1
        reason = exit_reason(position, value, snap.get('action'))
        if reason:
            message = (f'AURA paper position alert · {symbol}\n{reason}\n'
                       f"Observed {'5-minute quote' if quote else 'daily close'}: ₹{value:,.2f}\n"
                       f"Held: {position['quantity']:g} shares · average cost: ₹{position['cost'] / position['quantity']:,.2f}\n"
                       'Review now; no trade was placed. Market data may be delayed.')
            event_key = f"position:{settings['AURA_USER_ID']}:{symbol}:{reason}:{now.date()}"
            send_once(client, event_key, 'POSITION_EXIT', symbol, date, message, settings)
    if not intraday:
        market_date = str(latest[0]['analysis_date']) if latest else now.date().isoformat()
        client.table('portfolio_daily').upsert({'user_id': settings['AURA_USER_ID'],
            'market_date': market_date, 'open_cost': open_cost, 'marked_value': marked,
            'unrealized_pnl': marked - marked_cost,
            'realized_pnl': realized, 'marked_symbols': int(covered), 'missing_symbols': int(missing)},
            on_conflict='user_id,market_date').execute()
    return {'open_positions': sum(p['quantity'] > 0 for p in positions.values()), 'missing_marks': int(missing)}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['digest', 'positions', 'intraday'])
    mode = parser.parse_args().mode
    if mode == 'digest':
        daily_digest()
    else:
        print(monitor_portfolio(intraday=mode == 'intraday'))
