
import pandas as pd
import yfinance as yf
import datetime


tickers       = ["BTC-USD"]
intervals     = ["90m"]
end_date      = datetime.datetime.now()
start_date    = end_date - datetime.timedelta(days=60)


df = yf.download(tickers[0], start=start_date, end=end_date, interval=intervals[0])
df.to_csv(f'/Users/leonardorisca/Desktop/AT/propBT/ClaudeAI_test/data/90m/BTC-USD.csv', index=True)