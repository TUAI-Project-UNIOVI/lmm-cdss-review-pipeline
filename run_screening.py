"""Stage 2 — abstract screening and full-paper reading aid.

Reads outputs/corpus.pkl, runs Phase 1 abstract screening, writes
screening_results, then optionally runs the Phase 2 full-paper reading aid.

Usage:
    python run_screening.py [--skip-fullpaper]

Options:
    --skip-fullpaper   Run only the abstract screener (Phase 1).
                       Useful when full texts are not yet retrieved.
"""

import argparse
import logging
import os

import joblib
import pandas as pd

import config
from screening.abstract_screen import AbstractScreener
from screening.fullpaper_screen import FullPaperScreener
from utils import setup_logging, ensure_output_dir

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 2: screening")
    p.add_argument("--skip-fullpaper", action="store_true")
    return p.parse_args()


def main() -> None:
    setup_logging()
    ensure_output_dir("outputs")
    args = parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    # --- Load corpus ---
    logger.info("Loading corpus from %s", config.CORPUS_PKL)
    corpus: pd.DataFrame = joblib.load(config.CORPUS_PKL)
    corpus = corpus[~corpus["is_duplicate"]].reset_index(drop=True)
    logger.info("Corpus: %d unique records loaded.", len(corpus))

    # --- Phase 1: abstract screening ---
    screener = AbstractScreener(api_key=gemini_key)
    results = screener.screen(corpus)

    results.to_csv(config.SCREENING_CSV, index=False)
    results.to_excel(config.SCREENING_XLSX, index=False)
    joblib.dump(results, config.SCREENING_PKL)
    logger.info(
        "Abstract screening done. Results: %s",
        results["inclusion_status"].value_counts().to_dict(),
    )

    if args.skip_fullpaper:
        logger.info("--skip-fullpaper set; skipping Phase 2 reading aid.")
        return

    # --- Phase 2: full-paper reading aid ---
    fp_screener = FullPaperScreener(api_key=gemini_key)
    fp_results = fp_screener.screen(results)

    fp_results.to_csv(config.FULLPAPER_CSV, index=False)
    fp_results.to_excel(config.FULLPAPER_XLSX, index=False)
    logger.info(
        "Full-paper reading aid done. %d summaries written to %s",
        len(fp_results), config.FULLPAPER_CSV,
    )


if __name__ == "__main__":
    main()
