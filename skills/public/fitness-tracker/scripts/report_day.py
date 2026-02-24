#!/usr/bin/env python3

import argparse
import json

from db import ensure_db, get_day, get_targets


def main() -> None:
    ap = argparse.ArgumentParser(description="Report totals for a day")
    ap.add_argument("--day", help="YYYY-MM-DD (defaults to local today)")
    args = ap.parse_args()

    day = get_day(args.day)
    conn = ensure_db()

    totals = conn.execute(
        """
        SELECT
          COALESCE(SUM(kcal), 0) AS kcal,
          COALESCE(SUM(protein_g), 0) AS protein_g,
          COALESCE(SUM(carbs_g), 0) AS carbs_g,
          COALESCE(SUM(fat_g), 0) AS fat_g,
          COUNT(*) AS entry_count
        FROM food_entries
        WHERE day = ?
        """,
        (day,),
    ).fetchone()

    items = conn.execute(
        """
        SELECT created_at, raw_text, item, kcal, protein_g, carbs_g, fat_g, confidence, source
        FROM food_entries
        WHERE day = ?
        ORDER BY created_at ASC
        """,
        (day,),
    ).fetchall()

    payload = {
        "day": day,
        "targets": get_targets(),
        "totals": dict(totals),
        "entries": [dict(r) for r in items],
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
