# Impact assessment: how we would find out if this warning system helps people

**Project:** Rainfall-aware landslide early warning for Himachal Pradesh (M.Tech ICTD, IIT Delhi)
**Written:** November 2026 · **Status:** a *proposed* method. Nothing here has been tested with real users yet.

**How to read this section.** The rest of the report shows that the system works *technically*: it predicts landslide days reasonably well and runs every day by itself. This section asks a different question: **would it actually make life safer for people in Himachal, and how would we check that?** It is written so that any partner (a state or district disaster office, an NGO, or a research group) could use it as the plan for a one-monsoon pilot. Words that may be new are explained in the box at the end of the section.

---

## 1. Summary
- **What exists today:** a free, automatic system that every morning scores every 1 km square of Himachal Pradesh (HP) for landslide risk today and tomorrow, puts each of the 12 districts at *no alert*, *Watch* or *Warning*, emails the result and publishes a map online.
- **Evidence it works technically:** when we replayed two full past monsoons with a model that had never seen them, the district was on alert on about **7 out of 10** days with a recorded landslide, usually **a day in advance** (§2).
- **The main risk:** it raises alerts often (a district is on alert about **1 monsoon day in 3–4**), and many of those alerts have no recorded landslide. Some are probably real landslides that nobody recorded; some are false alarms. Too many false alarms make people stop paying attention (*alert fatigue*).
- **What we propose:** a one-monsoon pilot in a few districts that measures, with simple forms and records, (1) whether the alerts reach the right people in time, (2) how many alerts match real events on the ground, (3) whether people act on them, and (4) whether that action reduces harm, such as people stuck on blocked roads.

## 2. Proof of concept: what we already know

| Evidence | Result | Where |
|---|---|---|
| Storm replays: 16 storm days, 16 quiet days (2010–2025), model trained without each year | 86% of districts with recorded landslides at Watch on the day or the day before; Watch on 15% of quiet district-days; Warning on 1.6% | `docs/alert_rule_explained.md` |
| Full-monsoon replay 2023 (15 Jun–30 Sep) | 17 of 22 district-days with a recorded landslide on alert (12 of them a day early); districts on alert on 33% of days | `docs/monsoon_replay_explained.md` |
| Full-monsoon replay 2025 | 24 of 35 caught (20 a day early); districts on alert on 26% of days | same |
| Live system | Running every morning since 9 Nov 2026 on GitHub; email + public web page; run time about 1 minute | `docs/daily_system_setup.md` |
| Cost of running | Free data (NASA IMERG rain, NOAA GFS forecast, ESA/USGS maps) and free hosting | same |

**What the technical tests cannot tell us:** whether the email reaches someone who can act, whether they trust it, what they do, and whether that prevents harm. Only a field pilot can answer these questions.

## 3. How the system is supposed to lead to impact (theory of change)
A *theory of change* is a simple chain: **if** this happens, **then** that follows. Writing it down shows exactly where the chain could break, and therefore what we must measure.

| Step | What has to happen | What could break it | What we measure (indicator) |
|---|---|---|---|
| 1. Prediction | The system flags the right districts on the right days | Missed storms; too many false alarms; rain data delays | Hit rate, false-alarm share, lead time (§5.3) |
| 2. Delivery | The alert reaches the right officer before the danger | Wrong contact; email not read; message sent too late | Share of alerts received and read within 2 hours |
| 3. Understanding and trust | The officer understands the alert and believes it | Confusing map; alert fatigue; conflict with official warnings | Survey scores on clarity and trust; trend in alerts acted on |
| 4. Action | Someone does something useful (see below) | No resources; no standard procedure; alert too vague | Share of alerts followed by at least one action; type of action |
| 5. Benefit | Fewer people harmed or stranded; roads reopened faster | The landslide hits a place where no action was taken | Stranded vehicles and people, road-closure hours, injuries (compared with earlier years) |

**Useful actions** (examples to be confirmed with officials): moving earth-movers (JCBs) close to known slide spots; closing or limiting traffic on risky road stretches at night; alerting police check-posts and bus depots; advising tourists through hotels and taxi unions; putting rescue teams on standby; checking drains and culverts.

**Who could use it:**

