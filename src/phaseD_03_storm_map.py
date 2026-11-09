"""Phase D, step 3: whole-HP risk map for one past storm day.

PURPOSE
  Shows the system working on a real disaster day: every 1 km cell of HP is
  scored, cells are put at Watch / Warning, districts get a level, and the
  landslides recorded that day are plotted on top.

  Honest test: the model used here is the live model (28 features, same
  recipe) trained WITHOUT any rows from the storm's year, exactly as in the
  year-blocked cross-validation. The production model has seen this storm,
  so using it would overstate skill.

  Two layers (decision of 5 Nov 2026):
    main map     road-neutral: both road distances set to the median of the
                 training positives ("as if observed like a roadside slope");
    second map   real road distances: "where slides are likely to hit roads".
  Cells more than 500 m from a motorable road are marked lower confidence.

  Levels (provisional): for each layer, the score at which the same share of
  HP same-place safe days is flagged as with the live model's levels
  (Watch: 25.6%, Warning: 13.3%), taken from the year-blocked out-of-fold
  scores in data/phaseC/road_neutral_oof.csv. District rule (provisional):
  a district is at a level when at least 5% of its cells reach it.

INPUTS   users/rajsuraj777/storm_<YYYYMMDD>_a ... _h (phaseD_02),
         data/phaseB/training_table_v1.csv, data/phaseC/road_neutral_oof.csv,
         data/positives_features_v1_local.csv (recorded slides)
OUTPUTS  data/phaseD/storm_<YYYYMMDD>_features.csv (cached download),
         data/phaseD/storm_<YYYYMMDD>_scores.csv, data/phaseD/storm_<YYYYMMDD>_districts.csv,
         data/phaseD/storm_<YYYYMMDD>_slides.csv,
         docs/figures/storm_<YYYYMMDD>_road_neutral.png, docs/figures/storm_<YYYYMMDD>_real_roads.png,
         docs/figures/storm_<YYYYMMDD>_rain.png
RUN      .venv/Scripts/python -W ignore src/phaseD_03_storm_map.py 2023-08-14
"""
import json
import os
import sys

import ee
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from phaseC_01_train_compare import CAT, ROAD, make_model
from phaseC_11_two_part_model import IMERG

ee.Initialize(project="idyllic-return-468714-j4")

# Usage: phaseD_03_storm_map.py DATE [DATA_SUFFIX] [--two-part]
#   DATA_SUFFIX selects the storm-day assets (e.g. "_v2": border cells kept);
#   --two-part scores with the WHERE x WHEN model (phaseC_11) instead of the
#   single live model. Outputs get the suffix and "_two_part" in their names.
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DATE = ARGS[0]
DATA_TAG = DATE.replace("-", "") + (ARGS[1] if len(ARGS) > 1 else "")
TWO_PART = "--two-part" in sys.argv
TAG = DATA_TAG + ("_two_part" if TWO_PART else "")
YEAR = int(DATE[:4])
SAFE_DAY_FA_HP = {"watch": 0.256, "warning": 0.133}   # HP safe-day false alarms of the live levels
DISTRICT_SHARE = 0.05
LOW_CONF_M = 500
HP_DISTRICTS = ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahul & Spiti",
                "Mandi", "Shimla", "Sirmaur", "Solan", "Una"]
COLORS = {"none": "#d9d9d9", "watch": "#f4a261", "warning": "#c0392b"}


def load_features():
    """Download the 8 storm-day strips once and cache them as CSV."""
    path = f"data/phaseD/storm_{DATA_TAG}_features.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    parts = []
    for c in "abcdefgh":
        fc = ee.FeatureCollection(f"users/rajsuraj777/storm_{DATA_TAG}_{c}")
        parts.append(ee.data.computeFeatures({"expression": fc, "fileFormat": "PANDAS_DATAFRAME"}))
        print("downloaded strip", c, len(parts[-1]), flush=True)
    df = pd.concat(parts, ignore_index=True)
    df.drop(columns=[c for c in df.columns if c == "geo"], errors="ignore").to_csv(path, index=False)
    return df


def level(p, thr):
    return np.where(p >= thr["warning"], "warning", np.where(p >= thr["watch"], "watch", "none"))


def district_polygons():
    hp = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1") \
        .filter(ee.Filter.eq("shapeID", "1811400B21086746745937")).first().geometry()
    d = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM2").filterBounds(hp) \
        .filter(ee.Filter.inList("shapeName", HP_DISTRICTS)).map(lambda f: f.simplify(300))
    return d.getInfo()["features"]


