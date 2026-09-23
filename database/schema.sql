CREATE TABLE IF NOT EXISTS prices(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 trade_date DATE,
 close NUMERIC,
 volume BIGINT
);

CREATE TABLE IF NOT EXISTS signals(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 strategy TEXT,
 technical_score NUMERIC,
 fundamental_score NUMERIC,
 sentiment_score NUMERIC,
 risk_score NUMERIC,
 overall_score NUMERIC,
 action TEXT,
 reason TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolios(
 id BIGSERIAL PRIMARY KEY,
 name TEXT,
 capital NUMERIC
);

CREATE TABLE IF NOT EXISTS positions(
 id BIGSERIAL PRIMARY KEY,
 portfolio TEXT,
 symbol TEXT,
 quantity INTEGER,
 entry_price NUMERIC
);

CREATE TABLE IF NOT EXISTS trades(
 id BIGSERIAL PRIMARY KEY,
 portfolio TEXT,
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
