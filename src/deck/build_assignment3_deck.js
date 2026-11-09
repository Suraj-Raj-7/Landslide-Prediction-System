// Builds the Assignment 3 deck, written to be
// read without a presenter by someone who remembers little of Presentations 1
// and 2. Every number on a slide comes from the result files in data/ or from
// the source named in the slide's source line. Run from the project root:
//   NODE_PATH=<folder with pptxgenjs> node src/deck/build_assignment3_deck.js <apply_theme.js path>
const pptxgen = require("pptxgenjs");
const path = require("path");

// Optional third argument: another output path (e.g. when the deck is open in PowerPoint)
const OUT = process.argv[3] || "docs/presentations/Suraj - Siddhesh - Rainfall aware Landslide Early Warning for Himachal Pradesh.pptx";
const FIG = (f) => path.join("docs", "figures", f);

// ---- theme: deep teal-slate; Watch orange and Warning red as on the maps ----
const THEME = {
  name: "Monsoon Slope",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2B2E", lt1: "FFFFFF", dk2: "1F4E5A", lt2: "EEF3F2",
    accent1: "1F4E5A", accent2: "C0392B", accent3: "F4A261", accent4: "2A9D8F",
    accent5: "6C7A7D", accent6: "1D3557", hlink: "1F4E5A", folHlink: "6C7A7D",
  },
};
const K = THEME.colors;
const INK = K.dk1, TEAL = K.dk2, MIST = K.lt2, RED = K.accent2, ORANGE = K.accent3,
  GREEN = K.accent4, GREY = K.accent5, NAVY = K.accent6, WHITE = "FFFFFF", BROWN = "B35C10";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Suraj Raj, Siddhesh Pohare";
pres.company = "IIT Delhi";
pres.title = "Rainfall-Aware Landslide Risk Mapping for Himachal Pradesh: Assignment 3";

const W = 13.333, M = 0.5;
const FOOT = "Rainfall-Aware Landslide Risk Mapping for Himachal Pradesh  |  Suraj Raj, Siddhesh Pohare  |  ICTD, IIT Delhi";

// ---- layouts ----
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: TEAL },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.6, w: W - 2 * M, h: 1.7, fontFace: "Cambria", fontSize: 40, bold: true, color: WHITE, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: M, y: 3.45, w: W - 2 * M, h: 1.0, fontSize: 20, color: "D7E6E3", valign: "top", align: "left" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  margin: [0.4, 0.5, 0.6, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.45, w: W - 2 * M, h: 0.62, fontFace: "Cambria", fontSize: 30, bold: true, color: TEAL, valign: "middle", align: "left" }, text: "" } },
    { placeholder: { options: { name: "msg", type: "body", x: M, y: 1.08, w: W - 2 * M, h: 0.55, fontSize: 16, italic: true, color: INK, valign: "middle", align: "left" }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: 7.1, w: 11.6, h: 0.28, fontSize: 9, color: GREY } } },
  ],
  slideNumber: { x: 12.3, y: 7.1, w: 0.55, h: 0.28, fontSize: 9, color: GREY, align: "right" },
});

