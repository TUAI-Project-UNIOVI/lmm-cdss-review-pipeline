# Review Execution Log

**Review title:** Large Multimodal Model-Driven Clinical Decision Support Systems: Mapping Architectures to Decision Requirements — A Scoping Review

**OSF registration:** https://doi.org/10.17605/OSF.IO/K7CDY

**Purpose of this document:** Transparent record of all methodological decisions, execution details, and AI-assisted steps across every stage of the review. Serves as the source of truth for Appendix C (Search Execution Log) and Appendix F (AI-Use Log / PRISMA-trAIce) in the final manuscript.

---

## Stage 1 — Search and Corpus Assembly

### Search scope

**Field restriction:** Title-only across all three databases.

**Rationale for title-only scope.** The decision to restrict search terms to title fields — rather than the more common title and abstract (tiab) combination — was made after a preliminary scoping run and is grounded in both methodological and practical considerations that align with accepted scoping review practice.

**Preliminary scoping results.** An initial title-and-abstract search produced a combined pool of approximately 3,760 records (PubMed: 1,497; IEEE Xplore: 186; Web of Science: 2,077). Inspection of a random sample of those records revealed a consistent pattern: a large proportion mentioned LLM or clinical decision support in the abstract only as background framing, related work, or a secondary observation, without the study being substantively about LLM-driven clinical decision support. Screening that volume of records with two independent human reviewers, as required by JBI methodology, would have been operationally infeasible within the project timeline and would have introduced a disproportionate burden relative to the expected yield of genuinely in-scope studies.

**Methodological grounding.** Restricting terms to the title is a recognised precision strategy in systematic and scoping reviews, particularly in fast-moving fields where abstract language is loose and indexing is inconsistent. Peters et al. (2020, JBI Manual for Scoping Reviews) and Arksey and O'Malley (2005) are explicit that scoping reviews aim to map a defined conceptual space rather than achieve exhaustive retrieval. A paper whose primary contribution is LLM-driven clinical decision support will almost invariably reflect that in the title; a paper that only mentions these terms in the abstract is unlikely to be a core contribution to the field this review intends to map. The title-only restriction is therefore a principled scope-definition decision, not an omission.

**Distinction from sampling.** This strategy does not constitute statistical sampling of the literature. All records meeting the defined scope criteria — as signalled by their title — are retrieved and considered for inclusion. Papers excluded by the title-field restriction are outside the defined scope of this review, not missed members of a target population. This framing is consistent with the PRISMA-ScR guidance on transparent reporting of search constraints (Tricco et al., 2018).

**Corpus adequacy.** The resulting corpus of 212 unique records after deduplication represents a substantive and coherent basis for the mapping exercise. LLM-driven clinical decision support is a recent and rapidly consolidating field (literature concentrated from 2023 onwards); a corpus of this size, drawn from three complementary databases with distinct indexing strengths, is sufficient to characterise the main architectural patterns, clinical deployment contexts, and evidence gaps that constitute the review's four specific aims. The transparency and reproducibility of every step — exact strings, execution dates, rationale, and record counts documented here — provides the methodological accountability required by JBI and PRISMA-ScR standards regardless of the field restriction applied.

**Date range covered:** 2024–2026 (all databases).

**Language restriction:** English only. Applied via inline filter in PubMed; applied manually via website sidebar in IEEE Xplore and Web of Science (see per-database notes below).

### Execution summary

| Database | Execution date | Records retrieved | Duplicates removed | Unique records | Forwarded to Title/Abstract Screening (post SE1–SE4) |
|---|---|---|---|---|---|
| PubMed | 2026-06-18 | 164 | 2 | 162 | 152 |
| IEEE Xplore | 2026-06-18 | 13 | 1 | 12 | 12 |
| Web of Science | 2026-06-18 | 143 | 105 | 38 | 12 |
| **Total** | | **320** | **108** | **212** | **176** |

Deduplication applied in two passes: (1) exact DOI match; (2) fuzzy title match (RapidFuzz ≥ 92 similarity score, same publication year). Source priority when a duplicate is retained: PubMed > IEEE > WoS — duplicates are attributed to the lower-priority source, which is why Web of Science absorbs most of the duplicate count. The final column reflects the corpus after the Stage 2 automatic pre-filter (SE1–SE4, see below).

### Search strings

#### PubMed

**Interface:** NCBI PubMed API (`metapub`) + manual validation at https://pubmed.ncbi.nlm.nih.gov/

**String:**

