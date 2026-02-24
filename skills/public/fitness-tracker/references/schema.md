# SQLite schema (local, private)

DB location by default:
- `~/.config/openclaw-fitness-tracker/db.sqlite`

Tables:
- `food_entries`: day-level nutrition entries with optional macros and confidence
- `workout_entries`: workout log lines with optional parsed sets
- `injury_entries`: injury/pain notes (area, severity, status)
- `checkins`: daily check-ins (weight, waist, optional steps/sleep)
- `presets`: reusable shortcuts ("cava-usual", "sweetfin-usual", etc.)
- `daily_targets`: calories and macro targets