// ---- helpers ----
let SEC = "";
function section(t) { SEC = t; pres.addSection({ title: t }); }
// Content slide: section label, title, one-line message, source line, notes
function content(eyebrow, title, msg, source, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC });
  s.addText(eyebrow.toUpperCase(), { x: M, y: 0.2, w: 8, h: 0.28, fontSize: 11, bold: true, color: BROWN, charSpacing: 2, isTextBox: true, margin: 0 });
  s.addText(title, { placeholder: "title" });
  s.addText(msg, { placeholder: "msg" });
  if (source) s.addText("Source: " + source, { x: M, y: 6.76, w: W - 2 * M, h: 0.3, fontSize: 9.5, italic: true, color: GREY, isTextBox: true, margin: 0, valign: "top" });
  if (notes) s.addNotes(notes);
  return s;
}
// A tinted rounded card with a bold heading and bullet lines (body 1.5 pt above the given size)
function card(s, x, y, w, h, heading, lines, o = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: o.fill || MIST }, line: { color: o.fill || MIST }, objectName: "card " + heading });
  s.addText(heading, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.4, fontSize: o.hsize || 16, bold: true, color: o.hcolor || TEAL, isTextBox: true, margin: 0 });
  const items = lines.map((t, i) => ({ text: t, options: { bullet: o.bullets === false ? false : { indent: 14 }, breakLine: i < lines.length - 1, paraSpaceAfter: 4 } }));
  s.addText(items, { x: x + 0.15, y: y + 0.55, w: w - 0.3, h: h - 0.65, fontSize: (o.size || 13.5) + 1.5, color: o.color || INK, valign: "top", isTextBox: true, margin: 0 });
}
function stat(s, x, y, w, num, label, color) {
  s.addText(num, { x, y, w, h: 0.75, fontSize: 34, bold: true, color: color || TEAL, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText(label, { x, y: y + 0.75, w, h: 0.6, fontSize: 13, color: INK, valign: "top", isTextBox: true, margin: 0 });
}
// Table with a teal header row (one point above the size given)
function table(s, rows, o) {
  const head = rows[0].map((t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: TEAL } } }));
  const body = rows.slice(1).map((r, i) => r.map((t) => {
    const cell = typeof t === "object" ? t : { text: String(t) };
    cell.options = Object.assign({ fill: { color: i % 2 ? WHITE : "F6F9F8" } }, cell.options || {});
    return cell;
  }));
  const opts = Object.assign({ fontSize: 12, color: INK, border: { type: "solid", pt: 0.5, color: "CFDAD8" }, valign: "middle", margin: 0.06, autoPage: false }, o);
  opts.fontSize += 1;
  s.addTable([head, ...body], opts);
}
function pic(s, file, x, y, maxW, maxH, ratio) {
  let w = maxW, h = maxW / ratio;
  if (h > maxH) { h = maxH; w = maxH * ratio; }
  s.addImage({ path: FIG(file), x: x + (maxW - w) / 2, y, w, h, altText: file });
  return { w, h };
}
function caption(s, text, x, y, w) {
  s.addText(text, { x, y, w, h: 0.35, fontSize: 11, italic: true, color: GREY, isTextBox: true, margin: 0 });
}
function chip(s, x, y, text, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 1.55, h: 0.32, rectRadius: 0.15, fill: { color }, line: { color } });
  s.addText(text, { x, y, w: 1.55, h: 0.32, fontSize: 11, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
}
const CHART = { catAxisLabelColor: INK, valAxisLabelColor: INK, valGridLine: { color: "E2E8E7", size: 0.5 }, catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, valAxisLabelFormatCode: "0.00", valAxisLabelFontSize: 11,
  showLegend: true, legendPos: "b", legendFontSize: 11, showTitle: true, titleFontSize: 13, titleColor: TEAL, showValAxisTitle: true, valAxisTitleFontSize: 11 };

// =====================================================================
section("Introduction");

// 1. Title
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: SEC });
  s.addText("ASSIGNMENT 3", { x: M, y: 0.6, w: 9, h: 0.4, fontSize: 14, bold: true, color: ORANGE, charSpacing: 2, isTextBox: true, margin: 0 });
  s.addText("Rainfall-Aware Landslide Risk Mapping for Himachal Pradesh", { placeholder: "title" });
  s.addText("Interim progress: from a risk map to a daily landslide early-warning system for HP's disaster authorities (problem, methodology, implementation, results)", { placeholder: "sub" });
  s.addText([
    { text: "Suraj Raj (2026MCS2801)  ·  Siddhesh Pohare (2026MCS2257)", options: { breakLine: true } },
    { text: "M.Tech ICTD, IIT Delhi  ·  Instructor: Prof. Aaditeshwar Seth  ·  NGO mentor: Betwa Solutions" },
  ], { x: M, y: 5.2, w: W - 2 * M, h: 1.2, fontSize: 15, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("Slide 3 recaps Presentations 1 and 2; slides 5–6 list what changed since then.", { x: M, y: 6.7, w: W - 2 * M, h: 0.4, fontSize: 12, italic: true, color: "BFD4D0", isTextBox: true, margin: 0 });
  s.addNotes("Assignment 3. Same project and title as Presentations 1 (17 Aug) and 2 (17 Sep). The deck is meant to be read without a presenter. Each content slide has a section label, a title, a one-line message (the conclusion), the evidence, and a source line; these notes add detail and point to the project files holding the numbers.");
}

// 3. At a glance
{
  const s = content("Summary", "The project at a glance",
    "We built and tested the core of a daily warning system; it separates storm days from quiet days, and we know its limits",
    "Our analysis of the landslide inventory (GSI Bhusanket, NASA Global Landslide Catalog) with NASA GPM IMERG rainfall; tests on slide 12; maps on slides 21–22.",
    "Summary of the whole deck. Skill: Random Forest, live data, whole years held out. Storm/quiet shares: road-neutral map with a model trained without 2023.");
  card(s, M, 1.75, 4.0, 2.55, "Problem", [
    "Rain-triggered landslides block roads and kill people in Himachal Pradesh (HP) every monsoon",
    "Published HP studies give static maps (where), not daily warnings (when)",
    "Goal: a daily, district-level warning for HP's disaster authorities, using free data only",
  ], { size: 12 });
  card(s, 4.67, 1.75, 4.0, 2.55, "What we built", [
    "981 dated landslides (HP, Uttarakhand, J&K) with 42 features each",
    "2,167 hard 'no-landslide' examples (training table: 3,136 rows)",
    "A model tested honestly (whole years hidden) and a whole-HP daily scoring of 55,253 cells of 1 km",
  ], { size: 12 });
  card(s, 8.83, 1.75, 4.0, 2.55, "Honest limits", [
    "Catches about half of recorded HP slides at the lower alert level",
    "Rain alone times slides as well as the model: the satellite rain data sets the ceiling",
    "Records are biased to roads; remote areas are less certain",
  ], { size: 12 });
  stat(s, M, 4.55, 3.0, "0.775", "Live model skill (ROC AUC), whole years hidden; 0.5 = coin toss", TEAL);
  stat(s, 3.7, 4.55, 3.0, "0.856", "Same model with the easy random-row test: why a high score can mislead", GREY);
  stat(s, 6.9, 4.55, 2.9, "66.8%", "of HP flagged on a storm day (14 Aug 2023), all 31 recorded slides inside", RED);
  stat(s, 10.0, 4.55, 2.8, "0.4%", "of HP flagged on a quiet day (12 Sep 2023), 0 of 12 districts alerted", GREEN);
  s.addText("Next: daily automation and email alerts, storm replays to set the final alert rules, impact-assessment design, final paper.", { x: M, y: 6.2, w: W - 2 * M, h: 0.45, fontSize: 14, bold: true, color: TEAL, isTextBox: true, margin: 0 });
}

// 4. Recap of Presentations 1 and 2
{
  const s = content("Recap", "Where the project stood after Presentations 1 and 2",
    "We proposed rainfall-aware risk mapping, built a first dataset and model, and were told our negative examples were the weak point",
    "Our Presentation 1 (17 Aug 2026) and Presentation 2 (17 Sep 2026) decks and the instructor's written feedback.",
    "Recap for a reader who does not remember the earlier presentations. Presentation 1 also included an AHP susceptibility baseline (Siddhesh: 6 factors, consistency ratio 0.0124; validated against Sentinel-2 change masks, global AUC 0.62).");
  card(s, M, 1.75, 4.0, 4.9, "Presentation 1 (17 Aug): proposal", [
    "Idea: risk = terrain susceptibility × rainfall, for HP, delivered to disaster authorities (not the public)",
    "AHP-weighted terrain map as a baseline",
    "Research questions: RQ1 does rainfall improve on terrain alone; RQ2 new vs reactivated slides; RQ3 terrain–land-use–rain combinations",
    "Feedback: AHP maps are common; rainfall-based prediction is under-explored but needs dated landslides; small road slides are too small for open satellite data",
  ], { size: 12.5 });
  card(s, 4.67, 1.75, 4.0, 4.9, "Presentation 2 (17 Sep): first build", [
    "GSI's national inventory extracted from a 904-page PDF (36,071 records); only 1.7% of HP records have an exact date",
    "Uttarakhand and J&K added by a two-stage method; 886 dated events",
    "CHIRPS rainfall for 3–30 days before each event",
    "First models on slope + rain with random background points: Random Forest AUC 0.895",
  ], { size: 12.5 });
  card(s, 8.83, 1.75, 4.0, 4.9, "Feedback on Presentation 2", [
    "'Good effort in assembling a dataset'",
    "'Negative sampling has some serious issue': a slope-and-rain model gives high recall but low precision, so many false alarms and users stop trusting it",
    "This feedback drove most of the work since (slides 5–6)",
  ], { size: 12.5, fill: "FDF1E6", hcolor: BROWN });
}

// 5. Problem
{
  const s = content("Problem", "Why Himachal Pradesh needs a daily landslide warning",
    "The data to warn exist every day for free; what is missing is a tested system that turns them into district alerts",
    "Meena et al. 2019; Singh et al. 2024; Ministry of Earth Sciences, Lok Sabha reply 2025 (GSI coverage); 2023 toll: state figures in the press, Aug 2023.",
    "The 2023 monsoon caused hundreds of deaths in HP and closed hundreds of roads; press reports of state figures give different totals depending on the date (e.g. 257 deaths reported on 14 Aug 2023, 361 on 24 Aug 2023), so no single figure is claimed here.");
  card(s, M, 1.75, 6.0, 3.4, "The gap", [
    "Monsoon rain triggers landslides across HP every year; in 2023 they caused hundreds of deaths and closed hundreds of roads",
    "Published HP studies (Kullu valley, AUC 0.79–0.91; Beas basin, AUC 0.86) produce static maps: where, not when",
    "GSI's regional landslide forecasting covered only Shimla and Kinnaur in HP as of the 2025 monsoon",
  ]);
  card(s, 6.83, 1.75, 6.0, 3.4, "Our goal and user", [
    "Every morning, score landslide risk for every 1 km cell of HP",
    "Give each of the 12 districts a level: no alert, Watch or Warning",
    "Email the district and state disaster authorities; show the map in a web app",
    "Built on free global data, so a partner organisation can run it",
  ], { fill: "E3EEEC" });
  stat(s, M, 5.3, 4.0, "195", "dated HP landslides (2005–2026) in our cleaned inventory", TEAL);
  stat(s, 4.67, 5.3, 4.0, "12 districts", "each to receive a daily level: none, Watch or Warning", TEAL);
  stat(s, 8.83, 5.3, 4.0, "55,253 cells", "of 1 km covering the whole state, scored every day", TEAL);
}

// 6. Response to feedback
{
  const s = content("Response to feedback", "What we changed since Presentation 2",
    "Each point of feedback was investigated, measured and fixed, not just acknowledged",
    "Our analysis of the 878 background points from Presentation 2 and of the re-audited inventory; testing comparison on slide 12.",
    "Old negatives' statistics from the Phase B notes and a later recheck. The strict-vs-easy comparison uses the same Random Forest recipes; only the testing changes.");
  table(s, [
    ["Feedback or issue", "What we found when we checked", "What we changed (Oct–Nov)"],
    ["Negative sampling has a serious issue", "Old negatives were random: median 3,868 m high (landslides: 1,228 m), 408 of 878 above 4,000 m, km away from roads", "2,167 hard negatives of two kinds: same place on a safe day, and similar slopes on the storm day"],
    ["Score looked high (RF AUC 0.895)", "Easy negatives plus random-row testing inflate the score: the same model scores 0.856 with random rows but 0.775 with whole years hidden", "All testing now hides whole years; we report the strict number"],
    ["Model used only slope and rain", "Too few factors to tell stable wet slopes from failing ones", "42 features in 9 groups (terrain, drainage, roads, rock, faults, landforms, land cover, vegetation, rain/soil/snow)"],
    ["Event dates (our own audit)", "Some dates were wrong; 2 coordinates had typos; 5 duplicates", "Inventory re-audited: 981 cleaned, dated events"],
    ["AHP maps are common (Presentation 1)", "Agreed with the literature", "AHP kept only as a baseline; contribution is daily, rain-aware prediction"],
  ], { x: M, y: 1.75, w: W - 2 * M, colW: [3.0, 4.9, 4.433], fontSize: 12.5 });
  card(s, M, 5.55, W - 2 * M, 1.1, "Net effect", [
    "A lower but honest score (0.775 instead of 0.856–0.895), from a model whose behaviour we can check: what it learned, where it fails, and why",
  ], { size: 13.5, bullets: false });
}

// 7. Reconciliation
{
  const s = content("Response to feedback", "Numbers that changed since Presentation 2, and why",
    "Every figure in this deck that differs from Presentation 2 is listed here with the reason; one earlier description was wrong",
    "Our Presentation 2 deck; our re-audit of the inventory and of the Presentation 2 background points.",
    "Background points: Presentation 2 said they were sampled inside the HP boundary with a 500 m buffer; mapping the file (slide 10) shows them over HP, Uttarakhand, J&K and beyond. The AHP baseline (Presentation 2, slide 4) has not yet been scored on the same test as the new model; that comparison is planned for the final report.");
  table(s, [
    ["Item", "Presentation 2", "Now", "Why it changed"],
    ["Dated landslide events", "886", "981", "A corrected date parser recovered more exact dates; the audit then removed 5 duplicates and 1 undatable event"],
    ["No-landslide examples", "878 random points", "2,167 hard negatives", "Instructor's feedback (slides 10–11)"],
    ["Features", "5 (slope + 4 rain windows)", "42 (38 used by the model)", "Full set of terrain, geology, land-cover and weather factors"],
    ["Best score (ROC AUC)", "0.895 (random rows)", "0.801 full / 0.775 live (whole years hidden)", "Harder negatives and stricter testing (slide 12)"],
    ["Most important factor", "30-day rain", "Rain on the day; road distance", "The old negatives were dry mountain tops, so long-term rain looked decisive (slide 20)"],
    [{ text: "Where the 878 background points were", options: { bold: true, color: RED } }, "'Inside HP, 500 m buffer'", { text: "Spread over HP, UK, J&K and beyond", options: { bold: true, color: RED } }, "Our earlier description was wrong; corrected here"],
    ["Rain 'trigger-consistency' check", "23.6% vs 11.7%", "Dropped", "It used the wrongly parsed dates; with correct dates it reverses"],
    ["AHP terrain baseline", "6-factor map", "Kept as baseline", "Not yet scored on the same test as the new model (final report)"],
  ], { x: M, y: 1.75, w: W - 2 * M, colW: [2.75, 2.25, 2.85, 4.483], fontSize: 12 });
}

// 8. System overview
{
  const s = content("Approach", "System overview: from records to daily district alerts",
    "The full chain is built up to a whole-HP daily map; the automatic daily run and email are next",
    "Data providers: NASA (GPM IMERG), UC Santa Barbara (CHIRPS), NOAA (GFS), ECMWF (ERA5-Land), ESA/Copernicus, USGS (Landsat), GSI, OpenStreetMap; computed in Google Earth Engine.",
    "Daily automation (GitHub Actions, email, Earth Engine map app) is designed and not yet running.");
  const steps = [
    ["Landslide records", "981 dated events, 3 states", "Done", GREEN],
    ["Features (GEE)", "42 per event, at its own date", "Done", GREEN],
    ["Training table", "969 slides + 2,167 negatives", "Done", GREEN],
    ["Model", "Random Forest, tested by year", "Done", GREEN],
    ["Daily HP scoring", "55,253 cells of 1 km", "Tested on 2 days", ORANGE],
    ["District levels", "Watch / Warning per district", "Provisional", ORANGE],
    ["Email + map app", "To disaster authorities", "Next", GREY],
  ];
  const bw = 1.62, gap = 0.17, y = 2.2;
  steps.forEach(([t, d, st, c], i) => {
    const x = M + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: 1.9, rectRadius: 0.1, fill: { color: MIST }, line: { color: "CFDAD8" } });
    s.addText(t, { x: x + 0.08, y: y + 0.12, w: bw - 0.16, h: 0.65, fontSize: 14, bold: true, color: TEAL, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(d, { x: x + 0.08, y: y + 0.8, w: bw - 0.16, h: 0.7, fontSize: 12, color: INK, align: "center", valign: "top", isTextBox: true, margin: 0 });
    chip(s, x + (bw - 1.55) / 2, y + 1.48, st, c);
    if (i < steps.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + 0.02, y: y + 0.85, w: 0.13, h: 0.22, fill: { color: GREY }, line: { color: GREY } });
  });
  card(s, M, 4.5, 6.0, 2.1, "Data used (all free)", [
    "Rain: NASA GPM IMERG (half-hourly), CHIRPS; forecast: NOAA GFS",
    "Terrain: Copernicus DEM 30 m, MERIT Hydro; land: ESA WorldCover, Landsat",
    "Geology: GSI National Geoscience Data Repository; roads: OpenStreetMap",
  ], { size: 12.5 });
  card(s, 6.83, 4.5, 6.0, 2.1, "Tools", [
    "Google Earth Engine (Python API) for all geodata, on Google's servers",
    "Python (scikit-learn) for models; every step scripted and logged",
    "Planned: GitHub Actions for the daily run, email alerts, an Earth Engine map app",
  ], { size: 12.5 });
}

