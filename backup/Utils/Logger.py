import logging

loggers = {}

def getLogger(filename) -> logging.Logger:
    if filename in loggers:
        return loggers[filename]
    
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    logger.handlers.clear()

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
    loggers[filename] = logger
    return logger