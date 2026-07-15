# lmm-cdss-review-pipeline

Systematic review pipeline for **LMMs/LLMs in Clinical Decision Support Systems (CDSS)** — TUAI DC4 project. Covers metadata retrieval, preprocessing and pre-filtering, human screening (Phase 1 title/abstract and Phase 2 full text), and full-text retrieval.

Charting and reporting (data extraction, PRISMA-ScR counts, synthesis figures) are future stages, not yet built — see `../claude_docs/pipeline_guide.md` for the full stage roadmap and current status.

## Pipeline overview

```
run_metadata.py            →  screening/ (manual)          →  run_fulltext_retrieval.py  →  screening/ (manual)
       ↓                           ↓                                  ↓                            ↓
  metadata/                  Phase 1 screening              papers_library/               Phase 2 screening
  fetch/ + preprocessing/    screening_phase1_*.xlsx        fulltext_retrieved/           screening_phase2_*.xlsx
       ↓                     SCREENING_GUIDE.md
  outputs/metadata/
  *_raw.csv + corpus.csv + duplicate_map.csv
```

**Stage 1** (`run_metadata.py`) runs two substeps: fetch raw records per database (`--fetch-only`), then preprocess — concat, dedup, apply the automatic pre-filter (SE1–SE4), and generate corpus + duplicate map (`--corpus-only`). Run both in sequence or use the default (no flags) to do both in one call.

**Phase 1 screening** (title/abstract) and **Phase 2 screening** (full text) are manual reviewer processes — see `screening/SCREENING_GUIDE.md`, the canonical reference for both phases.

**Full-text retrieval** (`run_fulltext_retrieval.py`) downloads open-access PDFs for every Phase 1 include, trying PMC Open Access then Unpaywall; anything not retrievable automatically goes to a manual worklist.

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

# 2. Phase 1 — human screening (see screening/SCREENING_GUIDE.md)
#    Reviewers fill screening_phase1_R1.xlsx / R2.xlsx by hand.

# 3. Full-text retrieval for Phase 1 includes
python run_fulltext_retrieval.py                 # full run over all includes
python run_fulltext_retrieval.py --only 5 12 40  # subset (smoke testing)
python run_fulltext_retrieval.py --rescan        # no network: fold manually
                                                  # downloaded PDFs back into the log

# 4. Generate BibTeX for included studies
python make_bibtex.py

