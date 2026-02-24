#!/usr/bin/env python3

import argparse
import json
import re
from typing import Any, Dict, Optional, Tuple

from db import ensure_db, get_day, get_preset, upsert_preset, utc_now_iso


QTY_RE = re.compile(r"(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>g|gram|grams|oz|lb|ml|cup|cups|tbsp|tsp|serving|servings)\b", re.I)


def parse_simple_qty(text: str) -> Tuple[Optional[float], Optional[str]]:
    m = QTY_RE.search(text)
    if not m:
        return None, None
    return float(m.group("qty")), m.group("unit").lower()


def main() -> None:
    ap = argparse.ArgumentParser(description="Log a food entry (with optional macros).")
    ap.add_argument("--text", required=True, help="Raw user text")
    ap.add_argument("--day", help="YYYY-MM-DD (defaults to local today)")
    ap.add_argument("--item", help="Normalized item name")
    ap.add_argument("--kcal", type=float)
    ap.add_argument("--protein", type=float)
    ap.add_argument("--carbs", type=float)
    ap.add_argument("--fat", type=float)
    ap.add_argument("--confidence", choices=["exact", "estimate", "unknown"], default="unknown")
    ap.add_argument("--source", default="manual")
    ap.add_argument("--preset", help="If set, save this entry as a reusable preset key")
    ap.add_argument("--use-preset", help="Log by preset key instead of macros")

    args = ap.parse_args()

    day = get_day(args.day)
    conn = ensure_db()

    if args.use_preset:
        preset = get_preset(args.use_preset)
        if not preset:
            raise SystemExit(f"Preset not found: {args.use_preset}")
        payload = preset
        args.item = payload.get("item")
        args.kcal = payload.get("kcal")
        args.protein = payload.get("protein_g")
        args.carbs = payload.get("carbs_g")
        args.fat = payload.get("fat_g")
        args.confidence = payload.get("confidence", "estimate")
        args.source = payload.get("source", "preset")

    qty, unit = parse_simple_qty(args.text)

    meta: Dict[str, Any] = {}
    if qty is not None:
        meta["parsed_qty"] = qty
        meta["parsed_unit"] = unit

    conn.execute(
        """
        INSERT INTO food_entries (
          day, created_at, raw_text, item, qty, unit,
          kcal, protein_g, carbs_g, fat_g,
          confidence, source, meta_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            day,
            utc_now_iso(),
            args.text,
            args.item,
            qty,
            unit,
            args.kcal,
            args.protein,
            args.carbs,
            args.fat,
            args.confidence,
            args.source,
            json.dumps(meta) if meta else None,
        ),
    )
    conn.commit()

    if args.preset:
        upsert_preset(
            args.preset,
            "food",
            {
                "item": args.item or args.text,
                "kcal": args.kcal,
                "protein_g": args.protein,
                "carbs_g": args.carbs,
                "fat_g": args.fat,
                "confidence": args.confidence,
                "source": args.source,
            },
        )

    print(json.dumps({"ok": True, "day": day}, indent=2))


if __name__ == "__main__":
    main()
