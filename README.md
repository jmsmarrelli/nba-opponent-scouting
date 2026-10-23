# Opponent scouting sheets

Joseph Smarrelli · September 2026

Completed 2025–26 scouting sheets for [Oklahoma City](reports/OKC_2025_26_scout.md), [Denver](reports/DEN_2025_26_scout.md) and [Houston](reports/HOU_2025_26_scout.md). Each includes offensive and defensive rate summaries, a location comparison and specific film-review questions.

## Run

Python 3.12 was used for this release. From the repository root:

```sh
python -m pip install -r requirements.txt
python -m src.fetch
python -m src.prepare
python -m src.scout
python -m pytest tests -q
python -m src.notebooks
```

The source fetch downloads two pinned public archives and verifies their hashes. Preparation reconciles event and shot records, retaining 1,212 league games. Derived summaries are included, so `python -m src.scout` also works without a raw download. The optional `--team OKC DEN HOU` argument selects teams; the three defaults have written review priorities.

## Definitions

Offensive-rebound percentage uses player offensive rebounds divided by those rebounds plus opponent player defensive rebounds. Team rebounds are excluded. Estimated possessions use FGA − player OREB + TOV + 0.44 × FTA. Turnover rate divides turnovers by that estimate; it is not the alternative FGA + 0.44 × FTA + TOV convention. These approximations are labeled on each sheet.

The defense panel summarizes opponent offense. Location figures describe attempts, not defensive positioning, openness or shot-clock behavior. Review priorities are questions for film work, not coded film observations or tested coverage recommendations. Current personnel need a separate check.

See [METHODS.md](METHODS.md) and [VALIDATION.md](VALIDATION.md) for source definitions and completed checks.

## Current review

See [current validation](VALIDATION_CURRENT.md) for executed checks and unresolved rebuild requirements, and [provenance](PROVENANCE.md) for AI assistance. [Portfolio navigation](https://github.com/jmsmarrelli/basketball-analytics).