def draw_districts(ax, polys, levels=None):
    def polygons_of(g):
        """Polygon / MultiPolygon / GeometryCollection -> list of polygons (list of rings)."""
        if g["type"] == "Polygon":
            return [g["coordinates"]]
        if g["type"] == "MultiPolygon":
            return g["coordinates"]
        if g["type"] == "GeometryCollection":
            return [p for sub in g["geometries"] for p in polygons_of(sub)]
        return []                                   # lines/points left over from simplifying

    for f in polys:
        rings = polygons_of(f["geometry"])
        if not rings:
            continue
        name = f["properties"]["shapeName"]
        for poly in rings:
            xy = np.array(poly[0])
            ax.plot(xy[:, 0], xy[:, 1], color="black", lw=0.6)
        if levels is not None:
            cx, cy = np.array(rings[0][0]).mean(axis=0)
            lv = levels.get(name, "none")
            ax.text(cx, cy, f"{name}\n{lv.upper() if lv != 'none' else ''}", fontsize=6.5, ha="center",
                    va="center", color="black", bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.5))


def main():
    os.makedirs("data/phaseD", exist_ok=True)
    os.makedirs("docs/figures", exist_ok=True)
    meta = json.load(open("models/rf_roads_live_v1_meta.json"))
    features = meta["features_in_order"]
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]

    # ---- held-out-year model(s) (no rows from the storm's year) ----
    t = pd.read_csv("data/phaseB/training_table_v1.csv")
    train = t[pd.to_datetime(t.event_date).dt.year != YEAR]
    road_median = train[train.label == 1][ROAD].median()
    if TWO_PART:
        # WHERE: slides vs other slopes on storm days; WHEN: slides vs safe days, log-rain logistic
        where = [c for c in features if c not in IMERG]
        trw = train[train.neg_type.isin(["positive", "similar_place_storm_day"])]
        trn = train[train.neg_type.isin(["positive", "same_place_safe_day"])]
        m_where = make_model("random_forest", [c for c in where if c not in CAT], [c for c in where if c in CAT]) \
            .fit(trw[where], trw.label)
        m_when = make_model("logistic", IMERG, []).fit(trn[IMERG], trn.label)

        def score(X):
            return m_where.predict_proba(X[where])[:, 1] * m_when.predict_proba(X[IMERG])[:, 1]
        oof_file, cols = "data/phaseC/two_part_oof.csv", {"road_neutral": ("live_LR__where_neutral", "live_LR__when"),
                                                           "real_roads": ("live_LR__where", "live_LR__when")}
    else:
        model = make_model("random_forest", num, cat).fit(train[features], train.label)

        def score(X):
            return model.predict_proba(X[features])[:, 1]
        oof_file, cols = "data/phaseC/road_neutral_oof.csv", {"road_neutral": ("rf_28_live__neutral",),
                                                               "real_roads": ("rf_28_live__real",)}
    print(f"{'two-part' if TWO_PART else 'single'} model trained without {YEAR}: {len(train)} rows; "
          f"road medians {road_median.round(0).to_dict()}")

    # ---- levels per layer, matched to the live levels' HP safe-day false alarms ----
    oof = pd.read_csv(oof_file)
    hp_safe = (oof.state == "HP") & (oof.neg_type == "same_place_safe_day")
    thr = {}
    for layer, cs in cols.items():
        s = np.prod([oof.loc[hp_safe, c].values for c in cs], axis=0)
        thr[layer] = {lv: float(np.quantile(s, 1 - fa)) for lv, fa in SAFE_DAY_FA_HP.items()}
    print("levels:", {k: {a: round(b, 3) for a, b in v.items()} for k, v in thr.items()})

    # ---- score every HP cell ----
    g = load_features()
    print("grid points:", len(g), "| unassigned district:", int((g.district == "unassigned").sum()))
    g["score_real_roads"] = score(g)
    gn = g.copy()
    for c in ROAD:
        gn[c] = road_median[c]
    g["score_road_neutral"] = score(gn)
    g["lower_confidence"] = g.dist_road_m > LOW_CONF_M
    for layer in ["road_neutral", "real_roads"]:
        g[f"level_{layer}"] = level(g[f"score_{layer}"].values, thr[layer])
    g[["id", "lon", "lat", "district", "dist_road_m", "lower_confidence", "imerg_d0", "imerg_ant7d",
       "score_road_neutral", "level_road_neutral", "score_real_roads", "level_real_roads"]] \
        .round(4).to_csv(f"data/phaseD/storm_{TAG}_scores.csv", index=False)

    # ---- districts ----
    drows = []
    # District levels only for the 12 real districts; border cells outside
    # every district outline ("unassigned") stay on the map but get no level
    for name, d in g[g.district != "unassigned"].groupby("district"):
        row = {"district": name, "cells": len(d), "rain_on_day_mean_mm": d.imerg_d0.mean()}
        for layer in ["road_neutral", "real_roads"]:
            w = (d[f"level_{layer}"] != "none").mean()
            wr = (d[f"level_{layer}"] == "warning").mean()
            row[f"{layer}_share_watch_or_above"] = w
            row[f"{layer}_share_warning"] = wr
            row[f"{layer}_district_level"] = "warning" if wr >= DISTRICT_SHARE else ("watch" if w >= DISTRICT_SHARE else "none")
        drows.append(row)
    dist = pd.DataFrame(drows).round(3)

    # ---- recorded slides that day (HP), matched to the nearest grid cell ----
    pos = pd.read_csv("data/positives_features_v1_local.csv")
    sl = pos[(pos.state == "HP") & (pos.event_date == DATE)].copy()
    gx, gy = g.lon.values, g.lat.values
    idx = [int(np.argmin((gx - r.lon) ** 2 + (gy - r.lat) ** 2)) for r in sl.itertuples()]
    for c in ["district", "level_road_neutral", "level_real_roads", "score_road_neutral", "score_real_roads"]:
        sl[c] = g[c].values[idx]
    sl[["id", "lat", "lon", "district", "score_road_neutral", "level_road_neutral",
        "score_real_roads", "level_real_roads"]].round(4).to_csv(f"data/phaseD/storm_{TAG}_slides.csv", index=False)
    slides_per_district = sl.groupby("district").size()
    dist["recorded_slides"] = dist.district.map(slides_per_district).fillna(0).astype(int)
    dist.to_csv(f"data/phaseD/storm_{TAG}_districts.csv", index=False)

    pd.set_option("display.width", 220)
    print(dist.to_string(index=False))
    for layer in ["road_neutral", "real_roads"]:
        lv = sl[f"level_{layer}"]
        dl = sl.district.map(dist.set_index("district")[f"{layer}_district_level"])
        print(f"{layer}: slides in cells at watch+ {int((lv != 'none').sum())}/{len(sl)}, warning {int((lv == 'warning').sum())}; "
              f"slides in districts at watch+ {int((dl != 'none').sum())}/{len(sl)}")
        print(f"   cells at watch+ {(g[f'level_{layer}'] != 'none').mean():.3f}, warning {(g[f'level_{layer}'] == 'warning').mean():.3f}")

    # ---- maps ----
    polys = district_polygons()
    titles = {"road_neutral": "Risk, road-neutral (main map)", "real_roads": "Risk with real road distances (where slides may hit roads)"}
    for layer in ["road_neutral", "real_roads"]:
        fig, ax = plt.subplots(figsize=(8.5, 8))
        for lv in ["none", "watch", "warning"]:
            m = g[f"level_{layer}"] == lv
            hi = m & ~g.lower_confidence
            lo = m & g.lower_confidence
            ax.scatter(g.lon[hi], g.lat[hi], s=3, c=COLORS[lv], marker="s", lw=0,
                       label=f"{lv.capitalize() if lv != 'none' else 'No alert'}")
            ax.scatter(g.lon[lo], g.lat[lo], s=3, c=COLORS[lv], marker="s", lw=0, alpha=0.45)
        dlev = dist.set_index("district")[f"{layer}_district_level"].to_dict()
        draw_districts(ax, polys, dlev)
        ax.scatter(sl.lon, sl.lat, s=28, facecolor="none", edgecolor="#1d3557", lw=1.2, label=f"Recorded slides ({len(sl)})")
        ax.set_title(f"{DATE}: {titles[layer]}\nModel trained without {YEAR}; faded cells: > {LOW_CONF_M} m from a road (lower confidence)", fontsize=9)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.legend(loc="lower left", fontsize=7, markerscale=3)
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(f"docs/figures/storm_{TAG}_{layer}.png", dpi=170)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 8))
    sc = ax.scatter(g.lon, g.lat, c=g.imerg_d0, s=3, marker="s", lw=0, cmap="Blues")
    draw_districts(ax, polys)
    ax.scatter(sl.lon, sl.lat, s=28, facecolor="none", edgecolor="#c0392b", lw=1.2, label="Recorded slides")
    plt.colorbar(sc, ax=ax, label="Rain on the day (mm, IMERG)", shrink=0.7)
    ax.set_title(f"{DATE}: rain on the day (IMERG, IST day)", fontsize=9)
    ax.set_aspect("equal")
    ax.legend(loc="lower left", fontsize=7)
    fig.tight_layout()
    fig.savefig(f"docs/figures/storm_{TAG}_rain.png", dpi=170)
    print("figures saved")


if __name__ == "__main__":
    main()