```
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
  "2024"[Date - Publication] : "2026"[Date - Publication]
)
AND
(
  English[Language]
))
```

**Notes:** MeSH term `"Decision Support Systems, Clinical"` provides controlled-vocabulary coverage; `"clinical decision*"` in title covers variations not yet indexed under MeSH. Truncation (`*`) supported in `[Title]` field. Date and language constraints embedded directly in the string.

#### IEEE Xplore

**Interface:** Website Command Search — https://ieeexplore.ieee.org/search/advanced/command

**String:**

```
("Document Title":"large language model" OR "Document Title":"large language models" OR "Document Title":"LLM"
OR "Document Title":"LMMs" OR "Document Title":"large multimodal model")
AND ("Document Title":"clinical decision")
```

**Notes:** IEEE Command Search does not support truncation wildcards in `"Document Title":` syntax; `"large language model"` and `"large language models"` are therefore listed as separate literals. The search string itself contains no date or language constraints — both were applied manually as website sidebar filters after running the string: "Publication Year" set to 2024–2026, language set to English. Results exported as CSV (metadata) and BibTeX from the website UI.

#### Web of Science

**Interface:** Web of Science Core Collection — Advanced Search (institutional access required)

**String:**

```
TI=("large language model*" OR "LLM" OR "LMMs" OR "large multimodal model*" OR "LMM")
AND TI=("clinical decision*")
AND PY=(2024-2026)
```

**Notes:** `TI=` restricts to title field only. `*` truncation supported. Date filter embedded in the string via `PY=` operator. Language (English) is not available as an inline operator in WoS Advanced Search and was applied manually as a sidebar filter ("English" under Languages) after running the string. Results exported as RIS (Full Record, includes abstracts) from the website UI.

### Retrieval method

| Database | Method |
|---|---|
| PubMed | NCBI E-utilities API via `metapub` Python library (`run_metadata.py --fetch-only --sources pubmed`) |
| IEEE Xplore | Manual website export → CSV + BIB files loaded by `IEEEExportLoader` |
| Web of Science | Manual website export → RIS file loaded by `WoSExportLoader` via `rispy` |

Pipeline version: `lmm-cdss-review-pipeline` — see commit history for exact code state at execution date.

### Deviations from registered protocol

- None at this stage.

---

## Stage 2 — Pre-filtering (Automatic codes SE1–SE4)

**Status: completed 2026-06-25.**

Automated exclusions applied to the deduplicated corpus before records are forwarded to human reviewers. Codes SE1–SE4 correspond to the Sources & Evidence dimension of the PCC framework (§2.4.4 of the protocol) and require no reviewer judgment — they operate entirely on corpus metadata fields.

Implemented in `metadata/preprocessing/prefilter.py`. Applied via `run_metadata.py --corpus-only` on 2026-06-25. All exclusion flags and the resulting record counts were confirmed and revised by the pipeline author to verify the quality of the executed code (see AI-Use Log entry 2). Exclusions logged with the codes below.

### SE1 — Language not English

| Code | Condition |
|---|---|
| `SE1` | Language field is not English |

**Note for this corpus:** English was enforced at search time — embedded in the PubMed string and applied as a website sidebar filter for IEEE and WoS. SE1 serves as a post-hoc integrity check; no exclusions are expected unless an export contained stray records.

### SE2 — Outside date range 2024–2026

| Code | Condition |
|---|---|
| `SE2` | Publication year outside 2024–2026 |

**Note for this corpus:** Date range was enforced at search time for all three databases. SE2 serves as a post-hoc integrity check.

### SE3 — Not peer-reviewed source type

| Code | Condition |
|---|---|
| `SE3` | Record is not a peer-reviewed journal article, conference paper, or published systematic/scoping review |

**Grey literature exception:** Pre-prints identified through backward citation snowballing bypass SE3 and enter human screening directly at PO1. These are tracked separately.

### SE4 — Retraction check

| Code | Condition |
|---|---|
| `SE4` | Paper has been retracted |

**Method:** Cross-reference corpus DOIs against the Retraction Watch database CSV (freely available at retractionwatch.com; local copy `data/retraction_watch.csv`, 61,632 retracted DOIs as of download date). DOI match (case-insensitive) flags the record as `SE4_retracted = True`.

**Status:** Applied 2026-06-25 — 0 matches in current corpus.

### Pre-filter results

