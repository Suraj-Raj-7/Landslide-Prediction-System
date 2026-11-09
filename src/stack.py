"""Python mirror of GEE module Current/26_step7_feature_stack_module.

The full feature stack for the landslide warning system:
  static_image()        terrain + drainage/roads + lithology + faults + geomorphology
                        (does not change with date; 30 m UTM 43N grid for sampling)
  landcover_image()     WorldCover 2021 (sampled at its native 10 m)
  extract_features(points, date_field)
                        every feature for every point at its own date: works for
                        positives (event_date), negatives, or a live daily grid.
"""
import ee

import drainage_roads as DR
import dynamic as DY
import faults as FA
import geomorph as GM
import land_cover as LC
import lithology as LI
import terrain as TE
import vegetation as VG

CRS, SCALE = "EPSG:32643", 30
STREAM_KM2 = 2


def static_image(lith_csv):
    """Raster stack for map export (lithology/geomorphology painted at 30 m)."""
    return ee.Image.cat([TE.terrain_image(), DR.image(STREAM_KM2), LI.image(lith_csv),
                         FA.image(), GM.image()])


def _point_raster_image():
    """Static bands sampled from rasters (everything except the two polygon layers)."""
    return ee.Image.cat([TE.terrain_image(), DR.image(STREAM_KM2), FA.image()])


def _join_polygon(points, polys, props):
    """Exact point-in-polygon lookup (a 30 m pixel centre can fall across an edge)."""
    j = ee.Join.saveFirst("m").apply(points, polys, ee.Filter.intersects(
        leftField=".geo", rightField=".geo", maxError=1))

    def take(f):
        m = ee.Feature(f.get("m"))
        return f.set({p: m.get(p) for p in props}).set("m", None)

    joined = ee.FeatureCollection(j).map(take)
    missed = points.filter(ee.Filter.inList("id", joined.aggregate_array("id")).Not())         .map(lambda f: f.set({p: 0 for p in props}))
    return joined.merge(missed)


def static_bands():
    return TE.BANDS + DR.BANDS + LI.BANDS + FA.BANDS + GM.BANDS


def all_bands():
    return static_bands() + LC.BANDS + VG.BANDS + DY.BANDS + ["imerg_images_31d", "imerg_provisional_31d"]


def extract_static(points, lith_csv):
    """The fixed features only (terrain, drainage/roads, faults, lithology,
    geomorphology, land cover). Used for training via extract_features and,
    unchanged, for the live prediction grid. Points need a unique 'id'."""
    fc = _point_raster_image().reduceRegions(points, ee.Reducer.first(), SCALE, CRS)
    fc = _join_polygon(fc, LI.polygons(lith_csv), ["glim_code", "rock_code"])
    fc = _join_polygon(fc, GM.polygons(), ["gm_code"])
    return LC.image().reduceRegions(fc, ee.Reducer.first(), 10)


def extract_features(points, lith_csv, date_field="event_date"):
    """Every feature for every point at its own date. Points need a unique 'id'."""
    fc = extract_static(points, lith_csv)
    fc = VG.extract(fc, date_field, 30)
    fc = DY.extract(fc, date_field, 1000)
    return fc
