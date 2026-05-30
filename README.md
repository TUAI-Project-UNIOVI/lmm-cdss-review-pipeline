# TUAI Review Scrapers

Systematic review pipeline for **LLMs in Clinical Decision Support Systems (CDSS)** — TUAI DC4 project. Covers metadata retrieval from three databases, abstract and full-text screening, data extraction (charting), and PRISMA-ScR reporting.

## Pipeline

```
run_metadata.py  →  run_screening.py  →  run_charting.py  →  run_reporting.py
     ↓                    ↓                    ↓                    ↓
 corpus.csv       screening_results.csv   charting_results.csv  prisma_counts.json
                                                                 outputs/figures/
```

Each stage reads the previous stage's CSV output. Stages can be re-run independently without re-running upstream steps.

## Quick Start

```bash
# 0. Install dependencies
pip install -r requirements.txt

# 1. Copy and fill in API keys
cp .env.example .env

# 2. Stage 1 — retrieve metadata from PubMed, IEEE Xplore, Web of Science
python run_metadata.py

# 3. Stage 2 — abstract screening (Phase 1) + full-paper reading aid (Phase 2)
python run_screening.py

# 4. Stage 3 — generate empty charting template for reviewers
python run_charting.py --template
# After reviewers complete the charting CSV:
python run_charting.py --file outputs/charting_results_r1.csv
# Compute IRR between two reviewers:
python run_charting.py --irr --r1 outputs/charting_r1.csv --r2 outputs/charting_r2.csv

# 5. Stage 4 — PRISMA-ScR counts + synthesis figures
python run_reporting.py
```

For quick tests, limit results before a full run:

```bash
python run_metadata.py --max 10
python run_metadata.py --pubmed-only --max 10
```

## Setup

### Prerequisites

```bash
pip install -r requirements.txt
```

### Environment variables

Copy `.env.example` to `.env` and fill in your keys:

| Key | Required for |
|---|---|
| `NCBI_API_KEY` | PubMed (raises rate limit 3 → 10 req/s) |
| `NCBI_EMAIL` | PubMed |
| `GEMINI_API_KEY` | Abstract + full-paper screening |
| `IEEE_API_KEY` | IEEE Xplore API |
| `WOS_API_KEY` | Web of Science API (optional — see WoS fallback below) |

`.env` and `outputs/` are gitignored — never commit them.

## Project Structure

```
TUAI_review_scrapers/
├── config.py                   ← queries, model IDs, output filenames — only file to edit for new searches
├── utils.py                    ← logging, ensure_output_dir, retry decorator
│
├── metadata/
│   ├── pubmed.py               ← PubMedScraper (NCBI metapub)
│   ├── ieee.py                 ← IEEEScraper (IEEE Xplore API)
│   └── wos.py                  ← WoSScraper (API) + WoSExportLoader (manual TSV fallback)
│
├── dedup.py                    ← deduplicate_corpus() — DOI exact + fuzzy title dedup
│
├── screening/
│   ├── abstract_screen.py      ← AbstractScreener — Gemini Phase 1 structured screening
│   └── fullpaper_screen.py     ← FullPaperScreener — Phase 2 reading-aid summaries
│
├── charting/
│   ├── charting.py             ← ChartingForm — three-dimension extraction template
│   └── irr.py                  ← compute_irr() — Cohen's κ + percent agreement
│
├── reporting/
│   ├── prisma.py               ← prisma_counts() → prisma_counts.json
│   └── synthesis.py            ← generate_figures() — matplotlib/seaborn figures
│
├── run_metadata.py             ← Stage 1 entry point
├── run_screening.py            ← Stage 2 entry point
├── run_charting.py             ← Stage 3 entry point
├── run_reporting.py            ← Stage 4 entry point
│
├── data/                       ← static input files
├── outputs/                    ← all generated files (gitignored)
├── drafts/                     ← legacy scripts and experimental code
├── .env.example
└── requirements.txt
```

## Inclusion / Exclusion Criteria

**Include** (all must hold): paper features an LLM/LMM as a core component that directly supports a clinical decision (diagnosis, treatment, triage, etc.). Systematic reviews and framework papers on these applications are included.

**Exclude** (any one triggers exclusion):

| Flag | Description |
|---|---|
| `is_genomic` | Primary focus on genomics or molecular biology |
| `is_mental_health` | Primary focus on mental health or psychiatry |
| `is_dentistry` | Primary focus on dentistry or oral health |
| `is_pediatric` | Primary focus on paediatric patients |
| `is_cadaver` | Involves cadaver studies |
| `is_no_LLM` | No LLM/LMM as a core component |
| `is_no_cds` | No direct clinical decision support |

Criteria are operationalised in the system prompt inside `screening/abstract_screen.py` and must stay in sync with `@ptx` §2 (PCC).

## WoS Fallback

If the WoS API key is unavailable, export results manually from the Web of Science UI (Save to → Tab-delimited, UTF-8, Full Record) and pass the file path:

```bash
python run_metadata.py --wos-export path/to/wos_export.txt
```

## Rules

- No hardcoded paths or queries — `config.py` only.
- Always test with `--max 10` before a full run.
- After modifying screening criteria, update both the exclusion flags table above and the system prompt in `screening/abstract_screen.py`.
- Every LLM use is logged in `outputs/screening_results.csv` (column: `screen_date`) for PRISMA-trAIce compliance (App F of the manuscript).
