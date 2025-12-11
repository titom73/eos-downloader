#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""
Centralized logging configuration for eos-downloader.

This module provides a unified logging setup using loguru across
all eos-downloader modules, replacing the mixed usage of standard
logging and loguru.

Functions
---------
configure_logging
    Configure loguru logger with standard format and level
get_logger
    Get the configured logger instance

Examples
--------
>>> from eos_downloader.logging_config import logger
>>> logger.info("Application started")
>>> logger.debug("Debug information", extra={"context": "value"})

Notes
-----
This module standardizes on loguru for all logging to ensure:
- Consistent log format across all modules
- Better structured logging with context
- Easier configuration and filtering
- Rich terminal output with colors
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger as LoguruLogger


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
    colorize: bool = True,
) -> None:
    """
    Configure the global loguru logger.

    Sets up logging with consistent format, level, and optional file output.
    Should be called once at application startup before any logging occurs.

    Parameters
    ----------
    level : str, optional
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL), by default "INFO"
    log_file : Optional[Path], optional
        Path to log file for persistent logging, by default None (no file)
    format_string : Optional[str], optional
        Custom format string, by default uses standard format
    colorize : bool, optional
        Enable colored output for terminal, by default True

    Examples
    --------
    Basic usage with INFO level:

    >>> configure_logging(level="INFO")

    Enable debug logging with file output:

    >>> configure_logging(
    ...     level="DEBUG",
    ...     log_file=Path("/tmp/eos-downloader.log")
    ... )

    Custom format:

    >>> configure_logging(
    ...     format_string="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    ... )

    Notes
    -----
    - Removes all existing handlers first
    - Default format includes: timestamp, level, module, function, line, message
    - Colored output works best in modern terminals
    - Log file is created with UTF-8 encoding
    - Thread-safe for concurrent logging
    """
    # Remove default handler
    logger.remove()

    # Default format string with rich context
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=colorize,
        backtrace=True,
        diagnose=True,
    )

    # Add file handler if requested
    if log_file:
        logger.add(
            str(log_file),
            format=format_string,
            level=level,
            rotation="10 MB",  # Rotate at 10MB
            retention="7 days",  # Keep logs for 7 days
            compression="zip",  # Compress old logs
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )

    logger.debug(f"Logging configured at {level} level")


def get_logger() -> "LoguruLogger":
    """
    Get the configured logger instance.

    Returns the global loguru logger that has been configured via
    configure_logging(). This function is provided for compatibility
    but direct import of logger is preferred.

    Returns
    -------
    loguru.Logger
        The configured logger instance

    Examples
    --------
    >>> from eos_downloader.logging_config import get_logger
    >>> log = get_logger()
    >>> log.info("Message")

    Preferred approach (direct import):

    >>> from eos_downloader.logging_config import logger
    >>> logger.info("Message")

    Notes
    -----
    - Returns the same logger instance across all calls
    - Logger is configured globally, not per-instance
    - Use logger directly instead of this function when possible
    """
    return logger


# Export logger for direct import
__all__ = ["logger", "configure_logging", "get_logger"]
