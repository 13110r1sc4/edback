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
    def __init__(self, events, csv_dir, symbol_tuple):
        self.events = events
        self.csv_dir = csv_dir
        assert isinstance(symbol_tuple, tuple), "symbol_tuple must be a tuple"
        self.check_input(symbol_tuple)
        self.symbol_tuple = symbol_tuple
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.multiasset = isinstance(self.symbol_tuple[0], tuple)
        print(f'Multiasset: {self.multiasset}')
        
        # self._open_convert_csv_files()

    def check_input(self, tup):
        if not isinstance(tup, tuple):
            raise TypeError("Input must be a tuple")
        
        for item in tup:
            if isinstance(item, tuple):
                self.check_input(item)
            elif not isinstance(item, str):
                raise TypeError("All elements in the tuple (and nested tuples) must be strings")

    def YFdownload2csv(self, start_date, end_date, interval):
        assert isinstance(interval, str), "Interval must be a str"
        self.interval = interval
        if self.multiasset:
            symbols = []
            for subtuple in self.symbol_tuple:
                for symbol in subtuple:
                    symbols.append(symbol)
        else:
            symbols = self.symbol_tuple

        for symbol in symbols:
            try:
                df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
                if not df.empty:
                    df["Close"].to_csv(os.path.join(self.csv_dir, f'{interval}/{symbol}.csv'), index=True)
            except Exception as e:
                    print(f"Error downloading {symbol}: {str(e)}")

    def _open_convert_csv_files(self):
        '''
        Each csv file must have two columns:
         1. Datetime
         2. Price
        '''

        for s in self.symbol_tuple:
                
            dfs = []
            for tkr in s:
                try:
                    new_data = pd.read_csv(os.path.join(self.csv_dir, f'{self.interval}/{tkr}.csv'),
                                                            header=0, index_col=0, parse_dates=['datetime'], names=['datetime', f'{tkr}_close'])
                    new_data.sort_index(inplace=True)
                    
                    if not pd.api.types.is_numeric_dtype(new_data[f'{tkr}_close']):
                        new_data[f'{tkr}_close'] = pd.to_numeric(new_data[f'{tkr}_close'], errors='coerce')

                    new_data.interpolate(method="linear", inplace=True)

                    new_data[f"{tkr}_returns"] = new_data[f"{tkr}_close"].pct_change().fillna(0)
                    dfs.append(new_data)

                except FileNotFoundError:
                    print(f"File {tkr}.csv not found.")

                self.latest_symbol_data[s] = []
                self.symbol_data[s] = pd.concat(dfs, axis=1, join="outer")

                if self.symbol_data[s].iloc[0].isna().any():
                    self.symbol_data[s].iloc[0] = self.symbol_data[s].iloc[0].ffill()
                self.symbol_data[s].interpolate(method="linear", inplace=True)
                self.symbol_data[s] = self.symbol_data[s].iterrows()
    

    def _get_new_bar(self, symbol):
        '''
        symbol (input):
        if self.multiasset: tuple
        else: str
        '''
        for b in self.symbol_data[symbol]:

            if self.multiasset:
                if not isinstance(symbol, tuple):
                    print("Method argument 'symbol' has to be a tuple when there are multiple assets")
                else:
                    yield tuple([b[0]]+ [symbol[_] for _ in range(len(symbol))] + [b[1][f'{tckr}_close'] for tckr in symbol]) # b 1 is all but the index

            else:
                if not isinstance(symbol, str):
                    print("Method argument 'symbol' has to be a str when single asset")
                else:
                    yield tuple([b[0], symbol, b[1]['close']])

    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print(f"That symbol {symbol} is not available in the historical data set.")
            return None
        else:
            if len(bars_list) >= N: # should be changed, this is temp 
                return bars_list[-N:]

    def update_bars(self):
        
        for s in self.symbol_tuple:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)

        self.events.put(MarketEvent())