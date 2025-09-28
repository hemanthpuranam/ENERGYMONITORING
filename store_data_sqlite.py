# store_data_sqlite.py

import pandas as pd
import sqlite3

# Load your actual dataset
df = pd.read_csv('energy_dataset.csv')

# Optional cleanup
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)

# Connect to SQLite DB
conn = sqlite3.connect('smart_energy.db')
cursor = conn.cursor()

# Drop old table if it exists
cursor.execute("DROP TABLE IF EXISTS energy_data")

# Store the dataset
df.to_sql('energy_data', conn, index=False)

conn.commit()
conn.close()

print("✅ Data saved to smart_energy.db in 'energy_data' table.")
