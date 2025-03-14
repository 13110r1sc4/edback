# event.py

class Event:
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type = 'MARKET'

class SignalEvent(Event):
    def __init__(self, tuple, datetime, signal_type, order_quantity, latestPricesForFill):
        self.type = 'SIGNAL'
        # self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.order_quantity = order_quantity
        self.tuple = tuple
        self.latestPricesForFill = latestPricesForFill

class OrderEvent(Event):
    def __init__(self, datetime, tuple, symbol, order_type, quantity, latestPrice, direction):
        self.type = 'ORDER'
        self.datetime = datetime
        self.tuple = tuple
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
        self.latestPrice = latestPrice

class FillEvent(Event):
    def __init__(self, timeindex, tuple, symbol, exchange, quantity, direction, fill_price, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.tuple = tuple
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_price = fill_price
        
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

    def calculate_ib_commission(self):
        """
        A simplified commission model based on Interactive Brokers fees.
        """
        full_cost = max(1.3, 0.013 * self.quantity)
        full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        return full_cost