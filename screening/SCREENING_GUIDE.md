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

- **`screening_phase1_R1.xlsx`** — for reviewer 1
- **`screening_phase1_R2.xlsx`** — for reviewer 2
- **`reviewer_guide_phase1.md`** — plain-language explanation of every column with examples

---

# Phase 2 — Full-Text Screening Modifications

Everything above (exclusion codes, decision logic, rationale format) still applies in Phase 2. This section adds what's different: two parent grey-area questions (GA7; GA1, GA5, and GA9) surfaced during Phase 1 that full-text reviewers will need to apply, the Phase 2 procedure, and the Phase 2 workbook structure.

**Status: GA1, GA5, GA7, GA9 — all RESOLVED.** All four grey areas are ratified and may be applied directly during screening. This is the single source for grey-area (GA) history and status — see `../review_execution_log.md § Stage 4` for the dated execution record.

---

## Key definitions — read before screening

Four grey areas (GA1, GA5, GA7, GA9) regroup into **two parent questions**. GA7 is not a "case" of anything — it's the root definition every CO3 judgment depends on. GA1, GA5, and GA9 are all specific instances of the second question: given the LLM does X (or sits at position X in the workflow), is X enough of a role in the CDSS to count?

1. **What is a clinical decision** (GA7) — defines the target itself: what counts as CDSS output at all.
2. **What LLM role is sufficient for inclusion** (GA1, GA5, GA9) — given a definition of clinical decision, is *this specific* LLM role enough to make the system an LLM-CDSS?

Both parents surfaced during Phase 1 (title/abstract) screening; see `../review_execution_log.md § Stage 4` for the dated execution record.

---

### Parent 1 — What is a clinical decision? (GA7) [RESOLVED]

**Criteria this amplifies:** CO3 (patient-specific CDSS output) — this is the foundational grey area feeding Parent 2 (GA1, GA5, GA9).

**Definition — GA7:** A **clinical decision output** is any patient-specific content — real or simulated patient — that the LLM itself generates and that constitutes, contributes to, or grounds a step in the clinician's decision cascade (diagnosis, differential, risk/prognosis, treatment, triage, test/order selection, discharge, or rationale for any of these). Judge against this definition, not the authors' framing. It need not be the full, final, or acted-upon decision, and it need not be prospective (justifying a decision already made also counts). It excludes: content with no specific patient in scope (cohort/protocol-level, population guidelines), and content the LLM only reformats or transcribes rather than generates (a decision or reasoning supplied by the clinician, not the model).

**Examples:**

- **Monitoring and alert-generating systems — INCLUDE.** An alert is itself a per-patient decision (priority/no-priority), even though the clinician takes the downstream action.

- **Partial decisions in a decision cascade — INCLUDE.** Clinical decisions are rarely one atomic choice but a cascade of sub-decisions (e.g., identifying barriers to a therapy). Resolving one link satisfies CO3 even without the full decision.

- **Evaluation frameworks that study LLM-CDSS rather than being one — decision depends on what is evaluated.** INCLUDE if the benchmarked task is a patient-specific clinical decision (e.g., diagnostic accuracy, treatment recommendation). EXCLUDE (`keep-as-reference: <topic>`) if not (e.g., licensing/board-exam performance, general medical QA). Re-check individually: #106 (PIEE red-teaming), #44 (Ho et al. metrics review), #52 (MetaMedQA benchmark).

- **Risk score, differential diagnosis list, or prognosis/outcome prediction, with no explicit recommendation attached — INCLUDE.** e.g., "72% risk of sepsis," a ranked differential, or a mortality/readmission/LOS prediction. Each is grounding/support information for a decision, not the decision itself, but satisfies CO3 under the "contributes to or grounds a step" clause.

- **Drug interaction / contraindication flagging — INCLUDE.** Binary yes/no flag on a specific patient's medication list; patient-specific and actionable.

- **Order-set / next-test suggestion — INCLUDE.** e.g., "recommend ordering troponin" — test selection is a step in the decision cascade.

- **Documentation / note-generation embedding clinical reasoning — split by direction.** EXCLUDE if the LLM only formats/transcribes a decision the clinician already made (e.g., ambient scribe tools) — the LLM never touches the decision. INCLUDE if the LLM generates the assessment/plan content itself and the clinician reviews/signs it — the reasoning in the note is the LLM's clinical judgment. Test: did the LLM generate the reasoning, or only reformat reasoning already supplied?

- **Explanation / justification-only output for a human-made decision — INCLUDE.** LLM generates the supporting rationale after the clinician already decided; still grounding/support information.

- **Cohort- or protocol-level recommendation, not individual-patient — EXCLUDE.** e.g., an LLM-suggested sepsis protocol update from aggregate data. No specific patient in scope — the clean boundary case opposite GA7's anchor.

- **Simulated / virtual patient case, no real patient data — INCLUDE.** "Patient-specific" is read as patient-specific framing, not requiring a real patient.

---

### Parent 2 — What LLM role is sufficient for inclusion? (GA1, GA5, GA9) [RESOLVED]

**Criteria this amplifies:** CO3 (patient-specific CDSS output), assuming GA7's definition of "clinical decision" is already in place.

**Definition — GA1/GA5/GA9:** Given GA7, an LLM's role qualifies when the LLM *itself* occupies a step in the decision cascade — directly as the CDSS, as a processed input feeding the CDSS's decision (even if a downstream model or rule set makes the final call), or as an orchestrator invoking tools/agents whose combined output is the decision. It does not qualify when the LLM sits outside the cascade: designing, building, selecting, or training the decision-making system that is then deployed without it (LLM-as-builder, GA2), or maintaining its knowledge base off-line (only online, per-patient recommendations count). Workflow position (first-opinion / second-opinion / independent-then-reconcile) does not affect this judgment — it is a charting dimension only, applied after role-type has already determined inclusion.

**Examples:**

- **LLM extracts patient-specific contraindications from notes; a rule set generates the treatment recommendation — INCLUDE.** The extraction is a step in the cascade.

- **LLM encodes patient history into a feature used by a gradient-boosted classifier to predict sepsis risk — INCLUDE.** Same reasoning: a processed input feeding the decision.

- **LLM acts as orchestrator, calling tools/agents (labs lookup, guideline retrieval, calculator) whose combined output is the decision — INCLUDE.**

- **LLM is used to select or design the predictive model (e.g., choosing which ML algorithm to deploy) — EXCLUDE.** This is building the CDSS, not being or feeding it (GA2).

- **LLM as off-line knowledge-maintenance layer behind a rule-based CDSS — EXCLUDE.** Updating the guideline/rule corpus a rule-based CDSS draws on is builder activity, not a step in the per-patient cascade, regardless of downstream effect on future recommendations. Mark disposition `keep-as-reference: knowledge-maintenance`. Corpus #150 (Abdellaoui et al.) and #177 (Wang et al.) both EXCLUDE under this rule.

- **LLM workflow position — first opinion (precedes clinician judgment, risks anchoring), second opinion/assistant (confirms or challenges an existing decision), or independent/combined (both decide, then reconcile) — does not change CO3 status.** Classify included studies by position for charting; it never gates inclusion on its own.

---
