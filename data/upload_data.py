import os
import pandas as pd
import sqlite3
import sys

# 1. Take folder input from the command line where all new CSV files to be added to the db are stored
# 2. Loop through all the files and add them to the SQL db
# 3. Delete the CSV files after adding them

db_path = "../data/market_data.db"
directory_path = sys.argv[1]

# Check if the directory exists
if not os.path.isdir(directory_path):
    print(f"❌ Error: Directory '{directory_path}' does not exist.")
    sys.exit(1)

# Check if the database path exists
if not os.path.isfile(db_path):
    print(f"❌ Error: Database file '{db_path}' does not exist.")
    sys.exit(1)

for csv_file in os.listdir(directory_path):
    csv_path = os.path.join(directory_path, csv_file)

    # ----------------------------- chatgpt
    if csv_file.endswith(".csv"):
        try:
            # Load CSV to DataFrame
            df = pd.read_csv(csv_path)
            
            # Connect to the SQLite DB
            conn = sqlite3.connect(db_path)
            
            # Use the CSV file name (without extension) as the table name
            table_name = os.path.splitext(csv_file)[0]
            
            # Upload the DataFrame to the DB
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ Uploaded {csv_file} to table '{table_name}' in the database.")
            
            # Commit the transaction and close the connection
            conn.commit()
            conn.close()
            
            # Delete the CSV file after uploading
            os.remove(csv_path)
            print(f"🗑️ Deleted {csv_file} after upload.")
        
        except Exception as e:
            print(f"❌ Error processing file '{csv_file}': {e}")
    else:
        print(f"⚠️ Skipping non-CSV file: {csv_file}")
    # -----------------------------