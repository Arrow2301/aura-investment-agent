CREATE TABLE IF NOT EXISTS signals(id bigserial primary key,symbol text,score numeric,action text,reason text,created_at timestamp default now());
CREATE TABLE IF NOT EXISTS trades(id bigserial primary key,symbol text,action text,quantity int,price numeric,created_at timestamp default now());
CREATE TABLE IF NOT EXISTS performance(id bigserial primary key,date date,value numeric,pnl numeric);
CREATE TABLE IF NOT EXISTS learning(id bigserial primary key,prediction text,outcome text,accuracy numeric);
