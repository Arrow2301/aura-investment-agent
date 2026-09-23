CREATE TABLE IF NOT EXISTS trades(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 portfolio TEXT,
 action TEXT,
 quantity INTEGER,
 price NUMERIC,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance(
 id BIGSERIAL PRIMARY KEY,
 date DATE,
 portfolio_value NUMERIC,
 pnl NUMERIC,
 drawdown NUMERIC
);

CREATE TABLE IF NOT EXISTS predictions(
 id BIGSERIAL PRIMARY KEY,
 symbol TEXT,
 prediction TEXT,
 outcome TEXT,
 accuracy NUMERIC
);

CREATE TABLE IF NOT EXISTS reports(
 id BIGSERIAL PRIMARY KEY,
 report TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);
