"""Generate GEE scripts Current/16_step3_lithology_module and 17_step3_lithology_run
from the reviewed mapping table, so the JS lookup can never drift from the CSV.
Usage: python -I make_js_lithology.py MAPPING_CSV GEE_REPO_DIR
"""
import json
import os
import sys

import lithology as LI

csv_path, repo = sys.argv[1], sys.argv[2]
glim, rock, names = LI.load_mapping(csv_path)

MODULE = """// ===================================================================
// SCRIPT:  Current/16_step3_lithology_module
// PURPOSE: Step 3 lithology features from the NGDR 1:50k LITHOLOGY layers of
//          HP, Uttarakhand, J&K and Ladakh. Each free-text 'lithologic'
//          description is mapped to a GLiM class and a main rock name through
//          the reviewed table lithology_mapping_v1.csv (embedded below).
//          Defines values only (no prints, no map layers).
//            var li = require('users/rajsuraj777/ICTD_Landslides_Project:Current/16_step3_lithology_module');
// INPUTS:  users/rajsuraj777/HP_lithology, UK_lithology, JK_lithology,
//          LADAKH_lithology (all 27 NGDR fields, identical names)
// OUTPUTS: exports.polygons(), exports.image(), exports.GLIM_ORDER,
//          exports.ROCK_NAMES, exports.BANDS
// STATUS:  IN USE from 2026-10-21.
// INDEX:   Current/00_README_index
//
// CLASSES
//   glim_code  GLiM level-1 class (Hartmann & Moosdorf 2012, Geochem. Geophys.
//              Geosyst. 13:Q12004): index in GLIM_ORDER below. 0 = nd (no data).
//   rock_code  dominant (first-listed) rock in the description: index in
//              ROCK_NAMES (0 = none). Keeps detail that GLiM's single
//              'metamorphics' class would lose (phyllite vs gneiss, etc.).
// MAPPING RULES (see lithology_mapping_v1.csv, one row per description)
//   1. The first rock term listed decides the class (dominant rock).
//   2. Siliciclastic + carbonate in one description -> sm (mixed sedimentary).
//   3. Loose-sediment words (sand, silt, clay, gravel) count as unconsolidated
//      (su) only if the polygon age is Quaternary; older -> consolidated (ss).
//   Classes are NOMINAL. Which classes are more susceptible is left to the
//   model and the landslide data, not expert scores.
// COVERAGE: 16,599 polygons, 516 descriptions; 186 polygons (1.1%, 4.0% of
//   area) are 'UNMAPPED' or vein-only -> nd. All 981 positives fall on a
//   classified polygon.
// ===================================================================

exports.ASSETS = ['users/rajsuraj777/HP_lithology', 'users/rajsuraj777/UK_lithology',
                  'users/rajsuraj777/JK_lithology', 'users/rajsuraj777/LADAKH_lithology'];
exports.GLIM_ORDER = __GLIM_ORDER__;
exports.BANDS = ['glim_code', 'rock_code'];

// ---- Lookup tables generated from lithology_mapping_v1.csv (do not hand-edit) ----
var GLIM_BY_DESC = __GLIM__;
var ROCK_BY_DESC = __ROCK__;
exports.ROCK_NAMES = __NAMES__;

var gDict = ee.Dictionary(GLIM_BY_DESC);
var rDict = ee.Dictionary(ROCK_BY_DESC);

exports.polygons = function() {
  return ee.FeatureCollection(exports.ASSETS.map(function(a) { return ee.FeatureCollection(a); }))
    .flatten()
    .map(function(f) {
      var key = ee.String(ee.Algorithms.If(f.get('lithologic'), f.get('lithologic'), '')).trim().toUpperCase();
      return f.set({glim_code: gDict.get(key, 0), rock_code: rDict.get(key, 0)});
    });
};

exports.image = function() {
  var p = exports.polygons();
  return ee.Image.cat([
    ee.Image(0).int().paint(p, 'glim_code').rename('glim_code'),
    ee.Image(0).int().paint(p, 'rock_code').rename('rock_code')
  ]);
};
"""

RUN = """// ===================================================================
// SCRIPT:  Current/17_step3_lithology_run
// PURPOSE: Step 3. Attach the lithology class of the polygon under each
//          positives_v5 point, map the classes, export the table to Drive.
// INPUTS:  Current/07_step0_config, Current/16_step3_lithology_module
// OUTPUTS: Drive > ICTD_Landslides_Project > positives_lithology_v1.csv
//          (981 rows + glim_code, rock_code, lithologic)
// STATUS:  DONE 2026-10-21 via the Python mirror (export COMPLETED).
//          Not yet run in the Code Editor.
// INDEX:   Current/00_README_index
//
// RESULTS (2026-10-21, 981 rows, 0 missing)
//   glim at positives: mt 435, sm 185, ss 178, su 120, pa 30, sc 24, pb 5,
//   vi 2, vb 2. Landslides per 1000 km2 of each class: sm 5.9, mt 5.7,
//   ss 5.4, sc 4.4, su 3.8, pa (granites) 1.3 - granites are the most stable.
// ===================================================================

var cfg = require('users/rajsuraj777/ICTD_Landslides_Project:Current/07_step0_config');
var li  = require('users/rajsuraj777/ICTD_Landslides_Project:Current/16_step3_lithology_module');

var polys = li.polygons();
var pos = ee.FeatureCollection(cfg.POSITIVES_ID);
var META = ['id', 'state', 'admin_unit', 'source', 'tier', 'lat', 'lon', 'event_date', 'event_end'];

print('Polygons (expect 16599):', polys.size());
print('Unclassified polygons (glim_code 0, expect 186):', polys.filter(ee.Filter.eq('glim_code', 0)).size());

var joined = ee.FeatureCollection(ee.Join.saveFirst('m').apply({
  primary: pos, secondary: polys,
  condition: ee.Filter.intersects({leftField: '.geo', rightField: '.geo', maxError: 10})
})).map(function(f) {
  var m = ee.Feature(f.get('m'));
  return f.set({glim_code: m.get('glim_code'), rock_code: m.get('rock_code'),
                lithologic: m.get('lithologic')}).set('m', null);
});
print('Rows with lithology (expect 981):', joined.size());
print('glim_code histogram:', joined.aggregate_histogram('glim_code'));

Map.centerObject(cfg.hp, 8);
Map.addLayer(li.image().select('glim_code').selfMask(), {min: 1, max: 15}, 'GLiM class (code)', false);
Map.addLayer(pos, {color: 'black'}, 'positives_v5');

Export.table.toDrive({
  collection: joined, description: 'positives_lithology_v1', folder: cfg.DRIVE_FOLDER,
  fileFormat: 'CSV', selectors: META.concat(['glim_code', 'rock_code', 'lithologic'])
});
"""

module = (MODULE.replace("__GLIM_ORDER__", json.dumps(LI.GLIM_ORDER))
          .replace("__GLIM__", json.dumps(glim, ensure_ascii=True, sort_keys=True))
          .replace("__ROCK__", json.dumps(rock, ensure_ascii=True, sort_keys=True))
          .replace("__NAMES__", json.dumps(names)))
for name, text in [("16_step3_lithology_module", module), ("17_step3_lithology_run", RUN)]:
    with open(os.path.join(repo, "Current", name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
print("written; descriptions", len(glim), "rock names", len(names))
