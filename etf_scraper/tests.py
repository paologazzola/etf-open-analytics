import yfinance as yf

df = yf.download("VHVE.L", start="2018-01-01", end="2024-12-31")
print(df.tail())