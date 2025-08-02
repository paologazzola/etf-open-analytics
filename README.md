# ETF Open Analytics

## Table of Contents

- [ETF Scraper](#etf-scraper)
- [ETF Predictor](#etf-predictor)
- [Portfolio Evaluator](#portfolio-evaluator)
- [License](#license)
- [Disclaimer on Data Usage](#disclaimer-on-data-usage)

ETF Open Analytics is an open-source project for scraping and analyzing historical ETF (Exchange-Traded Funds) data.

It uses:
- **Python** for data collection  
- **PostgreSQL** for structured data storage  
- **GitHub Actions** to schedule and automate daily updates  

This is a **proof-of-concept project**: the dataset currently includes only a subset of ETFs and partial historical data.  
However, the architecture is designed to be extensible, and it can be expanded to include more complete data and support deeper, more accurate portfolio analysis, backtesting, and machine learning applications.

## ETF Scraper

The `etf_scraper` module is responsible for downloading and storing historical ETF price data.

### Features

- Retrieves daily historical prices using [Yahoo Finance](https://finance.yahoo.com/) via `yfinance`
- Stores data into a PostgreSQL database (e.g. [Render](https://render.com))
- Keeps track of the latest saved price per ETF
- Automatically updates missing days on each run
- Uses GitHub Actions to run daily via scheduled job

### Database Tables

- `etf`: contains ETF metadata (ISIN, description, region, replication method, etc.)
- `etf_price`: contains historical daily prices for each ETF

### Usage

```bash
# Install dependencies
pip install -r etf_scraper/requirements.txt

# Run the updater manually
python etf_scraper/main.py
```

Make sure to create a .env file with the following variables:
```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>
TICKER_FIELD=yahoo_symbol
```

### GitHub Action
The workflow .github/workflows/fetch.yml runs the scraper daily using:
```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Every day at 6:00 UTC
```

To use it:
- Add `DATABASE_URL` as a GitHub secret
- Add `TICKER_FIELD` as a GitHub environment variable

## ETF Scraper

The `etf_scraper` module is responsible for downloading and storing historical ETF price data.

## ETF Predictor

The `etf_predictor` module provides tools for forecasting future ETF prices and trends using historical data.

### Features

- Applies machine learning models to predict future ETF prices
- Supports backtesting with historical data
- Allows evaluation of prediction accuracy
- Designed for extensibility with custom models and strategies

### Usage

```bash
# Install dependencies
pip install -r etf_predictor/requirements.txt

# Run a prediction example
python etf_predictor/main.py
```

Make sure to create a `.env` file with any required variables for your portfolio evaluation module.

## Portfolio Evaluator

The `portfolio_evaluator` module provides advanced tools for analyzing, simulating, and optimizing ETF portfolios using historical data and machine learning techniques.

### Features

- Calculates key portfolio metrics such as returns, volatility, Sharpe ratio, and maximum drawdown
- Simulates portfolio performance over time using historical ETF prices
- Supports scenario analysis and stress testing to evaluate portfolio robustness
- Applies machine learning models to optimize portfolio allocation based on risk and return objectives
- Performs feature selection and dimensionality reduction to identify the most relevant ETFs for a given strategy
- Enables backtesting of portfolio strategies and evaluation of their predictive performance
- Designed for extensibility with custom evaluation metrics and optimization algorithms

### Usage

```bash
# Install dependencies
pip install -r portfolio_evaluator/requirements.txt

# Run a portfolio evaluation example
python portfolio_evaluator/main.py

# Update or retrain the portfolio evaluation model (run once)
python portfolio_evaluator/run_once.py
```

Make sure to create a `.env` file with any required variables for the portfolio

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to use, modify, and distribute this code for **non-commercial purposes only**.  
Commercial use of this software or the data it processes is **strictly prohibited**.

## Disclaimer on Data Usage
This project uses data fetched from Yahoo Finance (via `yfinance`) for educational and non-commercial research purposes only.  
Make sure your usage complies with [Yahoo’s Terms of Service](https://legal.yahoo.com/ie/en/yahoo/terms/otos/index.html).
