import os
import pickle
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

# Importing custom modules
import indeed.scrap_job_blocks
import indeed.scrap_job_elements
import indeed.scrap_overall
import indeed.gmail_listener
import indeed.process_latest_emails
import indeed.gmail_auth


# Constants
SEARCH_SENDERS = ["malikhqtech@gmail.com", "alert@indeed.com", "noreply@example.com"]
ERROR_NOTIFICATION_EMAIL = "malikhqtech@gmail.com"



class GmailApp:
    def __init__(self, token_path=None, credentials_path=None):
        """
        Initialize the GmailApp with paths for authentication, logging, and default settings.

        :param token_path: Path to the token file for storing authentication tokens.
        :param credentials_path: Path to the credentials JSON file for OAuth authentication.
        """
        # Define the Gmail API scope to allow modifying messages (e.g., marking as read).
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

        # Define default paths relative to the project root if not provided.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        working_dir = os.path.abspath(os.path.join(script_dir, '..'))  # Move to the project root.
        os.chdir(working_dir)  # Set the working directory.
        logging.info(f"Working directory set to: {working_dir}")

        self.token_file = token_path or os.path.join(working_dir, '.secrets', 'token.pickle')
        self.credentials_file = credentials_path or os.path.join(working_dir, '.secrets', 'credentials.json')
        self.creds = None

        # Check if directories for secrets exist, but do not create them.
        if not os.path.exists(os.path.dirname(self.token_file)):
            raise FileNotFoundError(f"Secrets directory not found: {os.path.dirname(self.token_file)}")

        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")

        # Configure logging to file and console.
        log_file = os.path.join(working_dir, 'logs', f'gmail_app_{datetime.now().strftime("%Y%m%d")}.log')

        # Automatically create logs directory if it doesn't exist
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
            logging.info(f"Logs directory created at: {os.path.dirname(log_file)}")

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Add a console handler for logs so they show in the terminal too.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_handler)

    def authenticate(self):
        """
        Handle authentication and token refresh.

        :return: True if authentication is successful, False otherwise.
        """
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                logging.info("Loaded existing credentials")

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        logging.info("Refreshing expired credentials")
                        self.creds.refresh(Request())
                    except RefreshError:
                        logging.warning("Token refresh failed, initiating new OAuth flow")
                        self._new_authentication()
                else:
                    logging.info("No valid credentials found, starting new OAuth flow")
                    self._new_authentication()

                # Save the credentials for the next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                logging.info("Saved new credentials")

            return True

        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return False

    # def _new_authentication(self):
    #     """
    #     Perform OAuth authentication using a local server, compatible with Docker.
    #     """
    #     flow = InstalledAppFlow.from_client_secrets_file(
    #         self.credentials_file, self.SCOPES
    #     )

    #     # Ensure the local server binds to all network interfaces (0.0.0.0) in Docker
    #     self.creds = flow.run_local_server(port=8080, open_browser=False)
    #     logging.info("Completed OAuth authentication using local server")
    def _new_authentication(self):
        """
        Perform OAuth authentication using a manually specified redirect URI.
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.SCOPES
        )

        # Manually set the correct redirect URI
        redirect_uri = 'http://localhost:8080/'

        # Generate the authorization URL with the correct redirect URI
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        print(f"Please visit this URL to authorize the application: {auth_url}")

        # Start the local server for token exchange
        self.creds = flow.run_local_server(
            host='0.0.0.0',  # Bind to all interfaces for Docker
            port=8080,       # Ensure port matches the redirect URI port
            open_browser=False
        )
        logging.info("Completed OAuth authentication using local server")
        

    def process_emails(self):
        """
        Start the email fetch listener with specified filters and parameters.
        """
        try:
            # Initialize the Gmail API service
            service = build('gmail', 'v1', credentials=self.creds)

            # Start email fetch listener
            indeed.gmail_listener.start_email_fetch(
                service,
                SEARCH_SENDERS,
                ERROR_NOTIFICATION_EMAIL,
                interval=10  # Check every 10 seconds
            )
            logging.info("Started email fetch listener")

        except Exception as e:
            logging.error(f"Error in email listener: {str(e)}")
            raise


if __name__ == "__main__":
    # Initialize the GmailApp with paths for token and credentials.
    app = GmailApp()
    if app.authenticate():
        app.process_emails()  # Start email fetch listener
