import logging
from logging.handlers import RotatingFileHandler
import os

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
    - name: str - the logger's name. Example: 'api_logger'.
    - level: str - logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Example: 'INFO'.
    - handler_type: str - type of handler ('stream', 'file', 'rotating').
      'stream' will print to console, 'file' will write to a file, 'rotating' will write to a file with a max size and backup files. Example: 'rotating'.
    - filename: str - path to log file. Defaults to current directory if None provided. Example: '/var/logs/api.log'.
    - log_format: str - format of the log messages. Example: '%(asctime)s - %(levelname)s - %(message)s'.
    - date_format: str - format of the timestamp in log messages. Example: '%Y-%m-%d %H:%M:%S'.
    - max_bytes: int - maximum log file size in bytes (for 'rotating' handler). Example: 10485760 (10MB).
    - backup_count: int - number of backup files to keep (for 'rotating' handler). Example: 5.

    Returns:
    - logger: logging.Logger instance.
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

def get_logger(name, 
               level='DEBUG', 
               handler_type='stream', 
               filename=None, 
               log_format=None, 
               date_format=None, 
               max_bytes=10485760, 
               backup_count=5):
    """
    Wrapper for advanced_logger that allows custom logging configurations.
    Provides backward compatibility while allowing advanced customizations.

    Parameters:
    - All parameters are inherited from advanced_logger.

    Returns:
    - logger: logging.Logger instance.
    """
    return advanced_logger(name=name, 
                           level=level, 
                           handler_type=handler_type, 
                           filename=filename, 
                           log_format=log_format, 
                           date_format=date_format, 
                           max_bytes=max_bytes, 
                           backup_count=backup_count)
