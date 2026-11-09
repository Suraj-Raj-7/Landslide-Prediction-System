"""Python mirror of GEE module Current/18_step6_dynamic_module.

image_for_date(date) returns one ee.Image with the daily-changing features for
a given event (or forecast) date D (local calendar date, India Standard Time):

  Rainfall, GPM IMERG V07 (half-hourly, ~11 km; 'precipitation' in mm/h x 0.5 h):
    imerg_d0          rain on day D, 00:00-24:00 IST (= D-1 18:30 to D 18:30 UTC)
    imerg_ant{N}d     rain in the N days BEFORE day D (N = 1, 3, 7, 15, 30)
    imerg_max1d_7d    wettest single IST day in the 7 days before D
  Rainfall, CHIRPS daily (~5.5 km; calendar days as distributed):
    chirps_d0, chirps_ant{N}d   same windows on CHIRPS days
  Soil and snow state, ERA5-Land daily aggregates (~11 km), day D-1:
    sm_l1_dm1         volumetric soil water 0-7 cm (m3/m3)
    sm_l2_dm1         volumetric soil water 7-28 cm (m3/m3)
    swe_dm1_mm        snow water equivalent (mm); EMPTY on ERA5-Land permanent-glacier
                      cells, which hold a fixed 10,000 mm placeholder on every date
    era5_glacier      1 on those glacier cells, else 0
    snowmelt_ant7d_mm snowmelt in the 7 days before D (mm)

Day 0 is kept separate from the antecedent windows (which end at the start of
day D), so "today's rain" and "rain before today" are distinct features.
image metadata: imerg_images_31d (expected 1488) and imerg_provisional_31d
(images from the provisional stream; GEE holds final IMERG to 2025-09-30).
"""
import ee

IMERG = ee.ImageCollection("NASA/GPM_L3/IMERG_V07").select("precipitation")
CHIRPS = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").select("precipitation")
ERA5L = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
WINDOWS = [1, 3, 7, 15, 30]
IST_OFFSET_H = 5.5
BANDS = (["imerg_d0"] + [f"imerg_ant{n}d" for n in WINDOWS] + ["imerg_max1d_7d"] +
         ["chirps_d0"] + [f"chirps_ant{n}d" for n in WINDOWS] +
         ["sm_l1_dm1", "sm_l2_dm1", "swe_dm1_mm", "snowmelt_ant7d_mm", "era5_glacier"])


def _imerg_mm(start, end):
    # half-hourly rate (mm/h) x 0.5 h = mm; unmask(0) keeps a pixel valid if
    # one half-hour is masked (missing images are counted separately)
    return IMERG.filterDate(start, end).map(lambda i: i.unmask(0)).sum().multiply(0.5)


def image_for_date(date):
    d = ee.Date(date)                                   # local date at 00:00
    d0s = d.advance(-IST_OFFSET_H, "hour")              # 00:00 IST in UTC
    d0e = d0s.advance(1, "day")
    bands = [_imerg_mm(d0s, d0e).rename("imerg_d0")]
    bands += [_imerg_mm(d0s.advance(-n, "day"), d0s).rename(f"imerg_ant{n}d") for n in WINDOWS]
    daily7 = ee.ImageCollection([_imerg_mm(d0s.advance(-k, "day"), d0s.advance(-k + 1, "day"))
                                 for k in range(1, 8)])
    bands.append(daily7.max().rename("imerg_max1d_7d"))
    bands.append(CHIRPS.filterDate(d, d.advance(1, "day")).sum().rename("chirps_d0"))
    bands += [CHIRPS.filterDate(d.advance(-n, "day"), d).sum().rename(f"chirps_ant{n}d") for n in WINDOWS]
    e_dm1 = ERA5L.filterDate(d.advance(-1, "day"), d).first()
    swe = e_dm1.select("snow_depth_water_equivalent").multiply(1000).max(0)
    glacier = swe.gte(9999)
    bands += [e_dm1.select("volumetric_soil_water_layer_1").rename("sm_l1_dm1"),
              e_dm1.select("volumetric_soil_water_layer_2").rename("sm_l2_dm1"),
              swe.updateMask(glacier.Not()).rename("swe_dm1_mm"),
              ERA5L.filterDate(d.advance(-7, "day"), d).select("snowmelt_sum").sum()
              .multiply(1000).max(0).rename("snowmelt_ant7d_mm"),
              glacier.rename("era5_glacier")]
    win = IMERG.filterDate(d0s.advance(-30, "day"), d0e)
    return ee.Image.cat(bands).set({
        "imerg_images_31d": win.size(),
        "imerg_provisional_31d": ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
        .filterDate(d0s.advance(-30, "day"), d0e).filter(ee.Filter.eq("status", "provisional")).size(),
    })


def extract(points, date_field="event_date", scale=1000):
    """Sample image_for_date(point date) at every point; groups points by date."""
    dates = points.aggregate_array(date_field).distinct()

    def per_date(ds):
        img = image_for_date(ee.Date(ds))
        pts = points.filter(ee.Filter.eq(date_field, ds))
        return img.reduceRegions(pts, ee.Reducer.first(), scale).map(
            lambda f: f.set({"imerg_images_31d": img.get("imerg_images_31d"),
                             "imerg_provisional_31d": img.get("imerg_provisional_31d")}))

    return ee.FeatureCollection(dates.map(per_date)).flatten()
