"""Three-dimension data extraction (charting form).

Dimension 1 — Study characteristics:
  uid, title, authors, journal, year, doi, pub_type, study_design

Dimension 2 — Problem space:
  clinical_domain, decision_type, decision_criticality,
  reasoning_trajectory, workflow_integration

Dimension 3 — Solution space:
  llm_architecture, model_name, is_mas, is_rag, is_xai,
  validation_method, performance_metric

Reviewers fill in the charting form manually (or with AI reading-aid support).
This module provides the empty template and a loader/validator for completed forms.
"""

import logging

import pandas as pd

import config

logger = logging.getLogger(__name__)

# Ordered column list for the charting form — mirrors App E in @mtx
CHARTING_COLUMNS = [
    # D1 — Study characteristics
    "uid", "title", "authors", "journal", "year", "doi", "pub_type", "study_design",
    # D2 — Problem space
    "clinical_domain", "decision_type", "decision_criticality",
    "reasoning_trajectory", "workflow_integration",
    # D3 — Solution space
    "llm_architecture", "model_name", "is_mas", "is_rag", "is_xai",
    "validation_method", "performance_metric",
    # Metadata
    "charted_by", "chart_date", "notes",
]


class ChartingForm:
    """Manage the charting form template and validate completed entries."""

    def empty_template(self, screening_results: pd.DataFrame) -> pd.DataFrame:
        """Return an empty charting template pre-filled with Phase 2 inclusions.

        Args:
            screening_results: Output of run_screening.py with inclusion_status == 1.

        Returns:
            DataFrame with CHARTING_COLUMNS, study-characteristic columns pre-filled
            from corpus data; all extraction columns empty.
        """
        includes = screening_results[screening_results["inclusion_status"] == 1].copy()
        logger.info("ChartingForm: %d Phase 2 inclusions to chart.", len(includes))

        template = pd.DataFrame(columns=CHARTING_COLUMNS)
        for col in ["uid", "title", "authors", "journal", "year", "doi", "pub_type"]:
            if col in includes.columns:
                template[col] = includes[col].values

        # Fill extraction columns with empty strings
        for col in CHARTING_COLUMNS:
            if col not in template.columns or template[col].isna().all():
                template[col] = ""

        return template.reset_index(drop=True)

    def load(self, file_path: str) -> pd.DataFrame:
        """Load and validate a completed charting CSV.

        Raises ValueError if required columns are missing.
        """
        df = pd.read_csv(file_path, dtype=str)
        missing = [c for c in CHARTING_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Charting file missing columns: {missing}")
        logger.info("ChartingForm: loaded %d rows from %s", len(df), file_path)
        return df[CHARTING_COLUMNS]
