"""Phase 2 full-paper reading-aid screening (Stage 3).

This module provides LLM-assisted summaries to support human reviewers
during full-text review. The LLM acts as a reading aid only — final
inclusion/exclusion decisions are made by the human reviewer.

PRISMA-trAIce log row (for App F of @mtx):
  Stage: Phase 2 full-text review (Stage 3 reading aid)
  Tool: Google Gemini
  Model: see config.GEMINI_MODEL
  Prompting strategy: structured summary prompt; model returns key dimensions
    of interest (study type, LLM role, clinical decision type, population).
  Date range: logged at runtime in the output CSV (column: screen_date).
"""

import json
import logging
import time
from datetime import date

from google import genai
from google.genai import types
import pandas as pd
from tqdm import tqdm

import config
from utils import retry

logger = logging.getLogger(__name__)

_RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "study_type": types.Schema(
            type=types.Type.STRING,
            description="e.g. RCT, cohort, framework paper, systematic review.",
        ),
        "llm_role": types.Schema(
            type=types.Type.STRING,
            description="How the LLM/LMM is used in the system.",
        ),
        "clinical_decision_type": types.Schema(
            type=types.Type.STRING,
            description="Type of clinical decision supported (diagnosis, triage, etc.).",
        ),
        "population": types.Schema(
            type=types.Type.STRING,
            description="Patient population or clinical domain.",
        ),
        "reviewer_notes": types.Schema(
            type=types.Type.STRING,
            description="Any flags or caveats the human reviewer should check.",
        ),
    },
    required=["study_type", "llm_role", "clinical_decision_type", "population", "reviewer_notes"],
)

_SYSTEM_PROMPT = """
You are a reading-aid assistant for a systematic scoping review on LLMs in clinical
decision support systems. Given the full text (or abstract + methods excerpt) of a
paper, extract the key dimensions below and return a JSON object.
Do NOT make the inclusion/exclusion decision — that is the human reviewer's role.
Your job is to surface relevant information quickly.
"""


class FullPaperScreener:
    """Generate structured reading-aid summaries for full-text review."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required but not set in .env")
        self._client = genai.Client(api_key=api_key)
        self._gen_config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=_RESPONSE_SCHEMA,
        )
        logger.info("FullPaperScreener initialised (model=%s).", config.GEMINI_MODEL)

    @retry(max_attempts=3, wait=config.GEMINI_RATE_LIMIT_SLEEP)
    def _call_model(self, text: str) -> dict:
        response = self._client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=text,
            config=self._gen_config,
        )
        return json.loads(response.text)

    def screen(self, screening_results: pd.DataFrame) -> pd.DataFrame:
        """Generate reading-aid summaries for Phase 1 inclusions.

        Expects *screening_results* to have at minimum: uid, title, abstract.
        Returns a DataFrame with one row per paper and the extracted dimensions.
        """
        today = date.today().isoformat()
        rows = []

        includes = screening_results[screening_results["inclusion_status"] == 1].copy()
        logger.info("FullPaperScreener: %d Phase 1 inclusions to process.", len(includes))

        for _, row in tqdm(includes.iterrows(), total=len(includes), desc="Full-paper reading aid"):
            text = f"Title: {row.get('title', '')}\n\nAbstract: {row.get('abstract', '')}"
            try:
                data = self._call_model(text)
                rows.append({
                    "uid":                   row.get("uid"),
                    "title":                 row.get("title"),
                    "study_type":            data.get("study_type", ""),
                    "llm_role":              data.get("llm_role", ""),
                    "clinical_decision_type":data.get("clinical_decision_type", ""),
                    "population":            data.get("population", ""),
                    "reviewer_notes":        data.get("reviewer_notes", ""),
                    "screen_date":           today,
                })
            except Exception as exc:
                logger.warning("Full-paper screen failed for uid=%s: %s", row.get("uid"), exc)
                rows.append({
                    "uid": row.get("uid"),
                    "title": row.get("title"),
                    "study_type": "", "llm_role": "",
                    "clinical_decision_type": "", "population": "",
                    "reviewer_notes": f"ERROR: {exc}",
                    "screen_date": today,
                })

            time.sleep(config.GEMINI_RATE_LIMIT_SLEEP)

        return pd.DataFrame(rows)