// =====================================================================
section("Data");

// 9. Inventory
{
  const s = content("Data", "Building a dated landslide inventory",
    "A warning model needs landslides with exact dates; only 1.7% of HP's national records had one, so we pooled two sources and two similar states",
    "GSI Bhusanket inventory (bhusanket.gsi.gov.in); NASA Global Landslide Catalog (Kirschbaum et al. 2015); Survey of India sheet grid for coordinate checks.",
    "State selection: stage 1 same Himalayan thrust system (MBT/MCT) as HP; stage 2 similarity = 1 - |share of rain-triggered slides(state) - share(HP)|.");
  const funnel = [
    ["904-page PDF", "GSI Bhusanket national inventory"],
    ["36,071 records", "extracted; HP 6,607"],
    ["HP: 114 with a day-level date", "only 1.7%; most give month and year only"],
    ["+ NASA Global Landslide Catalog", "all dated; filtered by location accuracy"],
    ["981 cleaned events", "HP 195 · Uttarakhand 548 · J&K 238"],
  ];
  funnel.forEach(([a, b], i) => {
    const w = 6.2 - i * 0.55, x = M + (6.2 - w) / 2, y = 1.8 + i * 0.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.82, rectRadius: 0.08, fill: { color: i === 4 ? TEAL : MIST }, line: { color: i === 4 ? TEAL : "CFDAD8" } });
    s.addText([{ text: a, options: { bold: true, breakLine: true, fontSize: 15, color: i === 4 ? WHITE : TEAL } }, { text: b, options: { fontSize: 12, color: i === 4 ? "D7E6E3" : INK } }],
      { x, y, w, h: 0.82, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  card(s, 7.0, 1.8, 5.83, 2.45, "Why add Uttarakhand and J&K", [
    "HP alone has too few dated slides to learn from",
    "Chosen by a method, not by eye: (1) same Himalayan thrust system as HP; (2) similar share of rain-triggered slides",
    "Ladakh (12 points, cold desert) is left out of training",
  ], { size: 12.5 });
  card(s, 7.0, 4.4, 5.83, 2.2, "Cleaning (all logged)", [
    "Dates parsed to the day; impossible dates removed",
    "2 coordinate typos fixed against Survey of India sheets; 1 wrong year fixed; 5 duplicates removed",
    "242 of 981 events fall on one day (16 Jun 2013), so testing must hide whole storms or years",
  ], { size: 12.5 });
}

// 10. Features
{
  const s = content("Data", "42 features per event, computed at each event's own date",
    "Each feature group has a published basis or a data test, and the same code serves training and the daily map",
    "Reichenbach et al. 2018; Froude and Petley 2018; Stanley et al. 2021 (LHASA v2); data providers on slide 7.",
    "Checks: curvature tested on artificial surfaces (revealed and fixed a kernel-orientation error); stream threshold calibrated against OpenStreetMap streams in 4 areas (F1 0.75); 516 rock descriptions mapped to GLiM classes by explicit rules; NDVI from the 365 days before each event so the scar cannot leak in; rain on the event day uses the local Indian day. The daily map uses the same code, checked to give identical values (100 of 100).");
  table(s, [
    ["Group (count)", "Features", "Source", "Why it matters"],
    ["Terrain (9)", "elevation, slope, aspect, curvature, position, wetness index", "Copernicus DEM 30 m, MERIT Hydro", "Core landslide factors (Reichenbach et al. 2018)"],
    ["Drainage (2)", "distance to stream, height above stream", "MERIT Hydro", "Toe erosion, saturation"],
    ["Roads (2)", "distance to any road, to a major road", "OpenStreetMap", "Road cuts destabilise slopes (Froude and Petley 2018)"],
    ["Rock (2)", "rock class, main rock", "GSI geology 1:50k", "Weak vs strong rock"],
    ["Faults (2)", "distance to fault, to thrust", "GSI geology 1:50k", "Fractured rock near faults"],
    ["Landforms (1)", "landform class", "GSI geomorphology 1:250k", "Dissected hills fail more"],
    ["Land cover (2)", "class at point, local majority", "ESA WorldCover 2021", "Vegetation, built-up"],
    ["Vegetation (2)", "NDVI over the 365 days before", "Landsat 5/7/8/9", "Root strength; no post-event leakage"],
    ["Rain, soil, snow (18)", "rain on the day and 1–30 days before; soil water; snow", "GPM IMERG, CHIRPS, ERA5-Land", "The daily trigger (as in NASA LHASA v2)"],
    ["Data flags (2)", "rain-data completeness", "IMERG", "Removed before modelling"],
  ], { x: M, y: 1.75, w: W - 2 * M, colW: [2.1, 4.1, 2.9, 3.233], fontSize: 11.5 });
}

// =====================================================================
section("Method");

// 11. Old vs new negatives
{
  const s = content("Method: negative examples", "Why the old 'no-landslide' examples were wrong",
    "Random negatives sat on high, icy, remote ground, so a model could score well without learning anything about rain",
    "Our analysis of the 878 background points used in Presentation 2 and of the new negatives (elevation: Copernicus DEM; roads: OpenStreetMap).",
    "Median elevation rechecked (3,866 m, 406 above 4,000 m). The median road distance of 4.8 km is over all points; counting only the 755 inside our road layers it is 2.6 km.");
  pic(s, "negatives_before_after.png", M, 1.75, 8.3, 4.6, 2.029);
  const x = 9.0;
  stat(s, x, 1.8, 3.8, "3,868 m", "median height of old negatives (landslides: 1,228 m)", RED);
  stat(s, x, 3.2, 3.8, "408 of 878", "old negatives above 4,000 m: snow, glaciers, bare rock", RED);
  stat(s, x, 4.6, 3.8, "4.8 km", "median distance to a road (landslides: 22 m)", RED);
  caption(s, "Blue: recorded landslides. Left: old random negatives. Right: new 'similar place, storm day' negatives.", M, 6.4, 8.3);
}

// 12. Hard negative design
{
  const s = content("Method: negative examples", "New design: two kinds of 'hard' negatives",
    "One kind teaches WHEN (same place, safe day), the other teaches WHERE (similar slope, storm day)",
    "Steger et al. 2024, Geoscience Frontiers 15(3):101822; Zhu et al. 2024, Geomatics, Natural Hazards and Risk 15(1); thresholds from our own landslide data.",
    "10.9 degrees and 284 m are the 10th and 90th percentiles of our own landslides; 5 km, 30 days and 2 km are judgement values. Fixed random seed 20261022.");
  card(s, M, 1.75, 6.0, 3.25, "Type 1: same place, safe day (969)", [
    "Exactly the landslide's location, on a different day",
    "No recorded slide within 5 km and 30 days of that day",
    "Months follow the landslides' mix (88% June–September), so many safe days are rainy too",
    "Only the weather differs, so this measures how well the model reads rain",
  ], { size: 13 });
  card(s, 6.83, 1.75, 6.0, 3.25, "Type 2: similar place, storm day (1,198)", [
    "A random spot in the same state on the landslide's date",
    "Slope at least 10.9° and within 284 m of a motorable road (like 90% of our slides)",
    "At least 2 km from any recorded slide; at most 10 per storm day",
    "The storm is shared, so this teaches which ground fails",
  ], { size: 13 });
  table(s, [
    ["Median rain (IMERG, mm)", "On the day", "7 days before", "30 days before"],
    ["Recorded landslides", "34", "89", "217"],
    ["Type 1: same place, safe day", "1.5", "30", "145"],
    ["Type 2: similar place, storm day", "8", "65", "269"],
  ], { x: M, y: 5.2, w: 8.0, colW: [3.5, 1.5, 1.5, 1.5], fontSize: 12 });
  s.addText("Training table: 969 landslides + 2,167 negatives = 3,136 rows. All rules re-checked: 0 violations.", { x: 8.8, y: 5.25, w: 4.03, h: 1.3, fontSize: 13.5, bold: true, color: TEAL, valign: "middle", isTextBox: true, margin: 0 });
}

// 13. Fair testing
{
  const s = content("Method: testing", "Honest testing: hide whole years, not random rows",
    "Rows from the same storm share weather; testing on random rows lets the model 'see' the storm it is scored on",
    "Roberts et al. 2017, Ecography 40(8):913–929; Brenning 2005, NHESS 5:853–862; our cross-validation results (whole years held out).",
    "Year-blocked 5-fold cross-validation: every row is scored by a model that never saw its year. Same Random Forest recipes in all three tests; nothing was chosen from this comparison.");
  const yrs = ["2010", "2011", "2013", "2015", "2016", "2023", "2025"];
  s.addText("How it works (simplified):", { x: M, y: 1.8, w: 5.6, h: 0.35, fontSize: 14, bold: true, color: TEAL, isTextBox: true, margin: 0 });
  yrs.forEach((t, i) => {
    const held = t === "2013";
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M + i * 0.8, y: 2.3, w: 0.7, h: 0.6, rectRadius: 0.06, fill: { color: held ? ORANGE : MIST }, line: { color: held ? ORANGE : "CFDAD8" } });
    s.addText(t, { x: M + i * 0.8, y: 2.3, w: 0.7, h: 0.6, fontSize: 12, bold: true, color: held ? WHITE : TEAL, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addText([
    { text: "Grey years: train the model. ", options: { bold: true } },
    { text: "Orange year: scored by that model, which never saw any storm of that year. Repeat until every year has been scored once; then compute one score over all rows.", options: {} },
  ], { x: M, y: 3.05, w: 5.6, h: 1.1, fontSize: 13, color: INK, isTextBox: true, margin: 0 });
  card(s, M, 4.3, 5.6, 2.3, "What the chart shows", [
    "Same model, three ways of testing",
    "Random rows: 0.856 (live) and 0.880 (full model)",
    "Whole years hidden: 0.775 and 0.801, the numbers we report",
    "The gap (about 0.08) is the optimism of the easy test",
  ], { size: 13 });
  s.addChart(pres.charts.BAR, [
    { name: "Live model (28 features)", labels: ["Whole years hidden (ours)", "Whole storm days hidden", "Random rows (easy)"], values: [0.775, 0.792, 0.856] },
    { name: "Full model (38 features)", labels: ["Whole years hidden (ours)", "Whole storm days hidden", "Random rows (easy)"], values: [0.801, 0.819, 0.880] },
  ], Object.assign({}, CHART, {
    x: 6.5, y: 1.75, w: 6.33, h: 4.85, barDir: "col", barGrouping: "clustered", chartColors: [TEAL, ORANGE],
    dataLabelFontSize: 11, dataLabelFormatCode: "0.000", valAxisMinVal: 0.5, valAxisMaxVal: 0.95, catAxisLabelFontSize: 11,
    valAxisTitle: "ROC AUC (0.5 = coin toss)", title: "Same models, three tests",
  }));
}

// 14. Model comparison
{
  const s = content("Method: model choice", "Three model types, compared fairly",
    "XGBoost scored highest but leaned on roads instead of rain; we chose Random Forest",
    "Breiman 2001 (Random Forest); Chen and Guestrin 2016 (XGBoost); Stanley et al. 2021 (LHASA v2); our cross-validation results (whole years held out).",
    "Weather-only test: landslides vs same-place safe days, where road distance is identical. Rule fixed before running: 'clearly worse' if lower AUC and the 95% interval of the difference (2,000 resamples of whole years) lies entirely below zero. XGBoost with roads: -0.031 vs road-free logistic regression (interval -0.061 to -0.009) and -0.029 vs road-free Random Forest (-0.044 to -0.010).");
  table(s, [
    ["Model (38 features, whole years hidden)", "ROC AUC, all", "ROC AUC, HP", "Without road features", "Weather-only test", "Verdict"],
    ["Logistic regression", "0.780", "0.753", "0.762", "0.744", "Baseline"],
    [{ text: "Random Forest", options: { bold: true } }, { text: "0.801", options: { bold: true } }, { text: "0.790", options: { bold: true } }, "0.755", { text: "0.746", options: { bold: true } }, { text: "Chosen", options: { bold: true, color: GREEN } }],
    ["XGBoost", "0.807", "0.804", "0.737", { text: "0.722", options: { color: RED, bold: true } }, { text: "Clearly worse on weather-only test", options: { color: RED } }],
  ], { x: M, y: 1.8, w: W - 2 * M, colW: [3.4, 1.4, 1.4, 1.9, 1.7, 2.533], fontSize: 13 });
  card(s, M, 4.1, 6.0, 2.5, "The weather-only test", [
    "A daily warning lives or dies on reading the weather",
    "Landslide days vs safe days at the same places: roads, rock and slope are identical, only the weather differs",
    "The rule for 'clearly worse' was fixed before the test",
  ], { size: 13 });
  card(s, 6.83, 4.1, 6.0, 2.5, "Why Random Forest", [
    "Almost as good overall as XGBoost (0.801 vs 0.807)",
    "Not worse than road-free models at reading the weather; XGBoost was",
    "Fewer false alarms on HP safe days at the same catch rate",
  ], { size: 13 });
}

// 15. Road bias
{
  const s = content("Method: reporting bias", "The road bias in landslide records, and how we correct for it",
    "Slides are recorded where they hit roads; we keep road distance in training but score every cell as if it were watched like a roadside slope",
    "Steger et al. 2017, Landslides 14:1767–1781; Steger et al. 2021, Sci. Total Environ. 776:145935; our cross-validation results (whole years held out).",
    "Road-neutral scoring sets both road distances to the training landslides' median at prediction time. Adding remote negatives was rejected: almost all landslides are near roads, so the model would learn 'remote = safe' through other features. Real-road scores are kept as a second map layer, 'where slides are likely to hit roads'.");
  stat(s, M, 1.85, 3.0, "22 m", "median distance of a recorded landslide to a road", RED);
  stat(s, M, 3.25, 3.0, "1st / 2nd", "rank of 'distance to major road' among 38 features in every model", RED);
  stat(s, M, 4.65, 3.0, "70 (9 in HP)", "recorded slides more than 500 m from a road: few to test remote skill with", GREY);
  table(s, [
    ["Live model; same safe-day false alarms (16%)", "Real road distances", "Road-neutral"],
    ["All recorded slides caught", "37%", "49%"],
    ["Remote slides caught (> 500 m from road)", "29%", "36%"],
    ["Weather-only test (ROC AUC)", "0.683", "0.741"],
    ["Other slopes flagged on storm days", "3%", "18%"],
  ], { x: 3.9, y: 1.85, w: 8.93, colW: [4.73, 2.1, 2.1], fontSize: 13 });
  card(s, 3.9, 4.4, 8.93, 2.2, "Decision and its cost", [
    "Road-neutral scores drive the whole-HP map and the district alerts; real-road scores kept as a second layer",
    "Gain: more slides caught, including remote ones, at the same false-alarm rate on safe days",
    "Cost: on storm days much more of the map is flagged; remote false alarms cannot be measured",
  ], { size: 12.5 });
}

// 16. Live vs full
{
  const s = content("Method: live data", "Live model: only data available on the morning it runs",
    "Two rain and soil sources arrive weeks late, so the daily system uses a slightly weaker 'live' model",
    "Data delays checked in the Google Earth Engine catalogue (Oct 2026); our cross-validation results (whole years held out).",
    "GFS rain totals reset every 6 hours, so a day's forecast is the sum of the four 6-hour totals (tested at three wet locations). Training always uses observed rain only; forecast rain is used only in the live run for the most recent days.");
  table(s, [
    ["Data", "Delay in Earth Engine", "Usable every morning?"],
    ["NASA GPM IMERG rain", "about 2 days", { text: "Yes", options: { color: GREEN, bold: true } }],
    ["NOAA GFS forecast rain", "runs complete in 6–12 h", { text: "Yes (fills the last 2 days, today, tomorrow)", options: { color: GREEN, bold: true } }],
    ["ERA5-Land soil moisture, snow", "about 12 days", { text: "No", options: { color: RED, bold: true } }],
    ["CHIRPS rain", "about 24 days (monthly)", { text: "No", options: { color: RED, bold: true } }],
  ], { x: M, y: 1.8, w: 6.2, colW: [2.4, 1.9, 1.9], fontSize: 12.5 });
  table(s, [
    ["Whole years hidden", "Full model (38)", "Live model (28)"],
    ["ROC AUC, all states", "0.801", "0.775"],
    ["ROC AUC, HP", "0.790", "0.763"],
    ["Weather-only test", "0.746", "0.683"],
    ["HP safe days flagged at Watch", "16%", "26%"],
    ["HP safe days flagged at Warning", "5%", "13%"],
  ], { x: 7.0, y: 1.8, w: 5.83, colW: [2.63, 1.6, 1.6], fontSize: 12.5 });
  card(s, M, 4.95, W - 2 * M, 1.65, "What this means", [
    "The full model is the best possible with complete data; the live model is what can actually run each day. We report both.",
    "The cost of the delays: the same share of slides is caught, with more false alarms (26% vs 16% of safe days at Watch).",
    "Rejected: putting IMERG values into the CHIRPS slots; in these mountains the two correlate only 0.53–0.75.",
  ], { size: 12.5 });
}

// 17. Alert levels
{
  const s = content("Method: alert levels", "Two alert levels, set provisionally",
    "Watch and Warning trade missed slides against false alarms; final values will be set from storm replays with rules fixed in advance",
    "NASA GES DISC, Global Landslide Nowcast (LHASA) README; Kirschbaum and Stanley 2018, Earth's Future 6:505–523; our cross-validation results (whole years held out).",
    "'False alarms per month at one spot' = safe-day false-alarm rate x 30 (a proxy for a landslide-prone spot, mostly monsoon months); real district counts come from the replays. Replay criteria written on 24 Oct, before any replay.");
  table(s, [
    ["Level (HP, chosen model)", "Score", "HP slides caught", "HP safe days flagged", "About false alarms per month at one spot"],
    [{ text: "Watch: be ready", options: { bold: true, color: BROWN } }, "≥ 0.35", "55%", "16%", "4.8"],
    [{ text: "Warning: act", options: { bold: true, color: RED } }, "≥ 0.45", "33%", "5%", "1.5"],
  ], { x: M, y: 1.8, w: W - 2 * M, colW: [3.2, 1.4, 2.0, 2.4, 3.333], fontSize: 13.5 });
  card(s, M, 3.4, 6.0, 3.2, "Why provisional", [
    "Levels are set per 1 km cell, but alerts go out per district",
    "The district rule (now: a district is alerted when 5% of its cells are) proved far too loose on the storm day",
    "Both are fixed together after replaying several storms and quiet periods",
  ], { size: 13 });
  card(s, 6.83, 3.4, 6.0, 3.2, "Rules for the replays, written before running them", [
    "Hit: the district is at Watch or higher on the event day or the day before",
    "Quiet days: count alert days on monsoon days with no recorded slide",
    "Each storm scored by a model that never saw its year",
    "Context: NASA's LHASA detected 8–60% of catalogued landslides",
  ], { size: 13, fill: "FDF1E6", hcolor: BROWN });
}

// =====================================================================
section("Results");

// 18. Research questions
{
  const s = content("Results: research questions", "Our three research questions: where they stand",
    "RQ1 is answered: rainfall is what makes daily timing possible, and adds a little to locating slides; RQ2 and RQ3 are not started",
    "Research questions as set in our Presentation 1; our cross-validation results (whole years held out).",
    "Fair RQ1 test: landslides vs other slopes on the same storm days, trained without the same-place twins, whole years hidden. A first run on all rows gave a terrain-only score below 0.5 because each landslide's same-place twin (identical terrain, opposite label) is in training when it is tested; it was not a fair test and is recorded as such. The terrain score includes road distance, so it carries the reporting bias of slide 14.");
  table(s, [
    ["Research question (Presentation 1)", "Status", "Answer so far"],
    ["RQ1: Does past and forecast rain improve prediction beyond terrain alone?", { text: "Answered (past rain)", options: { bold: true, color: GREEN } }, "WHEN a slide happens can only come from rain (terrain is the same every day). For WHERE on a storm day, rain adds a little on top of terrain (chart). Forecast rain: live system only, to be measured in the replays"],
    ["RQ2: Can activity records tell new slides from reactivated ones?", { text: "Not started", options: { bold: true, color: BROWN } }, "Needs the inventory's free-text movement and activity fields cleaned first"],
    ["RQ3: Which terrain, land-use change and rain combinations go with persistent movement?", { text: "Not started", options: { bold: true, color: BROWN } }, "Land-cover change needs more than the two WorldCover years (2020, 2021) available"],
  ], { x: M, y: 1.75, w: 7.4, colW: [2.6, 1.3, 3.5], fontSize: 11.5 });
  s.addChart(pres.charts.BAR, [
    { name: "All three states", labels: ["Terrain only", "+ vegetation", "+ IMERG rain", "+ all rain, soil, snow"], values: [0.912, 0.918, 0.926, 0.928] },
    { name: "HP rows", labels: ["Terrain only", "+ vegetation", "+ IMERG rain", "+ all rain, soil, snow"], values: [0.858, 0.853, 0.870, 0.877] },
  ], Object.assign({}, CHART, {
    x: 8.1, y: 1.75, w: 4.73, h: 4.85, barDir: "col", barGrouping: "clustered", chartColors: [TEAL, ORANGE],
    dataLabelFontSize: 10, dataLabelFormatCode: "0.00", valAxisMinVal: 0.8, valAxisMaxVal: 0.95, catAxisLabelFontSize: 10,
    valAxisTitle: "ROC AUC", title: "RQ1: landslides vs other slopes on storm days", titleFontSize: 12,
  }));
}

// 19. Baseline
{
  const s = content("Results: baseline", "Does the model beat a simple rain rule?",
    "Rain alone tells WHEN a slide happens about as well as any model; the model adds WHERE",
    "IMD national bulletins (heavy rain: 64.5–115.5 mm per day); our cross-validation results (whole years held out).",
    "Rule family: 'rain on the day >= threshold' (IMERG, local Indian day). Two tests on HP rows: WHEN = landslides vs same-place safe days; WHERE + WHEN = landslides vs all negatives. Diagnosis: the live model trained only on landslides vs safe days reaches timing 0.802 in HP, equal to rain alone; mixing in storm-day negatives, which are as wet as the slides, made the single model weigh rain less.");
  const labels = ["Rain on the day (rule)", "Single model, full data", "Single model, live", "Single, live, road-neutral", "Two-part, live", "Two-part, live, road-neutral"];
  s.addChart(pres.charts.BAR, [
    { name: "WHEN: slide day vs safe day at the same place", labels, values: [0.805, 0.788, 0.705, 0.779, 0.717, 0.781] },
    { name: "WHERE + WHEN: slides vs all negatives", labels, values: [0.675, 0.790, 0.763, 0.699, 0.777, 0.707] },
  ], Object.assign({}, CHART, {
    x: M, y: 1.75, w: 8.4, h: 4.85, barDir: "col", barGrouping: "clustered", chartColors: [NAVY, ORANGE],
    dataLabelFontSize: 10, dataLabelFormatCode: "0.00", valAxisMinVal: 0.5, valAxisMaxVal: 0.9, catAxisLabelFontSize: 10,
    valAxisTitle: "ROC AUC, HP rows (0.5 = coin toss)", title: "Himachal Pradesh, whole years hidden",
  }));
  card(s, 9.1, 1.75, 3.73, 4.85, "What we learn", [
    "WHEN: rain on the day alone (0.805) is as good as or better than every model",
    "WHERE + WHEN: every model beats rain alone (up to 0.79 vs 0.68)",
    "Why: half our negatives are other slopes on the same storm days, as wet as the slides, so one model learns to weigh rain less",
    "No model can time slides better than its rain input; satellite rain pixels are about 10 km wide",
  ], { size: 12 });
}

// 20. Two-part model
{
  const s = content("Results: model structure", "A two-part model: WHERE × WHEN",
    "Splitting the questions, as NASA's LHASA does, improves the overall score and halves wrong flags on other slopes",
    "Kirschbaum and Stanley 2018, Earth's Future 6:505–523; our cross-validation results (whole years held out).",
    "WHERE part: Random Forest, landslides vs other slopes on storm days, fixed features + NDVI + glacier flag (21). WHEN part: landslides vs same-place safe days, IMERG rain only (7), logistic regression on log rain. Two WHEN variants (Random Forest 0.793, logistic 0.813 overall) were compared on the same test folds, so the chosen variant's score is slightly optimistic. Candidate for the final live model; not yet adopted.");
  const boxes = [["WHERE", "Which slopes fail?", "Landslides vs other slopes on the same storm day; terrain, rock, roads, vegetation", MIST, TEAL],
    ["WHEN", "Which days are dangerous?", "Landslides vs safe days at the same place; rain only", "FDF1E6", BROWN]];
  boxes.forEach(([h, q, d, f, c], i) => {
    const x = M + i * 3.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.85, w: 2.9, h: 2.3, rectRadius: 0.1, fill: { color: f }, line: { color: f } });
    s.addText([{ text: h, options: { bold: true, fontSize: 22, color: c, breakLine: true } }, { text: q, options: { bold: true, fontSize: 14, color: INK, breakLine: true } }, { text: d, options: { fontSize: 13, color: INK } }],
      { x: x + 0.15, y: 1.95, w: 2.6, h: 2.1, valign: "top", isTextBox: true, margin: 0 });
  });
  s.addText("×", { x: 3.4, y: 2.6, w: 0.45, h: 0.6, fontSize: 32, bold: true, color: GREY, align: "center", isTextBox: true, margin: 0 });
  s.addText("= daily risk score", { x: M, y: 4.25, w: 6.25, h: 0.4, fontSize: 15, bold: true, color: TEAL, align: "center", isTextBox: true, margin: 0 });
  table(s, [
    ["Live data, whole years hidden", "Single model", "Two-part model"],
    ["ROC AUC, all states", "0.775", "0.813"],
    ["ROC AUC, HP", "0.763", "0.777"],
    ["HP safe days flagged (55% caught)", "25.6%", "21.5%"],
    ["Other slopes flagged on storm days", "13.9%", "7.4%"],
    ["Timing (HP); rain alone 0.805", "0.705", "0.717"],
  ], { x: 7.0, y: 1.85, w: 5.83, colW: [3.03, 1.4, 1.4], fontSize: 12.5 });
  card(s, M, 4.85, W - 2 * M, 1.75, "Reading", [
    "Better overall and fewer wrong flags on other slopes: a real improvement, and a structure used by an operational system",
    "Timing improves only slightly: the satellite rain data, not the algorithm, limits how well slides can be timed",
    "Status: candidate for the final live model; to be confirmed in the storm replays",
  ], { size: 12.5 });
}

// 21. Partial dependence
{
  const s = content("Results: physics check", "Physics check: what the model learned",
    "Rain effects look physical; two odd curves trace back to how the negatives were sampled",
    "Our partial-dependence analysis of the live model.",
    "Partial dependence: the average score when one input is varied over its 5th-95th percentile range while the others keep their observed values. 30-day rain: storm-day negatives are as wet over 30 days as the landslides (median 269 vs 217 mm). Slope spike near 10 degrees: storm-day negatives were only drawn on slopes of at least 10.9 degrees. Both are reasons to revisit the negative design for the final version.");
  pic(s, "pdp_panel.png", M, 1.75, W - 2 * M, 2.95, 4.211);
  const items = [
    ["Rain on the day", "Score doubles (0.23 to 0.46), steepest between 10 and 40 mm, then levels off", "Physical", GREEN],
    ["Rain in the 7 days before", "Steady rise (0.28 to 0.36): wet ground fails more easily", "Physical", GREEN],
    ["Rain in the 30 days before", "Flat: storm-day negatives are just as wet over 30 days", "Sampling artefact", ORANGE],
    ["Slope", "Spike near 10° (negatives only drawn on slopes ≥ 10.9°); gentle rise above 30°", "Partly artefact", ORANGE],
  ];
  items.forEach(([h, d, st, c], i) => {
    const x = M + i * 3.12;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.85, w: 2.95, h: 1.75, rectRadius: 0.08, fill: { color: MIST }, line: { color: MIST } });
    s.addText(h, { x: x + 0.12, y: 4.92, w: 2.71, h: 0.35, fontSize: 13, bold: true, color: TEAL, isTextBox: true, margin: 0 });
    s.addText(d, { x: x + 0.12, y: 5.28, w: 2.71, h: 0.85, fontSize: 12.5, color: INK, valign: "top", isTextBox: true, margin: 0 });
    chip(s, x + 0.12, 6.18, st, c);
  });
}

