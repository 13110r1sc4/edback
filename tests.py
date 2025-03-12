import pandas as pd
import os

comb_index = None
symbol_tuple = (("BTC-USD", "ETH-USD"),)
csv_dir = "/Users/leonardorisca/Desktop/AT/propBT/data/"
intervals   = "90m"

# new_data = pd.read_csv(os.path.join(csv_dir, f'{intervals}/BTC-USD.csv'),
#                                             header=0, index_col=0, parse_dates=True, names=['datetime', 'BTC-USD_close'])
# comb_index = new_data.index
symbol_data = {}

for s in symbol_tuple:
    
    # symbol_data[s] = pd.DataFrame()
    for i,a in enumerate(s):
        print(a)
        # global new_data

        new_data = pd.read_csv(os.path.join(csv_dir, f'{intervals}/{a}.csv'),
                                            header=0, index_col=0, parse_dates=True, names=['datetime', f'{a}_close'] # OK
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
        #     print(f"Type of self.symbol_data[s].index: {type(symbol_data[s].index)}, dtype: {symbol_data[s].index.dtype}")
            
            
        #     symbol_data[s] = pd.concat([symbol_data[s], new_data])
        #     symbol_data[s] = symbol_data[s].reindex(index=comb_index, method='pad')
        #     # ------------------------------
        #     symbol_data[s][f"{a}_returns"] = symbol_data[s][f"{a}_close"].pct_change().dropna()

# tuple = "BTC-USD"
# symbol_data = pd.DataFrame()
# new_data = pd.read_csv(os.path.join(csv_dir, f'{intervals}/{tuple}.csv'),
#                                             header=0, index_col=0, parse_dates=True, names=['datetime', f'{tuple}_close'])
# comb_index = new_data.index