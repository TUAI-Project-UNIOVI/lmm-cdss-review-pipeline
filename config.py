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
# Database queries (locked strings from @ptx §3.2.2)
# ---------------------------------------------------------------------------

PUBMED_QUERY = f"""
((
  "Decision Support Systems, Clinical"[MeSH Terms] OR
  "clinical decision*"[Title/Abstract] 
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
  "{SEARCH_YEAR_START}"[Date - Publication] : "{SEARCH_YEAR_END}"[Date - Publication]
)
AND
(
  English[Language]
))
"""

PUBMED_QUERY_TITLE_ONLY = f"""
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

IEEE_QUERY = (
    '("large language model" OR "large language models" OR "LLM" OR "LMMs" OR "large multimodal model") '
    'AND ("clinical decision support" OR "CDSS")'
)

WOS_QUERY = (
    f'TS=("large language model*" OR "LLM" OR "LMMs" OR "large multimodal model*" OR "LMM") '
    f'AND TS=("clinical decision support" OR "CDSS") '
    f'AND PY=({SEARCH_YEAR_START}-{SEARCH_YEAR_END})'
)

# ---------------------------------------------------------------------------
# Website versions — paste these directly into each database's search box
# for manual validation. Not used by the pipeline.
# ---------------------------------------------------------------------------

# PubMed — paste into https://pubmed.ncbi.nlm.nih.gov/
PUBMED_QUERY_WEBSITE = f"""
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
  "{SEARCH_YEAR_START}"[Date - Publication] : "{SEARCH_YEAR_END}"[Date - Publication]
)
AND
(
  English[Language]
))
"""

# PubMed title-only variant — same as above but restricts CDSS term to [Title] only
PUBMED_QUERY_TITLE_ONLY_WEBSITE = f"""
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

# IEEE Xplore — paste into https://ieeexplore.ieee.org/search/searchresult.jsp
# Use "Command Search" mode.
# Date filter: apply via the "Publication Year" sidebar filter after running the query.
IEEE_QUERY_WEBSITE = f"""
("Document Title":"large language model" OR "Document Title":"large language models" OR "Document Title":"LLM"
OR "Document Title":"LMMs" OR "Document Title":"large multimodal model")
AND ("Document Title":"clinical decision" )
"""

# IEEE title + abstract variant
IEEE_QUERY_TITLE_ABSTRACT_WEBSITE = f"""
(
  "Document Title":"large language model" OR "Document Title":"large language models" OR
  "Document Title":"LLM" OR "Document Title":"LMMs" OR "Document Title":"large multimodal model" OR
  "Abstract":"large language model" OR "Abstract":"large language models" OR
  "Abstract":"LLM" OR "Abstract":"LMMs" OR "Abstract":"large multimodal model"
)
AND
(
  "Document Title":"clinical decision" OR
  "Abstract":"clinical decision"
)
"""



# Web of Science — paste into https://www.webofscience.com/wos/woscc/advanced-search
# Use Advanced Search with TS= (Topic) field tags. Date filter via PY= operator.
WOS_QUERY_WEBSITE = (
    f'TS=("large language model*" OR "LLM" OR "LMMs" OR "large multimodal model*" OR "LMM") '
    f'AND TS=("clinical decision") '
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