// 22. Storm map
{
  const s = content("Results: whole-HP map", "Whole-HP risk map for a real disaster day: 14 Aug 2023",
    "With a model that never saw 2023, all 31 recorded slides fall in alert cells, but two-thirds of the state is flagged",
    "Our model run on NASA GPM IMERG V07 rainfall for all HP cells (Google Earth Engine); recorded slides: GSI Bhusanket, NASA Global Landslide Catalog.",
    "Live model retrained without any 2023 rows; road-neutral scoring; levels matched to the live levels' HP safe-day false alarms (Watch 0.376, Warning 0.463). All 55,253 cells scored. Real-road layer: 10 of 31 slides in alert cells (grid-cell centres are often farther from a road than the slide itself). One day is an illustration, not a validation.");
  pic(s, "storm_20230814_v2_rain.png", M, 1.7, 4.3, 4.3, 1.062);
  pic(s, "storm_20230814_v2_road_neutral.png", 4.95, 1.7, 4.3, 4.3, 1.062);
  caption(s, "Left: rain on the day (IMERG). Right: risk levels; circles = recorded slides.", M, 6.05, 8.75);
  stat(s, 9.55, 1.8, 3.3, "31 of 31", "recorded slides in Watch or Warning cells (29 at Warning)", GREEN);
  stat(s, 9.55, 3.2, 3.3, "66.8%", "of HP's cells at Watch or above (47.2% at Warning)", RED);
  stat(s, 9.55, 4.6, 3.3, "12 of 12", "districts at Warning under the provisional 5% rule: too loose", RED);
}

