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

---

### Execution summary

| Database | Execution date | Records retrieved | Duplicates removed | Forwarded to Phase 1 screening |
|---|---|---|---|---|
| PubMed | 2026-06-18 | 164 | — | — |
| IEEE Xplore | 2026-06-18 | 13 | — | — |
| Web of Science | 2026-06-18 | 143 | — | — |
| **Total** | | **320** | **108** | **212** |

Deduplication applied in two passes: (1) exact DOI match; (2) fuzzy title match (RapidFuzz ≥ 92 similarity score, same publication year). Source priority when a duplicate is retained: PubMed > IEEE > WoS.

*Per-database count forwarded to Phase 1 to be filled after screening completes.*

---

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

---

#### IEEE Xplore

**Interface:** Website Command Search — https://ieeexplore.ieee.org/search/advanced/command

**String:**

```
("Document Title":"large language model" OR "Document Title":"large language models" OR "Document Title":"LLM"
OR "Document Title":"LMMs" OR "Document Title":"large multimodal model")
AND ("Document Title":"clinical decision")
```

**Notes:** IEEE Command Search does not support truncation wildcards in `"Document Title":` syntax; `"large language model"` and `"large language models"` are therefore listed as separate literals. The search string itself contains no date or language constraints — both were applied manually as website sidebar filters after running the string: "Publication Year" set to 2024–2026, language set to English. Results exported as CSV (metadata) and BibTeX from the website UI.

---

#### Web of Science

**Interface:** Web of Science Core Collection — Advanced Search (institutional access required)

**String:**

```
TI=("large language model*" OR "LLM" OR "LMMs" OR "large multimodal model*" OR "LMM")
AND TI=("clinical decision*")
AND PY=(2024-2026)
```

**Notes:** `TI=` restricts to title field only. `*` truncation supported. Date filter embedded in the string via `PY=` operator. Language (English) is not available as an inline operator in WoS Advanced Search and was applied manually as a sidebar filter ("English" under Languages) after running the string. Results exported as RIS (Full Record, includes abstracts) from the website UI.

---

### Retrieval method

| Database | Method |
|---|---|
| PubMed | NCBI E-utilities API via `metapub` Python library (`run_metadata.py --fetch-only --sources pubmed`) |
| IEEE Xplore | Manual website export → CSV + BIB files loaded by `IEEEExportLoader` |
| Web of Science | Manual website export → RIS file loaded by `WoSExportLoader` via `rispy` |

Pipeline version: `lmm-cdss-review-pipeline` — see commit history for exact code state at execution date.

---

### Deviations from registered protocol

- None at this stage.

---

## Stage 1b — Pre-filtering (Automatic codes SE1–SE3)

Automated exclusions applied to the deduplicated corpus before records are forwarded to human reviewers. Codes SE1–SE3 correspond to the Sources & Evidence dimension of the PCC framework (§2.4.4 of the protocol) and require no reviewer judgment — they operate entirely on corpus metadata fields.

Implemented in `metadata/preprocessing/prefilter.py`. Applied via `run_metadata.py --corpus-only` on 2026-06-25. Exclusions logged with the codes below.

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

### SE4 — Retraction check *(pending)*

| Code | Condition |
|---|---|
| `SE4` | Paper has been retracted |

**Method:** Cross-reference all corpus DOIs against the Retraction Watch database CSV (freely available at retractionwatch.com). A DOI match flags the record as `SE4`. To be implemented in `metadata/preprocessing/prefilter.py` alongside SE1–SE3.

**Method:** Cross-reference corpus DOIs against `data/retraction_watch.csv` (61,632 retracted DOIs as of download date). DOI match (case-insensitive) flags the record as `SE4_retracted = True`.

**Status:** Applied 2026-06-25 — 0 matches in current corpus.

### Pre-filter results

| Code | Records excluded | Notes |
|---|---|---|
| SE1 — Language | 1 | Lithuanian-language paper detected via `langdetect` on title+abstract (lowercased) |
| SE2 — Date range | 0 | Date enforced at search time; post-hoc integrity check passed |
| SE3 — Source type | 35 | Editorials (PubMed), letters (PubMed), meeting abstracts and editorial material (WoS); 1 record excluded by both SE1 and SE3 |
| SE4 — Retraction | 0 | Cross-referenced against Retraction Watch (61,632 DOIs); no matches |
| **Records forwarded to Phase 1 screening** | **176** | 212 unique − 36 excluded (union of SE1–SE4) |

> For the human reviewer checklist (codes PO1, CO2, CO3, CX4, OT5), see [`screening/SCREENING_GUIDE.md`](screening/SCREENING_GUIDE.md).

---

## Stage 2 — Phase 1 Screening (Title and Abstract)

*To be completed after screening runs.*

| Metric | Count |
|---|---|
| Records entering Phase 1 | 176 |
| Excluded at Stage 1 (both reviewers agree exclude) | — |
| Disagreements forwarded to Stage 2 discussion | — |
| Included after Stage 2 discussion | — |
| Total forwarded to Phase 2 | — |

---

## Stage 3 — Phase 2 Screening (Full Text)

*To be completed after full-text screening runs.*

| Metric | Count |
|---|---|
| Records entering Phase 2 | — |
| Full text not retrievable | — |
| Excluded at Stage 3 (both reviewers agree exclude) | — |
| Disagreements forwarded to Stage 4 discussion | — |
| Included after Stage 4 discussion | — |
| **Final included studies** | — |

---

## Stage 4 — Charting and Synthesis

*To be completed after data extraction.*

---

## AI-Use Log (PRISMA-trAIce)

Every AI-assisted step in this review is logged here per the PRISMA-trAIce commitment in §2.1 of the manuscript. Human reviewers retain all inclusion, exclusion, and extraction decisions.

| # | Stage | Task | Tool | Model / Version | Prompting strategy | Date(s) | Decision authority |
|---|---|---|---|---|---|---|---|
| 1 | Pipeline development | Metadata retrieval pipeline: PubMedFetcher, IEEEExportLoader, WoSExportLoader; deduplication; corpus assembly (`run_metadata.py` with `--fetch-only` / `--corpus-only` flags; substeps in `metadata/fetch/` and `metadata/preprocessing/`) | Claude Code (Anthropic) | claude-sonnet-4-6 | Interactive pair-programming via CLI; user directed tasks, Claude generated and revised code, user approved all changes | 2026-06-18 | Human (pipeline author reviewed and approved all code) |
| 2 | Stage 1 — Abstract screening | *(to be filled)* | | | | | |
| 3 | Stage 2 — Full-text reading aid | *(to be filled)* | | | | | |
| 4 | Synthesis | *(to be filled)* | | | | | |
