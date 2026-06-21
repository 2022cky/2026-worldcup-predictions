import urllib.request, json

for date_str in ["20260620", "20260621"]:
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=" + date_str
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=15).read()
    j = json.loads(data)
    events = j.get("events", [])
    print("=== " + date_str + " found " + str(len(events)) + " events ===")
    for ev in events:
        name = ev.get("name", "")
        st = ev.get("status", {}).get("type", {})
        comps = ev.get("competitions", [{}])[0]
        desc = st.get("description", "N/A")
        clock = st.get("displayClock", "N/A")
        state = st.get("state", "N/A")
        print("Match: " + name)
        print("Status: " + desc + " | Clock: " + clock + " | State: " + state)
        for c in comps.get("competitors", []):
            team_name = c["team"]["displayName"]
            score = str(c.get("score", "N/A"))
            print("  " + team_name + ": " + score)
            for s in c.get("statistics", []):
                print("    " + s["name"] + ": " + s["displayValue"])
        print("")
