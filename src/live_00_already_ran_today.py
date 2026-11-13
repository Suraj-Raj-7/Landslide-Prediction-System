"""Live system, step 0: has today's outlook already been made?

WHY THIS EXISTS
  GitHub starts scheduled runs "when it can". In the first days (10-13 Nov
  2026) the 10:00 IST run actually started between 17:32 and 18:36 IST.
  To get the outlook in the morning, the workflow now asks GitHub three times
  (06:00, 08:00 and 10:00 IST). Whichever attempt starts first does the work;
  the later ones run this check, see that today is already done, and stop,
  so nobody gets the same email twice.

WHAT IT DOES
  Asks GitHub's public API for successful runs of this workflow that started
  today (Indian date). Prints "done=true" or "done=false" (the workflow reads
  this line); explanations go to the log (stderr), not to that output.
  If GitHub cannot be reached, it prints "done=false", so a day is never
  skipped by mistake (at worst an extra email is sent).

RUN (on GitHub this is automatic)
  python src/live_00_already_ran_today.py
  Uses GITHUB_REPOSITORY and, if present, GITHUB_TOKEN from the environment.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "Suraj-Raj-7/Landslide-Prediction-System")
WORKFLOW = "daily.yml"
IST = dt.timedelta(hours=5, minutes=30)


def main():
    now = dt.datetime.now(dt.timezone.utc)
    today_ist = (now + IST).date()
    start_utc = dt.datetime.combine(today_ist, dt.time(), dt.timezone.utc) - IST   # 00:00 IST today, in UTC
    url = (f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/runs"
           f"?status=success&per_page=20&created=>={start_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            runs = json.load(r)["workflow_runs"]
    except Exception as e:   # cannot check: better one extra run than a missed day
        print(f"could not check earlier runs ({e}); running anyway", file=sys.stderr)
        print("done=false")
        return
    print(f"Indian date {today_ist}: {len(runs)} successful run(s) already today", file=sys.stderr)
    print(f"done={'true' if runs else 'false'}")


if __name__ == "__main__":
    main()
