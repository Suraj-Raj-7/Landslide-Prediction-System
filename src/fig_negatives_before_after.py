"""Figure: where the old random negatives were vs the new hard negatives.

PURPOSE
  Presentation 2 (17 Sep 2026) used 878 random negatives; the instructor
  flagged the negative sampling as a serious issue. This map shows why:
  left, the old random negatives against the recorded landslides; right,
  the new "similar place, storm day" (Type 2) negatives. Type 1 negatives
  ("same place, safe day") sit exactly on the landslide points and are not
  drawn separately.

INPUTS   data/legacy/negatives_features_v3.csv (September negatives),
         data/phaseB/training_table_v1.csv
OUTPUTS  docs/figures/negatives_before_after.png
RUN      .venv/Scripts/python -W ignore src/fig_negatives_before_after.py
"""
import ee
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ee.Initialize(project="idyllic-return-468714-j4")
STATE_IDS = ["1811400B21086746745937", "1811400B3558497485804", "1811400B42025667129192", "1811400B23769854471902"]


def outlines():
    fc = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1") \
        .filter(ee.Filter.inList("shapeID", STATE_IDS)).map(lambda f: f.simplify(1000))
    def polys(g):
        """Polygon / MultiPolygon / GeometryCollection -> list of polygons."""
        if g["type"] == "Polygon":
            return [g["coordinates"]]
        if g["type"] == "MultiPolygon":
            return g["coordinates"]
        if g["type"] == "GeometryCollection":
            return [p for s in g["geometries"] for p in polys(s)]
        return []
    return [np.array(p[0]) for f in fc.getInfo()["features"] for p in polys(f["geometry"])]


def main():
    old = pd.read_csv("data/legacy/negatives_features_v3.csv")
    t = pd.read_csv("data/phaseB/training_table_v1.csv")
    pos = t[t.label == 1]
    t2 = t[t.neg_type == "similar_place_storm_day"]
    rings = outlines()
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), sharex=True, sharey=True)   # same extent in both panels
    panels = [(axes[0], old, "#e76f51", f"Before (Sep 2026): {len(old)} random negatives"),
              (axes[1], t2, "#2a9d8f", f"After (Oct 2026): {len(t2):,} 'similar place, storm day' negatives")]
    for ax, neg, col, title in panels:
        for r in rings:
            ax.plot(r[:, 0], r[:, 1], color="grey", lw=0.6)
        ax.scatter(neg.lon, neg.lat, s=5, c=col, label="Negatives (no landslide)")
        ax.scatter(pos.lon, pos.lat, s=5, c="#1d3557", label=f"Recorded landslides ({len(pos)})")
        ax.set_title(title, fontsize=11)
        ax.set_aspect("equal")
        ax.set_xlabel("Longitude (°E)")
        ax.legend(loc="lower left", fontsize=9, markerscale=3)
    axes[0].set_ylabel("Latitude (°N)")
    fig.savefig("docs/figures/negatives_before_after.png", dpi=170, bbox_inches="tight")
    print("saved docs/figures/negatives_before_after.png")


if __name__ == "__main__":
    main()
