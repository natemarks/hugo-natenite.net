#!/usr/bin/env python3
"""Sync data/events.json into a generated static/events.ics feed.

data/events.json is the event store for now: a hand-edited JSON file,
each event keyed by a stable `id`. That `id` becomes the ICS VEVENT's UID
(never shown in the calendar UI) so that if the store later moves to
something else (sqlite, etc.), a real incremental sync can still recognize
"this is the same event" across edits. This version regenerates the whole
feed from scratch on every run -- simple, and safe as long as the store
stays small and hand-edited.

data/events.example.json is a reference template only (worked examples of
both recurrenceTypes) -- it is never read by this script. Copy entries from
it into data/events.json's real "events" array to publish them.

Usage: python3 scripts/sync_calendar.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = REPO_ROOT / "data" / "events.json"
OUTPUT_PATH = REPO_ROOT / "static" / "events.ics"
UID_DOMAIN = "natenite.net"


def escape_ics_text(value):
    """Escape RFC 5545 TEXT special characters: backslash, comma, semicolon, newline."""
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def format_datetime(date_str, time_str):
    """Combine YYYY-MM-DD and HH:MM into an ICS local DATE-TIME value."""
    return date_str.replace("-", "") + "T" + time_str.replace(":", "") + "00"


def fold_ics_line(line):
    """Fold a single ICS content line per RFC 5545 3.1: lines over 75
    octets are split across multiple physical lines, each continuation
    line prefixed with a single space, without ever splitting a
    multi-byte UTF-8 character across the boundary."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line

    chunks = []
    start = 0
    limit = 75
    while start < len(encoded):
        end = min(start + limit, len(encoded))
        while start < end < len(encoded) and (encoded[end] & 0xC0) == 0x80:
            end -= 1
        chunks.append(encoded[start:end].decode("utf-8"))
        start = end
        limit = 74  # continuation lines lose one octet to the leading space
    return "\r\n ".join(chunks)


class ICSValidationError(Exception):
    """Raised when generated ICS output fails structural validation."""


def validate_ics(ics_text):
    """Structurally validate generated ICS text before it's written --
    a bug in the generator should fail loudly, not silently publish a
    broken feed. Checks balanced BEGIN/END pairs and that every VEVENT
    carries its required fields; this is not a full RFC 5545 parser."""
    lines = ics_text.split("\r\n")
    if lines and lines[-1] == "":
        lines.pop()

    if not lines or lines[0] != "BEGIN:VCALENDAR":
        raise ICSValidationError("Missing BEGIN:VCALENDAR as the first line")
    if lines[-1] != "END:VCALENDAR":
        raise ICSValidationError("Missing END:VCALENDAR as the last line")

    required_vevent_fields = ("UID:", "DTSTAMP:", "DTSTART", "SUMMARY:")
    in_vevent = False
    vevent_lines = []
    for line in lines:
        if line == "BEGIN:VEVENT":
            if in_vevent:
                raise ICSValidationError(
                    "Nested BEGIN:VEVENT without a matching END:VEVENT"
                )
            in_vevent = True
            vevent_lines = []
        elif line == "END:VEVENT":
            if not in_vevent:
                raise ICSValidationError(
                    "END:VEVENT without a matching BEGIN:VEVENT"
                )
            for field in required_vevent_fields:
                if not any(l.startswith(field) for l in vevent_lines):
                    raise ICSValidationError(
                        f"VEVENT missing required field {field!r}"
                    )
            in_vevent = False
        elif in_vevent:
            vevent_lines.append(line)

    if in_vevent:
        raise ICSValidationError("BEGIN:VEVENT without a matching END:VEVENT")


def until_utc(end_date_str, tzid):
    """RRULE's UNTIL must be a real UTC instant -- convert local end-of-day
    in the event's own timezone, rather than treating the local date as if
    it were already UTC (which would shift it by the zone's offset)."""
    local_end_of_day = datetime.strptime(end_date_str, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=ZoneInfo(tzid)
    )
    return local_end_of_day.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_vevent(event, dtstamp):
    """Build the ICS lines for a single event's VEVENT block."""
    recurrence_type = event["recurrenceType"]
    if recurrence_type == "weekly":
        start_date = event["startDate"]
    elif recurrence_type == "once":
        start_date = event["date"]
    else:
        raise ValueError(
            f"Unknown recurrenceType {recurrence_type!r} for event {event['id']!r}"
        )

    tzid = event["timezone"]
    lines = [
        "BEGIN:VEVENT",
        f"UID:{event['id']}@{UID_DOMAIN}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;TZID={tzid}:{format_datetime(start_date, event['startTime'])}",
        f"DTEND;TZID={tzid}:{format_datetime(start_date, event['endTime'])}",
    ]

    if recurrence_type == "weekly":
        until = until_utc(event["endDate"], tzid)
        lines.append(
            f"RRULE:FREQ=WEEKLY;BYDAY={event['dayOfWeek']};UNTIL={until}"
        )

    lines += [
        f"SUMMARY:{escape_ics_text(event['title'])}",
        f"LOCATION:{escape_ics_text(event['location'])}",
        f"DESCRIPTION:{escape_ics_text(event['notes'])}",
        "END:VEVENT",
    ]
    return lines


def build_ics(events):
    """Skip and report a malformed event rather than aborting the whole
    sync -- one bad entry in the store shouldn't take down every other
    event's feed."""
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//natenite.net//lacrosse-calendar//EN",
        "CALSCALE:GREGORIAN",
    ]
    included, skipped = 0, []
    for event in events:
        try:
            lines.extend(build_vevent(event, dtstamp))
            included += 1
        except (KeyError, ValueError) as err:
            skipped.append((event.get("id", "<no id>"), err))
    lines.append("END:VCALENDAR")
    folded = "\r\n".join(fold_ics_line(line) for line in lines) + "\r\n"
    return folded, included, skipped


def main():
    """Regenerate static/events.ics from data/events.json. Returns a process
    exit code: 0 if every event synced cleanly, 1 if any were skipped, 2 if
    the generated output failed structural validation (nothing is written
    in that case -- a bug in the generator must not overwrite a good feed
    with a broken one)."""
    data = json.loads(EVENTS_PATH.read_text())
    events = data["events"]
    ics_text, included, skipped = build_ics(events)

    try:
        validate_ics(ics_text)
    except ICSValidationError as err:
        print(f"Refusing to write invalid ICS output: {err}", file=sys.stderr)
        return 2

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(ics_text)
    print(f"Wrote {included} event(s) to {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    for event_id, skip_err in skipped:
        print(f"Skipped event {event_id!r}: {skip_err}", file=sys.stderr)
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
