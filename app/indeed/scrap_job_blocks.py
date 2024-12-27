from bs4 import BeautifulSoup  # For parsing HTML
import os
import datetime
import logging

# Configure logging
import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

def extract_individual_job_blocks(soup):
    """
    Extract job postings by finding the nearest ancestor <tbody> or <table>
    for labels like 'days ago' or 'just posted'.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
    Returns:
        list: List of filtered <tbody> or <table> elements containing job postings.
    """
    job_postings = []
    seen_ancestors = set()
    job_labels = ["days ago", "just posted", "day ago"]

    matching_strings = soup.find_all(
        string=lambda text: text and any(label in text.lower() for label in job_labels)
    )

    for match in matching_strings:
        ancestor = match.find_parent(['tbody', 'table'])
        if ancestor and id(ancestor) not in seen_ancestors:
            job_postings.append(ancestor)
            seen_ancestors.add(id(ancestor))

    logging.info(f"Extracted {len(job_postings)} job postings.")
    return job_postings

def save_flagged_html(soup):
    """
    Save the flagged HTML content to a log file with proper UTF-8 encoding.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
    """
    try:
        log_dir = "./log/flagged_html_files"
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        file_name = f"flagged_{timestamp}.html"
        file_path = os.path.join(log_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

        logging.info(f"No job postings found. HTML content saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save flagged HTML content: {e}", exc_info=True)

def sample():
    """
    Main function to parse HTML and extract job postings.
    """
    try:
        html_content = """<html><body><table><tr><td>3 days ago</td></tr></table></body></html>"""
        soup = BeautifulSoup(html_content, 'html.parser')

        job_postings = extract_individual_job_blocks(soup)

        if job_postings:
            logging.info(f"Found {len(job_postings)} job postings.")
            for idx, posting in enumerate(job_postings, start=1):
                logging.info(f"Job Posting {idx}:\n{posting.prettify()}")
        else:
            logging.warning("No job postings found.")
            save_flagged_html(soup)
    except Exception as e:
        logging.error(f"An error occurred in the sample function: {e}", exc_info=True)

# if __name__ == "__main__":
#     sample()
