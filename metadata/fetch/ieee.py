"""IEEE Xplore metadata loader from website exports.

Reads the two files exported from the IEEE Xplore website:
  - CSV  : general metadata (one row per record)
  - BIB  : BibTeX entries (all entries concatenated)

Both files are matched on DOI. The loader normalises the result to
the pipeline corpus schema (config.CORPUS_COLUMNS) and also writes
a clean, properly formatted .bib file to outputs/.
"""

import logging
import re
from pathlib import Path

import pandas as pd

import config

logger = logging.getLogger(__name__)

# Mapping: IEEE CSV column → corpus column
# Note: "Document Identifier" is always "IEEE Conferences" and is useless as a uid.
# uid is derived from DOI instead (see load()).
_CSV_MAP = {
    "Document Title": "title",
    "Authors": "authors",
    "Publication Title": "journal",
    "Publication Year": "year",
    "Abstract": "abstract",
    "DOI": "doi",
    "PDF Link": "url",
}

# Keyword columns to merge into one field
_KEYWORD_COLS = ["Author Keywords", "IEEE Terms", "Mesh_Terms"]

# Publication type inference
_PROC_KEYWORDS = {"conference", "proceedings", "symposium", "workshop", "congress"}


def _infer_pub_type(journal: str) -> str:
    low = journal.lower()
    if any(k in low for k in _PROC_KEYWORDS):
        return "conference paper"
    return "journal article"


def _parse_bib(bib_path: Path) -> dict[str, str]:
    """Parse a concatenated BibTeX file and return {doi_lower: raw_entry}."""
    text = bib_path.read_text(encoding="utf-8")
    # Split on entry boundaries (@TYPE{...)
    raw_entries = re.split(r"(?=@\w+\{)", text)
    mapping: dict[str, str] = {}
    for entry in raw_entries:
        entry = entry.strip()
        if not entry:
            continue
        doi_match = re.search(r"\bdoi\s*=\s*\{([^}]+)\}", entry, re.IGNORECASE)
        if doi_match:
            doi = doi_match.group(1).strip().lower()
            mapping[doi] = entry
    logger.info("BIB: parsed %d entries with DOIs.", len(mapping))
    return mapping


def _normalise_authors(raw: str) -> str:
    """Convert 'First Last; First Last' (CSV) to 'Last, First and Last, First' (BIB-style)."""
    # CSV uses semicolons; names are already 'First Last' or 'F. Last'
    parts = [p.strip() for p in raw.split(";") if p.strip()]
    return "; ".join(parts)


class IEEEExportLoader:
    """Load IEEE Xplore website exports and produce a corpus DataFrame."""

    def __init__(self, csv_path: str, bib_path: str) -> None:
        self.csv_path = Path(csv_path)
        self.bib_path = Path(bib_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"IEEE CSV not found: {self.csv_path}")
        if not self.bib_path.exists():
            raise FileNotFoundError(f"IEEE BIB not found: {self.bib_path}")

    def _load_csv(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path, dtype=str).fillna("")
        logger.info("IEEE CSV: %d rows loaded.", len(df))
        return df

    def _build_keywords(self, row: pd.Series) -> str:
        parts = []
        for col in _KEYWORD_COLS:
            val = row.get(col, "").strip()
            if val:
                parts.append(val)
        return "; ".join(parts)

    def load(self) -> pd.DataFrame:
        """Return a DataFrame conforming to config.CORPUS_COLUMNS."""
        raw = self._load_csv()
        bib_map = _parse_bib(self.bib_path)

        rows = []
        for _, row in raw.iterrows():
            doi = row.get("DOI", "").strip()
            doi_key = doi.lower()

            corpus_row: dict = {col: "" for col in config.CORPUS_COLUMNS}
            corpus_row["source"] = "ieee"
            corpus_row["is_duplicate"] = False
            corpus_row["corpus_id"] = ""
            corpus_row["duplicate_of"] = ""

            for csv_col, corpus_col in _CSV_MAP.items():
                corpus_row[corpus_col] = row.get(csv_col, "").strip()

            corpus_row["authors"] = _normalise_authors(corpus_row["authors"])
            corpus_row["keywords"] = self._build_keywords(row)
            corpus_row["pub_type"] = _infer_pub_type(corpus_row["journal"])
            corpus_row["doi"] = doi
            corpus_row["uid"] = doi if doi else f"ieee_{len(rows)}"
            corpus_row["bibtex"] = bib_map.get(doi_key, "")

            if not corpus_row["bibtex"]:
                logger.warning("No BIB entry found for DOI: %s", doi)

            rows.append(corpus_row)

        df = pd.DataFrame(rows, columns=config.CORPUS_COLUMNS)
        logger.info(
            "IEEE loader: %d records; %d matched to BIB entries.",
            len(df),
            (df["bibtex"] != "").sum(),
        )
        return df

    def write_clean_bib(self, out_path: str) -> None:
        """Write a clean, newline-separated .bib file to out_path."""
        bib_map = _parse_bib(self.bib_path)
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            for entry in bib_map.values():
                fh.write(entry.strip())
                fh.write("\n\n")
        logger.info("Wrote clean BIB with %d entries to %s", len(bib_map), out_path)
