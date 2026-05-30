"""Descriptive statistics and figures for the manuscript synthesis section.

Reads outputs/charting_results.csv and writes figures to outputs/figures/.
All figures are matplotlib/seaborn — no interactive dependencies.

Figures produced:
  - year_distribution.png   : bar chart of publications per year
  - clinical_domain.png     : horizontal bar chart of clinical domain frequency
  - llm_architecture.png    : bar chart of LLM architecture types
  - decision_type.png       : bar chart of clinical decision types
"""

import logging
import os

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless runs
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import config

logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid", palette="muted")


def _save(fig: plt.Figure, name: str) -> None:
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    path = os.path.join(config.FIGURES_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    logger.info("Saved figure: %s", path)


def generate_figures(charting_csv: str = config.CHARTING_CSV) -> None:
    """Generate all synthesis figures from the completed charting CSV."""
    if not os.path.exists(charting_csv):
        logger.error("Charting file not found: %s. Run run_charting.py first.", charting_csv)
        return

    df = pd.read_csv(charting_csv, dtype=str)
    logger.info("synthesis.py: %d charted records loaded.", len(df))

    # Year distribution
    if "year" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        df["year"].value_counts().sort_index().plot(kind="bar", ax=ax)
        ax.set_title("Publications per year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
        _save(fig, "year_distribution.png")

    # Clinical domain
    if "clinical_domain" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        df["clinical_domain"].value_counts().head(15).plot(kind="barh", ax=ax)
        ax.set_title("Clinical domain frequency (top 15)")
        ax.invert_yaxis()
        _save(fig, "clinical_domain.png")

    # LLM architecture
    if "llm_architecture" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        df["llm_architecture"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("LLM architecture types")
        ax.set_ylabel("Count")
        _save(fig, "llm_architecture.png")

    # Decision type
    if "decision_type" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        df["decision_type"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Clinical decision types")
        ax.set_ylabel("Count")
        _save(fig, "decision_type.png")

    logger.info("All figures written to %s/", config.FIGURES_DIR)