// 23. Storm vs quiet
{
  const s = content("Results: whole-HP map", "Storm day vs quiet day, same model and levels",
    "The system lights up on the disaster day and stays calm on a quiet day; rainy days without slides are the next test",
    "Our model runs for 14 Aug and 12 Sep 2023 on NASA GPM IMERG V07 rainfall (Google Earth Engine); recorded slides: GSI Bhusanket, NASA Global Landslide Catalog.",
    "Quiet day 12 Sep 2023: no recorded HP slide within 10 days and none in the three states within 3 days. Same model trained without 2023 and same levels as the storm day. The two-part model gives the same picture (quiet day: 0.2% of HP at Watch, 0 districts).");
  pic(s, "storm_20230814_v2_road_neutral.png", M, 1.75, 3.1, 3.1, 1.062);
  pic(s, "storm_20230912_v2_road_neutral.png", 3.5, 1.75, 3.1, 3.1, 1.062);
  s.addText([{ text: "Storm day, 14 Aug 2023", options: { bold: true, breakLine: true } }, { text: "66.8% of HP at Watch or above", options: { color: RED } }],
    { x: M, y: 4.85, w: 3.0, h: 0.6, fontSize: 13, color: INK, align: "center", isTextBox: true, margin: 0 });
  s.addText([{ text: "Quiet day, 12 Sep 2023", options: { bold: true, breakLine: true } }, { text: "0.4% of HP at Watch or above", options: { color: GREEN } }],
    { x: 3.5, y: 4.85, w: 3.1, h: 0.6, fontSize: 13, color: INK, align: "center", isTextBox: true, margin: 0 });
  caption(s, "Grey: no alert · orange: Watch · red: Warning · circles: recorded slides.", M, 5.6, 6.2);
  table(s, [
    ["", "Storm day 14 Aug 2023", "Quiet day 12 Sep 2023"],
    ["HP mean rain on the day", "40.3 mm", "0.8 mm"],
    ["HP at Watch or above", { text: "66.8%", options: { bold: true, color: RED } }, { text: "0.4%", options: { bold: true, color: GREEN } }],
    ["HP at Warning", "47.2%", "0.0%"],
    ["Districts alerted (of 12)", "12", "0"],
    ["Recorded slides in alert cells", "31 of 31", "none recorded"],
  ], { x: 6.9, y: 1.75, w: 5.93, colW: [2.33, 1.8, 1.8], fontSize: 12.5 });
  card(s, 6.9, 4.55, 5.93, 2.05, "Caveat, stated plainly", [
    "The quiet day was also nearly dry, so it shows only that the system stays calm without rain",
    "The harder test, rainy days with no slides, comes from the storm replays (next phase)",
  ], { size: 12.5, fill: "FDF1E6", hcolor: BROWN });
}

