"""Tests for scripts/sync_calendar.py.

Covers: the pure datetime/escaping helpers, RFC 5545 line-folding,
structural .ics validation, and fixture-based coverage of the
generator's own output shape (recurring event, one-off event, and a
deliberately incomplete entry that must be skipped, not silently
included). Assertions target the generator's own output directly, not
a third-party ICS parser or the calendar library -- that rendering
behavior is already covered manually (see issue #2).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import sync_calendar  # noqa: E402  pylint: disable=wrong-import-position

RECURRING_EVENT = {
    "id": "test-recurring",
    "title": "Test Recurring Event",
    "location": "123 Test St",
    "notes": "Test notes",
    "recurrenceType": "weekly",
    "dayOfWeek": "TU",
    "startDate": "2026-09-22",
    "endDate": "2026-11-10",
    "startTime": "20:00",
    "endTime": "21:00",
    "timezone": "America/New_York",
}

ONEOFF_EVENT = {
    "id": "test-oneoff",
    "title": "Test One-off Event",
    "location": "456 Test Ave",
    "notes": "Test notes",
    "recurrenceType": "once",
    "date": "2026-10-18",
    "startTime": "09:00",
    "endTime": "10:00",
    "timezone": "America/New_York",
}

INCOMPLETE_EVENT = {
    **ONEOFF_EVENT,
    "id": "test-incomplete",
    "title": "Missing Fields Event",
}
del INCOMPLETE_EVENT["endTime"]  # the field deliberately missing


def unfold(folded):
    """Reverse fold_ics_line: join a CRLF-folded line back into one string
    by stripping the leading space each continuation line carries."""
    physical_lines = folded.split("\r\n")
    return physical_lines[0] + "".join(pl[1:] for pl in physical_lines[1:])


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


@pytest.mark.unit
def test_fold_ics_line_leaves_short_lines_unchanged():
    """A line under 75 octets needs no folding at all."""
    assert sync_calendar.fold_ics_line("SUMMARY:short") == "SUMMARY:short"


@pytest.mark.unit
def test_fold_ics_line_folds_long_lines_with_leading_space_continuation():
    """RFC 5545 3.1: lines over 75 octets fold onto CRLF + a single space,
    and unfolding (stripping that CRLF+space) must reconstruct the original."""
    line = "SUMMARY:" + ("x" * 100)
    folded = sync_calendar.fold_ics_line(line)
    physical_lines = folded.split("\r\n")

    assert len(physical_lines) > 1
    assert all(len(pl.encode("utf-8")) <= 75 for pl in physical_lines)
    assert all(pl.startswith(" ") for pl in physical_lines[1:])
    assert unfold(folded) == line


@pytest.mark.unit
def test_fold_ics_line_does_not_split_a_multibyte_utf8_character():
    """A naive 75-byte cut lands mid-character here (multi-byte emoji padding
    around the boundary) -- folding must never produce an invalid string, and
    unfolding must still exactly reconstruct the original."""
    line = "DESCRIPTION:" + ("a" * 70) + ("\U0001f600" * 5)
    folded = sync_calendar.fold_ics_line(line)
    physical_lines = folded.split("\r\n")

    assert all(len(pl.encode("utf-8")) <= 75 for pl in physical_lines)
    assert unfold(folded) == line


@pytest.mark.unit
def test_validate_ics_accepts_a_well_formed_calendar():
    """The generator's own well-formed output must pass validation."""
    ics_text, _, _ = sync_calendar.build_ics([RECURRING_EVENT])
    sync_calendar.validate_ics(ics_text)  # must not raise


@pytest.mark.unit
def test_validate_ics_rejects_missing_end_vcalendar():
    """A truncated calendar (no closing END:VCALENDAR) must be rejected."""
    broken = "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nEND:VEVENT\r\n"
    with pytest.raises(sync_calendar.ICSValidationError):
        sync_calendar.validate_ics(broken)


@pytest.mark.unit
def test_validate_ics_rejects_vevent_missing_required_field():
    """A VEVENT missing SUMMARY (and DTSTART/DTSTAMP) must be rejected."""
    broken = (
        "BEGIN:VCALENDAR\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:x@y\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    with pytest.raises(sync_calendar.ICSValidationError):
        sync_calendar.validate_ics(broken)


@pytest.mark.unit
def test_validate_ics_rejects_unbalanced_vevent():
    """A BEGIN:VEVENT with no matching END:VEVENT must be rejected."""
    broken = "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nEND:VCALENDAR\r\n"
    with pytest.raises(sync_calendar.ICSValidationError):
        sync_calendar.validate_ics(broken)


@pytest.mark.unit
def test_build_ics_recurring_event_is_one_vevent_with_rrule():
    """A weekly-recurring event is a single VEVENT with an RRULE, not one
    VEVENT per occurrence."""
    ics_text, included, skipped = sync_calendar.build_ics([RECURRING_EVENT])

    assert included == 1
    assert not skipped
    assert ics_text.count("BEGIN:VEVENT") == 1
    assert "RRULE:FREQ=WEEKLY;BYDAY=TU;UNTIL=20261111T045959Z" in ics_text
    assert "SUMMARY:Test Recurring Event" in ics_text


@pytest.mark.unit
def test_build_ics_oneoff_event_has_no_rrule():
    """A one-off event is a single VEVENT with no RRULE at all."""
    ics_text, included, skipped = sync_calendar.build_ics([ONEOFF_EVENT])

    assert included == 1
    assert not skipped
    assert ics_text.count("BEGIN:VEVENT") == 1
    assert "RRULE" not in ics_text
    assert "SUMMARY:Test One-off Event" in ics_text


@pytest.mark.unit
def test_build_ics_skips_incomplete_event_without_aborting_the_rest():
    """A deliberately incomplete entry is excluded and flagged -- the
    valid events on either side of it still sync normally."""
    ics_text, included, skipped = sync_calendar.build_ics(
        [RECURRING_EVENT, INCOMPLETE_EVENT, ONEOFF_EVENT]
    )

    assert included == 2
    assert len(skipped) == 1
    assert skipped[0][0] == "test-incomplete"
    assert ics_text.count("BEGIN:VEVENT") == 2
    assert "Missing Fields Event" not in ics_text
    # The valid events either side of the bad one must still be present.
    assert "Test Recurring Event" in ics_text
    assert "Test One-off Event" in ics_text


@pytest.mark.unit
def test_build_ics_folds_a_long_field_end_to_end():
    """Folding must actually fire through the real build_ics/build_vevent
    pipeline on a realistic long field, not just on fold_ics_line in
    isolation -- confirms the two aren't accidentally disconnected."""
    long_notes = "Directions and parking details: " + ("x" * 80)
    event = {**ONEOFF_EVENT, "id": "test-long-notes", "notes": long_notes}
    ics_text, included, skipped = sync_calendar.build_ics([event])

    assert included == 1
    assert not skipped

    # Locate the folded DESCRIPTION block: from "DESCRIPTION:" up to (but
    # not including) the next unfolded (non-continuation) line.
    physical_lines = ics_text.split("\r\n")
    start = next(
        i
        for i, line in enumerate(physical_lines)
        if line.startswith("DESCRIPTION:")
    )
    end = start + 1
    while end < len(physical_lines) and physical_lines[end].startswith(" "):
        end += 1
    folded_block = "\r\n".join(physical_lines[start:end])

    assert end - start > 1  # it actually folded onto more than one line
    assert (
        unfold(folded_block)
        == f"DESCRIPTION:{sync_calendar.escape_ics_text(long_notes)}"
    )
