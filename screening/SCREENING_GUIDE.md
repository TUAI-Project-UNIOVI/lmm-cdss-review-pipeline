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
- **`reviewer_guide.md`** — plain-language explanation of every column with examples

---

# Phase 2 — Full-Text Screening Modifications

Everything above (exclusion codes, decision logic, rationale format) still applies in Phase 2. This section adds what's different: two parent grey-area questions (GA7; GA1, GA5, and GA9) surfaced during Phase 1 that full-text reviewers will need to apply, the Phase 2 procedure, and the Phase 2 workbook structure.

**Status: GA1, GA5, GA7, GA9 — OPEN, TO DISCUSS.** The definitions and rules below are drafts, not final decisions — do not apply them to screening yet. This is the single source for grey-area (GA) history and status — see `../review_execution_log.md § Stage 4` for the dated execution record.

---

## Key definitions — read before screening

Four grey areas (GA1, GA5, GA7, GA9) regroup into **two parent questions**. GA7 is not a "case" of anything — it's the root definition every CO3 judgment depends on. GA1, GA5, and GA9 are all specific instances of the second question: given the LLM does X (or sits at position X in the workflow), is X enough of a role in the CDSS to count?

1. **What is a clinical decision** (GA7) — defines the target itself: what counts as CDSS output at all.
2. **What LLM role is sufficient for inclusion** (GA1, GA5, GA9) — given a definition of clinical decision, is *this specific* LLM role enough to make the system an LLM-CDSS?

Both parents surfaced during Phase 1 (title/abstract) screening; see `../review_execution_log.md § Stage 4` for the dated execution record.

---

### Parent 1 — What is a clinical decision? (GA7) [OPEN — TO DISCUSS]

**Premise for review:** Judge whether a system produces clinical recommendations *against this definition*, not against the authors' framing. A paper may call its output a "clinical decision" when it does not qualify under this definition.

**Criteria this amplifies:** CO3 (patient-specific CDSS output) — CO3 can't be judged consistently without this definition. This is the foundational grey area: GA1 and GA5 (Parent 2) both assume some definition of "clinical decision" is already in place before they can be applied.

**Definition (work in progress) — GA7:** "Clinical decision" means any *patient-specific judgment* in the clinician's decision cascade.

**History:**
- **2026-07-10** — GA7 registered: CO3 needs an explicit statement of what is and is not a clinical decision, since some decisions are clinical but not patient-facing (e.g., selecting a medical calculator for a case). Draft rule proposed: anchor on *patient-specific* rather than *patient-facing* — any per-patient judgement in the care decision cascade qualifies, decisions with no specific patient in scope do not. Ranked ahead of GA1/GA5/GA9 since its definition feeds them.
- **2026-07-10** — GA8 registered as GA7's corollary: some papers label their system as supporting clinical decisions when it does not qualify under the review's own definition. Rule: CO3 is judged on the system's actual function per GA7; mention of "clinical decision (support)" alone never triggers inclusion. A paper's own label is a claim to verify, not evidence.
- **2026-07-13** — GA7 marked DECIDED, folded into this guide.
- **2026-07-15 (later)** — GA7 reopened; decision reverted to OPEN (this current status). GA8 remains dependent on GA7 and is unmoored until GA7 is re-decided.

**Examples and cases to clarify:**

- **Monitoring and alert-generating systems (GA4, resolved as its own rule — INCLUDE).** Raised 2026-07-09: systems that monitor patients or generate alerts satisfy CO3 and are included — generating an alert is itself a decision that triggers clinician review, the system deciding per patient whether the patient requires priority attention. This is a patient-specific clinical recommendation (a triage-like judgement at the front of the decision cascade), not merely administrative, even though the clinician takes the downstream action. Kept here as a live example because it's the same "what counts as a decision" question GA7 is trying to pin down. **To confirm:** does this hold for every alert type, or only ones tied to a specific clinical threshold?

- **Partial decisions in a decision cascade (GA3, resolved as its own rule — INCLUDE).** Raised during abstract screening: systems that do not explicitly output a decision but produce all the patient-specific information needed to take it — e.g., identifying barriers to implementing a therapy. Clinical decisions rarely arrive as a single atomic choice but as a cascade of sub-decisions; such a system resolves one link of that cascade. These outputs are not merely informational or educational, because the output directly constitutes a component of the clinical decision even though it is not the full decision — so they satisfy CO3. Kept here as a live example because it's the same "what counts as a decision" question GA7 is trying to pin down: a *partial* decision still counts.