// 24. Where we stand
{
  const s = content("Results: status", "Where we stand against the original goal",
    "Coverage and honesty are on track; accuracy is moderate and limited by the data; automation is the main work left",
    "Results on slides 12–22 of this deck.",
    "Goal from the start: predict rainfall-triggered landslides for the whole of HP, as accurately as the data allow, delivered daily to authorities, with free tools. Three model types land within 0.03 AUC of each other, which points to data limits rather than the method.");
  table(s, [
    ["Original goal", "Current status", "Verdict"],
    ["Whole of Himachal Pradesh", "All 55,253 cells of 1 km scored; cells > 500 m from a road marked 'lower confidence'", { text: "On track", options: { bold: true, color: GREEN } }],
    ["As accurate as the data allow", "Live model AUC 0.775 (strict test); two-part 0.813. Rain timing capped by satellite rain; records biased to roads", { text: "Moderate; limits measured and explained", options: { bold: true, color: BROWN } }],
    ["Daily warning to authorities", "Daily scoring tested on two real days; district rule provisional; automation and email not built yet", { text: "Main remaining work", options: { bold: true, color: BROWN } }],
    ["Research questions", "RQ1 answered for past rain; RQ2 and RQ3 not started", { text: "Partly", options: { bold: true, color: BROWN } }],
    ["Honest evaluation", "Whole years hidden; rain-rule baseline; every experiment logged, including dropped and wrong ones", { text: "Achieved", options: { bold: true, color: GREEN } }],
    ["Free tools only", "Google Earth Engine, open data, Python", { text: "Achieved", options: { bold: true, color: GREEN } }],
  ], { x: M, y: 1.8, w: W - 2 * M, colW: [3.0, 6.6, 2.733], fontSize: 13 });
}

