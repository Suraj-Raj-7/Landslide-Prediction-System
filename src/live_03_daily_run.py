"""Live system, step 3 (every day): landslide risk for HP today and tomorrow.

WHAT ONE RUN DOES
  1. Reads the HP grid file (55,253 cells: fixed features, district,
     vegetation; made monthly by live_01_monthly_grid.py).
  2. Adds rain for today and tomorrow (live_02_rain.py: measured IMERG rain,
     GFS forecast for the part not yet measured) and the glacier flag.
  3. Scores every cell with the live model (models/rf_roads_live_v1.joblib),
     road-neutral: both road distances set to the median of the training
     landslides, so every cell is scored "as if watched like a roadside
     slope" (decision of 5 Nov 2026).
  4. Puts each cell at Watch / Warning with the final levels, and each
     district at a level when >= 30% of its cells within 500 m of a road
     reach it (final rule, adopted 9 Nov 2026 after the storm replays;
     docs/alert_rule_explained.md). All numbers come from
     models/rf_roads_live_v1_meta.json, so they live in one place.
  5. Writes the results: district table, cell scores, maps, a web page, and
     an email to the recipients.

WHERE IT RUNS
  On this laptop (for tests) or on GitHub Actions every morning
  (.github/workflows/daily.yml). On GitHub, the Earth Engine login and the
  email password come from GitHub secrets, never from files:
    EE_SERVICE_ACCOUNT_KEY   the service-account key (JSON text)
    ALERT_SENDER             Gmail address that sends the email
    ALERT_APP_PASSWORD       Gmail app password of that address
    ALERT_RECIPIENTS         comma-separated email addresses
    SITE_URL                 address of the published web page (to keep the run history)
  Without the email secrets the run still works and just skips the email.

RUN
  .venv/Scripts/python -W ignore src/live_03_daily_run.py                 # today (IST)
  .venv/Scripts/python -W ignore src/live_03_daily_run.py --date 2026-11-09 --no-email
OUTPUTS  site/ (web page, maps, tables, history.json; published by the workflow)
"""
import argparse
import datetime as dt
import html
import json
import os
import smtplib
import ssl
import urllib.request
from email.message import EmailMessage

import ee
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

PROJECT = "idyllic-return-468714-j4"
GRID = "data/live/grid_live.csv.gz"
GRID_INFO = "data/live/grid_live_info.json"
OUTLINES = "data/live/hp_districts.geojson"
MODEL = "models/rf_roads_live_v1.joblib"
META = "models/rf_roads_live_v1_meta.json"
SITE = "site"
LEVEL_NAMES = {0: "none", 1: "watch", 2: "warning"}
COLORS = {"none": "#d9d9d9", "watch": "#f4a261", "warning": "#c0392b"}


def init_ee():
    """Service account on GitHub; the normal personal login on the laptop."""
    key = os.environ.get("EE_SERVICE_ACCOUNT_KEY")
    if key:
        info = json.loads(key)
        creds = ee.ServiceAccountCredentials(info["client_email"], key_data=key)
        ee.Initialize(creds, project=PROJECT)
    else:
        ee.Initialize(project=PROJECT)


