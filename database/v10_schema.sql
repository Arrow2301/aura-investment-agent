CREATE TABLE IF NOT EXISTS signal_memory(
id BIGSERIAL PRIMARY KEY,
symbol TEXT,
prediction TEXT,
outcome TEXT,
accuracy NUMERIC
);

CREATE TABLE IF NOT EXISTS portfolio_metrics(
id BIGSERIAL PRIMARY KEY,
date DATE,
value NUMERIC,
risk TEXT
);
