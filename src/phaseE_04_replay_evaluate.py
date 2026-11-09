"""Phase E, step 4: apply the replay rule and choose the model and district rule.

PURPOSE
  Applies the selection rule written in documentation §17.10 on 6 Nov 2026,
  before any replay was scored:
    hit           a district with a recorded slide on a storm day is at Watch
                  or higher on that day or the day before (44 checks)
    false alarm   a district is at Watch or higher on a quiet day
                  (12 districts x 16 quiet days = 192 district-days)
    TSS           hit rate - false-alarm rate (Peirce skill score)
  Candidates: model (rf, 2p) x district share (1-30%) x cells counted
  (all cells, or only cells within 500 m of a road). Road-neutral scores
  (the main map). The highest TSS wins; ties go to fewer false alarms, then
  to "all cells".

  Point levels per model are those used for the storm map (phaseD_03): the
  scores at which the HP same-place safe days are flagged at the live
  levels' rates (Watch 25.6%, Warning 13.3%), from year-blocked out-of-fold
  scores. The Warning tier uses the chosen district share on Warning cells
  and is reported, not optimised.

INPUTS   data/phaseE/scores/*.csv.gz (phaseE_03), data/phaseE/replay_dates.csv,
         data/positives_features_v1_local.csv,
         data/phaseC/road_neutral_oof.csv, data/phaseC/two_part_oof.csv
OUTPUTS  data/phaseE/replay_candidates.csv  (every candidate with hits, false alarms, TSS)
         data/phaseE/replay_storm_checks.csv (each of the 44 checks under the chosen rule)
         data/phaseE/replay_quiet_days.csv   (each quiet district-day under the chosen rule)
RUN      .venv/Scripts/python -W ignore src/phaseE_04_replay_evaluate.py
"""
import numpy as np
import pandas as pd

SHARES = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30]
SCOPES = {"all_cells": None, "road_zone": 500}
SAFE_DAY_FA_HP = {"watch": 0.256, "warning": 0.133}
OOF = {"rf": ("data/phaseC/road_neutral_oof.csv", ["rf_28_live__neutral"]),
       "2p": ("data/phaseC/two_part_oof.csv", ["live_LR__where_neutral", "live_LR__when"])}


def point_levels():
    """Watch and Warning score levels per model (same method as phaseD_03)."""
    thr = {}
    for m, (f, cols) in OOF.items():
        o = pd.read_csv(f)
        safe = (o.state == "HP") & (o.neg_type == "same_place_safe_day")
        s = np.prod([o.loc[safe, c].values for c in cols], axis=0)
        thr[m] = {lv: float(np.quantile(s, 1 - fa)) for lv, fa in SAFE_DAY_FA_HP.items()}
    return thr


def district_shares(dates, thr):
    """Share of cells at Watch+ and at Warning per date, district, model and scope."""
    rows = []
    for d in dates:
        g = pd.read_csv(f"data/phaseE/scores/{d}.csv.gz")
        g = g[g.district != "unassigned"]
        for scope, max_road in SCOPES.items():
            gg = g if max_road is None else g[g.dist_road_m <= max_road]
            for m in OOF:
                s = gg[f"{m}_neutral"]
                tmp = pd.DataFrame({"district": gg.district, "watch": s >= thr[m]["watch"],
                                    "warning": s >= thr[m]["warning"]})
                agg = tmp.groupby("district")[["watch", "warning"]].mean().reset_index()
                agg["date"], agg["model"], agg["scope"] = d, m, scope
                rows.append(agg)
    return pd.concat(rows, ignore_index=True)


def slide_districts(storm_days, grid):
    """District of each recorded HP slide on the storm days (nearest grid cell)."""
    p = pd.read_csv("data/positives_features_v1_local.csv")
    s = p[(p.state == "HP") & p.event_date.isin(storm_days)].copy()
    s["district"] = [grid.district.values[np.argmin((grid.lon.values - a) ** 2 + (grid.lat.values - b) ** 2)]
                     for a, b in zip(s.lon, s.lat)]
    return s.groupby(["event_date", "district"]).size().rename("slides").reset_index()


