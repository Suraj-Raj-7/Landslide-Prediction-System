# ICTD Landslide Project: Work Log

Every change made from 22 Oct 2026 onwards: **what** was done, **why**, the **evidence** behind it, and **how to undo it**.
Newest entries at the top. Each decision is backed by a data check or a cited paper; entries say which.

Rules for this log:
- Nothing is deleted or overwritten without a backup first (backups are kept locally, named `<file>_<date>_<reason>`).
- GEE assets are never deleted or overwritten; new versions get a new name (`_v2`, `_v3` …).
- The master copy of the documentation is `docs/ICTD_Landslide_Feature_Stack_Documentation.md`.
- Older entries refer to `outputs/` and `py_runners/`; these are now `data/` and `src/` (see the 22 Oct project setup entry).

---

## 2026-11-13 · Key facts sheet, reference check, demo plan

| | |
|---|---|
| **Key facts** | `docs/key_facts.md`: every final number (data, models, alert rule, replays, storm maps, whole monsoons, live system), each read from its result file on 13 Nov, with the file named. Use it to check slides and the report. |
| **References checked** | McAdoo et al. 2018 and Leibundgut et al. 2016: exact titles, volumes and DOIs confirmed and corrected in the technical documentation and project history. Saaty 1980, Varnes 1978, Cruden & Varnes 1996, Hungr et al. 2014: full entries added. **Not found:** Dhiman, Prakash & Banshtu 2026 (use only with the original PDF or link). **2023 HP figures:** "509 deaths, 7,000+ landslides" (Assignment 1) not traceable to a primary source; official data via Mongabay (Sept 2023): 428 deaths, 2,614 houses and 318 shops fully damaged, more than 11,000 houses partly damaged. Recorded in `docs/project_history.md` and the key facts sheet. |
| **Demo plan** | `docs/demo/demo_plan.md`: 4-minute script, checklist for the day before, a backup for every step, short answers to likely questions. Offline copy of the live page of 13 Nov: `docs/demo/live_page_13nov/` (about 0.5 MB). |
| **Small fix** | The district tables on the live page and in the email said "Rain today" also in the tomorrow table; now "Rain on the day" (`src/live_03_daily_run.py`). |

---

## 2026-11-13 · Daily run: three morning attempts, one email

| | |
|---|---|
| **Problem found** | Every scheduled run since 10 Nov succeeded, but GitHub started them 7–8 hours late: scheduled for 10:00 IST, actually started 18:24, 17:32, 18:36 and 18:00 IST (10–13 Nov, from the GitHub Actions run list). GitHub documents that scheduled runs can be delayed when it is busy. The outlook was correct, only late. |
| **Change** | `.github/workflows/daily.yml` now has three schedules (06:00, 08:00, 10:00 IST) and a first job `check` that runs `src/live_00_already_ran_today.py`: it asks GitHub's API whether this workflow already succeeded today (Indian date) and, if so, the run and publish jobs are skipped. Manual runs always run. If the API cannot be reached the run goes ahead (an extra email is better than a missed day). Permission `actions: read` added for this check. |
| **Tests (on the laptop)** | Against the real run history on 13 Nov: `done=true` (one successful run today). With an unreachable repository: `done=false`. |
| **If it is still late** | Next option: an outside scheduler that presses "Run workflow" at a fixed time (needs a GitHub token); not set up unless needed. |
| **Docs** | `docs/daily_system_setup.md` (timing), `src/README.md`. |

---

## 2026-11-12 · Guides for new visitors; questionnaire formatting

| | |
|---|---|
| **Why** | The repository is read by people with no background on the project. Each main folder now has a short guide in plain words. |
| **Changes** | `README.md` rewritten (story, live link, picture, how it works in five steps, results, honest limits, where to look, how to run, sources, credits); new `docs/README.md` (what to read first, list of all documents, glossary), `src/README.md` (every script grouped in the order the project was built), `data/README.md` (every folder, the key files, and which large files stay on the computer and how to remake them). All links checked. |
| **Big files** | Kept where they are. They are already in the repository history, so moving or removing them now would not make it smaller, and moving would break scripts that expect them in place. New large regenerable files stay out through `.gitignore`. |
| **Formatting fix** | In `docs/impact_assessment.md` the numbered questions in Appendices A–C ran together into one paragraph on GitHub; a blank line after each sub-heading fixes it. |

---

## 2026-11-12 · Impact assessment section (proposed method)

| | |
|---|---|
| **What** | `docs/impact_assessment.md`: the report's impact section, written as the professor asked (31 Oct mail): a *proposed* impact-assessment method with survey questions and formats, usable by any partner as a one-monsoon pilot plan. No budget (Suraj, 12 Nov). Not tied to any organisation continuing the work. |
| **Contents** | Summary; proof of concept (storm replays, two full-monsoon replays, live system); theory of change (prediction → delivery → trust → action → benefit, with what can break each link); users; fit with the UN *Early Warnings for All* four pillars; position next to official IMD/GSI warnings (decision support for officials, never a replacement); evaluation questions; pilot design (baseline, shadow month, live season, review; before/after and pilot vs neighbouring districts, because withholding safety warnings is not acceptable); 14 indicators; qualitative evidence; success criteria to be fixed before the live season; risks, fairness and ethics (alert fatigue, false sense of safety, conflicting messages, uneven coverage, digital divide, personal data, data dependence, responsibility); glossary. |
| **Appendices** | A: officials' questionnaire; B: road agencies and police; C: residents and travellers (some themes adapted from Suraj's earlier socio-economic landslide survey, reworded around warnings; only question headings were read, not responses); D: per-alert feedback form; E: alert and action log with event stories; F: monthly summary. All with a consent text. |
| **Sources checked** | UN/WMO Early Warnings for All (four pillars); GSI National Landslide Forecasting Centre bulletins (Bhusanket portal); Piciullo et al. 2017 (Landslides 14(3), 995–1008, doi 10.1007/s10346-016-0750-2); Calvello & Piciullo 2016. |

---

## 2026-11-12 · Full-monsoon replays (2023 and 2025)

