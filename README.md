# TUAI Review Scrapers

Automated pipeline for literature retrieval and screening for the **TUAI DC4** systematic review project. The review focuses on the use of **Large Language Models (LLMs) in Clinical Decision Support Systems (CDSS)**.

## Overview

This project implements a multi-stage systematic review pipeline:

1. **Search & Scrape** — Query PubMed and retrieve article metadata
2. **Abstract Screening** — Use the Gemini AI API to automatically screen abstracts against inclusion/exclusion criteria
3. **Full Paper Analysis** — Parse and consolidate full-paper analysis results (e.g., from NotebookLM)

## Pipeline Stages

### Stage 1 — PubMed Scraping (`main.py` + `scraper.py`)

Queries PubMed via the NCBI API and saves article metadata to CSV, Excel, and pickle files.

**Current search query targets:**
- Papers mentioning LLMs (`large language*`, `LLM*`)
- In the context of Clinical Decision Support Systems (`CDSS`, MeSH terms)
- Published 2010–2025, in English, with free full text available

**Output fields:** PMID, Title, Journal, Year, Authors, DOI, Keywords, Abstract, URL, BibTeX, Publication Type

### Stage 2 — Abstract Screening (`screening.py`)

Uses the **Google Gemini API** (`gemini-2.5-flash`) to automatically screen abstracts against predefined criteria and outputs structured JSON decisions.

**Inclusion criteria (ALL must be met):**
- Features an LLM as a core component
- LLM directly supports a clinical decision (diagnosis, treatment, triage, etc.)
- Systematic reviews and framework papers on these applications are included

**Exclusion criteria (ANY triggers exclusion):**
| Flag | Description |
|---|---|
| `is_genomic` | Primary focus on genomics/molecular biology |
| `is_mental_health` | Primary focus on mental health/psychiatry |
| `is_dentistry` | Primary focus on dentistry/oral health |
| `is_pediatric` | Primary focus on pediatric patients |
| `is_cadaver` | Involves cadaver studies |
| `is_no_LLM` | No LLM as a core component |
| `is_no_cds` | No direct clinical decision support |

**Output per article:** `inclusion_status` (1=Include, 0=Exclude, 2=Unsure), `exclusion_reasons` flags, and `observations`.

### Stage 3 — Full Paper Analysis (`full_paper_analysis.py`)

Parses multi-entry JSON output files (e.g., from NotebookLM manual analysis) delimited by `---END---` and loads them into a DataFrame for further processing.

## Project Structure

```
TUAI_review_scrapers/
├── config.py               # Search query, filenames, and CSV column definitions
├── main.py                 # Entry point: runs PubMed scraping
├── scraper.py              # PubMedScraper class (NCBI API logic)
├── screening.py            # Abstract screening via Gemini API
├── full_paper_analysis.py  # Full-paper analysis result parser
├── data/                   # Raw input data (e.g., NotebookLM analysis text files)
└── outputs/                # All generated output files
```

## Setup

### Prerequisites

```bash
pip install metapub tqdm google-generativeai python-dotenv pandas openpyxl joblib
```

### Environment Variables

Create a `.env` file in the project root:

```env
NCBI_API_KEY=your_ncbi_api_key
NCBI_EMAIL=your_email@example.com
GEMINI_API_KEY=your_gemini_api_key
```

- **NCBI API key**: Register at [NCBI](https://www.ncbi.nlm.nih.gov/account/) (increases rate limit from 3 to 10 requests/second)
- **Gemini API key**: Obtain from [Google AI Studio](https://aistudio.google.com/)

<!-- Test comment: README last reviewed 2026-03-18 -->

## Usage

### 1. Configure the search

Edit [config.py](config.py) to adjust the PubMed query, `MAX_RESULTS`, and output filenames.

### 2. Run the scraper

```bash
python main.py
```

Outputs: `outputs/pubmed_results.csv`, `outputs/pubmed_results.xlsx`, `outputs/pubmed_results.pkl`

### 3. Run abstract screening

```bash
python screening.py
```

Outputs: `outputs/gemini_analysis_results.csv`, `outputs/gemini_analysis_results.xlsx`, `outputs/gemini_analysis_results.joblib`

### 4. Parse full-paper analysis

Place your NotebookLM (or similar) analysis results in `data/notebook_LM_analysis.txt`, separated by `---END---`, then run:

```bash
python full_paper_analysis.py
```
