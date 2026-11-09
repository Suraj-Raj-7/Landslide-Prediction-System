"""Live system, step 2: the rain features for today (and tomorrow) for every HP cell.

WHAT THE MODEL NEEDS
  Seven IMERG rain features (definitions in src/dynamic.py), all built from
  rain totals per Indian day (IST, 00:00-24:00 = 18:30-18:30 UTC):
    imerg_d0        rain on the day
    imerg_antNd     rain in the N days before the day (N = 1, 3, 7, 15, 30)
    imerg_max1d_7d  wettest single day among the 7 days before
  plus the glacier flag era5_glacier.

THE PROBLEM
  IMERG reaches GEE about 1.5 days late (checked 9 Nov 2026: last image
  34 hours old). So "today" and the last day or so have no measured rain yet.

THE SOLUTION (design note §3, decided 24 Oct 2026)
  For every Indian day from 30 days before today up to tomorrow, the rain
  total is:
    measured IMERG rain for the part of the day IMERG already covers, plus
    GFS forecast rain for the rest. For each missing hour the NEWEST GFS run
    issued before that hour is used, because short-range forecasts are the
    most accurate; hours after the latest run come from that run.
  GFS gives rain as a running total that restarts every 6 hours (test of
  24 Oct 2026), so the rain in forecast hour h is the total at h minus the
  total at h-1, except in the first hour of each 6-hour block.
  The model was trained on measured rain only; forecast rain adds warning
  time but also errors. Each run reports how much of the inputs came from
  the forecast.

  Rain is read once per day at the native pixels (IMERG 0.1 deg, GFS 0.25 deg
  read at the IMERG pixel centres) and each cell gets the pixel that contains
  it, after snapping to the 1 km sampling grid used in training
  (reduceRegions, scale 1000). Checked identical to the training extraction
  (phaseE_03 check; check_against_training below).

  era5_glacier marks permanent glacier (snow water equivalent >= 9999 mm in
  ERA5-Land). ERA5-Land is about a week late, so the latest available day is
  used; the flag is a fixed glacier mask in practice (checked in
  check_glacier_static).
"""
import datetime as dt

import ee
import numpy as np
import pandas as pd

IMERG_COL = ee.ImageCollection("NASA/GPM_L3/IMERG_V07").select("precipitation")
GFS_COL = ee.ImageCollection("NOAA/GFS0P25")
ERA5L = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
HP_BOX = [75.4, 30.2, 79.2, 33.4]
IMERG_FEATURES = ["imerg_d0", "imerg_ant1d", "imerg_ant3d", "imerg_ant7d", "imerg_ant15d",
                  "imerg_ant30d", "imerg_max1d_7d"]
HOUR = dt.timedelta(hours=1)
IST = dt.timedelta(hours=5, minutes=30)


def ms(t):
    """UTC datetime (naive, meaning UTC) -> milliseconds since 1970, as GEE stores times.
    (datetime.timestamp() alone would read a naive time as laptop-local time.)"""
    return int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def ist_day_window(day):
    """UTC start and end of an Indian (IST) day."""
    start = dt.datetime.combine(day, dt.time()) - IST
    return start, start + dt.timedelta(days=1)


def imerg_last_end():
    """End time (UTC) of the last IMERG half-hour available in GEE."""
    t = IMERG_COL.filterDate((dt.datetime.utcnow() - dt.timedelta(days=10)).isoformat(),
                             (dt.datetime.utcnow() + dt.timedelta(days=1)).isoformat()) \
        .aggregate_max("system:time_start").getInfo()
    return dt.datetime.utcfromtimestamp(t / 1000) + dt.timedelta(minutes=30)


def complete_gfs_runs(since):
    """GFS runs (UTC creation times) issued after `since` with all 209 forecast steps in GEE."""
    col = GFS_COL.filterDate(since.isoformat(), (dt.datetime.utcnow() + dt.timedelta(days=1)).isoformat())
    hist = col.aggregate_histogram("creation_time").getInfo()   # {millis: number of images}
    return sorted(dt.datetime.utcfromtimestamp(int(float(k)) / 1000) for k, n in hist.items() if n >= 209)


def gfs_hour_mm(run, h):
    """GFS rain (mm) in forecast hour h of a run: (h-1, h]."""
    acc = GFS_COL.filter(ee.Filter.eq("creation_time", ms(run))) \
        .filter(ee.Filter.eq("forecast_hours", h)).first().select("total_precipitation_surface")
    if h % 6 == 1:      # first hour of a 6-hour block: running total restarted
        return acc
    prev = GFS_COL.filter(ee.Filter.eq("creation_time", ms(run))) \
        .filter(ee.Filter.eq("forecast_hours", h - 1)).first().select("total_precipitation_surface")
    return acc.subtract(prev)


def forecast_mm(start, end, runs):
    """GFS rain between start and end (UTC, on half-hours), from the newest run issued
    before each hour. Returns (image, list of (hour, run) used)."""
    img, used = ee.Image(0), []
    t = start.replace(minute=0)                     # hour slots [t, t+1h)
    while t < end:
        lo, hi = max(t, start), min(t + HOUR, end)
        w = (hi - lo) / HOUR                        # 1, or 0.5 for a half-covered hour
        if w > 0:
            run = max(r for r in runs if r <= t)    # newest run issued before this hour
            h = int((t + HOUR - run) / HOUR)
            img = img.add(gfs_hour_mm(run, h).multiply(w))
            used.append((t, run))
        t += HOUR
    return img, used