| User | What they could do with an alert |
|---|---|
| District Disaster Management Authority (DDMA) and district control room | Coordinate departments; issue local advisories; keep rescue on standby |
| State Disaster Management Authority (HPSDMA) and State Emergency Operation Centre | See the whole state at once; move resources between districts |
| Road agencies (PWD, Border Roads Organisation, NHAI) | Pre-position machines and staff; restrict traffic on risky stretches |
| Police and transport (state bus corporation, traffic police) | Hold or reroute buses and trucks; inform travellers |
| Panchayats, hotel and taxi associations | Pass the message to residents and tourists |
| Residents and travellers | Indirect users: they benefit through the actions above |

## 4. Where this system fits in a complete early-warning system
The UN *Early Warnings for All* initiative describes four pillars that every working early-warning system needs (UN / WMO, 2022–2027 plan). Our project covers part of the first two. The rest has to come from partners, and the pilot must include them.

| Pillar | What it means | What our system gives | What partners must bring |
|---|---|---|---|
| 1. Risk knowledge | Knowing where and why landslides happen | Terrain-based susceptibility built into the model; landslide inventory 2005–2026 | Local knowledge of known slide spots; better landslide records |
| 2. Monitoring and forecasting | Watching the hazard and forecasting it | Daily district alerts for today and tomorrow from satellite rain and forecast rain | Official forecasts (IMD rain, GSI landslide bulletins); rain gauges |
| 3. Warning communication | Getting the message to people in time, in a form they understand | Email and a web page (English) | SMS / WhatsApp, Hindi, sirens, local radio, a clear chain of who tells whom |
| 4. Preparedness and response | People know what to do and can do it | Nothing yet | Standard procedures per alert level, trained staff, machines, drills |

**Relation to official warnings.** India's official landslide forecasting is done by the Geological Survey of India (GSI) through its National Landslide Forecasting Centre, which issues regional forecast bulletins and is extending coverage to more districts. The India Meteorological Department (IMD) issues the official rain warnings. **Our system is a research prototype and decision-support tool for officials. It must not replace or contradict official warnings.** In a pilot, its alerts would go only to officials, labelled "research, not an official warning", and the evaluation would compare it with the official bulletins where they exist.

## 5. The proposed evaluation method

### 5.1 Questions the evaluation must answer
1. **Reach:** Do alerts reach the right people, on time, every day?
2. **Accuracy on the ground:** How many alerts match a real landslide or road blockage that day or the next? How many real events had no alert?
3. **Use:** Do officers act on alerts? Which actions? Does this change during the season (alert fatigue)?
4. **Benefit:** Is there less harm than in comparable situations without the alerts (stranded vehicles, closure hours, injuries)?
5. **Trust and fit:** Do users find the alerts clear and worth the effort? How does the system fit with IMD and GSI warnings?
6. **Fairness:** Are some areas or groups served worse, such as remote valleys far from roads, or people without smartphones or email?

### 5.2 Pilot design (one monsoon)
**Where:** 2 to 4 pilot districts, chosen to cover different situations, for example:
- **Mandi or Kullu:** many recorded landslides, and the alerts mostly match records.
- **Kangra or Hamirpur:** many alerts but few recorded landslides. This tests whether the "extra" alerts are false alarms or unrecorded events.

**When, in four phases:**

| Phase | Months (example) | What happens | Why |
|---|---|---|---|
| 0. Baseline | April–May | Interview officials (Appendix A, B); collect last 3 monsoons' records of road closures and landslide reports per district; agree on contacts and the alert format | We need a "before" picture to compare with |
| 1. Shadow mode | June | The system runs and is recorded, but alerts are **not** sent to users. Field reports are still collected | Checks accuracy on the ground without influencing anyone; tunes the per-district alert load before going live |
| 2. Live | July–September | Alerts go to the pilot officers every morning; every alert gets a short feedback form (Appendix D); every action goes into the log (Appendix E) | The main measurement period |
| 3. Review | October–November | End-of-season surveys (A, B, C); analysis; workshop with users; decide on changes (e.g. district-specific thresholds) | Learn and improve with evidence |

**What we compare against.** A full experiment (giving warnings to some districts and holding them back from others) is not acceptable for safety warnings. So we propose two fair comparisons:
- **Before and after:** the same district in the pilot monsoon versus the three earlier monsoons (closures, stranded vehicles, response times), adjusted for how much rain fell. A very wet year will have more damage anyway.
- **Pilot and non-pilot districts:** neighbouring districts with similar terrain that did not receive alerts. They still get all official warnings; only our extra alert is missing.

