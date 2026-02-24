#!/usr/bin/env python3

import argparse
import json

from db import ensure_db, get_day, utc_now_iso


def main() -> None:
    ap = argparse.ArgumentParser(description="Log an injury/pain note")
    ap.add_argument("--text", required=True, help="Raw user text")
    ap.add_argument("--day", help="YYYY-MM-DD (defaults to local today)")
    ap.add_argument("--area", help="Body area, e.g. left scapula, right ankle")
    ap.add_argument("--severity", type=float, help="0-10 pain scale")
    ap.add_argument("--status", default="active", choices=["active", "improving", "resolved", "flare"], help="Status tag")
    args = ap.parse_args()

    day = get_day(args.day)
    conn = ensure_db()

    conn.execute(
        """
        INSERT INTO injury_entries (day, created_at, raw_text, area, severity, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (day, utc_now_iso(), args.text, args.area, args.severity, args.status),
    )
    conn.commit()

    print(json.dumps({"ok": True, "day": day}, indent=2))


if __name__ == "__main__":
    main()
