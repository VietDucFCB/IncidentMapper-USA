import pandas as pd
import sqlalchemy # Will be needed for PostgreSQL

# --- Configuration ---
INPUT_CSV_PATH = '/home/vietducspector/Desktop/IncidentMapper-USA/scripts/MapReduce/output/traffic_extracteds.csv'
CLEANED_CSV_PATH = '/home/vietducspector/Desktop/IncidentMapper-USA/scripts/MapReduce/output/traffic_extracteds_cleaned.csv' # For intermediate storage or inspection

# PostgreSQL connection details (adjust if necessary)
DB_USER = 'superset'
DB_PASSWORD = 'superset'
DB_HOST = 'localhost' # Assuming script runs on host and port 5432 is mapped from the 'db' container
DB_PORT = '5433' # Changed from 5432
DB_NAME = 'superset'
TABLE_NAME = 'traffic_incidents' # Placeholder: Please confirm or provide your desired table name

# --- Extract ---
def extract_data(file_path):
    """Extracts data from the given CSV file."""
    print(f"Extracting data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully read {len(df)} rows.")
        return df
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

# --- Transform ---
def transform_data(df):
    """Transforms data by removing duplicates."""
    if df is None:
        return None
    print("Transforming data (removing duplicates)...")
    original_row_count = len(df)
    df.drop_duplicates(inplace=True)
    cleaned_row_count = len(df)
    duplicates_removed = original_row_count - cleaned_row_count
    print(f"Removed {duplicates_removed} duplicate rows. Data now has {cleaned_row_count} rows.")
    return df

# --- Load ---
def load_data_to_postgres(df, table_name):
    """Loads the DataFrame into a PostgreSQL table."""
    if df is None:
        print("No data to load.")
        return

    print(f"Loading data into PostgreSQL table '{table_name}'...")
    # Connection string: postgresql://user:password@host:port/dbname
    engine_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = sqlalchemy.create_engine(engine_url)
        
        # This will replace the table if it exists. 
        # For production, you might want 'append' and handle schema creation/migration separately.
        # The schema will be inferred from the DataFrame. For explicit control, 
        # you would define SQL DDL to create the table first.
        print(f"Attempting to write {len(df)} rows to table {table_name} using 'replace' mode.")
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Successfully loaded data into table '{table_name}'.")
    except Exception as e:
        print(f"Error loading data to PostgreSQL: {e}")
        print("Please ensure:")
        print(f"1. PostgreSQL server is running and accessible at {DB_HOST}:{DB_PORT}.")
        print(f"2. The database '{DB_NAME}' exists and user '{DB_USER}' has permissions.")
        print(f"3. If running this script on the host, the PostgreSQL port (5432) from the 'db' Docker container is mapped to {DB_HOST}:{DB_PORT} in docker-compose-superset.yml.")
        print("   Example for 'db' service in docker-compose-superset.yml:")
        print("     ports:")
        print("     5433:5432")
        print("4. You have 'psycopg2-binary' and 'SQLAlchemy' installed in your Python environment (e.g., pip install psycopg2-binary SQLAlchemy pandas).")

# --- Main ETL Orchestration ---
def main():
    print("Starting ETL process...")

    # Extract
    data_df = extract_data(INPUT_CSV_PATH)
    if data_df is None:
        print("ETL process failed at extraction step.")
        return

    # Transform
    transformed_df = transform_data(data_df.copy()) # Use .copy() to avoid modifying the original df during ops
    if transformed_df is None:
        print("ETL process failed at transformation step.")
        return

    # Save cleaned data to a CSV (optional, for inspection or backup)
    try:
        transformed_df.to_csv(CLEANED_CSV_PATH, index=False)
        print(f"Intermediate cleaned data saved to {CLEANED_CSV_PATH}")
    except Exception as e:
        print(f"Error writing cleaned CSV file: {e}")
        # Decide if this is a critical failure or if loading can proceed

    # Load
    # The TABLE_NAME is currently set to 'traffic_incidents'. Please update if needed.
    load_data_to_postgres(transformed_df, TABLE_NAME)
    
    print("ETL process completed.")

if __name__ == '__main__':
    main()
