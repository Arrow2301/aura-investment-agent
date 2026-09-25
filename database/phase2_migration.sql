-- Run after phase1_migration.sql for an existing Aura database.
-- For a new database run schema.sql, phase1_migration.sql, then this file.
-- The scan uses a service-role key only in GitHub Actions; Streamlit uses the anon key.
ALTER TABLE signals ADD COLUMN IF NOT EXISTS technical_score NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS fundamental_score NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS quality_score NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS risk_score NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS aura_score NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS confidence NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS price NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS market_date DATE;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE signals ADD COLUMN IF NOT EXISTS return_5d_pct NUMERIC;
ALTER TABLE signals ADD COLUMN IF NOT EXISTS return_20d_pct NUMERIC;
CREATE INDEX IF NOT EXISTS signals_date_idx ON signals(analysis_date DESC);

CREATE TABLE IF NOT EXISTS stock_analysis (
  id BIGSERIAL PRIMARY KEY, symbol TEXT NOT NULL, analysis_date DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS current_price NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS technical_score NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS fundamental_score NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS quality_score NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS risk_score NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS technical_signals JSONB DEFAULT '[]'::jsonb;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS fundamental_signals JSONB DEFAULT '[]'::jsonb;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS quality_signals JSONB DEFAULT '[]'::jsonb;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS risk_notes TEXT;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS aura_score NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS action TEXT;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS confidence NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS explanation TEXT;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS market_date DATE;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS return_5d_pct NUMERIC;
ALTER TABLE stock_analysis ADD COLUMN IF NOT EXISTS return_20d_pct NUMERIC;
CREATE UNIQUE INDEX IF NOT EXISTS stock_analysis_symbol_analysis_date_idx ON stock_analysis(symbol,analysis_date);

CREATE TABLE IF NOT EXISTS scan_runs (
  id UUID PRIMARY KEY, started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ, status TEXT NOT NULL CHECK(status IN ('RUNNING','SUCCESS','PARTIAL','FAILED')),
  universe_count INTEGER NOT NULL DEFAULT 0, success_count INTEGER NOT NULL DEFAULT 0,
  failure_count INTEGER NOT NULL DEFAULT 0, errors JSONB NOT NULL DEFAULT '[]'::jsonb
);

ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_runs ENABLE ROW LEVEL SECURITY;
-- Shared research outputs readable in the public dashboard; writes require service role.
DROP POLICY IF EXISTS "Public read signals" ON signals;
CREATE POLICY "Public read signals" ON signals FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "Public read stock analysis" ON stock_analysis;
CREATE POLICY "Public read stock analysis" ON stock_analysis FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "Public read scan runs" ON scan_runs;
CREATE POLICY "Public read scan runs" ON scan_runs FOR SELECT TO anon, authenticated USING (true);
