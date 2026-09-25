-- Apply after phase2_migration.sql. Review existing policies in staging first.
ALTER TABLE paper_trades ADD COLUMN IF NOT EXISTS stop_price NUMERIC CHECK (stop_price IS NULL OR stop_price > 0);
ALTER TABLE paper_trades ADD COLUMN IF NOT EXISTS target_price NUMERIC CHECK (target_price IS NULL OR target_price > 0);

CREATE TABLE IF NOT EXISTS alert_events (
  event_key TEXT PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  event_type TEXT NOT NULL,
  symbol TEXT,
  market_date DATE NOT NULL,
  message TEXT NOT NULL,
  sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE alert_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users read own alerts" ON alert_events;
CREATE POLICY "Users read own alerts" ON alert_events FOR SELECT TO authenticated
  USING (auth.uid() = user_id);
REVOKE ALL ON public.alert_events FROM anon, authenticated;
GRANT SELECT ON public.alert_events TO authenticated;

CREATE TABLE IF NOT EXISTS strategy_backtests (
  symbol TEXT NOT NULL, strategy TEXT NOT NULL, as_of DATE NOT NULL,
  train_start DATE, test_start DATE, tested_bars INTEGER NOT NULL DEFAULT 0,
  trade_count INTEGER NOT NULL DEFAULT 0, win_rate_pct NUMERIC,
  return_pct NUMERIC, benchmark_return_pct NUMERIC,
  max_drawdown_pct NUMERIC, profit_factor NUMERIC,
  fee_bps NUMERIC NOT NULL, slippage_bps NUMERIC NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('OK','INSUFFICIENT','ERROR')),
  notes TEXT, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (symbol,strategy,as_of)
);
ALTER TABLE strategy_backtests ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Read research backtests" ON strategy_backtests;
CREATE POLICY "Read research backtests" ON strategy_backtests FOR SELECT TO anon, authenticated USING (true);
REVOKE ALL ON public.strategy_backtests FROM anon, authenticated;
GRANT SELECT ON public.strategy_backtests TO anon, authenticated;

CREATE TABLE IF NOT EXISTS portfolio_daily (
  user_id UUID NOT NULL REFERENCES auth.users(id), market_date DATE NOT NULL,
  open_cost NUMERIC NOT NULL, marked_value NUMERIC NOT NULL,
  unrealized_pnl NUMERIC NOT NULL, realized_pnl NUMERIC NOT NULL,
  marked_symbols INTEGER NOT NULL, missing_symbols INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id,market_date)
);
ALTER TABLE portfolio_daily ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users read own portfolio daily" ON portfolio_daily;
CREATE POLICY "Users read own portfolio daily" ON portfolio_daily FOR SELECT TO authenticated
  USING (auth.uid() = user_id);
REVOKE ALL ON public.portfolio_daily FROM anon, authenticated;
GRANT SELECT ON public.portfolio_daily TO authenticated;
