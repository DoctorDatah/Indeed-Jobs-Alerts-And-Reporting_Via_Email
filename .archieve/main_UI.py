import tkinter as tk
from tkinter import messagebox
import logging
import threading
import indeed.gmail_auth
import indeed.gmail_listener
import sys

# Configure logging
log_filename = "app.log"
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger.addHandler(file_handler)

# Stream handler to redirect to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger.addHandler(stream_handler)

# Constants
SEARCH_SENDERS = ["malikhqtech@gmail.com", "alert@indeed.com", "noreply@example.com"]
ERROR_NOTIFICATION_EMAIL = "malikhqtech@gmail.com"

def start_process():
    """Start the email listener process."""
    logging.info("Starting process...")

    def process():
        try:
            # Authenticate Gmail API
            service = indeed.gmail_auth.authenticate_gmail()
            logging.info("Gmail API authenticated successfully!")

            # Start email fetch listener
            indeed.gmail_listener.start_email_fetch(
                service,
                SEARCH_SENDERS,
                ERROR_NOTIFICATION_EMAIL,
                interval=10
            )
        except Exception as e:
            logging.error(f"Error during initialization: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Run the process in a separate thread
    threading.Thread(target=process, daemon=True).start()

def main_ui():
    """Main UI for the application."""
    # Create the main window
    root = tk.Tk()
    root.title("Email Listener")

    # Configure the UI layout
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # Label
    label = tk.Label(frame, text="Click the button below to start the Email Listener.", font=("Arial", 12))
    label.pack(pady=10)

    # Start Button
    start_button = tk.Button(frame, text="Start Listener", font=("Arial", 12), bg="green", fg="white", command=start_process)
    start_button.pack(pady=10)

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main_ui()
