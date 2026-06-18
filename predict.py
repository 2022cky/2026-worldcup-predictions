#!/usr/bin/env python3
"""
Codex世界杯预测数据采集器 v3 — Final
用法: python predict.py
功能: ESPN API → 赛程/比分/统计 → 终端摘要 + worldcup_data.json
"""
import urllib.request, json, os, sys
from datetime import datetime, timedelta, timezone

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}
BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
OUT_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) or "."

AFRICA = {"Morocco","Senegal","Tunisia","Algeria","Egypt","Cape Verde",
          "South Africa","Ivory Coast","Cote d'Ivoire","Ghana","Congo DR",
          "Cameroon","Nigeria","Mali","Burkina Faso","Guinea"}
ASIA   = {"Japan","South Korea","Korea Republic","Saudi Arabia","Iran","Qatar",
          "Australia","Iraq","Uzbekistan","Jordan","China","United Arab Emirates","Oman","Bahrain"}
TOP10  = {"France","Brazil","Spain","Argentina","England","Portugal",
          "Netherlands","Belgium","Germany","Croatia"}
FINAL_STATES = {"STATUS_FINAL", "STATUS_FULL_TIME"}

def fetch(path):
    req = urllib.request.Request(f"{BASE}/{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def utc2tpe(s):
    try:
        dt = datetime.strptime(s[:19], "%Y-%m-%dT%H:%M")
        return (dt + timedelta(hours=8)).strftime("%m/%d %H:%M")
    except:
        return s

# ── Fetch: 6/11 to 6/20 ———————————————————————
print("=" * 72)
print("  Codex 2026 WC Data Collector v3")
print("=" * 72)

utc_now = datetime.now(timezone.utc)
start = datetime(2026, 6, 11, tzinfo=timezone.utc)
end   = datetime(2026, 6, 20, tzinfo=timezone.utc)
all_events = []

d = start
while d <= end:
    ds = d.strftime("%Y%m%d")
    try:
        data = fetch(f"scoreboard?dates={ds}")
        n = len(data.get("events", []))
        for ev in data.get("events", []):
            ev["_ds"] = ds
            all_events.append(ev)
        print(f"  {ds}: {n} events")
    except Exception as e:
        print(f"  {ds}: FAIL ({e})")
    d += timedelta(days=1)

# ── Classify —————————————————————————————————
final, live, sched = [], [], []
for ev in all_events:
    st = ev.get("status",{}).get("type",{}).get("name","")
    if st in FINAL_STATES:
        final.append(ev)
    elif st == "STATUS_IN_PROGRESS":
        live.append(ev)
    else:
        sched.append(ev)

# ── Print completed ——————————————————————————
print(f"\n{'='*72}")
print(f"  Completed ({len(final)})")
print(f"{'TPE':<14} {'Home':<22} {'Sc':<7} {'Away':<22}")
print(f"{'-'*72}")
stats = {"t":0,"d":0,"af":0,"afo":0,"as":0,"aso":0,"t10":0,"t10cs":0}
for ev in sorted(final, key=lambda e: e.get("date","")):
    c = ev["competitions"][0]
    h, a = c["competitors"]
    hn = h["team"]["displayName"]
    an = a["team"]["displayName"]
    hs = h.get("score","?")
    aw = a.get("score","?")
    dt = utc2tpe(ev.get("date",""))
    print(f"{dt:<14} {hn:<22} {hs}-{aw:<4} {an:<22}")

    stats["t"] += 1
    if hs == aw: stats["d"] += 1
    for tn, ts, op in [(hn,hs,aw),(an,aw,hs)]:
        if tn in AFRICA: stats["af"]+=1; stats["afo"]+=1 if ts>=op else 0
        if tn in ASIA:   stats["as"]+=1; stats["aso"]+=1 if ts>=op else 0
        if tn in TOP10:  stats["t10"]+=1; stats["t10cs"]+=1 if op==0 else 0

# ── Trends ———————————————————————————————————
print(f"\n{'='*72}")
print(f"  Trends")
print(f"{'-'*72}")
t = stats["t"]
if t:
    dp = stats["d"]/t*100
    ap = stats["afo"]/stats["af"]*100 if stats["af"] else 0
    sp = stats["aso"]/stats["as"]*100 if stats["as"] else 0
    tp = stats["t10cs"]/stats["t10"]*100 if stats["t10"] else 0
    print(f"  Total matches:       {t}")
    print(f"  Draws:               {stats['d']} ({dp:.1f}%) {'<< HIGH' if dp>30 else ''}")
    print(f"  Africa undefeated:   {stats['afo']}/{stats['af']} ({ap:.0f}%) {'<< HISTORIC' if ap==100 and stats['af']>=4 else ''}")
    print(f"  Asia undefeated:     {stats['aso']}/{stats['as']} ({sp:.0f}%) {'<< HISTORIC' if sp==100 and stats['as']>=4 else ''}")
    print(f"  Top10 Clean Sheets:  {stats['t10cs']}/{stats['t10']} ({tp:.0f}%)")

# ── Upcoming —————————————————————————————————
print(f"\n{'='*72}")
print(f"  Upcoming ({len(sched)})")
print(f"{'-'*72}")
for ev in sorted(sched, key=lambda e: e.get("date","")):
    c = ev["competitions"][0]
    h, a = c["competitors"]
    hn = h["team"]["displayName"]
    an = a["team"]["displayName"]
    dt = utc2tpe(ev.get("date",""))
    flags = []
    if hn in AFRICA or an in AFRICA: flags.append("[AFR]")
    if hn in ASIA or an in ASIA: flags.append("[ASI]")
    if hn in TOP10 or an in TOP10: flags.append("[TOP10]")
    fs = " " + " ".join(flags) if flags else ""
    print(f"  {dt:<12} {hn} vs {an}{fs}")

# ── Save JSON ————————————————————————————————
save = {
    "fetched_utc": utc_now.isoformat(),
    "total": len(all_events), "final": len(final),
    "live": len(live), "scheduled": len(sched),
    "stats": stats, "events": all_events,
}
out_path = os.path.join(OUT_DIR, "worldcup_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(save, f, ensure_ascii=False, indent=2)
print(f"\n  Saved: {out_path}")
print("=" * 72)
print("  Done. Paste this output to Codex for prediction analysis.")