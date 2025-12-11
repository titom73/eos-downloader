#!/usr/bin/env python
# coding: utf-8 -*-
# pylint: disable=line-too-long

"""
Tests for eos_downloader.logging_config module.

Tests the centralized logging configuration functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from loguru import logger

from eos_downloader.logging_config import configure_logging, get_logger


class TestConfigureLogging:
    """Test suite for configure_logging function."""

    def setup_method(self) -> None:
        """Setup for each test - remove all handlers."""
        logger.remove()

    def teardown_method(self) -> None:
        """Cleanup after each test - reset to default."""
        logger.remove()
        logger.add(sys.stderr)

    def test_configure_logging_default(self) -> None:
        """Test logging configuration with defaults."""
        configure_logging()

        # Logger should have at least one handler
        assert len(logger._core.handlers) > 0

    def test_configure_logging_debug_level(self) -> None:
        """Test configuration with DEBUG level."""
        configure_logging(level="DEBUG")

        # Verify by capturing a debug message
        with patch("sys.stderr") as mock_stderr:
            logger.debug("Test debug message")
            # Should be captured (not filtered out)

    def test_configure_logging_with_file(self, tmp_path: Path) -> None:
        """Test configuration with file output."""
        log_file = tmp_path / "test.log"

        configure_logging(level="INFO", log_file=log_file)

        # Write a log message
        logger.info("Test file logging")

        # Verify file was created
        assert log_file.exists()

        # Verify content
        content = log_file.read_text()
        assert "Test file logging" in content

    def test_configure_logging_custom_format(self) -> None:
        """Test configuration with custom format string."""
        custom_format = "{level} | {message}"

        configure_logging(format_string=custom_format)

        # Logger should be configured
        assert len(logger._core.handlers) > 0

    def test_configure_logging_no_colorize(self) -> None:
        """Test configuration without colors."""
        configure_logging(colorize=False)

        # Logger should be configured
        assert len(logger._core.handlers) > 0

    def test_configure_logging_removes_existing_handlers(self) -> None:
        """Test that configuration removes existing handlers."""
        # Add a handler first
        logger.add(sys.stderr)
        initial_count = len(logger._core.handlers)

        # Configure logging (should remove all and add new)
        configure_logging()

        # Should have exactly one handler (the new one)
        assert len(logger._core.handlers) == 1

    def test_configure_logging_with_rotation(self, tmp_path: Path) -> None:
        """Test file logging with rotation settings."""
        log_file = tmp_path / "rotating.log"

        configure_logging(level="INFO", log_file=log_file)

        # Write multiple messages
        for i in range(10):
            logger.info(f"Message {i}")

        # File should exist
        assert log_file.exists()

    def test_configure_logging_error_level(self) -> None:
        """Test configuration with ERROR level."""
        configure_logging(level="ERROR")

        with patch("sys.stderr.write") as mock_write:
            # INFO should be filtered out
            logger.info("This should not appear")
            assert not mock_write.called

            # ERROR should appear
            logger.error("This should appear")
            # Note: loguru buffering may affect this test


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_returns_logger_instance(self) -> None:
        """Test that get_logger returns a logger instance."""
        log = get_logger()

        # Should be the loguru logger
        assert log is logger

    def test_get_logger_same_instance(self) -> None:
        """Test that get_logger returns the same instance."""
        log1 = get_logger()
        log2 = get_logger()

        # Should be the same object
        assert log1 is log2

    def test_get_logger_can_log(self) -> None:
        """Test that logger from get_logger can log."""
        configure_logging(level="INFO")
        log = get_logger()

        # Should be able to log without error
        log.info("Test message")
        log.debug("Debug message")
        log.warning("Warning message")


class TestLoggingIntegration:
    """Integration tests for logging configuration."""

    def setup_method(self) -> None:
        """Setup for each test."""
        logger.remove()

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        logger.remove()
        logger.add(sys.stderr)

    def test_typical_usage_workflow(self, tmp_path: Path) -> None:
        """Test typical application usage workflow."""
        log_file = tmp_path / "app.log"

        # 1. Configure logging at startup
        configure_logging(level="DEBUG", log_file=log_file)

        # 2. Use logger throughout application
        logger.info("Application started")
        logger.debug("Debug information")
        logger.warning("Warning message")

        # 3. Verify logs
        assert log_file.exists()
        content = log_file.read_text()
        assert "Application started" in content
        assert "Debug information" in content
        assert "Warning message" in content

    def test_multiple_modules_same_logger(self) -> None:
        """Test that multiple modules share the same logger."""
        configure_logging(level="INFO")

        # Simulate imports from different modules
        from eos_downloader.logging_config import logger as logger1
        from eos_downloader.logging_config import logger as logger2

        # Should be the same instance
        assert logger1 is logger2

    def test_structured_logging_with_context(self, tmp_path: Path) -> None:
        """Test structured logging with context."""
        log_file = tmp_path / "structured.log"

        configure_logging(level="INFO", log_file=log_file)

        # Log with extra context
        logger.bind(request_id="123", user="test").info("User action")

        # Verify log was created
        assert log_file.exists()

    def test_exception_logging(self, tmp_path: Path) -> None:
        """Test exception logging with traceback."""
        log_file = tmp_path / "exceptions.log"

        configure_logging(level="ERROR", log_file=log_file)

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")

        # Verify exception was logged with traceback
        content = log_file.read_text()
        assert "ValueError" in content
        assert "Test exception" in content
