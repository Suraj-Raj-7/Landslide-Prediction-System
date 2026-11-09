"""Phase C, step 15: day-0 rain from PDIR-Now (0.04 deg, ~4 km) at the timing-test points.

PURPOSE
  Test whether a finer free rain product times landslides better than IMERG
  (0.1 deg, ~10 km). PDIR-Now (UC Irvine CHRS, infrared-based, no registration)
  is on a 0.04 deg grid. This script gets its day-0 rain at every landslide
  and every same-place safe day (Type 1) in the training table. The test
  itself is in phaseC_16.

DATA
  https://persiann.eng.uci.edu/CHRSdata/PDIRNow/PDIRNowdaily/pdirnow1dYYMMDD.bin.gz
  gzip of a 3000 x 9000 grid of LITTLE-endian float32 (checked: big-endian
  gives nonsense values), mm/day over the UTC day, 60N..60S, 0..360E,
  first pixel centred at 59.98N, 0.02E. NODATA = -9999 (negative values).

STORAGE
  Each daily file (~27 MB) is downloaded to a temporary folder, the needed
  points are read, and the file is deleted. Nothing large is kept. Results are
  appended per date, so the script can be stopped and restarted.

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/rain_pdirnow_d0.csv  (id, event_date, pdirnow_d0_utc)
RUN      .venv/Scripts/python -W ignore src/phaseC_15_pdirnow_extract.py TEMP_DIR
"""
import gzip
import os
import sys
import time
import urllib.request

import numpy as np
import pandas as pd

URL = "https://persiann.eng.uci.edu/CHRSdata/PDIRNow/PDIRNowdaily/pdirnow1d{}.bin.gz"
OUT = "data/phaseC/rain_pdirnow_d0.csv"
NROW, NCOL, RES = 3000, 9000, 0.04


def main():
    tmp = sys.argv[1]
    os.makedirs(tmp, exist_ok=True)
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    # Timing test rows only: landslides and the same places on safe days.
    df = df[df.neg_type.isin(["positive", "same_place_safe_day"])]
    done = set()
    if os.path.exists(OUT):
        # Dates where every point is empty are failed downloads (e.g. the
        # internet dropped on 6 Nov): remove them so they are fetched again.
        old = pd.read_csv(OUT)
        failed = old.groupby("event_date").pdirnow_d0_utc.apply(lambda s: s.isna().all())
        old[~old.event_date.isin(failed[failed].index)].to_csv(OUT, index=False)
        done = set(failed[~failed].index)
    dates = sorted(set(df.event_date) - done)
    print(f"{len(dates)} dates to fetch ({len(done)} already done)", flush=True)
    for i, d in enumerate(dates):
        t0 = time.time()
        path = os.path.join(tmp, "day.bin.gz")
        url = URL.format(pd.Timestamp(d).strftime("%y%m%d"))
        grid = None
        for attempt in range(3):  # retry short network drops
            try:
                urllib.request.urlretrieve(url, path)
                grid = np.frombuffer(gzip.open(path).read(), dtype="<f4").reshape(NROW, NCOL)
                break
            except Exception as e:  # still failing after 3 tries: recorded as NaN, retried next run
                print(f"{d}: attempt {attempt + 1} failed ({e})", flush=True)
                time.sleep(30)
        pts = df[df.event_date == d]
        rows = np.floor((60 - pts.lat.values) / RES).astype(int)
        cols = np.floor((pts.lon.values % 360) / RES).astype(int)
        vals = grid[rows, cols].astype(float) if grid is not None else np.full(len(pts), np.nan)
        vals[vals < 0] = np.nan  # NODATA
        pd.DataFrame({"id": pts.id.values, "event_date": d, "pdirnow_d0_utc": vals}).to_csv(
            OUT, mode="a", header=not os.path.exists(OUT), index=False)
        if os.path.exists(path):
            os.remove(path)
        print(f"{i + 1}/{len(dates)} {d} {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
