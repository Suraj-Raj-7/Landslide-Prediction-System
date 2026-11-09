# What the final system should achieve, and where we are (5 Nov 2026)

**Principle.** The aim is not a high score. The aim is a warning system whose behaviour we understand, tested honestly, with its limits stated. A score is only a check on whether the system does its job. Where the data limit what is possible, we report the limit rather than tune the method to hide it.

All numbers: Himachal Pradesh rows, year-blocked cross-validation (whole years held out), unless marked otherwise.

## 1. What the system must do, and how we check it

| # | The system should… | How we check it | Where we are now | What is left |
|---|---|---|---|---|
| 1 | **Tell landslide days from safe days** at the same place (timing) | Timing test: slides vs same-place safe days; compare with rain on the day alone (0.805) | Best live model 0.78 (road-neutral). Not better than rain alone. **Understood why:** the rain data itself sets the ceiling (IMERG pixels ~10 km), and storm-day negatives taught the model to weigh rain less | Keep the two-part structure; finer free rain tested 6 Nov: GSMaP ties IMERG, PDIR-Now (~4 km) is worse (HP 0.680 vs 0.790), so IMERG stays and the ceiling is stated; IMD gridded is coarser (0.25°), not denser; otherwise state the ceiling |
| 2 | **Point to the right places** on a rainy day | Slides vs other slopes on storm days | The model separates them clearly better than rain alone (0.777 vs 0.675, two-part live) | Revisit the slope ≥ 10.9° sampling rule that distorts gentle slopes |
| 3 | **Warn before or on the day of major events, at district level** | Storm replays, criteria fixed before running: district at Watch or higher on the event day or the day before | **Done (7 Nov):** 16 storm days replayed with held-out-year models: 38 of 44 affected districts at Watch on the day or the day before (86%); Warning 32 of 44 | Misses are local storms (Shimla, Solan, Lahul & Spiti); stated as a limitation |
| 4 | **Stay mostly quiet on quiet days**, so people keep trusting it | Alert days per district on monsoon days with no recorded slide; whole-HP map on a quiet day | **Done (7–9 Nov):** final district rule (≥ 30% of road-zone cells) alarms on 15% of quiet district-days at Watch and 1.6% at Warning, against 44% under the old 5% rule | False alarms concentrate on wet days without recorded slides; upper bound |
| 5 | **Be honest about where it is reliable** | Lower-confidence mark beyond 500 m from roads; road-neutral check on the 70 remote slides | Implemented on the map; the remote check rests on 70 slides (9 in HP); remote false alarms cannot be measured | State as a limitation |
| 6 | **Run every day without manual work** | Daily automatic run, email to the chosen recipients, GEE App | Designed; whole-HP grid features computed | Build and run for at least a week before 25 Nov |
| 7 | **Be evaluated honestly** | Same models tested three ways | Years held out 0.775; storm days held out 0.792; random rows 0.856 (live model). We report the strict number | Use the strict test throughout |

## 2. Reference points (not targets)
- **Rain on the day alone:** timing 0.805, where + when 0.675 (HP).
- **Earlier version (Sep 2026):** random negatives and random cross-validation gave RF 0.895. That number was too optimistic for two reasons we have since measured: easy negatives, and testing on storms the model had already seen (§1 row 7).
- **Published operational system:** NASA's LHASA nowcast detected 8–60% of catalogued landslides, depending on the evaluation (Kirschbaum & Stanley 2018).
- **Published static susceptibility studies in HP** report AUC 0.79–0.91 (Meena et al. 2019) and 0.863 (Singh et al. 2024). These are static maps tested in other ways, so they are not directly comparable with a daily, year-blocked test.

## 3. What a good outcome by 25 Nov looks like
1. A daily system that runs on its own and produces a whole-HP map and district alerts.
2. Storm replays and quiet-day checks, with criteria set in advance and results reported whatever they are.
3. A clear explanation of each limit: timing capped by rain data; reporting bias towards roads; few remote slides to test with; a live model weaker than the best model.
4. Every experiment, including the dropped and wrong ones, documented (`docs/experiments_log.md`).
