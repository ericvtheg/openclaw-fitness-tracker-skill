#!/usr/bin/env python3

import argparse
import json

from db import set_targets


def main() -> None:
    ap = argparse.ArgumentParser(description="Set daily macro targets")
    ap.add_argument("--kcal", type=float, required=True)
    ap.add_argument("--protein", type=float, required=True)
    ap.add_argument("--fat", type=float, required=True)
    ap.add_argument("--carbs", type=float)
    args = ap.parse_args()

    set_targets(args.kcal, args.protein, args.fat, args.carbs)
    print(json.dumps({"ok": True}, indent=2))


if __name__ == "__main__":
    main()
