"""
Configuration for the TUAI review pipeline.
This is the only file to edit for queries, model settings, and output filenames.
"""

# ---------------------------------------------------------------------------
# Database queries (locked strings from @ptx §3.2.2)
# ---------------------------------------------------------------------------

PUBMED_QUERY = """
((
  "Decision Support Systems, Clinical"[MeSH Terms] OR
  "clinical decision support system*"[Title/Abstract] OR
  "CDSS"[Title/Abstract]
)
AND
(
  "large language model*"[Title/Abstract] OR
  "large language*"[Title/Abstract] OR
  "LLM"[Title/Abstract] OR
  "LLMs"[Title/Abstract] OR
  "large multimodal model*"[Title/Abstract] OR
  "LMM"[Title/Abstract] OR
  "LMMs"[Title/Abstract]
)
AND
(
  "2023"[Date - Publication] : "2026"[Date - Publication]
)
AND
(
  English[Language]
))
"""

IEEE_QUERY = (
    '("Abstract":"large language model" OR "Abstract":"large language models" OR '
    '"Abstract":"LLM" OR "Abstract":"LMMs" OR "Abstract":"large multimodal model") AND '
    '("Abstract":"clinical decision support" OR "Abstract":"CDSS")'
)

WOS_QUERY = (
    'TS=("large language model*" OR "LLM" OR "LMMs" OR "large multimodal model*" OR "LMM") '
    'AND TS=("clinical decision support" OR "CDSS")'
)

# ---------------------------------------------------------------------------
# Search parameters
# ---------------------------------------------------------------------------

MAX_RESULTS = 1000

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_RATE_LIMIT_SLEEP = 5  # seconds between calls

# ---------------------------------------------------------------------------
# Output filenames
# ---------------------------------------------------------------------------

# Stage 1 — metadata
PUBMED_RAW_CSV   = "outputs/pubmed_raw.csv"
IEEE_RAW_CSV     = "outputs/ieee_raw.csv"
WOS_RAW_CSV      = "outputs/wos_raw.csv"
CORPUS_CSV       = "outputs/corpus.csv"
CORPUS_XLSX      = "outputs/corpus.xlsx"
CORPUS_PKL       = "outputs/corpus.pkl"
FAILED_PMIDS_FILE = "outputs/failed_pmids.txt"

# Stage 2 — screening
SCREENING_CSV    = "outputs/screening_results.csv"
SCREENING_XLSX   = "outputs/screening_results.xlsx"
SCREENING_PKL    = "outputs/screening_results.pkl"
FULLPAPER_CSV    = "outputs/fullpaper_summaries.csv"
FULLPAPER_XLSX   = "outputs/fullpaper_summaries.xlsx"

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
    "source",       # "pubmed" | "ieee" | "wos"
    "uid",          # PMID / accession number / WoS UT
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
    "is_duplicate",
]
