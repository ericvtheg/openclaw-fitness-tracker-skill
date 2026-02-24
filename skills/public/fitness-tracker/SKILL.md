---
name: fitness-tracker
description: Track nutrition (calories and macros) and workouts from plain-text messages. Use when the user texts what they ate (with grams/servings or restaurant orders) and wants running daily totals, macro targets, estimates vs exact entries, and saved "usual" presets. Also use when the user texts workout sets/reps/weight, asks for training suggestions at the gym, or wants trends like volume, PRs, and adherence to a cut plan.
---

# Fitness Tracker

Maintain a private local SQLite log of food and workouts, while keeping the skill and code open source.

## Data storage

- Local DB: `~/.config/openclaw-fitness-tracker/db.sqlite`
- Scripts live in `scripts/` and should be invoked via `python3 <script> ...`
- User logs are private and must never be committed.

## Quick start

1. Set daily targets:

```bash
python3 scripts/set_targets.py --kcal 2200 --protein 195 --fat 65
```

2. Log food (with known macros):

```bash
python3 scripts/log_food.py --text "200g chicken breast" --item "chicken breast" --kcal 330 --protein 62 --carbs 0 --fat 7 --confidence exact --source label
```

3. Log food (unknown macros):
- Estimate macros using web sources or reasonable ingredient breakdown.
- Log with `--confidence estimate` and include `--source restaurant|other`.

4. Get day totals:

```bash
python3 scripts/report_day.py
```

5. Log a workout line:

```bash
python3 scripts/log_workout.py --text "Bench: 135x8, 140x8, 140x7"
```

## Workflow: logging nutrition from chat

When the user texts food:

1. Extract day context (default to today).
2. **Weights default to cooked** unless the user explicitly says raw.
3. If macros are provided, log directly.
4. If macros are missing:
   - Prefer **official nutrition** (label, restaurant nutrition page).
   - If not available, estimate using a reasonable ingredient breakdown and mark `confidence=estimate`.
   - Ask only 1 clarifying question when it materially changes the answer (for example raw vs cooked for rice/pasta/meat, or missing restaurant item details).
   - For restaurant estimates, after logging: offer to save as a preset (or save once the user confirms it looks right).
5. Reply with:
   - Item macros
   - Running totals for the day
   - Remaining targets (if targets exist)

### Presets ("usuals")

If the user repeats an order, save it:

```bash
python3 scripts/log_food.py --text "CAVA usual" --kcal 805 --protein 52 --carbs 72 --fat 33 --confidence estimate --source restaurant --preset cava-usual
```

Then later:

```bash
python3 scripts/log_food.py --text "cava usual" --use-preset cava-usual
```

## Workflow: logging workouts from chat

When the user texts sets/reps/weight:

1. Log the raw text.
2. If it contains `weight x reps` patterns (for example `135x8`), `log_workout.py` will parse sets.
3. Reply with a concise confirmation and, if helpful, a quick summary (set count, main lift, etc.).

## Workflow: tracking injuries/pain

When the user mentions pain or injuries (for example left scap/upper back pain, pressing pain, right ankle pain):

1. Log an injury note with `log_injury.py`.
2. Track optional fields:
   - `area` (left scapula, left chest/armpit, right ankle)
   - `severity` (0-10)
   - `status` (active/improving/resolved/flare)
3. When generating a workout recommendation, always respect active injury notes and any pain rules (for example modified pressing).

## Reporting conventions

- Always distinguish "exact" vs "estimate".
- If estimates are used for restaurant items, note assumptions briefly.
- Prefer calories and macros in grams.

## References

- DB schema: `references/schema.md`
