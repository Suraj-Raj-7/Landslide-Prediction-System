# Experiments log: everything tried, kept, dropped, and why

**Project:** Landslide early-warning system for Himachal Pradesh · **Team:** Suraj Raj, Siddhesh Pohare (M.Tech ICTD, IIT Delhi) · **Started:** August 2026 · **Last updated:** 5 Nov 2026

This log lists every approach the project tried, from the first proposal onward, with its result and what happened to it: **kept**, **dropped**, **changed**, or **found wrong**. Failed and abandoned work is included on purpose: it explains why the current method looks the way it does. Items marked **[to confirm]** come from incomplete records and still need checking.

Status key: ✅ kept · ❌ dropped · 🔄 changed / replaced · ⚠️ found wrong and corrected · ⏸ deferred

---

## 1. Problem framing (Aug 2026)

| # | Tried | Result | Status | Why |
|---|---|---|---|---|
| 1.1 | Three directions proposed to the course instructor: (a) landslide prediction, (b) post-landslide impact data (road blockage), (c) a chatbot platform for government-scheme awareness | Instructor rejected (c): it only redirects people to websites without making anything simpler | ❌ (c) | Feedback: a feature must act on the user's behalf, not explain and redirect |
| 1.2 | Warning delivery to the public | Instructor: sending data to a government authority is enough; public alerting is the authority's job | 🔄 | Project reframed as decision support for authorities |
| 1.3 | A new AHP (Analytic Hierarchy Process) susceptibility map as the core contribution | Instructor feedback on Assignment 1: AHP risk maps are "abundantly available" | 🔄 AHP demoted to a baseline | Literature review agreed: Singh et al. 2024 (Beas basin, AUC 0.863), Meena et al. 2019 (Kullu, AUC 0.79–0.91) |
| 1.4 | Post-event detection of small road-blocking slides from open satellite imagery (Sentinel-2 + image processing) | Instructor: too small to see in open satellite data; a quick Sentinel-2 test confirmed that 10 m pixels are too coarse for narrow mountain roads | ❌ scoped out (an optional road-detection study was briefed on 26 Oct; research not started as of 5 Nov) | Resolution limit of free data |
| 1.5 | Sentinel-2 (optical) as the main post-event source | Monsoon cloud blocks optical imagery; Sentinel-1 radar sees through cloud | 🔄 Sentinel-1 primary, Sentinel-2 secondary (design only) | Physical limit of optical sensors in monsoon |
| 1.6 | Research questions 2 and 3 of Assignment 1 (new vs. reactivated slides from Bhusanket activity fields; terrain–land-use-change–rain combinations) | Not started: inventory dates and movement-type fields needed cleaning first, and only two WorldCover years (2020, 2021) exist for land-cover change | ⏸ | Data not ready; rainfall-triggered prediction (question 1) became the main thread |
| 1.7 | Forecast-rainfall experiments | Deferred in Assignment 1 (no reproducible forecast archive); later used only in the live design (GFS fills the last days), never for training | 🔄 | Training must use observed rain only |

## 2. Landslide inventory (Sep–Oct 2026)

