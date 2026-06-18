#!/usr/bin/env python3
"""实时比分查询 — 直连ESPN API,绕过WebFetch封锁"""
import urllib.request, json, sys

URL = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def live_scores(filter_teams=None):
    """拉取全部比赛状态, 可选按队名过滤"""
    req = urllib.request.Request(URL, headers=HEADERS)
    data = urllib.request.urlopen(req, timeout=15).read()
    j = json.loads(data)

    for ev in j.get('events', []):
        name = ev.get('name', '')
        if filter_teams and not any(t.lower() in name.lower() for t in filter_teams):
            continue

        c = ev['competitions'][0]
        st = c['status']['type']
        h, a = c['competitors']
        hs, aw = h['score'], a['score']
        hn, an = h['team']['displayName'], a['team']['displayName']
        clock = c['status'].get('displayClock', '?')
        period = c['status'].get('period', '?')

        print(f"{hn} {hs} - {aw} {an}")
        print(f"  状态: {st['description']} | 时间: {clock}' | 半场: {'上半场' if period==1 else '下半场' if period==2 else '?'}")

        for t in c['competitors']:
            stats = {s['name']: s['displayValue'] for s in t.get('statistics', [])}
            print(f"  {t['team']['displayName']}: "
                  f"控球{stats.get('possessionPct','?')}% "
                  f"射门{stats.get('totalShots','?')} "
                  f"射正{stats.get('shotsOnTarget','?')} "
                  f"犯规{stats.get('foulsCommitted','?')} "
                  f"角球{stats.get('wonCorners','?')}")
        print()

if __name__ == '__main__':
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    live_scores(args)
