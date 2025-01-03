import os
from datetime import datetime
import threading
import time
from bs4 import BeautifulSoup
import logging

# Importing custom modules
import indeed.scrap_job_blocks
import indeed.scrap_job_elements
import indeed.scrap_overall
import indeed.gmail_listener
import indeed.process_latest_emails
import indeed.gmail_auth


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__)) # Move up two levels to the project root (from `app/utils` to the root)
working_dir = os.path.abspath(os.path.join(script_dir, '..')) # Change the working directory
os.chdir(working_dir)
logging.info(f"Working directory set to: {working_dir}")


# Constants
SEARCH_SENDERS = ["malikhqtech@gmail.com", "alert@indeed.com", "noreply@example.com"]
ERROR_NOTIFICATION_EMAIL = "malikhqtech@gmail.com"

if __name__ == "__main__":
    try:
        # Authenticate Gmail API
        service = indeed.gmail_auth.authenticate_gmail()
        print("Gmail API authenticated successfully!")

        # Start email fetch listener
        indeed.gmail_listener.start_email_fetch(
            service, 
            SEARCH_SENDERS, 
            ERROR_NOTIFICATION_EMAIL, 
            interval=10
        )
    except Exception as e:
        print("Error during initialization:", e)
