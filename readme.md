# Job Scraping and Reporting Project

## Motivation
The primary motivation for this project is to automate the process of scraping job postings from emails, extracting relevant job details, and presenting the data in a structured and user-friendly manner. This project aims to save time and effort for job seekers and recruiters by automating the tedious task of manually parsing job emails and compiling job data.

## What This Project Does
This project automates the process of:
1. Fetching job-related emails from a specified Gmail account.
2. Parsing the email content to extract job postings.
3. Storing the extracted job data in CSV files.
4. Providing a dashboard for visualizing and reporting the job data.

## Value Proposition
- **Efficiency**: Automates the extraction and processing of job postings from emails, saving time and effort.
- **Accuracy**: Ensures consistent and accurate extraction of job details.
- **Visualization**: Provides a dashboard for easy visualization and reporting of job data.
- **Scalability**: Can be extended to support multiple email sources and job posting formats.

## Project Structure
The project is structured as follows:
. ├── .archieve/ ├── .secrets/ ├── .venv_job_scrap/ ├── app/ │ ├── indeed/ │ ├── reporting/ │ ├── init.py │ ├── dashboard.py │ ├── main.py │ ├── watchdog.py ├── data/ │ ├── emails/ │ ├── failed_emails/ ├── logs/ ├── requirements.txt ├── usecases/


### Watchdog Module and Main
- **Watchdog Module**: The [`app/watchdog.py`](app/watchdog.py) script monitors and restarts the main script if it crashes. It ensures the continuous operation of the email fetching and processing system.
- **Main Script**: The [`app/main.py`](app/main.py) script is the entry point of the application. It handles the authentication with Gmail, starts the email fetching process, and initiates the job data extraction and storage.

### Dashboard for Reporting
- **Dashboard**: The [`app/dashboard.py`](app/dashboard.py) script creates a Dash application that provides a user interface for visualizing and reporting the job data. It includes features like horizontal menus, refresh buttons, and tabs for different data views.

## Module Explanations
### [`indeed`](app/indeed/__init__.py) Module
- **[`scrap_job_blocks.py`](app/indeed/scrap_job_blocks.py)**: Contains functions for extracting individual job blocks from the email content.
- **[`scrap_job_elements.py`](app/indeed/scrap_job_elements.py)**: Contains functions for extracting specific job details from the job blocks.
- **[`scrap_overall.py`](app/indeed/scrap_overall.py)**: Orchestrates the overall scraping process, including parsing emails and saving job data to CSV files.
- **[`gmail_auth.py`](app/indeed/gmail_auth.py)**: Handles Gmail authentication and token management.
- **[`gmail_listener.py`](app/indeed/gmail_listener.py)**: Listens for new emails and triggers the scraping process.

### [`reporting`](app/dashboard.py) Module
- **[`raw_data_reporting.py`](app/reporting/raw_data_reporting.py)**: Contains functions for generating reports from the raw job data.

### [`app`](app) Module
- **`dashboard.py`**: Creates and runs the Dash application for visualizing job data.
- **[`main.py`](app/dashboard.py)**: Entry point for the application, handles initialization and starts the email fetching process.
- **`watchdog.py`**: Monitors and restarts the main script if it crashes.

## Future Improvements
- **Multi-Source Support**: Extend the project to support multiple email sources and job posting formats.
- **Enhanced Visualization**: Add more visualization options and interactive features to the dashboard.
- **Machine Learning**: Implement machine learning models to categorize and rank job postings based on user preferences.
- **Notification System**: Add a notification system to alert users of new job postings.

## Contact
For any questions or support, please contact Malik Hassan Qayyum at malikhqtech@gmail.com.