| Code | Records excluded | Notes |
|---|---|---|
| SE1 — Language | 1 | Lithuanian-language paper detected via `langdetect` on title+abstract (lowercased) |
| SE2 — Date range | 0 | Date enforced at search time; post-hoc integrity check passed |
| SE3 — Source type | 35 | Editorials (PubMed), letters (PubMed), meeting abstracts and editorial material (WoS); 1 record excluded by both SE1 and SE3 |
| SE4 — Retraction | 0 | Cross-referenced against Retraction Watch (61,632 DOIs); no matches |
| **Records forwarded to Title/Abstract Screening** | **176** | 212 unique − 36 excluded (union of SE1–SE4) |

> For the human reviewer checklist (codes PO1, CO2, CO3, CX4, OT5), see [`screening/SCREENING_GUIDE.md`](screening/SCREENING_GUIDE.md).

---

## Stage 3 — Title/Abstract Screening

**Status: completed 2026-07-13.**

Two reviewers (R1, R2) independently assessed all 176 records by title and abstract against the PCC checklist codes (PO1, CO2, CO3, CX4, OT5 — see [`screening/SCREENING_GUIDE.md`](screening/SCREENING_GUIDE.md)), then resolved every disagreement by joint discussion.

**Evidence of execution:** [`screening/screening_phase1_append.xlsx`](screening/screening_phase1_append.xlsx) — compiled workbook with three blocks per record: R1's independent assessment (checklist flags, decision, rationale, borderline flag), R2's independent assessment (same structure), and Discussion Results (disagreement flag, final decision, discussion rationale).

| Metric | Count |
|---|---|
| Records entering Title/Abstract Screening | 176 |
| Included at Step A (both reviewers agree include) | 152 |
| Excluded at Step A (both reviewers agree exclude) | 12 |
| Disagreements forwarded to Step B discussion | 12 |
| Included after Step B discussion | 5 (of 12; the other 7 excluded) |
| **Total forwarded to Full-Text Screening** | **157** |

**Step A — Independent Screening.** R1: 157 include / 19 exclude. R2: 159 include / 17 exclude. Observed agreement: 164/176 records (93.2%).

**Step B — Reviewer Discussion.** All 12 disagreements (corpus_ids 16, 44, 52, 58, 68, 77, 84, 94, 148, 150, 159, 177) were resolved by discussion; no conflict remained unresolved, so the include-by-default rule was never invoked.

**Borderline flags.** 27 records were flagged as borderline by at least one reviewer (R1: 5, R2: 24). Flags are preserved in the workbook (`Final Borderline` column) so these records receive priority attention during full-text screening.

**Grey areas.** Recurring CO3 boundary cases surfaced during screening — LLM-as-CDSS-builder, partial decisions in a decision cascade, monitoring/alert systems, LLM as pipeline component, LLM as knowledge-maintenance layer, papers that evaluate rather than constitute an LLM-CDSS, and the underlying definition of "clinical decision." These are registered as grey areas GA1–GA8 in `binnacle.md` § Full-Text Review Preparation; resolved rules will be codified into the Phase 2 (full-text) reviewer guide before Stage 4 starts.

---

## Stage 4 — Full-Text Retrieval and Screening

**Status: retrieval completed 2026-07-14; screening in progress.**

### Full-Text Retrieval

**Execution method:** Two-phase retrieval combining automated download and manual access via university account.

| Phase | Method | Records Retrieved | Success Rate |
|---|---|---|---|
| Automated retrieval | IEEE API, PMC OA, Unpaywall (`run_fulltext_retrieval.py`) | 57/157 | 36.3% |
| Manual retrieval | University account institutional access | 91/100 | 91.0% |
| **Total retrieved** | | **148/157** | **94.3%** |
| **Not accessible** | Despite institutional credentials | **9/157** | **5.7%** |

**Papers not accessible (Corpus IDs):** 122, 10, 27, 37, 62, 98, 125, 142, 144

**Retrieval log:** [`outputs/fulltext_retrieval_log.md`](outputs/fulltext_retrieval_log.md) and [`fulltext_retrieval_log.md`](fulltext_retrieval_log.md) — documents exact access attempts and reasoning.

**Exclusion rationale:** Per PRISMA 2020 and JBI methodology, papers excluded due to full-text inaccessibility are documented as a distinct exclusion category at the full-text screening stage. This is a recognized practical limitation in systematic and scoping reviews. Documented access attempts satisfy reporting standards.

### Full-Text Screening

*To be completed after full-text review.*

| Metric | Count |
|---|---|
| Records entering Full-Text Screening | 157 |
| Full text not retrievable (access exclusion) | 9 |
| Records available for screening | 148 |
| Excluded at Step A (both reviewers agree exclude) | — |
| Disagreements forwarded to Step B discussion | — |
| Included after Step B discussion | — |
| **Final included studies** | — |

