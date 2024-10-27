import os
import pandas as pd
from abc import ABCMeta, abstractmethod
from event import MarketEvent
import yfinance as yf

class DataHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError("Should implement update_bars()")

class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events, csv_dir, symbol_list):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.multiasset = isinstance(self.symbol_list[0], list) if symbol_list else False
        
        # self._open_convert_csv_files()

    def YFdownload2csv(self, start_date, end_date, interval):
        self.interval = interval
        if self.multiasset:
            for ma in self.symbol_list:
                for symbol in ma:

                    df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
                    df = df["Close"]
                    df.to_csv(os.path.join(self.csv_dir, f'{interval}/{symbol}.csv'), index=True)
        
        else:
            for symbol in self.symbol_list:

                df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
                df = df["Close"]
                df.to_csv(os.path.join(self.csv_dir, f'{interval}/{symbol}.csv'), index=True)

    def _open_convert_csv_files(self):
        comb_index = None

        for s in self.symbol_list:

            if self.multiasset:
                self.symbol_data[s] = pd.DataFrame()
                for i,a in enumerate(self.symbol_list[s]):
                    try:
                        new_data = pd.read_csv(os.path.join(self.csv_dir,
                                                            f'{self.interval}/{a}.csv'),
                                                            header=0, 
                                                            index_col=0, 
                                                            parse_dates=True,
                                                            names=['datetime', 
                                                            f'{a}_close']
                        )
                        new_data.sort_index(inplace=True)
                        if comb_index is None:
                            comb_index = new_data.index
                        else:
                            comb_index = comb_index.union(new_data.index)
                        self.latest_symbol_data[s] = []

                        if i != 0:
                            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad')
                        self.symbol_data[s] = pd.concat([self.symbol_data[s], new_data])
                        self.symbol_data[s][f"{a}_returns"] = self.symbol_data[s][f"{a}_close"].pct_change().dropna()
                    
                    except FileNotFoundError:
                        print(f"File {a}.csv not found.")

                    self.symbol_data[s] = self.symbol_data[s].iterrows()
                        

            else:

                self.symbol_data[s] = pd.read_csv(
                    os.path.join(self.csv_dir, f'{self.interval}/{s}.csv'),
                    header=0, index_col=0, parse_dates=True,
                    names=['datetime', 'close']
                )
            
                self.symbol_data[s].sort_index(inplace=True)
                # create combindex for dates that has all available dates in it
                if comb_index is None:
                    comb_index = self.symbol_data[s].index
                else:
                    comb_index = comb_index.union(self.symbol_data[s].index)
                self.latest_symbol_data[s] = []

        # use combindex to adjust dates and forward-fill missing data
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad')
            self.symbol_data[s]["returns"] = self.symbol_data[s]["close"].pct_change().dropna()
            self.symbol_data[s] = self.symbol_data[s].iterrows()
    

    def _get_new_bar(self, symbol):
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, b[0], b[1]['close'],])

    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print(f"That symbol {symbol} is not available in the historical data set.")
            return None
        else:
            return bars_list[-N:]

    def update_bars(self):
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())