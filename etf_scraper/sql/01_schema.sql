CREATE TABLE etf (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    isin TEXT UNIQUE,
    description TEXT NOT NULL,
    distribution_policy TEXT CHECK (distribution_policy IN ('accumulating', 'distributing')),
    region TEXT CHECK (region IN ('all_world', 'developed', 'emerging')),
    replication_method TEXT CHECK (replication_method IN ('physical', 'synthetic')),
    issuer TEXT NOT NULL,
    yahoo_symbol TEXT UNIQUE NOT NULL,
    asset_class TEXT CHECK (asset_class IN ('equity', 'bond')) NOT NULL,
    last_price_date DATE
);

CREATE TABLE etf_price (
    id SERIAL PRIMARY KEY,
    etf_id INTEGER REFERENCES etf(id),
    date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    UNIQUE(etf_id, date)
);