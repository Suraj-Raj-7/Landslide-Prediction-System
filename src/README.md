# Code: what each script does

All code is Python. Run scripts **from the project's main folder**, for example:

```bash
.venv/Scripts/python -W ignore src/live_03_daily_run.py --no-email
```

Every script starts with a comment block that explains, in plain words, what it does, why, what it reads and what it writes. The groups below follow the order in which the project was built.

## 1. The daily system (start here)
These three files are the working warning system.

| Script | What it does | How often |
|---|---|---|
| `live_01_monthly_grid.py` | Makes the HP grid file (`data/live/grid_live.csv.gz`): all 55,253 squares with their fixed features, district and vegetation | Once a month |
| `live_02_rain.py` | Rain for today and tomorrow for every square: measured satellite rain, plus forecast rain for the hours not yet measured | Used by the daily run |
| `live_03_daily_run.py` | Scores every square, decides district levels, draws maps, builds the web page, sends the email | Every morning (GitHub Actions) |

## 2. Feature modules (shared building blocks)
Each module computes one group of features in Google Earth Engine. They mirror scripts first written in Earth Engine's JavaScript editor, which is why they say "Python mirror of GEE module".

| Module | Features |
|---|---|
| `terrain.py` | Elevation, slope, aspect, curvature, terrain position, wetness index |
| `drainage_roads.py` | Distance to streams and roads, height above the nearest drainage |
| `lithology.py`, `faults.py`, `geomorph.py` | Rock type, distance to faults and thrusts, landforms (Geological Survey of India maps) |
| `land_cover.py` | Land-cover class |
| `vegetation.py` | Vegetation over the year before the date (Landsat NDVI) |
| `dynamic.py` | Rain (IMERG, CHIRPS), soil moisture and snow (ERA5-Land) on and before the date |
| `stack.py` | Puts all the modules together into the full feature set |

## 3. Building the landslide data (Step 0 to Step 3, September–October)
| Script | What it does |
|---|---|
| `05_step0_audit.py` | Checks the landslide records (dates, places, duplicates) |
| `07_step0_build_positives_v5.py` | Applies the fixes and writes the cleaned landslide list (`data/positives_v5.csv`) |
| `10_step1_terrain_run.py`, `13_step2_drainage_roads_run.py` | Extract terrain, drainage and road features for every landslide |
| `16_step3_lithology_mapping.py`, `make_js_lithology.py` | Build the table that groups rock descriptions into rock classes |

## 4. "No landslide" examples (Phase B)
| Script | What it does |
|---|---|
| `phaseB_make_type1.py` | Type 1: the same place as a landslide, on a safe day |
| `phaseB_make_type2.py` | Type 2: a similar slope on the same storm day that did not slide |
| `phaseB_extract.py` | Starts the Earth Engine jobs that measure their features |
| `phaseB_assemble.py` | Builds the training table (`data/phaseB/training_table_v1.csv`) |
| `fig_negatives_before_after.py` | Map of old random vs new careful "no landslide" examples |

## 5. Models and tests (Phase C)
| Script | Question it answers |
|---|---|
| `phaseC_01_train_compare.py` | Which model is best: logistic regression, Random Forest or XGBoost? (shared training code lives here) |
| `phaseC_02_type1_check.py` | Can the models tell a landslide day from a safe day at the same place? |
| `phaseC_03_threshold_options.py` | Which score should trigger an alert? |
| `phaseC_04_train_final.py` | Train and save the main model |
| `phaseC_05_live_features.py` | Which data actually arrives in time for a daily run? |
| `phaseC_06_road_neutral_test.py` | What changes if every square is scored as if it were next to a road? |
| `phaseC_07_train_live.py` | Train the model the daily system uses (`models/rf_roads_live_v1.joblib`) |
| `phaseC_08_heavy_rain_baseline.py` | Does the model beat a simple "heavy rain" rule? |
| `phaseC_09_timing_diagnostic.py` | Why does rain alone tell *when* better than the model? |
| `phaseC_10_partial_dependence.py` | Does the model react to rain and slope in a physically sensible way? |
| `phaseC_11_two_part_model.py` | A model in two parts: *where* (terrain) × *when* (rain) |
| `phaseC_12_summary_figure.py` | One chart comparing all models |
| `phaseC_13_strict_vs_easy_cv.py` | How much does the testing method change the score? |
| `phaseC_14_rq1_terrain_vs_rain.py` | Research question 1: does rain add to terrain? |
| `phaseC_15_pdirnow_extract.py`, `phaseC_16_gee_rain_d0.py`, `phaseC_17_rain_product_timing_test.py` | Is a finer free rain product better than IMERG? (No.) |

## 6. Maps of all of HP (Phase D)
| Script | What it does |
|---|---|
| `phaseD_01_static_grid.py` | Fixed features for all 55,253 squares of HP |
| `phaseD_02_storm_features.py` | Daily features for all squares on one date |
| `phaseD_03_storm_map.py` | Risk map of HP for one past day, with recorded landslides on top |
| `phaseD_04_storm_vs_quiet_figure.py` | A disaster day and a quiet day side by side |

## 7. Storm replays: choosing the alert rule (Phase E)
| Script | What it does |
|---|---|
| `phaseE_01_replay_dates.py` | Picks the test days by a fixed rule, before any scoring |
| `phaseE_02_replay_features.py` | Builds the HP grid for each test year in Earth Engine |
| `phaseE_03_replay_scores.py` | Scores every square on every test day, with models that never saw that year |
| `phaseE_04_replay_evaluate.py` | Tries 24 district rules and picks the best by a rule set in advance |
| `phaseE_05_replay_uncertainty.py` | How sure can we be about that choice? |

## 8. Impact evidence
| Script | What it does |
|---|---|
| `impact_01_monsoon_replay.py` | Runs the system for every day of a past monsoon (2023, 2025) |

## Other
- `deck/build_assignment3_deck.js`: builds the interim presentation slides (JavaScript, pptxgenjs).
