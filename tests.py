import datetime
import yfinance as yf
interval   = "90m"
end_date    = datetime.datetime.now()
start_date  = end_date - datetime.timedelta(days=10)

df = yf.download(("AAPL"), start=start_date, end=end_date, interval=interval)
