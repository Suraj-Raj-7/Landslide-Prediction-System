"""Impact step 1: run the warning system for EVERY day of one past monsoon.

IN SIMPLE WORDS
  Our storm replays tested 32 chosen days. Here we pretend the system was
  already running during a whole monsoon (15 June to 30 September) and look
  at what a district office would have received, day after day:
    - on how many days was each district on Watch or Warning?
    - on the days with recorded landslides, was the district on alert
      (on that day or the day before)?
    - how many alert days had no recorded landslide (possible false alarms)?
  This is the "proof of concept" evidence for the impact section.

FAIR TEST
  The model is trained WITHOUT any data from the monsoon year being replayed
  (the same rule as the storm replays), so it has never seen these storms.
  Same model, levels and district rule as the live system:
    live Random Forest, road-neutral scoring; cell Watch >= 0.376,
    Warning >= 0.463; district at a level when >= 30% of its cells within
    500 m of a road reach it (docs/alert_rule_explained.md).

INPUTS (all checked earlier)
  - Grid per year: users/rajsuraj777/replays/grid_ndvi_<YEAR>_a..h (fixed
    features, district, vegetation). The vegetation window ends on the day
    before that year's first storm-replay day (2023-07-07, 2025-07-16). For
    days BEFORE that date the vegetation value contains a few weeks of later
    data; the effect is tiny (median change 0.01 over 90 days, test of
    6 Nov 2026), and results are also reported for the later days only.
  - Rain: measured IMERG rain per Indian day, the same code as the live
    system (live_02_rain.py; identical to the training data for 55,252 of
    55,253 cells). No forecast is needed for past days.
  - Glacier flag: fixed over time (627 cells), as in the live system.
  - Recorded landslides: data/positives_features_v1_local.csv (HP only),
    each placed in the district of its nearest grid cell.

LIMITS
  "No recorded landslide" does not mean "no landslide": the inventory misses
  many events, mostly away from roads. So "alert days without a recorded
  slide" are an upper bound on false alarms.

RUN      .venv/Scripts/python -W ignore src/impact_01_monsoon_replay.py 2023
OUTPUTS  data/impact/monsoon_<YEAR>_daily.csv    one row per district per day
         data/impact/monsoon_<YEAR>_summary.csv  one row per district (+ HP total)
         docs/figures/monsoon_<YEAR>_calendar.png
"""
import datetime as dt
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from phaseE_03_replay_scores import load_year_grid, train_year   # also logs in to Earth Engine  # noqa: E402
import live_02_rain as R  # noqa: E402
from phaseC_01_train_compare import ROAD  # noqa: E402

FIRST_REPLAY_DAY = {2023: dt.date(2023, 7, 7), 2025: dt.date(2025, 7, 16)}   # vegetation window ends the day before
LEVELS = {0: "none", 1: "watch", 2: "warning"}


def season_rain(grid, year):
    """Measured rain per Indian day, 30 days before 15 June up to 30 September, for every cell."""
    first, last = dt.date(year, 6, 15), dt.date(year, 9, 30)
    days = [first - dt.timedelta(days=30) + dt.timedelta(days=k) for k in range((last - first).days + 31)]
    t_end = R.ist_day_window(last)[1]                    # everything measured: no forecast
    parts = []
    for i in range(0, len(days), 25):                    # 25 days per request keeps each request small
        img, _, _ = R.daily_totals_image(days[i:i + 25], t_end, [])
        vals, xy = R.sample_pixels(img, R.IMERG_COL.first().projection())
        parts.append(R.to_cells(grid, vals, xy))
        print(f"rain: {days[i]} .. {days[min(i + 24, len(days) - 1)]}", flush=True)
    return pd.concat(parts, axis=1), [first + dt.timedelta(days=k) for k in range((last - first).days + 1)]


def recorded_slides(grid, year):
    """Recorded HP landslides in the monsoon, with the district of the nearest grid cell."""
    p = pd.read_csv("data/positives_features_v1_local.csv")
    s = p[(p.state == "HP") & (p.event_date >= f"{year}-06-15") & (p.event_date <= f"{year}-09-30")].copy()
    s["district"] = [grid.district.values[np.argmin((grid.lon.values - a) ** 2 + (grid.lat.values - b) ** 2)]
                     for a, b in zip(s.lon, s.lat)]
    return s.groupby(["event_date", "district"]).size().rename("slides").reset_index()


def summarise(daily, part):
    """One row per district: alert days, recorded-slide days, hits, misses, unconfirmed alerts."""
    rows = []
    for name, d in list(daily.groupby("district")) + [("HP (all districts)", daily)]:
        d = d.sort_values("date")
        alert = d.level != "none"
        # a slide day is a hit if the district was on alert that day or the day before
        prev = d.groupby("district")["level"].shift(1).fillna("none") != "none"
        slide = d.slides > 0
        nxt = d.groupby("district")["slides"].shift(-1).fillna(0) > 0
        rows.append({"district": name, "days": d.date.nunique(), "part": part,
                     "watch_or_warning_days": int(alert.sum()), "warning_days": int((d.level == "warning").sum()),
                     "days_with_recorded_slides": int(slide.sum()),
                     "slide_days_on_alert_day_or_day_before": int((slide & (alert | prev)).sum()),
                     "slide_days_alert_already_day_before": int((slide & prev).sum()),
                     "slide_days_missed": int((slide & ~(alert | prev)).sum()),
                     "alert_days_with_slide_that_day_or_next": int((alert & (slide | nxt)).sum()),
                     "alert_days_without_recorded_slide": int((alert & ~(slide | nxt)).sum())})
    return pd.DataFrame(rows)


