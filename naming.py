"""Standard names for included papers — single source of truth.

Format: {Surname}{Year}_{corpus_id}_{word1-word2-word3}
    e.g.  Sandmann2025_45_prompt-design-clinical

The same string is used as the PDF filename stem and as the BibTeX citation
key, so \\cite{X} <-> X.pdf is a mechanical lookup. Legal characters only:
ASCII letters, digits, underscore (field separator), hyphen (inside the
title segment). The corpus_id is the only all-digit field between
underscores, which keeps it machine-parseable.
"""

import re
import unicodedata

STOPWORDS = {
    "the", "a", "an", "of", "for", "in", "on", "with", "to", "and", "or",
    "at", "by", "from", "is", "are", "as", "its", "their", "can", "do",
    "does", "how", "what", "when", "via", "into", "using", "based",
}


def _ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def first_author_surname(authors: str) -> str:
    """First author's surname, ASCII, CamelCased compounds (van der Berg → VanDerBerg)."""
    first = authors.split(";")[0].strip()
    if not first:
        return "Anon"
    if "," in first:  # WoS style: "Li, Jia"
        surname = first.split(",")[0]
    else:  # "Sandmann S" (PubMed) or "P. D. Paikrao" (IEEE): drop initials
        tokens = [t for t in first.split() if len(t.rstrip(".")) > 2 and "." not in t]
        surname = tokens[-1] if tokens else first.split()[0]
    parts = [p for p in re.split(r"[\s\-]+", _ascii(surname)) if p]
    return "".join(p[0].upper() + p[1:] for p in parts) or "Anon"


def title_slug(title: str, n_words: int = 3) -> str:
    """First *n_words* meaningful title words, lowercase, hyphen-joined."""
    tokens = re.findall(r"[A-Za-z0-9]+", _ascii(title).lower())
    words = [t for t in tokens if t not in STOPWORDS and len(t) > 1][:n_words]
    return "-".join(words) or "untitled"


def standard_name(corpus_id, authors: str, year, title: str) -> str:
    """The canonical name: PDF filename stem == BibTeX key."""
    match = re.search(r"\d{4}", str(year))
    year_str = match.group(0) if match else "nd"
    surname = re.sub(r"[^A-Za-z0-9]", "", first_author_surname(authors))
    return f"{surname}{year_str}_{int(corpus_id)}_{title_slug(title)}"
