"""Stage 4 — PRISMA counts and synthesis figures.

Aggregates all stage outputs into prisma_counts.json and generates
descriptive figures for the manuscript synthesis section.

Usage:
    python run_reporting.py [--counts-only] [--figures-only]

Options:
    --counts-only    Write only prisma_counts.json, skip figure generation.
    --figures-only   Generate only figures, skip PRISMA counts.
"""

import argparse
import json
import logging

import config
from reporting.prisma import prisma_counts
from reporting.synthesis import generate_figures
from utils import setup_logging, ensure_output_dir

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 4: reporting")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--counts-only", action="store_true")
    g.add_argument("--figures-only", action="store_true")
    return p.parse_args()


def main() -> None:
    setup_logging()
    ensure_output_dir("outputs")
    ensure_output_dir(config.FIGURES_DIR)
    args = parse_args()

    if not args.figures_only:
        counts = prisma_counts()
        logger.info("PRISMA counts summary:\n%s", json.dumps(counts, indent=2))

    if not args.counts_only:
        generate_figures()


if __name__ == "__main__":
    main()
