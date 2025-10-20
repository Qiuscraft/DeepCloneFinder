import logging
import os
import time
from logging.handlers import RotatingFileHandler

# Global variable to hold the logger instance
_logger = None
_log_file_path = None


def setup_logger(log_dir='logs'):
    """
    Set up a singleton logger to write to a file.
    """
    global _logger, _log_file_path
    if _logger is not None:
        return _logger

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = f"app_{time.strftime('%Y%m%d_%H%M%S')}.log"
    _log_file_path = os.path.join(log_dir, log_file)

    # Create a logger
    logger = logging.getLogger('DeepCloneFinder')
    logger.setLevel(logging.INFO)

    # Create a rotating file handler
    handler = RotatingFileHandler(_log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
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

    _logger = logger
    return _logger


def get_log_file_path():
    """
    Return the path of the current log file.
    """
    return _log_file_path


logger = setup_logger('logs')
