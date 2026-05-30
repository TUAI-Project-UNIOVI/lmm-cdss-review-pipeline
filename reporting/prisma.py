"""PRISMA-ScR flow diagram record counts.

Aggregates per-stage record counts from the output CSVs and writes
prisma_counts.json — the single source of truth for the PRISMA-ScR diagram
and Appendix C (Search Execution Log) in @mtx.

Expected counts structure:
  identification:
    pubmed_retrieved, ieee_retrieved, wos_retrieved, total_retrieved
  deduplication:
    duplicates_removed, records_after_dedup
  screening_phase1:
    records_screened, excluded_phase1, included_phase1, unsure_phase1
  screening_phase2:
    fulltext_sought, fulltext_unavailable, fulltext_screened,
    excluded_phase2, included_final
"""

import json
import logging
import os

import pandas as pd

import config

logger = logging.getLogger(__name__)


def prisma_counts() -> dict:
    """Read all output CSVs and compute the PRISMA-ScR record counts.

    Returns a dict that is also written to config.PRISMA_JSON.
    Missing output files are skipped with a warning — run the upstream
    stage first to populate them.
    """
    counts: dict = {}

    # --- Identification ---
    id_counts: dict = {}
    for source, path in [
        ("pubmed", config.PUBMED_RAW_CSV),
        ("ieee", config.IEEE_RAW_CSV),
        ("wos", config.WOS_RAW_CSV),
    ]:
        if os.path.exists(path):
            n = len(pd.read_csv(path, usecols=["uid"]))
            id_counts[f"{source}_retrieved"] = n
        else:
            logger.warning("Missing %s — %s count set to None.", path, source)
            id_counts[f"{source}_retrieved"] = None
    totals = [v for v in id_counts.values() if v is not None]
    id_counts["total_retrieved"] = sum(totals) if totals else None
    counts["identification"] = id_counts

    # --- Deduplication ---
    dedup: dict = {}
    if os.path.exists(config.CORPUS_CSV):
        corpus = pd.read_csv(config.CORPUS_CSV, usecols=["is_duplicate"])
        dedup["duplicates_removed"] = int(corpus["is_duplicate"].sum())
        dedup["records_after_dedup"] = int((~corpus["is_duplicate"]).sum())
    else:
        logger.warning("Missing %s — dedup counts set to None.", config.CORPUS_CSV)
        dedup = {"duplicates_removed": None, "records_after_dedup": None}
    counts["deduplication"] = dedup

    # --- Phase 1 screening ---
    sc1: dict = {}
    if os.path.exists(config.SCREENING_CSV):
        s = pd.read_csv(config.SCREENING_CSV, usecols=["inclusion_status"])
        s["inclusion_status"] = pd.to_numeric(s["inclusion_status"], errors="coerce")
        sc1["records_screened"] = len(s)
        sc1["included_phase1"] = int((s["inclusion_status"] == 1).sum())
        sc1["excluded_phase1"] = int((s["inclusion_status"] == 0).sum())
        sc1["unsure_phase1"]   = int((s["inclusion_status"] == 2).sum())
    else:
        logger.warning("Missing %s — Phase 1 counts set to None.", config.SCREENING_CSV)
        sc1 = {k: None for k in ["records_screened", "included_phase1", "excluded_phase1", "unsure_phase1"]}
    counts["screening_phase1"] = sc1

    # --- Phase 2 charting (final inclusions) ---
    sc2: dict = {}
    if os.path.exists(config.CHARTING_CSV):
        n = len(pd.read_csv(config.CHARTING_CSV, usecols=["uid"]))
        sc2["included_final"] = n
    else:
        sc2["included_final"] = None
    counts["screening_phase2"] = sc2

    # Write JSON
    os.makedirs(os.path.dirname(config.PRISMA_JSON), exist_ok=True)
    with open(config.PRISMA_JSON, "w", encoding="utf-8") as fh:
        json.dump(counts, fh, indent=2)

    logger.info("PRISMA counts written to %s", config.PRISMA_JSON)
    return counts
