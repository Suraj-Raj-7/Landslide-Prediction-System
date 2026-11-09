# Phase D design: the daily warning system

**Date:** 24 Oct 2026, updated 2 Nov 2026 · **Author:** Suraj Raj · **Status:** built and tested 9 Nov 2026 (see `docs/daily_system_setup.md`); final alert rule from the Phase E replays. Sections below are the original design; changes: vegetation refreshed monthly, page on GitHub Pages instead of a GEE App, road-neutral scoring adopted (5 Nov)

## Goal
Every day, automatically: score landslide risk for **the whole of Himachal Pradesh** for today (and tomorrow), summarise it per district, email the districts at Watch or Warning to the chosen recipients, and show the latest map in a GEE App. Cells more than 500 m from a motorable road are marked **lower confidence**, because almost all recorded landslides, and so the measured skill, lie near roads.

## 1. Data available on the day (checked in GEE, 24 Oct 2026)

| Data | Latest image on 24 Oct | Delay | Used by the model? |
|---|---|---|---|
| IMERG V07 (rain) | 22 Oct 21:00 UTC (provisional) | ~2 days | Yes |
| GFS 0.25° forecast | Run of 24 Oct 00 UTC complete (209 steps); 06 UTC run still loading | Runs take ~6–12 h to fully arrive | Live run only |
| ERA5-Land daily (soil moisture, snow) | 12 Oct | ~12 days | Yes (4 features) |
| CHIRPS v2 and v3 daily | 30 Sep | ~24 days (monthly release) | Yes (6 features) |

**Problem:** CHIRPS and ERA5-Land are too late for a daily run. On a given day, the 6 CHIRPS features (rain on the day and in the 1–30 days before) and the 4 ERA5-Land features do not exist yet. No faster daily CHIRPS is available: the preliminary CHIRPS is a 5-day total, updated weekly (GEE community catalog; CHIRPS FAQ), so it cannot fill daily features.

## 2. Live feature set (decided 1 Nov 2026: Option A)

**Decision (Suraj):** Option A. The live model `rf_roads_live_v1` uses IMERG + fixed features (28); `src/phaseC_07_train_live.py`. Year-blocked CV: ROC AUC 0.775 (HP 0.763; weather-only test 0.683). The same HP hit rates as the 38-feature levels are reached at scores of about 0.345 (Watch) and 0.441 (Warning), but with more false alarms on HP safe days: 26% instead of 16% at Watch, and 13% instead of 5% at Warning. Both models are reported: 38 features = best with complete data; 28 = what runs live. The Phase E replays use the live model.

**Background test that led to the decision:**
Data test (`src/phaseC_05_live_features.py`, `data/phaseC/live_feature_test.csv`): the chosen Random Forest, same recipe, same year-blocked cross-validation, with feature groups removed.

| Features | ROC AUC | Weather-only test (positives vs same-place safe days) | HP rows |
|---|---|---|---|
| All 38 (current model) | 0.801 | 0.746 | 0.790 |
| Without ERA5-Land soil/snow (34) | 0.797 | 0.740 | 0.792 |
| Without CHIRPS (32) | 0.782 | 0.693 | 0.759 |
| **Without CHIRPS and ERA5-Land (28): IMERG + fixed features** | **0.775** | **0.683** | **0.763** |

**Options:**
- **A (recommended): a live model on IMERG + fixed features only (28).** Every input exists every day. It costs skill (weather-only AUC 0.746 → 0.683), and the cost is stated in the report. The 38-feature model stays as the "best possible with complete data" reference.
- **B: feed IMERG into the CHIRPS features in the live run.** Not recommended: in these mountains IMERG and CHIRPS correlate only 0.53–0.75 (Step 6), so the model would receive values unlike those it was trained on.
- **C: use the ERA5-Land values from ~12 days ago as "latest known".** Not needed: removing ERA5-Land costs almost nothing (0.801 → 0.797).

If A is chosen: train `rf_roads_live_v1` (Random Forest with roads, 28 features) and redo the threshold table for it. The Watch and Warning levels stay provisional and are re-derived at similar hit rates.

