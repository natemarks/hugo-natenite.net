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
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def format_datetime(date_str, time_str):
    return date_str.replace("-", "") + "T" + time_str.replace(":", "") + "00"


def until_utc(end_date_str, tzid):
    """RRULE's UNTIL must be a real UTC instant -- convert local end-of-day
    in the event's own timezone, rather than treating the local date as if
    it were already UTC (which would shift it by the zone's offset)."""
    local_end_of_day = datetime.strptime(end_date_str, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=ZoneInfo(tzid)
    )
    return local_end_of_day.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_vevent(event, dtstamp):
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
        lines.append(f"RRULE:FREQ=WEEKLY;BYDAY={event['dayOfWeek']};UNTIL={until}")

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
    return "\r\n".join(lines) + "\r\n", included, skipped


def main():
    data = json.loads(EVENTS_PATH.read_text())
    events = data["events"]
    ics_text, included, skipped = build_ics(events)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(ics_text)
    print(f"Wrote {included} event(s) to {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    for event_id, err in skipped:
        print(f"Skipped event {event_id!r}: {err}", file=sys.stderr)
    if skipped:
        return 1


if __name__ == "__main__":
    sys.exit(main())
