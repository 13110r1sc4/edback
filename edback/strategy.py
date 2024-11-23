from abc import ABCMeta, abstractmethod
from event import SignalEvent
import sys
import os

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

class AdjPairTrade(Strategy):
    def __init__(self, bars, events, model_window):
        external_path = os.path.abspath('/Users/CCSS')
        sys.path.append(external_path)
        from model import CCSS
        self.bars = bars
        self.symbol_tuple = self.bars.symbol_tuple
        self.events = events
        self.model_window = model_window

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for ma in self.symbol_tuple:
            key = "||".join(ma)
            bought[key] = {}
            for s in ma:
                bought[key][s] = ['OUT', 'OUT']
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_tuple:
                bars = self.bars.get_latest_bars(symbol, N=self.model_window)
                if bars is not None and len(bars) == self.model_window:
                    ccss = CCSS(bars)
                    ccss.fit()
                    specific = ccss.predict().specific()

                    dt = bars[-1][1]
                    # if spread_pred > spread_actual and self.bought[symbol] == ["OUT", "OUT"]:
                    #     sig_dir = 'LONG'
                    #     signal = SignalEvent(symbol, dt, sig_dir)
                    #     self.events.put(signal)
                    #     self.bought[symbol] = 'LONG'
                    # elif short_sma < long_sma and self.bought[symbol] == "LONG":
                    #     sig_dir = 'EXIT'
                    #     signal = SignalEvent(symbol, dt, sig_dir)
                    #     self.events.put(signal)
                    #     self.bought[symbol] = 'OUT'

                    # ADD LOGIC TO SEE IF SPEC IS SIGNIFICANT + USE EXIT
                    if specific[0] > 0 and specific[1] > 0:
                        if self.bought[symbol] == ["OUT", "OUT"]:
                            sig_dir = ['LONG', 'LONG']
                            signal = SignalEvent(symbol, dt, sig_dir)
                            self.events.put(signal)
                            self.bought[symbol] = ['LONG', 'LONG']
                        else:
                            if "SHORT" in self.bought[symbol]:
                                for _ in range(2):
                                    if self.bought[symbol] == 'SHORT':
                                        self.bought[symbol][_] = 'LONG'
                                # NOT EMISSING SIGNAL TO PERFORM THE SAME ACTION

                    elif specific[0] < 0 and specific[1] < 0:
                        if self.bought[symbol] == ["OUT", "OUT"]:
                            sig_dir = ['SHORT', 'SHORT']
                            signal = SignalEvent(symbol, dt, sig_dir)
                            self.events.put(signal)
                            self.bought[symbol] = ['SHORT', 'SHORT']
                        else:
                            if "LONG" in self.bought[symbol]:
                                for _ in range(2):
                                    if self.bought[symbol] == 'LONG':
                                        self.bought[symbol][_] = 'SHORT'
                                # NOT EMISSING SIGNAL TO PERFORM THE SAME ACTION

                    elif specific[0] > 0 and specific[1] < 0:
                            
                            if self.bought[symbol] == ["OUT", "OUT"]:
                                sig_dir = ['LONG', 'SHORT']
                                signal = SignalEvent(symbol, dt, sig_dir)
                                self.events.put(signal)
                                self.bought[symbol] = ['LONG', 'SHORT']
                            elif self.bought[symbol] == ['LONG', 'SHORT']:
                                pass
                            else:
                                for ind,p in enumerate(['LONG', 'SHORT']):
                                    self.bought[symbol][ind] = p

                    elif specific[0] < 0 and specific[1] > 0:
                        if self.bought[symbol] == ["OUT", "OUT"]:
                            sig_dir = ['SHORT', 'LONG']
                            signal = SignalEvent(symbol, dt, sig_dir)
                            self.events.put(signal)
                            self.bought[symbol] = ['SHORT', 'LONG']
                        elif self.bought[symbol] == ['SHORT', 'LONG']:
                            pass
                        else:
                            for ind,p in enumerate(['SHORT', 'LONG']):
                                    self.bought[symbol][ind] = p