- **Evaluation frameworks that study LLM-CDSS rather than being one (GA6, resolved as its own rule — EXCLUDE CO3, `keep-as-reference: <topic>`).** A paper whose subject is evaluating, benchmarking, or red-teaming LLM-CDSS systems (rather than deploying one that produces patient-specific recommendations) does not itself qualify as an LLM-CDSS. Examples: Corpus #106 (PIEE red-teaming), #44 (Ho et al. metrics review), #52 (MetaMedQA benchmark). Kept here as a live example on the other edge of the same "what counts as a decision" question: a paper *about* clinical decisions is not itself a clinical decision.

---

### Parent 2 — What LLM role is sufficient for inclusion? (GA1, GA5, GA9) [OPEN — TO DISCUSS]

**Premise for review:** An LLM's mere presence in a system (CO2) doesn't automatically make the system's output a clinical decision (CO3). The question in every case below is whether the LLM's *specific role* is close enough to the decision to count, or whether it's one step removed (preprocessing, builder, maintenance, front/back of workflow) and therefore doesn't.

**Criteria this amplifies:** CO3 (patient-specific CDSS output), assuming a working definition of "clinical decision" from Parent 1 (GA7). GA1, GA5, and GA9 are three specific role-patterns under this same question — more may surface during screening.

**History:**
- **2026-07-09** — GA1 raised as a boundary case: when the LLM is only one component of a larger pipeline (e.g., extracts/summarizes patient information while a separate downstream model or rule set makes the recommendation), does the system qualify as an LLM-CDSS? Records matching this pattern were marked Uncertain pending resolution.
- **2026-07-09** — GA2 clarified (resolved): papers that use an LLM to *build* a CDSS rather than to *be* the decision-support engine (e.g., an LLM designing triage rules or prescription-start/stop rules) are excluded under CO3 — the deployed decision logic is the generated rule set, not the LLM. This is the resolved sibling case GA1 and GA5 both compare against (LLM-as-builder vs. LLM-as-decision-bearing-component).
- **2026-07-13** — Full-Text Review Preparation section created: GA1 and GA5 both registered OPEN with draft rules proposed, as decisions the reviewer resolves without supervisor validation. Both marked DECIDED, folded into this guide.
- **2026-07-15 (later)** — GA1 and GA5 reopened; decisions reverted to OPEN (this current status).
- **GA5's original framing** (research direction, predates its registration as a screening question): LLM as the knowledge-maintenance layer behind a (rule-based) CDSS — how to process new medical information to keep the guideline corpus behind a CDSS current, even when the CDSS itself is rule-based. Corpus papers #150, #177 are its supporting examples.
- **GA9's original framing** (charting/discussion-angle hypothesis, recognized 2026-07-15 as also bearing on screening): where should the LLM sit in the decision workflow — first opinion / assistant-second-opinion / combined-independent — and the anchoring-bias vs. added-value trade-off between them. Registered as a screening grey area same day.

#### GA1 — LLM as one component of a decision pipeline

**Definition (work in progress):** INCLUDE if the LLM's contribution is patient-specific AND decision-bearing (removing it changes the recommendation). EXCLUDE if the LLM performs generic preprocessing that non-generative NLP could do. Test: "Would removing or replacing the LLM change the recommendation for a specific patient?"

**Examples and cases to clarify:**

- ✅ **Candidate INCLUDE:** LLM extracts patient-specific contraindications from notes; a rule set then generates a treatment recommendation.
- ✅ **Candidate INCLUDE:** LLM encodes patient history; a gradient-boosted classifier predicts sepsis risk.
- ❌ **Candidate EXCLUDE:** LLM performs generic text preprocessing (tokenization, entity normalization) identical to traditional NLP; a separate model applies the decision.
- ❌ **Candidate EXCLUDE:** LLM builds the rule set itself (triage rules, prescription logic) for deployment — looks like GA2 (LLM-as-builder). **To confirm:** where's the line between "extracts decision-relevant data" and "generic preprocessing" when both are technically NLP tasks?

#### GA5 — LLM as knowledge-maintenance layer behind a rule-based CDSS

**Definition (work in progress):** Candidate rule — EXCLUDE via GA2 (deployed system is rule-based, not LLM-based), mark disposition `keep-as-reference: knowledge-maintenance`. Rationale: knowledge maintenance is off-line/builder activity, not an ongoing CDSS component.

**Examples and cases to clarify:**

