CREATE TABLE IF NOT EXISTS signals(
 id SERIAL PRIMARY KEY,
 symbol TEXT,
 score NUMERIC,
 decision TEXT,
 explanation TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades(
 id SERIAL PRIMARY KEY,
 symbol TEXT,
 action TEXT,
 quantity INTEGER,
 price NUMERIC,
 reason TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_log(
 id SERIAL PRIMARY KEY,
 lesson TEXT,
 metric NUMERIC,
 created_at TIMESTAMP DEFAULT NOW()
);
