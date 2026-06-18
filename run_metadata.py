"""Stage 1 — metadata retrieval.

Runs all three database fetchers, merges results, deduplicates, and writes
the corpus files that Stage 2 (screening) consumes.

Usage:
    python run_metadata.py [--max MAX_RESULTS] [--pubmed-only] [--wos-export PATH]

Options:
    --max           Override MAX_RESULTS from config.py (default: config value).
    --pubmed-only   Skip IEEE and WoS fetchers (useful for quick tests).
    --wos-export    Path to a manually exported WoS TSV file (uses WoSExportLoader
                    instead of the API — set when WOS_API_KEY is unavailable).
"""

import argparse
import logging
import os
import sys

import joblib
import pandas as pd

import config
from dedup import deduplicate_corpus
from metadata.pubmed import PubMedFetcher
from metadata.ieee import IEEEFetcher
from metadata.wos import WoSFetcher, WoSExportLoader
from utils import setup_logging, ensure_output_dir

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 1: metadata retrieval")
    p.add_argument("--max", type=int, default=config.MAX_RESULTS, dest="max_results")
    p.add_argument("--pubmed-only", action="store_true")
    p.add_argument("--wos-export", type=str, default=None, metavar="PATH")
    # parse_known_args ignores Jupyter kernel args that would crash parse_args()
    args, _ = p.parse_known_args()
    return args


def main() -> None:
    setup_logging()
    ensure_output_dir("outputs")
    args = parse_args()

    frames: list[pd.DataFrame] = []

    # --- PubMed ---
    ncbi_key = os.environ.get("NCBI_API_KEY", "")
    ncbi_email = os.environ.get("NCBI_EMAIL", "")
    try:
        pubmed = PubMedFetcher(email=ncbi_email, api_key=ncbi_key)
        df_pm = pubmed.fetch(max_results=args.max_results)
        df_pm.to_csv(config.PUBMED_RAW_CSV, index=False)
        logger.info("PubMed raw saved to %s", config.PUBMED_RAW_CSV)
        frames.append(df_pm)
    except Exception as exc:
        logger.error("PubMed fetcher failed: %s", exc)

    if not args.pubmed_only:
        # --- IEEE ---
        ieee_key = os.environ.get("IEEE_API_KEY", "")
        try:
            ieee = IEEEFetcher(api_key=ieee_key)
            df_ieee = ieee.fetch(max_results=args.max_results)
            df_ieee.to_csv(config.IEEE_RAW_CSV, index=False)
            logger.info("IEEE raw saved to %s", config.IEEE_RAW_CSV)
            frames.append(df_ieee)
        except Exception as exc:
            logger.error("IEEE fetcher failed: %s", exc)

        # --- WoS ---
        if args.wos_export:
            try:
                loader = WoSExportLoader()
                df_wos = loader.load(args.wos_export)
                df_wos.to_csv(config.WOS_RAW_CSV, index=False)
                logger.info("WoS export loaded and saved to %s", config.WOS_RAW_CSV)
                frames.append(df_wos)
            except Exception as exc:
                logger.error("WoS export loader failed: %s", exc)
        else:
            wos_key = os.environ.get("WOS_API_KEY", "")
            try:
                wos = WoSFetcher(api_key=wos_key)
                df_wos = wos.fetch(max_results=args.max_results)
                df_wos.to_csv(config.WOS_RAW_CSV, index=False)
                logger.info("WoS raw saved to %s", config.WOS_RAW_CSV)
                frames.append(df_wos)
            except Exception as exc:
                logger.error("WoS fetcher failed: %s", exc)

    if not frames:
        logger.error("No data collected from any source. Aborting.")
        return

    # --- Merge + dedup ---
    combined = pd.concat(frames, ignore_index=True)
    corpus = deduplicate_corpus(combined)

    corpus.to_csv(config.CORPUS_CSV, index=False)
    corpus.to_excel(config.CORPUS_XLSX, index=False)
    joblib.dump(corpus, config.CORPUS_PKL)

    unique_count = (~corpus["is_duplicate"]).sum()
    logger.info(
        "Corpus saved: %d total rows, %d unique records.",
        len(corpus), unique_count,
    )
    logger.info("Files: %s | %s | %s", config.CORPUS_CSV, config.CORPUS_XLSX, config.CORPUS_PKL)


if __name__ == "__main__":
    # In Jupyter there are no meaningful CLI args, so default to --pubmed-only
    if len(sys.argv) == 1 or not any(a.startswith("--") for a in sys.argv[1:]):
        sys.argv = ["run_metadata.py", "--pubmed-only"]
    main()