| | |
|---|---|
| **What** | `src/impact_01_monsoon_replay.py` runs the live system for every day from 15 Jun to 30 Sep (108 days) of a past monsoon, with the model trained without that year. Plain-language write-up: `docs/monsoon_replay_explained.md`. Results in `data/impact/`, pictures `docs/figures/monsoon_2023_calendar.png` and `monsoon_2025_calendar.png`. |
| **Why** | Evidence for the impact section ("proof of concept"): what a district office would have received for a whole season, not only on 32 chosen days. |
| **Results** | 2023: 17 of 22 district-days with a recorded slide were on alert that day or the day before (77%; 12 already the day before); 426 of 1,296 district-days on alert (33%), 402 without a recorded slide that day or the next. 2025: 24 of 35 (69%; 20 the day before); 333 alert district-days (26%), 291 without a recorded slide. |
| **Reading** | Good catch rate with a day's notice, but a high alert load (about 1 monsoon day in 3–4 per district). Many "extra" alerts may be unrecorded slides (the inventory has almost no 2023 events in the lower districts), so they are an upper bound on false alarms. The rule was **not** changed after seeing these results; alert fatigue is named as the main risk for a pilot to measure. |
| **Checks** | Days after the vegetation cut-off only (2023 from 7 Jul, 2025 from 16 Jul): 17 of 21 and 23 of 32 caught, same conclusion. No recorded slide outside the 12 districts. |
| **Bugs fixed during the run** | Summary step used `.level` on a pandas group (reserved name in pandas 3) → crashed after scoring; fixed with `["level"]`, and the script now reuses the saved daily table instead of rescoring. A code restructuring broke indentation; rewritten and rerun. |

---

## 2026-11-09 · Daily system switched on

| | |
|---|---|
| **Set up by Suraj** | Repository https://github.com/Suraj-Raj-7/Landslide-Prediction-System (first commit by Suraj, sole contributor); Earth Engine service account `daily-run` (roles: Earth Engine Resource Writer, Service Usage Consumer; key kept outside the project), tested on the laptop before use; Gmail app password; 4 secrets, `SITE_URL` variable, Pages source = GitHub Actions. |
| **First run (manual, 9 Nov 16:24 UTC)** | Success in 4 min 45 s (run 58 s, publish 3 min 35 s). Email received. Page live at https://suraj-raj-7.github.io/Landslide-Prediction-System/ with history. Result: no district on alert today or tomorrow. |
| **Change after the first run** | Workflow fixed to `ubuntu-24.04` instead of `ubuntu-latest`, because GitHub announced a switch of `ubuntu-latest` to Ubuntu 26; a fixed version avoids a change during the trial week. GitHub's "Node.js 20 is deprecated" notice concerns GitHub's own helper steps and needs no action. |
| **From now** | Runs daily at 10:00 IST. Vegetation grid to be refreshed monthly (`docs/daily_system_setup.md`). |

## 2026-11-09 · Final alert rule adopted; daily system built and tested

| | |
|---|---|
| **Decision (Suraj, 9 Nov)** | Final rule adopted from the replays: live Random Forest, road-neutral; cell Watch ≥ 0.376, Warning ≥ 0.463; district at a level when ≥ 30% of its cells within 500 m of a road reach it. Written into documentation §17.10, model card, targets, project history §14.10 and `models/rf_roads_live_v1_meta.json` (`final_alert_rule`, with the exact levels and the road-neutral distances 22.1 m / 46.0 m). |
| **Monthly grid** | `src/live_01_monthly_grid.py`: fixed features + district + vegetation for all 55,253 cells, as one file `data/live/grid_live.csv.gz` (GEE assets `users/rajsuraj777/live/grid_ndvi_202611_a…h`, NDVI window ending 8 Nov 2026). Monthly because vegetation takes ~40 min and barely changes (6 Nov test). A file, so the daily run needs no access to private GEE assets. |
| **Daily rain** | `src/live_02_rain.py`. Data delays checked 9 Nov 13:30 UTC: IMERG ends 34 h earlier; ERA5-Land a week earlier; GFS runs complete within ~7 h. Rain per IST day = measured IMERG + GFS forecast for the rest (for each missing hour the newest run issued before it). Checks: measured path identical to the training extraction for 55,252 of 55,253 cells (14 Aug 2023); GFS running total confirmed to restart every 6 hours on real data; glacier flag identical in Aug 2023 and Nov 2026 (627 cells), so the latest ERA5-Land day is used. |
| **Daily run** | `src/live_03_daily_run.py`: scores today and tomorrow, district levels, two maps, web page (`site/`), email (Gmail, only when the secrets are set). Test for 9 Nov 2026 (stand-in grid): 31 s, all of today's rain from the forecast, no district on alert (0–3 mm in HP). Test for 14 Aug 2023 (pipeline check only: the live model has seen 2023): 10 districts at Warning, 1 at Watch. |
| **Bugs found in testing** | (1) the rain module was imported before the Earth Engine login; (2) GFS run times were converted as laptop-local time (IST) instead of UTC, so no forecast was found; (3) the run summary listed unused GFS runs; (4) map titles too long. All fixed and retested. |
| **GitHub (not pushed; Suraj commits)** | `.github/workflows/daily.yml` (10:00 IST daily + run button; publishes the page with GitHub Pages and keeps each run 90 days; makes no commits), `requirements-live.txt` (same versions as the trained model), `.gitignore` extended (separate GEE repo, regenerable large files, run output). Setup guide in plain words: `docs/daily_system_setup.md`. README status updated. |
| **Real run, 9 Nov 2026** | With the real grid file (55,253 cells, 8.8 MB, NDVI window ending 8 Nov): IMERG to 8 Nov 04:00 UTC; 62.5 forecast hours from 6 GFS runs; today's rain entirely forecast; no district on alert (dry November). A syntax error from editing the map title was found on this run and fixed. |
| **Cells without vegetation** | 2,633 cells (4.8%) have no NDVI: very high ground (median 5,230 m; Lahul & Spiti, Kullu, Kinnaur) where snow masks every clear image of the year (2023 grids: 1,056–1,252). The model fills them with the training median, as in the replays. Only 2 of 18,286 road-zone cells are affected, so district alerts are not. |
| **Choices made for time** | No GEE App (the GitHub Pages page shows the same latest map without extra accounts); during the trial week the email is sent every day, also when no district is on alert, to show the system ran. |

## 2026-11-09 · Plain-language explanation of the alert rule

| | |
|---|---|
| **Added** | `docs/alert_rule_explained.md`: what the scores, levels and district percentage mean, how the replays tested the rule, how the winner was chosen (TSS) and the two cautions, in simple words for the final report and presentation. |

