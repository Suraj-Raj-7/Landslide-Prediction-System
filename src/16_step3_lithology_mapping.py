"""Step 3: draft the explicit lithology mapping table (review before use).

Every distinct NGDR 'lithologic' description gets one row with:
  glim_class   GLiM level-1 class (Hartmann & Moosdorf 2012, G3 13:Q12004)
  rock_main    first rock term found in the description (dominant rock)
  matched      every rock term found, in order, with its GLiM class
  flag         MIXED (terms from >1 GLiM class), NO_MATCH, or empty
  rule         which rule decided glim_class
Rule: the first rock term listed decides the class (NGDR descriptions list the
dominant rock first); a description mixing siliciclastic and carbonate rocks is
'sm' (mixed sedimentary), as GLiM defines it. Flagged rows are reviewed by hand
and fixed in MANUAL below, never silently.
Usage: python -I 16_step3_lithology_mapping.py IN_CSV OUT_CSV
"""
import csv
import re
import sys

GLIM = {"su": "unconsolidated sediments", "ss": "siliciclastic sedimentary", "sm": "mixed sedimentary",
        "sc": "carbonate sedimentary", "ev": "evaporites", "mt": "metamorphics", "pa": "acid plutonic",
        "pi": "intermediate plutonic", "pb": "basic plutonic", "va": "acid volcanic",
        "vi": "intermediate volcanic", "vb": "basic volcanic", "py": "pyroclastics",
        "wb": "water bodies", "ig": "ice and glaciers", "nd": "no data"}

# rock term (regex, whole word) -> (rock_main label, GLiM class). Order matters only for
# overlapping words (longer terms first).
TERMS = [
    (r"alluvi\w*", "alluvium", "su"), (r"moraine\w*|morainic", "moraine", "su"),
    (r"scree", "scree", "su"), (r"hill ?wash", "hillwash", "su"), (r"talus", "talus", "su"),
    (r"colluvi\w*", "colluvium", "su"), (r"fluvio[- ]?glacial|glacial deposit\w*|outwash", "glacial deposit", "su"),
    (r"terrace\w*", "terrace deposit", "su"), (r"fan deposit\w*|debris", "debris/fan", "su"),
    (r"loess", "loess", "su"), (r"karewa\w*", "karewa", "su"),
    (r"(?:rounded |assorted )?(?:oxidised |unoxidised )?(?:and consolidated )?rock fragments", "rock fragments", "su"),
    (r"boulders?|gravels?|pebbles?|cobbles?", "gravel", "su"),
    (r"sandstones?", "sandstone", "ss"), (r"siltstones?", "siltstone", "ss"),
    (r"claystones?", "claystone", "ss"), (r"mudstones?", "mudstone", "ss"), (r"shales?", "shale", "ss"),
    (r"conglomerates?", "conglomerate", "ss"), (r"greywackes?|graywackes?", "greywacke", "ss"),
    (r"arkoses?", "arkose", "ss"), (r"quartz[- ]?arenites?|arenites?", "quartz arenite", "ss"),
    (r"cherts?|jaspers?", "chert", "ss"), (r"intratrappean sediments?", "intertrappean sediment", "ss"), (r"grits?", "grit", "ss"), (r"diamictites?", "diamictite", "ss"),
    (r"sands?", "sand", "su"), (r"silts?", "silt", "su"), (r"clays?", "clay", "su"),
    (r"limestones?", "limestone", "sc"), (r"dolomit\w*|dolostones?", "dolomite", "sc"),
    (r"marls?", "marl", "sc"), (r"gypsum|evaporit\w*|salt", "evaporite", "ev"),
    (r"slates?", "slate", "mt"), (r"phyllit\w*", "phyllite", "mt"), (r"schists?", "schist", "mt"),
    (r"gneiss\w*", "gneiss", "mt"), (r"migmatit\w*", "migmatite", "mt"),
    (r"quartzites?|qtzt?|qtzites?|qtzite", "quartzite", "mt"), (r"marbles?", "marble", "mt"),
    (r"amphibolit\w*", "amphibolite", "mt"), (r"granulit\w*", "granulite", "mt"),
    (r"mylonit\w*", "mylonite", "mt"), (r"calc[- ]?silicate\w*", "calc-silicate", "mt"),
    (r"meta[- ]?\w+", "metamorphic (meta-)", "mt"), (r"hornfels", "hornfels", "mt"),
    (r"eclogit\w*", "eclogite", "mt"), (r"epidiorit\w*", "epidiorite", "mt"), (r"serpentinit\w*", "serpentinite", "pb"),
    (r"leuco ?granit\w*|granit\w*|grnt|granitoid\w*", "granite", "pa"),
    (r"granodiorit\w*|grandiort\w*|grndrt", "granodiorite", "pa"), (r"pegmatit\w*", "pegmatite", "pa"),
    (r"aplit\w*", "aplite", "pa"), (r"tonalit\w*", "tonalite", "pi"), (r"diorit\w*|diort", "diorite", "pi"), (r"appinit\w*", "appinite", "pi"),
    (r"monzonit\w*", "monzonite", "pi"), (r"syenit\w*", "syenite", "pi"),
    (r"gabbro\w*", "gabbro", "pb"), (r"dolerit\w*", "dolerite", "pb"), (r"norit\w*", "norite", "pb"),
    (r"peridotit\w*|dunit\w*|ultrama\w*|pyroxenit\w*|ultra ?basic\w*|harzburgit\w*|ophiolit\w*", "ultramafic", "pb"),
    (r"anorthosit\w*", "anorthosite", "pb"),
    (r"rhyolit\w*", "rhyolite", "va"), (r"dacit\w*", "dacite", "va"), (r"ignimbrit\w*", "ignimbrite", "va"),
    (r"andesit\w*", "andesite", "vi"), (r"trachyt\w*", "trachyte", "vi"),
    (r"basalt\w*|traps?|basic (?:lava|flow)s?|lava flows?|basic volcanics?|volcanic flows?", "basalt", "vb"),
    (r"basic rocks?", "basic rock (unspecified)", "pb"),
    (r"tuffs?|agglomerat\w*|volcaniclastic\w*|pyroclastic\w*", "tuff/pyroclastic", "py"),
    (r"glaciers?|ice|snow", "ice", "ig"), (r"quartz (?:vein|reef)\w*", "quartz vein", "nd"), (r"water ?bod\w*|lakes?|river\w*", "water", "wb"),
]
COMPILED = [(re.compile(r"(?<![a-z])(?:" + p + r")(?![a-z])"), name, cls) for p, name, cls in TERMS]

