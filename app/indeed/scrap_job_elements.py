import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging
import csv  
import re

# Configure logging
import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

def get_individual_job(soup):
    """
    Extract job details from the given BeautifulSoup object, handling potential HTML structure variations.
    Supports both Data_2 and single data column structures, with special handling for company names containing periods.

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

    # Save DataFrame for validation
    temp_title_for_save = tr_df[tr_df['Number'] == 1]['Data 1'].iloc[0]
    filename = f"{temp_title_for_save}.csv" 
    tr_df.to_csv(
        filename,
        index=False,
        quoting=csv.QUOTE_ALL,
        quotechar='"',
        escapechar='\\',
        lineterminator='\n',
        sep=',',
        encoding='utf-8',
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

    # Check if Data_2 exists in the DataFrame
    has_data_2 = 'Data 2' in tr_df.columns
    print(f"Data_2 column exists: {has_data_2}")
    
    if has_data_2: 
        # Original logic for Data_2 structure
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
    else:
          # New logic for structure without Data_2
        for _, row in tr_df.iterrows():
            number = row['Number']

            if number == 1:
                job_data['title'] = row.get('Data 1', None)
                job_data['link'] = row.get('Link', None)
            elif number == 2:
                # Parse company info with enhanced handling of company names with periods and non-breaking spaces
                company_info = row.get('Data 1', '')
                if '-' in company_info:
                    left_side, location = company_info.split('-', 1)
                    job_data['location'] = location.strip() # Remove leading/trailing spaces
                    
                    
                    # Prepare for the next step to extract company name and rating
                    left_side = left_side.replace('\xa0', ' ') # (Important) # Replace non-breaking spaces with regular spaces 
                    left_side = left_side.strip() # Remove leading/trailing spaces 
                    last_space_index = left_side.rfind(' ') # Find the last space (either regular or non-breaking)
                    potential_comany_name_and_rating = left_side


                    if last_space_index != -1:  # has some index meaning some space is found 
                        pattern = r"^\d+(\.\d{1,2})?$"  # is a number X, X.XX or X.X
                        possible_rating = potential_comany_name_and_rating[last_space_index+1:].strip() # Get the rating part and remove leading/trailing spaces
                        if bool(re.match(pattern, possible_rating)):
                            job_data['rating'] = possible_rating
                            job_data['company'] = potential_comany_name_and_rating[:last_space_index].strip() 
                        else: 
                            job_data['company'] = potential_comany_name_and_rating.strip()

                    else:  # no space found 
                        job_data['company'] = potential_comany_name_and_rating.strip() 
                        

                else:
                    job_data['company'] = company_info.strip()
                    
            elif number == 3:
                job_data['type'] = row.get('Data 1', None)
            elif number == len(tr_df):
                job_data['days_posted'] = row.get('Data 1', None)
            elif number == len(tr_df) - 1:
                job_data['description'] = row.get('Data 1', None)

    # Process posting date
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