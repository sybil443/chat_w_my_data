import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging(name):
    """
    Set up logging configuration that can be used across the application
    
    Args:
        name (str): Logger name ('FlaskApp' or 'ExcelQuerySystem')
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Only add handlers if they haven't been added already
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Create handlers
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            f'logs/application_{current_time}.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter('%(levelname)s - %(message)s')
        
        # Add formatters to handlers
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger