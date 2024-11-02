import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
import hashlib
import tkinter as tk
from tkinter import filedialog

# Database connection details
DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
USER = 'chrism'
PASSWORD = '!Cncamrts1'
HOST = '192.168.128.30'
PORT = '5432'
DATABASE = 'Production_data'
SCHEMA = 'production'
TABLE_NAME = 'bin_inventory'

# Create database engine
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# Create the orders table if it does not exist
with engine.connect() as connection:
    connection.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.{TABLE_NAME} (
            company VARCHAR,
            warehouse VARCHAR,
            receive_date VARCHAR,
            commodity_id VARCHAR,
            variety_id VARCHAR,
            style_id VARCHAR,
            size_id VARCHAR,
            grade_id VARCHAR,
            region_id VARCHAR,
            method_id VARCHAR,
            storage_id VARCHAR,
            color_id VARCHAR,
            on_hand_quantity VARCHAR,
            tag_id VARCHAR PRIMARY KEY,
            room_row_id VARCHAR,
            import_id INTEGER)
    """))

# Open a file picker dialog to select the file
root = tk.Tk()
root.withdraw()  # Hide the root window
file_path = filedialog.askopenfilename(title="Select Report File", filetypes=[("CSV files", "*.csv")])

if not file_path:
    print("No file selected. Exiting program.")
else:
    # Load the report file
    df = pd.read_csv(file_path)
    now = datetime.now()
    # Transform headers to lowercase and replace spaces with underscores
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.columns = df.columns.str.lower().str.replace('/', '_')


    # Get today's date to track imports only within the day
    today_date = date.today()
    today_date_str = today_date.strftime('%Y-%m-%d')

    # Retrieve the latest import_id and increment it by 1
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT COALESCE(MAX(import_id), 0) FROM {SCHEMA}.{TABLE_NAME}"))
        latest_import_id = result.scalar()  # Get the maximum import ID from the table
        new_import_id = latest_import_id + 1

    df['import_id'] = new_import_id  # Assign the new import_id to all rows

    # Insert the new data with the new import_id
    try:
        with engine.begin() as connection:
            df.to_sql(TABLE_NAME, connection, schema=SCHEMA, if_exists='replace', index=False)
            print("Data uploaded successfully with import tracking.")
    except IntegrityError as e:
        print("Error uploading data:", e)
