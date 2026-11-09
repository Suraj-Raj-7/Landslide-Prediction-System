"""Phase D, step 4: storm day vs quiet day, side by side.

PURPOSE
  A warning system must tell a disaster day from a quiet day. This figure
  puts the whole-HP maps of the two days next to each other: rain on the day
  (top) and the road-neutral risk levels of the live model (bottom), both
  days scored by the same model trained without 2023 and with the same
  provisional levels (phaseD_03_storm_map.py).

  Storm day: 14 Aug 2023 (31 recorded HP slides).
  Quiet day: 12 Sep 2023 (no recorded HP slide within +/-10 days, none in
  the three states within +/-3 days).

  Caveat stated on the figure: the quiet day was also nearly dry (HP mean
  rain 0.8 mm), so it shows that the system stays calm on a dry day; the
  harder test, wet days without slides, comes from the storm replays.

INPUTS   data/phaseD/storm_20230814_v2_scores.csv, storm_20230912_v2_scores.csv
         (and the matching _two_part files with --two-part)
OUTPUTS  docs/figures/storm_vs_quiet_20230814_20230912[_two_part].png
RUN      .venv/Scripts/python -W ignore src/phaseD_04_storm_vs_quiet_figure.py [--two-part]
"""
import sys

import ee
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ee.Initialize(project="idyllic-return-468714-j4")

SUFFIX = "_two_part" if "--two-part" in sys.argv else ""
DAYS = [("2023-08-14", "Storm day, 14 Aug 2023"), ("2023-09-12", "Quiet day, 12 Sep 2023")]
COLORS = {"none": "#d9d9d9", "watch": "#f4a261", "warning": "#c0392b"}
HP_DISTRICTS = ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahul & Spiti",
                "Mandi", "Shimla", "Sirmaur", "Solan", "Una"]


def district_outlines():
    hp = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1") \
        .filter(ee.Filter.eq("shapeID", "1811400B21086746745937")).first().geometry()
    d = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM2").filterBounds(hp) \
        .filter(ee.Filter.inList("shapeName", HP_DISTRICTS)).map(lambda f: f.simplify(300))
    rings = []

    def polys(g):
        if g["type"] == "Polygon":
            return [g["coordinates"]]
        if g["type"] == "MultiPolygon":
            return g["coordinates"]
        if g["type"] == "GeometryCollection":
            return [p for s in g["geometries"] for p in polys(s)]
        return []
    for f in d.getInfo()["features"]:
        rings += [np.array(p[0]) for p in polys(f["geometry"])]
    return rings


def main():
    rings = district_outlines()
    pos = pd.read_csv("data/positives_features_v1_local.csv")
    fig, axes = plt.subplots(2, 2, figsize=(13, 11.5))
    for col, (date, title) in enumerate(DAYS):
        g = pd.read_csv(f"data/phaseD/storm_{date.replace('-', '')}_v2{SUFFIX}_scores.csv")
        d = pd.read_csv(f"data/phaseD/storm_{date.replace('-', '')}_v2{SUFFIX}_districts.csv")
        sl = pos[(pos.state == "HP") & (pos.event_date == date)]
        lv = g.level_road_neutral
        # top: rain
        ax = axes[0, col]
        sc = ax.scatter(g.lon, g.lat, c=g.imerg_d0, s=2, marker="s", lw=0, cmap="Blues", vmin=0, vmax=120)
        ax.set_title(f"{title}\nRain on the day (IMERG): HP mean {g.imerg_d0.mean():.1f} mm", fontsize=10)
        # bottom: risk levels
        ax2 = axes[1, col]
        for level in ["none", "watch", "warning"]:
            m = lv == level
            ax2.scatter(g.lon[m], g.lat[m], s=2, marker="s", lw=0, c=COLORS[level],
                        label={"none": "No alert", "watch": "Watch", "warning": "Warning"}[level])
        n_w = int((d.road_neutral_district_level == "warning").sum())
        n_a = int((d.road_neutral_district_level == "watch").sum())
        ax2.set_title(f"Risk levels (road-neutral): Watch+ {(lv != 'none').mean():.1%} of HP, "
                      f"Warning {(lv == 'warning').mean():.1%}\nDistricts: {n_w} at Warning, {n_a} at Watch (of 12)",
                      fontsize=10)
        for a in (ax, ax2):
            for r in rings:
                a.plot(r[:, 0], r[:, 1], color="black", lw=0.5)
            if len(sl):
                a.scatter(sl.lon, sl.lat, s=26, facecolor="none", edgecolor="#1d3557", lw=1.1,
                          label=f"Recorded slides ({len(sl)})" if a is ax2 else None)
            a.set_aspect("equal")
            a.set_xticks([])
            a.set_yticks([])
        ax2.legend(loc="lower left", fontsize=8, markerscale=4)
    fig.colorbar(sc, ax=axes[0, :], shrink=0.6, label="Rain on the day (mm)")
    model = "two-part live model" if SUFFIX else "live model"
    fig.suptitle(f"Same {model}, trained without 2023, same provisional levels. "
                 "Quiet day was also nearly dry: wet days without slides are tested in the storm replays.",
                 fontsize=10)
    out = f"docs/figures/storm_vs_quiet_20230814_20230912{SUFFIX}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
