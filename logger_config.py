"""Centralized logging configuration for ARAT-RL.

Usage:
    from logger_config import setup_logging, get_logger

    # In entry point scripts (if __name__ == "__main__"):
    setup_logging('arat-rl', log_file='arat-rl.log')

    # Create a module-level logger:
    logger = get_logger('arat-rl')

    # Use the logger:
    logger.info('Starting testing with spec: %s', spec_file)
    logger.warning('Request error: %s', e)
    logger.debug('Response value: %s = %s', key, value)

The log level can be controlled via the LOG_LEVEL environment variable.
Supported levels: DEBUG, INFO, WARNING, ERROR. Default: INFO.
"""

import os
import logging


def setup_logging(name, log_level='INFO', log_file=None):
    """Configure and return a logger with console and optional file output.

    Args:
        name: Logger name.
        log_level: Default log level (overridden by LOG_LEVEL env var).
        log_file: Optional path to a log file.

    Returns:
        Configured logging.Logger instance.
    """
    level_str = os.environ.get('LOG_LEVEL', log_level).upper()
    level = getattr(logging, level_str, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name):
    """Convenience function to get a logger by name.

    Args:
        name: Logger name.

    Returns:
        logging.Logger instance.
    """
    return logging.getLogger(name)
