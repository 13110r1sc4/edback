# TO BE CHANGED, JUST A SAMPLE FROM GPT

import pandas as pd
import sqlite3

def upload_csv_to_db(csv_path, table_name, db_path="data/market_data.db"):
    # Load the CSV
    df = pd.read_csv(csv_path)

    # Open (or create) database
    conn = sqlite3.connect(db_path)

    # Upload to table
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()
    print(f"Uploaded {csv_path} to table '{table_name}' in {db_path}")

# Example usage
if __name__ == "__main__":
    upload_csv_to_db("data/btc_usdt.csv", "btc_usdt")


# or



from pathlib import Path
import pandas as pd
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

def upload_csv_to_db(csv_name, table_name):
    csv_path = DATA_DIR / csv_name
    db_path = DATA_DIR / "market_data.db"

    # Read CSV and upload to SQLite
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Uploaded {csv_name} to table '{table_name}' in {db_path.name}")

# Example usage
if __name__ == "__main__":
    upload_csv_to_db("btc_usdt.csv", "btc_usdt")