Both comparisons are imperfect, because every monsoon is different. So results are reported per district and per event, together with the qualitative evidence (interviews), not as a single number.

### 5.3 What we measure (indicators)

| # | Indicator | How it is calculated, in simple words | Data source | Who collects | How often |
|---|---|---|---|---|---|
| 1 | Alert delivery | Share of days the alert arrived by 10:30 IST | System run log | System (automatic) | Daily |
| 2 | Alert read | Share of alerts the officer confirmed reading within 2 hours | Feedback form (D) | Pilot officer | Per alert |
| 3 | Hit rate | Of the district-days with a real landslide or blockage, the share that were on alert that day or the day before | Feedback form (D) + road logs | Officer + evaluation team | Weekly |
| 4 | Confirmed alerts | Of the alert days, the share with a landslide or blockage that day or the next | Same | Same | Weekly |
| 5 | Lead time | How long before the event the first alert came (same day / 1 day / more) | Alert log (E) | Evaluation team | Per event |
| 6 | Alert load | Alert days per district per month | System log | Automatic | Monthly |
| 7 | Action rate | Share of alerts followed by at least one action | Action log (E) | Pilot officer | Per alert |
| 8 | Action types | Which actions (machines moved, road closed, advisory, standby) | Action log (E) | Pilot officer | Per alert |
| 9 | Alert fatigue | Does the action rate fall during the season, especially after alerts with no event? | Logs (D, E) | Evaluation team | Monthly |
| 10 | Harm on roads | Vehicles or people stranded; hours of road closure per event | Road agency and police records | Road agency / police | Per event |
| 11 | Response time | Hours from a road blockage to reopening | Road agency records | Road agency | Per event |
| 12 | Clarity and trust | Average rating (1–5) on "the alert is clear", "I trust it" | Surveys (A, B) | Evaluation team | Start and end of season |
| 13 | Fairness of coverage | Hit rate and alert load for areas near roads vs far from roads; share of events in remote areas reported at all | Logs + panchayat reports | Evaluation team | End of season |
| 14 | Agreement with official warnings | Share of days where our district level and the IMD/GSI warning agree or disagree | Official bulletins + system log | Evaluation team | Daily |

Indicators 3, 4 and 5 are the same measures used in our replays, so pilot results can be compared directly with the technical tests.

### 5.4 Qualitative evidence
Numbers alone cannot say *why* an alert was or was not used. So we add:
- **Interviews** with 2–3 officers per pilot district at baseline and at the end of the season (Appendix A, B).
- **One group discussion** per pilot district with drivers' or taxi associations, panchayat members and hotel owners (Appendix C used as a guide).
- **"Story" records** of the 3–5 most important events per district: what happened, what the alert said, who did what, what the result was (the "Event story" part of Appendix E).

### 5.5 How results will be judged (decided before the pilot)
To avoid choosing the "success" definition after seeing the results, the pilot team should agree on these before Phase 2, for example:
- **Technical:** the hit rate (indicator 3) is at least as good as in the replays (about 70%), with an alert load (indicator 6) that the officers in the baseline interviews called acceptable.
- **Use:** at least half of alerts lead to an action (indicator 7), and the action rate does not fall steadily during the season (indicator 9).
- **Benefit:** fewer stranded vehicles or shorter closures per event than in comparable earlier events, supported by the event stories.

If these are not met, the result is still useful: it shows which link of the chain in §3 breaks, and that is what the next version should fix.

## 6. Risks, fairness and ethics

| Risk | Why it matters | How the pilot handles it |
|---|---|---|
| **Alert fatigue** | Alerts on about 1 monsoon day in 3–4 may train people to ignore them | Shadow month to set a per-district alert load; track indicator 9; keep Warning (rare: 1.6% of quiet days) as the "act now" signal |
| **False sense of safety** | About 2–3 in 10 recorded events had no alert (2023: 5 of 22; 2025: 11 of 35); "no alert" does not mean "safe" | Every message says so; the system adds to official warnings, never replaces them |
| **Conflicting messages** | Two different warnings confuse people | Alerts go only to officials, labelled "research"; indicator 14 tracks agreement with IMD/GSI |
| **Uneven coverage** | The model learned from landslides that were reported, mostly near roads; remote valleys are less certain | Remote squares are marked "lower confidence" on the map; indicator 13; panchayat reports to capture remote events |
| **Digital divide** | Email reaches officers, not villagers or drivers | Pilot tests passing alerts on through existing channels (police, panchayats, bus depots); ask in surveys which channel works |
| **Personal data** | Surveys and feedback collect names and phone numbers | Ask only what is needed; consent before every survey; names optional for residents; data stored securely and used only for evaluation; results published only as totals |
| **Data dependence** | The system uses free foreign satellite and forecast data that could change or stop | Daily run log shows data delays; a fallback to IMD data is a planned improvement |
| **Responsibility** | Who is responsible if an alert is missed? | Clear written agreement: research decision-support only; official responsibility stays with the authorities |

