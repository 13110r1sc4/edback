import queue
from data import HistoricCSVDataHandler
from strategy import AdjPairTrade
from portfolio import Portfolio
from execution import SimulatedExecutionHandler
import datetime

def main():

    ########### GENERAL ###########
    events       = queue.Queue()
    symbol_tuple = ("AAPL", "MSFT", "GOOGL") # HAS TO BE TUPLE FOR DATA HANDLING
    csv_dir      = "/Users/leonardorisca/Desktop/AT/propBT/ClaudeAI_test/data/"

    ############# YF ##############
    intervals   = ["90m"]
    end_date    = datetime.datetime.now()
    start_date  = end_date - datetime.timedelta(days=2)

    ######### STRATEGY ############
    model_window = ["60"]
    ###############################
    
    bars = HistoricCSVDataHandler(events, csv_dir, symbol_tuple)
    for interval in intervals:
        bars.YFdownload2csv(start_date, end_date, interval)

    bars._open_convert_csv_files()
    strategy = AdjPairTrade(bars, events, model_window)
    port = Portfolio(bars, events, start_date, initial_capital=100000.0)
    broker = SimulatedExecutionHandler(events)

    while True:
        # Update the bars (specific backtest code, as opposed to live trading)
        if bars.continue_backtest:
            bars.update_bars()
        else:
            break

        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'MARKET':
                        strategy.calculate_signals(event)
                        port.update_timeindex(event)
                    elif event.type == 'SIGNAL':
                        port.update_signal(event)
                    elif event.type == 'ORDER':
                        broker.execute_order(event)
                    elif event.type == 'FILL':
                        port.update_fill(event)

    print(f"Final Portfolio Value: ${port.current_holdings['cash']:.2f}")
    print(f"Total Return: {(port.current_holdings['cash'] / port.initial_capital - 1) * 100:.2f}%")

if __name__ == "__main__":
    main()