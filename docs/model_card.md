# Model card: rf_roads_v1

**Model:** Random Forest with road features · **File:** `models/rf_roads_v1.joblib` (details in `models/rf_roads_v1_meta.json`) · **Trained:** 24 Oct 2026 by `src/phaseC_04_train_final.py` · **Owner:** Suraj Raj

## What it predicts
The chance that a **reported landslide** occurs at a road-corridor location on a given day, from that location's terrain and that day's rain, soil moisture and snow. It is used for Himachal Pradesh only, and only for cells **within 500 m of a motorable road**.

## Training data
- `data/phaseB/training_table_v1.csv` (SHA-256 in the meta file): 3,136 rows from HP, Uttarakhand and UT of J&K, 2005–2026.
  - 969 reported landslides (label 1), from Bhusanket (GSI) and the NASA Global Landslide Catalog; Ladakh excluded.
  - 969 same place, safe day negatives.
  - 1,198 similar slope, storm day negatives.
- 38 features (terrain, drainage, roads, rock, faults, landforms, land cover, pre-event NDVI, IMERG and CHIRPS rain, ERA5-Land soil moisture and snow). Left out: `ndvi_pre_n`, `imerg_images_31d`, `imerg_provisional_31d`, `aspect_deg` (documentation §17.1).

## Method
Gaps filled with the median; category columns one-hot encoded; Random Forest with 500 trees and at least 3 rows per leaf (Breiman 2001). No tuning.

## How good it is (cross-validated, whole years held out)

| Measure | All 3 states | HP only |
|---|---|---|
| ROC AUC | 0.801 | 0.790 |
| PR AUC (no-skill 0.31) | 0.639 | – |
| ROC AUC, landslides vs same-place safe days (weather only) | 0.746 | – |

## Alert levels

**Final (9 Nov 2026), used by the daily system:** live model `rf_roads_live_v1`, road-neutral scoring; cell Watch ≥ 0.376, Warning ≥ 0.463; a district is at a level when ≥ 30% of its cells within 500 m of a road reach it. Storm replays (16 storm days, 16 quiet days, held-out-year models): Watch caught 38 of 44 affected districts with 15% false alarms on quiet district-days; Warning 32 of 44 with 1.6%. Details: documentation §17.10, `docs/alert_rule_explained.md`.

*Earlier provisional levels for the 38-feature model (24 Oct), kept for the record:*

| Level | Score | HP slides caught | HP safe days flagged | ≈ False alarms / month at one spot (HP) |
|---|---|---|---|---|
| Watch | ≥ 0.35 | 55% | 16% | 4.8 |
| Warning | ≥ 0.45 | 33% | 5% | 1.5 |

## Limitations
1. **Learns reported slides near roads.** Road distance is among the strongest features, partly a real effect of road cuts and partly reporting bias. Not valid away from roads.
2. **Misses many slides:** about 45% of HP slides fall below Watch.
3. **False alarms:** about 16% of safe days at a landslide spot reach Watch.
4. **Label noise:** some negatives may be unrecorded landslides.
5. **Small HP sample** (195 slides): HP figures are uncertain by several percentage points.
6. **Trained on real (satellite) rain only.** In the live run, forecast rain fills the last days, which adds warning time but also errors.
7. **Probabilities are relative,** not true daily chances: the training sample has about 1 landslide for every 2.2 negatives, far more than in reality.

## Comparisons kept
XGBoost with roads (ROC AUC 0.807, but clearly worse on the weather-only test) and the road-free models (0.737–0.762) are documented in §17 of the technical documentation as sensitivity checks.
