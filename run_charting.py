"""Stage 3 — charting and IRR.

Generates an empty charting template from Phase 2 inclusions,
or loads and validates a completed charting CSV and computes IRR
if a second reviewer's file is provided.

Usage:
    # Generate empty template
    python run_charting.py --template

    # Validate a completed charting file
    python run_charting.py --file outputs/charting_results_r1.csv

    # Compute IRR between two reviewers
    python run_charting.py --irr --r1 outputs/charting_r1.csv --r2 outputs/charting_r2.csv

Options:
    --template       Write an empty charting template from screening results.
    --file PATH      Load and validate a completed charting CSV.
    --irr            Compute IRR between two reviewer files (requires --r1 and --r2).
    --r1 PATH        Reviewer 1 charting CSV.
    --r2 PATH        Reviewer 2 charting CSV.
    --col COLUMN     Decision column to use for IRR (default: inclusion_status).
"""

import argparse
import json
import logging

import pandas as pd

import config
from charting.charting import ChartingForm
from charting.irr import compute_irr
from utils import setup_logging, ensure_output_dir

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 3: charting + IRR")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--template", action="store_true", help="Generate empty charting template.")
    group.add_argument("--file", type=str, metavar="PATH", help="Validate a completed charting CSV.")
    group.add_argument("--irr", action="store_true", help="Compute IRR between two reviewer files.")
    p.add_argument("--r1", type=str, metavar="PATH")
    p.add_argument("--r2", type=str, metavar="PATH")
    p.add_argument("--col", type=str, default="inclusion_status", metavar="COLUMN")
    return p.parse_args()


def main() -> None:
    setup_logging()
    ensure_output_dir("outputs")
    args = parse_args()
    form = ChartingForm()

    if args.template:
        logger.info("Loading screening results from %s", config.SCREENING_CSV)
        screening = pd.read_csv(config.SCREENING_CSV, dtype=str)
        screening["inclusion_status"] = pd.to_numeric(screening["inclusion_status"], errors="coerce")
        template = form.empty_template(screening)
        template.to_csv(config.CHARTING_CSV, index=False)
        template.to_excel(config.CHARTING_XLSX, index=False)
        logger.info("Empty charting template written to %s (%d rows).", config.CHARTING_CSV, len(template))

    elif args.file:
        df = form.load(args.file)
        df.to_csv(config.CHARTING_CSV, index=False)
        df.to_excel(config.CHARTING_XLSX, index=False)
        logger.info("Charting file validated and saved to %s.", config.CHARTING_CSV)

    elif args.irr:
        if not args.r1 or not args.r2:
            logger.error("--irr requires --r1 and --r2 paths.")
            return
        r1 = pd.read_csv(args.r1, dtype=str)
        r2 = pd.read_csv(args.r2, dtype=str)
        result = compute_irr(r1[args.col], r2[args.col], label=args.col)
        irr_df = pd.DataFrame([result])
        irr_df.to_csv(config.IRR_CSV, index=False)
        logger.info("IRR report written to %s.", config.IRR_CSV)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
