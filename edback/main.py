import queue
from data import HistoricCSVDataHandler
from strategy import NotAPairTrade
from portfolio import Portfolio
from execution import SimulatedExecutionHandler
import datetime
import matplotlib.pyplot as plt
import pandas as pd

def main():

    ########### GENERAL ###########
    events       = queue.Queue()
    symbol_tuple = (("BTC-USD", "ETH-USD"),) # HAS TO BE TUPLE FOR DATA HANDLING
    csv_dir      = "/Users/leonardorisca/Desktop/AT/propBT/data/"

    ############# YF ##############
    useYf = True
    intervals   = ["1d"]
    end_date    = datetime.datetime.now()
    start_date  = end_date - datetime.timedelta(days=50)

    ######### STRATEGY ############
    model_window = 30
    ###############################
    
    bars = HistoricCSVDataHandler(events, csv_dir, symbol_tuple)
    if useYf == True:
        for interval in intervals:
            bars.YFdownload2csv(start_date, end_date, interval)

    bars._open_convert_csv_files()
    strategy = NotAPairTrade(bars, events, model_window)
    port = Portfolio(bars, events, start_date, initial_capital=100000.0)
    broker = SimulatedExecutionHandler(events)

    while True:
        # Update the bars (specific backtest code, as opposed to live trading)
        if bars.continue_backtest:
            bars.update_bars()
        else:
            # CLEAN UP POSITIONS
            port.cleanUpPositions()
            break

        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'MARKET':
                        # print('MARKET')
                        strategy.calculate_signals(event)
                        port.update_timeindex(event)
                    elif event.type == 'SIGNAL':
                        # print('SIGNAL')
                        port.update_signal(event)
                    elif event.type == 'ORDER':
                        broker.execute_order(event)
                    elif event.type == 'FILL':
                        port.update_fill(event)

    print(f"Final Portfolio Value: ${port.current_holdings['cash']:.2f}")
    print(f"Total Return: {(port.current_holdings['cash'] / port.initial_capital - 1) * 100:.2f}%")

    df = port.get_portfolio_value_history()
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

    print(df.tail())

    # plt.figure(figsize=(10, 5))
    # plt.plot(df['datetime'], df['total'], label="Portfolio Value", color='blue')
    # plt.xlabel("Time")
    # plt.ylabel("Portfolio Value ($)")
    # plt.title("Portfolio Value Over Time")
    # plt.legend()
    # plt.grid()
    # plt.xticks(rotation=45)
    # plt.show()

if __name__ == "__main__":
    main()