- Corpus #150 (Abdellaoui et al.) — LLM compares guideline versions to update the DESIREE CDSS knowledge base. **To confirm:** does directly changing future recommendations push this back toward CO3-relevant, or does "off-line, one-shot" still dominate?
- Corpus #177 (Wang et al.) — LLM agents extend a rule/SQL CDSS knowledge base. Same open question.

#### GA9 — LLM position in the decision workflow (front vs. back)

**Premise for this case:** Where the LLM sits in the clinical decision workflow is itself part of what defines its role — an LLM sitting in front of the human (shaping the first read of the case) plays a functionally different part than one sitting behind a human decision (checking or challenging it after the fact), even when both are technically "involved in the decision." GA1 and GA5 ask about role *type* (pipeline component vs. knowledge-maintenance); GA9 asks about role *position*.

**Definition (work in progress):** Three candidate configurations, not yet mapped to INCLUDE/EXCLUDE:
- **(a) First opinion** — LLM output comes before the clinician's own judgment. Less biased than a human first-pass (no fatigue, no recency/availability effects) but risks anchoring the clinician toward its answer.
- **(b) Assistant / second opinion** — LLM confirms or challenges a decision the clinician already reached. Avoids anchoring but limits the LLM's contribution to error-catching.
- **(c) Combined / independent** — Both decide independently, then reconcile through structured discussion (analogous to this review's own dual-reviewer screening with discussion).

**Examples and cases to clarify:**

- **To confirm:** does workflow position change a system's CO3 status at all, or is it purely a charting/discussion-section dimension (classify included studies by position, note whether anchoring effects are measured) that doesn't affect inclusion/exclusion? If it does affect CO3, which position(s) would fail to qualify and why?
- **To confirm:** how does GA9 interact with GA1 — e.g., an LLM in a "first opinion" position that only does generic preprocessing (GA1 candidate-exclude) vs. one in a "second opinion" position doing patient-specific validation (GA1 candidate-include). Does position modulate the GA1 test, or are they fully independent axes?

---

## Phase 2 decision codes quick lookup

Codes `CO3_GA1`, `CO3_GA5`, and `CO3_GA7` depend on the open GA1/GA5/GA7 discussions above — **do not use them until those are resolved.** GA9 has no candidate code yet — it isn't even mapped to INCLUDE/EXCLUDE as a draft (see § Parent 2 → GA9); flag matching papers borderline and describe the workflow position in `rationale`.

| Code | Reason | Example | Status |
|---|---|---|---|
| `PO1` | Not used by clinicians | Patient-facing app, student training tool | Stable |
| `CO2` | No LLM/LMM | Random Forest CDSS, rule-based only | Stable |
| `CO3` | No patient-specific decisions | Evaluation framework, general education | Stable |
| `CO3_GA1` | LLM is generic preprocessing | LLM does tokenization; downstream model decides | OPEN — draft only |
| `CO3_GA5` | LLM maintains knowledge base | LLM updates rule set; deployed system is rules | OPEN — draft only |
| `CO3_GA7` | Framing mismatch; not patient-specific | Paper claims "clinical decision" but outputs general info | OPEN — draft only |
| — | LLM workflow position (GA9) | First-opinion / second-opinion / independent-parallel | OPEN — no code yet, flag borderline |
| `CX4` | No clinical data | Synthetic non-medical data, NLP benchmark on reviews | Stable |
| `OT5` | Other reason | Explain in rationale | Stable |
| `ACCESS` / `ACCESS_INSUFFICIENT` | Full text unavailable, insufficient info to decide | Access-restricted paper (see below) | Stable |

Rationale template:

```
Decision: EXCLUDE
Code: CO3_GA1
Rationale: LLM performs entity extraction from notes; separate ML model
generates diagnosis recommendation. LLM output is not decision-bearing;
could replace with traditional NER.
Borderline: [blank]
```

---

## Phase 2 procedure — Step A / Step B

Read the **full text** (not abstract alone) for every paper.

### Step A — Independent Screening (each reviewer)

1. Open PDF from `papers_library/fulltext_retrieved/`.
2. Apply checks in order: PO1 → CO2 → CO3 → CX4 → OT5. Stop at first `Yes`. **GA7/GA1/GA5/GA9 are still open — do not apply their draft rules yet; flag CO3 borderline cases matching these patterns for discussion instead.**
3. Set `decision`; log `rationale` for every exclusion and every doubt.
4. Mark `borderline_flag = Yes` if the decision feels close — this prioritizes the paper for Step B discussion.
5. Do **not** consult your co-reviewer or look at their workbook during Step A.

### Step B — Reviewer Discussion

1. Identify all disagreements between R1 and R2.
2. For each, share rationales, consult GA7/GA1/GA5/GA9 draft definitions if the disagreement is interpretive, and attempt consensus. **These definitions are still open — use the discussion to help ratify or revise them, not as settled rules.**
3. If consensus: log `final_decision` and `discussion_rationale` in `screening_phase2_append.xlsx`.
4. If no consensus: **INCLUDE** (conservative default) and note why consensus wasn't reached.

### Access-restricted papers

9 papers are access-restricted (corpus IDs 122, 10, 27, 37, 62, 98, 125, 142, 144):

1. Try to assess from title, abstract, and any available preview/supplementary materials.
2. If a confident decision is possible, make it and note the basis in `rationale`.
3. If not, mark `EXCLUDE / ACCESS_INSUFFICIENT` and document the access attempt — this is expected and acceptable under PRISMA-ScR transparency requirements.

### When in doubt

- Mark `borderline_flag = Yes`.
- Document your reasoning in `rationale`.
- Discuss with your co-reviewer before excluding.
- Default to include — Phase 2 is the last gate; Phase 1 already filtered out many false positives.

---

## Phase 2 screening database — column structure

One file per reviewer (`screening_phase2_R1.xlsx`, `screening_phase2_R2.xlsx`), plus a compiled `screening_phase2_append.xlsx` for Step B.

### Identity columns *(pre-filled, do not edit)*

| Column | Content |
|---|---|
| `corpus_id` | Record identifier from corpus |
| `standard_name` | Canonical paper name (`Surname Year_corpus_id_title-words`) |
| `title` | Paper title |
| `journal` | Journal or venue |
| `year` | Publication year |
| `full_text_retrieved` | `Yes` if PDF is available in library; `No` if access-restricted |

### Check columns *(reviewer fills Yes / No)*

| Column | Code | Exclusion condition — what makes this Yes |
|---|---|---|
| `PO1_population_clinician` | PO1 | Not used by licensed clinicians |
| `CO2_concept_llm_presence` | CO2 | No LLM/LMM in any role |
| `CO3_concept_cdss_function` | CO3 | No patient-specific decision output. GA7/GA1/GA5/GA9 draft refinements (definition, pipeline exclusions, knowledge-maintenance exclusions, workflow-position) are **OPEN — do not apply yet**; flag matching cases as borderline instead |
| `CX4_context_clinical_data` | CX4 | No clinical data of any kind |
| `OT5_other` | OT5 | Exclusion reason not covered by PO1–CX4; detail in `rationale` |

### Decision and rationale columns *(reviewer fills)*

| Column | Content |
|---|---|
| `decision` | `INCLUDE` / `EXCLUDE` |
| `rationale` | Explanation; required for exclusions and doubts |
| `disposition` | For excluded papers: `keep-as-reference: <topic>` (e.g. `knowledge-maintenance`, `evaluation-frameworks`) or blank |
| `borderline_flag` | `Yes` if the decision felt close — prioritizes Step B discussion |

### Discussion columns *(filled during Step B, in `screening_phase2_append.xlsx`)*

| Column | Content |
|---|---|
| `disagreement_flag` | `Yes` if R1 and R2 decisions differ |
| `discussion_rationale` | Joint rationale after discussion |
| `final_decision` | Agreed decision (`INCLUDE` / `EXCLUDE`) after Step B |

### Companion files to generate

- **`screening_phase2_R1.xlsx`** — reviewer 1
- **`screening_phase2_R2.xlsx`** — reviewer 2
- **`screening_phase2_append.xlsx`** — compiled Step A + Step B results

---

## Phase 2 pre-screening checklist

- [ ] Read this section, especially GA7, GA1, GA5, GA9 draft definitions — note these are OPEN and not yet ratified
- [ ] Understand the four checks (PO1, CO2, CO3, CX4) and what triggers each
- [ ] Understand decision logic: check in order, first `Yes` stops review
- [ ] Have access to the PDF library (`papers_library/fulltext_retrieved/`)
- [ ] Have your workbook (`screening_phase2_R1.xlsx` or `R2.xlsx`)
- [ ] Will not look at co-reviewer's decisions during Step A
- [ ] Will mark borderline papers clearly to help Step B discussion

**Estimated time:** ~10–15 min per paper; ~26–39 hours total for 157 papers (spread over 1–2 weeks is typical).
