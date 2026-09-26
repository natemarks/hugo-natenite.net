"""Minimal smoke tests for scripts/sync_calendar.py.

Full fixture-based coverage (VEVENT/RRULE shape, error isolation,
structural .ics validation) is tracked in issue #4 -- this just keeps
`make unit` meaningful rather than an empty test suite.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import sync_calendar  # noqa: E402  pylint: disable=wrong-import-position


@pytest.mark.unit
def test_until_utc_converts_local_end_of_day_to_utc():
    """RRULE UNTIL must be a real UTC instant, not the local date verbatim."""
    # America/New_York is UTC-5 in November (EST, no DST).
    assert sync_calendar.until_utc("2026-11-10", "America/New_York") == (
        "20261111T045959Z"
    )


@pytest.mark.unit
def test_escape_ics_text_escapes_commas_semicolons_and_newlines():
    """RFC 5545 TEXT special characters must be backslash-escaped."""
    assert sync_calendar.escape_ics_text("A, B; C\nD") == "A\\, B\\; C\\nD"