## 7. After the pilot: what could change
Changes are made **only from pilot evidence**, not before:

1. **District-specific alert levels**, if the shadow month and feedback show that some districts get too many alerts.
2. **More channels and languages:** SMS or WhatsApp in Hindi, if surveys show email is too slow or not read.
3. **Official forecasts as inputs:** IMD rain forecasts alongside the free global forecast.
4. **Better landslide records:** the feedback forms themselves become a richer landslide record, which improves the next model.

## Words used in this section
- **District-day:** one district on one day (12 districts × 108 monsoon days = 1,296 district-days).
- **Hit rate:** out of the real landslide days, how many had an alert.
- **False alarm:** an alert with no landslide. Because many landslides are never recorded, we say "alert without a recorded landslide".
- **Lead time:** how early the warning came before the event.
- **Alert fatigue:** people stop reacting to alerts because many of them seemed unnecessary.
- **Shadow mode:** the system runs and is checked, but its alerts are not sent to anyone yet.
- **Baseline:** the situation before the pilot, used for comparison.
- **Indicator:** one clear number that is measured the same way every time.

## Sources
- UN, *Early Warnings for All* initiative and Executive Action Plan 2023–2027 (UNDRR, WMO, ITU, IFRC): the four pillars. https://www.un.org/en/node/207773 ; https://wmo.int/resources/wmo-bulletin/wmo-bulletin-vol-72-1-2023/overview-of-early-warnings-all-executive-action-plan-2023-2027
- Calvello, M. and Piciullo, L. (2016). Assessing the performance of regional landslide early warning models: the EDuMaP method. *Natural Hazards and Earth System Sciences* 16, 103–122.
- Piciullo, L., Gariano, S. L., Melillo, M., Brunetti, M. T., Peruccacci, S., Guzzetti, F. and Calvello, M. (2017). Definition and performance of a threshold-based regional early warning model for rainfall-induced landslides. *Landslides* 14(3), 995–1008. https://doi.org/10.1007/s10346-016-0750-2
- Geological Survey of India, National Landslide Forecasting Centre; landslide forecast bulletins on the Bhusanket portal (bhusanket.gsi.gov.in).
- Project evidence: `docs/alert_rule_explained.md`, `docs/monsoon_replay_explained.md`, `docs/daily_system_setup.md`.

---

# Appendices: questionnaires and formats

All questionnaires start with the consent text below. Questions marked *(baseline)* are asked before the monsoon, *(end)* after it, and *(both)* at both times, so that "before" and "after" can be compared.

> **Consent (read out or shown first).** "We are evaluating a research landslide early-warning system for Himachal Pradesh. Taking part is voluntary. You can skip any question or stop at any time. Your answers will be used only for this evaluation and reported only as totals, without your name. Do you agree to take part?" ☐ Yes ☐ No

## Appendix A. Questionnaire for disaster management officials (DDMA, district control room, HPSDMA, SEOC)
*About 15 minutes. Interview or form.*

**About you**

1. Office and district. *(both)*
2. Your role (e.g. District Disaster Management Officer, control-room operator). *(both)*
3. Years in this role: ☐ <1 ☐ 1–3 ☐ 3–5 ☐ >5 *(baseline)*

**Current warnings** *(baseline)*

4. Which landslide or heavy-rain warnings do you receive today? ☐ IMD ☐ GSI landslide bulletin ☐ State control room ☐ News or social media ☐ None ☐ Other: ___
5. How do they reach you? ☐ Email ☐ SMS ☐ WhatsApp ☐ Phone call ☐ Website ☐ Other: ___
6. How early do they usually arrive before a landslide? ☐ Same day ☐ 1 day ☐ 2+ days ☐ Usually after the event
7. On a scale of 1 (not at all) to 5 (fully), how useful are the current warnings for deciding what to do?

