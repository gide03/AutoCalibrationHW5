import logging
import pathlib


def getLogger(filename) -> logging.Logger:
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger