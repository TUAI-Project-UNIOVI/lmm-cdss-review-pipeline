# lmm-cdss-review-pipeline

Systematic review pipeline for **LMMs/LLMs in Clinical Decision Support Systems (CDSS)** — TUAI DC4 project. Covers metadata retrieval, preprocessing and pre-filtering, human screening, data extraction (charting), and PRISMA-ScR reporting.

## Pipeline overview

```
run_metadata.py  →  run_screening.py  →  run_charting.py  →  run_reporting.py
       ↓                   ↓                    ↓                    ↓
  metadata/           screening/           charting/            reporting/
  fetch/ + preprocessing/   SCREENING_GUIDE.md   charting.py         prisma.py
       ↓                                         irr.py              synthesis.py
  outputs/metadata/
  *_raw.csv + corpus.* + duplicate_map.csv
```

**Stage 1** (`run_metadata.py`) runs two substeps: fetch raw records per database (`--fetch-only`), then preprocess — concat, dedup, and generate corpus + duplicate map (`--corpus-only`). Run both in sequence or use the default (no flags) to do both in one call. **Stages 2–4** each read the previous stage's output and can be re-run independently.

## Quick start

```bash
# 0. Install dependencies
pip install -r requirements.txt

# 1. Stage 1 — fetch all sources then build corpus
python run_metadata.py

# Run substeps independently if needed:
python run_metadata.py --fetch-only --sources pubmed   # fetch PubMed only
python run_metadata.py --fetch-only --sources ieee wos # fetch IEEE + WoS only
python run_metadata.py --corpus-only                   # build corpus from existing raws

# 2. Stage 2 — human screening (see screening/SCREENING_GUIDE.md)
python run_screening.py

# 3. Stage 3 — charting template and IRR
python run_charting.py --template
python run_charting.py --irr --r1 outputs/charting_r1.csv --r2 outputs/charting_r2.csv

# 4. Stage 4 — PRISMA-ScR counts + synthesis figures
python run_reporting.py
```

Limit PubMed results for quick tests:

```bash
python run_metadata.py --fetch-only --sources pubmed --max 10
```

## Setup

### Prerequisites

```bash
pip install -r requirements.txt
```

### Environment variables

Set as persistent variables in `~/.bashrc` or `~/.profile`. IEEE and WoS use website exports — no API keys required for those.

| Key | Required for |
|---|---|
| `NCBI_API_KEY` | PubMed (raises rate limit 3 → 10 req/s) |
| `NCBI_EMAIL` | PubMed |
| `GEMINI_API_KEY` | Reserved for future screening assistance |

### Database exports (IEEE + WoS)

IEEE and WoS are loaded from files exported manually from each database's website. Place exports in the `data/` subfolders and update paths in `config.py` if filenames change.

| Database | Export format | Folder |
|---|---|---|
| IEEE Xplore | CSV (metadata) + BIB (references) | `data/ieee/` |
| Web of Science | RIS (Full Record, includes abstracts) | `data/wos/` |

**IEEE:** Website Command Search → export → CSV + BibTeX. Set `IEEE_EXPORT_CSV` and `IEEE_EXPORT_BIB` in `config.py`.

**WoS:** Website Advanced Search → Export → "Other Reference Software" → RIS → Full Record. Set `WOS_EXPORT_RIS` in `config.py`.

## Project structure

