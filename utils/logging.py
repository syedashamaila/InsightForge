"""
Logging configuration module for the multi-agent analytics platform.

This module provides reusable logging setup functionality with support for
console and file logging, multiple log levels, and duplicate handler prevention.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    logger_name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
) -> logging.Logger:
    """
    Configure and return a logger with console and optional file handlers.

    This function sets up application-wide logging with support for both console
    and file output. It prevents duplicate handlers by checking existing handlers
    before adding new ones, ensuring clean logging output in multi-agent scenarios.

    Args:
        logger_name: The name of the logger instance. Typically use __name__.
        log_level: Logging level as string. Supported values: "DEBUG", "INFO".
                   Defaults to "INFO".
        log_file: Optional filename for file-based logging. If None, only console
                  logging is configured. Defaults to None.
        log_dir: Directory path for log files. Created if it doesn't exist.
                Defaults to "logs".

    Returns:
        logging.Logger: Configured logger instance ready for use.

    Example:
        >>> logger = setup_logging(__name__, log_level="DEBUG", log_file="app.log")
        >>> logger.info("Application started")
        >>> logger.debug("Debug information")
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)

    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path / log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger in multi-agent scenarios
    logger.propagate = False

    return logger
