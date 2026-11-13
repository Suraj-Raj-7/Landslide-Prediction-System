# Landslide Early-Warning Project: Feature Stack Documentation

**Project:** M.Tech ICTD course project, IIT Delhi (team: Suraj Raj, Siddhesh Pohare)
**This document covers:** the data-collection and feature-engineering phase (plan steps 0–8), carried out 19–21 October 2026.
**GEE cloud project:** `idyllic-return-468714-j4` · **Asset folder:** `users/rajsuraj777` · **Drive folder:** `ICTD_Landslides_Project`
**Script repository:** `users/rajsuraj777/ICTD_Landslides_Project` (Code Editor), folders `Current/` and `Archive/`

---

## Contents

1. [Summary](#1-summary)
2. [Project goal and scope](#2-project-goal-and-scope)
3. [How the work was done](#3-how-the-work-was-done)
4. [Step 0: positives audit and cleaning](#4-step-0-positives-audit-and-cleaning)
5. [Step 1: terrain](#5-step-1-terrain)
6. [Step 2: drainage and roads](#6-step-2-drainage-and-roads)
7. [Step 3: lithology, faults, geomorphology](#7-step-3-lithology-faults-geomorphology)
8. [Step 4: land cover](#8-step-4-land-cover)
9. [Step 5: pre-event vegetation (NDVI)](#9-step-5-pre-event-vegetation-ndvi)
10. [Step 6: rainfall, soil moisture, snow](#10-step-6-rainfall-soil-moisture-snow)
11. [Step 7: the assembled feature stack](#11-step-7-the-assembled-feature-stack)
12. [Feature dictionary (all 42 features)](#12-feature-dictionary-all-42-features)
13. [Assets, scripts and output files](#13-assets-scripts-and-output-files)
14. [Problems, failures and fixes](#14-problems-failures-and-fixes)
15. [Limitations](#15-limitations)
16. [Phase B: no-landslide (negative) examples and training table](#16-phase-b-no-landslide-negative-examples-and-training-table)
17. [Phase C: model comparison](#17-phase-c-model-comparison)
18. [What comes next](#18-what-comes-next)
19. [References](#19-references)

---

## 1. Summary

- **981 cleaned, dated landslide events** (HP 195, Uttarakhand 548, J&K 238 of which 12 in Ladakh), dated 2005-07-29 to 2026-07-07, are stored as `users/rajsuraj777/positives_v5`.
- **42 features per event**, built the same way for all three states, with no missing values except one deliberately masked glacier snow value (see §10). Final table: `positives_features_v1.csv` on Drive.
- Every feature is computed by a **reusable GEE module**. One function, `extractFeatures(points, dateField)`, returns all 42 features for any set of points at each point's own date. The same code therefore serves the positives, the later hard negatives, and the live daily warning run.
- Static features can be exported as **HP-wide 30 m rasters** for statewide prediction maps (export prepared, not yet run).
- **Every method choice is backed** by a verified reference or, where no paper settles the question, by an explicit data test (for example, the stream threshold was calibrated against OpenStreetMap streams).
- All JavaScript scripts are in the Code Editor repository with a standard header (purpose, inputs, outputs, status, results). Every computation was **run and checked through a Python mirror** using the Earth Engine Python API. The JavaScript versions are syntax-checked but **have not yet been run in the Code Editor**.

| Feature group | Features | Source |
|---|---|---|
| Terrain | 9 | Copernicus GLO-30 DEM, MERIT Hydro |
| Drainage and roads | 4 | MERIT Hydro, OpenStreetMap (HOT export) |
| Lithology | 2 | GSI/NGDR 1:50k lithology, GLiM classes |
| Faults | 2 | GSI/NGDR 1:50k fault layer |
| Geomorphology | 1 | GSI/NGDR 1:250k geomorphology |
| Land cover | 2 | ESA WorldCover 2021 |
| Vegetation | 2 | Landsat 5/7/8/9 NDVI, 365 days before event |
| Rainfall, soil, snow | 18 | GPM IMERG V07, CHIRPS, ERA5-Land |
| Data-source flags | 2 | IMERG completeness and final/provisional status |

---

## 2. Project goal and scope

**End goal of the project.** A working, *dynamic* landslide **early-warning system** for Himachal Pradesh that warns the relevant authorities (not the public) when the day's conditions, mainly rainfall, make landslides likely. It is explicitly not just a static susceptibility map.

**What the model predicts.** The target is **reported landslides near roads**: the events in the inventories, which are mostly slides that hit roads (median 22 m from a road, §6). The risk map and alerts are therefore limited to **road corridors** (within about 500 m of a motorable road), where the training data lie (§17.8).

**Why three states.** HP alone has too few *dated* landslide records to train a model. Uttarakhand and J&K events are added as extra training data; the prediction target remains HP.

**Scope of this phase.** Build a reusable feature stack for all three states and extract it at the positive (landslide) events.
Out of scope here: hard-negative sampling, model choice and training, validation design, forecast rainfall, the live pipeline, NISAR, and satellite change detection (teammate's work).

**Working rules followed.**
1. Every method choice is backed by literature or by a data test, and the evidence type is stated.
2. No guessed dataset IDs: every GEE dataset was checked in the catalog before use.
3. Expected results were stated before running, and each step was checked against them.
4. No paid services were used. Everything ran on free GEE (non-commercial) and free data portals.
5. Scripts are organised in `Current/` (in use) and `Archive/` (never used again; nothing deleted), named `NN_stepK_topic`, with a standard header, and listed in `Current/00_README_index`.

---

## 3. How the work was done

- **Earth Engine Python API** (earthengine-api 1.7.48, on the user's laptop with the user's approval) ran all computations. The computing itself happens on Google's servers.
- **The Code Editor repository** was cloned through Git (`earthengine.googlesource.com`, authenticated with the user's Git cookie). Every new script was written in JavaScript, pushed to `Current/`, and documented in `Current/00_README_index`.
- **Each step has two scripts:** a *module* that only defines the feature image (loaded with `require`, no side effects) and a *run* script that spot-checks, extracts at the positives and exports to Drive.
- **Python mirrors** (`src/*.py`, same logic as the JS modules) were used to execute and verify every step.
- **Data the user downloaded by hand:** OSM roads (HOT Export Tool) and GSI/NGDR lithology, faults and geomorphology. Each download was unpacked and checked locally (record counts, fields, extent, coverage at the landslide points) before the user uploaded it to GEE. Each upload was then verified in GEE.

**Common sampling grid:** UTM zone 43N (EPSG:32643) at 30 m. A metric grid was chosen so terrain derivatives use true metre spacing and do not change with export scale. UK extends to 81°E, outside zone 43, and the resulting scale error is below 0.3%.

**Study area boundaries:** geoBoundaries v6.0.0 ADM1 (`WM/geoLab/geoBoundaries/600/ADM1`), selected by `shapeID`, defined once in `Current/07_step0_config`:

| Unit | shapeID | Area (km²) | Official (km²) |
|---|---|---|---|
| Himachal Pradesh | 1811400B21086746745937 | 55,276 | 55,673 |
| Uttarakhand | 1811400B3558497485804 | 51,737 | 53,483 |
| UT of Jammu & Kashmir | 1811400B42025667129192 | 43,013 | 42,241 |
| UT of Ladakh | 1811400B23769854471902 | 62,580 | ~59,146 |

FAO GAUL (used by the earlier scripts) was **dropped**. GAUL 2015 is deprecated, and both GAUL 2015 and GAUL 2025 store J&K as a single disputed unit of about 186,000 km², which includes Gilgit-Baltistan and Azad Kashmir. geoBoundaries separates the India-administered UTs, and its areas are closer to the official figures. Units are selected by ID because their names contain non-ASCII letters.

---

## 4. Step 0: positives audit and cleaning

**Input.** `positives_v4_corrected` (986 events from Bhusanket and the NASA Global Landslide Catalog, after a corrected date parser).

**Checks and results.**

| Check | Expected | Result |
|---|---|---|
| Stored date format | ISO `YYYY-MM-DD` text | 986/986 ISO strings (event_date and event_end) |
| Counts | HP 197, UK 548, J&K 241 | Matched |
| Latest CHIRPS date | ≥ last event (2026-07-07) | 2026-09-30 |
| CHIRPS images in the latest event's 31-day window | 31 | 31 |
| Asset vs CSV | identical | Identical except the upload rewrote NASA IDs (`NASA_9,892` → `NASA_9_892`) and coordinate rounding < 1 m |
| Point-in-state (geoBoundaries) | all match | 2 mismatches (fixed, below) |

**Fixes, drops and kept items** (full log: `step0_changes_log.csv`):

| Action | Record | Change | Reason |
|---|---|---|---|
| Fix | BH_8569 | lon 75.153 → **77.153** | Labelled HP/Solan with slide no. 53F01. Survey of India sheet 53F/1 covers 30.75–31.00°N, 77.00–77.25°E; the latitude fits and 75.15°E lies in Punjab. Leading-digit typo. |
| Fix | BH_35971 | lat 31.945 → **30.945** | Labelled Uttarkashi with sheet 53F_13 (30.75–31.00°N, 77.75–78.00°E); 31.945°N lies in Kinnaur (HP). Digit typo. |
| Fix | BH_35861_1 | date 2018-08-06 → **2025-08-06** | Raw text "06 August…, 18 August… and 26 August 2025": the parser read "18 August" as the year 2018. |
| Add | BH_35861_3 | **2025-08-18** | The third date in that same record, lost by the parser. |
| Drop | BH_8460_2 | | Date came from a lone "1" in "27 October 2023, 1, 26 August 2025"; not recoverable. |
| Drop | NASA_5,088 | | Duplicate of NASA_5,086 (same date, identical coordinates). |
| Drop | NASA_5,234 | | Duplicate of NASA_5,233 (same date, identical coordinates). |
| Drop | NASA_3,895 | | Duplicate of NASA_3,894 (same date, 29 m apart; NASA has no slide IDs). |
| Drop | BH_10901 | | Duplicate of BH_10952 (same date, 0.9 m apart; numeric re-entry slide ID). |
| Drop | BH_11272 | | Duplicate of BH_10955 (same date, 0.9 m apart; numeric re-entry slide ID). |
| Keep | BH_35882 (2005-07-29) | | Its 2025 survey series also records past events (2015 dates); the raw text is unambiguous. |
| Keep | 12 NASA points in Ladakh | tagged `admin_unit = Ladakh` | Real events (9 near Leh, 7 of them the 2010-08-06 cloudburst; 3 in Kargil). Can be filtered later. |
| Rename | all NASA IDs | `NASA_9,892` → `NASA_9892` | Commas removed. |

**Duplicate rules.** Bhusanket: same date and under 5 m apart means the same slide entered twice. NASA: same date and under 100 m apart means the same event reported twice. Bhusanket pairs 20–100 m apart have different slide numbers and were kept as separate slides.

**Result: `users/rajsuraj777/positives_v5`.** 981 events; HP 195, UK 548, J&K 238 (UT J&K 226, Ladakh 12); Bhusanket 728 (tier A 658, tier B 70), NASA 253; 344 unique dates; ranges of 1 day (711), 2 days (269) and 3 days (1). Columns: `id, sl_no, lat, lon, event_date, event_end, range_days, state, source, tier, also_in_glc, slide_no, admin_unit`. It was read back from GEE and matched the CSV exactly, with 0 label/polygon mismatches.

**Event clustering** (matters for validation later): 242 events on 2013-06-16 (Uttarakhand/Kedarnath), 33 on 2016-06-30, 32 on 2023-08-14.

Scripts: `Current/07_step0_config` (shared settings and boundaries), `Current/08_step0_verify_positives_v5`. Python: `07_step0_build_positives_v5.py`.

---

## 5. Step 1: terrain

**Module:** `Current/09_step1_terrain_module` · **Run:** `Current/10_step1_terrain_run` · **Output:** `positives_terrain_v2.csv`

**How it was built**
- **DEM:** Copernicus GLO-30 (`COPERNICUS/DEM/GLO30_2024_1`, which replaces the deprecated `GLO30`; identical values at test points). Mosaicked with **no clip** (clipping masked pixels near state edges in the old scripts), resampled bilinearly once onto UTM 43N at 30 m.
- **Slope and aspect:** `ee.Terrain.slope/aspect`. Aspect is also stored as sine and cosine, because aspect is circular (359° and 1° are neighbours). Both are set to 0 where slope < 1°, where aspect is meaningless.
- **Curvature:** plan and profile curvature with the Zevenbergen & Thorne (1987) 3×3 formulas, in 1/m.
- **TPI:** elevation minus the mean elevation within 500 m.
- **TWI:** ln(a / tan β) on the MERIT Hydro grid (~93 m). Here a = upstream area ÷ cell width (specific catchment area) and β = slope of MERIT elevation, with tan β floored at 0.001.

**Why.** Slope, aspect, elevation and curvature are the core landslide conditioning factors in the susceptibility literature (Reichenbach et al. 2018). TPI and TWI describe topographic position and wetness. MERIT Hydro (Yamazaki et al. 2019) provides a consistent upstream area. The old draft TWI could reach −∞ on ridges and mixed scales.

**Verification.**
- **Kernel direction and curvature signs** were tested on artificial surfaces: planes, a bowl, a dome, and a diagonal valley and ridge. This revealed that GEE's `ee.Kernel.fixed` puts weight row 0 on the **south** neighbour, so a north-rising plane gave H = −1. The north-south (H) and cross (F) kernels were corrected to list rows from south to north. After the fix all eight surfaces gave the expected values: east-west and north-south gradients +1, bowl profile −1/R, dome +1/R, valley plan +1/R, ridge −1/R.
- **Sign convention:** profile curvature is negative on concave and positive on convex slopes. Plan curvature is positive where flow converges (hollows, valleys) and negative where it diverges (spurs, ridges).
- **Town spot-checks:** Shimla Ridge 2,206 m (published about 2,205), Kullu Dhalpur 1,226 m (about 1,220), Dehradun Clock Tower 674 m (the city is about 640; the centre sits higher).

**Results at positives** (981 rows, 0 missing): elevation 320–5,906 m (median 1,236; mean 1,390); slope median 28.6° (mean 27.6°); TPI median −29 m (landslides sit slightly below their surroundings); profile curvature mostly concave; TWI 4.1–24.4.

---

## 6. Step 2: drainage and roads

**Module:** `Current/12_step2_drainage_roads_module` · **Run:** `Current/13_step2_drainage_roads_run` · **Output:** `positives_drainage_roads_v2.csv`

### Roads
- **Data:** OpenStreetMap roads from the HOT Export Tool.
  - HP: existing asset `HP_roads_osm` (45,135 lines, 38,066 inside HP).
  - Uttarakhand: `UK_roads_osm`, 172,824 lines.
  - J&K and Ladakh: `JK_Ladakh_roads_osm`, 148,877 lines.
  - The UK and J&K/Ladakh exports used the state boundary plus a 10 km buffer, so landslides near borders find the nearest road across them.
  - HOT limits an area by the number of OSM nodes in its bounding box (15 million), not by km², which is why two separate exports were used.
  - The boundary files were checked against GAUL 2025: all 548 UK landslides lie inside the buffered area. Every exported line has a `highway` value, so the exports are roads only.
- **Feature `dist_road_m`:** distance to the nearest *motorable* road. That includes unpaved tracks and roads under construction, and excludes paths, footways, steps and cycleways.
  - **Why:** rainfall-triggered landslides cluster along informally built rural roads (McAdoo et al. 2018), road construction and hill cutting drive rising human-triggered landslides with India the leading country (Froude & Petley 2018), and earthen rural roads drive shallow landslides (Leibundgut et al. 2016).
- **Feature `dist_major_road_m`:** distance to motorway, trunk, primary or secondary roads (national/state level).
- **Exact distances** use `FeatureCollection.distance` with an 80 km search radius. A 30 km radius left gaps in remote Ladakh and Spiti; 80 km leaves none, the largest distance seen being 31.8 km. This replaces the old `fastDistanceTransform(256)`, which was capped at about 7.7 km and depended on scale.

### Drainage
- **Choice of stream source** (compared at 981 landslides vs 1,500 random points):

| Source | Landslides (median) | Random (median) | Verdict |
|---|---|---|---|
| HydroSHEDS FreeFlowingRivers | 329 m | 1,087 m | Big rivers only (~500 m source data) |
| MERIT streams ≥ 0.1 km² | 90 m | 180 m | Too dense |
| MERIT streams ≥ 1 km² | 201 m | 485 m | Good separation |
| MERIT streams ≥ 10 km² | 285 m | 1,423 m | Similar to HydroSHEDS |

- **Threshold calibration** (data test). OSM `waterway=river|stream` lines were downloaded from the Overpass API for four test areas: Kullu, Shimla, Chamoli and Ramban. MERIT streams at upstream-area thresholds of 0.25–10 km² were scored by recall (share of OSM stream cells within 100 m of a MERIT stream) and precision (share of MERIT stream cells within 100 m of an OSM stream):

| Threshold | Recall | Precision | F1 (mean of 4 areas) |
|---|---|---|---|
| 0.25 km² | 0.90 | 0.42 | 0.57 |
| 0.5 km² | 0.87 | 0.52 | 0.65 |
| 1 km² | 0.82 | 0.65 | 0.72 |
| **2 km²** | **0.75** | **0.77** | **0.75** |
| 5 km² | 0.61 | 0.89 | 0.72 |
| 10 km² | 0.47 | 0.94 | 0.62 |

  **2 km² was chosen:** best mean F1, with recall and precision balanced. Literature context: a fixed contributing-area threshold marks the hillslope-to-valley transition (Montgomery & Foufoula-Georgiou 1993), and the area at which channels begin decreases with slope (Montgomery & Dietrich 1988), so a threshold has to be calibrated rather than taken from a paper. OSM under-maps small streams, which penalises the low thresholds a little, so the true optimum may lie between 1 and 2 km².
- **Feature `dist_stream_m`:** distance to the nearest MERIT stream cell (≥ 2 km²), computed on the MERIT grid within 20 km. GEE's kernel limit is 512 pixels; the computation is pinned to the ~93 m grid so the 20 km kernel fits.
- **Feature `hand_m`** (*experimental*): MERIT height above nearest drainage. The method is well established (Nobre et al. 2011), but no Himalayan landslide study using it was found; keep it only if the model shows it helps.

**Spot-checks.** On-road points 10–20 m from a road; Beas riverbank 0 m from a stream and 0 m above it; remote Spiti massif 15.7 km from a road.

**Results at positives** (981 rows, 0 missing):

| Feature | Landslides (median) | Random (median) |
|---|---|---|
| dist_stream_m | 207 m | 649 m |
| hand_m | 67 m | 141 m |
| dist_road_m | **22 m** | 1,989 m |
| dist_major_road_m | 47 m | 6,218 m |

**Important caution.** The median landslide is 22 m from a road, and 64% of UK landslides are within 30 m of one. The inventories mostly record slides that hit roads, so distance-to-road partly reflects *where slides are reported*. Hard negatives must also be sampled near roads.

---

## 7. Step 3: lithology, faults, geomorphology

All three come from the **GSI National Geoscience Data Repository (NGDR, geodataindia.gov.in → Bhu-Chayan)**, downloaded per state by the user. Every download was a zip inside a zip, the structure that GEE's uploader rejects. Flat upload zips (`.shp .shx .dbf .prj .cpg`) were built locally and uploaded by the user.

### 7.1 Lithology (1:50k)
- **Assets:** `HP_lithology` (4,331 polygons), `UK_lithology` (4,554), `JK_lithology` (4,229), `LADAKH_lithology` (3,485). All four have the same 27 NGDR fields.
- **Coverage:** about 81–88% of each state's area is mapped. **All 981 landslides lie on a mapped polygon.** The gaps are in high glaciated terrain.
- **Classification.** The 516 distinct free-text `lithologic` descriptions were mapped to the **GLiM level-1 classes** (Global Lithological Map; Hartmann & Moosdorf 2012), a published standard of 16 classes. A **main rock name** (49 names, such as phyllite, quartzite, granite) was also kept, because GLiM's single "metamorphics" class would merge most Himalayan rocks.
- **Explicit mapping table** `lithology_mapping_v1.csv`: one row per description, with the GLiM class, main rock, the rule that decided it, every rock term found, and flags. The rules:
  1. The first rock term listed decides the class (NGDR lists the dominant rock first).
  2. A description combining siliciclastic and carbonate rocks becomes `sm` (mixed sedimentary).
  3. Loose-sediment words (sand, silt, clay, gravel) count as unconsolidated (`su`) only if the polygon's age is Quaternary. Older ones, such as the Siwalik clays, count as consolidated (`ss`).

  Abbreviations such as QTZITE, GRNT and DIORT are recognised. 204 descriptions are flagged MIXED for review.
- **Unmapped:** 186 polygons (1.1%), 4.0% of the area ("UNMAPPED" or quartz veins), containing **0 landslides**.
- **Why nominal classes and not expert scores:** the class susceptibility is left to the model and the data. The Beas-basin AHP study (Singh et al. 2024) shows how expert scores can go wrong: its distance ratings are inverted relative to its own text.
- **Sanity check:** landslides per 1,000 km² are 5.9 (mixed sedimentary), 5.7 (metamorphics), 5.4 (siliciclastic), 4.4 (carbonate), 3.8 (unconsolidated) and **1.3 (granites)**, consistent with granites being more stable.
- **At positives:** metamorphics 435, mixed sedimentary 185, siliciclastic 178, unconsolidated 120, acid plutonic 30, carbonate 24, basic plutonic 5, intermediate volcanic 2, basic volcanic 2.
- Scripts: `Current/16_step3_lithology_module` (the lookup is generated from the CSV by `make_js_lithology.py`, so the two cannot drift apart) and `Current/17_step3_lithology_run`. Output: `positives_lithology_v1.csv`.

### 7.2 Faults (1:50k)
- **Assets:** `HP_fault` (1,289 lines), `UK_fault` (2,605), `JK_fault` (800), `LADAKH_fault` (896). The layer includes the major Himalayan thrusts: MBT, MCT, Vaikrita, Jutogh, Murree, Panjal, Karakoram and others.
- **Features:** `dist_fault_m` (any fault) and `dist_thrust_m`.
- **Thrust definition.** A line counts as a thrust if its `fault_type` **or** its `fault_name` contains "THRUST". J&K and Ladakh type most named thrusts as "FAULT INFERRED", so type alone would give them 1% and 0% thrusts, against 26–48% in every state when names are included.
- **Not used: Shear Zone.** It exists only for Uttarakhand (30 short lines in one ~25 km area), and a feature present in one state only would bias a pooled model.
- **Why:** distance to faults is a standard factor, used in the global susceptibility map behind NASA's LHASA (Stanley & Kirschbaum 2017), in the Beas basin study, and widely elsewhere (Reichenbach et al. 2018).
- **Results** (0 missing; 80 km search): distance to fault, landslides 1.9 km vs random 5.3 km; distance to thrust, 3.1 km vs 11.5 km. Median thrust distance by state: HP 2.6 km, UK 3.1 km, J&K 3.8 km, a sign that the states are consistent.
- Scripts: `Current/22_step3_faults_module`, `Current/23_step3_faults_run`. Output: `positives_faults_v1.csv`.

### 7.3 Geomorphology (1:250k)
- **Assets:** `HP_geomorph` (6,201 polygons), `UK_geomorph` (7,252), `JK_geomorph` (3,970), `LADAKH_geomorph` (6,482). A duplicate upload, `HP_geomorphology`, is identical and unused.
- **Feature `gm_code`:** the 30 legend classes (`legend_sho`) shared by all four states; 0 means unmapped.
- **Checks:** all 981 landslides lie on a polygon, and no polygons overlap at any landslide. "Mass Wasting Products" (mapped old landslide deposits) exists in all four states and holds only 3 landslides, so it does not leak the label.
- **At positives:** Highly Dissected Hills and Valleys 680, Alluvial Plain 118, Moderately Dissected Hills 79, Waterbody–River 55, Piedmont Slope 20, Low Dissected Hills 13, others ≤ 4.
- **Why:** used as a factor in the HP Beas-basin study (Singh et al. 2024), at the same 1:250k scale.
- **Limitation:** at 1:250k, valley-floor polygons absorb the road cuts beside them, which is why 118 slides fall in "Alluvial Plain" and 55 in "Waterbody–River".
- Scripts: `Current/24_step3_geomorph_module`, `Current/25_step3_geomorph_run`. Output: `positives_geomorph_v1.csv`.

---

## 8. Step 4: land cover

- **Data:** ESA WorldCover v200 (2021, 10 m; overall accuracy 76.7%; Zanaga et al. 2022).
- **Features:** `lc_class` (class at the point) and `lc_class_30m` (majority class in the 3×3, 30 m window, which matches the terrain grid and is less sensitive to a point on a single road or river pixel). The two agree for 929 of 981 points.
- **At positives:** tree 417, grass 224, built-up 213, bare 96, water 14, crop 8, shrub 5, snow/ice 2, moss 2.
- **Spot-checks:** Shimla Ridge = built-up, Shimla reserve forest = tree, Lahaul = bare.
- **Limitation:** a single 2021 snapshot, so land cover at event time is unknown. Road-side slides often fall on built-up pixels, because paved surfaces are mapped as built-up.
- Scripts: `Current/14_step4_landcover_module`, `Current/15_step4_landcover_run`. Output: `positives_landcover_v1.csv`.

---

## 9. Step 5: pre-event vegetation (NDVI)

- **Leakage risk:** imagery taken after an event can show the landslide scar itself, so a post-event NDVI would leak the answer.
- **Design:**
  - `ndvi_pre365` = median NDVI over the **365 days before** the event (D−365 to D−1), from Landsat 5/7/8/9 Collection 2 Level-2.
  - Clouds, cloud shadow and snow are removed with `QA_PIXEL`, and USGS scaling (×0.0000275 − 0.2) is applied.
  - `ndvi_pre_n` records the number of clear observations.
  - A full year balances out the seasons, and ending at D−1 keeps the event out.
  - The same feature works in the live system as "vegetation over the past year".
- **Why:**
  - Time-varying, pre-rainy-season NDVI outperformed a fixed-year NDVI (Open Geosciences, 2023).
  - Pre-event NDVI was the strongest variable in a typhoon-landslide model (ACRS 2016).
  - Post-event NDVI is what change-detection studies use to find scars, which is exactly what a predictor must exclude.
- **Spot-checks** (year before 2023-08-14): forest 0.65, bare Lahaul 0.03, Shimla town 0.19.
- **Results** (0 missing): median 0.43, range −0.06 to 0.81. Clear observations: median 28; 979 events have ≥ 5; 2 have fewer (NASA_9892: 1, BH_34677: 2), which can be discounted using `ndvi_pre_n`.
- **Note:** TM/ETM+ and OLI NDVI differ slightly; not harmonised.
- Scripts: `Current/20_step5_vegetation_module`, `Current/21_step5_vegetation_run`. Output: `positives_vegetation_v1.csv`.

---

## 10. Step 6: rainfall, soil moisture, snow

**Why these inputs.** NASA's operational landslide nowcast, LHASA, combines satellite rainfall (GPM IMERG) with susceptibility (Kirschbaum & Stanley 2018). Its version 2 adds **antecedent rainfall, soil moisture and snow** as daily inputs to a machine-learning model (XGBoost) (Stanley et al. 2021). That is the closest published blueprint for this project's warning system.

**Data**

| Dataset | GEE ID | Resolution | Delay in GEE (21 Oct 2026) | Role |
|---|---|---|---|---|
| GPM IMERG V07 | `NASA/GPM_L3/IMERG_V07` | half-hourly, ~11 km | ~2 days | Main rainfall source (live-capable) |
| CHIRPS daily | `UCSB-CHG/CHIRPS/DAILY` | daily, ~5.5 km | ~20 days | Second source and regression check |
| ERA5-Land daily | `ECMWF/ERA5_LAND/DAILY_AGGR` | daily, ~11 km | ~10 days | Soil moisture and snow state |

ERA5-Land was used instead of NASA SMAP (used in LHASA v2) because SMAP only starts in 2015 and would miss the 2013 Uttarakhand events.

**Window definitions** (D = event date as a local date, India Standard Time):
- `imerg_d0`: rain on day D, **00:00–24:00 IST** (= D−1 18:30 to D 18:30 UTC). The half-hourly IMERG makes a true local day possible, and the inventories record local dates.
- `imerg_antNd` (N = 1, 3, 7, 15, 30): rain in the N days **before** day D. Day 0 is kept separate, so "today's rain" and "rain before today" are distinct features. This resolves the plan's open question about including day 0.
- `imerg_max1d_7d`: the wettest single IST day in the 7 days before D.
- `chirps_d0`, `chirps_antNd`: the same windows on CHIRPS calendar days.
- `sm_l1_dm1`, `sm_l2_dm1`: ERA5-Land soil water at 0–7 cm and 7–28 cm on D−1 (m³/m³).
- `swe_dm1_mm`: snow water equivalent on D−1. `snowmelt_ant7d_mm`: snowmelt in the 7 days before D.
- `era5_glacier`: 1 on ERA5-Land permanent-glacier cells (see below).
- Windows end at `event_date` (the first day of multi-day events).

**Checks**
- **Completeness:** every event's 31-day IMERG window had all 1,488 half-hourly images.
- **Final vs provisional IMERG:** GEE holds **final** (gauge-corrected) IMERG up to **2025-09-30** and the **provisional** stream after that. 8 events (2025-11-22 to 2026-07-07) use provisional data only; all others use final data. Recorded per event in `imerg_provisional_31d`.
- **Regression check** (plan requirement): 5 random NASA events with correct dates (seed 42: NASA_6889, NASA_10943, NASA_10073, NASA_7224, NASA_2648). The new CHIRPS 3/7/15/30-day values equal the old file's values in **20 of 20 cases**. The antecedent windows reproduce the old pipeline wherever its dates were right.
- **Glacier placeholder:** one landslide (BH_35387, high Chamoli) lies on an ERA5-Land permanent-glacier cell, which holds a fixed 10,000 mm snow value on every date tested (2015, 2018, 2022). Its snow value is **set to missing** and `era5_glacier = 1`. The other 57 values above 100 mm are real snowpack.
- **Example:** Mandi, 2023-08-14: 85 mm on the day, 136 mm in the 3 days before, 393 mm in 30 days, soil water 0.43 (near saturation).

**Results at positives** (medians): IMERG on the day 33 mm; 3 days before 30 mm; 7 days 90 mm; 30 days 214 mm. CHIRPS on the day 22 mm; 30 days 284 mm. Topsoil water 0.45 m³/m³.

Scripts: `Current/18_step6_dynamic_module`, `Current/19_step6_dynamic_run`. Output: `positives_dynamic_v1.csv`. That file predates the glacier fix and its one SWE value of 10,000 is superseded by the final table.

---

## 11. Step 7: the assembled feature stack

- **Module:** `Current/26_step7_feature_stack_module`.
  - `staticImage()`: terrain, drainage/roads, lithology, faults and geomorphology as one image (polygons painted at 30 m), for HP-wide map export.
  - `dynamicImage(date)`: NDVI plus rainfall/soil/snow for any date (training dates or *today*).
  - `extractFeatures(points, dateField)`: all 42 features for any points at each point's own date. Raster bands are sampled at 30 m (UTM 43N), land cover at 10 m, NDVI at 30 m and the daily data at 1 km. **Lithology and geomorphology use an exact point-in-polygon lookup**: in testing, the 30 m pixel containing BH_8629 had its centre across a polygon edge 0.4 m away. Points need a unique `id`.
- **Run:** `Current/27_step7_assemble_run`. It builds and exports the final table, and contains an **optional HP-wide raster export** (`HP_static_features_30m`, 30 m, UTM 43N), switched off until the statewide map is needed.
- **Consistency test:** on 5 events the stack reproduced the per-step tables for all 42 features (the only difference, the edge case above, was fixed).
- **Final table:** `positives_features_v1.csv` on Drive (and asset `users/rajsuraj777/positives_features_v1`): 981 rows, 10 ID/metadata columns + 42 feature columns.

**Missing values per column in the final table:**

| Result | Value |
|---|---|
| Rows | 981 |
| Feature columns | 42 |
| Empty cells | **1 of 41,202** |
| Columns with any gap | `swe_dm1_mm` only: 1 (BH_35387, ERA5-Land permanent-glacier cell, masked on purpose; `era5_glacier = 1`) |
| All other 41 columns | 0 missing |

The Drive export `positives_features_v1.csv` completed on 2026-10-21. The gap count above was computed from the per-step tables that the stack reproduces (local copy: `positives_features_v1_local.csv`).

---

## 12. Feature dictionary (all 42 features)

| # | Column | Group | Unit / values | Source | Notes |
|---|---|---|---|---|---|
| 1 | elevation_m | Terrain | m | GLO-30 | UTM 43N 30 m, bilinear |
| 2 | slope_deg | Terrain | degrees | GLO-30 | |
| 3 | aspect_deg | Terrain | degrees from grid north | GLO-30 | grid north is ~1–3° off true north |
| 4 | aspect_sin | Terrain | −1..1 (east +) | GLO-30 | 0 where slope < 1° |
| 5 | aspect_cos | Terrain | −1..1 (north +) | GLO-30 | 0 where slope < 1° |
| 6 | plan_curv | Terrain | 1/m (+ converging) | GLO-30 | Zevenbergen & Thorne |
| 7 | profile_curv | Terrain | 1/m (− concave) | GLO-30 | Zevenbergen & Thorne |
| 8 | tpi_500m | Terrain | m (+ ridge, − valley) | GLO-30 | 500 m circle |
| 9 | twi | Terrain | ln(m) | MERIT Hydro | ~93 m grid |
| 10 | dist_stream_m | Drainage | m | MERIT Hydro | streams ≥ 2 km² |
| 11 | hand_m | Drainage | m | MERIT Hydro | experimental |
| 12 | dist_road_m | Roads | m | OSM | motorable incl. tracks and construction |
| 13 | dist_major_road_m | Roads | m | OSM | motorway/trunk/primary/secondary |
| 14 | glim_code | Lithology | 0–15 (GLiM order below) | NGDR 1:50k | 0 = no data |
| 15 | rock_code | Lithology | 0–49 (rock names in mapping) | NGDR 1:50k | 0 = none |
| 16 | dist_fault_m | Faults | m | NGDR 1:50k | |
| 17 | dist_thrust_m | Faults | m | NGDR 1:50k | thrust by type or name |
| 18 | gm_code | Geomorphology | 0–30 (classes below) | NGDR 1:250k | 0 = unmapped |
| 19 | lc_class | Land cover | WorldCover code | ESA WorldCover 2021 | point, 10 m |
| 20 | lc_class_30m | Land cover | WorldCover code | ESA WorldCover 2021 | 3×3 majority |
| 21 | ndvi_pre365 | Vegetation | −1..1 | Landsat 5/7/8/9 | 365 days before event |
| 22 | ndvi_pre_n | Vegetation | count | Landsat | clear observations |
| 23 | imerg_d0 | Rainfall | mm | IMERG V07 | event day, IST |
| 24–28 | imerg_ant1d … imerg_ant30d | Rainfall | mm | IMERG V07 | 1/3/7/15/30 days before |
| 29 | imerg_max1d_7d | Rainfall | mm | IMERG V07 | wettest day of past week |
| 30 | chirps_d0 | Rainfall | mm | CHIRPS | event day (calendar) |
| 31–35 | chirps_ant1d … chirps_ant30d | Rainfall | mm | CHIRPS | 1/3/7/15/30 days before |
| 36 | sm_l1_dm1 | Soil | m³/m³ | ERA5-Land | 0–7 cm, day before |
| 37 | sm_l2_dm1 | Soil | m³/m³ | ERA5-Land | 7–28 cm, day before |
| 38 | swe_dm1_mm | Snow | mm | ERA5-Land | missing on glacier cells |
| 39 | snowmelt_ant7d_mm | Snow | mm | ERA5-Land | 7 days before |
| 40 | era5_glacier | Flag | 0/1 | ERA5-Land | permanent-glacier cell |
| 41 | imerg_images_31d | Flag | count (1,488 = complete) | IMERG | data completeness |
| 42 | imerg_provisional_31d | Flag | count | IMERG | > 0 = provisional stream |

**GLiM code order (`glim_code`):** 0 nd (no data), 1 su unconsolidated sediments, 2 ss siliciclastic sedimentary, 3 sm mixed sedimentary, 4 sc carbonate, 5 ev evaporites, 6 mt metamorphics, 7 pa acid plutonic, 8 pi intermediate plutonic, 9 pb basic plutonic, 10 va acid volcanic, 11 vi intermediate volcanic, 12 vb basic volcanic, 13 py pyroclastics, 14 wb water, 15 ig ice/glaciers.

**Geomorphology code order (`gm_code` = 1 + position):** 1 Aeolian Sand Dune, 2 Aeolian dune complex, 3 Alluvial Plain, 4 Anthropogenic terrain, 5 Avalanche Chute, 6 Dam and Reservoir, 7 Deltaic Plain, 8 Flood Plain, 9 Glacial Cirque–Arete–Horn, 10 Glacial Lake and Nunatak, 11 Glacial Moraine, 12 Glacial Terrain, 13 Glacial Valley, 14 Highly Dissected Hills and Valleys, 15 Highly Dissected Plateau, 16 Kame Terrace, 17 Lacustrine Plain, 18 Lacustrine Swamp and Marsh, 19 Lacustrine Terrain, 20 Lake Island, 21 Low Dissected Hills and Valleys, 22 Mass Wasting Products, 23 Moderately Dissected Hills and Valleys, 24 Pediment Pediplain Complex, 25 Piedmont Slope, 26 Quarry and Mine Dump, 27 Snow Cover, 28 Valley Glacier, 29 Waterbodies–Other, 30 Waterbody–River.

**WorldCover codes:** 10 tree, 20 shrub, 30 grass, 40 crop, 50 built-up, 60 bare/sparse, 70 snow/ice, 80 water, 90 herbaceous wetland, 95 mangrove, 100 moss/lichen.

**Categorical columns** (`glim_code`, `rock_code`, `gm_code`, `lc_class`, `lc_class_30m`) are labels, not quantities: one-hot encode them or use a model that handles categories.

---

## 13. Assets, scripts and output files

### GEE assets (`users/rajsuraj777/…`)

| Asset | Content | Status |
|---|---|---|
| positives_v5 | 981 cleaned events | **In use** |
| positives_features_v1 | Final table (981 × 42 features) | **In use** (copy of the Drive table) |
| positives_dynamic_v1, positives_vegetation_v1 | Working copies used for checks | Superseded by positives_features_v1 |
| HP_roads_osm, UK_roads_osm, JK_Ladakh_roads_osm | OSM roads | In use |
| HP/UK/JK/LADAKH_lithology | NGDR 1:50k lithology | In use |
| HP/UK/JK/LADAKH_fault | NGDR 1:50k faults | In use |
| HP/UK/JK/LADAKH_geomorph | NGDR 1:250k geomorphology | In use |
| HP_geomorphology | Duplicate of HP_geomorph | Unused (can be deleted by the user) |
| positives_v4_corrected | 986 events before cleaning | Superseded |
| combined_landslide_points_v2, negative_points_v1 | Earlier prototype | Obsolete |

### Code Editor scripts (`ICTD_Landslides_Project/Current/`)

| Script | Role |
|---|---|
| 00_README_index | Index of folders, naming rule, assets and scripts |
| 07_step0_config | Shared settings: asset IDs, Drive folder, geoBoundaries units |
| 08_step0_verify_positives_v5 | Checks positives_v5; documents the cleaning |
| 09 / 10 step1_terrain | Terrain module / run |
| 12 / 13 step2_drainage_roads | Drainage and roads module / run |
| 14 / 15 step4_landcover | Land cover module / run |
| 16 / 17 step3_lithology | Lithology module (embedded mapping) / run |
| 18 / 19 step6_dynamic | Rainfall, soil and snow module / run |
| 20 / 21 step5_vegetation | NDVI module / run |
| 22 / 23 step3_faults | Fault module / run |
| 24 / 25 step3_geomorph | Geomorphology module / run |
| 26 step7_feature_stack_module | The complete stack and `extractFeatures` |
| 27 step7_assemble_run | Final table; optional HP-wide raster export |

`Archive/` holds 17 earlier scripts that will never be used again, each with an ARCHIVED header (original name, why archived, replaced by). Nothing was deleted.

### Python mirrors (`src/`)
`terrain.py, drainage_roads.py, land_cover.py, lithology.py, faults.py, geomorph.py, vegetation.py, dynamic.py, stack.py` (modules); `05_step0_audit.py, 07_step0_build_positives_v5.py, 10_step1_terrain_run.py, 13_step2_drainage_roads_run.py, 16_step3_lithology_mapping.py, make_js_lithology.py` (runs and tools). These live in the project folder (`src/`), not in the GEE repository, because the Code Editor treats every file there as JavaScript.

### Drive exports (`ICTD_Landslides_Project/`)

| File | Content | Use |
|---|---|---|
| **positives_features_v1.csv** | **Final table, all 42 features** | **Use this** |
| positives_terrain_v2.csv | Step 1 | Per-step |
| positives_drainage_roads_v2.csv | Step 2 | Per-step |
| positives_lithology_v1.csv | Step 3 lithology | Per-step |
| positives_faults_v1.csv | Step 3 faults | Per-step |
| positives_geomorph_v1.csv | Step 3 geomorphology | Per-step |
| positives_landcover_v1.csv | Step 4 | Per-step |
| positives_vegetation_v1.csv | Step 5 | Per-step |
| positives_dynamic_v1.csv | Step 6 | Per-step (one glacier SWE value pre-fix) |
| positives_drainage_roads_v1.csv | Step 2, 30 km road search | **Do not use** (1 missing value) |
| positives_terrain_v1.csv | Old draft (15 Oct) | **Do not use** (wrong curvature/TWI) |

### Local files (project folder `data/`)
`positives_v5.csv`, `step0_changes_log.csv`, `step0_states_map.png`, `lithology_mapping_v1.csv`, `lithology_descriptions_all.csv`, `osm_streams_testboxes.json`, the HOT area files (`hot_aoi/`), and local copies of the per-step tables.

---

## 14. Problems, failures and fixes

| # | Problem | How it was found | Fix |
|---|---|---|---|
| 1 | GAUL stores J&K as one disputed unit (incl. Gilgit-Baltistan, Azad Kashmir); GAUL 2015 deprecated | Area 186,067 km², map check | Switched to geoBoundaries v6 for all states |
| 2 | Upload changed NASA IDs (`,` → `_`) | Asset-vs-CSV comparison | Clean IDs in v5 (`NASA_9892`) |
| 3 | Coordinate typos (BH_8569, BH_35971), parser error (BH_35861), unrecoverable date, 5 duplicates | Point-in-state check, parse audit, distance search | §4 |
| 4 | Old draft terrain script: wrong curvature formulas, degree-grid kernels, TWI could be −∞ | Code review | Rewritten module; old script archived |
| 5 | GEE fixed kernels put row 0 at the south | Synthetic-surface test (north-rising plane gave −1) | H and F kernels corrected; all tests pass |
| 6 | First synthetic test used pixel indices, not metres | Implausible results | Test rebuilt in metres |
| 7 | GLO30 DEM deprecated | GEE warning | GLO30_2024_1 (identical at test points) |
| 8 | Kernel too large (512-pixel limit) for stream distance | GEE error | Computation pinned to the ~93 m MERIT grid |
| 9 | 30 km road search left gaps in remote areas | Null counts | 80 km radius, 0 gaps; v1 table marked "do not use" |
| 10 | Overpass API 502/504 errors | Download failures | Retries with backup mirrors |
| 11 | NGDR downloads are zip-in-zip | Inspection | Flat upload zips built locally |
| 12 | My mistake: three empty fault zips written (shell stripped backslashes) | File sizes 22 bytes | Rebuilt in Python before upload |
| 13 | My mistake: asset exports without geometry failed; one cancelled | GEE task list | Re-run with geometry kept; both completed |
| 14 | My mistake: provisional-IMERG count first written as 18 | Re-count before finishing | Corrected to 8 |
| 15 | Fault types inconsistent across states | Thrust count per state | Thrust = type **or** name |
| 16 | ERA5-Land glacier placeholder (10,000 mm SWE) | Range check | Masked; `era5_glacier` flag |
| 17 | Polygon edge vs 30 m pixel centre (BH_8629) | Stack-vs-table comparison | Exact point-in-polygon for points |
| 18 | Duplicate upload `HP_geomorphology` | Asset listing | Ignored (unused) |

**Not yet verified:** the JavaScript scripts have been syntax-checked but not run in the Code Editor. Every number in this document comes from the Python mirrors, which use the same logic and data. Running each `*_run` script once in the Code Editor and comparing its console output with the RESULTS block in its header would close this gap.

---

## 15. Limitations

1. **Road bias of the inventory:** the median landslide is 22 m from a road, because surveys mostly record slides that affect roads. Distance-to-road will look stronger than its physical effect.
2. **Event clustering:** 242 of 981 events occurred on one day (2013-06-16). Random train/test splits would overstate accuracy, so whole storms or years should be held out.
3. **NASA Global Landslide Catalog:** this mirror ends in mid-2018, comes mostly from English-language news reports, and has variable location accuracy.
4. **Satellite rainfall in mountains:** IMERG and CHIRPS both have known biases over high terrain, including documented overestimation of daily rain over HP. Both are kept so the difference is visible.
5. **IMERG final vs provisional:** training uses mostly final data, while a live system runs on provisional data (~2 days behind). 8 recent events already use provisional data.
6. **ERA5-Land resolution and delay:** ~11 km cells, ~10 days behind in GEE, so the soil and snow state is regional, not slope-scale.
7. **Land cover:** a single 2021 snapshot.
8. **Geomorphology scale:** 1:250k is coarse, and valley-floor polygons absorb road-side slides.
9. **Lithology mapping:** the first-listed-rock rule is a stated assumption; 204 mixed descriptions are flagged for review in the mapping table.
10. **Stream threshold:** calibrated against OSM, which under-maps small streams; the optimum may lie between 1 and 2 km².
11. **HAND:** experimental, without landslide-specific literature.
12. **NDVI:** not harmonised across Landsat sensors; 2 events have fewer than 3 clear images.
13. **Boundaries:** geoBoundaries follows administered boundaries, so its areas differ slightly from official state areas, which include claimed land.
14. **DEM:** GLO-30 may have artefacts on steep, shadowed, glaciated slopes.
15. **Reporting bias and model target:** the models learn *reported* landslides, which are mostly slides on or near roads, especially highways. Road distance is among the strongest features (§17.4), partly through real slope effects of road cuts and partly because slides on roads are the ones that get recorded. The models are therefore valid for road corridors only, and their skill must not be read as skill for landslides in general. Results without road features are kept as a sensitivity check (§17.4, §17.6).
16. **Many slides are missed even at the lower alert level:** at Watch (0.35) about 45% of recorded HP slides (41% across the three states) score below the level; at Warning (0.45) about two-thirds are missed (cross-validated, §17.7). This is in line with published nowcasts: LHASA's evaluations detected 8–60% of catalogued landslides depending on period, rainfall product and window size (Kirschbaum & Stanley 2018, as summarised in the Eos research spotlight "A near-real-time tool to characterize global landslide hazards", https://eos.org/research-spotlights/a-near-real-time-tool-to-characterize-global-landslide-hazards). But it means a quiet day is not a guarantee of safety.

---

## 16. Phase B: no-landslide (negative) examples and training table

**Design note:** `docs/phaseB_design_note.md` (approved 22 Oct 2026) · **Scripts:** `src/phaseB_make_type1.py`, `src/phaseB_make_type2.py`, `src/phaseB_extract.py`, `src/phaseB_assemble.py` · **Output:** `data/phaseB/training_table_v1.csv`

### 16.1 Why negatives are needed
A model learns by comparing landslide cases (label 1) with no-landslide cases (label 0). If the no-landslide cases are easy (dry days, flat ground far from roads), the model only learns trivial differences. The negatives must look like the positives in every way except "a landslide happened".

### 16.2 Design

**Training region:** HP, Uttarakhand, UT of J&K. **Ladakh is excluded** (12 positives), because it lies outside the monsoon belt that justified pooling the three states. Training positives: **969**.
**Date range for negatives:** 2005-01-01 to 2025-09-30, the period of final (not provisional) IMERG rainfall.

| | Type 1: same place, safe day | Type 2: similar place, storm day |
|---|---|---|
| **Teaches** | What rain does (same ground, different weather) | What terrain does (same weather, different ground) |
| **Count** | 1 per positive → **969** | 2 per positive, max 10 per storm date → **1,198** |
| **Location** | Same coordinates as the positive | Random 30 m cell in the same state: slope ≥ 10.9°, ≤ 284 m from a motorable road, ≥ 2 km from any recorded landslide (any date) |
| **Date** | Random date from a pool of 250 dates whose months follow the positives' month mix; no recorded landslide within 5 km and ±30 days | The storm date itself |
| **Features** | Fixed features (terrain, roads, rock, faults, landforms, land cover) copied from the positive; NDVI, rain, soil and snow computed for the new date | All 42, via `stack.extract_features` |

**Total:** 2,167 negatives against 969 positives (about 2.2 : 1). The per-storm cap stops 2013-06-16 from dominating: it contributes 10 Type 2 negatives, not 242.

### 16.3 Basis

- **Absence at landslide locations and at other locations.** Space–time landslide models sample absence observations both at landslide locations on other dates and at non-landslide locations (Steger et al. 2024).
- **Keep negatives away from mapped landslides.** Buffer-based selection of non-landslide samples gave better models than whole-area random selection, for both XGBoost and Random Forest (Zhu et al. 2024).
- **NASA LHASA v2** drew negatives at random across space and time, at about 100 : 1, with no buffer, and warned that random train/test splits reduce the independence of validation (Stanley et al. 2021). This project uses hard negatives instead, and holds out whole storms or years in Phase C.
- **Thresholds from this project's data (data test on the 969 training positives):** 88% occur in June–September; 90% lie on slopes ≥ 10.9° (10th percentile); 90% lie within 284 m of a road (90th percentile).

### 16.4 How it was built
1. `phaseB_make_type1.py` builds the date pool (seed 20261022) and assigns each positive a safe date.
2. `phaseB_make_type2.py` sets the per-date quotas and finds candidate cells. A 30 m `stratifiedSample` over whole states timed out, so uniform random points were drawn in each state's bounding box and checked in GEE at their 30 m cell (inside the state, slope, road distance, 2 km buffer), in batches of 2,000 until each state's quota was met. The rules are unchanged.
3. `phaseB_extract.py` submitted 6 export jobs (3 per type, split by date). Type 1 jobs compute only NDVI, rain, soil and snow.
4. `phaseB_assemble.py` reads the 6 assets, copies Type 1 fixed features from the positives, and writes the tables.

**GEE assets (new; nothing was overwritten):** `negB_type1_a` (349 points), `negB_type1_b` (300), `negB_type1_c` (320), `negB_type2_a` (376), `negB_type2_b` (420), `negB_type2_c` (402). Task IDs are in `data/phaseB/phaseB_tasks.log`.

### 16.5 Checks (re-run independently on 23 Oct 2026)

| Check | Result |
|---|---|
| Size | 3,136 rows × 51 columns (969 positives + 969 Type 1 + 1,198 Type 2); all 42 features present |
| Duplicates, Ladakh | 0 duplicate ids; 0 Ladakh rows |
| Per state (positives / Type 1 / Type 2) | HP 195 / 195 / 324 · UK 548 / 548 / 487 · J&K 226 / 226 / 387 |
| Positives unchanged | The 969 positive rows equal `positives_features_v1` (Ladakh removed) |
| Type 1 fixed features | Identical to the source positive for all 969 rows |
| Type 1 rule (5 km, ±30 days) | 0 violations; dates 2005-06-17 to 2025-09-18; 244 distinct dates |
| Type 2 rules | Nearest recorded slide ≥ 2.0 km; slope ≥ 10.9°; road ≤ 284 m; max 10 per date; all 340 dates are positive dates |
| Missing cells | 2, both `swe_dm1_mm` at ERA5-Land glacier cells (masked on purpose, as in Step 6) |
| June–September share | Positives 88%, Type 1 79%, Type 2 82% |
| Provisional IMERG in the 31-day window | Positives 8 rows, Type 1 0, Type 2 16 |

**Medians**

| Feature | Positives | Type 1 | Type 2 |
|---|---|---|---|
| slope_deg | 28.7 | 28.7 | 25.9 |
| dist_road_m | 22 | 22 | 115 |
| dist_stream_m | 207 | 207 | 557 |
| elevation_m | 1,228 | 1,228 | 1,444 |
| imerg_d0 (mm) | 33.8 | 1.5 | 8.0 |
| imerg_ant7d (mm) | 89.1 | 30.2 | 64.6 |
| imerg_ant30d (mm) | 217.1 | 145.4 | 269.2 |
| sm_l1_dm1 (m³/m³) | 0.448 | 0.415 | 0.450 |
| ndvi_pre365 | 0.43 | 0.43 | 0.56 |

**Reading:**
- Type 1 matches the positives on all fixed features and differs mainly in rain, as designed.
- Type 2 shares the storm date, so its 30-day rain is similar to the positives, but on the day itself it is much drier (8 vs 34 mm): recorded slides sit where the storm hit hardest.
- Type 2 points are farther from roads (115 vs 22 m) and from streams, and greener. Recorded slides cluster on roads partly because that is where they are reported, so the model may learn "near a road" as a reporting effect. Phase C measures this.

### 16.6 Limitations
1. **Label noise:** "no landslide recorded" is not "no landslide happened". Some negatives, especially Type 2 on storm days, may be unrecorded slides. The 2 km buffer reduces but cannot remove this.
2. **Road distance:** Type 2 is limited to ≤ 284 m from a road, but its median (115 m) is still far from the positives' (22 m), because the road-bias of the inventory is stronger than the sampling rule.
3. **Different year mix:** positives cluster in 2013 (288) and 2025 (260); Type 1 dates are spread evenly over 2005–2025. Year itself is not a feature, but columns that depend on the satellite record of a year (`ndvi_pre_n`, the IMERG completeness flags) could let a model tell years apart. Phase C keeps these data-quality columns out of the model.
4. **Seasonal mix:** Type 1 has fewer monsoon dates (79% vs 88%), because the 5 km / ±30-day rule rejects more monsoon dates.

---

## 17. Phase C: model comparison

**Script:** `src/phaseC_01_train_compare.py` · **Outputs:** `data/phaseC/` (`cv_metrics.csv`, `threshold_table.csv`, `permutation_importance.csv`, `road_check.csv`, `oof_predictions.csv`, three figures) · **Status:** comparison done (23 Oct 2026); the alert threshold and the road-feature question are open decisions.

### 17.1 Set-up

- **Data:** `training_table_v1.csv` (969 positives, 2,167 negatives).
- **Features: 38** of the 42. Left out:
  - `ndvi_pre_n`, `imerg_images_31d`, `imerg_provisional_31d`: data-quality counts, not ground conditions. **Data test:** the median `ndvi_pre_n` is 18 images for 2005–2012, 27 for 2013–2020 and 41 for 2021–2026, so it encodes the year of the satellite record. Positives and Type 1 negatives have different year mixes (§16.6), so this column could let the model tell them apart for the wrong reason.
  - `aspect_deg`: circular; `aspect_sin` and `aspect_cos` carry the same information.
- **Category columns** (`glim_code`, `rock_code`, `gm_code`, `lc_class`, `lc_class_30m`) are one-hot encoded. The 2 missing `swe_dm1_mm` cells are filled with the training-fold median.
- **Models:**
  - logistic regression (baseline; long-tailed distances and rain log-transformed, all columns scaled);
  - Random Forest, 500 trees (Breiman 2001);
  - XGBoost, 400 trees, depth 4, learning rate 0.05 (Chen & Guestrin 2016), the model family of NASA LHASA v2 (Stanley et al. 2021).
  - No tuning, to keep the comparison simple.
- **Validation:** 5-fold blocked cross-validation that holds out **whole years** (main test) or **whole event dates** (second test), never random rows. Random CV overstates skill when data have time structure (Roberts et al. 2017; Brenning 2005). Every row gets a prediction from a model that never saw its year (or date).

### 17.2 Results

| Model | ROC AUC, year CV | PR AUC, year CV | ROC AUC, date CV | ROC AUC, year CV, HP rows only |
|---|---|---|---|---|
| Logistic regression | 0.780 | 0.621 | 0.794 | 0.753 |
| Random Forest | 0.801 | 0.639 | 0.819 | 0.790 |
| **XGBoost** | **0.807** | **0.649** | **0.834** | **0.804** |

- Holding out whole years is the stricter test: every model scores 0.01–0.03 lower than with date blocking, because nearby dates in the same year (one monsoon) share weather.
- PR AUC depends on the sample ratio (969 : 2,167); the no-skill value is 0.31.

### 17.3 Hit rate and false alarms

At the same hit rate the three models give almost the **same false-alarm rate on safe days** (Type 1). They differ only on Type 2 (other slopes on storm days):

| Hit rate | Safe-day false-alarm rate (LR / RF / XGB) | Storm-day false-alarm rate (LR / RF / XGB) |
|---|---|---|
| 50% | 0.20 / 0.19 / 0.20 | 0.10 / 0.06 / 0.05 |
| 60% | 0.26 / 0.24 / 0.27 | 0.15 / 0.10 / 0.07 |
| 70% | 0.33 / 0.33 / 0.37 | 0.21 / 0.16 / 0.12 |
| 80% | 0.42 / 0.47 / 0.50 | 0.32 / 0.29 / 0.22 |

**False alarms per month (proxy):** Type 1 negatives are random days at landslide spots, so "safe-day rate × 30" approximates the false alarms per month at one landslide-prone spot, mostly in monsoon months. For XGBoost: hit rate 60% ≈ 8 false alarms per month at one spot; 50% ≈ 6; 42% (threshold 0.5) ≈ 5. These are per spot, not per district; Phase E replays real storms on the HP grid to get district-level counts. Full table: `data/phaseC/threshold_table.csv`.

**Reading:** the weather signal tells landslide days from safe days at the same place only moderately well (ROC AUC 0.71–0.75 against Type 1, for all models). Most of the extra skill of the tree models comes from telling landslide spots from other slopes, where road distance dominates (§17.4).

### 17.4 How much the models rely on distance to road

| Check (year CV) | Logistic | Random Forest | XGBoost |
|---|---|---|---|
| Permutation importance rank of `dist_major_road_m` | 1 | 1 | 2 |
| Permutation importance rank of `dist_road_m` | no effect (−0.003) | 3 | 3 |
| ROC AUC with all features | 0.780 | 0.801 | 0.807 |
| ROC AUC **without** both road features | 0.762 | 0.755 | 0.737 |
| AUC vs Type 1 negatives (road identical): with / without road | 0.744 / 0.753 | 0.746 / 0.751 | 0.723 / 0.706 |
| AUC vs Type 2 negatives (road differs): with / without road | 0.809 / 0.769 | 0.846 / 0.758 | 0.875 / 0.763 |

(Rank 1 = the largest drop in ROC AUC when the column is shuffled. The other top-3 feature in every model is `imerg_d0`, rain on the day: rank 1 for XGBoost, rank 2 for logistic regression and Random Forest.)

**Reading:**
- Road distance matters a lot, and most of all for XGBoost: removing it costs 0.07 AUC, and XGBoost falls from best to worst.
- Road distance can only help against Type 2: Type 1 shares the positive's location, so road distance is identical, and removing it changes nothing there.
- `dist_major_road_m` ranks above `dist_road_m`. Type 2 points were matched to *motorable* roads (≤ 284 m) but not to major roads, while recorded slides sit close to highways (median 47 m, §6). Slides on highways are the ones that get reported.
- Part of this is real physics: road cuts destabilise slopes, and road construction is a known driver of landslides in South Asia (§6; Froude & Petley 2018). Part is reporting bias. The data cannot separate the two.
- Without road features, logistic regression is the strongest model (0.762).

### 17.5 Decision on road features (Suraj, 23 Oct 2026)
**Keep the road features**, tentatively with XGBoost, on three conditions:
1. Compare all models on the Type 1 test alone (positives vs same-place safe days, where road distance cannot help). If XGBoost with roads is clearly worse there than the road-free models, review the choice (§17.6).
2. Limit the risk map and alerts to road corridors, about 500 m from a motorable road (§17.8).
3. Describe the target as "reported landslides near roads", state the reporting-bias limitation (§2, §15 item 15), and keep the road-free results as a sensitivity check (§17.4, §17.6).

### 17.6 Type 1 test: how well each model reads the weather
Type 1 negatives share the positives' locations, so all fixed features, roads included, are identical. This test isolates the day-to-day weather signal that a daily warning depends on.

**Decision rule, fixed before the test:** a model counts as *clearly worse* than another if its ROC AUC on this test is lower and the 95% interval of the difference lies entirely below zero. The interval comes from a block bootstrap that resamples whole years, 2,000 times (rows from the same year share weather). Script: `src/phaseC_02_type1_check.py`; outputs `data/phaseC/type1_check.csv`, `type1_differences.csv`, `type1_equal_hit.csv`.

| Model (year CV) | ROC AUC, Type 1 test | 95% interval |
|---|---|---|
| Logistic, with roads | 0.744 | 0.678–0.793 |
| Random Forest, with roads | 0.746 | 0.645–0.813 |
| XGBoost, with roads | 0.722 | 0.637–0.791 |
| Logistic, no roads | 0.753 | 0.676–0.819 |
| Random Forest, no roads | 0.751 | 0.652–0.820 |
| XGBoost, no roads | 0.706 | 0.611–0.788 |

| Comparison (with roads minus road-free) | Difference | 95% interval | Clearly worse? |
|---|---|---|---|
| XGBoost − logistic (no roads) | −0.031 | −0.061 to −0.009 | **Yes** |
| XGBoost − Random Forest (no roads) | −0.029 | −0.044 to −0.010 | **Yes** |
| Random Forest − logistic (no roads) | −0.007 | −0.049 to 0.019 | No |
| Random Forest − Random Forest (no roads) | −0.006 | −0.016 to 0.003 | No |
| Logistic − logistic (no roads) | −0.009 | −0.031 to 0.012 | No |
| Logistic − Random Forest (no roads) | −0.008 | −0.035 to 0.041 | No |

**Result:** by the rule, **XGBoost with roads is clearly worse** at reading the weather than both road-free models, by about 0.03 AUC. Random Forest and logistic regression with roads are not. At a 70% hit rate, XGBoost flags 37% of safe days, against 30% for road-free logistic regression and 33% for Random Forest with roads.

### 17.7 Alert-threshold options
Script: `src/phaseC_03_threshold_options.py`; output `data/phaseC/threshold_options.csv`. Year-blocked out-of-fold predictions. "False alarms per month" = safe-day false-alarm rate × 30, at one landslide-prone spot (proxy; §17.3). HP rows: 195 positives, 195 Type 1, 324 Type 2.

**Random Forest, with roads**

| Threshold | Hit rate (all) | Hit rate (HP) | Safe-day false alarms (all) | Safe-day false alarms (HP) | ≈ False alarms / month, HP |
|---|---|---|---|---|---|
| 0.25 | 76% | 77% | 42% | 35% | 10.6 |
| 0.30 | 69% | 67% | 32% | 25% | 7.5 |
| 0.35 | 59% | 55% | 24% | 16% | 4.8 |
| 0.40 | 48% | 44% | 17% | 10% | 3.1 |
| 0.45 | 38% | 33% | 11% | 5% | 1.5 |

**XGBoost, with roads**

| Threshold | Hit rate (all) | Hit rate (HP) | Safe-day false alarms (all) | Safe-day false alarms (HP) | ≈ False alarms / month, HP |
|---|---|---|---|---|---|
| 0.15 | 75% | 77% | 43% | 39% | 11.5 |
| 0.20 | 69% | 68% | 36% | 31% | 9.4 |
| 0.30 | 60% | 56% | 28% | 25% | 7.4 |
| 0.35 | 56% | 51% | 24% | 23% | 6.8 |
| 0.40 | 51% | 48% | 22% | 20% | 6.0 |

At similar HP hit rates, Random Forest raises fewer safe-day false alarms than XGBoost (e.g. 55% vs 51% caught with 16% vs 23% of safe days flagged). The two models' probability scales differ (Random Forest's are compressed towards the middle), so the same threshold number does not mean the same thing for both. The HP sample is small (195 slides), so HP figures are uncertain by several percentage points.

### 17.8 Road-corridor limit
Share of training rows within a given distance of a motorable road:

| Rows | ≤ 300 m | ≤ 500 m | Farthest |
|---|---|---|---|
| Positives (and Type 1, same places) | 90.2% | 92.8% | 17.8 km |
| Type 2 | 100% | 100% | 284 m |

The model has seen almost no data far from roads, so the risk map and alerts are limited to cells within 500 m of a motorable road. About 7% of recorded slides lie beyond 500 m and would fall outside the warned area.

### 17.9 Model choice (Suraj, 23 Oct 2026)
**Random Forest with road features.** Reasons:
- Its overall skill is close to XGBoost's (ROC AUC 0.801 vs 0.807; HP 0.790 vs 0.804).
- It is not worse than the road-free models on the Type 1 test, while XGBoost is (§17.6), so it relies less on roads at the expense of the weather signal that drives a daily warning.
- At similar HP hit rates it flags fewer safe days (§17.7).

XGBoost with roads and the road-free models stay documented as comparisons.

### 17.10 Alert levels (Suraj, 24 Oct 2026): two levels, both provisional

| Level | Random Forest score | HP slides caught | HP safe days flagged | ≈ False alarms / month at one spot (HP) | Meaning for authorities |
|---|---|---|---|---|---|
| **Watch** | ≥ 0.35 | 55% | 16% | 4.8 | Conditions favour landslides; be ready |
| **Warning** | ≥ 0.45 | 33% | 5% | 1.5 | High likelihood; act |
| (none) | < 0.35 | | | | No alert |

(Cross-validated, year-blocked; §17.7. Across all three states: Watch catches 59%, Warning 38%.)

**Basis:** operational nowcasts use graded levels rather than one cut-off. NASA's LHASA issues daily *moderate* and *high* hazard levels on a ~1 km grid (LHASA nowcast README; Stanley et al. 2021).

**Why provisional:** these levels are set per point (one road-corridor cell). Alerts go out per **district**, so a district rule is needed (e.g. a district is on Watch when at least N corridor cells, or X% of them, score ≥ 0.35). The point levels and the district rule are therefore fixed together after the Phase E storm replays.

**How they will be finalised (criteria written down before the replays):**
1. **Hit check:** for each replayed storm, the affected district must be on Watch or higher on the event day or the day before.
2. **Quiet-day check:** count Watch and Warning days per district on quiet days, meaning monsoon days with no recorded slide in that district.
3. **Fair replay:** each storm is replayed with a model trained **without that storm's year**, as in the year-blocked cross-validation. The final model has seen every storm in the inventory (e.g. 32 slides on 2023-08-14 around Mandi), so replaying with it would overstate skill.
4. The levels and the district rule may move after the replays; any change and its reason is recorded here and in the CHANGELOG.

**Replay design, fixed on 6 Nov 2026 before any replay was scored:**
- **Days** (`src/phaseE_01_replay_dates.py`, `data/phaseE/replay_dates.csv`): every HP date with ≥ 3 recorded landslides (16 storm days, 2010–2025), the day before each, and 2 random monsoon days (15 Jun–30 Sep) per storm year with no recorded HP slide within 3 days (16 quiet days). 46 dates.
- **Checks:** 44 storm-district checks (a district with a recorded slide that day; hit = Watch or higher on that day or the day before) and 192 quiet district-days (12 districts × 16 quiet days; false alarm = Watch or higher).
- **Candidates:** model (live Random Forest, two-part), road-neutral scoring, district share of cells needed (1, 2, 5, 10, 20, 30%), counted over all cells or only cells within 500 m of a road. Point levels stay as set by the HP safe-day false-alarm rates (Watch 25.6%, Warning 13.3%).
- **Selection rule:** the candidate with the highest true skill statistic, TSS = hit rate − false-alarm rate (Peirce skill score; Wilks 2006), on district-days. Ties: fewer quiet-day false alarms, then the simpler rule (all cells). Basis: territorial early-warning systems are evaluated per warning zone and per day with a 2×2 table of correct, missed and false alerts (Calvello & Piciullo 2016, EDuMaP; Piciullo et al. 2017), and rainfall thresholds are calibrated by maximising such skill scores rather than by fixing a hit rate first (Gariano et al. 2015). A fixed minimum hit rate was considered and not used, because any value would be a judgement without a source.
- **Known biases, stated in advance:** the rule is chosen and scored on the same 46 days, so its scores are slightly optimistic; unreported landslides make some "quiet" days not truly quiet, so the false-alarm rate is an upper bound (Gariano et al. 2015 note the same issue).

**Final rule, adopted by Suraj on 9 Nov 2026 after the replays** (results: `data/phaseE/`, plain-language version: `docs/alert_rule_explained.md`):

| | Value |
|---|---|
| Model | Live Random Forest `rf_roads_live_v1` (28 features: IMERG + fixed), road-neutral scoring |
| Cell Watch / Warning | score ≥ 0.376 / ≥ 0.463 (scores at which 25.6% / 13.3% of HP same-place safe days are flagged, road-neutral out-of-fold scores) |
| District rule | a district is at a level when **≥ 30% of its cells within 500 m of a road** reach that level |
| Replay result, Watch | 38 of 44 storm-district checks hit (86%); 28 of 192 quiet district-days alarmed (15%); TSS 0.718 (95% interval 0.545–0.870) |
| Replay result, Warning | 32 of 44 (73%); 3 of 192 (1.6%) |
| Old provisional rule (5%, all cells) | 43 of 44, but 84 of 192 false alarms (44%); TSS 0.540 |

Cautions: the top seven candidates are not statistically distinguishable (`data/phaseE/replay_uncertainty.csv`); 30% was the largest share tried and TSS was still rising there; the rule was chosen and scored on the same 46 days.

---

## 18. What comes next

1. **Hard negatives.** ✅ Done (§16).
2. **Model.** Compared (§17); final choice and alert threshold pending.
3. **Validation.** ✅ Year- and date-blocked CV done (§17).
4. **HP-wide maps.** Build the HP prediction grid **only within 500 m of motorable roads** (§17.8), in Python (the logic of `Current/27_step7_assemble_run`).
5. **Live pipeline.** A daily run for HP using IMERG provisional data, plus the alert route to the authorities. Consider IMERG Early Run (a few hours behind, outside GEE) and rainfall forecasts for warning lead time.
6. **Optional checks.** Run the JavaScript `*_run` scripts once in the Code Editor; review the MIXED rows in `lithology_mapping_v1.csv`; delete the duplicate `HP_geomorphology` asset.

---

## 19. References

Citations marked ✓ were checked by web search during this work (authors, year, journal, volume/pages or DOI). Those marked ○ are standard references cited from the original method or data provider and were **not** separately verified here.

**Landslide studies and reviews**
- ✓ Steger, S., Moreno, M., Crespi, A., Gariano, S.L., Brunetti, M.T., Melillo, M., Peruccacci, S., Marra, F., de Vugt, L., Zieher, T., Rutzinger, M., Mair, V., Pittore, M. (2024). Adopting the margin of stability for space–time landslide prediction. *Geoscience Frontiers* 15(3), 101822. doi:10.1016/j.gsf.2024.101822
- ✓ Zhu et al. (2024). Considering the effect of non-landslide sample selection on landslide susceptibility assessment (Huize County). *Geomatics, Natural Hazards and Risk* 15(1). doi:10.1080/19475705.2024.2392778
- ✓ NASA GES DISC. Global Landslide Nowcast (LHASA) v1.1, README: daily nowcast on a ~1 km grid with three levels (low, moderate, high). https://acdisc.gsfc.nasa.gov/data/Landslide/Global_Landslide_Nowcast.1.1/doc/README.Global_Landslide_Nowcast.pdf
- ✓ Roberts, D.R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40(8), 913–929. doi:10.1111/ecog.02881
- ✓ Breiman, L. (2001). Random forests. *Machine Learning* 45(1), 5–32. doi:10.1023/A:1010933404324
- ✓ Chen, T., Guestrin, C. (2016). XGBoost: a scalable tree boosting system. *Proc. 22nd ACM SIGKDD*, 785–794. doi:10.1145/2939672.2939785
- ✓ Brenning, A. (2005). Spatial prediction models for landslide hazards: review, comparison and evaluation. *Natural Hazards and Earth System Sciences* 5, 853–862. doi:10.5194/nhess-5-853-2005
- ✓ Singh, M., Khajuria, V., Singh, S., Singh, K. (2024). Landslide susceptibility evaluation in the Beas River Basin of North-Western Himalaya: a geospatial analysis employing the Analytical Hierarchy Process (AHP) method. *Quaternary Science Advances* 14, 100180. doi:10.1016/j.qsa.2024.100180
- ✓ Reichenbach, P., Rossi, M., Malamud, B.D., Mihir, M., Guzzetti, F. (2018). A review of statistically-based landslide susceptibility models. *Earth-Science Reviews* 180, 60–91. doi:10.1016/j.earscirev.2018.03.001
- ✓ Stanley, T., Kirschbaum, D. (2017). A heuristic approach to global landslide susceptibility mapping. *Natural Hazards* 87(1), 145–164. doi:10.1007/s11069-017-2757-y
- ✓ Kirschbaum, D., Stanley, T. (2018). Satellite-based assessment of rainfall-triggered landslide hazard for situational awareness. *Earth's Future* 6, 505–523. doi:10.1002/2017EF000715
- ✓ Stanley, T., et al. (2021). Data-driven landslide nowcasting at the global scale. *Frontiers in Earth Science* 9, 640043. doi:10.3389/feart.2021.640043
- ✓ Froude, M., Petley, D. (2018). Global fatal landslide occurrence from 2004 to 2016. *Natural Hazards and Earth System Sciences* 18, 2161. doi:10.5194/nhess-18-2161-2018
- ✓ McAdoo, B. G., Quak, M., Gnyawali, K. R., Adhikari, B. R., Devkota, S., Rajbhandari, P. L., Sudmeier-Rieux, K. (2018). Roads and landslides in Nepal: how development affects environmental risk. *Natural Hazards and Earth System Sciences* 18(12), 3203–3210. doi:10.5194/nhess-18-3203-2018 (title verified 13 Nov 2026)
- ✓ Leibundgut, G., et al. (2016). Rural earthen roads impact assessment in Phewa watershed, Western region, Nepal. *Geoenvironmental Disasters* 3, 13. doi:10.1186/s40677-016-0047-8 (title verified 13 Nov 2026)
- ✓ Time-varying NDVI as a landslide conditioning factor, Quang Ngai, Vietnam. *Open Geosciences* (2023). https://doaj.org/article/4326d226457a46d1b0ea99164b8cdb69
- ✓ Pre-event NDVI in a typhoon-triggered landslide model. ACRS 2016 poster. https://a-a-r-s.org/proceeding/ACRS2016/

**Hydrology and terrain**
- ✓ Yamazaki, D., Ikeshima, D., Sosa Moreno, J., Bates, P., Allen, G., Pavelsky, T.M. (2019). MERIT Hydro: a high-resolution global hydrography map based on latest topography dataset. *Water Resources Research* 55, 5053–5073. doi:10.1029/2019WR024873
- ✓ Nobre, A.D., Cuartas, L.A., Hodnett, M., Rennó, C.D., Rodrigues, G., Silveira, A., Waterloo, M., Saleska, S. (2011). Height Above the Nearest Drainage – a hydrologically relevant new terrain model. *Journal of Hydrology* 404, 13–29. doi:10.1016/j.jhydrol.2011.03.051
- ✓ Montgomery, D.R., Dietrich, W.E. (1988). Where do channels begin? *Nature* 336, 232–234. doi:10.1038/336232a0
- ○ Montgomery, D.R., Foufoula-Georgiou, E. (1993). Channel network source representation using digital elevation models. *Water Resources Research* 29, 3925–3934.
- ✓ Grill, G., et al. (2019). Mapping the world's free-flowing rivers. *Nature* 569, 215–221. doi:10.1038/s41586-019-1111-9
- ○ Zevenbergen, L.W., Thorne, C.R. (1987). Quantitative analysis of land surface topography. *Earth Surface Processes and Landforms* 12, 47–56.

**Geology**
- ✓ Hartmann, J., Moosdorf, N. (2012). The new global lithological map database GLiM. *Geochemistry, Geophysics, Geosystems* 13, Q12004. Data: doi:10.1594/PANGAEA.788537
- ○ Geological Survey of India, National Geoscience Data Repository (NGDR), Bhu-Chayan: Geology 50k (Lithology, Fault), Geomorphology 250k. https://geodataindia.gov.in

**Datasets**
- ✓ Huffman, G.J., et al. GPM IMERG Final Precipitation L3 Half Hourly 0.1° V07. NASA GES DISC. doi:10.5067/GPM/IMERG/3B-HH/07
- ✓ Funk, C., et al. (2015). The climate hazards infrared precipitation with stations — a new environmental record for monitoring extremes. *Scientific Data* 2, 150066. doi:10.1038/sdata.2015.66
- ✓ Muñoz-Sabater, J., et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. *Earth System Science Data* 13, 4349–4383. doi:10.5194/essd-13-4349-2021
- ✓ Zanaga, D., et al. (2022). ESA WorldCover 10 m 2021 v200. Zenodo. doi:10.5281/zenodo.7254221 (overall accuracy 76.7%)
- ✓ USGS Landsat Collection 2 Level-2 scale factors (×0.0000275 − 0.2). https://usgs.gov/faqs/how-do-i-use-scale-factor-landsat-level-2-science-products
- ○ Copernicus DEM GLO-30 (ESA/Airbus), GEE `COPERNICUS/DEM/GLO30_2024_1`.
- ○ geoBoundaries v6.0.0 ADM1, GEE `WM/geoLab/geoBoundaries/600/ADM1`.
- ○ OpenStreetMap contributors, via the HOT Export Tool (https://export.hotosm.org); OSM data © OpenStreetMap contributors, ODbL.
- ○ Bhusanket landslide inventory (GSI) and the NASA Global Landslide Catalog (WPRDC mirror) — the sources of the positive events, from the earlier phase.
