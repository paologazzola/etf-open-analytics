# ETF Open Analytics

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

Make sure to create a .env file with the following variables:
`
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>
TICKER_FIELD=yahoo_symbol
`

### GitHub Action
The workflow .github/workflows/fetch.yml runs the scraper daily using:
`
on:
  schedule:
    - cron: '0 6 * * *'  # Every day at 6:00 UTC
`

To use it:
- Add `DATABASE_URL` as a GitHub secret
- Add `TICKER_FIELD` as a GitHub environment variable

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to use, modify, and distribute this code for **non-commercial purposes only**.  
Commercial use of this software or the data it processes is **strictly prohibited**.

## Disclaimer on Data Usage
This project uses data fetched from Yahoo Finance (via `yfinance`) for educational and non-commercial research purposes only.  
Make sure your usage complies with [Yahoo’s Terms of Service](https://legal.yahoo.com/ie/en/yahoo/terms/otos/index.html).
