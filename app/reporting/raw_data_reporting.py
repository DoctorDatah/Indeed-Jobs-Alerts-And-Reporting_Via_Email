import os
import logging
import pandas as pd
from datetime import datetime


def pre_processed_load_data(data_dir, top_n=3):
    """Load and combine data from the top N recent months."""
    files = [f for f in os.listdir(data_dir) if f.endswith('_pre_processed.csv')]
    file_details = [(f, f.split('_')[0], f.split('_')[1]) for f in files]
    file_details = sorted(file_details, key=lambda x: (x[1], x[2]), reverse=True)[:top_n]

    combined_data = []
    for file, year, month in file_details:
        df = pd.read_csv(os.path.join(data_dir, file))
        combined_data.append(df)

    if combined_data:
        data = pd.concat(combined_data)
        if 'days_posted' in data.columns:
            data = data.sort_values(by='days_posted')
        else:
            raise ValueError("Expected column 'days_posted' not found in the dataset.")
    else:
        data = pd.DataFrame()

    return data


def raw_processed_load_data(raw_processed_dir, top_n=3):
    """Load and combine data from the top N recent months in the raw processed directory."""
    files = [f for f in os.listdir(raw_processed_dir) if f.endswith('.csv')]
    file_details = [(f, f.split('_')[0], f.split('_')[1]) for f in files]
    file_details = sorted(file_details, key=lambda x: (x[1], x[2]), reverse=True)[:top_n]

    combined_data = []
    for file, year, month in file_details:
        df = pd.read_csv(os.path.join(raw_processed_dir, file))
        combined_data.append(df)

    if combined_data:
        data = pd.concat(combined_data)
        if 'days_posted' in data.columns:
            data = data.sort_values(by='days_posted')
        else:
            raise ValueError("Expected column 'days_posted' not found in the dataset.")
    else:
        data = pd.DataFrame()

    return data