def score_day(grid, rain, model, meta):
    """Road-neutral score, cell level and district level for one day."""
    rule = meta["final_alert_rule"]
    X = grid.copy()
    X[rain.columns] = rain.values
    for col, v in rule["road_neutral_values_m"].items():
        X[col] = v
    s = model.predict_proba(X[meta["features_in_order"]])[:, 1]
    lvl = np.where(s >= rule["cell_warning"], 2, np.where(s >= rule["cell_watch"], 1, 0))
    cells = pd.DataFrame({"id": grid.id, "lon": grid.lon, "lat": grid.lat, "district": grid.district,
                          "road_zone": grid.dist_road_m <= rule["road_zone_m"],
                          "rain_today_mm": rain.imerg_d0.round(1), "rain_7d_before_mm": rain.imerg_ant7d.round(1),
                          "score": s.round(4), "level": lvl})
    rows = []
    for name, d in cells[(cells.district != "unassigned")].groupby("district"):
        rz = d[d.road_zone]
        watch, warn = (rz.level >= 1).mean(), (rz.level == 2).mean()
        level = 2 if warn >= rule["district_share"] else (1 if watch >= rule["district_share"] else 0)
        rows.append({"district": name, "level": LEVEL_NAMES[level],
                     "road_zone_cells_at_watch_or_above_pct": round(100 * watch, 1),
                     "road_zone_cells_at_warning_pct": round(100 * warn, 1),
                     "rain_today_mean_mm": round(d.rain_today_mm.mean(), 1),
                     "rain_today_max_mm": round(d.rain_today_mm.max(), 1)})
    order = {"warning": 0, "watch": 1, "none": 2}
    districts = pd.DataFrame(rows).sort_values(["level", "district"], key=lambda c: c.map(order) if c.name == "level" else c)
    return cells, districts


