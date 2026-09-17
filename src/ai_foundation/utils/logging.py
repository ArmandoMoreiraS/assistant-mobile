"""Structured logging configuration for the ai_foundation project."""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the root logger for the project.

    Parameters
    ----------
    level:
        Logging level (default: logging.INFO).

    Returns
    -------
    logging.Logger
        Configured logger instance named 'ai_foundation'.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    return logging.getLogger("ai_foundation")


logger = configure_logging()
