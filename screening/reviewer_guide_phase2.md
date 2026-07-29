# Reviewer Guide — Phase 2 Screening (Full Text)

You will receive a spreadsheet with one row per paper. For each paper, examine the full text (not title/abstract alone) closely enough to answer each check with evidence, then fill in the check columns, `decision`, `rationale`, and `borderline_flag`.

1. If no full text was available for a paper, do not screen it. Set `decision` to `EXCLUDE`, code `OT5`, and note in `rationale` that the full text could not be retrieved. Otherwise, open the full-text PDF for the paper.
2. Go through each check column in order (PO1 → CO2 → CO3 → CX4 → OT5). For each, examine the sections of the paper relevant to that check (e.g., methods/system design for CO2/CO3, participants/setting for PO1, data description for CX4) — you do not need to read every section of the paper for every check, but you must read enough to ground your answer in the text, not a guess from the abstract or title. Mark `Yes` if the exclusion applies, `No` if it does not. As soon as one column is `Yes`, you can stop.
3. If any column is `Yes`, set `decision` to `EXCLUDE` and explain the reason in `rationale`. Quote the specific text if it helps.
4. If all columns are `No`, set `decision` to `INCLUDE`. Rationale is optional for inclusions.
5. If in doubt at any check, do **not** default to include. Mark `borderline_flag = Yes` and note the doubt in `rationale` — it will be resolved jointly with your co-reviewer, not by you alone.
6. You may use Claude Opus 5 as an optional reading aid for any check that isn't clear from the text alone (see § Standard reading-aid prompt below). It only answers questions — the decision is always your own judgment.

---

## Column reference

| Column name in spreadsheet | Code | What to check — mark Yes to exclude |
|---|---|---|
| `PO1_population_clinician` | PO1 | System is NOT used by licensed clinicians (physicians, nurses, residents). Exclude if patient-facing, for students, or admin-only. |
| `CO2_concept_llm_presence` | CO2 | Study does NOT use an LLM or LMM in any role (core or orchestrator). Exclude if the system is traditional ML, rule-based, or BERT-only with no generative model. |
| `CO3_concept_cdss_function` | CO3 | System does NOT produce patient-specific clinical recommendations. See § Clarifying grey areas → CO3 below for boundary cases. |
| `CX4_context_clinical_data` | CX4 | Study uses NO clinical data of any kind — no patient records, clinical notes, medical imaging, synthetic clinical data, or medical benchmarks. |
| `OT5_other` | OT5 | Any other exclusion reason not covered above — e.g., an opinion/commentary/editorial piece, or a journalistic research briefing summarizing one primary study, with no systematic analysis of a body of qualifying research; or any other issue you can't map to PO1–CX4. If the paper itself is a review, see § Clarifying grey areas → Review papers below before using this code. Describe the specific reason in `rationale`. There is no scripted reading-aid question for OT5 — it is a catch-all for cases the other checks don't cover, so judge it directly from the text. |
| `decision` | — | `INCLUDE` or `EXCLUDE`. You must choose one — Phase 2 is definitive. |
| `rationale` | — | Brief explanation of the decision. Required for exclusions and doubts. |
| `borderline_flag` | — | `Yes` if the decision felt close, even if you reached one. Prioritizes the record for joint reviewer discussion. |

---

## Clarifying grey areas

Several boundary cases came up during abstract-level screening where it was unclear how a check applied. This section works through them with a clarifications and illustrative examples in some cases. The examples are not exhaustive. Mark `borderline_flag = Yes` for any case that doesn't clearly fit.

### CO3 — what counts as a patient-specific clinical decision

**What counts as a clinical decision** — any patient-specific content (real or simulated patient) the LLM itself generates that constitutes, contributes to, or grounds a step in the decision cascade (diagnosis, differential, risk/prognosis, treatment, triage, test/order selection, discharge, or rationale for any of these). Judge against this definition, not the paper's own framing. It need not be the full, final, or acted-upon decision, and need not be prospective — justifying a decision already made counts too.

