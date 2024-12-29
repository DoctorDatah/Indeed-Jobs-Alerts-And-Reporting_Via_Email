# Job Scraping and Reporting Project

## Motivation
Job hunting can be tedious and time-consuming, especially when companies post shadow jobs or when customizing job applications. Knowing the job posting history of a company can help determine whether it is worth investing time in the application process. This project aims to track companies of interest over the long term and provide alerts in a report for jobs that are fresh within 24 hours. Primarily, this project is designed to help myself by automating the process of scraping job postings from emails, extracting relevant job details, and presenting the data in a structured and user-friendly manner. This automation saves time and effort for job seekers and recruiters by eliminating the need to manually parse job emails and compile job data.

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
```
Indeed-Jobs-Alerts-And-Reporting_Via_Email/
├── .archive/
├── .secrets/
├── .venv_job_scrap/
├── app/
│   ├── indeed/
│   │   ├── scrap_job_blocks.py
│   │   ├── scrap_job_elements.py
│   │   ├── scrap_overall.py
│   │   ├── gmail_auth.py
│   │   ├── gmail_listener.py
│   ├── reporting/
│   │   ├── raw_data_reporting.py
│   ├── __init__.py
│   ├── dashboard.py
│   ├── main.py
│   ├── watchdog.py
├── data/
│   ├── emails/
│   ├── failed_emails/
├── logs/
├── requirements.txt
├── usecases/
```

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
- **[`dashboard.py`](app/dashboard.py)**: Creates and runs the Dash application for visualizing job data.
- **[`main.py`](app/main.py)**: Entry point for the application, handles initialization and starts the email fetching process.
- **[`watchdog.py`](app/watchdog.py)**: Monitors and restarts the main script if it crashes.

## Current Limitations
- **Gmail Authentication**: The project uses OAuth for Gmail authentication. Since a personal Gmail account is used, domain-level delegation is not possible. This means that a service account, which would allow for more seamless and automated authentication, cannot be utilized. Instead, the user must manually authenticate using OAuth, which can be less convenient and requires periodic re-authentication.
- **Docker Authentication**: Authenticating from Docker to an external browser has not been resolved. This limitation arises because the OAuth process typically involves opening a browser window for the user to log in and grant permissions. When running the application inside a Docker container, it is challenging to handle this browser-based authentication flow, which may cause issues when trying to authenticate Gmail from within Docker. As a result, running the application in a Docker container may not be fully supported at this time.

## Ports to be Available
- **Dashboard**: The Dash application runs on port `8050`.
- **Main Application**: The main application runs on port `8080`.

## Future Improvements
- **Multi-Source Support**: Extend the project to support multiple email sources and job posting formats.
- **Enhanced Visualization**: Add more visualization options and interactive features to the dashboard.
- **Machine Learning**: Implement machine learning models to categorize and rank job postings based on user preferences.
- **Notification System**: Add a notification system to alert users of new job postings.

## Requirements
- **Python Version**: This project uses Python version 3.13.1.
- **Libraries**:
  - `pandas`: For data manipulation and analysis.
  - `dash`: For creating the dashboard application.
  - `flask`: For serving the dashboard.
  - `google-auth`: For handling Gmail authentication.
  - `google-api-python-client`: For interacting with the Gmail API.
  - `watchdog`: For monitoring and restarting the main script.
  - `requests`: For making HTTP requests.
  - `beautifulsoup4`: For parsing HTML content.

## How to Use This Code

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/DoctorDatah/Indeed-Jobs-Alerts-And-Reporting_Via_Email
   cd Indeed-Jobs-Alerts-And-Reporting_Via_Email
   ```

2. **Set Up Google Cloud Platform (GCP)**:
   - Enable the Gmail API.
   - Create OAuth 2.0 credentials.
   - Download the credentials file and place it under `.secrets/credentials.json`.

3. **Install Python 3.13.1**:
   - Ensure Python 3.13.1 is installed on your system.

4. **Set Up Virtual Environment**:
   ```sh
   python -m venv .venv_job_scrap
   .\.venv_job_scrap\Scripts\activate
   ```

5. **Install Required Libraries**:
   ```sh
   pip install -r requirements.txt
   ```

6. **Update Alert Receiving Email**:
   - Open `app/main.py` and update the email address where you want to receive alerts.

7. **Run the Application**:
   - Execute the `watchdog.py` script to start the application.
   ```sh
   python app/watchdog.py
   ```

8. **Create Indeed Alerts**:
   - Go to indeed.com and create job alerts using the same email address you used for Gmail authentication.

9. **Launch the Dashboard**:
   - Run the `dashboard.py` script to launch the dashboard for visualizing job data.
   ```sh
   python app/dashboard.py
   ```

## Contact
For any questions or support, please contact Malik Hassan Qayyum via [LinkedIn](https://www.linkedin.com/in/malik-hassan-qayyum/).