| # | Tried | Result | Status | Why |
|---|---|---|---|---|
| 2.1 | Extract GSI Bhusanket's national inventory (published only as a 904-page PDF) with `pdfplumber` | 36,976 raw rows → 36,071 clean rows (HP 6,607), matching GSI's stated 36,072 | ✅ | First table-cleaning filter missed a title row; fixed by keeping only rows with a numeric serial number |
| 2.2 | First date audit: "any text in the History field" | HP 687 (10.4%), India 13,674 (37.9%) | ⚠️ wrong | It counted any text, not real dates. A pandas missing-value bug first gave 100% |
| 2.3 | Corrected audit: parseable day-level dates only | HP **114 (1.7%)**, India 5,313 (14.7%) | ✅ | Most HP records have month-year dates only |
| 2.4 | Mendeley "geo-environmental HP dataset" (6,503 points, 40 predictors) | Its README says it is for static susceptibility only; the main file had no coordinates; only 9 day-dated records, all duplicates of Bhusanket rows | ❌ for event modelling | Adds no new dated events |
| 2.5 | NASA Global Landslide Catalog (COOLR) via the WPRDC mirror | 175 HP records, 100% dated; location accuracy varies (exact to 50 km) | ✅ (good-accuracy, rain-triggered records) | Best date quality; filtered by location accuracy |
| 2.6 | Other sources: NRSC/ISRO Landslide Atlas, IndLands (HuggingFace), HPSDMA repository | Atlas: PDFs and map layers only; IndLands: unclear provenance, no event dates; HPSDMA: blocks automated access | ❌ | No usable dated records |
| 2.7 | Pool other states, chosen by method, not by eye: (1) same Himalayan thrust system (MCT/MBT) as HP; (2) similarity of the share of rain-triggered slides | Uttarakhand and J&K selected (largest combined usable samples as well) | ✅ | HP alone has too few dated slides |
| 2.8 | Combined positives v2 (Sep): 987 → 930 (unparseable dates) → 886 (8 impossible dates, e.g. 2028-03-29, removed) | 886 events | 🔄 replaced by v4/v5 | Later audit found date and coordinate errors |
| 2.9 | Positives audit and cleaning (Oct): v4 (986) → **v5 (981)** | 2 coordinates fixed against Survey of India sheets; 1 wrong year fixed and 1 missing event added; 1 undatable event and 5 duplicates removed; IDs cleaned (GEE upload had rewritten commas) | ✅ | Details in `data/step0_changes_log.csv` and documentation §4 |
| 2.10 | Ladakh points (12) | Kept in the inventory, excluded from training | 🔄 | Outside the monsoon belt that justified pooling |
| 2.11 | Boundaries: FAO GAUL 2015 | Deprecated, and it stores J&K as one disputed unit | 🔄 replaced by geoBoundaries v6 | Correct, current boundaries |

## 3. Features (Sep–Oct 2026)

| # | Tried | Result | Status | Why |
|---|---|---|---|---|
| 3.1 | Sep prototype features: slope + CHIRPS rain (3/7/15/30 days) | Used in the first models (§4) | 🔄 replaced | Too few factors; dates later found wrong in part |
| 3.2 | "Trigger-consistency" check (Sep): share of events with almost no rain, Bhusanket 23.6% vs NASA 11.7% | Presented as evidence the rain extraction works | ⚠️ wrong | Based on the wrong prototype dates; with corrected dates it reverses (Bhusanket 2.9%, NASA 11.9%). Claim dropped |
| 3.3 | Full feature stack (Oct): 42 features in 9 groups (terrain, drainage, roads, lithology, faults, geomorphology, land cover, NDVI, rain/soil/snow, 2 data flags) | 981 × 42, one intentional empty cell | ✅ | Documentation §5–12 |
| 3.4 | Curvature kernels in GEE | GEE's fixed kernels put row 0 at the south; first curvature signs were wrong | ⚠️ corrected | Tested on synthetic planes, bowls, ridges |
| 3.5 | HydroSHEDS free-flowing rivers (~500 m) for stream distance | Misses small mountain streams | 🔄 replaced by MERIT Hydro, calibrated against OSM streams | Resolution |
| 3.6 | Road search radius 30 km | One gap in remote areas | 🔄 80 km | Remote points need a larger radius |
| 3.7 | Lithology free text (516 descriptions) | Mapped to GLiM classes with an explicit table | ✅ | `lithology_mapping_v1.csv` |
| 3.8 | Painted 30 m rasters for polygon layers at points | Edge effects at polygon borders | 🔄 exact point-in-polygon lookups | Accuracy at points |

## 4. Negative examples (Sep and Oct 2026)

