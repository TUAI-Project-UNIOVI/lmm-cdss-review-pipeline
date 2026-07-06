"""Stage 1b — automatic pre-filtering.

Applies four exclusion codes to the deduplicated corpus before records are
forwarded to human reviewers.  Does NOT drop rows; adds boolean flag columns
so the caller controls what gets forwarded.

Exclusion codes:
    SE1_language  — detected language is not English
    SE2_date      — publication year outside SEARCH_YEAR_START–SEARCH_YEAR_END
    SE3_pub_type  — not a peer-reviewed source type
    SE4_retracted — paper appears in Retraction Watch

Conservative default for all codes: when data are missing or unparseable,
return False (include).
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import pandas as pd

import config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SE3 — peer-reviewed type allowlists (source-aware)
# ---------------------------------------------------------------------------

_PUBMED_PEER_REVIEWED: set[str] = {
    "Journal Article",
    "Systematic Review",
    "Scoping Review",
    "Randomized Controlled Trial",
    "Clinical Trial",
    "Meta-Analysis",
    "Multicenter Study",
    "Observational Study",
    "Comparative Study",
    "Controlled Clinical Trial",
    "Twin Study",
    "Validation Study",
}

_WOS_PEER_REVIEWED: set[str] = {"Article", "Review", "Proceedings Paper"}

_IEEE_PEER_REVIEWED: set[str] = {"journal article", "conference paper"}


# ---------------------------------------------------------------------------
# SE1 — language detection
# ---------------------------------------------------------------------------

def _detect_not_english(row: pd.Series) -> bool:
    """Return True if the record is detected as non-English."""
    try:
        from langdetect import detect  # type: ignore
    except ImportError:
        logger.warning("langdetect not installed; SE1 check skipped (all treated as English).")
        return False

    text = f"{row.get('title', '')} {row.get('abstract', '')}".strip().lower()
    if not text:
        return False
    try:
        return detect(text) != "en"
    except Exception:
        return False


# ---------------------------------------------------------------------------
# SE3 — source-type check
# ---------------------------------------------------------------------------

def _is_not_peer_reviewed(row: pd.Series) -> bool:
    """Return True if the record is NOT a peer-reviewed source type."""
    source = str(row.get("source", "")).lower().strip()
    pub_type = row.get("pub_type", "")
    if pd.isna(pub_type) or str(pub_type).strip() == "":
        return False  # unknown → conservative include

    pub_type_str = str(pub_type).strip()

    if source == "pubmed":
        # pub_type is stored as the string repr of a dict: "{'D016428': 'Journal Article'}"
        try:
            type_dict = ast.literal_eval(pub_type_str)
            labels: set[str] = set(type_dict.values())
            return labels.isdisjoint(_PUBMED_PEER_REVIEWED)
        except Exception:
            return False

    if source == "ieee":
        return pub_type_str.lower() not in _IEEE_PEER_REVIEWED

    if source == "wos":
        return pub_type_str not in _WOS_PEER_REVIEWED

    return False  # unknown source → conservative include


# ---------------------------------------------------------------------------
# SE4 — retraction check
# ---------------------------------------------------------------------------

def _load_retraction_dois(csv_path: str) -> set[str]:
    """Load Retraction Watch CSV and return a set of lowercased DOIs."""
    df = pd.read_csv(csv_path, usecols=["OriginalPaperDOI"], dtype=str)
    return set(df["OriginalPaperDOI"].str.lower().str.strip().dropna())


def _check_retracted(corpus: pd.DataFrame, retraction_csv: str | None) -> pd.Series:
    """Return a boolean Series — True if the record's DOI is in Retraction Watch."""
    result = pd.Series(False, index=corpus.index)
    if not retraction_csv:
        return result

    path = Path(retraction_csv)
    if not path.exists():
        logger.warning("Retraction Watch CSV not found at %s — SE4 skipped.", retraction_csv)
        return result

    try:
        retracted_dois = _load_retraction_dois(str(path))
        logger.info("Retraction Watch: %d retracted DOIs loaded.", len(retracted_dois))
    except Exception as exc:
        logger.warning("Could not load Retraction Watch CSV (%s) — SE4 skipped.", exc)
        return result

    doi_col = corpus["doi"].fillna("").str.lower().str.strip()
    result = doi_col.isin(retracted_dois) & (doi_col != "")
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_prefilter(
    corpus: pd.DataFrame,
    retraction_csv: str | None = None,
) -> pd.DataFrame:
    """Add SE1–SE4 boolean flag columns to *corpus* and return the result.

    Does not drop rows.  Operates on all rows (including duplicates) so the
    full corpus is stamped consistently; callers filter to unique + SE-passing
    records before forwarding to reviewers.
    """
    corpus = corpus.copy()

    logger.info("Applying SE1 — language check...")
    corpus["SE1_language"] = corpus.apply(_detect_not_english, axis=1)

    logger.info("Applying SE2 — date range check...")
    year_col = pd.to_numeric(corpus["year"], errors="coerce")
    corpus["SE2_date"] = ~year_col.between(config.SEARCH_YEAR_START, config.SEARCH_YEAR_END)

    logger.info("Applying SE3 — source type check...")
    corpus["SE3_pub_type"] = corpus.apply(_is_not_peer_reviewed, axis=1)

    logger.info("Applying SE4 — retraction check...")
    corpus["SE4_retracted"] = _check_retracted(corpus, retraction_csv)

    return corpus


def prefilter_summary(corpus: pd.DataFrame) -> dict[str, int]:
    """Return exclusion counts per SE code, computed on unique records only."""
    unique = corpus[~corpus["is_duplicate"].astype(bool)]
    se_cols = ["SE1_language", "SE2_date", "SE3_pub_type", "SE4_retracted"]
    summary: dict[str, int] = {}
    for col in se_cols:
        if col in unique.columns:
            summary[col] = int(unique[col].sum())
    any_excluded = unique[se_cols].any(axis=1).sum() if se_cols else 0
    summary["total_excluded"] = int(any_excluded)
    summary["forwarded_to_screening"] = int(len(unique) - any_excluded)
    return summary
