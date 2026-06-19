# Screening Guide — LMM-CDSS Scoping Review

Reviewer checklist for **Phase 1** (title + abstract) and **Phase 2** (full text) human screening. Covers codes PO1, CO2, CO3, CX4, OT5 only. Codes SE1–SE3 (language, date, source type) are applied automatically by the pipeline before records reach reviewers — see `review_execution_log.md § Stage 1b — Pre-filtering` for details.

---

## Exclusion code system

Codes follow the PCC framework from the protocol (§2.4), plus SE for Sources & Evidence (§2.4.4 — pipeline-only) and OT for unclassified exclusions. Numbers are unique and sequential across all codes.

| Code | PCC dimension | Full label | Applied by |
|---|---|---|---|
| **SE1** | Sources & Evidence | Language not English | Pipeline |
| **SE2** | Sources & Evidence | Outside date range 2024–2026 | Pipeline |
| **SE3** | Sources & Evidence | Not peer-reviewed source type | Pipeline |
| **PO1** | Population | Not used by licensed clinicians | Reviewer |
| **CO2** | Concept | No LLM/LMM involvement | Reviewer |
| **CO3** | Concept | No patient-specific CDSS output | Reviewer |
| **CX4** | Context | No clinical data of any kind | Reviewer |
| **OT5** | Other | Unclassified exclusion; detail in rationale | Reviewer |

---

## Decision logic

Apply reviewer codes **in order** (PO1 → CO2 → CO3 → CX4). A single confirmed exclusion is sufficient — stop and record the code. All checks must pass to include.

### Conservative default
- If two reviewers disagree → **discuss** → if no consensus → **INCLUDE**
- **Phase 1 only:** if in doubt at any check → **INCLUDE**
- **Phase 1 only:** if abstract is absent → **INCLUDE**, forward to Phase 2

---

## PO1 — Population: who uses the system
*PCC: Population (§2.4.1)*

**Exclude (Yes) if:** System is NOT used by licensed clinicians (physicians, specialists, nurses, residents) or multidisciplinary clinical teams in a professional workflow.

Examples that trigger exclusion: patient-facing app (self-diagnosis, symptom checker), undergraduate medical education tool, administrative staff only (billing, scheduling).

---

## CO2 — Concept: LLM/LMM involvement
*PCC: Concept (§2.4.2)*

**Exclude (Yes) if:** Study does NOT use an LLM/LMM in any meaningful role — neither as core component nor as orchestrator.

Exclude if the system relies solely on traditional ML (Random Forest, CNN-only, SVM), rule-based logic, or legacy transformers (e.g. BERT) with no generative LLM/LMM involvement.

> LLM and LMM are equivalent for inclusion. Do not exclude on terminology alone.

---

## CO3 — Concept: CDSS decision-support function
*PCC: Concept (§2.4.2)*

**Exclude (Yes) if:** System does NOT produce patient-specific recommendations supporting a clinical decision (diagnosis, differential diagnosis, treatment planning, prognosis, triage, discharge planning).

Examples that trigger exclusion: administrative automation only (scribing, billing, ICD coding), general medical education or information retrieval without patient-specific decision context.

---

## CX4 — Context: clinical data
*PCC: Context (§2.4.3)*

**Exclude (Yes) if:** Study uses no clinical data of any kind — neither real patient data, clinical notes, medical imaging, synthetic clinical data, nor recognised medical benchmarks.

---

## OT5 — Other
**Exclude (Yes) if:** Exclusion reason not covered by PO1–CX4. Detail the reason in `rationale`.

---

## Decision summary

| Phase | Situation | Decision |
|---|---|---|
| Both | All codes pass | **INCLUDE** |
| Both | Any code triggered (confirmed) | **EXCLUDE** — log code |
| Phase 1 | Doubt at any check | **INCLUDE** |
| Phase 1 | Abstract absent | **INCLUDE** (forward to Phase 2) |
| Phase 2 | Doubt at any check | Discuss with co-reviewer |
| Both | No consensus after discussion | **INCLUDE** |

---

## Rationale logging format

For every record log:
1. **Decision** — `INCLUDE` or `EXCLUDE`
2. **Code** — code that triggered exclusion (e.g. `CO2`), or `all_pass` for inclusions
3. **Evidence** — brief explanation; quote the specific text if it helps

---

## Screening database — column structure

One file per reviewer (`screening_phase1_R1.xlsx`, `screening_phase1_R2.xlsx`). Each row is one paper. Identity columns are pre-filled. Check and decision columns are blank for the reviewer to fill.

Check columns: `Yes` = exclusion criterion met, `No` = paper passes this check.

### Identity columns *(pre-filled, do not edit)*

| Column | Content |
|---|---|
| `uid` | Record identifier from corpus |
| `title` | Paper title |
| `abstract` | Abstract text |
| `phase` | `1` or `2` — screening phase this record is being assessed in |

### Check columns *(reviewer fills Yes / No)*

| Column | Code | Exclusion condition — what makes this Yes |
|---|---|---|
| `PO1_population_clinician` | PO1 | System is NOT used by licensed clinicians — e.g. patient-facing app, undergraduate education tool, admin-only workflow |
| `CO2_concept_llm_presence` | CO2 | Does NOT use an LLM/LMM in any role — neither as core component nor as orchestrator; relies solely on traditional ML, rule-based logic, or legacy transformers (e.g. BERT) |
| `CO3_concept_cdss_function` | CO3 | No patient-specific clinical decision output — e.g. admin automation only (scribing, billing), general medical education without patient context |
| `CX4_context_clinical_data` | CX4 | Study uses no clinical data of any kind — neither real patient data, clinical notes, medical imaging, synthetic clinical data, nor recognised medical benchmarks |
| `OT5_other` | OT5 | Exclusion reason not covered by PO1–CX4; detail in `rationale` |

### Decision and rationale columns *(reviewer fills)*

| Column | Content |
|---|---|
| `decision` | `INCLUDE` / `EXCLUDE` — reviewer must commit to one; disagreements flagged during compilation |
| `rationale` | Brief explanation of the decision. Required for exclusions and doubts. |

### Companion files to generate

- **`screening_phase1_R1.xlsx`** and **`screening_phase1_R1.csv`** — for reviewer 1
- **`screening_phase1_R2.xlsx`** and **`screening_phase1_R2.csv`** — for reviewer 2
- **`reviewer_guide.md`** — plain-language explanation of every column with examples
