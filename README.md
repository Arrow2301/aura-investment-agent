# AURA · Automated paper research for NSE equities

AURA scans a curated 50-stock NSE watchlist plus open paper positions, records end-of-day entry and exit *candidates*, sends a Telegram summary, checks logged holdings for exit conditions, measures forward outcomes, and runs weekly held-out technical backtests. The dashboard is read-only research except for your manual paper-trade journal. **No broker orders are submitted. Returns cannot be guaranteed.**

## One-time setup

1. Back up the existing Supabase project. Apply `database/phase3_automation.sql` in its SQL Editor **after** the previous phase 1 and 2 migrations. Review the changes on a staging copy first. This adds optional stop/target columns to `paper_trades` and RLS-protected alerts and portfolio history. It also adds public read-only backtest results.
2. Configure Supabase email Auth and sign in on **Paper portfolio** in the Streamlit dashboard. Copy the **Account ID for one-time alert setup** displayed there. This ensures the server scanner reads only your paper trades even though it has a database secret key.
3. In Telegram, create a bot using [@BotFather](https://t.me/BotFather) and `/newbot`. Open your new bot and send `/start`. Obtain your numeric chat ID with Telegram's `getUpdates` method; do this privately because the request uses your bot token. Do not post the bot token or chat ID in an issue, commit, or chat. [Telegram's bot tutorial](https://core.telegram.org/bots/tutorial) covers bot creation.
4. Add these **GitHub Actions repository secrets** (Settings → Secrets and variables → Actions). Keep the existing URL and secret key from Phase 2:

   | Secret | Value |
   | --- | --- |
   | `SUPABASE_URL` | Your project URL |
   | `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key; never put in Streamlit |
   | `AURA_USER_ID` | Signed-in dashboard Account ID (UUID) |
   | `TELEGRAM_BOT_TOKEN` | Token from BotFather |
   | `TELEGRAM_CHAT_ID` | Your private numeric chat ID |

5. Manually run **AURA daily research and alerts** in GitHub Actions after 4 PM IST on a market day. Expect 50+ signals, a single Telegram digest, and `portfolio_daily` for your account. If one stock fails, a partial digest is still attempted, and the Action finishes failed to draw attention to missing data. Repeat a run safely: sent alert keys are stored to reduce duplicates.
6. Manually run **AURA weekly held-out backtests** once. Check **Strategy performance** on the dashboard. The first week can have insufficient-trade labels. The **AURA forward outcomes** workflow adds 5- and 20-session close-to-close observations after sufficient market sessions.

## Automatic schedule (India Standard Time)

| When | What happens |
| --- | --- |
| Weekdays 11:05 AM and 2:35 PM | Check open paper positions using recent 5-minute vendor quotes; alert on recorded stop/target or prior trend exit. |
| Weekdays 5:12 PM | Scan completed daily bars; send Telegram entry/exit digest; mark open paper positions; send new exit alerts. |
| Weekdays 6:00 PM | Fill mature 5- and 20-session outcomes for older signals. |
| Sunday 3:05 PM | Refresh held-out, next-session technical backtests for the watchlist. |

GitHub scheduled Actions can be delayed; neither GitHub nor Yahoo Finance is an exchange-grade real-time alert service. Intraday notifications require a quote from **today within the last hour** and cannot guarantee a timely stop. Prices, fundamentals, and corporate actions should be independently verified before investing real money.

## Your routine

- Read the daily Telegram digest and inspect a stock's explanation and risk setup in Streamlit.
- If you make a **paper** purchase, enter ticker, quantity, executed price, and optional stop/target on **Paper portfolio**. If you sell, enter a SELL transaction. The app prevents selling more than recorded open quantity.
- AURA watches your logged open positions and suggests exits; it does not update your journal or execute your trades. The portfolio page shows average-cost realized P&L, marked unrealized P&L, and a closed-exit win rate. Fees, taxes, and dividends are excluded from the journal.

## Methods and limits

- The daily score combines technical, vendor fundamentals, quality and risk. Missing fundamentals suppress buy eligibility. `EXIT_CANDIDATE` means review an **existing long**, not sell short. A score labelled as confidence is **not a calibrated probability**.
- Breakout target estimates use a fixed 3-ATR projection. Other targets reference the previous 20-session high. These are estimates; gap openings, slippage and orders can produce different fills.
- Weekly backtests use the last 30% of each ticker's available five-year history as a held-out test. The technical rules use prior prices only, enter on the next session, include 10 bps fees and 5 bps slippage per fill, and report actual closed-trade win rates. Tests with fewer than five exits are labelled **INSUFFICIENT**. Open positions are marked but not counted as wins. The buy-and-hold benchmark is the same stock over the test window. Historical fundamentals are excluded because dated vendor releases are unavailable.
- Performance and forward returns are descriptive; strategy parameters are **not automatically promoted** based on backtests. This guards against adapting rules to noise. Neither a historical win rate nor this project's design establishes future profitability.
- The previous prototype directories remain for compatibility. Production entry points: `automation/daily_run.py`, `automation/notify.py`, `automation/outcomes.py`, `automation/backtest_run.py`, and `dashboard/app.py`.

## Test and troubleshoot

Run `python -m unittest discover -s tests -v`. For scheduled failures inspect GitHub Actions logs, `scan_runs.errors`, and database policies. A missing Telegram secret raises an explicit error. A stale market session does not generate a daily digest. Intraday quote gaps skip that stock's alert and are reported in the workflow log.