def draw_map(cells, districts, outlines, title, path):
    fig, ax = plt.subplots(figsize=(7.5, 7))
    for lv in [0, 1, 2]:
        m = cells.level == lv
        ax.scatter(cells.lon[m & cells.road_zone], cells.lat[m & cells.road_zone], s=2.5, marker="s", lw=0,
                   c=COLORS[LEVEL_NAMES[lv]], label={0: "No alert", 1: "Watch", 2: "Warning"}[lv])
        ax.scatter(cells.lon[m & ~cells.road_zone], cells.lat[m & ~cells.road_zone], s=2.5, marker="s", lw=0,
                   c=COLORS[LEVEL_NAMES[lv]], alpha=0.4)
    dl = districts.set_index("district").level.to_dict()
    for f in outlines["features"]:
        g, name = f["geometry"], f["properties"]["shapeName"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"] if g["type"] == "MultiPolygon" else \
            [p for sub in g.get("geometries", []) if sub["type"] in ("Polygon", "MultiPolygon")
             for p in ([sub["coordinates"]] if sub["type"] == "Polygon" else sub["coordinates"])]
        for p in polys:
            xy = np.array(p[0])
            ax.plot(xy[:, 0], xy[:, 1], color="black", lw=0.6)
        if polys:
            cx, cy = np.array(polys[0][0]).mean(axis=0)
            lv = dl.get(name, "none")
            ax.text(cx, cy, name + ("\n" + lv.upper() if lv != "none" else ""), fontsize=6.5, ha="center", va="center",
                    bbox=dict(fc="white", ec="none", alpha=0.65, pad=0.5))
    ax.set_title(title, fontsize=9)
    ax.set_aspect("equal")
    ax.legend(loc="lower left", fontsize=7, markerscale=4)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.text(0.01, 0.005, "Faded: more than 500 m from a road (lower confidence). District level: >= 30% of its road-zone cells.",
             fontsize=6.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def headline(districts):
    w = districts[districts.level == "warning"].district.tolist()
    a = districts[districts.level == "watch"].district.tolist()
    parts = ([f"WARNING: {', '.join(w)}"] if w else []) + ([f"WATCH: {', '.join(a)}"] if a else [])
    return "; ".join(parts) if parts else "No district on alert"


def counts(districts):
    """Short line for map titles, e.g. '2 districts at Warning, 3 at Watch'."""
    w, a = (districts.level == "warning").sum(), (districts.level == "watch").sum()
    return f"{w} district(s) at Warning, {a} at Watch" if w or a else "No district on alert"


def table_html(districts):
    head = "".join(f"<th>{h}</th>" for h in ["District", "Level", "Road-zone cells at Watch+ (%)",
                                               "at Warning (%)", "Rain today, mean / max (mm)"])
    rows = "".join(
        f"<tr class='{r.level}'><td>{html.escape(r.district)}</td><td>{r.level.capitalize() if r.level != 'none' else '-'}</td>"
        f"<td>{r.road_zone_cells_at_watch_or_above_pct}</td><td>{r.road_zone_cells_at_warning_pct}</td>"
        f"<td>{r.rain_today_mean_mm} / {r.rain_today_max_mm}</td></tr>" for r in districts.itertuples())
    return f"<table><tr>{head}</tr>{rows}</table>"


def write_site(today, res, info, history):
    """Static web page with today's and tomorrow's maps, district tables and the run history."""
    tomorrow = today + dt.timedelta(days=1)
    css = ("body{font-family:Arial,sans-serif;max-width:1000px;margin:20px auto;padding:0 12px;color:#222}"
           "table{border-collapse:collapse;margin:8px 0 20px}td,th{border:1px solid #ccc;padding:4px 8px;font-size:14px}"
           "tr.warning td{background:#f5c6c0}tr.watch td{background:#fbe3cf}img{max-width:100%}"
           ".maps{display:flex;gap:12px;flex-wrap:wrap}.maps div{flex:1 1 420px}small{color:#666}")
    hist_rows = "".join(f"<tr><td>{h['date']}</td><td>{html.escape(h['today'])}</td><td>{html.escape(h['tomorrow'])}</td></tr>"
                        for h in reversed(history[-30:]))
    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HP landslide early warning</title><style>{css}</style></head><body>
<h1>Landslide early warning, Himachal Pradesh</h1>
<p><b>Today ({today:%d %b %Y}):</b> {html.escape(headline(res[today][1]))}<br>
<b>Tomorrow ({tomorrow:%d %b %Y}):</b> {html.escape(headline(res[tomorrow][1]))}</p>
<div class="maps"><div><img src="map_today.png" alt="Risk map today"></div><div><img src="map_tomorrow.png" alt="Risk map tomorrow"></div></div>
<h2>Districts today</h2>{table_html(res[today][1])}
<h2>Districts tomorrow (forecast)</h2>{table_html(res[tomorrow][1])}
<h2>How to read this</h2>
<p>Every 1 km square of HP gets a risk score from terrain, vegetation and rain. A square is at <b>Watch</b> at a score of
{info['levels']['watch']} or more and at <b>Warning</b> at {info['levels']['warning']} or more. A <b>district</b> is put at a level
when at least 30% of its squares within 500 m of a road reach it. In tests on 16 past storm days and 16 quiet days, this rule put
86% of the districts with recorded landslides at Watch (73% at Warning), and alarmed on 15% of quiet district-days at Watch (1.6% at Warning).</p>
<p><small>Rain: measured satellite rain (NASA IMERG) up to {info['rain']['imerg_until_utc']} UTC; after that, the GFS weather forecast.
Share of today's rain that is forecast: {round(100 * info['rain']['today_rain_from_forecast_share'])}%. The model was trained on measured rain only,
so forecast rain adds warning time but also errors. Vegetation layer: window ending {info['grid']['ndvi_window_ends']}.
Glacier flag: ERA5-Land of {info['glacier_date']}. Run at {info['run_utc']} UTC.
The model learned from reported landslides, which are mostly near roads; squares far from roads are less certain.</small></p>
<h2>Recent runs</h2><table><tr><th>Date</th><th>Today</th><th>Tomorrow</th></tr>{hist_rows}</table>
<p><small>M.Tech ICTD project, IIT Delhi. Research prototype, not an official warning.</small></p>
</body></html>"""
    open(f"{SITE}/index.html", "w", encoding="utf-8").write(page)


def send_email(today, res, info):
    sender, pwd, to = (os.environ.get(k) for k in ("ALERT_SENDER", "ALERT_APP_PASSWORD", "ALERT_RECIPIENTS"))
    if not (sender and pwd and to):
        print("email skipped (no email secrets set)")
        return
    tomorrow = today + dt.timedelta(days=1)
    msg = EmailMessage()
    msg["Subject"] = f"HP landslide outlook {today:%d %b}: {headline(res[today][1])}"
    msg["From"], msg["To"] = sender, to
    site = os.environ.get("SITE_URL", "")
    body = (f"<p><b>Today ({today:%d %b}):</b> {html.escape(headline(res[today][1]))}<br>"
            f"<b>Tomorrow ({tomorrow:%d %b}, forecast):</b> {html.escape(headline(res[tomorrow][1]))}</p>"
            f"{table_html(res[today][1])}"
            f"<p>Map attached. {'Full page: <a href=' + chr(34) + site + chr(34) + '>' + site + '</a>' if site else ''}</p>"
            f"<p style='color:#666;font-size:12px'>A district is at a level when at least 30% of its squares within 500 m of a road reach it. "
            f"Rain after {info['rain']['imerg_until_utc']} UTC is forecast (GFS). Research prototype (M.Tech ICTD, IIT Delhi), not an official warning.</p>")
    msg.set_content("HTML email; open in a mail client that shows HTML.")
    msg.add_alternative(body, subtype="html")
    with open(f"{SITE}/map_today.png", "rb") as f:
        msg.add_attachment(f.read(), maintype="image", subtype="png", filename=f"hp_landslide_{today:%Y%m%d}.png")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(sender, pwd)
        s.send_message(msg)
    print("email sent to", len(to.split(",")), "recipient(s)")


def load_history():
    """Earlier runs, read back from the published page (no commits needed to keep them)."""
    url = os.environ.get("SITE_URL")
    if url:
        try:
            with urllib.request.urlopen(url.rstrip("/") + "/history.json", timeout=20) as r:
                return json.load(r)
        except Exception as e:  # first run, or page not published yet
            print("no earlier history found:", e)
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="IST date to run for (default: today in IST)")
    ap.add_argument("--no-email", action="store_true")
    a = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    init_ee()
    import live_02_rain as R   # after the login: the module builds Earth Engine objects on import
    today = dt.date.fromisoformat(a.date) if a.date else (now + R.IST).date()

    os.makedirs(SITE, exist_ok=True)
    meta = json.load(open(META))
    model = joblib.load(MODEL)
    grid = pd.read_csv(GRID)
    grid_info = json.load(open(GRID_INFO))
    grid["era5_glacier"], glacier_date = R.glacier_flag(grid)
    rain, _, rain_info = R.rain_features(grid, today)
    print("rain:", rain_info)

    res = {}
    for day, r in rain.items():
        cells, districts = score_day(grid, r, model, meta)
        res[day] = (cells, districts)
        tag = "today" if day == today else "tomorrow"
        draw_map(cells, districts, json.load(open(OUTLINES)),
                 f"{'Today' if tag == 'today' else 'Tomorrow (forecast)'}, {day:%d %b %Y}\n{counts(districts)}",
                 f"{SITE}/map_{tag}.png")
        districts.to_csv(f"{SITE}/districts_{tag}.csv", index=False)
        cells.to_csv(f"{SITE}/cells_{tag}.csv.gz", index=False)
        print(f"{tag} {day}: {headline(districts)}")
        print(districts.to_string(index=False))

    rule = meta["final_alert_rule"]
    info = {"date": today.isoformat(), "run_utc": now.strftime("%Y-%m-%d %H:%M"), "rain": rain_info,
            "grid": grid_info, "glacier_date": glacier_date,
            "levels": {"watch": rule["cell_watch"], "warning": rule["cell_warning"]}}
    json.dump(info, open(f"{SITE}/run_info.json", "w"), indent=2, default=str)
    history = [h for h in load_history() if h["date"] != today.isoformat()]
    history.append({"date": today.isoformat(), "today": headline(res[today][1]),
                    "tomorrow": headline(res[today + dt.timedelta(days=1)][1]), "run_utc": info["run_utc"]})
    json.dump(history, open(f"{SITE}/history.json", "w"), indent=1)
    write_site(today, res, info, history)
    if not a.no_email:
        send_email(today, res, info)
    print("done:", headline(res[today][1]))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
