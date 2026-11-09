# How the alerts work, in simple words

Written 9 Nov 2026 for the final report and presentation. Technical details: documentation §17.10, `CHANGELOG.md` (7 Nov 2026), `data/phaseE/`.

## 1. Every square gets a score each day
HP is divided into 55,253 squares of 1 km × 1 km. Every day the model looks at each square's slope, rock, vegetation and rain, and gives it a **risk score between 0 and 1**.
- Score **≥ 0.38** → the square is at **Watch**
- Score **≥ 0.46** → the square is at **Warning**

These two cut-offs were set earlier from how often safe days get flagged (live Random Forest, road-neutral scoring).

## 2. A district needs a rule
Alerts go to districts, not to squares. On a rainy day a district such as Mandi may have 50 squares at Watch, or 2,000. The **district rule** says when the whole district is put on alert:

> **A district is at Watch when at least 30% of its squares within 500 m of a road are at Watch.** The same for Warning.

- A 1% rule: a handful of risky squares is enough → districts alert very easily.
- A 30% rule: a large part of the district must be risky → districts alert on big, widespread rain.

## 3. How the rule was tested ("storm replays")
We went back to 32 past days and ran the system as if it had existed then:
- **16 storm days**: every HP day with 3 or more recorded landslides (2010–2025). On these days **44 districts** had at least one recorded slide.
- **16 quiet days**: random monsoon days with no recorded slide within 3 days. 16 days × 12 districts = **192 quiet district-days**.

For each candidate rule two questions were asked:
1. **Did it catch the storms?** Of the 44 districts with slides, how many were on alert that day or the day before?
2. **Did it stay quiet on quiet days?** Of the 192 quiet district-days, how many alerts went out for nothing?

The model used for each day was trained **without that year's data**, so it had never seen the storm it was tested on (like an exam with unseen questions).

## 4. Results

| District rule | Storms caught | False alarms on quiet days |
|---|---|---|
| 5% of all squares (old, temporary rule) | 43 of 44 (98%) | 84 of 192 (44%) |
| **30% of road-zone squares (chosen)**, Watch | **38 of 44 (86%)** | **28 of 192 (15%)** |
| Same rule, Warning | 32 of 44 (73%) | 3 of 192 (1.6%) |

The old rule caught almost everything but alarmed on nearly half of the quiet days: like a smoke alarm that rings every time you cook, people stop trusting it. The chosen rule misses 6 of 44 affected districts but cuts false alarms by about two-thirds. Warning is a strong signal: under 2% false alarms.

## 5. How the winner was chosen
There is always a trade-off: catching more storms means more false alarms. A standard score from warning-system research balances the two:

> **Skill score (TSS) = share of storms caught − share of false alarms**

- 30% rule: 0.86 − 0.15 = **0.72**
- 5% rule: 0.98 − 0.44 = **0.54**

Higher is better. 24 combinations were tried (2 models × 6 percentages × all squares or only squares near roads). **The scoring method was agreed before any result was seen**, so the choice was not made by picking the answer that looked best. Basis: warning systems for whole regions are judged per warning zone and per day by correct, missed and false alerts (Calvello & Piciullo 2016; Piciullo et al. 2017), and their thresholds are set by maximising such a skill score (Gariano et al. 2015).

## 6. Two honest cautions
1. **The top few rules are nearly tied.** With only 32 test days, the 20% and 30% rules and the two models perform about the same (when the test days are resampled, the winner ranks first in only 44% of draws). We can say "loose rules are clearly worse", not "30% is clearly the best".
2. **30% was the highest share tried, and the score was still rising.** A higher share might score better. Testing it after seeing the results would be changing the exam after marking it, so it was not used to choose.

Also: the 6 missed districts were local storms (Shimla 2010 and 2011, Solan 2010, Lahul & Spiti and Mandi 2025), and some "false alarms" were wet days on which slides may have happened without being recorded, so the false-alarm rate is an upper bound.

## In one line
The district rule warns on most real storms and stays quiet on most quiet days, far better than the temporary 5% rule; the small differences between the top options are within the noise.
