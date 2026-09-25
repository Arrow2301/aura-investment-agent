# AURA India Investment Intelligence

AURA is a research and paper-trading application for Indian equities. It does
**not** execute broker orders or promise investment returns.

## Current architecture

- `automation/daily_run.py` is the production daily scan entry point.
- `data_engine/` retrieves NSE history and fundamentals.
- `intelligence/` produces technical, fundamental, quality, risk, and composite
  AURA results. Technical results now expose each confirmed strategy and risk
  results expose the observed entry, stop, resistance target, and reward/risk.
- `database/supabase_client.py` persists one result per symbol per analysis day.
- `dashboard/` remains the Streamlit entry point and includes authenticated,
  row-level-secured paper-trade journaling.
- `backtesting/engine.py` is a reusable long-only research backtester. Signals
  fill at the next open and reported performance includes fees and slippage.

The repository contains earlier overlapping modules (`backtest/`, `market/`,
and several portfolio prototypes). They are retained in this non-destructive
phase because removing potentially imported modules without deployment usage
data is riskier than documenting the production path above.

## Safe review and deployment

1. Run `python -m unittest discover -s tests -v`.
2. Apply `database/phase1_migration.sql` to a **staging** Supabase project. The
   migration is additive. Review the unique-index creation for pre-existing
   same-day duplicates before applying it to production.
3. Ensure Supabase authentication is configured. The migration enables RLS on
   `paper_trades`; every user can access only rows whose `user_id` matches the
   authenticated identity. Never place service-role credentials in Streamlit
   or repository files.
4. Set `SUPABASE_URL` and the appropriate non-service client key through
   Streamlit/GitHub secrets, run the workflow manually, and inspect staging.
5. Only after review, apply the migration and deploy the commit to production.

The scheduled workflow runs at 01:00 UTC on weekdays, which is 06:30 IST. This
conversion is explicit because GitHub Actions schedules are UTC.

## Backtest contract

`backtesting.engine.run(ohlc, signals)` accepts aligned `BUY`, `EXIT`, and
`HOLD` values. A signal observed on bar *t* can only fill on bar *t+1*. `EXIT`
only closes an existing long. Stops take precedence when both stop and target
are touched in a bar, avoiding optimistic intraday ordering. Defaults include
10 bps fees and 5 bps slippage on each fill. Results include trade count, win
rate, total return, profit factor, maximum drawdown, and buy-and-hold return.

## Deferred deliberately

- Persisted backtest runs and a full interactive dashboard require longer,
  point-in-time signal history and benchmark data (for example, NIFTY 50).
- News sentiment and fundamental score adjustments need licensed/reliable data
  with timestamps to prevent look-ahead bias.
- Historical recommendation backsimulation and portfolio mark-to-market need a
  stable daily snapshot history first.
- Telegram alerts should follow alert preferences, authentication, and secret
  management rather than being wired directly into the scanner.
- Walk-forward optimization must be a separate research artifact with explicit
  human review; it will not automatically promote parameters to production.
- Destructive cleanup of duplicate legacy modules is postponed until import and
  deployment consumers are audited.