| # | Tried | Result | Status | Why |
|---|---|---|---|---|
| 4.1 | Random negatives across HP + UK + J&K (Sep prototype; 1,500 random points, ≥ 2 km from any slide, 878 kept, dates copied from slides ± 30 days). Median elevation 3,868 m vs 1,228 m for slides; 408 of 878 above 4,000 m; median 4.8 km from a road vs 22 m (see `docs/Negative_Points_Generation_Notes.pdf`) | First models: logistic regression, slope only AUC 0.72 → slope + rain 0.83 (random split); final presented deck LR 0.789, **RF 0.895** (5-fold CV) | ❌ | Instructor: "negative sampling has some serious issue": a slope + rain model gives high recall but many false alarms. Random negatives are too easy |
| 4.2 | **Hard negatives** (Oct): Type 1 same place, safe day (969); Type 2 similar slope near roads, storm day (1,198); per-storm cap 10 | Training table 3,136 rows | ✅ | Steger et al. 2024; Zhu et al. 2024 (buffer-based selection) |
| 4.3 | Full 30 m stratified sampling over whole states for Type 2 | GEE timed out | 🔄 random points in each state's bounding box, checked at their 30 m cell | Compute limit; same rules |
| 4.4 | Type 2 restricted to slopes ≥ 10.9° (10th percentile of positives) | Later found to create an artefact: the few slides on gentler slopes have no counter-examples, so low slopes look risky (partial dependence, §6.8) | ⚠️ to revisit | Sampling rule |
| 4.5 | Type 2 on the same storm days | Later found: these are as wet as the slides, so a single model gives rain too little weight (§6.11) | ⚠️ to revisit | Sampling design |
| 4.6 | Regenerating the negatives (v2) | Possible for the final version if the sampling artefacts (§4.4, §4.5) need fixing for better training | ⏸ open | Decision after the interim review |

## 5. Earlier AHP and change-detection work (Siddhesh, Aug–Sep 2026)

| # | Tried | Result | Status | Why |
|---|---|---|---|---|
| 5.1 | AHP model, 6 factors (slope 36.4%, NDVI 23.2%, aspect 13.6%, NDWI 13.6%, BSI 8.0%, NBR 5.1%), consistency ratio 0.0124 | Static susceptibility maps for 10 HP sites | ✅ as baseline | Valid weights (CR < 0.10) |
| 5.2 | Validation against Sentinel-2 pre/post change masks (dNDVI, dBSI, slope thresholds) | Global AUC 0.624; Mandi 0.835, Shimla 0.833; Lahaul–Spiti 0.337 (worse than random) | ✅ reported | Masks are spectral change, not field-verified |
| 5.3 | Mask fixes v2 (NDVI-only mask in Lahaul; seasonal offset correction) | Global AUC 0.626 (no real change); the offset fix was shown to be mathematically a no-op | ❌ | Real fixes need new data (same-season image pairs, permafrost/lithology factors) |
| 5.4 | Monthly rainfall anomaly (because ~90% of Bhusanket HP dates are month-year only) | Planned | ⏸ superseded | The day-dated subset (Bhusanket + NASA) was used instead |
| 5.5 | Satellite change detection as a "confirmation" layer for the warning system | Proposed; no further work after September (as of 5 Nov) | ⏸ | |

## 6. Models and evaluation (Oct–Nov 2026)

