"""Phase 1 abstract screening via Gemini structured JSON output.

Reads outputs/corpus.pkl, runs each title+abstract through the Gemini model,
and writes outputs/screening_results.{csv,xlsx,pkl}.

PRISMA-trAIce log row (for App F of @mtx):
  Stage: Phase 1 abstract screening
  Tool: Google Gemini
  Model: see config.GEMINI_MODEL
  Prompting strategy: structured JSON schema (response_schema); system prompt
    contains inclusion/exclusion criteria verbatim from @ptx §2 (PCC).
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

# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

_RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "inclusion_status": types.Schema(
            type=types.Type.INTEGER,
            description="1 = Include, 0 = Exclude, 2 = Unsure (needs manual review).",
        ),
        "exclusion_reasons": types.Schema(
            type=types.Type.OBJECT,
            description="Binary flags (0 or 1) for each exclusion criterion.",
            properties={
                "is_genomic":       types.Schema(type=types.Type.INTEGER),
                "is_mental_health": types.Schema(type=types.Type.INTEGER),
                "is_dentistry":     types.Schema(type=types.Type.INTEGER),
                "is_pediatric":     types.Schema(type=types.Type.INTEGER),
                "is_cadaver":       types.Schema(type=types.Type.INTEGER),
                "is_no_LLM":        types.Schema(type=types.Type.INTEGER),
                "is_no_cds":        types.Schema(type=types.Type.INTEGER),
            },
        ),
        "observations": types.Schema(
            type=types.Type.STRING,
            description=(
                "If 0: main exclusion reason(s). "
                "If 2: source of ambiguity. "
                "If 1: paper type (e.g. framework, RCT)."
            ),
        ),
    },
    required=["inclusion_status", "exclusion_reasons", "observations"],
)

_SYSTEM_PROMPT = """
You are an expert clinical research assistant performing a systematic scoping review.
Analyse the provided title and abstract using the inclusion and exclusion criteria below
and return ONLY a valid JSON object matching the requested schema.

Inclusion criteria (ALL must hold):
1. The paper features a Large Language Model (LLM) or Large Multimodal Model (LMM).
2. The LLM/LMM directly supports, makes, or prompts a clinical decision.
3. Clinical decisions include: treatment recommendations, therapy plans, diagnostics,
   differential diagnoses, risk/medication alerts, triage, or similar.
4. Systematic reviews or framework papers about these specific applications are INCLUDED.

Exclusion criteria (exclude if ANY is true):
- is_genomic: primary focus is genomics or molecular biology.
- is_mental_health: primary focus is mental health, psychiatry, or psychology.
- is_dentistry: primary focus is dentistry or oral health.
- is_pediatric: primary focus is paediatric patients (children).
- is_cadaver: study involves cadavers.
- is_no_LLM: no LLM/LMM as a core component.
- is_no_cds: no direct clinical decision support (administrative tasks, billing,
  patient note summarisation, education, or basic research without a clinical
  decision application).

Decision rules for inclusion_status:
- 1 (Include): meets all inclusion criteria AND zero exclusion criteria.
- 0 (Exclude): one or more exclusion criteria apply.
- 2 (Unsure): abstract is ambiguous or lacks sufficient detail.
"""


class AbstractScreener:
    """Screen title+abstract pairs using the Gemini model."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required but not set in .env")
        self._client = genai.Client(api_key=api_key)
        self._gen_config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=_RESPONSE_SCHEMA,
        )
        logger.info("AbstractScreener initialised (model=%s).", config.GEMINI_MODEL)

    @retry(max_attempts=3, wait=config.GEMINI_RATE_LIMIT_SLEEP)
    def _call_model(self, text: str) -> dict:
        response = self._client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=text,
            config=self._gen_config,
        )
        return json.loads(response.text)

    def screen(self, corpus: pd.DataFrame) -> pd.DataFrame:
        """Run screening on *corpus* and return an annotated DataFrame.

        Adds columns: inclusion_status, observations, is_genomic, is_mental_health,
        is_dentistry, is_pediatric, is_cadaver, is_no_LLM, is_no_cds, screen_date.
        """
        today = date.today().isoformat()
        result_rows = []

        for _, row in tqdm(corpus.iterrows(), total=len(corpus), desc="Screening abstracts"):
            text = f"{row.get('title', '')}: {row.get('abstract', '')}"
            try:
                data = self._call_model(text)
                er = data.get("exclusion_reasons", {})
                result_rows.append({
                    **row.to_dict(),
                    "inclusion_status": data.get("inclusion_status"),
                    "observations":     data.get("observations", ""),
                    "is_genomic":       er.get("is_genomic", 0),
                    "is_mental_health": er.get("is_mental_health", 0),
                    "is_dentistry":     er.get("is_dentistry", 0),
                    "is_pediatric":     er.get("is_pediatric", 0),
                    "is_cadaver":       er.get("is_cadaver", 0),
                    "is_no_LLM":        er.get("is_no_LLM", 0),
                    "is_no_cds":        er.get("is_no_cds", 0),
                    "screen_date":      today,
                })
            except Exception as exc:
                logger.warning("Screening failed for uid=%s: %s", row.get("uid"), exc)
                result_rows.append({
                    **row.to_dict(),
                    "inclusion_status": None,
                    "observations": f"ERROR: {exc}",
                    "is_genomic": None, "is_mental_health": None,
                    "is_dentistry": None, "is_pediatric": None,
                    "is_cadaver": None, "is_no_LLM": None, "is_no_cds": None,
                    "screen_date": today,
                })

            time.sleep(config.GEMINI_RATE_LIMIT_SLEEP)

        return pd.DataFrame(result_rows)
