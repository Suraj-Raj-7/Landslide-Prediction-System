# Phase B design: "no-landslide" (negative) examples

**Date:** 22 Oct 2026 · **Author:** Suraj Raj · **Status:** approved, 22 Oct 2026

## Goal

The model learns by comparing landslide cases (label 1) with no-landslide cases (label 0). If the no-landslide cases are easy (dry days, flat ground far from roads), the model learns nothing useful. So the negatives must look like the positives in every way except "a landslide happened".

## Basis

- **Two kinds of absence: same places on other dates, and other places.** Space–time landslide models by Steger and colleagues sample absence observations "at landslide locations and at non-landslide locations" with rule-based stratification.
  - ICG2022-388: Steger, Moreno, Crespi, et al., *Applying a hierarchical Generalized Additive Model to integrate predisposing, preparatory and triggering factors for landslide prediction*.
  - Steger et al. 2024, *Adopting the margin of stability for space–time landslide prediction*, *Geoscience Frontiers* 15(3):101822, doi:10.1016/j.gsf.2024.101822 (a space–time model built on a "spatio-temporally representative sample of landslide presence and absence observations").
- **Keep negatives away from mapped landslides.** Buffer-constrained sampling outperformed whole-area random sampling (Zhu et al. 2024, *Considering the effect of non-landslide sample selection on landslide susceptibility assessment*, Huize County, *Geomatics, Natural Hazards & Risk* 15(1), doi:10.1080/19475705.2024.2392778).
- **NASA LHASA v2** (Stanley et al. 2021, *Front. Earth Sci.* 9:640043) drew negatives at random across space and time, at about 100:1, with no buffer. The authors warn that random train/test splits reduce the independence of validation. We follow that warning in Phase C by holding out whole storms or years.
- **Thresholds come from our own data** (data test on the 969 non-Ladakh positives): 88% occur in June–September; 90% lie on slopes ≥ 10.9°; 90% lie within 284 m of a road.

## Design

**Training region:** HP, Uttarakhand, UT of J&K. **Ladakh is excluded** (12 positives dropped from training).
**Date range for negatives:** 2005-01-01 to 2025-09-30, the period of *final* IMERG rainfall.

### Type 1: SAME PLACE, SAFE DAY (teaches what rain does)

- **Count:** one per positive event, so **969**.
- **Location:** the same coordinates as the positive.
- **Date:** a random date whose **month follows the positives' month mix** (88% monsoon). Many safe days are therefore rainy, which is the hard part.
- **Rule:** no recorded landslide within **5 km** and within **±30 days** of that date.
- **Speed:** dates are drawn from a **pool of about 250 dates**, so GEE processes fewer distinct days.
- **Features:** the fixed features (terrain, roads, rock, faults, landforms, land cover) are **copied from the positive's row**. Only rain, soil, snow and NDVI are computed for the new date.

### Type 2: SIMILAR PLACE, STORM DAY (teaches what terrain does)

- **Count:** **2 per positive event, at most 10 per storm date**, so **1,198**. 2013-06-16 contributes 10, not 242.
- **Date:** the storm date itself.
- **Location:** a random 30 m cell in the **same state** with:
  - slope **≥ 10.9°**;
  - distance to road **≤ 284 m**;
  - distance **≥ 2 km from any recorded landslide** on any date.
- **Features:** all 42, using the existing `extract_features`.

**Total:** about **2,167 negatives** against 969 positives, roughly 2.2 : 1.

## Known limitation

"No landslide recorded" is not the same as "no landslide happened". The inventory is incomplete, especially on storm days, so some negatives are unrecorded landslides (label noise). The 2 km buffer reduces this risk but cannot remove it.

## Output

`training_table_v1.csv` with about 3,136 rows: 969 positives (label 1) plus about 2,167 negatives (label 0). Columns: `id, label, neg_type, state, admin_unit, lat, lon, event_date` and the same 42 features.
