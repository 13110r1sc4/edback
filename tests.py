import pandas as pd
import os

comb_index = None
symbol_tuple = (("BTC-USD", "ETH-USD"),)
csv_dir = "/Users/leonardorisca/Desktop/AT/propBT/data/"
intervals   = "90m"

# new_data = pd.read_csv(os.path.join(csv_dir, f'{intervals}/BTC-USD.csv'),
#                                             header=0, index_col=0, parse_dates=True, names=['datetime', 'BTC-USD_close'])
# comb_index = new_data.index


for s in symbol_tuple:
    
    # symbol_data[s] = pd.DataFrame()
    for i,a in enumerate(s):
        print(a)
        # global new_data

        new_data = pd.read_csv(os.path.join(csv_dir, f'{intervals}/{a}.csv'),
                                            index_col='datetime', parse_dates=True, names=['datetime', f'{a}_close'] # OK
        )
        # print(new_data)
        # new_data.head()
        new_data.sort_index(inplace=True)
        if comb_index is None:
            comb_index = new_data.index
            
        else:
            comb_index = comb_index.union(new_data.index)
        #  latest_symbol_data[s] = []

        if i == 0:
            symbol_data[s] = new_data
            symbol_data[s][f"{a}_returns"] = symbol_data[s][f"{a}_close"].pct_change().fillna(0)
        print(symbol_data)
        print(symbol_data[s].columns)
        # else:
        #     print(f"Type of comb_index: {type(comb_index)}, dtype: {comb_index.dtype}")
        #     print(f"Type of symbol_data[s].index: {type(symbol_data[s].index)}, dtype: {symbol_data[s].index.dtype}")
            
            
        #     symbol_data[s] = pd.concat([symbol_data[s], new_data])
        #     symbol_data[s] = symbol_data[s].reindex(index=comb_index, method='pad')
        #     # ------------------------------
        #     symbol_data[s][f"{a}_returns"] = symbol_data[s][f"{a}_close"].pct_change().dropna()

# tuple = "BTC-USD"
# symbol_data = pd.DataFrame()
# new_data = pd.read_csv(os.path.join(csv_dir, f'{intervals}/{tuple}.csv'),
#                                             header=0, index_col=0, parse_dates=True, names=['datetime', f'{tuple}_close'])
# comb_index = new_data.index

import pandas as pd
import os

symbol_tuple = (("BTC-USD", "ETH-USD"),)
csv_dir = "/Users/leonardorisca/Desktop/AT/propBT/data/"
interval   = "90m"

symbol_data = {}
for s in symbol_tuple:
                
            dfs = []
            for tkr in s:
                try:
                    new_data = pd.read_csv(os.path.join(csv_dir, f'{interval}/{tkr}.csv'),
                                                            index_col='datetime', parse_dates=True, names=['datetime', f'{tkr}_close'])
                    new_data.sort_index(inplace=True)
                    
                    if not pd.api.types.is_numeric_dtype(new_data[f'{tkr}_close']):
                        new_data[f'{tkr}_close'] = pd.to_numeric(new_data[f'{tkr}_close'], errors='coerce')

                    new_data.interpolate(method="linear", inplace=True)

                    new_data[f"{tkr}_returns"] = new_data[f"{tkr}_close"].pct_change().fillna(0)
                    dfs.append(new_data)

                except FileNotFoundError:
                    print(f"File {tkr}.csv not found.")

                symbol_data[s] = pd.concat(dfs, axis=1, join="outer")

                if symbol_data[s].iloc[0].isna().any():
                    symbol_data[s].iloc[0] = symbol_data[s].iloc[0].ffill()
                symbol_data[s].interpolate(method="linear", inplace=True)
                symbol_data[s] = symbol_data[s].iterrows()


import pandas as pd
import os
latest = {('BTC-USD', 'ETH-USD'): [('Dates', 'BTC-USD', 'ETH-USD', 92944.046875, 2458.85791015625), ('Dates', 'BTC-USD', 'ETH-USD', 93272.4140625, 2445.773193359375)]}
symbol = (('BTC-USD', 'ETH-USD'),)
def get_latest_bars(symbol, N=1):
        try:
            bars_list = latest[symbol]
        except KeyError:
            print(f"That symbol {symbol} is not available in the historical data set.")
            return None
        else:
            if len(bars_list) == N:
                return bars_list[-N:]

print(get_latest_bars(symbol[0]))