def calendar(daily, year, path):
    """One row per district: coloured by level each day, black dot on days with recorded slides."""
    names = sorted(daily.district.unique())
    days = sorted(daily.date.unique())
    col = {"none": "#e6e6e6", "watch": "#f4a261", "warning": "#c0392b"}
    fig, ax = plt.subplots(figsize=(13, 0.42 * len(names) + 1.6))
    for i, n in enumerate(names):
        d = daily[daily.district == n].set_index("date")
        for j, day in enumerate(days):
            ax.add_patch(plt.Rectangle((j, i), 1, 0.85, color=col[d.level[day]], lw=0))
            if d.slides[day] > 0:
                ax.plot(j + 0.5, i + 0.42, "o", color="black", ms=3.5)
    ax.set_xlim(0, len(days))
    ax.set_ylim(len(names), -0.2)
    ax.set_yticks([i + 0.42 for i in range(len(names))])
    ax.set_yticklabels(names, fontsize=8)
    ticks = [j for j, day in enumerate(days) if pd.Timestamp(day).day in (1, 15)]
    ax.set_xticks([t + 0.5 for t in ticks])
    ax.set_xticklabels([pd.Timestamp(days[t]).strftime("%d %b") for t in ticks], fontsize=8)
    handles = [plt.Rectangle((0, 0), 1, 1, color=col[k]) for k in ["none", "watch", "warning"]] + \
              [plt.Line2D([], [], marker="o", color="black", lw=0, ms=4)]
    ax.legend(handles, ["No alert", "Watch", "Warning", "Recorded landslide(s)"], loc="upper center",
              bbox_to_anchor=(0.5, -0.12), ncol=4, fontsize=8, frameon=False)
    ax.set_title(f"Monsoon {year}: district alert level every day (model trained without {year})", fontsize=10)
    for s in ["top", "right", "left", "bottom"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def score_season(year, rule, features):
    """Score every HP cell on every monsoon day and apply the district rule (the slow part, ~30 min)."""
    grid = load_year_grid(year)
    grid["era5_glacier"], _ = R.glacier_flag(grid)
    print(f"grid {year}: {len(grid)} cells", flush=True)
    rain, season = season_rain(grid, year)

    t = pd.read_csv("data/phaseB/training_table_v1.csv")
    score, road_median = train_year(t, features, year)
    print(f"model trained without {year}", flush=True)

    rz = (grid.dist_road_m <= rule["road_zone_m"]).values
    keep = (grid.district != "unassigned").values
    X = grid.copy()
    for c in ROAD:
        X[c] = road_median[c]                            # road-neutral scoring
    rows = []
    for day in season:
        X[R.IMERG_FEATURES] = R.features_from_daily(rain, day).values
        s = score(X)["rf"]
        lvl = np.where(s >= rule["cell_warning"], 2, np.where(s >= rule["cell_watch"], 1, 0))
        g = pd.DataFrame({"district": grid.district.values, "lvl": lvl, "rain": X.imerg_d0.values})[keep & rz]
        for name, d in g.groupby("district"):
            w, wr = (d.lvl >= 1).mean(), (d.lvl == 2).mean()
            level = 2 if wr >= rule["district_share"] else (1 if w >= rule["district_share"] else 0)
            rows.append({"date": day.isoformat(), "district": name, "level": LEVELS[level],
                         "road_zone_cells_watch_or_above_pct": round(100 * w, 1),
                         "road_zone_cells_warning_pct": round(100 * wr, 1),
                         "rain_road_zone_mean_mm": round(d.rain.mean(), 1)})
        if day.day == 1:
            print("scored up to", day, flush=True)

    daily = pd.DataFrame(rows)
    sl = recorded_slides(grid, year).rename(columns={"event_date": "date"})
    daily = daily.merge(sl, on=["date", "district"], how="left").fillna({"slides": 0})
    daily["slides"] = daily.slides.astype(int)
    daily.to_csv(f"data/impact/monsoon_{year}_daily.csv", index=False)
    return daily


def recorded_slides_for(year):
    grid = pd.read_csv("data/live/grid_live.csv.gz", usecols=["lon", "lat", "district"])   # same cells and districts every year
    return recorded_slides(grid, year).rename(columns={"event_date": "date"})


def main():
    year = int(sys.argv[1])
    os.makedirs("data/impact", exist_ok=True)
    meta = json.load(open("models/rf_roads_live_v1_meta.json"))
    rule, features = meta["final_alert_rule"], meta["features_in_order"]

    path = f"data/impact/monsoon_{year}_daily.csv"
    if os.path.exists(path) and "--redo" not in sys.argv:   # reuse the scored days (scoring takes ~30 min)
        daily = pd.read_csv(path)
        print("using saved", path)
    else:
        daily = score_season(year, rule, features)
    sl = recorded_slides_for(year)
    cut = FIRST_REPLAY_DAY[year].isoformat()
    summ = pd.concat([summarise(daily, "whole monsoon"),
                      summarise(daily[daily.date >= cut], f"from {cut} (vegetation fully before each day)")])
    summ.to_csv(f"data/impact/monsoon_{year}_summary.csv", index=False)
    calendar(daily, year, f"docs/figures/monsoon_{year}_calendar.png")
    pd.set_option("display.width", 250)
    print(summ.to_string(index=False))
    print("recorded slides in districts outside the 12 (border cells):",
          int(sl[~sl.district.isin(daily.district.unique())].slides.sum()))


if __name__ == "__main__":
    main()
