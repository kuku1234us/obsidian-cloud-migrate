"""
Error Handler Module

This module provides centralized error handling functionality for the EOD Downloader application.
It implements an ErrorHandler class that can be used to manage and respond to various types of errors.

The ErrorHandler uses the Logger for logging errors and can be configured to handle different
types of errors in different ways (e.g., logging, raising exceptions, or custom actions).

Usage:
    from utils.error_handler import ErrorHandler
    
    error_handler = ErrorHandler()
    try:
        # Some operation that might raise an exception
        result = 10 / 0
    except Exception as e:
        error_handler.handle_error(e, "Division by zero occurred", show_message=True)

Configuration:
    Error handling settings can be read from the application's config file if needed.
"""

from utils.logger import Logger
import traceback
from PyQt6.QtWidgets import QMessageBox
import sys


class ErrorHandler:
    def __init__(self):
        self.logger = Logger()

    def handle_error(
        self, error, message=None, log_level="error", raise_exception=False, show_message=False, parent=None
    ):
        """
        Handle an error by logging it and optionally raising an exception and/or showing a message to the user.

        Args:
            error (Exception): The error that occurred.
            message (str, optional): Additional message to log and display.
            log_level (str, optional): The log level to use ('debug', 'info', 'warning', 'error', 'critical').
            raise_exception (bool, optional): Whether to re-raise the exception after logging.
            show_message (bool, optional): Whether to show a message box to the user.
            parent (QWidget, optional): Parent widget for the message box.
        """
        error_message = f"{message}: {str(error)}" if message else str(error)
        error_type = type(error).__name__

        # Get the full stack trace
        stack_trace = traceback.format_exc()

        # Log the error
        log_method = getattr(self.logger, log_level)
        log_method(f"Error Type: {error_type}")
        log_method(f"Error Message: {error_message}")
        log_method(f"Stack Trace:\n{stack_trace}")

        # Show message to the user if requested
        if show_message:
            QMessageBox.critical(parent, "Error", error_message)

        if raise_exception:
            raise error

    def handle_fatal_error(self, error, message=None, parent=None):
        """
        Handle a fatal error by logging it, showing a message, and exiting the application.

        Args:
            error (Exception): The fatal error that occurred.
            message (str, optional): Additional message to log and display.
            parent (QWidget, optional): Parent widget for the message box.
        """
        self.handle_error(error, message, log_level="critical", show_message=True, parent=parent)
        self.logger.critical("Fatal error occurred. Exiting application.")
        sys.exit(1)

    def log_warning(self, message):
        """
        Log a warning message.

        Args:
            message (str): The warning message to log.
        """
        self.logger.warning(message)

    def log_info(self, message):
        """
        Log an informational message.

        Args:
            message (str): The informational message to log.
        """
        self.logger.info(message)
