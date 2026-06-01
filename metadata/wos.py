"""Web of Science metadata retrieval.

Primary path: WoS Starter API (free tier, requires WOS_API_KEY in .env).
Fallback path: WoSExportLoader reads a manually exported TSV/CSV from the WoS UI
  and normalises it to the corpus contract — use when the API is unavailable.

API docs: https://developer.clarivate.com/apis/wos-starter
"""

import logging
import os

import pandas as pd
import requests

import config
from utils import retry

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.clarivate.com/apis/wos-starter/v1/documents"


class WoSFetcher:
    """Fetch metadata from Web of Science Starter API."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("WOS_API_KEY is required but not set in .env")
        self.headers = {"X-ApiKey": api_key}

    @retry(max_attempts=3, wait=15.0)
    def _get_page(self, query: str, page: int, limit: int = 50) -> dict:
        params = {"q": query, "limit": limit, "page": page, "db": "WOS"}
        resp = requests.get(_BASE_URL, params=params, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _parse_record(self, rec: dict) -> dict:
        uid = rec.get("uid", "")
        names = rec.get("names", {})
        authors = "; ".join(
            a.get("displayName", "") for a in names.get("authors", [])
        )
        source = rec.get("source", {})
        links = rec.get("links", {})
        keywords = "; ".join(
            kw for kw in rec.get("keywords", {}).get("authorKeywords", [])
        )
        return {
            "source": "wos",
            "uid": uid,
            "title": rec.get("title", ""),
            "journal": source.get("sourceTitle", ""),
            "year": str(source.get("publishYear", "")),
            "authors": authors,
            "doi": links.get("identifiers", {}).get("doi", ""),
            "keywords": keywords,
            "abstract": rec.get("abstract", {}).get("value", ""),
            "url": links.get("record", ""),
            "bibtex": "",
            "pub_type": rec.get("documentType", ""),
            "is_duplicate": False,
        }

    def fetch(
        self,
        query: str = config.WOS_QUERY,
        max_results: int = config.MAX_RESULTS,
    ) -> pd.DataFrame:
        """Paginate through WoS API and return a corpus DataFrame."""
        rows, page, limit = [], 1, 50

        logger.info("Querying Web of Science Starter API...")
        first = self._get_page(query, page, limit)
        total = first.get("metadata", {}).get("total", 0)
        logger.info("WoS: %d total records.", total)

        for rec in first.get("hits", []):
            rows.append(self._parse_record(rec))

        page += 1
        while (page - 1) * limit < min(total, max_results):
            data = self._get_page(query, page, limit)
            for rec in data.get("hits", []):
                rows.append(self._parse_record(rec))
            page += 1

        logger.info("WoS: %d records fetched.", len(rows))
        return pd.DataFrame(rows, columns=config.CORPUS_COLUMNS)


class WoSExportLoader:
    """Load a manually exported WoS TSV file and normalise to corpus contract.

    Use this when the API is unavailable. Export from WoS UI:
      Save to → Tab-delimited (Win, UTF-8), Full Record and Cited References.
    """

    # Map from WoS export column names to corpus columns
    _COL_MAP = {
        "UT": "uid",
        "TI": "title",
        "SO": "journal",
        "PY": "year",
        "AU": "authors",
        "DI": "doi",
        "DE": "keywords",
        "AB": "abstract",
    }

    def load(self, file_path: str) -> pd.DataFrame:
        """Parse *file_path* (TSV) and return a corpus-contract DataFrame."""
        logger.info("Loading WoS export from %s", file_path)
        raw = pd.read_csv(file_path, sep="\t", dtype=str, on_bad_lines="skip")

        df = pd.DataFrame(columns=config.CORPUS_COLUMNS)
        for wos_col, corpus_col in self._COL_MAP.items():
            if wos_col in raw.columns:
                df[corpus_col] = raw[wos_col].fillna("")
            else:
                df[corpus_col] = ""

        df["source"] = "wos"
        df["url"] = ""
        df["bibtex"] = ""
        df["pub_type"] = raw.get("DT", pd.Series(dtype=str)).fillna("") if "DT" in raw.columns else ""
        df["is_duplicate"] = False

        logger.info("WoS export: %d records loaded.", len(df))
        return df
