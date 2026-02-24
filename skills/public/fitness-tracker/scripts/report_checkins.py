#!/usr/bin/env python3

import argparse
import json

from db import ensure_db


def main() -> None:
    ap = argparse.ArgumentParser(description="Report recent weigh-ins / check-ins")
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args()

    conn = ensure_db()
    rows = conn.execute(
        """
        SELECT day, created_at, weight_lb, waist_in, steps, sleep_h, notes
        FROM checkins
        WHERE day >= date('now', ?)
        ORDER BY day DESC, created_at DESC
        """,
        (f"-{args.days} days",),
    ).fetchall()

    # Collapse to most recent checkin per day
    by_day = {}
    for r in rows:
        d = r["day"]
        if d not in by_day:
            by_day[d] = dict(r)

    payload = {
        "days": args.days,
        "entries": [by_day[d] for d in sorted(by_day.keys(), reverse=True)],
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
