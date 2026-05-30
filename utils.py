"""Shared utilities: logging, directory setup, and API retry decorator."""

import os
import logging
import functools
import time
from typing import Callable, TypeVar

from dotenv import load_dotenv

load_dotenv()

F = TypeVar("F", bound=Callable)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with timestamp + level format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def ensure_output_dir(dir_path: str = "outputs") -> None:
    """Create *dir_path* if it does not exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logging.info("Created output directory: %s", dir_path)


def retry(max_attempts: int = 3, wait: float = 10.0, backoff: float = 2.0) -> Callable[[F], F]:
    """Decorator: retry *max_attempts* times with exponential back-off on any Exception.

    Args:
        max_attempts: Total number of tries (including the first).
        wait: Initial wait in seconds before the second attempt.
        backoff: Multiplier applied to *wait* after each failure.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = wait
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_attempts:
                        logging.error(
                            "%s failed after %d attempts: %s", func.__name__, max_attempts, exc
                        )
                        raise
                    logging.warning(
                        "%s attempt %d/%d failed (%s). Retrying in %.0fs.",
                        func.__name__, attempt, max_attempts, exc, delay,
                    )
                    time.sleep(delay)
                    delay *= backoff
        return wrapper  # type: ignore[return-value]
    return decorator
