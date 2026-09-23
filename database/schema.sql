CREATE TABLE IF NOT EXISTS market_prices(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 date DATE,
 open NUMERIC,
 high NUMERIC,
 low NUMERIC,
 close NUMERIC,
 volume BIGINT
);

CREATE TABLE IF NOT EXISTS analysis_results(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 date DATE DEFAULT CURRENT_DATE,
 technical_score NUMERIC,
 fundamental_score NUMERIC,
 sentiment_score NUMERIC,
 overall_score NUMERIC,
 strategy TEXT,
 action TEXT,
 confidence NUMERIC,
 reason TEXT
);

CREATE TABLE IF NOT EXISTS paper_positions(
 id BIGSERIAL PRIMARY KEY,
 portfolio_type TEXT,
 symbol TEXT,
 quantity INTEGER,
 entry_price NUMERIC,
 current_price NUMERIC,
 pnl NUMERIC
);

CREATE TABLE IF NOT EXISTS trades(
 id BIGSERIAL PRIMARY KEY,
 portfolio_type TEXT,
 symbol TEXT,
 action TEXT,
 quantity INTEGER,
 price NUMERIC,
 reason TEXT
);

CREATE TABLE IF NOT EXISTS learning_memory(
 id BIGSERIAL PRIMARY KEY,
 prediction TEXT,
 outcome TEXT,
 lesson TEXT
);