For example:
- A risk score, differential diagnosis list, or prognosis prediction with no explicit action attached still **includes**, since it grounds a decision even without stating one.
- Documentation/note-generation depends on which way the reasoning flows: if the LLM generates the assessment/plan itself (clinician reviews/signs), that **includes**; if it only formats or transcribes a decision the clinician already made (e.g., ambient scribe tools), that **excludes**.
- An evaluation/benchmark paper's inclusion depends on what's being benchmarked, not on being an evaluation paper: a patient-specific clinical task (e.g., diagnostic accuracy) **includes**; a non-clinical task (e.g., licensing-exam performance) **excludes**.
- A recommendation at the cohort or protocol level, not tied to an individual patient, **excludes** — this is the boundary case opposite the definition above.

**What LLM role counts** — the LLM must itself occupy a step in the cascade: directly as the CDSS, as a processed input feeding the CDSS's decision (even if a downstream model or rule set makes the final call), or as an orchestrator invoking tools/agents whose combined output is the decision.

For example:
- If the LLM is used to select, design, or build the decision-making system itself (e.g., picks which model to deploy), that **excludes** — this is building the tool, not using it.
- If the LLM only maintains a rule-based CDSS's knowledge base off-line (e.g., updating its guideline corpus), that **excludes** too, regardless of any downstream effect on future recommendations.
- Where the LLM sits in the workflow (first opinion, second opinion, or independent-then-reconcile) does not change this test on its own — note it in `rationale` for context, but it isn't itself grounds for inclusion or exclusion.

### Review papers — how paper type changes the checklist

Review papers (narrative, systematic, scoping) are included when their subject matter is LLM-CDSS — apply PO1–CX4 to what the review analyzes, not to whether it presents an original system of its own. If the subject matter is out of scope, exclude on whichever code it triggers.

---

## Standard reading-aid prompt

Both reviewers must use **Claude Opus 5** (do not substitute a different model or version, to keep the PRISMA-trAIce report consistent), loaded with the full-text PDF. Start every session with:

> You are assisting a human reviewer in a systematic literature screening process. Answer questions about this paper's content precisely and point to the specific page or section. Do not offer an include/exclude recommendation or a PO1/CO2/CO3/CX4/OT5 judgment — that decision belongs to the reviewer alone. If the answer isn't in the paper, say so rather than inferring.

For whichever checks you consult it on, use this exact wording, in order:

1. **PO1** — "Does this paper describe a system used by licensed clinicians (physicians, nurses, residents) in a professional workflow, or is it patient-facing, for students, or administrative-only?"
2. **CO2** — "Does the system use an LLM or LMM in any role — core component or orchestrator — or does it rely solely on traditional ML, rule-based logic, or a non-generative model (e.g., BERT)?"
3. **CO3a (decision output)** — "Does the system produce a patient-specific clinical decision output — diagnosis, treatment, triage, prognosis, or test/order selection — or a partial step that grounds one of these, even if not the full or final decision?"
4. **CO3b (LLM role)** — "Does the LLM's output feed into that decision directly, as a processed input, or as an orchestrator of tools/agents that jointly produce it? Or is the LLM instead used to select, design, or build the decision-making system, or to maintain its knowledge base off-line, rather than sitting in the decision cascade itself?"
5. **CX4** — "Does the study use any clinical data — real patient data, clinical notes, imaging, synthetic clinical data, or a recognised medical benchmark?"

If the paper involves documentation/note-generation, an evaluation or benchmark task, or an LLM whose exact role in the pipeline is unclear, ask the matching fixed follow-up below immediately after question 4. Ask only the one that applies; skip the others.

- **Documentation/note-generation:** "Does the LLM generate the assessment or plan content itself, with the clinician reviewing or signing it — or does it only format or transcribe a decision the clinician already made?"
- **Evaluation/benchmark paper:** "What specific task does this paper benchmark or evaluate — is that task itself a patient-specific clinical decision (e.g., diagnostic accuracy), or something else (e.g., exam performance, general medical QA)?"
- **LLM pipeline role unclear:** "Does removing or replacing the LLM change the patient-specific recommendation this system produces? Describe exactly what the LLM's output is used for downstream."

Do not ask any other follow-up questions. If a check is still unclear after the fixed question (and follow-up, if applicable), mark `borderline_flag = Yes` rather than probing further.

Note "Claude Opus 5" and the date in `rationale` (PRISMA-trAIce reporting commitment) whenever you use it.
