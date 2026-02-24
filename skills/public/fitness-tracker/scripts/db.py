#!/usr/bin/env python3

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

APP_DIR = Path(os.environ.get("OPENCLAW_FITNESS_DIR", "~/.config/openclaw-fitness-tracker")).expanduser()
DB_PATH = APP_DIR / "db.sqlite"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_db() -> sqlite3.Connection:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS food_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          day TEXT NOT NULL,              -- YYYY-MM-DD
          created_at TEXT NOT NULL,       -- ISO UTC
          raw_text TEXT NOT NULL,
          item TEXT,
          qty REAL,
          unit TEXT,
          kcal REAL,
          protein_g REAL,
          carbs_g REAL,
          fat_g REAL,
          confidence TEXT NOT NULL,       -- exact|estimate|unknown
          source TEXT,                    -- label|restaurant|off|usda|manual|other
          meta_json TEXT                  -- arbitrary JSON
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          day TEXT NOT NULL,
          created_at TEXT NOT NULL,
          raw_text TEXT NOT NULL,
          exercise TEXT,
          sets_json TEXT,                 -- JSON array of {weight, reps, unit}
          meta_json TEXT
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS presets (
          key TEXT PRIMARY KEY,
          kind TEXT NOT NULL,            -- food|workout
          value_json TEXT NOT NULL
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_targets (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          kcal REAL,
          protein_g REAL,
          fat_g REAL,
          carbs_g REAL
        );
        """
    )

    conn.commit()
    return conn


def get_day(day: Optional[str]) -> str:
    if day:
        return day
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def set_targets(kcal: float, protein_g: float, fat_g: float, carbs_g: Optional[float] = None) -> None:
    conn = ensure_db()
    conn.execute(
        "INSERT INTO daily_targets (id, kcal, protein_g, fat_g, carbs_g) VALUES (1, ?, ?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET kcal=excluded.kcal, protein_g=excluded.protein_g, fat_g=excluded.fat_g, carbs_g=excluded.carbs_g",
        (kcal, protein_g, fat_g, carbs_g),
    )
    conn.commit()


def get_targets() -> Dict[str, Any]:
    conn = ensure_db()
    row = conn.execute("SELECT kcal, protein_g, fat_g, carbs_g FROM daily_targets WHERE id=1").fetchone()
    if not row:
        return {}
    return dict(row)


def upsert_preset(key: str, kind: str, value: Dict[str, Any]) -> None:
    conn = ensure_db()
    conn.execute(
        "INSERT INTO presets (key, kind, value_json) VALUES (?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET kind=excluded.kind, value_json=excluded.value_json",
        (key, kind, json.dumps(value)),
    )
    conn.commit()


def get_preset(key: str) -> Optional[Dict[str, Any]]:
    conn = ensure_db()
    row = conn.execute("SELECT value_json FROM presets WHERE key=?", (key,)).fetchone()
    if not row:
        return None
    return json.loads(row["value_json"])
