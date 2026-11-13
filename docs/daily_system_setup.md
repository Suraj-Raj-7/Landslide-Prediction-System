# Daily system: how it works and how to switch it on

Written 9 Nov 2026. Everything below is done by Suraj; nothing is pushed or committed automatically.

## 1. What runs every morning
Every morning GitHub starts `src/live_03_daily_run.py` (workflow: `.github/workflows/daily.yml`).

**Timing.** GitHub starts scheduled runs "when it can", not exactly on time: in the first days (10–13 Nov 2026) the 10:00 IST run started between 17:32 and 18:36 IST. So the workflow asks three times, at 06:00, 08:00 and 10:00 IST. The first attempt that starts does the work. Later attempts first run `src/live_00_already_ran_today.py`, see that today's outlook already exists, and stop, so the email is not sent twice. A manual "Run workflow" always runs.

In about one minute the run:
1. reads the HP grid file `data/live/grid_live.csv.gz` (55,253 squares of 1 km: terrain, rock, roads, land cover, district, vegetation);
2. adds rain for **today and tomorrow** (`src/live_02_rain.py`): measured satellite rain (IMERG) as far as it goes, about 1.5 days behind, and the GFS weather forecast for the rest;
3. scores every square with the live model and applies the final alert rule (`docs/alert_rule_explained.md`);
4. draws today's and tomorrow's map, builds a web page and emails the recipients.

Nothing is committed by GitHub; the page is published with GitHub Pages and each run is kept as a downloadable record for 90 days. **Only Suraj commits to the repository.**

**Once a month** (any day, ~5 minutes of your time + ~40 min waiting): refresh the vegetation layer, then commit the new grid file.
```powershell
cd "G:\ALL PROJECTS\Landslide Prediction Project"
.venv\Scripts\python -W ignore src\live_01_monthly_grid.py submit
# wait ~40 min (GEE tasks), then:
.venv\Scripts\python -W ignore src\live_01_monthly_grid.py download
git add data/live/grid_live.csv.gz data/live/grid_live_info.json
git commit -m "Refresh vegetation grid"
git push
```

## 2. Why these choices (short)
| Choice | Reason / evidence |
|---|---|
| Vegetation monthly, not daily | It takes GEE ~40 min and hardly changes: moving its 1-year window by 90 days changed it by a median of 0.010 (spread between places 0.19). Test of 6 Nov 2026. |
| Forecast rain for the newest hours | Measured rain reaches GEE ~1.5 days late (checked 9 Nov 2026). For each missing hour the newest forecast issued before it is used (short-range forecasts are the most accurate). The model learned from measured rain only, so forecast rain adds warning time but also errors; the page shows how much of today's rain is forecast. |
| Grid as a file in the repository | The daily run then reads only public datasets, so the robot login (service account) needs no access to private GEE assets. |
| Checks done | Measured-rain path identical to the training data for 55,252 of 55,253 squares (14 Aug 2023); GFS 6-hour reset confirmed on real data; glacier flag identical over time (627 squares); full run on 14 Aug 2023 puts 10 districts at Warning, 1 at Watch. |
| Email every day during the trial week | A daily message (also "No district on alert") shows the system ran. In real use it would be sent only on Watch or Warning. |

## 3. One-time setup (Suraj), in order

### Step A. GitHub repository (you commit and push)
1. On github.com: **New repository** → name `Landslide-Prediction-System` (created 9 Nov 2026: https://github.com/Suraj-Raj-7/Landslide-Prediction-System) → **Public** (GitHub Pages is free for public repositories; for a private one you need GitHub Pro, free with the GitHub Student Developer Pack) → do **not** add a README → Create.
2. In PowerShell:
```powershell
cd "G:\ALL PROJECTS\Landslide Prediction Project"
git init
git config user.name "Suraj Raj"
git config user.email "YOUR_GITHUB_EMAIL"
git add .
git status
```
3. Check the `git status` list: there must be **no** `_private/`, `.venv/`, `gee_scripts_repo/`, `site/` and **no key or password file**. Then:
```powershell
git commit -m "Add landslide early warning project"
git branch -M main
git remote add origin https://github.com/Suraj-Raj-7/Landslide-Prediction-System.git
git push -u origin main
```

### Step B. Earth Engine robot login (service account)
GitHub cannot use your personal Google login, so it gets its own "robot" account in your Cloud project.
1. Open https://console.cloud.google.com/iam-admin/serviceaccounts?project=idyllic-return-468714-j4
2. **Create service account** → name `daily-run` → Create and continue.
3. Roles: add **Earth Engine Resource Writer** and **Service Usage Consumer** → Done. (Writer includes reading and running computations; the run reads only public data.)
4. Click the new account → **Keys** → **Add key** → **Create new key** → **JSON** → it downloads a `.json` file.
5. Move that file **outside the project folder**, e.g. `C:\Users\91906\keys\ee-daily-run.json`. Never put it in the project or commit it.
6. Test it on the laptop (shows that the robot login works before GitHub uses it):
```powershell
cd "G:\ALL PROJECTS\Landslide Prediction Project"
$env:EE_SERVICE_ACCOUNT_KEY = Get-Content "C:\Users\91906\keys\ee-daily-run.json" -Raw
.venv\Scripts\python -W ignore src\live_03_daily_run.py --no-email
Remove-Item Env:EE_SERVICE_ACCOUNT_KEY
```

### Step C. Gmail app password (for sending the email)
1. The sending Gmail account needs **2-Step Verification** on (https://myaccount.google.com/security).
2. Open https://myaccount.google.com/apppasswords → name it `landslide alerts` → **Create** → copy the 16-letter password (shown once).

### Step D. Secrets and settings on GitHub
In the repository: **Settings → Secrets and variables → Actions**.
- **Secrets** → New repository secret, four times:

| Name | Value |
|---|---|
| `EE_SERVICE_ACCOUNT_KEY` | the whole content of the `.json` key file (open it in Notepad, copy all) |
| `ALERT_SENDER` | the sending Gmail address |
| `ALERT_APP_PASSWORD` | the 16-letter app password |
| `ALERT_RECIPIENTS` | addresses separated by commas, e.g. `you@gmail.com,teammate@gmail.com` |

- **Variables** tab → New repository variable: `SITE_URL` = `https://suraj-raj-7.github.io/Landslide-Prediction-System/`
- **Settings → Pages** → Source: **GitHub Actions**.

### Step E. First run
**Actions** tab → **Daily landslide outlook** → **Run workflow**. After 2–4 minutes: green tick, an email, and the page at `SITE_URL`. From then on it runs every morning by itself.

## 4. If something fails
Open the failed run in the **Actions** tab and read the red step. Common causes: a secret pasted incompletely (copy the whole JSON), service-account role missing (step B3), Pages source not set to GitHub Actions (step D). GEE or GFS delays only shift which forecast is used; the run reports it on the page.
