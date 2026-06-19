"""Deduplicate a merged metadata corpus.

Strategy (two-pass):
  1. Exact DOI match — records sharing a non-empty DOI are duplicates.
  2. Fuzzy title match via rapidfuzz — titles with similarity >= TITLE_THRESHOLD
     within the same year are considered duplicates.

corpus_id is assigned to ALL records before this function is called (in
run_corpus). Dedup only flags is_duplicate and records duplicate_of (the
corpus_id of the canonical record a duplicate maps to).

Source priority when two records are equivalent: pubmed > ieee > wos.
"""

import logging

import pandas as pd
from rapidfuzz import fuzz

import config

logger = logging.getLogger(__name__)

TITLE_THRESHOLD = 92
SOURCE_PRIORITY = {"pubmed": 0, "ieee": 1, "wos": 2}


def _source_rank(source: str) -> int:
    return SOURCE_PRIORITY.get(str(source).lower(), 99)


def deduplicate_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """Flag duplicate rows in *df* and return the annotated DataFrame.

    Expects a ``corpus_id`` column already assigned (sequential, 1-based,
    unique per row). Adds:
        is_duplicate  — True for rows that are duplicates of an earlier row.
        duplicate_of  — corpus_id of the canonical record; empty for unique rows.

    Args:
        df: Combined corpus with corpus_id already set and columns matching
            config.CORPUS_COLUMNS.

    Returns:
        Same DataFrame with is_duplicate and duplicate_of populated.
    """
    df = df.copy()
    df["corpus_id"] = df["corpus_id"].astype(int)
    df["is_duplicate"] = False
    df["duplicate_of"] = pd.array([pd.NA] * len(df), dtype=object)

    # Sort so preferred source comes first within each duplicate group
    df["_rank"] = df["source"].map(_source_rank)
    df = df.sort_values(["_rank", "corpus_id"]).reset_index(drop=True)
    df.drop(columns="_rank", inplace=True)

    seen_dois: dict[str, int] = {}                    # doi → corpus_id of canonical
    seen_title_year: list[tuple[str, str, int]] = []  # (title_lower, year, corpus_id)

    for idx, row in df.iterrows():
        doi = str(row.get("doi", "")).strip().lower()
        title = str(row.get("title", "")).strip().lower()
        year = str(row.get("year", ""))
        cid = row["corpus_id"]

        if df.at[idx, "is_duplicate"]:
            continue  # already flagged

        # Pass 1: exact DOI
        if doi and doi in seen_dois:
            df.at[idx, "is_duplicate"] = True
            df.at[idx, "duplicate_of"] = seen_dois[doi]
            continue

        # Pass 2: fuzzy title within same year
        matched_id = None
        for seen_title, seen_year, seen_cid in seen_title_year:
            if seen_year == year and fuzz.ratio(title, seen_title) >= TITLE_THRESHOLD:
                matched_id = seen_cid
                break

        if matched_id is not None:
            df.at[idx, "is_duplicate"] = True
            df.at[idx, "duplicate_of"] = matched_id
            continue

        # Unique — register as canonical
        if doi:
            seen_dois[doi] = cid
        seen_title_year.append((title, year, cid))

    n_dup = df["is_duplicate"].sum()
    logger.info(
        "Deduplication: %d total records, %d duplicates flagged, %d unique.",
        len(df), n_dup, len(df) - n_dup,
    )
    return df


def build_duplicate_map(df: pd.DataFrame) -> pd.DataFrame:
    """Build a summary table of canonical records and their duplicates.

    Returns one row per canonical record that has at least one duplicate:
        corpus_id        — id of the canonical record
        title            — title of the canonical record
        source           — source of the canonical record
        n_duplicates     — number of duplicates
        duplicate_ids    — comma-separated corpus_ids of the duplicate records
    """
    unique = df[~df["is_duplicate"]].set_index("corpus_id")
    dupes = df[df["is_duplicate"]].copy()

    rows = []
    for cid, group in dupes.groupby("duplicate_of"):
        if cid not in unique.index:
            continue
        canon = unique.loc[cid]
        dup_ids = ", ".join(str(r["corpus_id"]) for _, r in group.iterrows())
        rows.append({
            "corpus_id":     cid,
            "title":         canon["title"],
            "source":        canon["source"],
            "n_duplicates":  len(group),
            "duplicate_ids": dup_ids,
        })

    result = pd.DataFrame(rows, columns=["corpus_id", "title", "source", "n_duplicates", "duplicate_ids"])
    result = result.sort_values("corpus_id").reset_index(drop=True)
    logger.info("Duplicate map: %d canonical records have duplicates.", len(result))
    return result