| # | Tried | Result | Status | Why |
|---|---|---|---|---|
| 6.1 | Three models, 5-fold CV holding out whole years: logistic regression, Random Forest, XGBoost | ROC AUC 0.780 / 0.801 / 0.807 | ✅ method | Roberts et al. 2017: hold out blocks, not random rows |
| 6.2 | Data-quality columns as features (`ndvi_pre_n`, IMERG completeness flags) | `ndvi_pre_n` rises from 18 to 41 images over the years, so it encodes the year | ❌ removed | They describe the satellite record, not the ground |
| 6.3 | Road features | Strongest feature; partly physics (road cuts), partly reporting bias | ✅ kept, with conditions | Decision 23 Oct |
| 6.4 | XGBoost (best overall) | Clearly worse on the weather-only test (−0.03 AUC, interval below 0) | ❌ | It leans on roads instead of rain |
| 6.5 | Random Forest with roads | 0.801; passes the weather-only test | ✅ chosen | |
| 6.6 | Map limited to 500 m road corridors | Shrank coverage to one-third of HP, against the whole-HP goal | ❌ reversed (1 Nov) | Replaced by whole HP + lower-confidence mark |
| 6.7 | Alert levels Watch 0.35 / Warning 0.45 | HP: 55% / 33% of slides caught; 16% / 5% of safe days flagged | ✅ provisional | To be set in storm replays |
| 6.8 | 38-feature model in a daily system | CHIRPS is ~24 days late and ERA5-Land ~12 days late in GEE | 🔄 live model on IMERG + fixed features (28): AUC 0.775 | Data latency; 38-feature model kept as reference |
| 6.9 | Road-neutral scoring (roads set to the positives' median at prediction) | Catches more slides at the same safe-day false alarms (live: 37% → 49%), but flags many more slopes on storm days (3% → 18%) | ✅ adopted for whole-HP map and district alerts (5 Nov) | Bias correction idea from Steger et al. 2017, 2021; remote check rests on 70 slides (9 in HP) |
| 6.10 | Heavy-rain rule baseline (IMD: ≥ 64.5 mm/day) | Rain alone times slides better than the models (HP 0.805 vs 0.705); the models tell "where" better (0.763 vs 0.675) | ✅ reported | Honest baseline comparison |
| 6.11 | Timing diagnostic: model trained on positives vs safe days only | Timing gap mostly explained by the storm-day negatives | ✅ reported | §4.5 |
| 6.12 | Partial dependence | Rain on the day and 7-day rain: physical. 30-day rain flat and slope spike at 10°: sampling artefacts | ✅ reported | §4.4, §4.5 |
| 6.13 | Two-part model (where × when) | Live overall AUC 0.775 → 0.813 (HP 0.763 → 0.777); fewer false alarms on other slopes (14% → 7%); timing still capped at rain-alone level | ✅ candidate | LHASA structure (Kirschbaum & Stanley 2018) |
| 6.14 | "When" part as Random Forest vs logistic regression on log rain | 0.793 vs 0.813 | ⚠️ note | Both variants were compared on the same test folds, so the chosen variant's score is slightly optimistic |
| 6.15 | Strict vs easy testing on the same models | Live model: years held out 0.775, storm days held out 0.792, random rows 0.856 (timing 0.683 → 0.802) | ✅ reported | Explains why the Sep result (0.895, random negatives, random CV) was too high |
| 6.16 | Whole-HP storm map, 14 Aug 2023, model trained without 2023 | All 31 recorded slides in alert cells, but 67% of HP at Watch+ and all districts at Warning under the 5% rule | ✅ reported; district rule ❌ too loose | One day is an illustration |
| 6.18 | RQ1 (does rain add to terrain?), first run: terrain-only model on all rows | AUC 0.419, timing 0.060: **below coin toss** | ⚠️ not a fair test | Each landslide's same-place twin (identical terrain, opposite label) sits in training when it is tested, so a terrain-only model learns "this spot = the opposite label". A property of the paired design, not of terrain |
| 6.19 | RQ1, fair test: landslides vs other slopes on storm days, trained without the twins | Terrain only 0.912 (HP 0.858); + vegetation 0.918; + IMERG rain 0.926 (HP 0.870); + all rain/soil/snow 0.928 (HP 0.877). Timing can only come from rain (rain alone, HP: 0.805) | ✅ reported | Answer to RQ1: rain is what makes daily timing possible and adds a little to "where"; terrain score includes road distance (reporting bias) |
| 6.17 | Quiet-day map, 12 Sep 2023 (no recorded slides nearby), same model and levels | HP at Watch+ 0.4%, Warning 0.0%, 0 of 12 districts alerted (storm day: 66.8%, 47.2%, 12 of 12) | ✅ reported | Separates disaster day from quiet day; but the quiet day was nearly dry (0.8 mm), so wet days without slides still need testing (Phase E) |
| 6.20 | Other rain product: GSMaP v8 gauge-corrected (0.1°, GEE), rain on the day only, timing test | IST day 0.816 vs IMERG 0.824 (diff −0.009, 95% year-block interval −0.040 to +0.022); UTC day 0.822 vs 0.819; HP 0.801 vs 0.807 | ❌ not better (tie) | Rule stated before the run: higher AUC and interval above 0. Same 10 km scale as IMERG |
| 6.21 | Finer rain product: PDIR-Now (0.04°, ~4 km, infrared-based, open download), rain on the UTC day, timing test | 0.761 vs IMERG 0.819 on the same UTC day (diff −0.058, interval −0.105 to −0.032); HP 0.680 vs 0.790 (−0.109, −0.158 to −0.033) | ❌ worse | Finer grid does not help: infrared-only estimates miss rain forced up by mountains. IMERG stays the live product; INSAT-3DR (also infrared, ~4 km) not pursued |

## 7. Mistakes found and corrected (by us, during the work)

| # | Mistake | How found | Correction |
|---|---|---|---|
| 7.1 | District name typo "Kulu" vs "Kullu" in GEE; "Jammu And Kashmir" vs "Jammu & Kashmir (Ut)" in the inventory | Empty or wrong results | Always match exact source strings |
| 7.2 | First slide deck too close in structure and look to another team's deck | Self-review | Rebuilt from scratch |
| 7.3 | Date coverage inflated (any text counted as a date) | Re-audit | Day-level parser (§2.3) |
| 7.4 | Prototype event dates partly wrong | Positives audit (Oct) | Positives v5 |
| 7.5 | "23.6% vs 11.7%" trigger-consistency claim | Rechecked with corrected dates | Dropped |
| 7.6 | Terrain "medians" reported were means | Recomputed | Documentation fixed (22 Oct) |
| 7.7 | Curvature kernel orientation | Synthetic-surface tests | Kernels corrected |
| 7.8 | Road corridor limit narrowed the whole-HP goal without being flagged | Team review (29 Oct) | Reversed |
| 7.9 | Feature counts and importance ranks misreported in drafts (7 vs 6 CHIRPS features; two rank errors) | Checked against result files | Corrected before use |
| 7.10 | 255 border cells dropped from the storm map by an inner join | Count check (54,998 vs 55,253) | Outer join; rerun |
| 7.11 | Model variant selected on the same folds used for scoring (§6.14) | Self-review | Reported as slightly optimistic |
| 7.13 | Presentation 2 described the 878 background points as "sampled inside the HP boundary with a 500 m exclusion buffer" | Mapping the actual file (`data/legacy/negatives_features_v3.csv`) on 5 Nov | The points are spread over HP, Uttarakhand and J&K and beyond (up to 36.9° N); stated in the Assignment 3 deck |
| 7.14 | First RQ1 terrain-only comparison run on all rows (unfair, see 6.18) | Result below 0.5 | Rerun on landslides vs storm-day slopes only |
| 7.15 | IMD gridded rainfall described as denser rain data and a candidate for better timing (§8, targets, project history) | Checked IMD's product specification on 6 Nov: 0.25° grid | Wording corrected; finer free products (PDIR-Now 0.04°) tested instead |
| 7.12 | 255 border cells counted as a 13th "district" ("unassigned") in the district tables | A quiet-day district alert that was not a real district | District levels for the 12 real districts only |

## 8. Not done, and why

| Item | Why not (yet) |
|---|---|
| Research questions 2 and 3 of Assignment 1 | Inventory movement/activity fields and land-cover-change data not ready |
| NISAR radar data | Not in GEE's catalog (only on NASA ASF); limited history |
| CoRE Stack integration | Not landslide-specific; researched only |
| IMD gridded rainfall | Not in GEE; registration and manual download. Grid 0.25°, coarser than IMERG, so not a timing improvement (corrected, see 7.15) |
| Lithology in Siddhesh's AHP model / merging the two pipelines | Not done; flagged |
| Reconciling HP inventory counts (16,097 vs 6,607) | Different exports of GSI data **[to confirm]** |
| Daily automation, email alerts, GEE App | Phase D, in progress |
| Storm replays and final alert levels | Phase E |
| Impact-assessment design | Required for the final report (25 Nov) |