# 5. Phase 2 — human screening (see screening/SCREENING_GUIDE.md § Phase 2)
python make_phase2_screening.py                  # (re)generate empty R1/R2/append workbooks
#    Reviewers fill screening_phase2_R1.xlsx / R2.xlsx by hand.
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
| `NCBI_EMAIL` | PubMed; also required by `run_fulltext_retrieval.py` (NCBI ID Converter) |
| `UNPAYWALL_EMAIL` | `run_fulltext_retrieval.py` Unpaywall lookups (falls back to `NCBI_EMAIL` if unset) |
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
├── naming.py                        ← standard_name() — canonical PDF filename / BibTeX key
│
├── metadata/                        ← Stage 1 package
│   ├── fetch/                       ← Substep 1: raw retrieval per database
│   │   ├── pubmed.py                    PubMedFetcher (NCBI metapub API)
│   │   ├── ieee.py                      IEEEExportLoader (CSV + BIB)
│   │   └── wos.py                       WoSExportLoader (RIS via rispy)
│   └── preprocessing/               ← Substep 2: concat, dedup, pre-filter
│       ├── dedup.py                     deduplicate_corpus() — DOI exact + fuzzy title
│       └── prefilter.py                 SE1–SE4 automatic exclusions
│
├── screening/                       ← Phase 1 + Phase 2: human reviewer resources
│   ├── SCREENING_GUIDE.md               Canonical reference for both phases (PO1, CO2, CO3, CX4, OT5 + Phase 2 GA1/GA5/GA7)
│   ├── reviewer_guide.md                Phase 1 reviewer instructions
│   ├── screening_phase1_R1/R2.xlsx      Phase 1 reviewer worksheets
│   ├── screening_phase1_append.xlsx     Phase 1 compiled results (R1 + R2 + discussion) — 157 IN / 19 EX
│   ├── screening_phase2_R1/R2.xlsx      Phase 2 reviewer worksheets (full-text)
│   └── screening_phase2_append.xlsx     Phase 2 compiled results (R1 + R2 + discussion)
│
├── run_metadata.py                  ← Stage 1 orchestrator (--fetch-only / --corpus-only / both)
├── run_fulltext_retrieval.py        ← Full-text retrieval for Phase 1 includes (PMC OA, Unpaywall, manual worklist)
├── make_phase2_screening.py         ← Generates Phase 2 screening workbooks from the retrieval summary
├── make_bibtex.py                   ← Generates naming_map.csv + includes.bib for Phase 1 includes
│
├── data/
│   ├── ieee/                        ← IEEE website exports
│   └── wos/                         ← WoS website export
│   └── retraction_watch.csv         ← Retraction Watch DOI database (gitignored)
│
├── outputs/                         ← generated files (gitignored)
│   ├── metadata/                        Stage 1 outputs
│   ├── screening/                       Phase 1 decision extract (phase1_decisions.csv)
│   └── fulltext/                        Retrieval log, manual worklist, naming map, includes.bib
│
├── review_execution_log.md          ← transparent record of all execution details
│                                        and AI-use log (PRISMA-trAIce source)
└── drafts/mute/                     ← no-traceability zone; never reference elsewhere (gitignored)
```

`papers_library/fulltext_retrieved/` (retrieved PDFs) lives one level **above** this pipeline folder, at `../papers_library/fulltext_retrieved` — not inside `lmm-cdss-review-pipeline/`.

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
| `outputs/metadata/duplicate_map.csv` | preprocessing — one row per canonical record listing its duplicate corpus_ids |

The corpus includes all records. Every record has a `corpus_id` (sequential 1–N) and an `is_duplicate` flag. Duplicate records also have a `duplicate_of` field pointing to the canonical `corpus_id`. Filter unique records with `corpus[~corpus.is_duplicate]`.

## Full-text retrieval outputs

Written to `outputs/fulltext/` by `run_fulltext_retrieval.py`:

| File | Content |
|---|---|
| `retrieval_log.csv` | One row per Phase 1 include: status (`retrieved` / `manual_needed`), method, file path |
| `manual_worklist.xlsx` | Records not retrieved automatically, with candidate URLs for hand retrieval |

PDFs land in `../papers_library/fulltext_retrieved/`, named `{Surname}{Year}_{corpus_id}_{title-words}.pdf` (see `naming.py`). Sources tried, in order: PMC Open Access subset (PMCID resolved via the NCBI ID Converter), then Unpaywall. Anything neither source can fetch goes to the manual worklist for retrieval via institutional access.

## Inclusion / Exclusion criteria

Gates are split into two tiers:

| Tier | Codes | Applied by |
|---|---|---|
| Automatic pre-filter | SE1 (language), SE2 (date), SE3 (source type), SE4 (retraction) | `metadata/preprocessing/prefilter.py` |
| Human screening | PO1 (population), CO2 (concept — LLM core), CO3 (concept — CDSS function), CX4 (context), OT5 (other) | Reviewers — see `screening/SCREENING_GUIDE.md` |

Full execution details, exclusion counts, and deviations from protocol are recorded in `review_execution_log.md`.

## Rules

- `config.py` is the only file to edit for queries, paths, and model settings.
- Always test PubMed with `--max 10` before a full run.
- Every AI-assisted step is logged in `review_execution_log.md` for PRISMA-trAIce compliance.
- `drafts/mute/` is a no-traceability zone (gitignored) — never reference its contents in commit messages, `review_execution_log.md`, or any other project document.

## Funding

This project has received funding from the European Union under grant agreement No. 101168344 (HORIZON-MSCA-2023-DN-01). Views and opinions expressed are those of the authors only and do not necessarily reflect those of the European Union or the European Research Executive Agency.
