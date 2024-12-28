import os
import logging
import base64
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
import indeed.scrap_overall 
import indeed.process_remove_duplicates

import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

def sample():
    """
    Main function to initialize the Gmail API service and process emails.
    """
    try:
        service = initialize_service()  # Replace with your Gmail API service initialization
        senders = ["example@example.com", "another@example.com"]  # Add sender email addresses to filter
        error_recipient = "admin@example.com"  # Email to send error notifications
        process_emails_with_transaction(service, senders, error_recipient)
    except Exception as e:
        logging.error(f"Failed to initialize and process emails: {e}", exc_info=True)

def process_emails_with_transaction(service, senders, error_recipient):
    """
    Process emails from specific senders. Implements fetching, scraping, and final updates.
    """
    try:
        labels = {
            "success_fetched": ensure_label_exists(service, "email fetched successfully"),
            "failure_fetched": ensure_label_exists(service, "failed fetching"),
            "success_scraped": ensure_label_exists(service, "successfully scraped"),
            "failure_scraped": ensure_label_exists(service, "failed scraping"),
            "success_final": ensure_label_exists(service, "success"),
            "failure_final": ensure_label_exists(service, "failure"),
        }

        if not all(labels.values()):
            logging.error("Failed to ensure all required labels.")
            return

        query = f"({' OR '.join([f'from:{sender}' for sender in senders])}) is:unread"
        results = retry_api_call(lambda: service.users().messages().list(userId='me', q=query).execute())
        messages = results.get('messages', [])

        if not messages:
            logging.info("No new emails found.")
            return

        for email in messages:
            email_id = email.get('id')
            try:
                email_data = fetch_email(service, email_id)
                html_content, metadata = email_data["html_content"], email_data["metadata"]
                scrape_email_content(html_content, metadata, labels, service, email_id)
                finalize_email(email_id, service, html_content, metadata, labels, error_recipient, success=True)
            except Exception as e:
                logging.error(f"Email processing failed for ID {email_id}: {e}", exc_info=True)
                finalize_email(email_id, service, None, {}, labels, error_recipient, success=False, error=e)
        
        
        # Call the deduplication function after processing all emails
        try:
            indeed.process_remove_duplicates.raw_csv_to_inter_csv()
        except Exception as e:
            logging.error(f"Error during deduplication process: {e}", exc_info=True)
       
    except HttpError as error:
        logging.error(f"An API error occurred: {error}", exc_info=True)

def fetch_email(service, email_id):
    """
    Fetch email content, decode HTML, and extract metadata.
    """
    try:
        msg = retry_api_call(lambda: service.users().messages().get(userId='me', id=email_id).execute())
        payload = msg['payload']
        headers = payload['headers']

        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
        sender_email = next((header['value'] for header in headers if header['name'] == 'From'), None)
        received_date = next((header['value'] for header in headers if header['name'] == 'Date'), None)

        if not received_date:
            raise Exception("No received date found in email headers.")

        received_datetime = parsedate_to_datetime(received_date)

        parts = payload.get('parts', [])
        html_content = None
        for part in parts:
            if part['mimeType'] == 'text/html':
                html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break

        if not html_content:
            raise Exception("No HTML content found in email.")

        return {"html_content": html_content, "metadata": {"subject": subject, "sender_email": sender_email, "received_datetime": received_datetime}}
    except Exception as e:
        logging.error(f"Failed to fetch email with ID {email_id}: {e}", exc_info=True)
        raise

def scrape_email_content(html_content, metadata, labels, service, email_id):
    """
    Scrape the email's HTML content and save extracted data.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        indeed.scrap_overall.scrap_process_email_content_to_csv(soup)
        logging.info(f"Scraping successful for email: {metadata['subject']}")
    except Exception as e:
        logging.error(f"Scraping failed for email {metadata['subject']} (ID: {email_id}): {e}", exc_info=True)
        raise

def finalize_email(email_id, service, html_content, metadata, labels, error_recipient, success, error=None):
    """
    Handle final updates on email based on success or failure.
    """
    try:
        if success:
            save_email_html(html_content, metadata['subject'], metadata['received_datetime'], metadata['sender_email'])
            mark_email_as_read(service, email_id)
            retry_api_call(lambda: service.users().messages().modify(
                userId='me',
                id=email_id,
                body={"addLabelIds": [labels['success_final']], "removeLabelIds": [labels['failure_final']]}
            ).execute())
        else:
            save_failed_html(html_content or "", metadata.get('subject', "No Subject"), metadata.get('received_datetime', datetime.now()), metadata.get('sender_email', "unknown"))
            send_error_email(service, error_recipient, metadata.get('subject', "Unknown"), str(error))
            mark_email_as_read(service, email_id)
            retry_api_call(lambda: service.users().messages().modify(
                userId='me',
                id=email_id,
                body={"addLabelIds": [labels['failure_final']]}
            ).execute())
    except Exception as e:
        logging.error(f"Finalizing email failed: {e}", exc_info=True)

def save_email_html(content, title, received_datetime, sender_email):
    """
    Save email content as an HTML file.
    """
    try:
        safe_title = "".join(c for c in title[:30] if c.isalnum() or c in " _-").strip()
        folder_path = os.path.join("data", "emails", str(received_datetime.year), received_datetime.strftime("%B"))
        os.makedirs(folder_path, exist_ok=True)
        file_name = f"{received_datetime.strftime('%Y_%m_%d_%H_%M_%S')}___{safe_title}.html"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logging.info(f"Email saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save email content: {e}", exc_info=True)

def save_failed_html(content, title, received_datetime, sender_email):
    """
    Save failed email content to a specific directory.
    """
    try:
        safe_title = "".join(c for c in title[:30] if c.isalnum() or c in " _-").strip()
        folder_path = os.path.join("data", "failed_emails")
        os.makedirs(folder_path, exist_ok=True)
        file_name = f"{received_datetime.strftime('%Y_%m_%d_%H_%M_%S')}___{safe_title}.html"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logging.info(f"Failed email saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save failed email content: {e}", exc_info=True)

def retry_api_call(call, retries=3, delay=2):
    for i in range(retries):
        try:
            return call()
        except HttpError as e:
            if i < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise e

def ensure_label_exists(service, label_name):
    try:
        label_list = service.users().labels().list(userId='me').execute()
        labels = label_list.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']

        label_body = {"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        new_label = service.users().labels().create(userId='me', body=label_body).execute()
        return new_label['id']
    except HttpError as error:
        logging.error(f"Failed to create label {label_name}: {error}", exc_info=True)
        return None

def mark_email_as_read(service, email_id):
    """
    Marks a specific Gmail message as read.
    """
    try:
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        logging.info(f"Email with ID {email_id} marked as read.")
    except Exception as e:
        logging.error(f"Failed to mark email as read: {e}", exc_info=True)

def send_error_email(service, recipient, subject, error_message):
    """
    Send an email to notify about a processing error.
    """
    try:
        message = {
            "raw": base64.urlsafe_b64encode(
                f"To: {recipient}\r\nSubject: {subject}\r\n\r\n{error_message}".encode("utf-8")
            ).decode("utf-8")
        }
        service.users().messages().send(userId='me', body=message).execute()
        logging.info(f"Error notification sent to {recipient}")
    except HttpError as error:
        logging.error(f"Failed to send error notification: {error}", exc_info=True)

# if __name__ == "__main__":
#     sample()