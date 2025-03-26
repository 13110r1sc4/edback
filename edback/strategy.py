from abc import ABCMeta, abstractmethod
from event import SignalEvent
import sys
import os
import numpy as np
external_path = os.path.abspath('/Users/leonardorisca/Desktop/AT/strats/CCSS')
sys.path.append(external_path)
from CCSS_fun import CCSS


class Strategy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self, event):
        raise NotImplementedError("Should implement calculate_signals()")

class MovingAverageCrossoverStrategy(Strategy):
    def __init__(self, bars, events, short_window=10, long_window=30):
        self.bars = bars
        self.symbol_tuple = self.bars.symbol_tuple
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_tuple:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_tuple:
                bars = self.bars.get_latest_bars(symbol, N=self.long_window)
                if bars is not None and len(bars) == self.long_window:
                    short_sma = sum([b[5] for b in bars[-self.short_window:]]) / self.short_window
                    long_sma = sum([b[5] for b in bars]) / self.long_window

                    dt = bars[-1][1]
                    if short_sma > long_sma and self.bought[symbol] == "OUT":
                        sig_dir = 'LONG'
                        signal = SignalEvent(symbol, dt, sig_dir)
                        self.events.put(signal)
                        self.bought[symbol] = 'LONG'
                    elif short_sma < long_sma and self.bought[symbol] == "LONG":
                        sig_dir = 'EXIT'
                        signal = SignalEvent(symbol, dt, sig_dir)
                        self.events.put(signal)
                        self.bought[symbol] = 'OUT'

class NotAPairTrade(Strategy):
    #### DEF: 
    #### Use specifics only from ccss and only do what they say
    def __init__(self, bars, events, model_window):
        
        self.bars = bars
        self.symbol_tuple = self.bars.symbol_tuple
        self.events = events
        self.model_window = model_window

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for ma in self.symbol_tuple:
            bought[ma] = {}
            for s in ma:
                bought[ma][s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for tuple in self.symbol_tuple:
                bars = self.bars.get_latest_bars(tuple, N=self.model_window)
                
                if bars is not None and len(bars) == self.model_window:
                    bars_array = np.array([(t[3], t[4]) for t in bars]).T
                    latestPriceForFill = bars_array[:,-1].T

                    ccss = CCSS(bars_array)
                    ccss.fit()
                    specific = ccss.predict().specific()
                    dt = bars[-1][0]
                    sig_dir = []
                    b = []
                    for spec in specific:
                        if spec > 0:
                            sig_dir.append('LONG')
                            b.append('LONG')
                        elif spec < 0:
                            sig_dir.append('SHORT')
                            b.append('SHORT')
                        else:
                            sig_dir.append('OUT')
                            b.append('OUT')

                    # MODIFY ORDER QUANTITY BASED ON COINTEGRATION COEFFICIENT
                    order_quantity = [0.1, 1]

                    signal = SignalEvent(tuple, dt, sig_dir, order_quantity, latestPriceForFill)
                    self.events.put(signal)
                    self.bought[tuple] = b