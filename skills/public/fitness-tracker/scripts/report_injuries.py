#!/usr/bin/env python3

import argparse
import json

from db import ensure_db


def main() -> None:
    ap = argparse.ArgumentParser(description="List recent injury/pain notes")
    ap.add_argument("--days", type=int, default=30, help="Lookback window")
    args = ap.parse_args()

    conn = ensure_db()
    rows = conn.execute(
        """
        SELECT day, created_at, area, severity, status, raw_text
        FROM injury_entries
        WHERE day >= date('now', ?)
        ORDER BY created_at DESC
        """,
        (f"-{args.days} days",),
    ).fetchall()

    print(json.dumps({"entries": [dict(r) for r in rows]}, indent=2))


if __name__ == "__main__":
    main()
