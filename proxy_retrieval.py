"""Proxy-based PDF retrieval for paywalled articles.

Uses University of Oviedo OCLC EZproxy to access institutional subscriptions.
Converts DOI/journal URLs to proxy-wrapped versions and downloads PDFs.

Usage:
    python proxy_retrieval.py --test                    # Test proxy connectivity
    python proxy_retrieval.py --only 105 1 122          # Retrieve specific corpus_ids
    python proxy_retrieval.py --all                     # Attempt all manual_needed papers
    python proxy_retrieval.py --retry-failed            # Retry previous API errors

Environment:
    UNIOVI_USERNAME (optional) — institutional username for auth
    UNIOVI_PASSWORD (optional) — institutional password for auth
"""

import argparse
import csv
import logging
import os
import re
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

import config
from utils import setup_logging, ensure_output_dir

logger = logging.getLogger(__name__)

# University of Oviedo OCLC EZproxy configuration
PROXY_PREFIX = "uniovi.idm.oclc.org"
PROXY_TIMEOUT = 30
PROXY_SLEEP = 1.0  # seconds between requests (politeness)

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def wrap_url_for_proxy(url: str) -> str:
    """Convert a URL to proxy-wrapped version for University of Oviedo.

    Examples:
        https://doi.org/10.1016/j.foo
        → https://doi-org.uniovi.idm.oclc.org/10.1016/j.foo

        https://www.sciencedirect.com/science/article/...
        → https://www-sciencedirect-com.uniovi.idm.oclc.org/science/article/...
    """
    # Parse URL
    match = re.match(r"https?://([^/]+)(.*)", url)
    if not match:
        return url

    domain, path = match.groups()

    # Convert domain: www.example.com → www-example-com
    proxy_domain = domain.replace(".", "-")

    # Construct proxied URL
    return f"https://{proxy_domain}.{PROXY_PREFIX}{path}"


def test_proxy() -> bool:
    """Test proxy connectivity and authentication."""
    logger.info("Testing University of Oviedo proxy connectivity...")

    # Test with a known-free resource (doesn't require auth)
    test_url = "https://doi.org/10.1038/nature.2015.17433"
    proxied = wrap_url_for_proxy(test_url)

    logger.info("Test URL (proxied): %s", proxied)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    try:
        resp = session.head(proxied, timeout=PROXY_TIMEOUT, allow_redirects=True)
        logger.info("Status: %s", resp.status_code)

        if resp.status_code == 200:
            logger.info("✓ Proxy is working!")
            return True
        elif resp.status_code in (401, 403):
            logger.warning("⚠ Proxy requires authentication (401/403)")
            logger.warning("  Check if UNIOVI_USERNAME and UNIOVI_PASSWORD are set")
            return False
        else:
            logger.warning("? Unexpected status code: %s", resp.status_code)
            return False
    except Exception as e:
        logger.error("✗ Proxy connection failed: %s", e)
        return False


def retrieve_via_proxy(doi: str, dest: Path, session: requests.Session) -> tuple[bool, str]:
    """Attempt to retrieve PDF via university proxy.

    Returns: (success, method_or_error)
    """
    if not doi:
        return False, "no_doi"

    # Create proxied DOI URL
    doi_url = f"https://doi.org/{doi}"
    proxied_url = wrap_url_for_proxy(doi_url)

    logger.debug("Attempting proxy retrieval: %s", proxied_url)

    try:
        time.sleep(PROXY_SLEEP)
        resp = session.get(proxied_url, timeout=PROXY_TIMEOUT, allow_redirects=True)

        if resp.status_code == 401 or resp.status_code == 403:
            return False, f"proxy_auth_required:{resp.status_code}"

        if resp.status_code != 200:
            return False, f"proxy_error:{resp.status_code}"

        # Check if we got a PDF
        content = resp.content
        if b"%PDF" not in content[:1024]:
            logger.debug("Content is not PDF: %s...", content[:100])
            return False, "not_pdf"

        # Write to disk
        dest.write_bytes(content)
        logger.info("✓ Retrieved via proxy: %s", dest.name)
        return True, "proxy_doi"

    except requests.Timeout:
        return False, "proxy_timeout"
    except Exception as e:
        logger.debug("Proxy error: %s", type(e).__name__)
        return False, f"proxy_error:{type(e).__name__}"


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Proxy-based retrieval for paywalled articles via University of Oviedo"
    )
    parser.add_argument("--test", action="store_true", help="Test proxy connectivity only")
    parser.add_argument("--only", nargs="+", type=int, metavar="ID",
                        help="Retrieve only specific corpus_ids")
    parser.add_argument("--all", action="store_true",
                        help="Attempt all manual_needed papers")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Retry papers that had API errors")

    args = parser.parse_args()

    # Test proxy if requested
    if args.test:
        test_proxy()
        return

    # Load retrieval log
    retrieval_log_path = Path("outputs/fulltext/retrieval_log.csv")
    if not retrieval_log_path.exists():
        logger.error("Retrieval log not found: %s", retrieval_log_path)
        logger.error("Run run_fulltext_retrieval.py first")
        return

    retrieval_log = pd.read_csv(retrieval_log_path, dtype=str).fillna("")
    retrieval_log["corpus_id"] = retrieval_log["corpus_id"].astype(int)

    # Filter for papers to attempt
    if args.only:
        to_retrieve = retrieval_log[retrieval_log["corpus_id"].isin(args.only)]
    elif args.retry_failed:
        to_retrieve = retrieval_log[
            (retrieval_log["status"] == "manual_needed") &
            (retrieval_log["attempts"].str.contains("error:HTTPError", na=False))
        ]
    elif args.all:
        to_retrieve = retrieval_log[retrieval_log["status"] == "manual_needed"]
    else:
        logger.error("Specify --test, --only, --all, or --retry-failed")
        parser.print_help()
        return

    logger.info("Attempting %d paper(s) via proxy...", len(to_retrieve))

    # Set up session with proxy auth if provided
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    username = os.environ.get("UNIOVI_USERNAME")
    password = os.environ.get("UNIOVI_PASSWORD")
    if username and password:
        session.auth = (username, password)
        logger.info("Using authenticated proxy session")

    fulltext_dir = Path("../papers_library/fulltext_retrieved")
    ensure_output_dir(fulltext_dir)

    # Retrieve
    success_count = 0
    for _, rec in to_retrieve.iterrows():
        corpus_id = int(rec["corpus_id"])
        doi = rec["doi"].strip()

        if not doi:
            logger.warning("corpus_id %d has no DOI, skipping", corpus_id)
            continue

        dest = fulltext_dir / f"{rec['standard_name']}.pdf"

        if dest.exists():
            logger.info("✓ corpus_id %d already exists: %s", corpus_id, dest.name)
            success_count += 1
            continue

        logger.info("Attempting corpus_id %d (DOI: %s)...", corpus_id, doi)
        ok, method = retrieve_via_proxy(doi, dest, session)

        if ok:
            success_count += 1
            # Update log
            retrieval_log.loc[retrieval_log["corpus_id"] == corpus_id, "status"] = "retrieved"
            retrieval_log.loc[retrieval_log["corpus_id"] == corpus_id, "method"] = method
            retrieval_log.loc[retrieval_log["corpus_id"] == corpus_id, "file_path"] = str(dest)
        else:
            logger.warning("  Failed: %s", method)

    # Save updated log
    ensure_output_dir("outputs/fulltext")
    retrieval_log.to_csv(retrieval_log_path, index=False)

    logger.info("✓ Complete: %d/%d papers retrieved", success_count, len(to_retrieve))


if __name__ == "__main__":
    main()
