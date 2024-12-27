import logging
import os
from logging.handlers import RotatingFileHandler

# Define log directory and file
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'logs'))
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, "app.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_filename, maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

# Function to get logger
def get_logger(name):
    return logging.getLogger(name)