```
lmm-cdss-review-pipeline/
├── config.py                        ← queries, model IDs, all file paths
├── utils.py                         ← logging, ensure_output_dir, retry decorator
│
├── metadata/                        ← Stage 1 package
│   ├── fetch/                       ← Substep 1: raw retrieval per database
│   │   ├── pubmed.py                    PubMedFetcher (NCBI metapub API)
│   │   ├── ieee.py                      IEEEExportLoader (CSV + BIB)
│   │   └── wos.py                       WoSExportLoader (RIS via rispy)
│   └── preprocessing/               ← Substep 2: concat, dedup, pre-filter
│       ├── dedup.py                     deduplicate_corpus() — DOI exact + fuzzy title
│       └── prefilter.py                 *(pending)* SE1–SE4 automatic exclusions
│
├── screening/                       ← Stage 2: human reviewer resources
│   └── SCREENING_GUIDE.md               Gates 3–7 checklist for reviewers
│
├── charting/                        ← Stage 3
│   ├── charting.py                      ChartingForm — three-dimension extraction
│   └── irr.py                           compute_irr() — Cohen's κ + percent agreement
│
├── reporting/                       ← Stage 4
│   ├── prisma.py                        prisma_counts() → prisma_counts.json
│   └── synthesis.py                     generate_figures() — matplotlib/seaborn
│
├── run_metadata.py                  ← Stage 1 orchestrator (--fetch-only / --corpus-only / both)
├── run_screening.py                 ← Stage 2 entry point
├── run_charting.py                  ← Stage 3 entry point
├── run_reporting.py                 ← Stage 4 entry point
│
├── data/
│   ├── ieee/                        ← IEEE website exports
│   └── wos/                         ← WoS website export
│
├── outputs/                         ← generated files (gitignored)
│   └── metadata/                        Stage 1 outputs
│
├── review_execution_log.md          ← transparent record of all execution details
│                                        and AI-use log (PRISMA-trAIce source)
└── drafts/                          ← experimental scripts (not part of pipeline)
```

## Stage 1 outputs

All Stage 1 files are written to `outputs/metadata/`. Raw files are overwritten on each fetch run — back up with `cp -r outputs/metadata outputs/metadata_backup` before a full re-fetch.

| File | Produced by |
|---|---|
| `outputs/metadata/pubmed_raw.csv` | fetch — PubMed |
| `outputs/metadata/pubmed_clean.bib` | fetch — PubMed |
| `outputs/metadata/ieee_raw.csv` | fetch — IEEE |
| `outputs/metadata/ieee_clean.bib` | fetch — IEEE |
| `outputs/metadata/wos_raw.csv` | fetch — WoS |
| `outputs/metadata/wos_clean.bib` | fetch — WoS |
| `outputs/metadata/corpus.csv` | preprocessing — corpus builder |
| `outputs/metadata/corpus.xlsx` | preprocessing — corpus builder |
| `outputs/metadata/corpus.pkl` | preprocessing — corpus builder |
| `outputs/metadata/duplicate_map.csv` | preprocessing — one row per canonical record listing its duplicate corpus_ids |

The corpus includes all records. Every record has a `corpus_id` (sequential 1–N) and an `is_duplicate` flag. Duplicate records also have a `duplicate_of` field pointing to the canonical `corpus_id`. Filter unique records with `corpus[~corpus.is_duplicate]`.

## Inclusion / Exclusion criteria

Gates are split into two tiers:

| Tier | Codes | Applied by |
|---|---|---|
| Automatic pre-filter | SE1 (language), SE2 (date), SE3 (source type), SE4 (retraction) | `metadata/preprocessing/prefilter.py` *(pending)* |
| Human screening | PO1 (population), CO2 (concept — LLM core), CO3 (concept — CDSS function), CX4 (context), OT5 (other) | Reviewers — see `screening/SCREENING_GUIDE.md` |

Full execution details, exclusion counts, and deviations from protocol are recorded in `review_execution_log.md`.

## Rules

- `config.py` is the only file to edit for queries, paths, and model settings.
- Always test PubMed with `--max 10` before a full run.
- Every AI-assisted step is logged in `review_execution_log.md` for PRISMA-trAIce compliance.

## Funding

This project has received funding from the European Union under grant agreement No. 101168344 (HORIZON-MSCA-2023-DN-01). Views and opinions expressed are those of the authors only and do not necessarily reflect those of the European Union or the European Research Executive Agency.
