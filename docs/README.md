# Documents: what to read, and in which order

New to the project? Read the first three, in this order. Each one is written for someone with no background in landslides or machine learning.

| # | Document | What it tells you |
|---|---|---|
| 1 | [alert_rule_explained.md](alert_rule_explained.md) | How every 1 km square gets a risk score, when a district goes on Watch or Warning, and how that rule was tested on past storms |
| 2 | [monsoon_replay_explained.md](monsoon_replay_explained.md) | What would have happened if the system had run every day of the 2023 and 2025 monsoons |
| 3 | [impact_assessment.md](impact_assessment.md) | How we would find out whether the system actually helps people: a pilot plan, measures, risks, and ready-to-use questionnaires |

## Running the system
| Document | What it tells you |
|---|---|
| [daily_system_setup.md](daily_system_setup.md) | How the daily run works, why it is built this way, and the one-time setup (GitHub, Earth Engine robot login, email) |
| [model_card.md](model_card.md) | A one-page "label" for the model: what it was trained on, how well it does, the final alert levels, and its limits |

## The full record
| Document | What it tells you |
|---|---|
| [project_history.md](project_history.md) | The complete story from August 2026: every phase, decision, mistake and result |
| [experiments_log.md](experiments_log.md) | Every experiment we tried, including the ones we dropped and the mistakes we found, with the reason |
| [targets_and_status.md](targets_and_status.md) | What the system should achieve, how each goal is checked, and where it stands |
| [ICTD_Landslide_Feature_Stack_Documentation.md](ICTD_Landslide_Feature_Stack_Documentation.md) | Technical documentation: how each of the 42 features was built and checked, with references (long; use it as a reference book) |
| [../CHANGELOG.md](../CHANGELOG.md) | Every change since 22 Oct 2026: what, why, the evidence, and how to undo it |

## Design notes (written before building each part)
| Document | What it tells you |
|---|---|
| [phaseB_design_note.md](phaseB_design_note.md) | How the "no landslide" examples were designed |
| [phaseD_design_note.md](phaseD_design_note.md) | The original design of the daily system (what changed later is noted at the top) |
| [Negative_Points_Generation_Notes.pdf](Negative_Points_Generation_Notes.pdf) | Notes on generating the "no landslide" examples |

## Pictures and slides
- [figures/](figures/): all charts and maps. The most useful ones:
  - `monsoon_2023_calendar.png`, `monsoon_2025_calendar.png`: alert level of every district on every monsoon day.
  - `storm_vs_quiet_20230814_20230912.png`: the whole-HP map on a disaster day next to a quiet day.
  - `storm_20230814_v2_road_neutral.png`: risk map of 14 Aug 2023, the worst day in our records.
  - `model_comparison.png`: all models compared.
  - `pdp_panel.png`: how rain and slope change the risk, a check that the model behaves sensibly.
- [presentations/](presentations/): the interim presentation (Assignment 3, 6 Nov 2026).

## Words you will meet
- **Positive / negative example:** a landslide / a "no landslide" case the model learns from.
- **Feature:** one measured property of a place or day, e.g. slope or rain in the last 7 days.
- **Random Forest:** the type of machine-learning model used; it combines many simple decision trees.
- **Year-blocked testing:** the model is always tested on years it did not learn from, like an exam with unseen questions.
- **ROC AUC:** a score from 0.5 (coin toss) to 1 (perfect) for how well the model ranks risky cases above safe ones.
- **IMERG / GFS:** NASA's satellite rain measurements / the US weather-forecast model.
- **Road-neutral scoring:** every square is scored as if it were watched as closely as a roadside slope, so that squares far from roads are not wrongly marked safe.
- **District-day:** one district on one day.