**Step A — Independent Screening.** Two reviewers independently read each full-text record; AI reading-aid tools permitted per PRISMA-trAIce, decision authority remains human.
**Step B — Reviewer Discussion.** Records not resolved by agreement in Step A go to joint discussion; unresolved conflicts default to include.

---

## Stage 5 — Backward Citation Snowballing

*To be completed after Stage 4 produces the final included-studies corpus, before charting.*

One level of backward snowballing (per `@ptx`/`@mtx` §2.5.3/§3.2.3) over the reference lists of the final included studies. Forward snowballing is not performed (rationale: 2024–2026 window, insufficient citation accumulation). This step is the safety net supporting the arXiv/grey-literature exclusion rationale (§2.4) — do not skip.

**Planned streamlining:** fetch reference lists programmatically by DOI (OpenAlex / Semantic Scholar), auto-exclude pre-2024 records and records already in the corpus, then human-screen only the residual shortlist against PCC criteria (not a manual skim of every reference list).

| Metric | Count |
|---|---|
| Reference lists processed | — |
| Candidate records surfaced (post date/dedup filter) | — |
| Included after screening | — |

---

## Stage 6 — Charting and Synthesis

*To be completed after data extraction.*

---

## AI-Use Log (PRISMA-trAIce)

Every AI-assisted step in this review is logged here per the PRISMA-trAIce commitment in §2.1 of the manuscript. Human reviewers retain all inclusion, exclusion, and extraction decisions.

| # | Stage | Task | Tool | Model / Version | Prompting strategy | Date(s) | Decision authority |
|---|---|---|---|---|---|---|---|
| 1 | Stage 1 — Search and Corpus Assembly | Metadata retrieval pipeline: PubMedFetcher, IEEEExportLoader, WoSExportLoader; deduplication; corpus assembly (`run_metadata.py` with `--fetch-only` / `--corpus-only` flags; substeps in `metadata/fetch/` and `metadata/preprocessing/`) | Claude Code (Anthropic) | claude-sonnet-4-6 | Interactive pair-programming via CLI; user directed tasks, Claude generated and revised code, user approved all changes | 2026-06-18 | Human (pipeline author reviewed and approved all code) |
| 2 | Stage 2 — Pre-filtering (Automatic codes SE1–SE4) | Generation of the automatic pre-filter code (`metadata/preprocessing/prefilter.py`, codes SE1–SE4) and its integration into `run_metadata.py --corpus-only`; the approved code was then executed to apply the pre-filter to the deduplicated corpus | Claude Code (Anthropic) | claude-sonnet-4-6 | Interactive pair-programming via CLI; Claude generated the code, user reviewed and approved all changes before execution | 2026-06-25 | Human (all code human-approved before execution; the executed pre-filter results were confirmed and revised by the pipeline author to verify the quality of the executed code; no AI judgment on individual records) |
| 3 | Stage 3 — Title/Abstract Screening | None — screening performed entirely by two human reviewers: independent assessment (Step A) and discussion-based conflict resolution (Step B); no AI-assisted steps at this stage | — | — | — | completed 2026-07-13 | Human (both reviewers) |
| 4 | Stage 4 — Full-Text Retrieval | Generation of the full-text retrieval script (`run_fulltext_retrieval.py`): parses Phase 1 final decisions from `screening_phase1_append.xlsx`, resolves PMCIDs via the NCBI ID Converter, downloads open-access PDFs (PMC OA subset packages, Unpaywall), and produces `outputs/fulltext/retrieval_log.csv` plus a manual worklist; the approved code was then executed, retrieving 57 of 157 full texts automatically (remaining 100 retrieved manually by the reviewer via university institutional access) | Claude Code (Anthropic) | claude-fable-5 | Interactive pair-programming via CLI; implementation plan approved by user before coding; user decided storage layout and XML handling; Claude generated the code, user approved all changes before execution | 2026-07-13 to 2026-07-14 | Human (all code human-approved before execution; retrieval is deterministic — no AI judgment on any record's content or eligibility; manual retrieval decisions made by reviewer with institutional access) |
| 5 | Stage 4 — Full-Text Screening | *(to be filled)* | | | | | |
| 6 | Stage 5 — Backward Citation Snowballing | *(to be filled)* | | | | | |
| 7 | Stage 6 — Charting and Synthesis | *(to be filled)* | | | | | |