// =====================================================================
section("Limitations and next steps");

// 25. Limitations
{
  const s = content("Limitations", "Limitations",
    "We state each limit together with what it means for using the system",
    "Our analyses on slides 10–22; Kirschbaum and Stanley 2018 (LHASA detection range).",
    "Scores are relative, not daily probabilities: training has about 1 landslide per 2.2 negatives, far more than in reality.");
  const L = [
    ["Records follow roads", "Slides are recorded where they hit roads (median 22 m). Skill is measured mostly near roads; remote skill rests on 70 slides (9 in HP)."],
    ["Timing capped by rain data", "Satellite rain pixels are about 10 km; cloudbursts can be smaller. Rain alone times slides as well as our models."],
    ["Many slides missed", "About 45% of HP slides at Watch and two-thirds at Warning (published nowcasts: 8–60% detected)."],
    ["False alarms", "Live model: about 1 in 4 safe days at a landslide spot reaches Watch; storm days flag large areas."],
    ["Small, clustered sample", "195 HP slides; 242 of 981 events on one day (2013). HP numbers can move by several points."],
    ["Unrecorded slides as negatives", "'No slide recorded' is not 'no slide happened'; buffers reduce but cannot remove this."],
    ["Sampling artefacts", "30-day rain and gentle slopes are distorted by the negative design; to revisit."],
    ["Live data", "The live model is weaker than the full model; forecast rain adds errors not yet measured."],
  ];
  L.forEach(([h, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.33, y = 1.75 + row * 1.24;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 6.0, h: 1.1, rectRadius: 0.08, fill: { color: MIST }, line: { color: MIST } });
    s.addText([{ text: h, options: { bold: true, color: TEAL, fontSize: 13.5, breakLine: true } }, { text: d, options: { color: INK, fontSize: 13.5 } }],
      { x: x + 0.15, y: y + 0.06, w: 5.7, h: 1.0, valign: "top", isTextBox: true, margin: 0 });
  });
}

