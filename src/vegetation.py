"""Python mirror of GEE module Current/20_step5_vegetation_module.

image_for_date(date) -> ee.Image with:
  ndvi_pre365    median NDVI over the 365 days BEFORE date D (D-365 .. D-1),
                 Landsat 5/7/8/9 Collection 2 Level-2 surface reflectance,
                 clouds, shadows and snow removed with QA_PIXEL.
  ndvi_pre_n     number of clear Landsat observations in that window.
The window ends the day before the event, so a post-event landslide scar
cannot enter the feature (no leakage). Scaling: SR x 0.0000275 - 0.2 (USGS).
"""
import ee

BANDS = ["ndvi_pre365", "ndvi_pre_n"]
# (collection, red band, NIR band)
SENSORS = [("LANDSAT/LT05/C02/T1_L2", "SR_B3", "SR_B4"),
           ("LANDSAT/LE07/C02/T1_L2", "SR_B3", "SR_B4"),
           ("LANDSAT/LC08/C02/T1_L2", "SR_B4", "SR_B5"),
           ("LANDSAT/LC09/C02/T1_L2", "SR_B4", "SR_B5")]


def _ndvi(red, nir):
    def f(img):
        qa = img.select("QA_PIXEL")
        # bits: 0 fill, 1 dilated cloud, 3 cloud, 4 cloud shadow, 5 snow
        bad = qa.bitwiseAnd(0b111011).neq(0)
        r = img.select(red).multiply(0.0000275).add(-0.2)
        n = img.select(nir).multiply(0.0000275).add(-0.2)
        nd = n.subtract(r).divide(n.add(r)).rename("ndvi")
        valid = r.gt(0).And(n.gt(0))
        return nd.updateMask(bad.Not()).updateMask(valid).clamp(-1, 1)
    return f


def collection(start, end):
    parts = [ee.ImageCollection(c).filterDate(start, end).map(_ndvi(r, n)) for c, r, n in SENSORS]
    return parts[0].merge(parts[1]).merge(parts[2]).merge(parts[3])


def image_for_date(date):
    d = ee.Date(date)
    col = collection(d.advance(-365, "day"), d)          # end is exclusive: up to D-1
    return ee.Image.cat([col.median().rename("ndvi_pre365"),
                         col.count().rename("ndvi_pre_n")])


def extract(points, date_field="event_date", scale=30):
    dates = points.aggregate_array(date_field).distinct()

    def per_date(ds):
        pts = points.filter(ee.Filter.eq(date_field, ds))
        return image_for_date(ee.Date(ds)).reduceRegions(pts, ee.Reducer.first(), scale)

    return ee.FeatureCollection(dates.map(per_date)).flatten()
