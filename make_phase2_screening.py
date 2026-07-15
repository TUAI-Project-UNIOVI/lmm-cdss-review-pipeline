#!/usr/bin/env python3
"""
Generate Phase 2 full-text screening templates (R1, R2, append).

Reads the corpus metadata and full-text retrieval log.
Produces:
  - screening_phase2_R1.xlsx
  - screening_phase2_R2.xlsx
  - screening_phase2_append.xlsx (for Step B discussion results)

Columns:
  - Identity (pre-filled): corpus_id, standard_name, title, journal, year, full_text_retrieved
  - Checks (reviewer fills): PO1, CO2, CO3, CX4, OT5
  - Decision (reviewer fills): decision, rationale, disposition, borderline_flag
  - Discussion (post-Step B): disagreement_flag, discussion_rationale, final_decision
"""

from pathlib import Path
import pandas as pd

# Config
OUTPUTS_DIR = Path(__file__).parent / "outputs"
RETRIEVAL_SUMMARY = OUTPUTS_DIR / "fulltext" / "stage4_retrieval_summary.csv"
SCREENING_DIR = Path(__file__).parent / "screening"

def load_retrieval_summary():
    """Load corpus metadata from retrieval summary."""
    df = pd.read_csv(RETRIEVAL_SUMMARY)
    return df[["corpus_id", "standard_name", "title", "journal", "year", "status"]].copy()

def make_reviewer_template(retrieval_df, reviewer_num):
    """Generate one reviewer's screening template."""
    # Map retrieval status to full_text_retrieved column
    retrieval_df["full_text_retrieved"] = retrieval_df["status"].apply(
        lambda x: "Yes" if x == "retrieved" else "No"
    )

    # Build screening sheet with identity columns and empty check/decision columns
    screening_df = retrieval_df[["corpus_id", "standard_name", "title", "journal", "year", "full_text_retrieved"]].copy()

    # Add check columns (Yes / No / blank)
    for code in ["PO1_population_clinician", "CO2_concept_llm_presence", "CO3_concept_cdss_function", "CX4_context_clinical_data", "OT5_other"]:
        screening_df[code] = ""

    # Add decision columns
    screening_df["decision"] = ""
    screening_df["rationale"] = ""
    screening_df["disposition"] = ""
    screening_df["borderline_flag"] = ""

    return screening_df.reset_index(drop=True)

def make_append_template(retrieval_df):
    """Generate the Step B discussion template (both reviewers + discussion results)."""
    # Identity + full retrieval status + decision columns for both reviewers
    append_df = retrieval_df[["corpus_id", "standard_name", "title", "journal", "year"]].copy()

    # Add check columns for reference
    append_df["full_text_retrieved"] = retrieval_df["status"].apply(
        lambda x: "Yes" if x == "retrieved" else "No"
    )

    # Step A — independent decisions
    for reviewer in ["R1", "R2"]:
        for col in ["decision", "rationale"]:
            append_df[f"{col}_{reviewer}"] = ""

    # Step B — discussion results
    append_df["disagreement_flag"] = ""
    append_df["discussion_rationale"] = ""
    append_df["final_decision"] = ""

    return append_df.reset_index(drop=True)

def write_xlsx(df, xlsx_path):
    """Write a dataframe to XLSX."""
    df.to_excel(xlsx_path, index=False, sheet_name="screening")
    print(f"✓ {xlsx_path}")

def main():
    retrieval_df = load_retrieval_summary()
    print(f"Loaded {len(retrieval_df)} records from retrieval summary.")

    # R1 template
    r1_df = make_reviewer_template(retrieval_df, 1)
    write_xlsx(r1_df, SCREENING_DIR / "screening_phase2_R1.xlsx")

    # R2 template
    r2_df = make_reviewer_template(retrieval_df, 2)
    write_xlsx(r2_df, SCREENING_DIR / "screening_phase2_R2.xlsx")

    # Append template (for after Step A)
    append_df = make_append_template(retrieval_df)
    write_xlsx(append_df, SCREENING_DIR / "screening_phase2_append.xlsx")

    print(f"\n✅ Phase 2 screening templates created for {len(retrieval_df)} papers")
    print(f"\nNext steps:")
    print(f"  1. R1: Open screening_phase2_R1.xlsx and fill checks + decisions for all papers")
    print(f"  2. R2: Open screening_phase2_R2.xlsx and fill checks + decisions independently")
    print(f"  3. After both: Merge results into screening_phase2_append.xlsx for Step B discussion")
    print(f"  4. Reference screening/SCREENING_GUIDE.md § Phase 2 for GA definitions and decision logic")

if __name__ == "__main__":
    main()
