"""Manual one-time end-to-end check for personal automation settings."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from automation.notify import credentials, send_telegram
from database.supabase_client import get_client


def run():
    settings = credentials()
    client = get_client(write=True)
    for table in ('signals','paper_trades','alert_events','portfolio_daily','strategy_backtests'):
        query = client.table(table).select('*').limit(1)
        if table in ('paper_trades','portfolio_daily','alert_events'):
            query = query.eq('user_id', settings['AURA_USER_ID'])
        query.execute()
    send_telegram('AURA setup verified. Daily paper research and portfolio alerts are ready.',
                  settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID'])
    logging.info('Database tables and Telegram delivery verified for the configured account.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
