"""
Configuration for the TUAI review pipeline.
This is the only file to edit for queries, model settings, and output filenames.
"""

# ---------------------------------------------------------------------------
# Date range (single source of truth for all queries)
# ---------------------------------------------------------------------------

SEARCH_YEAR_START = 2024
SEARCH_YEAR_END   = 2026

# ---------------------------------------------------------------------------
# Search queries
#
# PubMed: single query used both by the API (run_fetch_metadata.py) and for
#   manual validation on https://pubmed.ncbi.nlm.nih.gov/
# IEEE:   website-only (Command Search mode); exported manually — no API.
#   Date filter: "Publication Year" sidebar after running the query.
#   URL: https://ieeexplore.ieee.org/search/advanced/command
# WoS:    website-only (Advanced Search, TI= title field); exported manually.
#   Interface: Web of Science Core Collection Advanced Search (institutional access required)
# ---------------------------------------------------------------------------

# PubMed (API + website — identical string)
PUBMED_QUERY = f"""
((
  "Decision Support Systems, Clinical"[MeSH Terms] OR
  "clinical decision*"[Title]
)
AND
(
  "large language model*"[Title] OR
  "large language*"[Title] OR
  "LLM"[Title] OR
  "LLMs"[Title] OR
  "large multimodal model*"[Title] OR
  "LMM"[Title] OR
  "LMMs"[Title]
)
AND
(
  "{SEARCH_YEAR_START}"[Date - Publication] : "{SEARCH_YEAR_END}"[Date - Publication]
)
AND
(
  English[Language]
))
"""

# IEEE Xplore (website export — paste into Command Search)
IEEE_QUERY = f"""
("Document Title":"large language model" OR "Document Title":"large language models" OR "Document Title":"LLM"
OR "Document Title":"LMMs" OR "Document Title":"large multimodal model")
AND ("Document Title":"clinical decision")
"""

# Web of Science (website export — paste into Advanced Search)
WOS_QUERY = (
    f'TI=("large language model*" OR "LLM" OR "LMMs" OR "large multimodal model*" OR "LMM") '
    f'AND TI=("clinical decision*") '
    f'AND PY=({SEARCH_YEAR_START}-{SEARCH_YEAR_END})'
)

# ---------------------------------------------------------------------------
# Search parameters
# ---------------------------------------------------------------------------

MAX_RESULTS = 999

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_RATE_LIMIT_SLEEP = 5  # seconds between calls

# ---------------------------------------------------------------------------
# Output filenames
# ---------------------------------------------------------------------------

# Stage 1 — metadata
PUBMED_RAW_CSV    = "outputs/metadata/pubmed_raw.csv"
PUBMED_BIB_OUT    = "outputs/metadata/pubmed_clean.bib"
IEEE_RAW_CSV      = "outputs/metadata/ieee_raw.csv"
IEEE_BIB_OUT      = "outputs/metadata/ieee_clean.bib"
IEEE_EXPORT_CSV   = "data/ieee/ieee_export_2026-06-18.csv"
IEEE_EXPORT_BIB   = "data/ieee/ieee_export_2026-06-18.bib"
WOS_RAW_CSV       = "outputs/metadata/wos_raw.csv"
WOS_BIB_OUT       = "outputs/metadata/wos_clean.bib"
WOS_EXPORT_RIS    = "data/wos/wos.ris"
CORPUS_CSV        = "outputs/metadata/corpus.csv"
CORPUS_XLSX       = "outputs/metadata/corpus.xlsx"
CORPUS_PKL        = "outputs/metadata/corpus.pkl"
FAILED_PMIDS_FILE = "outputs/metadata/failed_pmids.txt"

# Stage 1b — pre-filter
RETRACTION_WATCH_CSV = "data/retraction_watch.csv"
PREFILTER_COLS = ["SE1_language", "SE2_date", "SE3_pub_type", "SE4_retracted"]

# Stage 2 — screening
SCREENING_CSV    = "outputs/screening_results.csv"
SCREENING_XLSX   = "outputs/screening_results.xlsx"
SCREENING_PKL    = "outputs/screening_results.pkl"
FULLPAPER_CSV    = "outputs/fullpaper_summaries.csv"
FULLPAPER_XLSX   = "outputs/fullpaper_summaries.xlsx"

# Phase 1 screening outputs (used by make_bibtex.py)
PHASE1_APPEND_XLSX   = "screening/screening_phase1_append.xlsx"
PHASE1_DECISIONS_CSV = "outputs/screening/phase1_decisions.csv"
PHASE1_EXPECTED      = {"INCLUDE": 157, "EXCLUDE": 19, "TOTAL": 176}

# Phase 2 — BibTeX generation (make_bibtex.py)
NAMING_MAP_CSV       = "outputs/fulltext/naming_map.csv"
INCLUDES_BIB         = "outputs/fulltext/includes.bib"

# Stage 3 — charting
CHARTING_CSV     = "outputs/charting_results.csv"
CHARTING_XLSX    = "outputs/charting_results.xlsx"
IRR_CSV          = "outputs/irr_report.csv"

# Stage 4 — reporting
PRISMA_JSON      = "outputs/prisma_counts.json"
FIGURES_DIR      = "outputs/figures"

# ---------------------------------------------------------------------------
# Corpus CSV columns (contract between metadata → downstream stages)
# ---------------------------------------------------------------------------

CORPUS_COLUMNS = [
    "corpus_id",    # sequential integer assigned before dedup; stable across runs
    "duplicate_of", # corpus_id of canonical record this row duplicates; empty if unique
    "is_duplicate", # True if this row is a duplicate
    "source",       # "pubmed" | "ieee" | "wos"
    "uid",          # PMID / DOI / WoS accession number
    "title",
    "journal",
    "year",
    "authors",
    "doi",
    "keywords",
    "abstract",
    "url",
    "bibtex",
    "pub_type",
    # Stage 1b pre-filter flags (bool; False = passes / include)
    "SE1_language",
    "SE2_date",
    "SE3_pub_type",
    "SE4_retracted",
]