def main():
    rd = pd.read_csv("data/phaseE/replay_dates.csv")
    dates = sorted(rd.date.unique())
    thr = point_levels()
    print("point levels:", {m: {k: round(v, 3) for k, v in t.items()} for m, t in thr.items()})
    sh = district_shares(dates, thr)
    grid = pd.read_csv(f"data/phaseE/scores/{dates[0]}.csv.gz", usecols=["lon", "lat", "district"])
    checks = slide_districts(rd[rd.role == "storm_day"].date, grid)
    checks["day_before"] = (pd.to_datetime(checks.event_date) - pd.Timedelta(days=1)).dt.strftime("%Y-%m-%d")
    quiet_days = rd[rd.role == "quiet_day"].date.tolist()
    districts = sorted(grid.district[grid.district != "unassigned"].unique())
    quiet = pd.DataFrame([(d, k) for d in quiet_days for k in districts], columns=["date", "district"])
    print(f"{len(checks)} storm-district checks, {len(quiet)} quiet district-days")

    rows, detail = [], {}
    for m in OOF:
        for scope in SCOPES:
            x = sh[(sh.model == m) & (sh.scope == scope)].set_index(["date", "district"])
            for s in SHARES:
                def at(d, k, lv):   # district at this level on date d? (no cells in scope -> no)
                    return bool(x[lv].get((d, k), 0) >= s)
                c = checks.copy()
                for lv in ["watch", "warning"]:
                    c[f"{lv}_hit"] = [at(a, k, lv) or at(b, k, lv) for a, b, k in zip(c.event_date, c.day_before, c.district)]
                q = quiet.copy()
                for lv in ["watch", "warning"]:
                    q[f"{lv}_alarm"] = [at(a, k, lv) for a, k in zip(q.date, q.district)]
                hr, far = c.watch_hit.mean(), q.watch_alarm.mean()
                rows.append({"model": m, "scope": scope, "district_share": s,
                             "watch_hits": int(c.watch_hit.sum()), "watch_hit_rate": hr,
                             "watch_false_alarms": int(q.watch_alarm.sum()), "watch_false_alarm_rate": far,
                             "watch_TSS": hr - far,
                             "warning_hits": int(c.warning_hit.sum()), "warning_hit_rate": c.warning_hit.mean(),
                             "warning_false_alarms": int(q.warning_alarm.sum()),
                             "warning_false_alarm_rate": q.warning_alarm.mean(),
                             "warning_TSS": c.warning_hit.mean() - q.warning_alarm.mean()})
                detail[(m, scope, s)] = (c, q)

    res = pd.DataFrame(rows)
    # Selection rule (§17.10): highest Watch TSS; ties -> fewer false alarms -> all cells
    res["scope_order"] = (res.scope != "all_cells").astype(int)
    res = res.sort_values(["watch_TSS", "watch_false_alarms", "scope_order"], ascending=[False, True, True])
    res["chosen"] = False
    res.iloc[0, res.columns.get_loc("chosen")] = True
    res = res.drop(columns="scope_order")
    res.round(3).to_csv("data/phaseE/replay_candidates.csv", index=False)
    best = res.iloc[0]
    c, q = detail[(best.model, best.scope, best.district_share)]
    c.to_csv("data/phaseE/replay_storm_checks.csv", index=False)
    q.to_csv("data/phaseE/replay_quiet_days.csv", index=False)
    pd.set_option("display.width", 220)
    print(res.round(3).to_string(index=False))
    print("\nchosen:", best[["model", "scope", "district_share", "watch_hits", "watch_false_alarms", "watch_TSS"]].to_dict())


if __name__ == "__main__":
    main()
