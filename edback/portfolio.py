# portfolio.py

import pandas as pd
from event import OrderEvent

class Portfolio:
    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        self.bars = bars
        self.events = events
        self.symbol_tuple = self.bars.symbol_tuple
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.multiasset = bars.multiasset
        self.all_positions = self.construct_all_positions()
        self.current_positions = {t: {s: 0 for s in t} for t in self.symbol_tuple} if self.multiasset else {s: 0 for s in self.symbol_tuple}

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(self):
        if self.multiasset:
            d = {t: {s: 0 for s in t} for t in self.symbol_tuple}
        else:
            d = {s: 0 for s in self.symbol_tuple}
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        if self.multiasset:
            d = {t: {s: 0.0 for s in t} for t in self.symbol_tuple}
        else:
            d = {s: 0.0 for s in self.symbol_tuple}
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        if self.multiasset:
            d = {t: {s: 0.0 for s in t} for t in self.symbol_tuple}
        else:
            d = {s: 0.0 for s in self.symbol_tuple}
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self, event):
        latest_datetime = self.bars.get_latest_bars(self.symbol_tuple[0])[0]

        if self.multiasset:
            dp, dh = {t: {s: 0.0 for s in t} for t in self.symbol_tuple}
        else:
            dp, dh = {s: 0.0 for s in self.symbol_tuple}

        dp['datetime'] = latest_datetime
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_tuple:
            if self.multiasset:
                for i,t  in enumerate(s):
                    dp[s][t] = self.current_positions[s][t]
                    market_value = self.current_positions[s][t] * self.bars.get_latest_bars(s)[3+i] # date, tckr1, tckr2,
                    dh[s][t] = market_value
                    dh['total'] += market_value
            else:
                dp[s] = self.current_positions[s]
                market_value = self.current_positions[s] * self.bars.get_latest_bars(s)[2]
                dh[s] = market_value
                dh['total'] += market_value

        self.all_positions.append(dp)
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        # modify to handle ma. current pos is dict with tuple: ticker
    
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        
        if self.multiasset:
            self.current_positions[fill.tuple][fill.symbol] += fill_dir * fill.quantity
        else:
            self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        # modify to handle ma
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        
        if self.multiasset:
            for i, tckr in enumerate(fill.tuple):
                if fill.symbol == tckr:
                    index = i + 1
            fill_cost = self.bars.get_latest_bars(fill.symbol)[0][len(fill.tuple) + index]
        else:
            fill_cost = self.bars.get_latest_bars(fill.symbol)[0][2]

        cost = fill_dir * fill_cost * fill.quantity # fill_cost is close
        self.current_holdings[fill.tuple][fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        order = None

        symbol = signal.symbol
        sig = signal.signal_type
        strength = signal.strength
        tuple = signal.tuple

        mkt_quantity = 100
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        # modify this to handle multiasset -> loop through sig and do orders for each of the single asset
        
        if cur_quantity == 0:
            if sig == 'LONG':
                order = OrderEvent(tuple, symbol, order_type, mkt_quantity, 'BUY') # ADD TUPLE AS ARG TO CREATE FILL WITH TUPLE
            elif sig == 'SHORT':
                order = OrderEvent(tuple, symbol, order_type, mkt_quantity, 'SELL')

        elif cur_quantity < 0:
            if sig == 'LONG':
                order = OrderEvent(tuple, symbol, order_type, (mkt_quantity + abs(cur_quantity)), 'BUY')
            elif sig == 'SHORT':
                order = OrderEvent(tuple, symbol, order_type, mkt_quantity, 'SELL')
            elif sig == 'EXIT':
                order = OrderEvent(tuple, symbol, order_type, abs(cur_quantity), 'BUY')
        
        else:
            if sig == 'LONG':
                order = OrderEvent(tuple, symbol, order_type, mkt_quantity, 'BUY')
            elif sig == 'SHORT':
                order = OrderEvent(tuple, symbol, order_type, (mkt_quantity + abs(cur_quantity)), 'SELL')
            elif sig == 'EXIT':
                order = OrderEvent(tuple, symbol, order_type, abs(cur_quantity), 'SHORT')
        
        
        ''' was in place of the above

        if sig == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if sig == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if sig == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if sig == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        '''

        return order

    def update_signal(self, event):
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

            