CREATE TABLE IF NOT EXISTS signals(
id BIGSERIAL PRIMARY KEY,
symbol TEXT,
score NUMERIC,
action TEXT,
confidence NUMERIC,
reason TEXT,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades(
id BIGSERIAL PRIMARY KEY,
symbol TEXT,
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

CREATE TABLE IF NOT EXISTS learning(
id BIGSERIAL PRIMARY KEY,
prediction TEXT,
actual TEXT,
accuracy NUMERIC
);
