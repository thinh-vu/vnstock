import logging
from logging.handlers import RotatingFileHandler
import os

def get_logger(name):
    """Configure and return a logger with a specified name."""
    logger = logging.getLogger(name)
    if not logger.handlers:  # Check if the logger already has handlers to prevent duplicate logs
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)  # You might want to make the level configurable
    return logger


def advanced_logger(name, 
                        level='DEBUG', 
                        handler_type='stream', 
                        filename=None, 
                        log_format=None, 
                        date_format=None, 
                        max_bytes=10485760, 
                        backup_count=5):
    """
    Configure and return a customizable logger with various options.

    Parameters:
    - name: str - the logger's name.
    - level: str - logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    - handler_type: str - type of handler ('stream', 'file', 'rotating'). stream will print to console, file will write to a file, rotating will write to a file with a max size and backup files.
    - filename: str - path to log file. Defaults to current directory if None provided.
    - log_format: str - format of the log messages.
    - date_format: str - format of the timestamp in log messages.
    - max_bytes: int - maximum log file size in bytes (for 'rotating' handler).
    - backup_count: int - number of backup files to keep (for 'rotating' handler).
    
    Returns:
    - logger: logging.Logger instance.

    Examples:
    - Set up a logger: logger = get_advanced_logger('api_data_fetcher', level='INFO', handler_type='stream')
    - Log info: logger.info(f"Starting to fetch data from {api_url}")
    - Log error: 
                except requests.HTTPError as e:
                    logger.error(f"Failed to fetch data: {e}")
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():  # Prevent adding multiple handlers if already configured
        logger.handlers.clear()

    # Set default file name if none provided
    if filename is None:
        filename = os.path.join(os.getcwd(), f'{name}.log')

    # Set default log format if not provided
    log_format = log_format or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = date_format or '%Y-%m-%d %H:%M:%S'

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Determine the handler type
    if handler_type == 'file':
        handler = logging.FileHandler(filename)
    elif handler_type == 'rotating':
        handler = RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
    else:  # Default to stream handler
        handler = logging.StreamHandler()

    # Set formatter and add handler to logger
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the logging level
    logger.setLevel(getattr(logging, level.upper()))

    return logger
