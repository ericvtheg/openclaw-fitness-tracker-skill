#!/usr/bin/env python3

import argparse
import json

from db import ensure_db, get_day, utc_now_iso


def main() -> None:
    ap = argparse.ArgumentParser(description="Log a weigh-in / daily check-in")
    ap.add_argument("--day", help="YYYY-MM-DD (defaults to local today)")
    ap.add_argument("--weight", type=float, help="Morning weight in lb")
    ap.add_argument("--waist", type=float, help="Waist at navel in inches")
    ap.add_argument("--steps", type=int, help="Steps for the day (optional)")
    ap.add_argument("--sleep", type=float, help="Sleep hours (optional)")
    ap.add_argument("--notes", help="Freeform notes")
    args = ap.parse_args()

    day = get_day(args.day)
    conn = ensure_db()

    conn.execute(
        """
        INSERT INTO checkins (day, created_at, weight_lb, waist_in, steps, sleep_h, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (day, utc_now_iso(), args.weight, args.waist, args.steps, args.sleep, args.notes),
    )
    conn.commit()

    print(json.dumps({"ok": True, "day": day}, indent=2))


if __name__ == "__main__":
    main()
