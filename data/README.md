# Data: what each folder holds

Every file here was made by a script in `src/` (see [src/README.md](../src/README.md)). Tables are CSV files: open them in Excel, Google Sheets or Python (pandas).

**One row = one thing.** In the landslide tables one row is one landslide. In the training table one row is one landslide or one "no landslide" example. In the district tables one row is one district on one day.

## The most important files

| File | What it is |
|---|---|
| `positives_v5.csv` | The cleaned list of **981 dated landslides** (2005–2026) in Himachal Pradesh (195), Uttarakhand (548) and Jammu & Kashmir (238): place, date, source |
| `positives_features_v1_local.csv` | The same landslides with all **42 measured features** (terrain, rock, roads, vegetation, rain, snow) |
| `phaseB/training_table_v1.csv` | What the model learned from: **3,136 rows** = 969 landslides + 969 same-place safe days + 1,198 similar slopes on storm days that did not slide |
| `live/grid_live.csv.gz` | The **HP grid used by the daily system**: 55,253 squares of 1 km with their fixed features, district and vegetation (refreshed monthly) |
| `live/hp_districts.geojson` | Outlines of HP's 12 districts, for the maps |

## Folder by folder

| Folder | What is inside | Made by |
|---|---|---|
| (main folder) | Landslide list and its features; `step0_changes_log.csv` lists every correction made to the landslide records, with the reason; `step0_states_map.png` maps them; `_gaps.txt` counts missing values per feature | Step 0–7 scripts |
| `step2/` … `step6/` | Features for every landslide, one step at a time (drainage and roads, rock and faults, land cover, vegetation, rain), before they were joined | Feature scripts |
| `hot_aoi/` | Road buffers used to choose the study areas in Uttarakhand and J&K | Early setup |
| `legacy/` | The older "no landslide" examples from September, kept for comparison | September prototype |
| `phaseB/` | "No landslide" examples (Type 1 and Type 2) and the training table | `phaseB_*.py` |
| `phaseC/` | Model test results: scores, predictions, alert-threshold tables, importance and partial-dependence charts, rain-product test | `phaseC_*.py` |
| `phaseD/` | Whole-HP maps of 14 Aug 2023 (storm) and 12 Sep 2023 (quiet day): scores per square, district levels, recorded landslides | `phaseD_*.py` |
| `phaseE/` | Storm replays: the chosen days, every district rule tried, the checks of the chosen rule, uncertainty | `phaseE_*.py` |
| `impact/` | Whole-monsoon replays of 2023 and 2025: one row per district per day, and a summary per district | `impact_01_monsoon_replay.py` |
| `live/` | Files the daily system needs (grid, district outlines, information about the grid) | `live_01_monthly_grid.py` |

Files ending in `.log` record the Earth Engine jobs and runs that made the results (job IDs, timings).

## Large files kept only on the computer
A few large files are not uploaded, because a script can make them again. They are listed in `.gitignore`.

| File(s) | Size | How to make them again |
|---|---|---|
| `phaseD/storm_*_features.csv` | about 35–38 MB each | Run `src/phaseD_03_storm_map.py` with the same date; it downloads them from Earth Engine |
| `phaseE/scores/` | about 62 MB | `src/phaseE_03_replay_scores.py` |
| `live/grid_pending.json` | tiny | A temporary note written by `live_01_monthly_grid.py submit` |

The daily web page (`site/`) is not stored here either: GitHub publishes it after every run.