**What you do when a warning comes** *(baseline)*

8. Is there a written procedure for what to do at each warning level? ☐ Yes ☐ No ☐ Not sure
9. Which actions does your office take after a warning? (tick all) ☐ Rescue teams on standby ☐ Inform road agencies ☐ Move machines ☐ Close or restrict roads ☐ Advisory to public/tourists ☐ Evacuate ☐ None ☐ Other: ___
10. What usually stops your office from acting on a warning? (tick all) ☐ Warning too vague (area too large) ☐ Arrives too late ☐ Too many false alarms ☐ No staff or machines ☐ Not our responsibility ☐ Other: ___

**Alert load** *(baseline)*

11. In one monsoon, how many alert days for your district would you consider acceptable if most of them were right? ☐ <10 ☐ 10–20 ☐ 20–30 ☐ >30
12. Which is worse for your work: ☐ a missed landslide ☐ a false alarm ☐ both equally? Why? ___

**About our system** *(end)*

13. How often did you read the daily alert? ☐ Daily ☐ Most days ☐ Sometimes ☐ Rarely
14. "The alert was easy to understand" (1 = strongly disagree … 5 = strongly agree).
15. "I trusted the alert" (1–5).
16. "The alert helped me decide what to do" (1–5).
17. Did the alert ever arrive before a landslide in time to act? ☐ Yes ☐ No. If yes, describe one case: ___
18. Did you feel there were too many alerts? ☐ Yes ☐ About right ☐ Too few
19. Did our alert ever disagree with IMD or GSI warnings? ☐ Often ☐ Sometimes ☐ Never ☐ Don't know. What did you do then? ___
20. What would make the alert more useful? (tick all) ☐ Smaller areas (tehsil or road stretch) ☐ SMS/WhatsApp ☐ Hindi ☐ Earlier time of day ☐ Clear action per level ☐ Other: ___
21. Should this system continue next monsoon? ☐ Yes ☐ Yes, with changes ☐ No. Why? ___

## Appendix B. Questionnaire for road agencies (PWD, BRO, NHAI) and police/transport
*About 10 minutes.*

1. Organisation, division and district. *(both)*
2. Road stretches you are responsible for (names or numbers). *(baseline)*
3. In the last monsoon, roughly how many times were your roads blocked by landslides? ☐ <5 ☐ 5–20 ☐ 20–50 ☐ >50 *(baseline)*
4. Average time to reopen a blocked road: ☐ <3 h ☐ 3–12 h ☐ 12–24 h ☐ >24 h *(both)*
5. Do you keep a record of blockages (date, place, hours closed)? ☐ Yes, digital ☐ Yes, paper ☐ No. Could it be shared for this evaluation? ☐ Yes ☐ No *(baseline)*
6. What do you do today when heavy rain is forecast? (tick all) ☐ Machines on standby ☐ Machines moved near known spots ☐ Night traffic restricted ☐ Nothing specific ☐ Other: ___ *(baseline)*
7. How much warning time do you need to move a machine and crew to a risky spot? ☐ <3 h ☐ 3–12 h ☐ 12–24 h ☐ >24 h *(baseline)*
8. Is a district-level alert detailed enough for you, or do you need road-stretch level? ☐ District is enough ☐ Need road stretch ☐ Need exact spots *(both)*
9. During the pilot, how many times did you act because of our alert? ___ Which actions? ___ *(end)*
10. Did any of those actions reduce the closure time or keep people safe? Describe one case: ___ *(end)*
11. "The alert was worth the effort of reading it" (1–5). *(end)*

## Appendix C. Questionnaire for residents and travellers
*About 10 minutes. Name and phone number are optional. Used also as a guide for group discussions.*

**About you** (all optional except district)

1. District and village/town: ___
2. Age group: ☐ Below 22 ☐ 22–55 ☐ Above 55
3. You are mainly: ☐ Resident ☐ Driver (taxi, bus, truck) ☐ Shop or hotel owner ☐ Farmer ☐ Tourist ☐ Government staff ☐ Other: ___

**Experience with landslides** *(baseline)*

