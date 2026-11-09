"""Phase E, step 5: how certain is the replay choice? (diagnostic, chooses nothing)

PURPOSE
  phaseE_04 picks the candidate with the highest TSS on 44 storm-district
  checks and 192 quiet district-days. With so few days, close TSS values may
  not be truly different. This script resamples whole days with replacement
  (storm days and quiet days separately, 2,000 draws, fixed seed), since
  districts on one day share the same weather, and reports for each candidate:
    - the 95% interval of its TSS
    - how often it ranks first
    - the 95% interval of (its TSS - TSS of the chosen candidate)

INPUTS   same as phaseE_04 (data/phaseE/scores, replay_dates.csv, ...)
OUTPUTS  data/phaseE/replay_uncertainty.csv
RUN      .venv/Scripts/python -W ignore src/phaseE_05_replay_uncertainty.py
"""
import numpy as np
import pandas as pd

import phaseE_04_replay_evaluate as E

SEED, N_BOOT = 20261107, 2000


def main():
    rd = pd.read_csv("data/phaseE/replay_dates.csv")
    dates = sorted(rd.date.unique())
    sh = E.district_shares(dates, E.point_levels())
    grid = pd.read_csv(f"data/phaseE/scores/{dates[0]}.csv.gz", usecols=["lon", "lat", "district"])
    checks = E.slide_districts(rd[rd.role == "storm_day"].date, grid)
    checks["day_before"] = (pd.to_datetime(checks.event_date) - pd.Timedelta(days=1)).dt.strftime("%Y-%m-%d")
    quiet_days = rd[rd.role == "quiet_day"].date.tolist()
    districts = sorted(grid.district[grid.district != "unassigned"].unique())

    # Hit / alarm indicator per candidate, per check and per quiet district-day
    cands, H, A = [], [], []
    for m in E.OOF:
        for scope in E.SCOPES:
            x = sh[(sh.model == m) & (sh.scope == scope)].set_index(["date", "district"])["watch"]
            for s in E.SHARES:
                cands.append((m, scope, s))
                H.append([x.get((a, k), 0) >= s or x.get((b, k), 0) >= s
                          for a, b, k in zip(checks.event_date, checks.day_before, checks.district)])
                A.append([x.get((d, k), 0) >= s for d in quiet_days for k in districts])
    H, A = np.array(H, float), np.array(A, float)
    storm_of = checks.event_date.values
    quiet_of = np.repeat(quiet_days, len(districts))
    u_storm, u_quiet = np.unique(storm_of), np.array(quiet_days)
    idx_s = {d: np.where(storm_of == d)[0] for d in u_storm}
    idx_q = {d: np.where(quiet_of == d)[0] for d in u_quiet}

    tss0 = H.mean(1) - A.mean(1)
    best = int(np.argmax(tss0))   # same winner as phaseE_04 (ties aside)
    rng = np.random.default_rng(SEED)
    boot = np.empty((N_BOOT, len(cands)))
    for b in range(N_BOOT):
        si = np.concatenate([idx_s[d] for d in rng.choice(u_storm, len(u_storm))])
        qi = np.concatenate([idx_q[d] for d in rng.choice(u_quiet, len(u_quiet))])
        boot[b] = H[:, si].mean(1) - A[:, qi].mean(1)
    first = np.bincount(boot.argmax(1), minlength=len(cands)) / N_BOOT
    diff = boot - boot[:, [best]]
    res = pd.DataFrame([{"model": m, "scope": sc, "district_share": s, "TSS": tss0[i],
                         "TSS_low": np.percentile(boot[:, i], 2.5), "TSS_high": np.percentile(boot[:, i], 97.5),
                         "share_of_draws_ranked_first": first[i],
                         "diff_vs_chosen_low": np.percentile(diff[:, i], 2.5),
                         "diff_vs_chosen_high": np.percentile(diff[:, i], 97.5)}
                        for i, (m, sc, s) in enumerate(cands)]).sort_values("TSS", ascending=False)
    res.round(3).to_csv("data/phaseE/replay_uncertainty.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.round(3).head(12).to_string(index=False))


if __name__ == "__main__":
    main()
