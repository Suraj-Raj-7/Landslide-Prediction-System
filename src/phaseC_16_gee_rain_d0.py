"""Phase C, step 16: day-0 rain from GSMaP and IMERG (GEE) at the timing-test points.

PURPOSE
  Companion to phaseC_15 (PDIR-Now). For every landslide and same-place safe
  day (Type 1) this gets, from Google Earth Engine (read-only, no assets):
    gsmap_d0_ist   GSMaP v8 gauge-corrected (hourlyPrecipRateGC), IST day
    gsmap_d0_utc   same, UTC day (matches PDIR-Now's day)
    imerg_d0_utc   IMERG V07, UTC day (fair partner for PDIR-Now)
    imerg_d0_ist   IMERG V07, IST day; this must equal the table's imerg_d0
                   and is only a check that this code reads rain correctly.
  IST day D = D-1 18:30 UTC to D 18:30 UTC. UTC day D = D 00:00 to D+1 00:00.
  GSMaP is 0.1 deg like IMERG (not finer) but uses a different method and a
  daily rain-gauge correction, so it is a second opinion at the same scale.

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/rain_gee_d0.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_16_gee_rain_d0.py
"""
import ee

ee.Initialize(project="idyllic-return-468714-j4")
import time  # noqa: E402

import pandas as pd  # noqa: E402

GSMAP = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v8/operational").select("hourlyPrecipRateGC")
IMERG = ee.ImageCollection("NASA/GPM_L3/IMERG_V07").select("precipitation")
SCALE = 11132  # native 0.1 deg grid of both products
OUT = "data/phaseC/rain_gee_d0.csv"
STEP = 8


def total(coll, start, end, hours_per_image):
    """Rain total in mm between start and end (rates in mm/h times image length)."""
    return coll.filterDate(start, end).map(lambda i: i.unmask(0)).sum().multiply(hours_per_image)


def rain_image(date_str):
    d = ee.Date(date_str)
    ist_s, ist_e = d.advance(-5.5, "hour"), d.advance(18.5, "hour")
    utc_s, utc_e = d, d.advance(1, "day")
    return ee.Image.cat([
        total(GSMAP, ist_s, ist_e, 1).rename("gsmap_d0_ist"),
        total(GSMAP, utc_s, utc_e, 1).rename("gsmap_d0_utc"),
        total(IMERG, utc_s, utc_e, 0.5).rename("imerg_d0_utc"),
        total(IMERG, ist_s, ist_e, 0.5).rename("imerg_d0_ist"),
    ])


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    df = df[df.neg_type.isin(["positive", "same_place_safe_day"])]
    dates = sorted(df.event_date.unique())
    out = []
    # 8 dates per request: 40 failed with "Too many concurrent aggregations".
    for k in range(0, len(dates), STEP):
        feats = []
        for d in dates[k:k + STEP]:
            pts = df[df.event_date == d]
            fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([r.lon, r.lat]), {"id": r.id})
                                       for r in pts.itertuples()])
            feats.append(rain_image(d).reduceRegions(fc, ee.Reducer.first(), SCALE))
        for attempt in range(4):  # GEE sometimes refuses under load; wait and retry
            try:
                res = ee.FeatureCollection(feats).flatten().getInfo()["features"]
                break
            except ee.EEException as e:
                print(f"retry {attempt + 1}: {e}", flush=True)
                time.sleep(20)
        else:
            raise RuntimeError(f"GEE failed 4 times at dates {dates[k]}..")
        out += [f["properties"] for f in res]
        print(f"{min(k + STEP, len(dates))}/{len(dates)} dates", flush=True)
    res = pd.DataFrame(out)
    res.to_csv(OUT, index=False)
    print(res.describe().round(2).to_string())


if __name__ == "__main__":
    main()
