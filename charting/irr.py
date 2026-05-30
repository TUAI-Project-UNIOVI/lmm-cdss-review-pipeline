"""Inter-rater reliability (IRR) computation.

Computes Cohen's kappa and percent agreement for two reviewers' decisions
on the same set of records. Used for both Phase 1 (abstract screening)
and Phase 3 (full-text charting) to satisfy JBI single-reviewer + IRR policy.
"""

import logging

import pandas as pd
from sklearn.metrics import cohen_kappa_score

logger = logging.getLogger(__name__)


def compute_irr(
    decisions_1: pd.Series,
    decisions_2: pd.Series,
    label: str = "screening",
) -> dict:
    """Compute Cohen's kappa and percent agreement between two decision series.

    Args:
        decisions_1: Series of decisions from reviewer 1 (categorical/integer).
        decisions_2: Series of decisions from reviewer 2 (same length and index).
        label:       Descriptive label for logging (e.g. "abstract_screening").

    Returns:
        Dict with keys: label, n_records, percent_agreement, cohens_kappa.
    """
    if len(decisions_1) != len(decisions_2):
        raise ValueError("Decision series must have the same length.")

    n = len(decisions_1)
    agreement = (decisions_1 == decisions_2).sum()
    pct_agreement = round(agreement / n * 100, 2) if n > 0 else 0.0

    kappa = cohen_kappa_score(decisions_1, decisions_2)

    result = {
        "label": label,
        "n_records": n,
        "percent_agreement": pct_agreement,
        "cohens_kappa": round(kappa, 4),
    }

    logger.info(
        "IRR [%s]: n=%d, %%agreement=%.1f, kappa=%.4f",
        label, n, pct_agreement, kappa,
    )
    return result
