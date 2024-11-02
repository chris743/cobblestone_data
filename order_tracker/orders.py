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
TABLE_NAME = 'orders'

# Create database engine
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# Create the orders table if it does not exist
with engine.connect() as connection:
    connection.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.{TABLE_NAME} (
            warehouse_location VARCHAR,
            customer VARCHAR,
            ship_to_location VARCHAR,
            sales_order_number VARCHAR,
            salesperson VARCHAR,
            customer_po_number VARCHAR,
            commodity_id VARCHAR,
            style_id VARCHAR,
            size_id VARCHAR,
            grade_id VARCHAR,
            label_id VARCHAR,
            region_id VARCHAR,
            method_id VARCHAR,
            storage_id VARCHAR,
            color_id VARCHAR,
            order_quantity INTEGER,
            sales_order_date DATE,
            ship_date DATE,
            order_julian VARCHAR,
            line_id VARCHAR PRIMARY KEY,
            uploaded_at TIMESTAMP,
            import_id INTEGER,
            flag VARCHAR
        )
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

    # Generate a unique line ID by hashing key fields
    def generate_line_id(row):
        unique_str = f"{row['sales_order_number']}_{row['commodity_id']}_{row['style_id']}_{row['order_quantity']}_{row['size_id']}_{row['grade_id']}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    df['line_id'] = df.apply(generate_line_id, axis=1)
    df['uploaded_at'] = now

    # Get today's date to track imports only within the day
    today_date = date.today()
    today_date_str = today_date.strftime('%Y-%m-%d')

    # Retrieve the latest import_id and increment it by 1
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT COALESCE(MAX(import_id), 0) FROM {SCHEMA}.{TABLE_NAME}"))
        latest_import_id = result.scalar()  # Get the maximum import ID from the table
        new_import_id = latest_import_id + 1

    df['import_id'] = new_import_id  # Assign the new import_id to all rows

    # Retrieve all existing line IDs from today's imports in the database
    existing_today_df = pd.read_sql(
        f"""
        SELECT sales_order_number, line_id FROM {SCHEMA}.{TABLE_NAME}
        WHERE uploaded_at::date = '{today_date_str}'
        """, 
        engine
    )

    # Identify rows in previous imports from today that are missing in the new import
    reassigned_lines = existing_today_df[~existing_today_df['line_id'].isin(df['line_id'])].copy()  # add .copy() here
    if not reassigned_lines.empty:
        reassigned_lines.loc[:, 'flag'] = 'assigned_day_of'

        # Update the flag for reassigned rows in the database
        with engine.begin() as connection:
            for _, row in reassigned_lines.iterrows():
                connection.execute(
                    text(f"""
                        UPDATE {SCHEMA}.{TABLE_NAME}
                        SET flag = :flag
                        WHERE line_id = :line_id AND DATE(uploaded_at) = :today_date
                    """),
                    {'flag': 'assigned_day_of', 'line_id': row['line_id'], 'today_date': today_date}
                )

    # Set the "flag" for current import rows
    df['flag'] = df.apply(
        lambda row: 'day_of_order' if row['sales_order_date'] == row['ship_date'] else '',
        axis=1
    )

    # Retrieve existing line_ids from the database
    with engine.connect() as connection:
        existing_line_ids_df = pd.read_sql(f"SELECT line_id FROM {SCHEMA}.{TABLE_NAME}", connection)
    existing_line_ids = existing_line_ids_df['line_id'].tolist()

    # Filter df to exclude rows where line_id already exists in the database
    new_rows_df = df[~df['line_id'].isin(existing_line_ids)]

    # Export the filtered DataFrame (only new rows) to a CSV file
    filepath = 'new_rows_output.csv'
    new_rows_df.to_csv(filepath, index=False)
    print(f"New rows exported to {filepath}")

    # Insert the new data with the new import_id
    try:
        with engine.begin() as connection:
            new_rows_df.to_sql(TABLE_NAME, connection, schema=SCHEMA, if_exists='append', index=False)
        print("Data uploaded successfully with import tracking.")
    except IntegrityError as e:
        print("Error uploading data:", e)
