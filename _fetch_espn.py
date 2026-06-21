import urllib.request, json
url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260621"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    data = urllib.request.urlopen(req, timeout=15).read()
    j = json.loads(data)
    print("=== 6月21日 比赛结果 ===")
    for ev in j.get("events", []):
        name = ev.get("name", "")
        short = ev.get("shortName", "")
        status_type = ev.get("status", {}).get("type", {})
        comps = ev.get("competitions", [{}])[0]
        print(f"\n--- {name} ({short}) ---")
        print(f"状态: {status_type.get(\"description\", \"N/A\")} | 时间: {status_type.get(\"displayClock\", \"N/A\")}")
        for c in comps.get("competitors", []):
            score = c.get("score", "N/A")
            print(f"  {c[\"team\"][\"displayName\"]}: {score}")
            for s in c.get("statistics", []):
                print(f"    {s[\"name\"]}: {s[\"displayValue\"]}")
except Exception as e:
    print(f"Error: {e}")