def daily_totals_image(days, t_last, runs):
    """One band per IST day: measured IMERG up to t_last, GFS forecast after it."""
    bands, forecast_hours, runs_used = [], 0.0, set()
    for d in days:
        s, e = ist_day_window(d)
        part = IMERG_COL.filterDate(s.isoformat(), min(e, t_last).isoformat()) \
            .map(lambda i: i.unmask(0)).sum().multiply(0.5) if s < t_last else ee.Image(0)
        if e > t_last:
            f, used = forecast_mm(max(s, t_last), e, runs)
            part = ee.Image(part).add(f)
            forecast_hours += (e - max(s, t_last)) / HOUR
            runs_used |= {r for _, r in used}
        bands.append(ee.Image(part).rename(d.strftime("d%Y%m%d")))
    return ee.Image.cat(bands), forecast_hours, sorted(runs_used)


def sample_pixels(img, proj):
    fc = img.sample(region=ee.Geometry.Rectangle(HP_BOX), projection=proj, geometries=True)
    df = ee.data.computeFeatures({"expression": fc, "fileFormat": "PANDAS_DATAFRAME"})
    xy = np.array([g["coordinates"] for g in df.geo])
    return df.drop(columns="geo"), xy


def to_cells(grid, values, xy):
    """Each cell takes the pixel that contains it (cells snapped to the 1 km training sampling grid)."""
    step = 1000 / 111319.490793
    cells = (np.floor(grid[["lon", "lat"]].values / step) + 0.5) * step
    near = np.empty(len(cells), int)
    for i in range(0, len(cells), 5000):            # in chunks, to keep memory small
        c = cells[i:i + 5000]
        near[i:i + 5000] = np.argmin((c[:, None, 0] - xy[None, :, 0]) ** 2 + (c[:, None, 1] - xy[None, :, 1]) ** 2, axis=1)
    return values.iloc[near].reset_index(drop=True)


def features_from_daily(daily, day):
    """The 7 rain features for `day` from a table of IST daily totals (columns dYYYYMMDD)."""
    col = lambda d: daily[d.strftime("d%Y%m%d")]  # noqa: E731
    before = lambda n: [day - dt.timedelta(days=k) for k in range(1, n + 1)]  # noqa: E731
    f = {"imerg_d0": col(day)}
    for n in [1, 3, 7, 15, 30]:
        f[f"imerg_ant{n}d"] = sum(col(d) for d in before(n))
    f["imerg_max1d_7d"] = pd.concat([col(d) for d in before(7)], axis=1).max(axis=1)
    return pd.DataFrame(f)


def glacier_flag(grid):
    """era5_glacier from the latest ERA5-Land day (same formula as dynamic.py)."""
    last = ERA5L.filterDate((dt.datetime.utcnow() - dt.timedelta(days=40)).isoformat(),
                            dt.datetime.utcnow().isoformat()).sort("system:time_start", False).first()
    swe = last.select("snow_depth_water_equivalent").multiply(1000).max(0)
    vals, xy = sample_pixels(swe.gte(9999).rename("era5_glacier"), ERA5L.first().projection())
    date = ee.Date(last.get("system:time_start")).format("YYYY-MM-dd").getInfo()
    return to_cells(grid, vals, xy)["era5_glacier"].values, date


def rain_features(grid, today, t_last=None):
    """Rain features for today and tomorrow for every cell, plus a summary of where the rain came from."""
    t_last = t_last or imerg_last_end()
    days = [today - dt.timedelta(days=k) for k in range(30, -2, -1)]   # today-30 .. tomorrow
    runs = complete_gfs_runs(t_last - dt.timedelta(days=2))
    need_gfs = ist_day_window(days[-1])[1] > t_last
    if need_gfs and not [r for r in runs if r <= t_last]:
        raise RuntimeError("no complete GFS run issued before the end of IMERG")
    img, fh, runs_used = daily_totals_image(days, t_last, runs)
    vals, xy = sample_pixels(img, IMERG_COL.first().projection())
    daily = to_cells(grid, vals, xy)
    out = {d: features_from_daily(daily, d) for d in [today, today + dt.timedelta(days=1)]}
    info = {"imerg_until_utc": t_last.isoformat(timespec="minutes"),
            "gfs_runs_used": [r.isoformat(timespec="minutes") for r in runs_used],
            "forecast_hours_in_31_days_up_to_tomorrow": fh,
            "today_rain_from_forecast_share": max(0.0, min(1.0, (ist_day_window(today)[1] - max(ist_day_window(today)[0], t_last)) / dt.timedelta(days=1)))}
    return out, daily, info


def check_against_training(grid_file="data/phaseD/storm_20230814_v2_features.csv", day=dt.date(2023, 8, 14)):
    """Measured-rain path vs the training extraction (14 Aug 2023 export): must be identical."""
    ref = pd.read_csv(grid_file)
    days = [day - dt.timedelta(days=k) for k in range(30, -1, -1)]
    img, _, _ = daily_totals_image(days, ist_day_window(day)[1], [])
    vals, xy = sample_pixels(img, IMERG_COL.first().projection())
    f = features_from_daily(to_cells(ref, vals, xy), day)
    for c in IMERG_FEATURES:
        d = (f[c].values - ref[c].values)
        print(f"{c}: cells differing by > 0.05 mm: {(np.abs(d) > 0.05).sum()} of {len(d)}; max {np.abs(d).max():.2f}")


if __name__ == "__main__":
    ee.Initialize(project="idyllic-return-468714-j4")
    check_against_training()
