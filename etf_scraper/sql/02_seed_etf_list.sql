-- 1. Vanguard FTSE Developed World UCITS ETF - Accumulating
INSERT INTO etf (
    name, isin, description, distribution_policy, region,
    replication_method, issuer, yahoo_symbol, asset_class, last_price_date
) VALUES (
    'A2PLS9',
    'IE00BK5BQV03',
    'Vanguard FTSE Developed World UCITS ETF - Accumulating',
    'accumulating',
    'developed',
    'physical',
    'vanguard',
    'VHVE.L',
    'equity',
    NULL
);

-- 2. iShares Core MSCI World UCITS ETF USD (Acc)
INSERT INTO etf (
    name, isin, description, distribution_policy, region,
    replication_method, issuer, yahoo_symbol, asset_class, last_price_date
) VALUES (
    'A0RPWJ',
    'IE00B4L5YC18',
    'iShares Core MSCI World UCITS ETF USD (Acc)',
    'accumulating',
    'developed',
    'physical',
    'ishares',
    'ISAC.L',
    'equity',
    NULL
);

-- 3. iShares Core MSCI Emerging Markets IMI UCITS ETF USD (Acc)
INSERT INTO etf (
    name, isin, description, distribution_policy, region,
    replication_method, issuer, yahoo_symbol, asset_class, last_price_date
) VALUES (
    'A0RPWH',
    'IE00B6R52259',
    'iShares Core MSCI Emerging Markets IMI UCITS ETF USD (Acc)',
    'accumulating',
    'emerging',
    'physical',
    'ishares',
    'ISAC.L',
    'equity',
    NULL
);

-- 4. Amundi STOXX Europe 600 UCITS ETF Accumulating
INSERT INTO etf (
  name,
  isin,
  description,
  distribution_policy,
  region,
  replication_method,
  issuer,
  yahoo_symbol,
  asset_class,
  last_price_date
) VALUES (
  'LYX0Q0',
  'LU0908500753',
  'Amundi STOXX Europe 600 UCITS ETF Accumulating',
  'accumulating',
  'developed',
  'physical',
  'amundi',
  'MEUD.PA',
  'equity',
  NULL
);

-- 5. Vanguard EUR Eurozone Government Bond UCITS ETF EUR Accumulating
INSERT INTO etf (
    name, isin, description, distribution_policy, region,
    replication_method, issuer, yahoo_symbol, asset_class, last_price_date
) VALUES (
    'VGEA',
    'IE00BH04GL39',
    'Vanguard EUR Eurozone Government Bond UCITS ETF EUR Accumulating',
    'accumulating',
    'developed',
    'physical',
    'vanguard',
    'VETA.L',
    'bond',
    NULL
);

-- 6. Vanguard EUR Corporate Bond UCITS ETF EUR Accumulating
INSERT INTO etf (
    name, isin, description, distribution_policy, region,
    replication_method, issuer, yahoo_symbol, asset_class, last_price_date
) VALUES (
    'VECA',
    'IE00BZ163L38',
    'Vanguard EUR Corporate Bond UCITS ETF EUR Accumulating',
    'accumulating',
    'developed',
    'physical',
    'vanguard',
    'VECA.DE',
    'bond',
    NULL
);

-- 7. iShares Global Aggregate Bond ESG SRI UCITS ETF EUR Hedged Accumulation
INSERT INTO etf (
    name, isin, description, distribution_policy, region,
    replication_method, issuer, yahoo_symbol, asset_class, last_price_date
) VALUES (
    'AEGE',
    'IE00BDBRDM35',
    'iShares Global Aggregate Bond ESG SRI UCITS ETF EUR Hedged Accumulation',
    'accumulating',
    'developed',
    'physical',
    'ishares',
    'AEGE.DE',
    'bond',
    NULL
);

-- 8. Vanguard S&P 500 UCITS ETF USD Accumulating
INSERT INTO etf (
  name,
  isin,
  description,
  distribution_policy,
  region,
  replication_method,
  issuer,
  yahoo_symbol,
  asset_class,
  last_price_date
) VALUES (
  'A1JX53',
  'IE00B3XXRP09',
  'Vanguard S&P 500 UCITS ETF USD Accumulating',
  'accumulating',
  'developed',
  'physical',
  'vanguard',
  'VUSD.L',
  'equity',
  NULL
);
