-- Additive Phase 1 migration. Review in a staging Supabase project before production.
ALTER TABLE signals ADD COLUMN IF NOT EXISTS analysis_date DATE DEFAULT CURRENT_DATE;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS explanation JSONB DEFAULT '{}'::jsonb;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS risk_setup JSONB DEFAULT '{}'::jsonb;
CREATE UNIQUE INDEX IF NOT EXISTS signals_symbol_analysis_date_idx ON signals(symbol, analysis_date);

CREATE TABLE IF NOT EXISTS stock_analysis (id BIGSERIAL PRIMARY KEY, symbol TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS analysis_date DATE DEFAULT CURRENT_DATE;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS risk_setup JSONB DEFAULT '{}'::jsonb;
CREATE UNIQUE INDEX IF NOT EXISTS stock_analysis_symbol_analysis_date_idx ON stock_analysis(symbol, analysis_date);

CREATE TABLE IF NOT EXISTS paper_trades (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id),
  symbol TEXT NOT NULL CHECK (length(symbol) BETWEEN 1 AND 30),
  side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
  quantity NUMERIC NOT NULL CHECK (quantity > 0),
  price NUMERIC NOT NULL CHECK (price > 0),
  traded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes TEXT DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE paper_trades ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users manage their own paper trades" ON paper_trades;
CREATE POLICY "Users manage their own paper trades" ON paper_trades
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
