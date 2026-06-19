"""Stage 2 — abstract screening and full-paper reading aid.

Reads outputs/corpus.pkl, runs Phase 1 abstract screening, writes
screening_results, then optionally runs the Phase 2 full-paper reading aid.

Usage:
    python run_screening.py [--skip-fullpaper]

Options:
    --skip-fullpaper   Run only the abstract screener (Phase 1).
                       Useful when full texts are not yet retrieved.
"""
