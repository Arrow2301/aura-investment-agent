# AURA India Investment Intelligence

AURA scans ten NSE stocks after market close, stores dated research snapshots, measures 5 and 20 trading-session forward returns, and provides a Streamlit dashboard, manual paper-trade journal, and a technical-only historical backtest. It does not place broker orders. A stored closing price is **not a live quote**.

## Production paths

| Purpose | Entry point |
| --- | --- |
| Weekday market scan | `python -m automation.daily_run` |
| Outcome updates | `python -m automation.outcomes` |
| Dashboard | `streamlit run dashboard/app.py` |
| Tests | `python -m unittest discover -s tests -v` |

The older `market/`, `backtest/`, `learning/`, `risk_engine/`, and similarly named modules remain for compatibility. They are **not** the scheduled production implementation. `automation/daily_pipeline.py` delegates to the production scan. Do not use the legacy prototype modules to make investment decisions.

## Deploy in order

1. Create a Supabase project. In its SQL editor, run `database/schema.sql`, `database/phase1_migration.sql`, then `database/phase2_migration.sql` **in that order** for a new project. For an existing Aura project, first inspect the schema and duplicate `(symbol, analysis_date)` rows before creating unique indexes. Back up the database. Apply the missing migrations in staging before production. The migration makes scan summaries publicly readable through the anon key; individual paper trades remain protected with Supabase Auth and row-level security. Do not put a service-role key in Streamlit.
2. In GitHub Actions repository secrets set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`. The service role belongs only in the private Actions runtime. Enable Actions, trigger **AURA tests**, then manually trigger **AURA end-of-day scan**. Check `scan_runs` and `signals`; a partial scan fails the Action and records per-symbol errors.
3. In Streamlit Community Cloud deploy `dashboard/app.py`. Add `SUPABASE_URL` and `SUPABASE_ANON_KEY` to Streamlit secrets. Configure Supabase email authentication for the paper portfolio. Do not paste database credentials into the repository. The public scan pages are readable to anyone with the deployed dashboard URL; protect the hosting app separately if required.
4. Trigger **AURA forward outcomes** after at least 5 completed trading sessions. The workflows run at 17:00 IST and 18:00 IST on weekdays, respectively; GitHub may delay scheduled jobs. A market holiday can yield a recent prior-session snapshot. A missing data provider, schema, or credential causes the Action to fail rather than report success.

Locally, install `requirements.txt`, set the corresponding environment variables, and run the entry points above. `SUPABASE_KEY` remains an anon-key fallback for older local deployments; it does **not** authorize scheduled writes.

## Methodology and limits

- AURA uses observed daily OHLCV and Yahoo Finance fundamentals. Missing fundamental fields are counted as missing, not assumed positive. Yahoo data can lag or be incomplete; verify reported factors and prices before use. `confidence` is the composite score displayed as a percent, **not a calibrated probability**.
- The scan discards today's candle before 16:00 IST, rejects history over five calendar days old, and stores the completed market date. Repeated scans of a date upsert the same symbol/date pair.
- The outcomes view measures close-to-close forward returns for all actions. It is descriptive, not a portfolio backtest, and excludes transaction costs. Earlier results before this version have no reliable recorded starting close, so the outcome updater only fills dates present in retrieved price history.
- The interactive backtest evaluates a historical EMA trend using only each historical prefix and buys/sells at the next session open. It includes fees and slippage. It does not reproduce the full AURA score: historical publication dates for fundamentals are unavailable, so using today's fundamentals in old periods would leak future information. It uses daily OHLC bars and assumes a stop wins if stop and target are touched on one bar. Results are in sample and sensitive to the selected ticker and parameters.
- Paper positions use average cost and the most recently saved close, with the close date displayed. Orders are manual and no broker executes them. There is no automated learning or promotion of strategy parameters. Compare outcomes across dates and test proposed changes separately before changing the production strategy.

## Troubleshooting

- `stock_analysis` or score columns missing: apply the migrations in order, and check the SQL editor for errors.
- Empty scan: verify GitHub secrets, the Action log, `scan_runs.errors`, and that the data provider returned completed daily bars.
- Dashboard connection error: verify the Streamlit **anon** secret and database read policies.
- Paper sign-in fails: enable Supabase email Auth and confirm the `paper_trades` policy from phase 1.
