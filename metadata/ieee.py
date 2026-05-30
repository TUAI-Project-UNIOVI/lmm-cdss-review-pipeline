"""IEEE Xplore metadata retrieval via the IEEE Xplore API.

API docs: https://developer.ieee.org/docs
Requires IEEE_API_KEY in .env.
"""

import logging
import os

import pandas as pd
import requests

import config
from utils import retry

logger = logging.getLogger(__name__)

_BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"


class IEEEScraper:
    """Fetch metadata from IEEE Xplore and return a corpus DataFrame."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("IEEE_API_KEY is required but not set in .env")
        self.api_key = api_key

    @retry(max_attempts=3, wait=10.0)
    def _get_page(self, query: str, start: int, page_size: int = 25) -> dict:
        params = {
            "apikey": self.api_key,
            "querytext": query,
            "start_record": start,
            "max_records": page_size,
            "output_type": "json",
        }
        resp = requests.get(_BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _parse_record(self, rec: dict) -> dict:
        authors = "; ".join(
            a.get("full_name", "") for a in rec.get("authors", {}).get("authors", [])
        )
        return {
            "source": "ieee",
            "uid": str(rec.get("article_number", "")),
            "title": rec.get("title", ""),
            "journal": rec.get("publication_title", ""),
            "year": str(rec.get("publication_year", "")),
            "authors": authors,
            "doi": rec.get("doi", ""),
            "keywords": "; ".join(
                kw.get("value", "")
                for kw in rec.get("index_terms", {}).get("ieee_terms", {}).get("terms", [])
            ),
            "abstract": rec.get("abstract", ""),
            "url": rec.get("html_url", ""),
            "bibtex": "",
            "pub_type": rec.get("content_type", ""),
            "is_duplicate": False,
        }

    def fetch(
        self,
        query: str = config.IEEE_QUERY,
        max_results: int = config.MAX_RESULTS,
    ) -> pd.DataFrame:
        """Paginate through IEEE API results and return a corpus DataFrame."""
        rows, start, page_size = [], 1, 25

        logger.info("Querying IEEE Xplore...")
        first = self._get_page(query, start, page_size)
        total = int(first.get("total_records", 0))
        logger.info("IEEE Xplore: %d total records.", total)

        for rec in first.get("articles", []):
            rows.append(self._parse_record(rec))

        start += page_size
        while start <= min(total, max_results):
            page = self._get_page(query, start, page_size)
            for rec in page.get("articles", []):
                rows.append(self._parse_record(rec))
            start += page_size

        logger.info("IEEE Xplore: %d records fetched.", len(rows))
        return pd.DataFrame(rows, columns=config.CORPUS_COLUMNS)
