# Key facts and numbers (one page to check slides and the report against)

Checked against the result files on 13 Nov 2026. If a number on a slide or in the report differs from this page, this page and the file named next to it are right.

"HP" = Himachal Pradesh. "AUC" = a score from 0.5 (coin toss) to 1 (perfect) for how well risky cases are ranked above safe ones. All model scores come from **year-blocked testing**: the model is always tested on years it did not learn from.

## 1. Data

| Fact | Number | Source |
|---|---|---|
| Dated landslides used | **981** (2005-07-29 to 2026-07-07) | `data/positives_v5.csv` |
| ...in HP / Uttarakhand / Jammu & Kashmir | 195 / 548 / 238 | same |
| Features measured per landslide | 42 | `data/positives_features_v1_local.csv` |
| Training table | **3,136 rows** = 969 landslides + 969 same-place safe days + 1,198 similar slopes on storm days | `data/phaseB/training_table_v1.csv` |
| ...of which HP rows | 714 | same |
| HP grid for maps and the daily run | **55,253** squares of 1 km; 18,286 of them within 500 m of a road | `data/live/grid_live.csv.gz` |

## 2. Models

| Fact | Number | Source |
|---|---|---|
| Three models compared (38 features): logistic regression / Random Forest / XGBoost | AUC 0.780 / **0.801** / 0.807 | `data/phaseC/cv_metrics.csv` |
| Chosen: Random Forest (XGBoost leaned on roads instead of rain) | | `docs/experiments_log.md` §6.4–6.5 |
| Live model (28 features: satellite rain IMERG + fixed features; other rain and soil data arrive 12–24 days late) | AUC **0.775** (HP 0.763) | `data/phaseC/live_feature_test.csv`, `models/rf_roads_live_v1_meta.json` |
| Same live model, tested three ways: whole years held out / whole storm days / random rows | 0.775 / 0.792 / 0.856 | `data/phaseC/strict_vs_easy_cv.csv` |
| Why the September prototype scored 0.895: easy random "no landslide" points and random-row testing | | same, and `docs/project_history.md` |
| Telling a landslide day from a safe day at the same place: rain on the day alone / live model | AUC **0.824** (HP 0.805) / 0.683 | `data/phaseC/two_part_comparison.csv` |
| Two-part model (where × when), live | AUC 0.813 (HP 0.777) | same |
| Research question 1, "does rain add to terrain?" (landslides vs other slopes on storm days): terrain only / + IMERG rain / all rain and soil data | 0.912 / 0.926 / 0.928 (HP 0.858 / 0.870 / 0.877) | `data/phaseC/rq1_terrain_vs_rain.csv` |
| Finer free rain data, timing test: GSMaP vs IMERG / PDIR-Now (4 km) vs IMERG, HP | 0.801 vs 0.807 (tie) / 0.680 vs 0.790 (worse) | `data/phaseC/rain_product_timing_test.csv` |

## 3. Alert rule (final, adopted 9 Nov 2026)

| Fact | Number | Source |
|---|---|---|
| Square at Watch / Warning | score ≥ **0.376** / ≥ **0.463** | `models/rf_roads_live_v1_meta.json` |
| District at a level when | ≥ **30%** of its squares within 500 m of a road reach it | same |
| Scoring | road-neutral: every square scored as if watched like a roadside slope (road distances set to 22 m and 46 m) | same |

## 4. Storm replays (how the rule was chosen)

| Fact | Number | Source |
|---|---|---|
| Test days | 16 storm days (2010–2025) + the day before each + 16 quiet days | `data/phaseE/replay_dates.csv` |
| Checks | 44 storm-district checks; 192 quiet district-days | `data/phaseE/replay_candidates.csv` |
| Watch: districts with landslides caught / quiet district-days alarmed | **38 of 44 (86%)** / **28 of 192 (15%)** | same |
| Warning: caught / alarmed | 32 of 44 (73%) / 3 of 192 (1.6%) | same |
| Skill score TSS (caught share − false-alarm share), chosen rule | 0.718 (95% range 0.545–0.870) | `data/phaseE/replay_uncertainty.csv` |
| Old temporary rule (5% of all squares) | 43 of 44 caught, but 84 of 192 false alarms (44%); TSS 0.540 | `data/phaseE/replay_candidates.csv` |

## 5. Maps of one storm day and one quiet day (earlier, with temporary levels)

| Fact | Number | Source |
|---|---|---|
| 14 Aug 2023 (worst day in our records): recorded HP landslides in alert squares | **31 of 31** | `data/phaseD/storm_20230814_v2_slides.csv` |
| ...squares at Watch or above / at Warning | 66.8% / 47.2% (mean rain 40 mm) | `data/phaseD/storm_20230814_v2_scores.csv` |
| 12 Sep 2023 (quiet day): squares at Watch or above | 0.4% (mean rain 0.8 mm) | `data/phaseD/storm_20230912_v2_scores.csv` |

## 6. Whole monsoons replayed (15 Jun–30 Sep, model trained without that year)

| Fact | 2023 | 2025 | Source |
|---|---|---|---|
| District-days with a recorded landslide | 22 | 35 | `data/impact/monsoon_<year>_summary.csv` |
| ...on alert that day or the day before | **17 (77%)** | **24 (69%)** | same |
| ...already on alert the day before | 12 | 20 | same |
| District-days on alert, out of 1,296 | 426 (33%) | 333 (26%) | same |
| Alert days per district (average) | about 36 | about 28 | same |

## 7. The live system

| Fact | Number | Source |
|---|---|---|
| Running every day since | 9 Nov 2026 | `CHANGELOG.md` |
| Time for one daily run | about 1 minute (whole workflow 3–5 min) | GitHub Actions run list |
| Satellite rain delay | about 1.5 days (34 h on 9 Nov 2026); the rest comes from the GFS forecast | `CHANGELOG.md` (9 Nov) |
| Data delays that ruled out other inputs | CHIRPS about 24 days, ERA5-Land about 12 days | `docs/phaseD_design_note.md` |
| Vegetation refresh | monthly (moving the 1-year window by 90 days changes it by a median of 0.010) | `CHANGELOG.md` (6 Nov) |
| Cost | free data and free hosting | `docs/daily_system_setup.md` |
| Live page | https://suraj-raj-7.github.io/Landslide-Prediction-System/ | |

## 8. Context figures (cite with care)
- **2023 monsoon in HP:** official data reported by Mongabay (Sept 2023): 428 deaths in weather-related events (125 in 2022), 2,614 houses and 318 shops fully damaged, more than 11,000 houses partly damaged. The figure of "509 deaths and 7,000+ landslides" used in Assignment 1 could not be traced to a primary source; do not use it unless the source is found.
- **Official warnings in India:** IMD (rain), Geological Survey of India's National Landslide Forecasting Centre (landslide bulletins). Our system is a research decision-support tool, not an official warning.
