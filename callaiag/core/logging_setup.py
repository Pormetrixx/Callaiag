"""
Logging configuration for Callaiag.

This module sets up structured logging with appropriate handlers and formatters.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name
        log_dir: Optional log directory path
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logging(level="DEBUG", log_file="callaiag.log")
        >>> logger.info("Application started")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        if log_dir:
            log_path = Path(log_dir) / log_file
        else:
            log_path = Path(log_file)
        
        # Create log directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at {level} level")
    
    return root_logger
