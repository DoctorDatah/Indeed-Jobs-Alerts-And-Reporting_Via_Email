import subprocess
import time
import logging
import os
import signal
import sys

import indeed.logging_config 

# Get logger
logger = indeed.logging_config.get_logger(__name__)

# Path to the main script
MAIN_SCRIPT = os.path.abspath("./app/main.py")

def restart_program():
    """
    Function to monitor and restart the main script.
    """
    while True:
        try:
            # Log and start the main script
            logging.info(f"Starting main script: {MAIN_SCRIPT}")
            process = subprocess.Popen(["python", MAIN_SCRIPT])

            # Wait for the process to finish
            process.wait()
            exit_code = process.returncode

            if exit_code == 0:
                # Normal exit
                logging.info("Main script exited normally.")
                break
            else:
                # Log if the script crashes
                logging.error(f"Main script crashed with exit code {exit_code}. Restarting...")

        except Exception as e:
            logging.error(f"Error while starting main script: {e}")

        # Wait a few seconds before restarting
        time.sleep(5)

def handle_exit(sig, frame):
    """
    Gracefully handle termination signals.
    """
    logging.info("Watchdog is shutting down.")
    sys.exit(0)

if __name__ == "__main__":
    # Catch termination signals for graceful shutdown
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    logging.info("Watchdog started.")
    restart_program()
