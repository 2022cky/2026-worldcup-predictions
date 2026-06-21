import urllib.request, json

url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=15).read()
j = json.loads(data)

targets = ['Switzerland', 'Bosnia', 'Canada', 'Qatar', 'Mexico', 'Korea']

for ev in j.get('events', []):
    name = ev.get('name', '')
    if any(t in name for t in targets):
        c = ev['competitions'][0]
        st = c['status']['type']
        h, a = c['competitors']
        print(f"{h['team']['displayName']} {h['score']} - {a['score']} {a['team']['displayName']}")
        print(f"  Status: {st['description']} | Clock: {c['status'].get('displayClock','?')} | Period: {c['status'].get('period','?')}")
        for t in c['competitors']:
            stats = {s['name']: s['displayValue'] for s in t.get('statistics', [])}
            print(f"  {t['team']['displayName']}: Poss={stats.get('possessionPct','?')}% Shots={stats.get('totalShots','?')} SOT={stats.get('shotsOnTarget','?')} Fouls={stats.get('foulsCommitted','?')} Corners={stats.get('wonCorners','?')}")
        print()