---

## 2026-11-07 · Storm replays: results (adoption pending Suraj's review)

| | |
|---|---|
| **Run** | 64 GEE tasks finished. `src/phaseE_03_replay_scores.py` scored all 46 days (55,253 cells each, models trained without each day's year). First run stopped on a missing input (`era5_glacier`, read per day from ERA5-Land; now read at its own grid, checked identical to the 14 Aug 2023 export). Scoring code reproduces the published 14 Aug 2023 storm-map scores exactly (max difference 0.0). |
| **Rule applied** | `src/phaseE_04_replay_evaluate.py` → `data/phaseE/replay_candidates.csv` (24 candidates). **Chosen: live Random Forest, road-neutral, district at a level when ≥ 30% of its cells within 500 m of a road reach it.** Watch: 38/44 storm checks hit (86%), 28/192 quiet district-days alarmed (15%), TSS 0.718. Warning: 32/44 (73%), 3/192 (1.6%). |
| **Old provisional rule** | Random Forest, all cells, 5%: hits 43/44 but false alarms 84/192 (44%), TSS 0.540; confirms it was too loose. |
| **Uncertainty** | `src/phaseE_05_replay_uncertainty.py` (whole days resampled, 2,000 draws): chosen TSS 0.718 (95% interval 0.545–0.870), ranked first in 44% of draws. The next six candidates (including the two-part model at 20–30%) are not distinguishable from it (difference intervals include 0). |
| **Limits found** | 30% is the largest share tried, and TSS was still rising there for this model, so a higher share might score higher; widening the grid now would be a choice made after seeing results, so it was not done. Misses: Shimla 2010-07-25 and 2011-08-07, Solan 2010-09-19/20, Lahul & Spiti and Mandi 2025-08-05 (local storms). False alarms are concentrated on wet "quiet" days (2011-09-01, 2012-08-09, 2012-09-13: mean HP rain 9–16 mm) and after the very wet July 2023; some may be unrecorded slides. |

---

## 2026-11-06 · Storm replays (Phase E) started

| | |
|---|---|
| **Goal** | Set the final alert levels and the district rule with the criteria of documentation §17.10, on past storms and quiet days, with models trained without each day's year. |
| **Replay days** | `src/phaseE_01_replay_dates.py` → `data/phaseE/replay_dates.csv`: every HP date with ≥ 3 recorded slides (16 storm days, 2010–2025), the day before each, 2 random quiet monsoon days per storm year (16). 46 dates; 44 storm-district checks; 192 quiet district-days. Chosen by rule before any scoring. |
| **Selection rule (fixed before results)** | Highest true skill statistic (hit rate − false-alarm rate) over model × district share × cells counted; basis and stated biases in §17.10. Suraj asked for a sourced rule rather than a chosen minimum hit rate; a fixed minimum was considered and not used. Both models compete (Suraj). |
| **GEE, first attempt (stopped)** | Per-day exports (46 × 8 = 368 tasks) into the new folder `users/rajsuraj777/replays/`. GEE ran them one at a time at 3–11 min each (over a day in total). 5 finished (kept), 365 queued tasks cancelled; nothing deleted. |
| **Evidence for the change** | NDVI is ~95% of the cost (259 s vs 13 s for IMERG on the same points). Ending the NDVI window 30/60/90 days earlier changes it by a median of 0.003/0.007/0.010 (correlation ≥ 0.98) vs a spread of 0.19 between places (150 HP landslide points). |
| **GEE, current** | `src/phaseE_02_replay_features.py`: grid + district + NDVI once per replay year (window ends the day before that year's first replay day; largest gap 91 days), 8 years × 8 strips = 64 tasks, assets `replays/grid_ndvi_<YYYY>_<strip>`. `src/phaseD_02_storm_features.py` refactored into a `submit()` function (same command line; backup kept). |
| **IMERG per day** | `src/phaseE_03_replay_scores.py` reads IMERG at its 0.1° pixels (≈11 s per day) and gives each cell its pixel's values after snapping the cell to the 1 km sampling grid used by `reduceRegions(scale=1000)` in training. Check against the full 14 Aug 2023 export: identical for all but ≤ 3 of 55,253 cells (without the snapping, 4.6% of cells near pixel edges differed; the same effect explains the 52-point difference in the rain test). |
| **Next** | When the 64 tasks finish: `phaseE_03` (scores), then `phaseE_04_replay_evaluate.py` (applies the rule). |

## 2026-11-06 · Rain product timing test: IMERG stays

| | |
|---|---|
| **Question** | Does another free rain product time landslides better than IMERG? Rule stated before running: score = rain on the day only; a product is better only if its timing AUC is higher on the same events and the 95% year-block bootstrap interval of the difference is above 0. |
| **Scripts** | `src/phaseC_15_pdirnow_extract.py` (PDIR-Now, 0.04°, open download, each daily file deleted after reading), `src/phaseC_16_gee_rain_d0.py` (GSMaP v8 gauge-corrected and IMERG from GEE, read-only, no assets), `src/phaseC_17_rain_product_timing_test.py` (the test). |
| **GSMaP result** | `data/phaseC/rain_product_timing_test.csv`. IST day: GSMaP 0.816 vs IMERG 0.824 (diff −0.009, interval −0.040 to +0.022); UTC day: 0.822 vs 0.819 (+0.003, −0.024 to +0.030); HP: 0.801 vs 0.807 (IST), 0.797 vs 0.790 (UTC). **Not better** (tie). |
| **Check** | IMERG re-pulled in step 16 matches the training table's `imerg_d0` (correlation 0.999); 52 of 1,938 points differ, likely points near pixel edges sampled differently. |
| **PDIR-Now result** | All 1,938 rows, UTC day: PDIR-Now 0.761 vs IMERG 0.819 (diff −0.058, interval −0.105 to −0.032); HP 0.680 vs 0.790 (−0.109, −0.158 to −0.033). **Worse.** Likely reason: infrared-only estimates miss mountain-forced rain. |
| **Download history** | Paused at 226 of 569 dates (laptop off). 6 downloaded dates were lost when the results file was briefly renamed during the GSMaP run; they are re-fetched automatically, since the script resumes from the dates already in `data/phaseC/rain_pdirnow_d0.csv`. Resume: `.venv/Scripts/python -W ignore src/phaseC_15_pdirnow_extract.py <temporary folder>`, then run step 17. On resume, 208 dates failed when the internet dropped ("getaddrinfo failed"), stored as empty; the script was changed to retry each download 3 times and to re-fetch dates that are empty at every point (results file backed up first). Re-fetch: all 208 recovered, 0 empty values left. |
| **Decision** | IMERG stays the live product. INSAT-3DR (also infrared, ~4 km) not pursued; no MOSDAC registration needed. Experiments log 6.20–6.21, mistake 7.15 (IMD gridded wording) corrected in project history, experiments log and targets. |

## 2026-11-06 · Deck v4: public sources only

| | |
|---|---|
| **Change** | Every slide's source line now cites only what a reader can access: publications, public data providers (GSI, NASA, NOAA, ECMWF, ESA, USGS, OpenStreetMap, IMD) and our earlier presentations; our own numbers are labelled "our analysis" or "our cross-validation results". No project file paths on any slide (checked: 0 of 27 slides). Speaker notes still point to project files for the team. |
| **Checks** | Validation passed; v3 backed up locally. |

## 2026-11-06 · Deck v3 (Suraj's review)

| | |
|---|---|
| **Changes** | Removed the "How to read this deck" slide (27 slides now); labelled only "Assignment 3" (no "presentation 3 of 4" anywhere); removed the date from the title slide, footer and notes; removed the 25 Nov date (summary line and next-steps title); footer simplified to title, names and institute; all slide cross-references renumbered and checked. Generator now accepts an optional output path (used while the deck was open in PowerPoint). |
| **Checks** | Validation passed; text scan: no "3 of 4", no dates of today or 25 Nov. v2 backed up locally. |

## 2026-11-06 · RQ1 test; Presentation 2 correction; deck revised for continuity

| | |
|---|---|
| **RQ1 test** | `src/phaseC_14_rq1_terrain_vs_rain.py`. First run on all rows: terrain-only AUC 0.419 (timing 0.060), below coin toss because each landslide's same-place twin (identical terrain, opposite label) is in training when it is tested; kept as `data/phaseC/rq1_terrain_vs_rain_all_rows.csv` and recorded as not a fair test. Fair test (landslides vs other slopes on storm days, no twins), `data/phaseC/rq1_terrain_vs_rain.csv`: terrain only 0.912 (HP 0.858) → + vegetation 0.918 → + IMERG rain 0.926 (HP 0.870) → full 0.928 (HP 0.877). Timing can only come from rain. |
| **Correction** | Presentation 2 described its 878 background points as sampled inside HP with a 500 m buffer; the file shows them over HP, Uttarakhand, J&K and beyond. Recorded as mistake 7.13 and stated in the deck. |
| **Deck review (Suraj)** | Compared with Presentations 1 and 2: keep the project title, label "Checkpoint Presentation 3 of 4", add a recap (the professor may not remember earlier details), research-question status, reconciliation of changed numbers, section labels and a source line on every slide; file renamed without the abbreviation "EWS". |
| **Deck v2** | `docs/presentations/Suraj - Siddhesh - Rainfall aware Landslide Early Warning for Himachal Pradesh.pptx` (+ PDF copy), 28 slides: original project title kept, "Checkpoint Presentation 3 of 4", section label and source line on every slide, new slides 2 (how to read the deck, key terms), 4 (recap of Presentations 1 and 2), 7 (numbers changed since Presentation 2 and why), 18 (research questions, with the RQ1 chart); mistakes slide includes the Presentation 2 correction and the unfair first RQ1 run. Rendered in PowerPoint and checked slide by slide; validation passed. Version 1 files (with "EWS" in the name) moved to the local backups folder. |
| **Backups** | Experiments log, project history, this log and the deck generator backed up locally before editing. |

## 2026-11-05 · Interim deck (Assignment 3) built

| | |
|---|---|
| **What** | `docs/presentations/ICTD_Assignment3_Interim_Landslide_EWS.pptx` (24 slides, notes on every slide) and a PDF copy. Built to be read without a presenter: every content slide has a title, a one-line message, and the evidence (figure, native chart or table). Sections: introduction, data, method, results, limitations and next steps, references. |
| **How** | Generator `src/deck/build_assignment3_deck.js` (pptxgenjs; run from the project root with `NODE_PATH` pointing to a folder with pptxgenjs). Rendered through PowerPoint and checked slide by slide; fixes: shortened a wrapping title, larger body text, extra spacing, two full-size maps instead of a small four-panel figure on the storm-vs-quiet slide, a corrected "12 mistakes (main ones below)" message. File validation passed. |
| **New figure** | `src/fig_negatives_before_after.py` → `docs/figures/negatives_before_after.png` (September random negatives vs new Type 2 negatives); September negatives copied to `data/legacy/negatives_features_v3.csv`. |
| **Outside numbers on slides** | IMD heavy-rain category (IMD national bulletins); LHASA detection 8–60% (Kirschbaum and Stanley 2018); GSI forecasting coverage (Ministry of Earth Sciences, 2025). The 2023 HP death toll could not be verified to one figure (press reports 257–361 depending on date), so the slides say "hundreds" with the source noted. |
| **Records** | 26 Oct research-paper presentation given by Suraj and Siddhesh (project history updated). Possible regeneration of negatives (v2) recorded as an open item (experiments log 4.6). |

## 2026-11-05 · Decisions reviewed; road-neutral adopted; interim presentation work

| | |
|---|---|
| **Decisions (Suraj)** | All earlier decisions reviewed and kept. **Road-neutral scoring adopted** for the main whole-HP map and the district alerts; real-road scores kept as a second layer, "where slides are likely to hit roads". |
| **Deadline change** | Interim presentation (problem, methodology, implementation, results) due 6 Nov; final presentation and report 25 Nov, with an impact-assessment section (method, survey questions, formats). |
| **GEE grid job** | All 8 strips completed: `hp_grid_static_v1_a … _h`, 55,253 points in total (a 1,513 · b 3,499 · c 7,843 · d 10,741 · e 11,113 · f 10,364 · g 8,142 · h 2,038). |
| **Heavy-rain baseline** | `src/phaseC_08_heavy_rain_baseline.py` → `data/phaseC/heavy_rain_baseline.csv`, `heavy_rain_baseline_curve.csv`. Rule: IMERG rain on the day ≥ 64.5 mm (IMD "heavy rain", national bulletins). At the rule's own safe-day false-alarm rate (2% all, 3% HP), the rule catches 26% of slides (HP 20%); the models 4–9% (HP live road-neutral 22%, full road-neutral 35%). **Timing test** (slides vs same-place safe days), ROC AUC: rain on the day alone 0.824 (HP 0.805) vs live model 0.683 / 0.741 road-neutral (HP 0.705 / 0.779). **Full test** (all negatives): live model 0.775 (HP 0.763) vs rain rule 0.743 (HP 0.675). Meaning: rain alone tells *when* better than the models; the models tell *where* better than rain. |
| **Timing diagnostic** | `src/phaseC_09_timing_diagnostic.py` → `data/phaseC/timing_diagnostic.csv`. The live model trained only on slides vs same-place safe days: timing AUC 0.769 (HP 0.802) vs rain alone 0.824 (HP 0.805). Most of the gap comes from mixing storm-day negatives (as wet as the slides) into training. Proposed for the final version: a two-part model, *where* (terrain, roads) × *when* (rain), as in NASA LHASA (susceptibility + rainfall trigger; Kirschbaum & Stanley 2018). |
| **Partial dependence** | `src/phaseC_10_partial_dependence.py` → `docs/figures/pdp_*.png`, `data/phaseC/partial_dependence.csv` (live model). Rain on the day: score 0.23 → 0.46, steepest 10–40 mm, then levels off (physical). 7-day rain: 0.28 → 0.36 (physical). 30-day rain: flat (not physical; storm-day negatives are as wet over 30 days, median 269 vs 217 mm). Slope: spike near 10°, then flat, gentle rise above 30° (spike is an artefact of the ≥ 10.9° rule for storm-day negatives). |
| **Storm-day job** | `src/phaseD_02_storm_features.py`: 14 Aug 2023 (31 recorded HP slides), dated features for all 55,253 points with district names → `users/rajsuraj777/storm_20230814_a … _h` (8 new assets, all completed); task IDs in `data/phaseD/storm_20230814_tasks.log`. **Problem found:** the district join (`Join.saveFirst`, inner) dropped 255 border cells that fall outside every ADM2 outline, so 54,998 points instead of 55,253; fix with an outer join before the replays. |
| **Storm map** | `src/phaseD_03_storm_map.py` → `docs/figures/storm_20230814_road_neutral.png`, `storm_20230814_real_roads.png`, `storm_20230814_rain.png`; `data/phaseD/storm_20230814_scores.csv`, `_districts.csv`, `_slides.csv`. Live model retrained **without 2023** (2,888 rows). Levels matched to the live levels' HP safe-day false alarms: road-neutral Watch 0.376 / Warning 0.463; real roads 0.348 / 0.433. Road-neutral: all 31 slides in Watch+ cells (29 in Warning); but 67% of HP cells at Watch+, 47% at Warning, and all 12 districts at Warning under the 5% rule (incl. Una, 9 mm on the day). Real roads: 10 of 31 slides in Watch+ cells (grid-cell centres are often farther from a road than the slide itself); 58% of cells at Watch+. The Warning zone follows the day's rain (Kangra–Mandi–Kullu–Shimla); the dry trans-Himalaya stays mostly quiet. Districts ranked by share at Watch+: Mandi (23 slides) 99.9%, Kullu (2) 99.3%, Hamirpur (0) 98.5%, Kangra (0) 94.5%, Bilaspur (0) 94.5%, Sirmaur (0) 94.1%, Shimla (5) 83.0%, Una (0) 75.0%, Solan (1) 70.1%, Chamba (0) 62.0%, Lahul & Spiti (0) 37.7%, Kinnaur (0) 20.3%. **Meaning:** the 5% district rule is far too loose, and cell levels over-warn on big storm days; both must be set in the Phase E replays. One storm day is an illustration, not a validation. |
| **Code fix** | `phaseD_03_storm_map.py`: district outlines can be GeometryCollections after simplifying; drawing now handles Polygon, MultiPolygon and GeometryCollection. |
| **Two-part model** | `src/phaseC_11_two_part_model.py` → `data/phaseC/two_part_comparison.csv`, `two_part_oof.csv`. WHERE part (Random Forest; slides vs other slopes on storm days; fixed features + NDVI + glacier flag, 21) × WHEN part (slides vs same-place safe days; rain only), trained inside the same year-blocked folds. WHEN part as Random Forest overfits (live 0.793) and as logistic regression on log rain does better (live 0.813; rain on the day alone 0.824). Two-part live (when = logistic), real roads: full AUC 0.813 (HP 0.777) vs single live model 0.775 (HP 0.763); HP safe days flagged at 55% HP hit 21.5% (single 25.6%); other slopes on storm days 7.4% (13.9%). Road-neutral: full 0.758 (HP 0.707), HP safe days 15.4%. Finding: timing is capped by the rain data (best live when part ≈ rain on the day alone). |
| **Storm map, two-part** | `phaseD_03_storm_map.py` now takes `[DATA_SUFFIX] [--two-part]` (backup taken first). 14 Aug 2023, two-part, trained without 2023: road-neutral Watch+ 67% of HP (unchanged), Warning 32% (single: 47%); all 31 slides in Watch+ cells. Figures `docs/figures/storm_20230814_two_part_*.png`. One storm day cannot show over-warning on its own; a quiet-day comparison was started (below). |
| **Border fix** | `phaseD_02_storm_features.py`: outer join, cells outside every district outline are kept as "unassigned"; optional asset suffix (backup taken first). Rerun for 14 Aug 2023 → `storm_20230814_v2_a … _h` (8 new assets); task IDs in `data/phaseD/storm_20230814_v2_tasks.log`. |
| **Quiet-day result** | `storm_20230912_v2_*` (8 assets) completed. Same live model trained without 2023, same levels. Road-neutral: HP at Watch+ 0.4%, Warning 0.0%, 0 of 12 districts alerted (single and two-part model); HP mean rain 0.8 mm. Storm day for comparison: 66.8%, 47.2%, 12 of 12. Caveat: the quiet day was nearly dry; wet days without slides are tested in the replays. Figures: new `src/phaseD_04_storm_vs_quiet_figure.py` → `docs/figures/storm_vs_quiet_20230814_20230912.png` and `_two_part.png`. |
| **Fix: "unassigned" district** | The 255 border cells had been treated as a 13th district in the district tables (the only quiet-day "alert" came from it). `phaseD_03_storm_map.py` now sets district levels for the 12 real districts only (backup taken first); all four v2 maps rerun. Storm day: 12 districts at Warning (two-part: 11 Warning, 1 Watch). |
| **Border fix result** | `storm_20230814_v2_*` completed: 55,253 points (255 labelled "unassigned" district). Maps rerun (`docs/figures/storm_20230814_v2_*.png`, `data/phaseD/storm_20230814_v2_*`). Results essentially unchanged: single model road-neutral Watch+ 66.8% (was 66.9%), Warning 47.2%; two-part 66.6% / 31.5%; all 31 slides still in Watch+ cells. |
| **Quiet-day job** | 12 Sep 2023: no recorded HP slide within ±10 days and none in the three states within ±3 days (from the inventory) → `storm_20230912_v2_a … _h` (8 new assets); task IDs in `data/phaseD/storm_20230912_v2_tasks.log`. |
| **Targets and summary** | `docs/targets_and_status.md` (targets for 25 Nov vs now; proposals pending Suraj's approval); `src/phaseC_12_summary_figure.py` → `docs/figures/model_comparison.png`. |
| **Principle (Suraj)** | No tuning for a higher score. Understand why the system behaves as it does, correct real mistakes, and document every experiment, including dropped and wrong ones. |
| **Strict vs easy testing** | `src/phaseC_13_strict_vs_easy_cv.py` → `data/phaseC/strict_vs_easy_cv.csv`. Same Random Forest recipes. Live model (28): whole years held out 0.775 (HP 0.763, timing 0.683); whole storm days held out 0.792 (0.751, 0.707); random rows 0.856 (0.803, 0.802). Full model (38): 0.801 / 0.819 / 0.880. Random-row testing inflates scores by about 0.08 (timing by about 0.12). This explains the optimistic 0.895 of the Sep prototype, which also used random negatives. |
| **Targets rewritten** | `docs/targets_and_status.md` now states what the system must do and how each is checked, with scores as checks, not goals. Previous score-framed version backed up locally. |
| **Experiments log** | New `docs/experiments_log.md`: every approach since August, with its result and status (kept, dropped, changed, found wrong), including 11 of our own mistakes and a not-done list. |
| **Project history, merged** | `docs/project_history.md` replaced by the fuller project record (26 sections: timeline, decisions table, mistakes, data sources, tools, numbers, contributions, references), corrected: Siddhesh's change-detection track has no work after September (Suraj, 5 Nov); road-detection study briefed 26 Oct, research not started; GEE assets counted (53); the IMD reference for graded alert levels removed (not verified; LHASA kept); the September random negatives dated to September (the Phase B notes say October); their road distance rechecked (median 2.6 km for the 755 points inside our road layers; the notes give 4.8 km over all points); border-fix result added. Earlier version backed up locally. Counts verified: 35 Python scripts / 3,040 lines; 25 files in `data/phaseC/`; elevation of the September negatives 3,866 m median, 406 above 4,000 m (notes: 3,868 m, 408). |
| **Phase B notes** | `docs/Negative_Points_Generation_Notes.pdf` added (9 pages; read in full before adding). |
| **Project history (first version)** | New `docs/project_history.md`: the full record from August (proposal, feedback, data, models, system), timeline, references with verification status, contributions; open points marked [to confirm]. Sources: the team's working notes, reports and decks in Downloads, and this repository. |

## 2026-11-02 · Live model, road-neutral test, whole-HP grid job

| | |
|---|---|
| **Decisions (Suraj, 1 Nov)** | Option A (live model on IMERG + fixed features); whole-HP prediction with cells > 500 m from a road marked lower confidence; test road-neutral prediction before deciding. |
| **Live model** | `src/phaseC_07_train_live.py` → `models/rf_roads_live_v1.joblib` (5.9 MB) + meta; `data/phaseC/threshold_options_live.csv`, `oof_live.csv`. Year CV: ROC AUC 0.775, HP 0.763, weather-only test 0.683. Same HP hit rates as the 38-feature levels at scores ≈ 0.345 / 0.441, but HP safe-day false alarms 26% / 13% (vs 16% / 5%). |
| **Road-neutral test** | `src/phaseC_06_road_neutral_test.py` → `data/phaseC/road_neutral_test.csv`, `road_neutral_equal_false_alarm.csv`, `road_neutral_oof.csv`. Roads set to the training-fold positives' median at prediction. Remote positives (> 500 m from a road): 70, of which 9 in HP. At fixed Watch level (38-feature model): remote slides reaching Watch 47% → 57%; safe-day false alarms 24% → 31%; other slopes on storm days flagged 10% → 42%. At equal safe-day false alarms (16%), slides caught 47% → 53% (live: 37% → 49%), remote 39% → 44% (live: 29% → 36%), other slopes on storm days 5% → 22% (live: 3% → 18%). Weather-only AUC rises (0.746 → 0.777; live 0.683 → 0.741). Caveats: few remote cases; remote false alarms cannot be measured. **Decision pending (Suraj).** |
| **Code change** | `src/stack.py`: the fixed-feature steps of `extract_features()` moved unchanged into a new `extract_static()`, which `extract_features()` now calls. Check on 5 training landslides: 100/100 values identical. Backup taken first. |
| **GEE job (new assets, nothing overwritten)** | `src/phaseD_01_static_grid.py`: 55,253 HP 1 km cell centres, 20 fixed features, 8 latitude strips → `users/rajsuraj777/hp_grid_static_v1_a … _h`; task IDs in `data/phaseD/static_grid_tasks.log`. Status at last check: 3 running, 5 queued. |
| **Docs** | Phase D design note: goal (whole HP), §2 (Option A decided), §4 (55,253 points), §5 (rule wording), §6 (asset size). Technical documentation not changed yet (waiting for Suraj to see the numbers). |
| **Backup / undo** | Local backups of `stack.py`, the Phase D design note and this log before the edits. |

## 2026-10-24 · Alert levels, final model, live-data checks, Phase D design draft

| | |
|---|---|
| **Alert levels (Suraj)** | Two levels, both provisional: Watch ≥ 0.35 (HP: 55% caught, 16% of safe days flagged), Warning ≥ 0.45 (33%, 5%). Finalised after the Phase E replays with criteria written in advance (documentation §17.10): district on Watch or higher on the event day or the day before; alert days on quiet monsoon days; each storm replayed with a model trained without its year. Limitation 16 added (about 45% of HP slides missed even at Watch). |
| **Final model** | `src/phaseC_04_train_final.py` → `models/rf_roads_v1.joblib` (5.5 MB) + `models/rf_roads_v1_meta.json`; trained on all 3,136 rows; reload check identical; in-sample AUC 0.999 (sanity check only, not skill). Model card: `docs/model_card.md`. |
| **Live data check (GEE, read-only)** | IMERG ~2 days behind; ERA5-Land ~12 days (latest 12 Oct); CHIRPS v2 and v3 ~24 days (latest 30 Sep); GFS runs complete at 209 steps, taking ~6–12 h to arrive. GFS `total_precipitation_surface` resets every 6 hours (data test at 3 wet locations). |
| **Data test** | `src/phaseC_05_live_features.py` → `data/phaseC/live_feature_test.csv`. Random Forest, year CV: all 38 features 0.801; no ERA5-Land 0.797; no CHIRPS 0.782; neither 0.775 (weather-only test 0.746 → 0.683; HP 0.790 → 0.763). |
| **Grid estimate** | 18,277 of 55,253 HP 1 km cells have their centre within 500 m of a motorable road (34,853 road lines in HP). geoBoundaries ADM2 contains all 12 HP districts. |
| **Phase D design** | Draft `docs/phaseD_design_note.md`. Open: live feature set (recommended: IMERG + fixed features only), district rule starting value (5% of corridor points), Suraj's setup steps. |
| **Mistake corrected** | Said "7 CHIRPS features" in the first report; there are 6. |
| **Backup / undo** | Local backups of the documentation and this log before the edits. No GEE assets created; no git. |

## 2026-10-23 · Model chosen: Random Forest with road features

| | |
|---|---|
| **Decision (Suraj)** | Random Forest with road features (500 trees, min 3 rows per leaf, 38 features). |
| **Why** | Close to XGBoost overall (ROC AUC 0.801 vs 0.807; HP 0.790 vs 0.804); not worse than the road-free models on the Type 1 test, while XGBoost is; fewer safe-day false alarms at similar HP hit rates. |
| **Files changed** | Documentation §17.9. |
| **Open** | Alert threshold (Random Forest table, documentation §17.7). |

## 2026-10-23 · Road features kept; Type 1 test and threshold options

| | |
|---|---|
| **Decision (Suraj)** | Keep the road features, tentatively XGBoost, on 3 conditions: (1) compare all models on the Type 1 test alone and flag XGBoost if it is clearly worse; (2) limit the risk map and alerts to ~500 m road corridors; (3) describe the target as "reported landslides near roads", state the reporting bias, keep road-free results as a sensitivity check. |
| **What** | New scripts `src/phaseC_02_type1_check.py` and `src/phaseC_03_threshold_options.py`; outputs `data/phaseC/type1_check.csv`, `type1_differences.csv`, `type1_equal_hit.csv`, `threshold_options.csv`. Documentation: target and corridor rule in §2; limitation 15 in §15; §17.5–17.9 added; §18 updated. |
| **Rule (fixed before the test)** | "Clearly worse" = lower ROC AUC on positives vs Type 1, with the 95% year-block bootstrap interval (2,000 repeats) of the difference entirely below zero. |
| **Result** | XGBoost with roads: Type 1 AUC 0.722, **clearly worse** than road-free logistic (0.753; difference −0.031, interval −0.061 to −0.009) and road-free Random Forest (0.751; −0.029, −0.044 to −0.010). Random Forest with roads (0.746) and logistic with roads (0.744) are not clearly worse than any road-free model. |
| **Threshold options** | For HP at similar hit rates, Random Forest flags fewer safe days than XGBoost (e.g. 55% caught with 16% vs 23% of safe days flagged). Full tables in documentation §17.7. |
| **Road coverage** | 92.8% of positives and 100% of Type 2 rows lie within 500 m of a motorable road; about 7% of recorded slides fall outside the corridor. |
| **Open** | Final model (XGBoost or Random Forest with roads) and alert threshold: waiting for Suraj. |
| **Backup / undo** | Local backups of the documentation and this log before the edits. |

## 2026-10-23 · Phase C step 1: three models compared

| | |
|---|---|
| **What** | New script `src/phaseC_01_train_compare.py`; outputs in `data/phaseC/` (metrics, out-of-fold predictions, threshold table, permutation importance, road check, 3 figures). Added §17 (Phase C) to the documentation; renumbered §17→18, §18→19; added 3 verified references (Roberts et al. 2017, Breiman 2001, Chen & Guestrin 2016). |
| **Method** | Logistic regression, Random Forest, XGBoost; 38 features (left out `ndvi_pre_n`, `imerg_images_31d`, `imerg_provisional_31d`, `aspect_deg`); 5-fold blocked CV by year (main) and by event date. |
| **Evidence for leaving out `ndvi_pre_n`** | Data test: median clear-image count 18 (2005–12), 27 (2013–20), 41 (2021–26), so it encodes the year; positives and Type 1 negatives have different year mixes. |
| **Results (year CV)** | ROC AUC: logistic 0.780, RF 0.801, XGBoost 0.807 (HP rows only: 0.753 / 0.790 / 0.804). Without the two road features: 0.762 / 0.755 / 0.737. At equal hit rate the safe-day false-alarm rate is about the same for all models (≈ 0.20 at 50% hit, ≈ 0.26 at 60%); XGBoost at 60% hit ≈ 8 false alarms per month at one landslide spot (proxy). |
| **Found** | `dist_major_road_m` is the first or second most important feature in all models; road features help only against Type 2 negatives, and XGBoost's lead over the others comes from them. |
| **Open** | Keep or drop road features; final model; alert threshold. Not chosen yet; waiting for Suraj. |
| **Runtime** | About 4 minutes on the laptop; no GEE, no Drive, no git. |
| **Backup / undo** | Local backups of the documentation and this log before the edits. |

## 2026-10-23 · Phase B results added to the project

| | |
|---|---|
| **What** | Copied the Phase B outputs from `Downloads\ICTD_phaseB`: `data/phaseB/` (`training_table_v1.csv`, `negatives_features_v1.csv`, `negatives_type1_points.csv`, `negatives_type2_points.csv`, `phaseB_tasks.log`), `src/phaseB_*.py` (4 scripts), `docs/phaseB_design_note.md`. All byte-identical to the source. Added §16 (Phase B) to the documentation; renumbered §16→17, §17→18; added 3 verified references. |
| **Why** | Keep everything for Phase C and the report in one place. |
| **Evidence (checks re-run)** | 3,136 rows × 51 columns; 969 positives identical to `positives_features_v1` without Ladakh; Type 1 fixed features identical to the source positive (969/969); Type 1 rule 0 violations; Type 2 slope ≥ 10.9°, road ≤ 284 m, nearest slide ≥ 2.0 km, max 10 per date; 2 missing cells (glacier SWE). Full table in documentation §16.5. |
| **Fix** | Design note: Steger et al. 2024 is volume 15(**3**), not 15(5); full titles and DOIs added for Steger et al. 2024 and Zhu et al. 2024 (both verified by web search). |
| **Found** | Positives cluster in 2013 and 2025 while Type 1 dates are spread over 2005–2025; data-quality columns (`ndvi_pre_n`, `imerg_images_31d`, `imerg_provisional_31d`) could let a model tell years apart. To handle in Phase C. |
| **Backup / undo** | Local backups of the documentation, design note and this log before the edits. GEE assets `negB_type1_a/b/c`, `negB_type2_a/b/c` are new; nothing was overwritten. |

## 2026-10-22 · Old workspace in Downloads removed (Suraj confirmed)

| | |
|---|---|
| **What** | Sent the contents of `Downloads\ICTD_project_workspace` to the Windows Recycle Bin (not a permanent delete). The empty top folder could not be removed because a running process still holds it; it can be deleted by hand after closing the app or terminal. |
| **Check before removing** | Compared checksums of all 219 old files with the G: folder: 217 have identical copies. The other 2 differ for known reasons: `.gitignore` was updated in G: (added `.venv/`), and `gee_scripts_repo/.git/index` is git's file cache, refreshed when `git status` ran in G: (repo clean, 71 commits). |
| **Backup / undo** | Restore from the Recycle Bin (items: `gee_scripts_repo`, `outputs`, `py_runners`, `_private`, `.gitignore`, `CHANGELOG.md`). |
| **Data affected?** | No. Everything lives in the G: project folder. |

## 2026-10-22 · Project moved to G: and set up as a developer project

| | |
|---|---|
| **What** | Copied the whole workspace from `Downloads\ICTD_project_workspace` to `G:\ALL PROJECTS\Landslide Prediction Project` (219 files, all checksums matched; GEE repo clean, 71 commits). Reorganised: `py_runners/` → `src/`, `outputs/` → `data/` (documentation → `docs/`), new `models/`. Added `README.md`, `requirements.txt`, a project `.venv` (Python 3.13; earthengine-api 1.7.49, pandas 3.1.0, numpy 2.5.4, scikit-learn 1.9.1, xgboost 3.4.1, matplotlib 3.11.2, installed with `--no-cache-dir`), and `.venv/` in `.gitignore`. Updated the folder paths in the documentation (§3 and §13). |
| **Why** | One permanent project folder that becomes the GitHub repo; an isolated environment so nothing is installed into the system Python. |
| **Evidence (checks)** | With `.venv` Python: Earth Engine initialises; `stack.all_bands()` returns 42 bands; GEE `positives_v5` has 981 features; `data/positives_features_v1_local.csv` reads as 981 × 52 with 1 missing cell (the intentional glacier SWE cell); `git fetch` to the GEE repo works. |
| **Code changes** | None. Scripts take their input and output folders as arguments, so no paths had to change. |
| **Backup / undo** | The full original stays in `Downloads\ICTD_project_workspace` (to be deleted only after Suraj confirms). Local backups of the documentation and this log before the path edits. |
| **Data affected?** | No. |

## 2026-10-22 · Completion plan agreed

| | |
|---|---|
| **What** | Agreed the plan for the remaining phases (B: negatives, C: model, D: live system, E: storm replay, F: report and slides), target finish 18 Nov 2026. |
| **Speed-up decisions** | Python only from now on (the Code Editor is used only for the GEE App); "same place, safe day" negatives reuse the fixed features of the positives and only rain/soil/snow/NDVI are computed for the new dates; about 2,000 negatives with a per-storm-date cap only; the dashboard shows the latest daily risk map, saved as a GEE image by the daily job; one storm example for the forecast comparison; the GEE feature jobs start as soon as the Phase B design is approved. |
| **Deferred to the final report (Phase F)** | Dropping the old "23.6% vs 11.7%" trigger claim (corrected values: Bhusanket 2.9%, NASA 11.9%, overall 0.7%); verifying the titles of McAdoo et al. 2018 and Leibundgut et al. 2016; the OSM-roads-completeness limitation (UK 172,824 lines vs HP 45,135). |
| **Why** | Deadline about mid-November; fixed features (terrain, roads, rocks, faults, landforms, land cover) do not change with date, so recomputing them would waste hours of GEE time. |
| **Data affected?** | No. |

## 2026-10-22 · Fix 1: terrain "medians" in documentation §5 were actually means

| | |
|---|---|
| **What** | §5 "Results at positives" said elevation median 1,390 m and slope median 27.6°. Those numbers are the **means**. Changed to: elevation median 1,236 m (mean 1,390); slope median 28.6° (mean 27.6°). |
| **Why** | A median and a mean describe different things (the middle value vs the average). The report must label them correctly. Elevation is skewed by a few very high points, so its mean is higher than its median. |
| **Evidence (data check)** | Recomputed from `outputs/positives_features_v1_local.csv` (981 rows) with Python's `statistics` module: elevation mean 1,390.4, median 1,235.6; slope mean 27.6, median 28.6; TPI mean −28.8, median −28.5 (the TPI "median −29 m" was already correct after rounding); TWI range 4.1–24.4 (correct). |
| **Files changed** | `outputs/ICTD_Landslide_Feature_Stack_Documentation.md` (one sentence in §5). |
| **Backup / undo** | Local backup `ICTD_Landslide_Feature_Stack_Documentation_2026-10-22_before_median_fix.md`: copy it back over the master to undo. |
| **Data affected?** | No. Only a label in the documentation; no table or model input changed. |
