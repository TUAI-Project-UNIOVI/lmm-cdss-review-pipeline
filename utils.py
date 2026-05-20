"""Utility functions for the TUAI Review Scrapers project.

This module provides shared helper functions used across different stages 
of the systematic review pipeline.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_logging(level: int = logging.INFO) -> None:
    """Sets up basic configuration for logging.

    Args:
        level (int): The logging level to set (e.g., logging.INFO, logging.DEBUG).
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def ensure_output_dir(dir_path: str = "outputs") -> None:
    """Ensures that the specified output directory exists.

    If the directory does not exist, it will be created.

    Args:
        dir_path (str): The path to the directory to ensure exists. Defaults to "outputs".
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logging.info(f"Created output directory: {dir_path}")
    else:
        logging.debug(f"Output directory already exists: {dir_path}")

if __name__ == "__main__":
    # Example usage for testing purposes
    setup_logging()
    ensure_output_dir()
    print("Utilities initialized successfully.")
