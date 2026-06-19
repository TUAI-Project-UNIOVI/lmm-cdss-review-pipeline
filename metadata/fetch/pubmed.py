"""PubMed metadata retrieval via NCBI metapub API."""

import logging
from pathlib import Path

import pandas as pd
from metapub import PubMedFetcher as MetapubFetcher
from tqdm import tqdm

import config
from utils import retry

logger = logging.getLogger(__name__)


class PubMedFetcher:
    """Fetch metadata for all PMIDs matching a query and return a corpus DataFrame."""

    def __init__(self, email: str, api_key: str) -> None:
        if not api_key:
            raise ValueError("NCBI_API_KEY is required but not set in .env")
        if not email:
            raise ValueError("NCBI_EMAIL is required but not set in .env")
        logger.info("Initialising PubMedFetcher (email=%s)", email)
        self.fetcher = MetapubFetcher()

    @retry(max_attempts=3, wait=10.0)
    def _fetch_pmids(self, query: str, max_results: int) -> list[str]:
        """Return PMIDs for *query*."""
        logger.info("Querying PubMed (retmax=%d)...", max_results)
        pmids = self.fetcher.pmids_for_query(query, retmax=max_results)
        logger.info("Found %d PMIDs.", len(pmids))
        return pmids

    @retry(max_attempts=3, wait=5.0)
    def _fetch_article(self, pmid: str):
        """Fetch a single PubMedArticle by PMID."""
        return self.fetcher.article_by_pmid(pmid)

    def _parse_article(self, article) -> dict:
        author_str = "; ".join(str(a) for a in article.authors)
        return {
            "corpus_id":    "",
            "duplicate_of": "",
            "is_duplicate": False,
            "source":       "pubmed",
            "uid":          article.pmid,
            "title":        article.title or "",
            "journal":      article.journal or "",
            "year":         article.year or "",
            "authors":      author_str,
            "doi":          article.doi or "",
            "keywords":     article.keywords or "",
            "abstract":     article.abstract or "",
            "url":          article.url or "",
            "bibtex":       article.citation_bibtex or "",
            "pub_type":     str(article.publication_types or ""),
        }

    def fetch(
        self,
        query: str = config.PUBMED_QUERY,
        max_results: int = config.MAX_RESULTS,
        failed_file: str = config.FAILED_PMIDS_FILE,
    ) -> pd.DataFrame:
        """Run the full fetch and return a DataFrame with CORPUS_COLUMNS columns.

        Failed PMIDs are written to *failed_file* for later inspection.
        """
        pmids = self._fetch_pmids(query, max_results)
        if not pmids:
            logger.warning("No PMIDs returned. Returning empty DataFrame.")
            return pd.DataFrame(columns=config.CORPUS_COLUMNS)

        rows, failed = [], []
        for pmid in tqdm(pmids, desc="PubMed"):
            try:
                article = self._fetch_article(pmid)
                rows.append(self._parse_article(article))
            except Exception as exc:
                logger.warning("Failed PMID %s: %s", pmid, exc)
                failed.append(pmid)

        if failed:
            with open(failed_file, "w", encoding="utf-8") as fh:
                fh.write("\n".join(failed))
            logger.info("Wrote %d failed PMIDs to %s", len(failed), failed_file)

        logger.info("PubMed: %d records fetched, %d failed.", len(rows), len(failed))
        return pd.DataFrame(rows, columns=config.CORPUS_COLUMNS)

    @staticmethod
    def write_clean_bib(df: pd.DataFrame, out_path: str) -> None:
        """Write all non-empty bibtex entries from *df* to *out_path*."""
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        entries = df["bibtex"].dropna()
        entries = entries[entries != ""]
        with out.open("w", encoding="utf-8") as fh:
            for entry in entries:
                fh.write(entry.strip())
                fh.write("\n\n")
        logger.info("Wrote clean BIB with %d entries to %s", len(entries), out_path)
