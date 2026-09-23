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

CREATE TABLE IF NOT EXISTS stock_analysis(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 date DATE,
 technical_score NUMERIC,
 fundamental_score NUMERIC,
 sentiment_score NUMERIC,
 overall_score NUMERIC,
 action TEXT,
 confidence NUMERIC,
 reason TEXT,
 risk_notes TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolio(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 quantity INTEGER,
 entry_price NUMERIC,
 current_price NUMERIC,
 profit_loss NUMERIC,
 status TEXT
);

CREATE TABLE IF NOT EXISTS trades(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 action TEXT,
 quantity INTEGER,
 price NUMERIC,
 reason TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_memory(
 id BIGSERIAL PRIMARY KEY,
 prediction TEXT,
 result TEXT,
 lesson TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_logs(
 id BIGSERIAL PRIMARY KEY,
 module TEXT,
 message TEXT,
 severity TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);
