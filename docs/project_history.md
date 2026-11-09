# Landslide Early-Warning System for Himachal Pradesh: Complete Project Record

**Course:** ICTD (Information and Communication Technologies for Development and Sustainability), M.Tech, IIT Delhi, July–December 2026
**Instructor:** Prof. Aaditeshwar Seth · **NGO mentor:** Betwa Solutions (flood and landslide mapping, Sikkim)
**Team:** Suraj Raj (2026MCS2801) · Siddhesh Pohare (2026MCS2257)
**Record covers:** project start (August 2026) to 5 November 2026 · **Compiled:** 5 November 2026

Items marked **[to confirm]** come from incomplete notes and should be checked by the team before this record is shared.

**About the numbers.** The project went through several phases, each with its own working notes. Datasets, counts and scores from earlier phases (August–September) can differ slightly between those notes. Where they differ, this record gives the value from the result files in this repository, and the earlier value is kept where it explains a decision. The goal never changed: predicting rainfall-triggered landslides in Himachal Pradesh.

---

## Contents

1. [The project in one page](#1-the-project-in-one-page)
2. [Timeline](#2-timeline)
3. [Why this problem](#3-why-this-problem)
4. [August: proposal, literature review and first feedback](#4-august-proposal-literature-review-and-first-feedback)
5. [August–September: mentor tasks and setting up](#5-augustseptember-mentor-tasks-and-setting-up)
6. [September: building a dated landslide inventory](#6-september-building-a-dated-landslide-inventory)
7. [September: AHP susceptibility and change-detection track](#7-september-ahp-susceptibility-and-change-detection-track)
8. [September: first prediction prototype and Presentation 2](#8-september-first-prediction-prototype-and-presentation-2)
9. [October: rebuilding the data properly (the feature stack)](#9-october-rebuilding-the-data-properly-the-feature-stack)
10. [22 October: organising the project](#10-22-october-organising-the-project)
11. [Phase B: no-landslide (negative) examples](#11-phase-b-no-landslide-negative-examples)
12. [Phase C: models and honest testing](#12-phase-c-models-and-honest-testing)
13. [Phase D groundwork: from a model to a daily system](#13-phase-d-groundwork-from-a-model-to-a-daily-system)
14. [5 November: understanding the model](#14-5-november-understanding-the-model)
15. [Every decision, in one table](#15-every-decision-in-one-table)
16. [Mistakes we found and corrected](#16-mistakes-we-found-and-corrected)
17. [Not done, and why](#17-not-done-and-why)
18. [All data sources](#18-all-data-sources)
19. [Tools and working method](#19-tools-and-working-method)
20. [What exists now: assets, code and files](#20-what-exists-now-assets-code-and-files)
21. [Limitations](#21-limitations)
22. [Where we stand against the original goal](#22-where-we-stand-against-the-original-goal)
23. [What remains until 25 November](#23-what-remains-until-25-november)
24. [The work in numbers](#24-the-work-in-numbers)
25. [Who did what](#25-who-did-what)
26. [References](#26-references)

---

## 1. The project in one page

**Goal.** A daily landslide early-warning system for the whole of Himachal Pradesh (HP). Every day it scores landslide risk across the state, summarises it per district, and emails district authorities when the day's conditions, mainly rainfall, make landslides likely. It is meant as decision support for authorities, not a public alert and not a static map.

**What exists on 5 November 2026:**
- **A cleaned, dated landslide inventory:** 981 events from HP, Uttarakhand and Jammu & Kashmir, built from GSI's Bhusanket inventory (extracted from a 904-page PDF) and NASA's Global Landslide Catalog.
- **42 features for every event:** terrain, drainage, roads, rock type, faults, landforms, land cover, vegetation, rain, soil moisture and snow. All are computed at the event's own date by reusable Google Earth Engine (GEE) code.
- **2,167 carefully designed "no-landslide" examples,** giving a 3,136-row training table.
- **Three model types compared** with strict testing (whole years held out). A Random Forest was chosen and two alert levels (Watch and Warning) set provisionally.
- **A "live" model** that only uses data available on the morning it runs, plus a correction for the road-reporting bias.
- **Fixed features computed for all 55,253 one-kilometre cells of HP.**
- **A first whole-HP risk map** for a real storm day (14 August 2023), made with a model that never saw 2023.
- **A complete paper trail:** every change logged with evidence, every experiment recorded (including the dropped and wrong ones), and every method choice backed by a cited study or a data test.

**Honest result so far:**
- The system clearly learns where landslides happen, and it reads rainfall.
- It catches about half of recorded HP slides at the lower alert level, with a noticeable number of false alarms.
- Rain on the day alone is still as good at telling *when* as our model is. We have measured why: the satellite rain data and the reporting bias set the ceiling.

**Remaining:** the daily automation (email, map app), storm replays to set the final alert rules, the impact-assessment design, the final report (25 November), and the optional road-blockage detection study.

---

## 2. Timeline

| Date (2026) | What happened |
|---|---|
| Early Aug | Three project directions proposed. The instructor rejected the scheme-awareness chatbot and scoped warnings as authority-facing. |
| Aug | Literature review: Kullu valley, Beas basin and Chandra-Bhaga studies; GSI district susceptibility; GSI's regional forecasting system |
| **17 Aug** | **Presentation 1** (proposal) and the Assignment 1 position paper |
| After 17 Aug | Instructor feedback: AHP maps are common; rainfall-based prediction is under-explored but limited by data; small road slides are too small for open satellite data |
| Aug–Sep | NGO mentor's task list worked through; GEE account and cloud project set up; first Sentinel-1 and Sentinel-2 pulls over Kullu |
| Sep | Bhusanket PDF extracted (36,071 records); date audits; other inventories evaluated; Uttarakhand and J&K chosen by a two-stage method |
| Sep | AHP susceptibility model and Sentinel-2 change-detection validation for 10 HP sites |
| Sep | First prediction prototype (slope + CHIRPS rain, random negatives) |
| **17 Sep** | **Presentation 2** (methodology and prototype). Feedback: "negative sampling has some serious issue" |
| ~24 Sep | Assignment 2 report (dataset, methodology, preliminary results) **[to confirm date]** |
| Late Sep – 11 Oct | Environmental layers in GEE; inventory re-audit |
| 11–19 Oct | Corrected date parsing → positives v4 (986 events) |
| 19–22 Oct | Positives audited and cleaned → v5 (981); full 42-feature stack; technical documentation |
| 22 Oct | Project moved to one permanent folder; work log started; completion plan agreed (target 18 Nov) |
| 22–23 Oct | Hard negatives (2,167) and training table (3,136 rows) |
| 23–24 Oct | Three models compared with year-blocked testing; road and weather-only tests; Random Forest chosen; provisional Watch/Warning levels |
| 24 Oct | Data delays measured (CHIRPS ~24 days, ERA5-Land ~12 days); daily-system design drafted |
| 26 Oct | Research-paper presentation (Beas basin AHP study; a separate course task); brief written for an optional road-blockage detection study |
| 29 Oct | Team review: the road-corridor limit was reversed and the whole-HP goal restored |
| 1–2 Nov | Live model (IMERG + fixed features); road-neutral test; fixed features for all 55,253 HP grid cells |
| 5 Nov | All decisions reviewed; road-neutral scoring adopted; rain-only baseline, timing diagnostic, partial dependence, two-part model, strict-vs-easy testing, storm-day map (14 Aug 2023), quiet-day map (12 Sep 2023, running) |
| **6 Nov** | **Interim presentation (Assignment 3)**: problem, methodology, implementation, results |
| **25 Nov** | **Final presentation and final report**, including an impact-assessment section |

---

## 3. Why this problem

- **The hazard.** HP suffers frequent rainfall-triggered landslides. The 2023 monsoon alone brought more than 7,000 landslides, 509 deaths, about 12,300 homes destroyed or damaged and about 1,300 roads blocked for weeks (figures as cited in our Assignment 1 paper; primary source to be re-checked for the final report).
- **The gap.** Published HP studies produce **static susceptibility maps** (AHP or frequency ratio). They say *where* slides are likely, not *when*. GSI's regional landslide forecasting system covered only Shimla and Kinnaur in HP as of the 2025 monsoon.
- **Background.** Suraj studied civil engineering at IIT Mandi and lived in HP for four years. An earlier IIT Mandi practicum surveyed landslide-affected households in Mandi and Kullu. That survey motivated the topic, but it is **not** used as data here.
- **Target user.** District and state disaster authorities. The instructor's guidance: a system that sends its output to the responsible authority is enough, because public alerting is the authority's job.
- **What makes it ICTD.** The project turns free global data (satellite rain, terrain, geology) into a daily, district-level decision aid for an under-served mountain state, at zero data cost, and is designed so a partner organisation could take it over.

---

## 4. August: proposal, literature review and first feedback

**Directions proposed:**
1. Landslide prediction.
2. Post-landslide impact data (road blockage).
3. A chatbot platform for government-scheme awareness. The instructor rejected this one: it only redirects people to websites without acting on their behalf.

**Literature reviewed and verified** (full entries in §26):
- Meena et al. 2019, Kullu valley susceptibility, AUC 0.797–0.910.
- Singh et al. 2024, Beas basin AHP, AUC 0.863: the closest prior work.
- Dhiman et al. 2026, Chandra-Bhaga, AUC 0.90.
- GSI district susceptibility shares (from Chamba 42.86% to Shimla 14.95%).
- GSI's regional forecasting system (21 districts in 8 states; Shimla and Kinnaur in HP). A self-contradiction in our own draft, which listed Kinnaur as both covered and not covered, was caught and fixed.

**Data sources mapped:**
- DEM, land cover, rainfall (IMD gridded, CHIRPS, IMERG; IMD and GFS forecasts), geology, roads and post-event imagery.
- The post-event source was changed from optical Sentinel-2 to radar Sentinel-1, because monsoon cloud blocks optical images.

**Presentation 1 (17 Aug) and the Assignment 1 position paper,** "Rainfall- and Land-Change-Aware Landslide Risk Analysis for Himachal Pradesh". AHP was positioned as a baseline. Three research questions:
1. Does antecedent and forecast rain improve prediction beyond a static AHP baseline?
2. Can Bhusanket's activity fields tell new slides from reactivated ones?
3. Which terrain, land-use and rain combinations go with persistent movement?

Out of scope at that stage: small road-slide detection, a public dashboard, forecast experiments without an archive, and causal land-use claims.

**Instructor feedback:**
- AHP maps are abundant, so a new contribution must be clearer.
- Rainfall-based prediction is under-explored but needs dated data, and Bhusanket's PDF looked incomplete, with unclear dates.
- Landslides as continuing land movement could be studied with land-use change.
- Small road slides are too small for open satellite data.

**What we did with it:** question 1 (rainfall-based prediction) became the main thread, with AHP kept as a baseline.

---

## 5. August–September: mentor tasks and setting up

| Mentor's task | What we did and found |
|---|---|
| Remote-sensing tools, including CoRE Stack | CoRE Stack (IIT Delhi) covers land use, ecology and hydrology, not landslides. Studied, not integrated. |
| GEE account and radar (SAR) | GEE account and cloud project registered for non-commercial use. First Sentinel-1 composite over Kullu (Jul–Aug 2023, 26 images) after fixing a district-name bug ("Kulu" vs "Kullu"). Sentinel-2 composite (Oct–Nov 2023, 29 images). |
| Landslide types | Varnes classification (material × movement), as used in Bhusanket's survey form |
| Geology of Sikkim and HP | Both lie on the MBT/MCT Himalayan thrust system. HP slides are mainly rain-triggered; Sikkim adds earthquakes. Used later as the first filter for choosing extra states. |
| NISAR (new radar satellite) | Data public through NASA ASF from July 2026, but not in GEE and with little history. Not used. |
| Correlating trigger points | Deferred until the inventory audit was finished |

---

## 6. September: building a dated landslide inventory

A rainfall warning model needs landslides with **exact dates**. This turned out to be the hardest data problem of the project.

1. **Bhusanket extraction.** GSI publishes its national landslide inventory only as a 904-page PDF. We extracted it with `pdfplumber`: 36,976 raw rows → **36,071 clean rows** (HP 6,607), matching GSI's stated 36,072. A first cleaning filter missed a title row; it was fixed by keeping only rows with a numeric serial number.
2. **Date audit.**
   - A first count of "any text in the date field" gave HP 10.4%. That was wrong: it counted any text, not real dates (a missing-value bug first even gave 100%).
   - A proper day-level date parser gave **HP 114 (1.7%)** and India 5,313 (14.7%). Most HP records carry only month and year, so they can't be matched to daily rain.
3. **Other sources evaluated:**

| Source | Finding | Used? |
|---|---|---|
| Mendeley "geo-environmental HP dataset" (6,503 points) | Meant for static susceptibility; main file without coordinates; only 9 day-dated records, all duplicates of Bhusanket | No |
| **NASA Global Landslide Catalog** | 175 HP records, all dated; location accuracy varies (exact to 50 km). The official viewer and REST service failed, so we used the WPRDC mirror | **Yes** (good-accuracy, rain-triggered records) |
| NRSC/ISRO Landslide Atlas | PDFs and map layers only | No |
| IndLands | Unclear origin, no event dates | No |
| HPSDMA repository | Blocks automated access; no usable dated table | No |

4. **Choosing extra states by method, not by eye.** HP alone has too few dated slides. Two stages:
   1. The state must lie on the same Himalayan thrust system as HP.
   2. Rank by how similar its share of rain-triggered slides is to HP's: `1 − |share(state) − share(HP)|`.

   **Uttarakhand and J&K** were selected. They also had the largest usable samples (UK 555, J&K 240, HP 192 at that stage).
5. **Combined inventory v2:** 987 → 930 (unparseable dates removed) → **886** (8 impossible dates, such as 2028-03-29, removed).
6. **CHIRPS rainfall** extracted in GEE for all 886 events (878 complete), after fixing three upload and parsing errors.

---

## 7. September: AHP susceptibility and change-detection track

Mainly Siddhesh's work.

- **AHP susceptibility model** with 6 factors and weights: slope 36.4%, NDVI 23.2%, aspect 13.6%, NDWI 13.6%, BSI 8.0%, NBR 5.1%. Consistency ratio 0.0124, well below the 0.10 limit, so the weights are internally consistent. Maps were made for 10 HP sites.
- **Validation** against Sentinel-2 before/after change masks (dNDVI, dBSI, slope thresholds):
  - global AUC 0.624;
  - good at Mandi (0.835) and Shimla (0.833);
  - worse than random at Lahaul–Spiti (0.337).

  Diagnosis: vegetation indices carry little signal in high, rocky, sparsely vegetated terrain, and the factor set lacks lithology and elevation.
- **Mask fixes (v2):** an NDVI-only mask in Lahaul and a seasonal offset correction. Global AUC moved only to 0.626, and the offset fix was shown to be mathematically a no-op. A real fix needs new data (same-season image pairs, permafrost and lithology factors).
- **A finding that shaped the project:** about 90% of Bhusanket HP dates are month-year only. A monthly-rainfall-anomaly approach was planned for them, but it was superseded once the day-dated subset (Bhusanket + NASA) was assembled.
- **Satellite change detection as a "confirmation" layer** for the warning system: proposed, but no further work on this track after September (as of 5 Nov 2026).

---

## 8. September: first prediction prototype and Presentation 2

1. **Prototype:** landslide points with slope and CHIRPS antecedent rain; negative points drawn **at random** over the region (878, within the study area, at least 2 km from any slide, dates copied from slides ± 30 days).
   - Logistic regression: slope only, AUC 0.72; slope + rain, 0.83 (random split).
   - The merged final deck reported logistic regression 0.789 and **Random Forest 0.895** (5-fold cross-validation); 30-day rain was the most important factor.
2. **Presentation 2 (17 Sep, 20 slides).** Feedback:
   - "good effort in assembling a dataset";
   - "**negative sampling has some serious issue**": a rain-and-slope model gives high recall but low precision, so it raises too many false alarms and people stop trusting it.
3. **Assignment 2 report** (ACM format): dataset, methodology and preliminary results, with the precision problem treated as a finding **[to confirm final submitted version]**.

**What this feedback led to.** The October rebuild (§9–§12) is largely a direct answer to it:
- proper negatives (§11);
- strict testing (§12);
- a measured explanation of why 0.895 was too optimistic (§14.5).

---

## 9. October: rebuilding the data properly (the feature stack)

### 9.1 Working rules we adopted
1. Every method choice is backed by a verified reference or by an explicit data test, and the type of evidence is stated.
2. No guessed dataset IDs: every GEE dataset was checked in the catalogue before use.
3. The expected result is stated before running, and each step is checked against it.
4. No paid services: free GEE (non-commercial) and free data portals only.
5. Scripts are kept in `Current/` (in use) and `Archive/` (never deleted), named `NN_stepK_topic`, with a standard header (purpose, inputs, outputs, status, results) and an index script.
6. Each feature step has a **module** (defines the feature image, no side effects) and a **run** script (spot-checks, extracts at the landslides, exports), plus a Python mirror used to execute and verify it.

### 9.2 Boundaries and grid
- **Boundaries:** geoBoundaries v6 (ADM1), units selected by ID. FAO GAUL was dropped: GAUL 2015 is deprecated, and both GAUL versions store J&K as one disputed unit of about 186,000 km², including Gilgit-Baltistan and Azad Kashmir.
- **Common grid:** UTM zone 43N at 30 m, so terrain calculations use true metre spacing. Uttarakhand extends slightly outside zone 43; the scale error is below 0.3%.

### 9.3 Positives audit (Step 0): v4 (986) → v5 (981)

| Action | Record | What and why |
|---|---|---|
| Fix | BH_8569 | Longitude 75.153 → 77.153. Labelled HP/Solan with Survey of India sheet 53F/1 (77.00–77.25°E); 75.15°E lies in Punjab. Leading-digit typo. |
| Fix | BH_35971 | Latitude 31.945 → 30.945. Labelled Uttarkashi with sheet 53F/13; 31.945°N lies in Kinnaur. Digit typo. |
| Fix | BH_35861_1 | Date 2018-08-06 → 2025-08-06. The parser read "18 August" as the year 2018. |
| Add | BH_35861_3 | 2025-08-18: the third date in that same record, lost by the parser |
| Drop | BH_8460_2 | Date came from a lone "1" in the text; not recoverable |
| Drop | 5 duplicates | Same slide entered twice (Bhusanket: same date and < 5 m apart; NASA: same date and < 100 m apart) |
| Keep, tagged | 12 NASA points in Ladakh | Real events (e.g. the 2010 Leh cloudburst); later excluded from training |
| Clean | NASA IDs | The GEE upload had rewritten commas (`NASA_9,892` → `NASA_9_892`) |

**Result (`positives_v5`):**
- 981 events: HP 195, Uttarakhand 548, J&K 238 (UT J&K 226, Ladakh 12).
- By source: Bhusanket 728, NASA 253.
- 344 distinct dates, from 29 Jul 2005 to 7 Jul 2026.
- Strong clustering: 242 events on 16 Jun 2013 (Kedarnath disaster), 33 on 30 Jun 2016, 32 on 14 Aug 2023.

The September "trigger-consistency" claim (23.6% vs 11.7% of slides with almost no rain) rested on the wrong prototype dates. With corrected dates it reverses (Bhusanket 2.9%, NASA 11.9%), so the claim was dropped.

### 9.4 The 42 features: how and why

| Group (count) | Source | How | Why (evidence) | Checks |
|---|---|---|---|---|
| **Terrain (9):** elevation, slope, aspect (degrees, sine, cosine), plan and profile curvature, TPI, TWI | Copernicus GLO-30 DEM (2024 release); MERIT Hydro for TWI | No clipping (clipping masked pixels near state edges in the old scripts); Zevenbergen & Thorne curvature; TPI over 500 m; TWI = ln(a/tan β) | Core conditioning factors in the susceptibility literature (Reichenbach et al. 2018) | **Curvature tested on artificial surfaces** (planes, bowl, dome, valley, ridge). This revealed that GEE's fixed kernels put row 0 at the south, so the kernels were corrected. Town spot-checks: Shimla Ridge 2,206 m (published about 2,205). |
| **Drainage (2):** distance to stream, height above nearest drainage (HAND) | MERIT Hydro | **Stream threshold calibrated** against OpenStreetMap streams in four test areas (Kullu, Shimla, Chamoli, Ramban): 2 km² gave the best balance of recall and precision (F1 0.75) | A channel-start threshold must be calibrated, not borrowed (Montgomery & Dietrich 1988) | HydroSHEDS rivers rejected (big rivers only) |
| **Roads (2):** distance to motorable road, distance to major road | OpenStreetMap via the HOT Export Tool (HP 45,135 lines; UK 172,824; J&K and Ladakh 148,877; exports buffered 10 km beyond borders) | Exact distances with an 80 km search (30 km left gaps in remote Spiti and Ladakh) | Road building and hill cutting drive human-triggered slides, with India the leading country (Froude & Petley 2018) | Median landslide **22 m** from a road vs about 2 km for random points: the first sign of reporting bias |
| **Lithology (2):** GLiM rock class, main rock name | GSI NGDR 1:50k (HP 4,331 polygons; UK 4,554; J&K 4,229; Ladakh 3,485) | **516 free-text rock descriptions mapped by hand-written rules** to the 16 GLiM classes plus 49 main rock names; exact point-in-polygon lookups | GLiM is a published standard (Hartmann & Moosdorf 2012); classes left for the model to weigh rather than expert scores | Granites show the lowest slide density (1.3 per 1,000 km²), as expected; all 981 slides lie on mapped rock |
| **Faults (2):** distance to any fault, distance to thrust | GSI NGDR 1:50k fault layers | A line counts as a thrust if its type **or** name says "thrust", because J&K and Ladakh type most named thrusts as "fault inferred" | Standard factor in LHASA's global susceptibility map (Stanley & Kirschbaum 2017) | Landslides 1.9 km from a fault vs 5.3 km for random points |
| **Geomorphology (1):** landform class | GSI NGDR 1:250k | 30 shared legend classes | Used in the Beas basin study (Singh et al. 2024) | "Mass wasting products" holds only 3 slides, so it does not leak the answer |
| **Land cover (2):** class at the point, majority in 30 m | ESA WorldCover 2021 (10 m) | Point and 3×3 majority | Standard factor | Shimla Ridge = built-up, Lahaul = bare |
| **Vegetation (2):** NDVI over the 365 days before the event, number of clear images | Landsat 5/7/8/9 | Median of cloud-free images, ending the day before the event | **Leakage guard:** post-event images show the scar itself. Pre-event NDVI is supported by published studies | Forest 0.65, bare Lahaul 0.03 |
| **Rain, soil, snow (18):** IMERG rain on the day and 1/3/7/15/30 days before, wettest day of the past week; the same windows from CHIRPS; ERA5-Land soil water (2 layers), snow water, snowmelt; glacier flag | GPM IMERG V07 (half-hourly), CHIRPS daily, ERA5-Land daily | **Day 0 = the local Indian day (00:00–24:00 IST),** made possible by half-hourly IMERG; "rain today" kept separate from "rain before today" | Follows NASA's LHASA v2 blueprint: antecedent rain, soil moisture, snow (Stanley et al. 2021). ERA5-Land chosen over SMAP because SMAP starts in 2015 and would miss 2013 | Every 31-day window complete (1,488 half-hour images); CHIRPS values reproduced the old pipeline in 20 of 20 test cases; a glacier placeholder value (10,000 mm snow) found and masked |
| **Data flags (2):** IMERG completeness, provisional-data count | IMERG | Records which events use final vs provisional rain (8 recent events) | Transparency | Later removed from modelling (§12) |

**Final table:** 981 rows × 42 features, with exactly **1 empty cell out of 41,202** (the masked glacier value). A consistency test on 5 events reproduced every per-step value.

**Example (Mandi, 14 Aug 2023):** 85 mm of rain on the day, 136 mm in the 3 days before, 393 mm in 30 days, topsoil near saturation (0.43).

---

## 10. 22 October: organising the project

- **One permanent project folder** (`G:\ALL PROJECTS\Landslide Prediction Project`), organised as `src/` (code), `data/` (results), `docs/` (documentation), `models/`, plus a README, `requirements.txt` and an isolated Python environment. All 219 files were copied with matching checksums before the old folder was removed.
- **Work log (`CHANGELOG.md`)** from 22 Oct: every change with what, why, evidence and how to undo it. Nothing is overwritten without a backup; GEE assets are never overwritten.
- **Completion plan agreed:**

| Phase | Content |
|---|---|
| B | Training data (negatives) |
| C | Model |
| D | Daily system |
| E | Storm replays |
| F | Report and slides |

- **Speed decisions** (so the deadline could be met without cutting quality where it matters):
  - Python only from then on, with the Code Editor used only for the map app;
  - reuse fixed features wherever the location is the same;
  - about 2,000 negatives, with a cap per storm date;
  - one storm example for the forecast comparison.
- **Delivery decisions:**
  - alerts by email;
  - the demo shows both a live daily run and a replay of past storms;
  - forecast rain (GFS) fills only the most recent days in the live run, and training uses only observed rain.

---

## 11. Phase B: no-landslide (negative) examples

**Why.** A model learns by comparing landslides with non-landslides, so the negatives decide what it learns. The September random negatives were too easy:
- median elevation 3,868 m vs 1,228 m for the landslides;
- 408 of 878 above 4,000 m;
- median distance to road 4.8 km vs 22 m (Phase B notes; 2.6 km if only the 755 points inside our road layers are counted, rechecked 5 Nov).

These negatives were made in **September** for Presentation 2 (file `negatives_features_v3.csv`, 17 Sep). The Phase B notes PDF dates them to October; that date is a slip in the notes.

A model could separate them with "high, icy, flat or far = safe" and learn nothing about rain. That's exactly the false-alarm problem the instructor flagged.

**Design: two kinds of "hard" negatives.**

| | Type 1: same place, safe day | Type 2: similar place, storm day |
|---|---|---|
| Teaches | **When** (rain) | **Where** (ground) |
| Count | 969 (one per landslide; Ladakh excluded) | 1,198 (2 per landslide, at most 10 per storm date, 340 dates) |
| Location | Exactly the landslide's coordinates | Random spot in the same state with slope ≥ 10.9°, within 284 m of a motorable road, ≥ 2 km from any recorded slide |
| Date | A day with no recorded slide within 5 km and ±30 days; months follow the landslides' mix (88% June–September); 2005 to 30 Sep 2025 (final IMERG) | The storm date itself |
| Features | Fixed features copied from the landslide; rain, soil, snow and NDVI recomputed | All 42 recomputed |

**Where the thresholds came from:**
- 10.9° and 284 m are the 10th and 90th percentiles of our own landslides (data test).
- 5 km / ±30 days and 2 km are judgement values, stated as such.
- The cap of 10 per date stops the 2013 Kedarnath day (242 records) from dominating.

**Basis:**
- Steger et al. 2024 and the ICG2022 abstract: absences taken "at landslide locations and at non-landslide locations".
- Zhu et al. 2024: buffer-based negative selection beats random sampling.
- NASA LHASA v2 (Stanley et al. 2021): random space–time negatives, with a warning about random test splits.

**How it was built:**
- Type 1 dates came from a pool of about 250 dates (244 used) to keep GEE fast.
- For Type 2, a whole-state 30 m sampling job timed out. Random points were instead generated in batches of 2,000 and checked in GEE on their 30 m pixel; about 9% passed in HP.
- 6 GEE batch jobs computed the features.
- Fixed random seed (20261022).

**Checks (re-run independently):**
- 3,136 rows; no duplicates.
- Type 1 fixed features identical to their landslide (969/969); 0 rule violations.
- Every Type 2 point obeys every rule.
- Only 2 empty cells (glacier snow).

**Where the negatives are:**
- Type 2 sits in the same middle-hill road valleys as the slides (HP: mostly Shimla, Mandi, Sirmaur, Kangra, Chamba).
- Median elevation 1,444 m; median road distance 115 m.

**Rain medians (mm):**

| | On the day | 7 days before | 30 days before |
|---|---|---|---|
| Landslides | 34 | 89 | 217 |
| Type 1 | 1.5 | 30 | 145 |
| Type 2 | 8 | 65 | 269 |

A separate illustrated explainer, *Negative Points Generation Notes* (PDF), covers this phase in full.

---

## 12. Phase C: models and honest testing

1. **Testing method.** Whole years are held out: train on the other years, score the hidden year, repeat for every year (Roberts et al. 2017). Random-row testing would let a model see the same storm in training and testing. A second check holds out whole storm dates.
2. **Four features removed before modelling:**
   - `ndvi_pre_n` (clear-image count rises from 18 to 41 over the years, so it encodes the year, and positives and Type 1 have different year mixes);
   - the two IMERG data flags;
   - aspect in degrees (sine and cosine kept).

   That leaves 38 features.
3. **Three model types:**

| Model | AUC, all three states | AUC, HP only |
|---|---|---|
| Logistic regression | 0.780 | 0.753 |
| Random Forest | 0.801 | 0.790 |
| XGBoost | 0.807 | 0.804 |

4. **Finding: distance to a major road is the first or second most important feature in every model.**
   - Without road features: 0.762 / 0.755 / 0.737.
   - Road features help only against Type 2 negatives, and XGBoost's lead comes entirely from them.
   - It's partly physics (road cuts destabilise slopes) and partly reporting bias (slides on roads are the ones recorded).
5. **Weather-only test** (landslides vs same-place safe days, where roads can't help). The rule for "clearly worse" was fixed **before** running: lower AUC, with the 95% year-resampled interval of the difference entirely below zero.
   - XGBoost with roads: 0.722, **clearly worse** than the road-free models (−0.03).
   - Random Forest with roads: 0.746, fine.
6. **Decision (Suraj, 23 Oct): Random Forest with road features** (500 trees, at least 3 rows per leaf). Nearly as good overall, better at reading the weather, and fewer false alarms in HP at the same catch rate.
7. **Alert levels (24 Oct, provisional), as two graded levels, like NASA LHASA's moderate and high nowcast levels:**

| Level | Score | HP slides caught | HP safe days flagged |
|---|---|---|---|
| Watch | ≥ 0.35 | 55% | 16% |
| Warning | ≥ 0.45 | 33% | 5% |

   The rules for finalising them in the storm replays were written down in advance:
   - the district must be at Watch or higher on the event day or the day before;
   - alert days are counted on quiet monsoon days;
   - each storm is replayed with a model trained without its year.

8. **Saved model** `rf_roads_v1` with a model card (purpose, data, method, skill, limits). Scores are relative, not true daily probabilities, because training has 1 landslide per 2.2 negatives.

---

## 13. Phase D groundwork: from a model to a daily system

### 13.1 Data delays (checked in GEE, 24 Oct)

| Data | Delay | Usable daily? |
|---|---|---|
| IMERG rain | ~2 days | Yes |
| GFS forecast | runs complete in 6–12 h | Yes (live run only) |
| ERA5-Land soil and snow | ~12 days | No |
| CHIRPS rain | ~24 days (monthly release) | No |

How GFS rain is summed was tested: its rain total resets every 6 hours, so a day's rain is the sum of the four 6-hour block totals.

### 13.2 Live model (decided 1 Nov)

A separate model on IMERG plus fixed features only (28 features).

| | Full model (38) | Live model (28) |
|---|---|---|
| AUC (HP) | 0.801 (0.790) | 0.775 (0.763) |
| Weather-only test | 0.746 | 0.683 |
| HP safe days flagged at Watch / Warning | 16% / 5% | 26% / 13% |

- Rejected alternative: feeding IMERG into the CHIRPS slots. In these mountains the two correlate only 0.53–0.75, so the model would receive unfamiliar values.
- Both models are reported: 38 features is "best with complete data", 28 is "what actually runs".

### 13.3 Whole HP, the corridor detour, and road-neutral scoring

- **23 Oct:** the map was limited to cells within 500 m of a road, because all training data lie there. This shrank coverage to about a third of HP (18,277 of 55,253 cells).
- **29 Oct, team review:** that was against the goal. **Reversed:** all 55,253 cells are scored, and cells more than 500 m from a road are marked "lower confidence".
- **Option rejected:** adding remote negatives. Almost all landslides are near roads, so the model would learn "remote terrain = safe" through other features (Steger et al., EGU 2018, "Incompleteness matters").
- **Road-neutral scoring tested:** at prediction time every cell is treated as a roadside slope. At the same safe-day false-alarm rate (live model):

| | Real roads | Road-neutral |
|---|---|---|
| Slides caught | 37% | **49%** |
| Remote slides caught | 29% | 36% |
| Weather-only AUC | 0.683 | **0.741** |
| Other slopes flagged on storm days | 3% | **18%** |

- **Caveats:** only 70 remote slides (9 in HP), and remote false alarms can't be measured.
- **Decision (5 Nov):** road-neutral scores drive the district alerts and the main map. Real-road scores are kept as a second layer, "where slides are likely to hit roads".

### 13.4 The HP grid
- 55,253 one-km cells.
- The fixed-feature code was moved into a shared function and checked against the training values (**100 of 100 identical**).
- 8 GEE jobs computed all cells (all completed).

### 13.5 Daily-system design (drafted)
- **Daily run at about 10:00 IST on GitHub Actions:** latest complete forecast → day-0 features → score → daily GEE asset → district summary → email → map app.
- **District rule (provisional):** a district is at Watch/Warning when at least 5% of its cells are.
- **Secrets** (Earth Engine service key, Gmail app password, recipients) are kept in GitHub, never in files.

---

## 14. 5 November: understanding the model

**Principle stated by the team:** no tuning for a higher score. Understand why the system behaves as it does, correct real mistakes, and record every experiment, including the dropped and wrong ones.

### 14.1 Heavy-rain baseline
Rule: "alert if IMERG rain on the day ≥ 64.5 mm" (IMD "heavy rain").

| Test | Rain rule | Live model |
|---|---|---|
| Timing: slides vs same-place safe days, AUC | **0.824** (HP 0.805) | 0.683 (HP 0.705); road-neutral 0.741 (HP 0.779) |
| Full test, AUC | 0.743 (HP 0.675) | **0.775** (HP 0.763) |

**Meaning:** rain alone tells *when* better than the models, and the models tell *where* better than rain. An honest result, reported as is.

### 14.2 Timing diagnostic
A live model trained only on slides vs same-place safe days reaches timing AUC 0.769 (HP 0.802), close to rain alone. Most of the timing gap comes from mixing in storm-day negatives, which are as wet as the slides, so a single model learns to weigh rain less.

### 14.3 Partial dependence
- Rain on the day: risk rises from 0.23 to 0.46, steepest between 10 and 40 mm, then levels off. Physically sensible.
- 7-day rain: rises. Sensible.
- 30-day rain: flat. Not physical: storm-day negatives are as wet over 30 days.
- Slope: a spike near 10° caused by the ≥ 10.9° sampling rule.

Both oddities are traced to the sampling design, and recorded.

### 14.4 Two-part model
Following LHASA (Kirschbaum & Stanley 2018): a **where** part (Random Forest: slides vs other slopes on storm days, terrain only) × a **when** part (rain only).
- Live overall AUC 0.775 → **0.813** (HP 0.763 → 0.777).
- Other slopes flagged on storm days 13.9% → 7.4%.
- A logistic "when" part on log rain beat a Random Forest one (0.813 vs 0.793). Both were compared on the same test folds, so the chosen variant's score is slightly optimistic (recorded).
- Timing stays capped at about the rain-alone level, because the rain data sets the ceiling.

### 14.5 Strict vs easy testing
The same live model:

| Test | AUC |
|---|---|
| Whole years held out | 0.775 |
| Whole storm days held out | 0.792 |
| Random rows | 0.856 |

Random-row testing inflates scores by about 0.08 (timing by about 0.12). Together with the easy random negatives, this explains why September's 0.895 was too optimistic.

### 14.6 Storm-day map, 14 Aug 2023
Model retrained **without 2023**; whole HP; 31 recorded HP slides that day.
- Road-neutral: **all 31 slides fall in alert cells** (29 at Warning).
- But 67% of HP is at Watch or above, and all 12 districts reach Warning under the 5% rule, including Una with 9 mm of rain.
- The Warning zone follows the day's rain (Kangra–Mandi–Kullu–Shimla); the dry trans-Himalaya stays mostly quiet.
- Real roads: 10 of 31 slides in alert cells (grid-cell centres are often farther from a road than the slide itself).

**Meaning:** the 5% district rule is far too loose, and cell levels over-warn on big storm days. Both are to be set in the replays. One day is an illustration, not a validation. A bug that dropped 255 border cells was found by a count check and fixed: the rerun with all 55,253 cells gave the same picture (Watch+ 66.8%, Warning 47.2%; two-part model 66.6% / 31.5%; all 31 slides in alert cells).

### 14.7 Quiet-day map, 12 Sep 2023
A day with no recorded HP slide within ±10 days (and none in the three states within ±3 days). Same model trained without 2023, same levels as the storm day.

| | Storm day, 14 Aug 2023 | Quiet day, 12 Sep 2023 |
|---|---|---|
| HP mean rain on the day | 40.3 mm | 0.8 mm |
| HP at Watch or above (road-neutral) | 66.8% | **0.4%** |
| HP at Warning | 47.2% | **0.0%** |
| Districts alerted (of 12), single / two-part model | 12 / 12 | **0 / 0** |

**Meaning:** the system clearly separates a disaster day from a quiet day. **Caveat:** the quiet day was also nearly dry, so this shows the system stays calm when it does not rain. The harder test (wet days without slides) comes from the storm replays (Phase E). Figure: `docs/figures/storm_vs_quiet_20230814_20230912.png`.

A counting slip was found on the way: the 255 border cells outside every district outline had been treated as a 13th "district" in the district tables. District levels now cover the 12 real districts only; the cells stay on the map.

---

### 14.8 Research question 1: does rainfall add to terrain? (6 Nov)
- **First attempt, not a fair test:** a terrain-only model on all rows scored 0.419 (timing 0.060), below coin toss. Each landslide's same-place twin has identical terrain and the opposite label, so when one is tested the other is in training and a terrain-only model learns "this spot = the opposite label". Recorded as a lesson about the paired design.
- **Fair test** (landslides vs other slopes on storm days, trained without the twins): terrain only 0.912 (HP 0.858); + vegetation 0.918; + IMERG rain 0.926 (HP 0.870); + all rain, soil and snow 0.928 (HP 0.877).
- **Answer:** telling *when* comes entirely from rainfall (terrain is the same every day; rain alone scores 0.805 in HP on the timing test). Telling *where* on a storm day is mostly terrain, and rain adds a little. The terrain score includes road distance and therefore reporting bias.

### 14.9 Correction to Presentation 2
Presentation 2 described its 878 background points as sampled inside HP with a 500 m buffer. Mapping the file shows them spread over HP, Uttarakhand, J&K and beyond (up to 36.9° N). Stated in the Assignment 3 deck.

### 14.10 Storm replays and the final alert rule (6–9 Nov)
- **Days, fixed by rule before scoring:** every HP date with ≥ 3 recorded slides (16 storm days, 2010–2025), the day before each, and 16 random quiet monsoon days. 44 storm-district checks, 192 quiet district-days.
- **Fair test:** each day scored with models trained without its year; scoring code reproduces the published 14 Aug 2023 map exactly.
- **Speed-up:** GEE ran exports one at a time, and vegetation (NDVI) was 95% of the cost; NDVI barely changes over 90 days (median change ≤ 0.010), so it was computed once per year; rain was read per day at IMERG's own pixels (identical to the training extraction for all but ≤ 3 of 55,253 cells).
- **Choice by a rule agreed in advance** (highest TSS = hit rate − false-alarm rate; Calvello & Piciullo 2016; Gariano et al. 2015): live Random Forest, district at a level when ≥ 30% of its road-zone cells reach it. Watch: 86% of affected districts caught, 15% false alarms on quiet district-days (old 5% rule: 98%, 44%). Warning: 73%, 1.6%.
- **Honest limits:** the top candidates are statistically tied; 30% was the edge of the range tried; misses are local storms.
- **Plain-language explanation:** `docs/alert_rule_explained.md`.

## 15. Every decision, in one table

| Date | Decision | Alternatives considered | Why | Trade-off accepted |
|---|---|---|---|---|
| Aug | Landslide prediction as the project; warnings for authorities | Scheme chatbot; public alerts | Instructor feedback; authority is the right user | No direct public reach |
| Aug | AHP as a baseline only | AHP as the main contribution | AHP maps already abundant in HP | — |
| Aug | Sentinel-1 radar for post-event imagery | Sentinel-2 optical | Monsoon cloud | Radar is harder to interpret |
| Sep | Day-dated events only (Bhusanket + NASA) | Monthly-anomaly approach for month-dated records | Daily rain needs daily dates | Small sample (HP 195) |
| Sep | Add Uttarakhand and J&K as training data | HP only | HP alone too small; states chosen by a two-stage method | Terrain and climate differ a little |
| Oct | geoBoundaries instead of FAO GAUL | GAUL 2015/2025 | GAUL deprecated; J&K stored as one disputed unit | — |
| Oct | MERIT streams at 2 km² | HydroSHEDS; other thresholds | Calibrated against OSM (best F1) | OSM under-maps small streams |
| Oct | 80 km road search | 30 km | No gaps in remote areas | — |
| Oct | GLiM classes + main rock name, no expert scores | Expert-scored lithology | Let data weigh classes; expert scores can be wrong | 204 mixed descriptions flagged |
| Oct | Pre-event NDVI (365 days before) | Post-event NDVI | Avoids leaking the scar | Older sensors not harmonised |
| Oct | IST event day from half-hourly IMERG | UTC day | Inventories record local dates | — |
| Oct | ERA5-Land soil and snow | SMAP | SMAP starts in 2015 | ~11 km cells |
| 21 Oct | Ladakh excluded from training | Keep | 12 points, cold desert, not target | — |
| 22 Oct | Two types of hard negatives, ~2,000, cap 10 per date | Random negatives; buffer-only random | Instructor's feedback; Steger et al.; Zhu et al. | Some negatives may be unreported slides |
| 23 Oct | Whole years held out in testing | Random rows | Honest skill (Roberts et al. 2017) | Lower scores |
| 23 Oct | Remove 4 data-quality columns | Keep | They encode the year | None measurable |
| 23 Oct | Keep road features, with conditions | Drop them | Real effect + better skill; weather test as guard | Reporting bias enters the model |
| 23 Oct | Random Forest | XGBoost (best AUC), logistic | Passes the weather-only test; fewer false alarms | 0.006 lower AUC |
| 24 Oct | Two provisional levels, Watch 0.35 / Warning 0.45 | One threshold | Graded alerts (as in LHASA) | ~45% of HP slides missed at Watch |
| 1 Nov | Live model without CHIRPS and ERA5-Land | IMERG in CHIRPS slots; old ERA5 values | Data must exist on the morning of the run | AUC 0.801 → 0.775; more false alarms |
| 29 Oct–1 Nov | Whole HP; remote cells marked lower confidence | Road corridors only; extra remote negatives | Original goal; remote negatives would teach "remote = safe" | Remote skill unproven |
| 5 Nov | Road-neutral scoring for alerts and main map; real-road layer kept | Real roads only | Catches more slides at the same false-alarm rate | Wider storm-day warnings |
| 5 Nov | No tuning for scores; report the strict number | Tune and report the best | Honesty; understand behaviour | Less impressive headline numbers |

---

## 16. Mistakes we found and corrected

| # | Mistake | How we found it | Correction |
|---|---|---|---|
| 1 | District names ("Kulu" vs "Kullu"; "Jammu And Kashmir" vs "Jammu & Kashmir (UT)") | Empty or wrong results | Always match exact source strings |
| 2 | First slide deck too close in structure to another team's | Self-review | Rebuilt from scratch |
| 3 | Date coverage inflated (any text counted as a date) | Re-audit | Day-level parser |
| 4 | Prototype event dates partly wrong | October audit | Positives v5 |
| 5 | "23.6% vs 11.7%" trigger claim | Rechecked with corrected dates | Dropped |
| 6 | Two coordinate typos, a parser year error, 5 duplicates | Point-in-state check, parse audit, distance search | Fixed or dropped (§9.3) |
| 7 | GEE kernel orientation (curvature signs wrong) | Artificial-surface tests | Kernels corrected |
| 8 | First artificial test used pixel indices, not metres | Implausible results | Test rebuilt |
| 9 | Old terrain script: wrong curvature, TWI could be −∞ | Code review | Rewritten; old script archived |
| 10 | 30 km road search left gaps | Null counts | 80 km |
| 11 | Glacier placeholder snow value (10,000 mm) | Range check | Masked; flag added |
| 12 | Polygon edge vs pixel centre (one point) | Stack-vs-table comparison | Exact point-in-polygon lookups |
| 13 | Three empty fault zips (22 bytes) | File sizes | Rebuilt before upload |
| 14 | Asset exports without geometry failed | GEE task list | Re-run with geometry |
| 15 | Provisional-IMERG count first written as 18 | Re-count | Corrected to 8 |
| 16 | Terrain "medians" were actually means | Recomputed | Elevation median 1,236 m (mean 1,390) |
| 17 | Road-corridor limit narrowed the whole-HP goal without being flagged | Team review, 29 Oct | Reversed |
| 18 | Feature counts and importance ranks misreported in drafts (7 vs 6 CHIRPS features; two ranks) | Checked against result files | Corrected before use |
| 19 | 255 border cells dropped from the storm map by an inner join | Count check (54,998 vs 55,253) | Outer join; rerun |
| 20 | Model variant chosen on the same folds used for scoring | Self-review | Reported as slightly optimistic |

Mistakes are listed on purpose: each one was caught by a check we built in, and correcting them changed results for the better.

---

## 17. Not done, and why

| Item | Why not (yet) |
|---|---|
| Research questions 2 and 3 of Assignment 1 (new vs reactivated slides; land-use change) | Inventory activity fields and land-cover change data not ready (only two WorldCover years exist) |
| Small road-slide detection from satellite images | Instructor feedback and our own Sentinel-2 test: 10 m pixels too coarse for narrow roads. Restarted on 26 Oct as an optional study (brief written; research not started yet) |
| NISAR radar | Not in GEE; little history |
| CoRE Stack integration | Not landslide-specific |
| IMD gridded rainfall | Not in GEE; needs registration and manual download. Not a timing improvement: its grid is 0.25° (~25 km), coarser than IMERG (0.1°); earlier described here as a candidate for better timing, which was wrong (see experiments log 7.15). Finer free products tested instead (experiments log 6.20–6.21: none better than IMERG) |
| Lithology in the AHP model; merging the AHP and prediction pipelines | Not done; flagged |
| Reconciling HP inventory counts (16,097 in one GSI export vs 6,607 in the PDF) | Different exports **[to confirm]** |
| Forecast-rain training | Training must use observed rain only; forecast used only live |
| Running the JavaScript versions in the Code Editor | Syntax-checked; every number comes from the Python versions, which use the same logic |
| Daily automation, email, map app | Phase D, in progress |
| Storm replays and final alert levels | Phase E |
| Impact assessment | Required for the final report (25 Nov) |

---

## 18. All data sources

| Data | Provider | Resolution / scale | Used for |
|---|---|---|---|
| Bhusanket landslide inventory | Geological Survey of India (904-page PDF) | Points | Landslide events (728) |
| Global Landslide Catalog | NASA (WPRDC mirror) | Points (accuracy varies) | Landslide events (253) |
| Mendeley HP dataset; NRSC atlas; IndLands; HPSDMA | Various | — | Evaluated, not used |
| Copernicus GLO-30 DEM (2024 release) | ESA / Copernicus | 30 m | Terrain |
| MERIT Hydro | Yamazaki et al. 2019 | ~90 m | Streams, HAND, TWI |
| OpenStreetMap roads | OSM via HOT Export Tool | Lines | Road distances |
| OpenStreetMap streams | OSM via Overpass API | Lines | Stream-threshold calibration |
| Lithology, faults, geomorphology | GSI NGDR (Bhu-Chayan) | 1:50k / 1:250k | Geology features |
| ESA WorldCover 2021 | ESA | 10 m | Land cover |
| Landsat 5/7/8/9 Collection 2 | USGS | 30 m | Pre-event NDVI |
| GPM IMERG V07 | NASA | Half-hourly, ~11 km | Main rainfall (training and live) |
| CHIRPS daily | UCSB Climate Hazards Center | Daily, ~5.5 km | Second rainfall source |
| ERA5-Land daily | ECMWF | Daily, ~11 km | Soil moisture, snow |
| GFS forecast | NOAA | 0.25°, 6-hourly | Live run only (most recent days) |
| Sentinel-1 / Sentinel-2 | ESA / Copernicus | 10 m | Early tests; AHP validation masks |
| geoBoundaries v6 | geoLab | ADM1 / ADM2 | State and district boundaries |
| Survey of India sheet grid | Survey of India | Sheets | Fixing coordinate typos |

All free; no paid services.

---

## 19. Tools and working method

- **Google Earth Engine:** Python API for all computing (on Google's servers), plus a Code Editor repository with every script (module and run pairs, standard headers, an index, `Current/` and `Archive/`).
- **Python** (pandas, scikit-learn, XGBoost, matplotlib, pdfplumber) in an isolated project environment.
- **Version control:** Git for the GEE script repository (71 commits).
- **Work log:** `CHANGELOG.md` with evidence and an undo route for every change; backups before every edit.
- **Experiment log:** every approach, including dropped and wrong ones, with its result and status.
- **Rules followed throughout:**
  - expected results stated before running;
  - checks against independent data (Survey of India sheets, OSM streams, town elevations, artificial surfaces);
  - nothing deleted without confirmation;
  - free tools only.

---

## 20. What exists now: assets, code and files

**GEE assets (53 on 5 Nov, under `users/rajsuraj777/`):**
- landslide sets: `positives_v5`, `positives_v4_corrected`, plus the prototype's;
- 15 uploaded layers: roads, lithology, faults and geomorphology for each state;
- negatives' features: `negB_type1_a–c`, `negB_type2_a–c`;
- the HP grid: `hp_grid_static_v1_a–h`;
- storm-day and quiet-day features: `storm_20230814_*`, `storm_20230912_v2_*`.

**Code:**
- 35 Python scripts (~3,000 lines): feature modules, inventory audit and cleaning, negatives, 13 model and analysis scripts, grid and storm-map scripts.
- 21 current + 17 archived GEE Code Editor scripts.

**Data files:**
- `positives_features_v1.csv` (981 × 42);
- `training_table_v1.csv` (3,136 × 51);
- per-step feature tables, the lithology mapping table (516 rows), the cleaning log;
- all model test outputs (`data/phaseC/`, 25 files);
- storm-map outputs (`data/phaseD/`).

**Models:** `rf_roads_v1` (38 features) and `rf_roads_live_v1` (28 features), each with a metadata file.

**Documents:**
- technical documentation (19 sections);
- project history, experiments log, targets and status;
- model card;
- design notes for Phases B and D;
- the work log;
- *Negative Points Generation Notes* (PDF).

**Figures:** model comparison, partial dependence (4 + panel), storm maps (6), ROC/PR, importance and thresholds.

---

## 21. Limitations

1. **Reporting bias:**
   - The inventory mostly records slides that hit roads (median 22 m from a road).
   - Skill is measured almost only near roads.
   - Road-neutral scoring corrects the map, but its remote performance rests on 70 slides (9 in HP), and remote false alarms can't be measured.
2. **Unrecorded slides among the negatives** (label noise).
3. **Small HP sample:** 195 slides. HP numbers can move by several percentage points.
4. **Event clustering:** 242 of 981 events on one day (16 Jun 2013).
5. **Timing is capped by the rain data.** IMERG pixels are about 10 km; cloudbursts can be smaller. Rain alone currently times slides as well as our models do.
6. **The live model is weaker** than the full model, because CHIRPS and ERA5-Land arrive too late.
7. **Forecast rain adds errors;** not yet measured.
8. **Many slides are missed:** about 45% at Watch, about two-thirds at Warning. Published nowcasts report similar ranges (LHASA evaluations detected 8–60% of catalogued slides; Kirschbaum & Stanley 2018).
9. **Over-warning on big storm days** under the provisional district rule (§14.6).
10. **Sampling artefacts** (30-day rain flat, slope spike near 10°), traced to the negative design.
11. **Scores are relative,** not true daily probabilities.
12. **Data limits:**
    - land cover is a single 2021 snapshot;
    - geomorphology is coarse (1:250k);
    - 204 mixed rock descriptions;
    - OSM roads are less complete in HP than in Uttarakhand;
    - HAND is experimental;
    - NDVI is not harmonised across sensors;
    - the DEM has artefacts on steep, shadowed slopes.
13. **The NASA catalogue mirror ends in mid-2018** and comes mostly from English-language news.

---

## 22. Where we stand against the original goal

| Original goal | Status | Verdict |
|---|---|---|
| Whole of HP | All 55,253 cells scored; remote cells marked lower confidence. Briefly narrowed to road corridors (23–29 Oct), then reversed | On track |
| As accurate as possible | Best model AUC 0.80; the live model 0.775–0.813 depending on design. Strict testing used throughout. The ceiling is set by the data (road-biased, incomplete inventory; coarse satellite rain; late CHIRPS), not by the method: three model types land within 0.03 of each other | Honest, moderate; limits measured and explained |
| Daily, automatic, emailed to authorities | Designed; grid computed; first storm map made; automation not built yet | A few days behind our own plan; within the 25 Nov deadline |
| Free tools only | Yes | Achieved |

---

## 23. What remains until 25 November

1. **Interim presentation (6 Nov):** problem, methodology, implementation and results, based on §9–§14.
2. **Storm replays (Phase E):** done 7–9 Nov (§14.10); final rule adopted.
3. **Daily automation (Phase D):** GitHub Actions run, email alerts, GEE map app (whole-HP road-neutral layer plus a real-road layer), running for at least a week before 25 Nov. Team steps: GitHub repository, Earth Engine service account, Gmail app password, recipient list.
4. **Possible improvements:** the two-part model as the live design; revisit the slope rule of the storm-day negatives; rain product test done (6 Nov): GSMaP ties IMERG and the finer PDIR-Now (~4 km) is worse, so IMERG stays; IMD gridded rain is coarser (0.25°) and is not a timing improvement.
5. **Impact assessment** (required): how warnings would be judged in use (lead time, hits and false alarms per district, actions taken), survey questions for district disaster authorities, the state disaster authority and the road department, a feedback format for each alert, and a pilot plan suitable for a funding proposal.
6. **Final report** written as a paper (methods, results, limitations), plus the impact-assessment section.
7. **Optional:** the road-blockage detection study (free satellite data, starting from scratch; a valid result even if it shows the limits).
8. **Pending small fixes for the report:** verify the titles of McAdoo et al. 2018 and Leibundgut et al. 2016, the journal of Dhiman et al. 2026, the primary source of the 2023 HP figures, and full classification references; state the OSM-completeness limitation.

---

## 24. The work in numbers

| Item | Count |
|---|---|
| PDF pages of the national inventory extracted | 904 |
| Inventory rows cleaned | 36,071 |
| Inventories evaluated | 6 |
| Landslide events after audit | 981 (from 987 in the first combined set) |
| Coordinate, date and duplicate fixes documented | 11 |
| Features per event | 42, in 9 groups |
| Free-text rock descriptions mapped by rule | 516 |
| Data layers prepared and uploaded (roads, lithology, faults, landforms for 3–4 regions) | 15 |
| Independent checks of the stream threshold (test areas × thresholds) | 4 × 6 |
| No-landslide examples designed and built | 2,167 |
| Model types compared | 3, each under 3 testing schemes |
| Experiments recorded (kept, dropped, changed, wrong) | 50+ |
| Own mistakes found and corrected | 20 |
| HP grid cells with computed features | 55,253 |
| GEE assets | 50+ |
| Python scripts / lines | 35 / ~3,000 |
| GEE Code Editor scripts | 38 (21 current, 17 archived) |
| Commits in the GEE script repository | 71 |
| Verified references | 25+ |
| Course deliverables so far | Presentations 1 and 2, Assignments 1 and 2, research-paper presentation |

---

## 25. Who did what

**[To be confirmed by both team members before sharing]**

| Area | Main contributor |
|---|---|
| Problem framing, literature review, Presentations 1 and 2, Assignments 1 and 2 | Suraj and Siddhesh |
| AHP susceptibility model and Sentinel-2 change-detection validation (10 sites) | Siddhesh |
| Finding that ~90% of Bhusanket HP dates are month-year only; monthly-anomaly idea | Siddhesh |
| Presentation 2 model results (LR 0.789, RF 0.895) | Siddhesh |
| Bhusanket extraction, date audits, inventory evaluation, state selection, CHIRPS extraction | Suraj |
| October data rebuild: positives audit, 42-feature stack, data uploads, documentation | Suraj |
| Hard negatives, model comparison and testing, live model, road-neutral scoring, grid, storm maps | Suraj |
| Satellite change-detection "confirmation" layer | Proposed; no work after September (as of 5 Nov) |
| Research-paper presentation (26 Oct) | Suraj and Siddhesh (given in class) |
| Road-blockage detection study | Brief written 26 Oct; research not started |

---

## 26. References

**Verified (authors, year, journal and volume/pages or DOI checked):**
- Breiman, L. (2001). Random forests. *Machine Learning* 45, 5–32.
- Brenning, A. (2005). Spatial prediction models for landslide hazards. *NHESS* 5, 853–862.
- Chen, T., Guestrin, C. (2016). XGBoost: a scalable tree boosting system. *Proc. KDD*, 785–794.
- Froude, M., Petley, D. (2018). Global fatal landslide occurrence from 2004 to 2016. *NHESS* 18, 2161–2181.
- Juang, C.S., Stanley, T.A., Kirschbaum, D.B. (2019). Using citizen science to expand the global map of landslides: introducing COOLR. *PLOS ONE* 14(7), e0218657.
- Kirschbaum, D.B., Stanley, T., Zhou, Y. (2015). Spatial and temporal analysis of a global landslide catalog. *Geomorphology* 249, 4–15.
- Kirschbaum, D., Stanley, T. (2018). Satellite-based assessment of rainfall-triggered landslide hazard for situational awareness. *Earth's Future* 6, 505–523.
- Meena, S.R., Mishra, B.K., Blaschke, T. (2019). Landslide susceptibility mapping of the Kullu Valley, Himachal Himalayas. *Geosciences* 9(4), 156.
- Reichenbach, P. et al. (2018). A review of statistically-based landslide susceptibility models. *Earth-Science Reviews* 180, 60–91.
- Roberts, D.R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40(8), 913–929.
- Singh, M., Khajuria, V., Singh, S., Singh, K. (2024). Landslide susceptibility evaluation in the Beas River Basin … AHP. *Quaternary Science Advances* 14, 100180.
- Stanley, T., Kirschbaum, D. (2017). A heuristic approach to global landslide susceptibility mapping. *Natural Hazards* 87, 145–164.
- Stanley, T. et al. (2021). Data-driven landslide nowcasting at the global scale. *Frontiers in Earth Science* 9, 640043.
- Steger, S., Brenning, A., Bell, R., Glade, T. (2017). The influence of systematically incomplete shallow landslide inventories on statistical susceptibility models and suggestions for improvements. *Landslides* 14, 1767–1781.
- Steger, S., Brenning, A., Bell, R., Glade, T. (2018). Incompleteness matters: an approach to counteract inventory-based biases in statistical landslide susceptibility modelling. EGU General Assembly, EGU2018-8551.
- Steger, S., Mair, V., Kofler, C., Pittore, M., Zebisch, M., Schneiderbauer, S. (2021). Correlation does not imply geomorphic causation in data-driven landslide susceptibility modelling. *Science of the Total Environment* 776, 145935.
- Steger, S. et al. (2024). Adopting the margin of stability for space–time landslide prediction. *Geoscience Frontiers* 15(3), 101822.
- Zhu et al. (2024). Considering the effect of non-landslide sample selection on landslide susceptibility assessment. *Geomatics, Natural Hazards and Risk* 15(1). doi:10.1080/19475705.2024.2392778
- Data papers: Yamazaki et al. 2019 (MERIT Hydro); Hartmann & Moosdorf 2012 (GLiM); Funk et al. 2015 (CHIRPS); Muñoz-Sabater et al. 2021 (ERA5-Land); Huffman et al. (IMERG V07); Zanaga et al. 2022 (WorldCover); Nobre et al. 2011 (HAND).
- Method papers: Montgomery & Dietrich 1988; Montgomery & Foufoula-Georgiou 1993; Zevenbergen & Thorne 1987.
- IMD rainfall categories (heavy rain 64.5–115.5 mm per day): IMD national bulletins.

**To verify before the final report:**
- Dhiman, Prakash & Banshtu 2026 (journal name);
- McAdoo et al. 2018 and Leibundgut et al. 2016 (exact titles);
- Saaty (AHP) and Varnes / Cruden & Varnes / Hungr et al. (landslide classification), full entries;
- the 2023 HP disaster figures (primary source).

---

*Detailed companion files in the project folder:*
- *`docs/ICTD_Landslide_Feature_Stack_Documentation.md` (technical detail)*
- *`docs/experiments_log.md` (every experiment)*
- *`docs/project_history.md` (timeline)*
- *`CHANGELOG.md` (every change with evidence)*
- *`docs/model_card.md`*
- *`docs/phaseB_design_note.md`, `docs/phaseD_design_note.md`*
