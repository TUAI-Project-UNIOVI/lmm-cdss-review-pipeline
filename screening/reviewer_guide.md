# Reviewer Guide — Phase 1 Screening

You will receive a spreadsheet with one row per paper. For each paper, read the title and abstract, then fill the check columns and the decision column.

1. Read title and abstract.
2. Go through each check column in order. Mark `Yes` if the exclusion applies, `No` if it does not. As soon as one column is `Yes`, you can stop.
3. If any column is `Yes`, set `decision` to `EXCLUDE` and explain the reason in `rationale`. Quote the specific text if it helps.
4. If all columns are `No`, set `decision` to `INCLUDE`. Rationale is optional for inclusions.
5. If in doubt at any check, mark `No` and set `decision` to `INCLUDE`. Write the reason for the doubt in `rationale` as a support note.
6. If there is no abstract, set `decision` to `INCLUDE` and leave checks blank.

---

## Column reference

| Column name in spreadsheet | Code | What to check — mark Yes to exclude |
|---|---|---|
| `PO1_population_clinician` | PO1 | System is NOT used by licensed clinicians (physicians, nurses, residents). Exclude if patient-facing, for students, or admin-only. |
| `CO2_concept_llm_presence` | CO2 | Study does NOT use an LLM or LMM in any role (core or orchestrator). Exclude if the system is traditional ML, rule-based, or BERT-only with no generative model. |
| `CO3_concept_cdss_function` | CO3 | System does NOT produce patient-specific clinical recommendations (diagnosis, treatment, triage, prognosis). Exclude if purely administrative or educational. |
| `CX4_context_clinical_data` | CX4 | Study uses NO clinical data of any kind — no patient records, clinical notes, medical imaging, synthetic clinical data, or medical benchmarks. |
| `OT5_other` | OT5 | Any other exclusion reason not covered above. Describe in `rationale`. |
| `decision` | — | `INCLUDE` or `EXCLUDE`. You must choose one. |
| `rationale` | — | Brief explanation of the decision. Required for exclusions and doubts. |
