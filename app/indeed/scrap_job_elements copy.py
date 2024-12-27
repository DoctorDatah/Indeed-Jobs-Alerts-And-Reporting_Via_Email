import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import csv  

# Configure logging
import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

def get_individual_job(soup):
    """
    Extract job details from the given BeautifulSoup object, handling potential HTML structure variations.

    Args:
        soup (BeautifulSoup): Parsed BeautifulSoup object of the page.

    Returns:
        pd.DataFrame: A DataFrame containing job details.
    """
    rows = soup.find_all('tr')
    logging.info(f"Found {len(rows)} <tr> elements.")

    data = []
    for idx, row in enumerate(rows, start=1):
        columns = [td.text.strip() for td in row.find_all('td')]
        link = row.find('a', href=True)
        row_data = {
            "Number": idx,
            "TR HTML": str(row),
            "Link": link['href'] if link else None,
        }
        for i, col in enumerate(columns, start=1):
            row_data[f"Data {i}"] = col
        data.append(row_data)

    tr_df = pd.DataFrame(data)
    logging.info("Job details extracted Raw Dataframe based on tr.")
    logging.info(f"Job DataFrame:\n{tr_df}")

    # validation_tr_df
    # Save DataFrame with robust handling for special characters
    tr_df.to_csv(
        'validation_tr_df.csv',          # File name
        index=False,           # Exclude index
        quoting=csv.QUOTE_ALL, # Enclose all fields in quotes
        quotechar='"',         # Use double quotes for quoting
        escapechar='\\',       # Escape special characters if needed
        lineterminator='\n',  # Ensure consistent line endings (default is fine for most cases)
        sep=',',               # Comma-separated values
        encoding='utf-8',      # Use UTF-8 to handle international characters
    )



    job_data = {
        "title": None,
        "link": None,
        "company": None,
        "rating": None,
        "location": None,
        "type": None,
        "description": None,
        "days_posted": None,
        "days": None
    }


    # This logic is we have Data_1, Data_2, ...... Data_n columns in the tr_df
    for _, row in tr_df.iterrows():
        number = row['Number']

        if number == 1:
            job_data['title'] = row.get('Data 1', None)
            job_data['link'] = row.get('Link', None)
        elif number == 3:
            job_data['company'] = row.get('Data 1', None)
            job_data['rating'] = row.get('Data 2', None)
        elif number == 4:
            location_text = row.get('Data 1', None)
            if location_text and '•' in location_text:
                location_parts = location_text.split('•')
                job_data['location'] = location_parts[0].strip()
                job_data['type'] = location_parts[1].strip()
            else:
                job_data['location'] = location_text
                job_data['type'] = None
        elif number == len(tr_df):
            job_data['days_posted'] = row.get('Data 1', None)
        elif number == len(tr_df) - 1:
            job_data['description'] = row.get('Data 1', None)

    current_date = datetime.now()
    days_posted_text = job_data['days_posted']

    if days_posted_text:
        if "day" in days_posted_text.lower():
            days_ago = int(''.join(filter(str.isdigit, days_posted_text))) if any(c.isdigit() for c in days_posted_text) else 1
            posting_date = current_date - timedelta(days=days_ago)
            job_data['days'] = days_ago
        elif "just posted" in days_posted_text.lower():
            posting_date = current_date
            job_data['days'] = 0
        else:
            posting_date = current_date
            job_data['days'] = None
    else:
        posting_date = None
        job_data['days'] = None

    job_data['posting_date'] = posting_date.strftime('%Y-%m-%d') if posting_date else None
    job_data['fetched_date'] = current_date.strftime('%Y-%m-%d')

    job_df = pd.DataFrame([job_data])

    logging.info("Job details extracted successfully.")
    logging.info(f"Job DataFrame:\n{job_df}")

    return job_df