// 26. Mistakes
{
  const s = content("Limitations", "Mistakes we found and corrected",
    "Our own checks caught 14 mistakes (the main ones below); each was fixed and recorded, including one in Presentation 2",
    "Our own checks during the project; each change was recorded with its evidence.",
    "Every experiment, including dropped and wrong ones, is recorded in the experiments log (70+ entries).");
  table(s, [
    ["Mistake", "How we found it", "Correction"],
    ["Presentation 2 said the 878 background points were inside HP with a 500 m buffer", "Mapping the actual file", "They spread over three states and beyond; stated on slides 6 and 10"],
    ["Date coverage inflated (any text counted as a date)", "Re-audit with a day-level parser", "HP dated records: 10.4% → 1.7%"],
    ["Some event dates wrong; 'trigger-consistency' claim built on them", "October inventory audit", "981 cleaned events; claim dropped"],
    ["Random negatives too easy; score inflated (0.895)", "Instructor feedback; strict-vs-easy test", "Hard negatives; whole-year testing"],
    ["Curvature signs wrong (Earth Engine kernel orientation)", "Tests on artificial surfaces", "Kernels corrected"],
    ["Road-corridor limit shrank the whole-HP goal", "Team review, 29 Oct", "Reversed; remote cells marked lower confidence"],
    ["First RQ1 test unfair (terrain-only score below 0.5)", "Result made no physical sense", "Rerun on storm-day slopes only (slide 17)"],
    ["255 border cells dropped, then counted as a 13th district", "Count checks on the maps", "Fixed; levels for 12 real districts only"],
  ], { x: M, y: 1.75, w: W - 2 * M, colW: [5.0, 3.3, 4.033], fontSize: 11.5 });
  card(s, M, 5.05, W - 2 * M, 1.5, "Why we list them", [
    "Each mistake was caught by a check we built in: re-audits, count checks, and tests against known answers",
    "Every experiment, kept, dropped or found wrong (70+ entries), is recorded in the project files, so the results here can be traced and repeated",
  ], { size: 13 });
}

// 27. Next steps
{
  const s = content("Next steps", "Next steps to the final report",
    "Turn the tested pipeline into a running service, test it on many storms, and design how its impact would be assessed",
    "Final-report requirements from the instructor's mail.",
    "Impact assessment (final report): how warnings would be judged in use (lead time, hits and false alarms per district, actions taken), survey questions for district and state disaster authorities and the road department, a feedback format per alert, and a pilot plan suitable for a funding proposal.");
  const steps = [
    ["1", "Daily automation", "Automatic morning run, district summary, email to authorities, map app"],
    ["2", "Storm replays", "Several storms and quiet periods, each with a model that never saw that year; set final levels and district rule"],
    ["3", "Better training data", "Decide on regenerating negatives (v2); adopt the two-part model if confirmed; test IMD gridded rain; score the AHP baseline on the same test"],
    ["4", "Impact assessment", "Method, survey questions for disaster authorities and road department, alert feedback format, pilot plan"],
    ["5", "Road-blockage study", "Optional: what free satellite data can and cannot show after a slide"],
    ["6", "Final paper", "Methods, results, limitations, plus the impact-assessment section"],
  ];
  steps.forEach(([n, h, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.33, y = 1.75 + row * 1.62;
    s.addShape(pres.shapes.OVAL, { x, y: y + 0.1, w: 0.6, h: 0.6, fill: { color: TEAL }, line: { color: TEAL } });
    s.addText(n, { x, y: y + 0.1, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText([{ text: h, options: { bold: true, fontSize: 15, color: TEAL, breakLine: true } }, { text: d, options: { fontSize: 14, color: INK } }],
      { x: x + 0.8, y, w: 5.2, h: 1.45, valign: "top", isTextBox: true, margin: 0 });
  });
}

// 28. References
{
  const s = content("References", "References",
    "Every method choice above rests on one of these sources or on a data test documented in the project files",
    "All references were checked against the publisher or an index during the project.",
    "All references were checked (authors, year, journal, volume/pages or DOI) during the project.");
  const refs = [
    "Breiman, L. (2001). Random forests. Machine Learning 45, 5–32.",
    "Brenning, A. (2005). Spatial prediction models for landslide hazards. NHESS 5, 853–862.",
    "Chen, T., Guestrin, C. (2016). XGBoost: a scalable tree boosting system. Proc. KDD, 785–794.",
    "Froude, M., Petley, D. (2018). Global fatal landslide occurrence from 2004 to 2016. NHESS 18, 2161.",
    "Kirschbaum, D.B., Stanley, T., Zhou, Y. (2015). Spatial and temporal analysis of a global landslide catalog. Geomorphology 249, 4–15.",
    "Kirschbaum, D., Stanley, T. (2018). Satellite-based assessment of rainfall-triggered landslide hazard for situational awareness. Earth's Future 6, 505–523.",
    "Meena, S.R., Mishra, B.K., Blaschke, T. (2019). Landslide susceptibility mapping of the Kullu Valley, Himachal Himalayas. Geosciences 9(4), 156.",
    "Reichenbach, P. et al. (2018). A review of statistically-based landslide susceptibility models. Earth-Science Reviews 180, 60–91.",
    "Roberts, D.R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography 40(8), 913–929.",
    "Singh, M. et al. (2024). Landslide susceptibility evaluation in the Beas River Basin … AHP. Quaternary Science Advances 14, 100180.",
    "Stanley, T. et al. (2021). Data-driven landslide nowcasting at the global scale. Frontiers in Earth Science 9, 640043.",
    "Steger, S., Brenning, A., Bell, R., Glade, T. (2017). The influence of systematically incomplete shallow landslide inventories on statistical susceptibility models. Landslides 14, 1767–1781.",
    "Steger, S. et al. (2021). Correlation does not imply geomorphic causation in data-driven landslide susceptibility modelling. Science of the Total Environment 776, 145935.",
    "Steger, S. et al. (2024). Adopting the margin of stability for space–time landslide prediction. Geoscience Frontiers 15(3), 101822.",
    "Zhu et al. (2024). Considering the effect of non-landslide sample selection on landslide susceptibility assessment. Geomatics, Natural Hazards and Risk 15(1).",
    "Data: GSI Bhusanket inventory; NASA GPM IMERG V07; CHIRPS (Funk et al. 2015); ERA5-Land; Copernicus DEM; MERIT Hydro; ESA WorldCover; Landsat; GSI NGDR; OpenStreetMap; IMD national bulletins; NASA LHASA README.",
  ];
  const items = refs.map((t, i) => ({ text: t, options: { breakLine: i < refs.length - 1, paraSpaceAfter: 3 } }));
  s.addText(items, { x: M, y: 1.7, w: W - 2 * M, h: 5.0, fontSize: 11, color: INK, valign: "top", isTextBox: true, margin: 0 });
}

// ---- write, then apply the theme colors and fonts ----
(async () => {
  await pres.writeFile({ fileName: OUT });
  const applyTheme = require(process.argv[2]).applyTheme;
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
