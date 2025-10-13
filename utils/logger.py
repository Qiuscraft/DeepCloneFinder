import logging
import os
import time
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir='logs', log_file='app.log'):
    """
    Set up the logger to write to a file.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_file)

    # Create a logger
    logger = logging.getLogger('DeepCloneFinder')
    logger.setLevel(logging.INFO)

    # Create a rotating file handler
    handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger('logs', f"app_{time.strftime('%Y%m%d_%H%M%S')}.log")

