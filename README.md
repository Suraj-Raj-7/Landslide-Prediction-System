# Landslide Early-Warning System for Himachal Pradesh

M.Tech ICTD course project, IIT Delhi (Suraj Raj).

A daily landslide early-warning system for Himachal Pradesh (HP). Each day it combines fixed terrain conditions with recent and forecast rainfall, soil moisture and snow, estimates landslide risk, and emails the districts at high risk to the relevant authorities. Landslide events from Uttarakhand and Jammu & Kashmir are added to the training data because HP alone has too few dated events; predictions are made for HP only.

All processing runs on Google Earth Engine (GEE) through its Python API, using free data only.

## Status (9 Nov 2026)

| Phase | What | Status |
|---|---|---|
| A | Landslide inventory (981 events) and 42 features per event | Done |
| B | "No-landslide" examples and training table (3,136 rows) | Done |
| C | Models, year-blocked testing; live model on IMERG + fixed features | Done |
| E | Storm replays (16 storm days, 16 quiet days); final alert rule | Done |
| D | Daily run, email, web page (GitHub Actions) | Built and tested; switching on |
| F | Final report and presentation | In progress |

## How the alerts work
Every 1 km square of HP gets a daily risk score. A square is at Watch at ≥ 0.376 and at Warning at ≥ 0.463; a district is put at a level when at least 30% of its squares within 500 m of a road reach it. In replays of past storms this caught 86% of the districts with recorded landslides at Watch, with false alarms on 15% of quiet district-days. Plain-language explanation: `docs/alert_rule_explained.md`.

## Daily system
`src/live_03_daily_run.py`, run every morning by `.github/workflows/daily.yml`. Setup, reasons and monthly upkeep: `docs/daily_system_setup.md`.

## Folder layout

```
src/                Python code (Earth Engine feature modules and step scripts)
data/               Tables and files produced by each step (step2/ … step6/, hot_aoi/)
docs/               Technical documentation
models/             Trained models (from Phase C)
.github/workflows/  Daily run on GitHub Actions
gee_scripts_repo/   Clone of the GEE Code Editor repository (users/rajsuraj777/ICTD_Landslides_Project)
CHANGELOG.md        Work log: what was changed, why, evidence, how to undo
requirements.txt    Python packages
```

Key files:
- `data/positives_v5.csv`: cleaned landslide inventory (981 events).
- `data/positives_features_v1_local.csv`: final feature table (981 events × 42 features).
- `docs/ICTD_Landslide_Feature_Stack_Documentation.md`: how every feature was built, checked and why.

## Setup

Windows, Python 3.13.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install --no-cache-dir -r requirements.txt
.venv/Scripts/earthengine authenticate   # once per machine
```

GEE cloud project: `idyllic-return-468714-j4`.

## Running code

Always use the venv Python. Scripts in `src/` import each other directly, so run them from the project root:

```bash
.venv/Scripts/python -W ignore src/10_step1_terrain_run.py data
```

Quick check that the feature stack loads:

```bash
.venv/Scripts/python -W ignore -c "import sys; sys.path.insert(0,'src'); import ee; ee.Initialize(project='idyllic-return-468714-j4'); import stack; print(len(stack.all_bands()))"
```

## Data sources

Copernicus GLO-30 DEM, MERIT Hydro, OpenStreetMap roads, GSI/NGDR lithology, faults and geomorphology, ESA WorldCover 2021, Landsat Collection 2, GPM IMERG V07, CHIRPS, ERA5-Land, geoBoundaries. Landslide events: Bhusanket (GSI) and the NASA Global Landslide Catalog. Full references are in the documentation.
