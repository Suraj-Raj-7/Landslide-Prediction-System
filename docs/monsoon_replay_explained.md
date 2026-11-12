# What if the system had been running all monsoon? (2023 and 2025)

Written 12 Nov 2026. Script: `src/impact_01_monsoon_replay.py`. Results: `data/impact/`. Pictures: `docs/figures/monsoon_2023_calendar.png`, `docs/figures/monsoon_2025_calendar.png`.

## The idea
Our earlier test (the "storm replays") looked at 32 chosen days. Here we went further: we pretended the warning system had been running **every day from 15 June to 30 September** (108 days) in two real monsoons, 2023 and 2025. For each day and each of the 12 districts we wrote down what the system would have said: no alert, Watch or Warning.

**Fair test:** for each year, the model was trained **without any data from that year**. So it had never seen those storms, just like a real season in the future.

Everything else is exactly the live system: same model, same levels, same district rule (a district is on alert when at least 30% of its squares near roads are at that level).

## How to read the picture
Each row is a district, each small box is one day. Grey = no alert, orange = Watch, red = Warning. A black dot = a landslide was **recorded** in that district that day.

## What we found

| | 2023 | 2025 |
|---|---|---|
| District-days with a recorded landslide | 22 | 35 |
| ...of these, the district was on alert that day or the day before | **17 (77%)** | **24 (69%)** |
| ...of the caught ones, the alert was already there **the day before** | 12 | 20 |
| ...missed | 5 | 11 |
| District-days on alert (Watch or Warning), out of 1,296 | 426 (33%) | 333 (26%) |
| Alert days per district in the monsoon (average) | about 36 | about 28 |
| Alert district-days with **no recorded** landslide that day or the next | 402 | 291 |

### In plain words
1. **It catches most recorded landslides, often a day early.** About 7 out of 10 district-days with a recorded landslide were on alert, and most of those were already on alert the day before. A day's notice is what lets a road department move machines or close a road.
2. **The alerts line up with the real disasters.** In 2023 the long red stretches are 8–11 July and 13–15 August, the two worst events of that monsoon in HP.
3. **But it alerts a lot.** A district would be on alert on about 1 day in 3 or 4 during the monsoon. Most of those days have no recorded landslide.
4. **Some of those "extra" alerts are probably real landslides that nobody recorded.** Our landslide list is far from complete, and it hardly has any events for the lower districts (Kangra, Hamirpur, Una, Bilaspur) in 2023, even though those districts had very heavy rain. So "alert without a recorded landslide" is an **upper limit** on false alarms, not the true number.

### Why this matters for real use (impact)
- **The good part:** most recorded landslides come with a warning, often a day ahead.
- **The risk:** if officers receive alerts on one in three monsoon days and see nothing happen, they may start ignoring them ("alert fatigue"). This is the most important thing a pilot must measure: how many alerts are acceptable, and how many of the "extra" alerts were actually real landslides. The per-alert feedback form in the impact section is designed for exactly this.
- **What we did NOT do:** we did not change the rule to make these numbers look better. The rule was fixed by the earlier test; changing it after seeing this season would be fitting the answer to the data. Instead, a pilot would collect ground reports and then adjust the rule per district, with evidence.

## Two checks
- **Vegetation timing.** The vegetation layer used for each year was built from data up to early July (2023: up to 6 July; 2025: up to 15 July). For June days, that means it includes a few weeks of later data. Counting only the days after those dates gives almost the same result (2023: 17 of 21 caught; 2025: 23 of 32), so this does not change the conclusion.
- **Border squares.** No recorded landslide fell outside the 12 districts.
