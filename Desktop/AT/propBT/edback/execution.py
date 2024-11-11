from abc import ABCMeta, abstractmethod
from event import FillEvent

class ExecutionHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError("Should implement execute_order()")

class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self, events):
        self.events = events

    def execute_order(self, event):
        if event.type == 'ORDER':

            fill_price = event.price
            quantity = event.quantity

            # Create a FillEvent to signal that an order has been filled
            fill_event = FillEvent(
                timeindex=event.timeindex,
                symbol=event.symbol,
                quantity=quantity,
                fill_price=fill_price,
                commission=self.calculate_commission(quantity, fill_price)  # You might want to include commissions
            )

            # Put the fill event in the events queue for further processing
            self.events.put(fill_event)

    def calculate_commission(self, quantity, fill_price):
        # Example commission calculation (modify as needed)
        commission_rate = 0.0005  # 0.05% commission
        return quantity * fill_price * commission_rate
