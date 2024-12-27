import os
import pandas as pd
from pathlib import Path

# Define global variables
RAW_DATA_DIR = "./data/raw_processed/"
PREPROCESSED_DATA_DIR = "./data/pre_processed/"

def raw_csv_to_pre_processed_data():
    """
    Processes the latest CSV file from the raw data directory by removing duplicates and saving the result.

    Returns:
        None
    """
    # Ensure the preprocessed directory exists
    Path(PREPROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)

    # Get the latest CSV file from the raw data directory
    csv_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the specified raw data directory.")

    latest_csv = max(csv_files, key=lambda x: x.split('.')[0])

    # Load the latest CSV file into a DataFrame
    file_path = os.path.join(RAW_DATA_DIR, latest_csv)
    data = pd.read_csv(file_path)

    # Remove duplicates based on specific columns
    columns_to_check = ['title', 'link', 'company', 'days_posted']
    data_deduplicated = data.drop_duplicates(subset=columns_to_check, keep='first')

    # Save the deduplicated DataFrame to the preprocessed directory
    output_file = os.path.join(PREPROCESSED_DATA_DIR, latest_csv.replace('.csv', '_pre_processed.csv'))
    data_deduplicated.to_csv(output_file, index=False)

# Example usage
# raw_csv_to_pre_processed_data()