4. Has your area been affected by landslides in the last 5 years? ☐ Yes ☐ No ☐ Not sure
5. How many times? ☐ Once ☐ 2–5 times ☐ More than 5 times
6. Have you ever been stuck or delayed on a road because of a landslide? ☐ Never ☐ Once ☐ Several times. If yes, for how long (longest time)? ☐ <3 h ☐ 3–12 h ☐ >12 h ☐ More than a day
7. Has a landslide affected your work or income (e.g. lost days of work, closed shop, damaged crops)? ☐ Yes ☐ No

**Warnings today** *(both)*

8. Did you get any warning before the last landslide that affected you? ☐ Yes ☐ No ☐ Don't remember. If yes, from whom and how long before? ___
9. Where do you get weather or landslide warnings today? (tick all) ☐ SMS ☐ WhatsApp ☐ TV/radio ☐ Newspaper ☐ Panchayat ☐ Police ☐ Neighbours ☐ None
10. Which way would you most like to receive a warning? ☐ SMS ☐ WhatsApp ☐ Phone call ☐ Loudspeaker/siren ☐ Panchayat ☐ Radio
11. In which language? ☐ Hindi ☐ English ☐ Local language: ___
12. Who would you trust most to give you a warning? ☐ District administration ☐ Police ☐ Panchayat ☐ IMD/weather service ☐ News ☐ Other: ___

**Would a warning change what you do?** *(both)*

13. If you got a warning in the evening that landslides are likely tomorrow in your district, what would you do? (tick all) ☐ Delay or cancel travel ☐ Choose another route ☐ Move vehicle or goods ☐ Stay indoors/away from slopes ☐ Tell family and neighbours ☐ Nothing ☐ Other: ___
14. If warnings came often and nothing happened, would you still pay attention? ☐ Yes ☐ Less over time ☐ No
15. Is there a local group (e.g. panchayat committee, volunteers) that helps people prepare for landslides? ☐ Yes ☐ No ☐ Don't know
16. Any other comments: ___

## Appendix D. Per-alert feedback form (one per district per alert day)
*For the pilot officer. Under 2 minutes. Can be a Google Form linked from the daily email.*

| Field | Answer |
|---|---|
| Date of the alert and district | ___ |
| Alert level received | ☐ Watch ☐ Warning |
| Time you read it | ___ : ___ |
| Did a landslide or road blockage happen in the district **today or tomorrow**? | ☐ Yes ☐ No ☐ Not known yet |
| If yes: place (village, road and km), date, time, effect (road blocked hours, vehicles stranded, damage, injuries) | ___ |
| Did your office take any action because of the alert? | ☐ Yes ☐ No |
| If yes, what? | ☐ Standby ☐ Machines moved ☐ Road restricted/closed ☐ Advisory issued ☐ Informed other departments ☐ Other: ___ |
| If no, why not? | ☐ Not needed ☐ No resources ☐ Did not trust it ☐ Read too late ☐ Other: ___ |
| Did IMD/GSI also warn for this district today? | ☐ Yes ☐ No ☐ Don't know |

**Also report landslides on days *without* an alert** (one line each: date, place, effect). These are the misses, and without them the hit rate cannot be measured.

## Appendix E. Alert and action log (kept by the evaluation team)
One row per district per day during the pilot; filled from the system log, the feedback forms and road records.

| Date | District | Our level (none / Watch / Warning) | IMD/GSI warning (yes/no) | Alert read (time) | Event today or tomorrow (yes/no) | Event details (place, effect) | Action taken (type, time) | Closure hours | People/vehicles stranded | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

**Event story** (for the 3–5 most important events per district, half a page each): what happened; what our alert and the official warnings said, and when; who did what, and when; what the outcome was; what could have gone better.

## Appendix F. Monthly summary (one page per pilot district)

| Item | This month | Season so far |
|---|---|---|
| Days in month / days the alert arrived on time | | |
| Watch days / Warning days | | |
| Landslide or blockage days reported | | |
| …of which on alert that day or the day before (hit rate) | | |
| Alert days with an event that day or the next (confirmed alerts) | | |
| Alerts followed by an action (action rate) | | |
| Most common actions | | |
| Total closure hours / people or vehicles stranded | | |
| Days our level disagreed with IMD/GSI | | |
| Main problems reported by users | | |
| Changes agreed for next month (if any, with reason) | | |
