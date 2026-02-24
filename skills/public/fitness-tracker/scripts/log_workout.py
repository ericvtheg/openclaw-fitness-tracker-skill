#!/usr/bin/env python3

import argparse
import json
import re
from typing import Any, Dict, List, Optional

from db import ensure_db, get_day, utc_now_iso


# Examples it will parse:
#   "Bench: 135x8, 140x8, 140x7"
#   "DB incline 55s 10,10,8"
SET_RE = re.compile(r"(?P<w>\d+(?:\.\d+)?)\s*(?P<unit>lb|lbs|kg)?\s*[x×]\s*(?P<reps>\d+)", re.I)


def parse_sets(text: str) -> List[Dict[str, Any]]:
    sets: List[Dict[str, Any]] = []
    for m in SET_RE.finditer(text):
        sets.append(
            {
                "weight": float(m.group("w")),
                "reps": int(m.group("reps")),
                "unit": (m.group("unit") or "lb").lower(),
            }
        )
    return sets


def guess_exercise(text: str) -> Optional[str]:
    if ":" in text:
        return text.split(":", 1)[0].strip()
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Log a workout entry")
    ap.add_argument("--text", required=True)
    ap.add_argument("--day", help="YYYY-MM-DD (defaults to local today)")
    ap.add_argument("--exercise", help="Exercise name override")

    args = ap.parse_args()

    day = get_day(args.day)
    exercise = args.exercise or guess_exercise(args.text)
    sets = parse_sets(args.text)

    meta: Dict[str, Any] = {}
    if sets:
        meta["parsed"] = True

    conn = ensure_db()
    conn.execute(
        """
        INSERT INTO workout_entries (day, created_at, raw_text, exercise, sets_json, meta_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            day,
            utc_now_iso(),
            args.text,
            exercise,
            json.dumps(sets) if sets else None,
            json.dumps(meta) if meta else None,
        ),
    )
    conn.commit()

    print(json.dumps({"ok": True, "day": day, "exercise": exercise, "set_count": len(sets)}, indent=2))


if __name__ == "__main__":
    main()
