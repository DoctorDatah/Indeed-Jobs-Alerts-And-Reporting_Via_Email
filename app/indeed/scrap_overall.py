import os
import logging
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import indeed.scrap_job_blocks
import indeed.scrap_job_elements

# Configure logging
import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

# Set the global working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
working_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
os.chdir(working_dir)
logging.info(f"Working directory set to: {working_dir}")
raw_directory = './data/raw'


def scrap_process_email_content_to_csv(soup):
    """
    Process email content through scraping and data extraction.

    Args:
        soup (BeautifulSoup): Parsed email content as a BeautifulSoup object.
    """
    try:
        # Extract individual job blocks as a list of soups
        job_blocks = indeed.scrap_job_blocks.extract_individual_job_blocks(soup)

        # Scrape all individual job details into a DataFrame
        jobs_df = scrap_all_individual_jobs(job_blocks)

        # Append the DataFrame to a CSV file
        results_create_or_append_to_csv(jobs_df, reset_file=False)

        logging.info("Successfully processed email content for job data.")
    except Exception as e:
        logging.error(f"Failed to process email content: {e}", exc_info=True)
        raise

def scrap_all_individual_jobs(soup_list):
    """
    Takes a list of BeautifulSoup objects and extracts job details into a DataFrame.

    Args:
        soup_list (list): List of BeautifulSoup objects representing job blocks.

    Returns:
        pd.DataFrame: Unified DataFrame with job details.
    """
    all_jobs = []
    for soup in soup_list:
        try:
            job_data = indeed.scrap_job_elements.get_individual_job(soup)
            all_jobs.append(job_data)
        except Exception as e:
            logging.error(f"Error processing individual job block: {e}", exc_info=True)

    unified_dataframe = pd.concat(all_jobs, ignore_index=True) if all_jobs else pd.DataFrame()
    logging.info(f"Processed {len(all_jobs)} job blocks into a DataFrame.")
    return unified_dataframe

def results_create_or_append_to_csv(dataframe, reset_file=False):
    """
    Appends a DataFrame to a CSV file named with the current year and month.
    The file is stored in ./data/raw_processed. If the file does not exist, it is created.

    Args:
        dataframe (pd.DataFrame): The DataFrame to append to the CSV file.
        reset_file (bool): If True, resets the file and writes the DataFrame as a fresh file.
    """
    try:
        os.makedirs(raw_directory, exist_ok=True)

        current_year_month = datetime.now().strftime('%Y_%m')
        file_path = os.path.join(raw_directory, f'{current_year_month}.csv')

        if reset_file or not os.path.exists(file_path):
            dataframe.to_csv(file_path, mode='w', header=True, index=False)
            logging.info(f"Data written to {file_path} as a fresh file.")
        else:
            dataframe.to_csv(file_path, mode='a', header=False, index=False)
            logging.info(f"Data appended to {file_path}.")
    except Exception as e:
        logging.error(f"Error writing data to CSV: {e}", exc_info=True)

def sample(email_content):
    """
    Main function to handle the entire scraping process.

    Args:
        email_content (str): Raw email content to be processed.
    """
    try:
        soup = BeautifulSoup(email_content, 'html.parser')
        scrap_process_email_content_to_csv(soup)
    except Exception as e:
        logging.error(f"Error in main processing: {e}", exc_info=True)

# if __name__ == "__main__":
#     email_content = "<html>...email content...</html>"
#     sample(email_content)
