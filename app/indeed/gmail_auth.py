import os
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
working_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
os.chdir(working_dir)
logger.info(f"Working directory set to: {working_dir}")

# Paths for secrets
TOKEN_PATH = os.path.join(working_dir, '.secrets', 'token.json')
CREDENTIALS_PATH = os.path.join(working_dir, '.secrets', 'credentials.json')


def ensure_secrets_directory():
    """Ensure the _secrets directory exists."""
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)


def load_credentials():
    """Load existing credentials from the token file."""
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'r') as token:
                creds_data = json.load(token)
                creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
                logger.info("Loaded credentials from token.json.")
                return creds
        except Exception as e:
            logger.warning(f"Error loading token file: {e}. Removing corrupted token file.")
            os.remove(TOKEN_PATH)
    return None


def save_credentials(creds):
    """Save credentials to the token file."""
    try:
        creds_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        with open(TOKEN_PATH, 'w') as token:
            json.dump(creds_data, token)
        logger.info("Credentials saved successfully.")
    except Exception as e:
        logger.error(f"Error saving credentials: {e}")


def authenticate_gmail():
    """
    Authenticate and return the Gmail API service with enhanced token management.
    This method avoids repeated re-authentication by refreshing the token if possible.
    """
    ensure_secrets_directory()

    try:
        creds = load_credentials()

        # Refresh or obtain new credentials if needed
        if creds:
            if creds.expired:
                if creds.refresh_token:
                    try:
                        logger.info("Refreshing access token...")
                        creds.refresh(Request())
                        save_credentials(creds)  # Save updated credentials after refresh
                    except RefreshError as e:
                        logger.warning(f"Token refresh failed: {e}. Initiating re-authentication.")
                        creds = None  # Force re-authentication
                else:
                    logger.warning("No refresh token available. Re-authentication required.")
                    creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"No credentials file found at {CREDENTIALS_PATH}. "
                    "Please download it from Google Cloud Console."
                )
            logger.info("Starting new OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            # Force new refresh_token issuance by setting prompt='consent'
            creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
            save_credentials(creds)  # Save credentials for future use

        # Build and verify the Gmail service
        service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        user_profile = service.users().getProfile(userId='me').execute()
        logger.info(f"Successfully authenticated as: {user_profile.get('emailAddress')}")

        return service

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise


def get_account_email(service, user_id='me'):
    """Retrieve the email address of the authenticated Gmail account."""
    try:
        profile = service.users().getProfile(userId=user_id).execute()
        email_address = profile.get('emailAddress')
        logger.info(f"Authenticated Email Address: {email_address}")
        return email_address
    except Exception as e:
        logger.error(f"Error retrieving account email: {str(e)}", exc_info=True)
        return None


# # Example usage
# if __name__ == "__main__":
#     try:
#         gmail_service = authenticate_gmail()
#         email = get_account_email(gmail_service)
#         logger.info(f"Authenticated Gmail account: {email}")
#     except Exception as e:
#         logger.critical(f"Failed to authenticate and retrieve email: {str(e)}", exc_info=True)