## 3. Rain for the live run
- **Today's date (IST)** is "day 0". The model needs rain on day 0 and in the 1, 3, 7, 15 and 30 days before.
- **Past days:** IMERG, as in training.
- **Days IMERG does not yet cover** (about the last 2 days) **and day 0:** GFS forecast from the latest *complete* run (all 209 steps present).
- **Tomorrow's outlook:** a second score with day 0 = tomorrow, using GFS for the extra day.
- **How GFS rain is summed (data test, 24 Oct):** `total_precipitation_surface` is a running total inside each 6-hour block and resets after hours 6, 12, 18, 24. For example, Thiruvananthapuram read 16.75 mm at hour 18 and 3.06 mm at hour 19. A day's forecast rain is the sum of the values at the ends of the four 6-hour blocks covering that day.
- **Training stays on real rain only.** The report states that forecast rain adds lead time but also errors; Phase E measures this on one storm.

## 4. Prediction points
- **Every 1 km cell centre in HP** (UTM 43N grid): **55,253 points**.
  - **18,277** of them lie within 500 m of a motorable road: the tested zone.
  - The other **36,976** are marked **lower confidence**.
- **Fixed features** (terrain, drainage, roads, rock, faults, landforms, land cover; 20 features) are computed **once** for all 55,253 points with `stack.extract_static()`, the same code as training. A check on 5 training landslides gave identical values (100 of 100).
  - Script: `src/phaseD_01_static_grid.py`.
  - Assets: `users/rajsuraj777/hp_grid_static_v1_a … _h` (8 latitude strips, submitted 1 Nov 2026).
  - Each point keeps its **real** road distances, which are used for the lower-confidence mark.
- **Model:** the live model `rf_roads_live_v1` (Random Forest with roads, 28 features: IMERG + fixed).
- **Road distances at prediction time:** *pending Suraj's decision* on the road-neutral test (`src/phaseC_06_road_neutral_test.py`). Either real distances (as trained) or road-neutral, where every cell is scored "as if observed like a roadside slope" with both road distances set to the median of the training positives.
- **Daily features:** rain (IMERG/GFS) and NDVI over the past 365 days.
- **Districts:** geoBoundaries ADM2, keeping the 12 HP districts (Bilaspur, Chamba, Hamirpur, Kangra, Kinnaur, Kullu, Lahul & Spiti, Mandi, Shimla, Sirmaur, Solan, Una).

## 5. District alert rule (provisional)
A district is at **Watch** (or **Warning**) when **at least 5% of its points** score at or above that level (whether the rule counts all points or only the tested road-zone points is decided with the replays). The 5% figure is a starting value (judgement, not evidence). It is fixed after the Phase E replays, together with the point levels, using the criteria written in documentation §17.10.

## 6. Daily outputs
- **GEE table asset per day:** `users/rajsuraj777/risk_daily/risk_YYYYMMDD`, with **55,253 points**, each carrying id, score, level and a lower-confidence flag. Estimated at about 4–6 MB per day, so about 0.1–0.2 GB per month. A new asset is written each day and nothing is overwritten; deleting old days is only done with Suraj's approval.
- **District summary** (12 rows: share of points at Watch/Warning, level) saved with the run log.
- **Email** (only if any district is at Watch or above): district list with levels, today and tomorrow, plus a map image. A short "no alert" summary can optionally be sent on quiet days.
- **GEE App:** shows the latest daily asset as a coloured map, with district outlines.

## 7. Automation
- **GitHub Actions**, once a day around 10:00 IST (free for public repos; private repos have a free monthly allowance).
- **Secrets stored in GitHub, never in files:** the Earth Engine service-account key, the Gmail address and app password, the recipient list.
- **Steps:** find the latest complete GFS run → build day-0 features → score with the saved model → write the GEE asset → district summary → email.

## 8. What Suraj needs to do (guided, step by step)
1. Create the GitHub repository and sign in on this laptop.
2. Create a Google Cloud service account in project `idyllic-return-468714-j4`, register it for Earth Engine, and give it access to `users/rajsuraj777` assets. Add the key as a GitHub secret.
3. Create a Gmail app password for the sender address and add it as a GitHub secret.
4. Decide the alert recipients (for the demo, e.g. your own and your teammate's addresses).
5. Publish the GEE App from the Code Editor.

## 9. Order of work
1. Live model (after decision 2) and its threshold table.
2. Fixed features for the 18,277 points (one GEE export job, a few hours).
3. Daily feature builder (IMERG + GFS + NDVI) and scorer; test on past dates.
4. District summary, email, and the GEE App script.
5. GitHub Actions workflow; first automatic runs.
