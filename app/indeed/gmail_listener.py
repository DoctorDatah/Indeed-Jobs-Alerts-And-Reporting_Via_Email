import time
import logging
import indeed.process_latest_emails

import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

# Flag to control the fetching process
is_fetching = False

def start_email_fetch(service, senders, error_recipient, interval=10):
    """
    Start fetching emails periodically.

    Args:
        service: The Gmail API service instance.
        senders (list): List of sender email addresses to filter emails from.
        error_recipient (str): Email address to notify in case of processing errors.
        interval (int): Time interval (in seconds) between email fetch attempts.
    """
    global is_fetching

    if is_fetching:
        logging.warning("Email fetching is already running.")
        return

    is_fetching = True

    # Main fetching loop
    logging.info("Email fetching started.")
    try:
        while is_fetching:
            try:
                # Refresh Gmail auth
                service = indeed.gmail_auth.authenticate_gmail()
                indeed.process_latest_emails.process_emails_with_transaction(
                    service, senders, error_recipient
                )
                logging.info("Waiting for new emails...")
            except Exception as e:
                logging.error(f"Error while fetching emails: {e}", exc_info=True)

            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Stopping fetching process.")
        stop_email_fetch()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logging.info("Email fetching stopped.")

def stop_email_fetch():
    """Stop the email fetching process."""
    global is_fetching

    if not is_fetching:
        logging.warning("Email fetching is not running.")
        return

    is_fetching = False
    logging.info("Email fetching process has been stopped.")

def main():
    """Main function to initialize and start the email fetching process."""
    try:
        # Authenticate the Gmail API
        service = indeed.gmail_auth.authenticate_gmail()

        # Define the list of senders to monitor
        senders = ["example1@example.com", "example2@example.com"]

        # Define the error recipient email
        error_recipient = "admin@example.com"

        # Start the email fetching process
        start_email_fetch(service, senders, error_recipient, interval=10)

    except Exception as e:
        logging.error(f"An error occurred in the main process: {e}", exc_info=True)
    finally:
        stop_email_fetch()

# if __name__ == "__main__":
#     main()
