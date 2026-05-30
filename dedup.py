"""Deduplicate a merged metadata corpus.

Strategy (two-pass):
  1. Exact DOI match — records sharing a non-empty DOI are duplicates.
  2. Fuzzy title match via rapidfuzz — titles with similarity >= TITLE_THRESHOLD
     within the same year are considered duplicates.

The first occurrence (by source priority: pubmed > ieee > wos) is kept;
duplicates have is_duplicate=True and are retained in the output for audit.
"""

import logging

import pandas as pd
from rapidfuzz import fuzz

import config

logger = logging.getLogger(__name__)

# Minimum title similarity score (0–100) to call two records duplicates
TITLE_THRESHOLD = 92
SOURCE_PRIORITY = {"pubmed": 0, "ieee": 1, "wos": 2}


def _source_rank(source: str) -> int:
    return SOURCE_PRIORITY.get(str(source).lower(), 99)


def deduplicate_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """Mark duplicate rows in *df* and return the annotated DataFrame.

    Args:
        df: Combined corpus with columns matching config.CORPUS_COLUMNS.

    Returns:
        Same DataFrame with ``is_duplicate`` column updated.
        Call ``df[~df.is_duplicate]`` to get the clean subset.
    """
    df = df.copy()
    df["is_duplicate"] = False

    # Sort so the preferred source comes first
    df["_rank"] = df["source"].map(_source_rank)
    df = df.sort_values("_rank").reset_index(drop=True)
    df.drop(columns="_rank", inplace=True)

    seen_dois: set[str] = set()
    seen_title_year: list[tuple[str, str]] = []  # (normalised_title, year)

    for idx, row in df.iterrows():
        doi = str(row.get("doi", "")).strip().lower()
        title = str(row.get("title", "")).strip()
        year = str(row.get("year", ""))

        if doi and doi in seen_dois:
            df.at[idx, "is_duplicate"] = True
            continue

        # Fuzzy title check within same year
        is_dup = False
        title_lower = title.lower()
        for seen_title, seen_year in seen_title_year:
            if seen_year == year:
                score = fuzz.ratio(title_lower, seen_title)
                if score >= TITLE_THRESHOLD:
                    is_dup = True
                    break

        if is_dup:
            df.at[idx, "is_duplicate"] = True
            continue

        # Not a duplicate — add to seen sets
        if doi:
            seen_dois.add(doi)
        seen_title_year.append((title_lower, year))

    n_dup = df["is_duplicate"].sum()
    logger.info(
        "Deduplication: %d total records, %d duplicates flagged, %d unique.",
        len(df), n_dup, len(df) - n_dup,
    )
    return df
