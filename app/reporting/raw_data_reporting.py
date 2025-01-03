# This module is directly based of the interm data

import os
import logging
import pandas as pd
from datetime import datetime

def load_and_combine_data(files, data_dir):
    """Load and combine data from the given files."""
    combined_data = []
    for file in files:
        df = pd.read_csv(os.path.join(data_dir, file))
        combined_data.append(df)
    if combined_data:
        data = pd.concat(combined_data)
    else:
        data = pd.DataFrame()
    return data

def sort_data_by_days_posted(data):
    """Sort data by 'days_posted' column."""
    if 'days_posted' in data.columns:
        return data.sort_values(by='days_posted')
    else:
        raise ValueError("Expected column 'days_posted' not found in the dataset.")

def intermediate_load_data(data_dir, top_n=3):
    """Load and combine data from the top N recent months."""
    files = [f for f in os.listdir(data_dir) if f.endswith('intermediate.csv')]
    file_details = [(f, f.split('_')[0], f.split('_')[1]) for f in files]
    if top_n is not None:
        file_details = sorted(file_details, key=lambda x: (x[1], x[2]), reverse=True)[:top_n]
    else:
        file_details = sorted(file_details, key=lambda x: (x[1], x[2]), reverse=True)
    files = [f[0] for f in file_details]
    data = load_and_combine_data(files, data_dir)
    return sort_data_by_days_posted(data)

def raw_load_data(raw_processed_dir, top_n=3):
    """Load and combine data from the top N recent months in the raw processed directory."""
    files = [f for f in os.listdir(raw_processed_dir) if f.endswith('.csv')]
    file_details = [(f, f.split('_')[0], f.split('_')[1]) for f in files]
    if top_n is not None:
        file_details = sorted(file_details, key=lambda x: (x[1], x[2]), reverse=True)[:top_n]
    else:
        file_details = sorted(file_details, key=lambda x: (x[1], x[2]), reverse=True)
    files = [f[0] for f in file_details]
    data = load_and_combine_data(files, raw_processed_dir)
    return sort_data_by_days_posted(data)

