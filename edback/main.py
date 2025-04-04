import queue
from data import HistoricCSVDataHandler
from strategy import NotAPairTrade
from portfolio import Portfolio
from execution import SimulatedExecutionHandler
import datetime
import matplotlib.pyplot as plt
from event import OrderEvent
import matplotlib.dates as mdates

def cleanUpPositions(symbol_tuple, bars, broker, port, events):
        '''check current pos -> close them with new order (if needed) -> fill order and update positions '''

        datetime = 'CLEANUP'
        order_type = 'MKT'

        if bars.multiasset:
            for t in symbol_tuple:
                latestBar = bars.get_latest_bars(t)[0]
                l = len(latestBar)
                print(l)
                for i, s in enumerate(t):
                    cp = port.current_positions[t][s]
                    latestPrice = latestBar[(l-1)//2+1+i]
                    
                    if cp < 0:
                        direction = 'BUY'
                    elif cp > 0:
                        direction = 'SELL'
                    else:
                        return
                    order_quantity = abs(cp)
                    order = OrderEvent(datetime, t, s, order_type, order_quantity, latestPrice, direction)
                    events.put(order)
        else:
            for i, s in enumerate(symbol_tuple):
                latestBar = bars.get_latest_bars(s)[0]
                cp = port.current_positions[s][s]
                latestPrice = latestBar[2+i]
                if cp < 0:
                    direction = 'BUY'
                elif cp > 0:
                    direction = 'SELL'
                else:
                    return
                order_quantity = abs(cp)
                order = OrderEvent(datetime, s, s, order_type, order_quantity, latestPrice, direction)
                events.put(order)

        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'ORDER':
                        broker.execute_order(event)
                    elif event.type == 'FILL':
                        port.update_fill(event)

def main():

    ########### GENERAL ###########
    events       = queue.Queue()
    symbol_tuple = (("BTC-USD", "ETH-USD"),) # HAS TO BE TUPLE FOR DATA HANDLING
    csv_dir      = "./data/"

    ############# YF ##############
    useYf = True
    intervals   = ["1d"]
    end_date    = datetime.datetime.now()
    start_date  = end_date - datetime.timedelta(days=50)

    ######### STRATEGY ############
    model_window = 25
    ###############################
    
    bars = HistoricCSVDataHandler(events, csv_dir, symbol_tuple, intervals[0])
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
            cleanUpPositions(symbol_tuple, bars, broker, port, events)
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

    df_h, df_p= port.get_portfolio_value_history()
    print(df_h.iloc[-1])

    plt.figure(figsize=(12, 6))
    plt.plot(df_h['datetime'].iloc[model_window:], df_h['total'].iloc[model_window:], label="Portfolio Value", color='blue')
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator()) 
    plt.xlabel("Time")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Portfolio Value Over Time")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    main()