# Hand decisions for flagged rows: description -> (glim_class, rock_main, reason). Filled after review.
MANUAL = {}


QUATERNARY = ("quaternary", "holocene", "pleistocene", "recent")


def classify(desc, ages=""):
    text = desc.lower()
    hits = []
    for rx, name, cls in COMPILED:
        for m in rx.finditer(text):
            hits.append((m.start(), name, cls))
    hits.sort()
    seen, ordered = set(), []
    for pos, name, cls in hits:   # drop overlapping matches (e.g. 'sand' inside 'sand, silt')
        if any(pos >= s and pos < e for s, e in seen):
            continue
        ordered.append((name, cls))
        seen.add((pos, pos + 1))
    classes = []
    for _, c in ordered:
        if c not in classes:
            classes.append(c)
    if desc in MANUAL:
        g, r, why = MANUAL[desc]
        return g, r, ordered, "", "manual: " + why
    if not ordered:
        return "nd", "", ordered, "NO_MATCH", "no rock term found"
    main_name, main_cls = ordered[0]
    a = ages.lower()
    if main_cls == "su" and a and not any(q in a for q in QUATERNARY):
        flag = "MIXED" if len(classes) > 1 else ""
        return "ss", main_name, ordered, flag, "loose-sediment term but pre-Quaternary age -> consolidated (ss)"
    if set(classes) >= {"ss", "sc"} and main_cls in ("ss", "sc"):
        return "sm", main_name, ordered, "MIXED" if len(classes) > 2 else "", "siliciclastic + carbonate -> sm"
    flag = "MIXED" if len(classes) > 1 else ""
    return main_cls, main_name, ordered, flag, "first rock term"


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    out = []
    for r in rows:
        g, main, ordered, flag, rule = classify(r["lithologic"], r.get("ages", ""))
        out.append({**r, "glim_class": g, "glim_name": GLIM[g], "rock_main": main,
                    "matched": "; ".join(f"{n}({c})" for n, c in ordered), "flag": flag, "rule": rule})
    cols = ["lithologic", "glim_class", "glim_name", "rock_main", "flag", "rule", "matched",
            "states", "polygons", "area_km2", "landslides", "group_names", "ages"]
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print("rows", len(out), "| flags", Counter(o["flag"] for o in out))
    print("glim classes (by landslides):",
          sorted(((c, sum(int(o["landslides"]) for o in out if o["glim_class"] == c)) for c in GLIM), key=lambda x: -x[1]))
