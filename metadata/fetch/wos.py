"""Web of Science metadata loader from website RIS export.

Reads the .ris file exported from the WoS website and normalises it to
the pipeline corpus schema (config.CORPUS_COLUMNS). Also writes a clean
.bib file to outputs/.

Export instructions (WoS UI):
  1. Run your search → select all records → Export → RIS (other reference software)
  2. Select "Full Record" to include abstracts.
  3. Save the file to data/wos/ and set WOS_EXPORT_RIS in config.py.
"""

import logging
from pathlib import Path

import rispy
import pandas as pd

import config

logger = logging.getLogger(__name__)

# rispy key → corpus column  (rispy maps RIS two-letter tags to English names)
_RIS_MAP = {
    "accession_number":  "uid",
    "title":             "title",
    "secondary_title":   "journal",
    "year":              "year",
    "authors":           "authors",
    "doi":               "doi",
    "keywords":          "keywords",
    "abstract":          "abstract",
    "url":               "url",
    "type_of_work":      "pub_type",
}

# RIS type → BibTeX entry type
_RIS_TYPE_TO_BIBTEX = {
    "JOUR": "article",
    "CONF": "inproceedings",
    "CHAP": "incollection",
    "BOOK": "book",
    "RPRT": "techreport",
    "THES": "phdthesis",
    "GEN":  "misc",
}


def _make_bibtex_key(entry: dict) -> str:
    """Generate a citekey: FirstAuthorLastname + Year."""
    authors = entry.get("authors", [])
    first = authors[0].split(",")[0].strip().replace(" ", "") if authors else "Unknown"
    year = entry.get("year", "XXXX")
    uid = str(entry.get("accession_number", ""))[-4:]
    return f"{first}{year}_{uid}"


def _entry_to_bibtex(entry: dict, key: str) -> str:
    """Convert a rispy entry dict to a BibTeX string."""
    ris_type = entry.get("type_of_reference", "GEN")
    bib_type = _RIS_TYPE_TO_BIBTEX.get(ris_type, "misc")

    authors = entry.get("authors", [])
    author_str = " and ".join(authors)

    fields = {
        "author":  author_str,
        "title":   entry.get("title", ""),
        "journal": entry.get("secondary_title", ""),
        "year":    str(entry.get("year", "")),
        "volume":  str(entry.get("volume", "")),
        "number":  str(entry.get("number", "")),
        "pages":   f"{entry.get('start_page', '')}--{entry.get('end_page', '')}".strip("--"),
        "doi":     entry.get("doi", ""),
        "note":    str(entry.get("accession_number", "")),
    }
    # Drop empty fields
    body = "\n".join(
        f"  {k} = {{{v}}}," for k, v in fields.items() if v and v != "--"
    )
    return f"@{bib_type}{{{key},\n{body}\n}}"


class WoSExportLoader:
    """Load a WoS RIS export and produce a corpus DataFrame + clean .bib."""

    def __init__(self, ris_path: str) -> None:
        self.ris_path = Path(ris_path)
        if not self.ris_path.exists():
            raise FileNotFoundError(f"WoS RIS file not found: {self.ris_path}")

    def _parse_ris(self) -> list[dict]:
        with self.ris_path.open(encoding="utf-8") as fh:
            entries = rispy.load(fh)
        logger.info("WoS RIS: parsed %d entries.", len(entries))
        return entries

    def load(self) -> pd.DataFrame:
        """Return a DataFrame conforming to config.CORPUS_COLUMNS."""
        entries = self._parse_ris()
        rows = []
        for entry in entries:
            row: dict = {col: "" for col in config.CORPUS_COLUMNS}
            row["source"] = "wos"
            row["is_duplicate"] = False

            for ris_tag, corpus_col in _RIS_MAP.items():
                val = entry.get(ris_tag, "")
                if isinstance(val, list):
                    val = "; ".join(str(v) for v in val)
                row[corpus_col] = str(val) if val else ""

            key = _make_bibtex_key(entry)
            row["bibtex"] = _entry_to_bibtex(entry, key)
            rows.append(row)

        df = pd.DataFrame(rows, columns=config.CORPUS_COLUMNS)
        logger.info(
            "WoS loader: %d records, %d with abstracts, %d with DOIs.",
            len(df),
            (df["abstract"] != "").sum(),
            (df["doi"] != "").sum(),
        )
        return df

    def write_clean_bib(self, out_path: str) -> None:
        """Write a clean .bib file from all RIS entries to out_path."""
        entries = self._parse_ris()
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            for entry in entries:
                key = _make_bibtex_key(entry)
                fh.write(_entry_to_bibtex(entry, key))
                fh.write("\n\n")
        logger.info("Wrote clean BIB with %d entries to %s", len(entries), out_path)
