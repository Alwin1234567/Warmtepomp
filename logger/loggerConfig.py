import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Create a custom logger
logger = logging.getLogger('warmtepomp_logger')
logger.setLevel(logging.DEBUG)

# Define the log directory
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
log_dir_error = os.path.join(log_dir, 'errors')
os.makedirs(log_dir, exist_ok=True)
os.makedirs(log_dir_error, exist_ok=True)

# Create handlers
debug_handler = TimedRotatingFileHandler(os.path.join(log_dir, 'debug.log'), when='midnight', interval=1)
debug_handler.setLevel(logging.DEBUG)
debug_handler.suffix = "%Y-%m-%d"

error_handler = TimedRotatingFileHandler(os.path.join(log_dir_error, 'error.log'), when='midnight', interval=1)
error_handler.setLevel(logging.ERROR)
error_handler.suffix = "%Y-%m-%d"

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(debug_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)