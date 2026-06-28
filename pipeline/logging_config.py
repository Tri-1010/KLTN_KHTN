"""
Logging configuration for the VN30 Stock Prediction Pipeline.

Provides structured logging with format:
    [timestamp] [task_name] [level] message

Each task writes to its own log file under logs/.
"""

import logging
import os
from datetime import datetime


class TaskNameFilter(logging.Filter):
    """Injects task_name into log records."""

    def __init__(self, task_name: str = "PIPELINE"):
        super().__init__()
        self.task_name = task_name

    def filter(self, record):
        record.task_name = self.task_name
        return True


LOG_FORMAT = "[%(asctime)s] [%(task_name)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_DIR = "logs"


def setup_logger(
    task_name: str,
    level: int = logging.INFO,
    log_dir: str = LOG_DIR,
) -> logging.Logger:
    """
    Create and configure a logger for a specific pipeline task.

    Args:
        task_name: Name of the task (e.g., "TASK_1", "TASK_2").
        level: Logging level (default: INFO).
        log_dir: Directory for log files (default: "logs").

    Returns:
        Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(task_name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    task_filter = TaskNameFilter(task_name)

    # File handler: logs/{task_name}_{YYYYMMDD}.log
    today = datetime.now().strftime("%Y%m%d")
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"{task_name}_{today}.log"),
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(task_filter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(task_filter)
    logger.addHandler(console_handler)

    return logger
