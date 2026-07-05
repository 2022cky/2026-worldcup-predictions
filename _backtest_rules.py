#!/usr/bin/env python3
"""回测2026预测规则 → 2018 & 2022 世界杯"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from openfootball_data import WorldCupData

FIFA = {
    2018: {'Germany':1,'Brazil':2,'Belgium':3,'Portugal':4,'Argentina':5,'Switzerland':6,'France':7,
        'Spain':10,'Denmark':12,'England':13,'Uruguay':14,'Mexico':15,'Colombia':16,'Croatia':20,
        'Sweden':24,'Senegal':27,'Iran':34,'Serbia':35,'Australia':36,'Japan':61,'Morocco':41,
        'Egypt':45,'Nigeria':48,'Panama':55,'South Korea':57,'Saudi Arabia':67,'Russia':70,
        'Poland':8,'Peru':11,'Costa Rica':23,'Iceland':22,'Tunisia':21},
    2022: {'Brazil':1,'Belgium':2,'Argentina':3,'France':4,'England':5,'Spain':7,'Netherlands':8,
        'Portugal':9,'Denmark':10,'Germany':11,'Croatia':12,'Mexico':13,'Uruguay':14,'Switzerland':15,
        'USA':16,'Senegal':18,'Wales':19,'Iran':20,'Serbia':21,'Morocco':22,'Japan':24,'Poland':26,
        'South Korea':28,'Tunisia':30,'Costa Rica':31,'Australia':38,'Qatar':50,'Saudi Arabia':51,
        'Ecuador':44,'Cameroon':43,'Ghana':61,'Canada':41},
}

all_ko = []
all_grp = []

for year in [2018, 2022]:
    rankings = FIFA[year]
    wc = WorldCupData(year)
    for m in wc.matches:
        if 'score' not in m or 'ft' not in m['score']:
            continue
        t1,t2 = m['team1'],m['team2']
        r1=rankings.get(t1,999); r2=rankings.get(t2,999)
        if r1==999 or r2==999: continue

        ft = m['score']['ft']
        ht = m['score'].get('ht', [None,None])
        is_ko = any(r in m.get('round','') for r in ['Round of 16','Quarter-final','Semi-final','Final','Match for third place'])

        if r1 < r2:
            stronger, weaker = t1, t2
            sg, wg = ft[0], ft[1]
        else:
            stronger, weaker = t2, t1
            sg, wg = ft[1], ft[0]

        rank_gap = abs(r1 - r2)

        entry = {
            'year': year, 'stronger': stronger, 'weaker': weaker,
            'sg': sg, 'wg': wg, 'rank_gap': rank_gap,
            'ht_zz': ht[0]==0 and ht[1]==0 if ht[0] is not None else None,
            'is_draw': ft[0]==ft[1],
            'is_upset': wg > sg,
            'strong_2plus': sg >= 2,
            'strong_3plus': sg >= 3,
            'weak_scored': wg > 0,
            'narrow': abs(ft[0]-ft[1]) == 1,
            'blowout': abs(ft[0]-ft[1]) >= 3,
            'round': m.get('round',''),
        }
        if is_ko:
            all_ko.append(entry)
        else:
            all_grp.append(entry)

print("="*70)
print("2018+2022 全量历史数据 × 2026预测逻辑链验证")
print(f"小组赛{len(all_grp)}场 + 淘汰赛{len(all_ko)}场")
print("="*70)

# ── CLAIM 1: 弱队进球率 ──
print("\n" + "="*50)
print("[1] 弱队进球率 (2026声称: 淘汰赛61%)")
print("="*50)
for label, matches in [("小组赛", all_grp), ("淘汰赛", all_ko)]:
    scored = sum(1 for m in matches if m['weak_scored'])
    print(f"  {label}: {scored}/{len(matches)} = {scored/len(matches)*100:.0f}%")
    for gap_min, gap_max, glabel in [(0,5,'0-5名'),(6,15,'6-15'),(16,30,'16-30'),(31,100,'31+')]:
        subset = [m for m in matches if gap_min <= m['rank_gap'] <= gap_max]
        if subset:
            s = sum(1 for m in subset if m['weak_scored'])
            print(f"    {glabel}: {s}/{len(subset)}={s/len(subset)*100:.0f}%")

# ── CLAIM 2: 半场0-0率 ──
print("\n" + "="*50)
print("[2] 半场0-0率 (2026声称: 淘汰赛71%)")
print("="*50)
for label, matches in [("小组赛", all_grp), ("淘汰赛", all_ko)]:
    valid = [m for m in matches if m['ht_zz'] is not None]
    zz = sum(1 for m in valid if m['ht_zz'])
    print(f"  {label}: {zz}/{len(valid)} = {zz/len(valid)*100:.0f}%")
    for gap_min, gap_max, glabel in [(0,5,'0-5名'),(6,15,'6-15'),(16,30,'16-30'),(31,100,'31+')]:
        subset = [m for m in valid if gap_min <= m['rank_gap'] <= gap_max]
        if subset:
            s = sum(1 for m in subset if m['ht_zz'])
            print(f"    {glabel}: {s}/{len(subset)}={s/len(subset)*100:.0f}%")

# ── CLAIM 3: 强队进球量 ──
print("\n" + "="*50)
print("[3] 强队进球量 (2026: 预测偏高估约1球)")
print("="*50)
for label, matches in [("小组赛", all_grp), ("淘汰赛", all_ko)]:
    avg_sg = sum(m['sg'] for m in matches)/len(matches)
    s2 = sum(1 for m in matches if m['strong_2plus'])
    s3 = sum(1 for m in matches if m['strong_3plus'])
    s1_or_less = sum(1 for m in matches if m['sg'] <= 1)
    print(f"  {label}: 强队场均{avg_sg:.1f}球 | 0-1球:{s1_or_less/len(matches)*100:.0f}% | 2+球:{s2/len(matches)*100:.0f}% | 3+球:{s3/len(matches)*100:.0f}%")
    for gap_min, gap_max, glabel in [(0,5,'0-5'),(6,15,'6-15'),(16,30,'16-30'),(31,100,'31+')]:
        subset = [m for m in matches if gap_min <= m['rank_gap'] <= gap_max]
        if subset:
            avg = sum(m['sg'] for m in subset)/len(subset)
            s2_ = sum(1 for m in subset if m['strong_2plus'])
            s0_1 = sum(1 for m in subset if m['sg'] <= 1)
            print(f"    {glabel}: 场均{avg:.1f}球 | 0-1球:{s0_1/len(subset)*100:.0f}% | 2+:{s2_/len(subset)*100:.0f}%")

# ── CLAIM 4: 排名差距预测力 ──
print("\n" + "="*50)
print("[4] 排名差距 vs 强队胜率 (身价比代理)")
print("="*50)
for label, matches in [("小组赛", all_grp), ("淘汰赛", all_ko)]:
    print(f"  {label}:")
    for gap_min, gap_max, glabel in [(0,5,'0-5名'),(6,15,'6-15'),(16,30,'16-30'),(31,100,'31+')]:
        subset = [m for m in matches if gap_min <= m['rank_gap'] <= gap_max]
        if subset:
            win = sum(1 for m in subset if m['sg'] > m['wg'])
            draw = sum(1 for m in subset if m['sg'] == m['wg'])
            lose = sum(1 for m in subset if m['sg'] < m['wg'])
            avg_gd = sum(m['sg']-m['wg'] for m in subset)/len(subset)
            print(f"    {glabel} ({len(subset)}场): 强队胜{win/len(subset)*100:.0f}% 平{draw/len(subset)*100:.0f}% 负{lose/len(subset)*100:.0f}% 净胜{avg_gd:+.1f}")

# ── CLAIM 5: 淘汰赛 vs 小组赛 ──
print("\n" + "="*50)
print("[5] 淘汰赛特征差异")
print("="*50)
for label, matches in [("小组赛", all_grp), ("淘汰赛", all_ko)]:
    draws = sum(1 for m in matches if m['is_draw'])/len(matches)*100
    narrow = sum(1 for m in matches if m['narrow'])/len(matches)*100
    blowout = sum(1 for m in matches if m['blowout'])/len(matches)*100
    upset = sum(1 for m in matches if m['is_upset'])/len(matches)*100
    print(f"  {label}: 平局{draws:.0f}% | 1球差{narrow:.0f}% | 3+球差{blowout:.0f}% | 冷门{upset:.0f}%")

# ── CLAIM 6: R16平局率最高? ──
print("\n" + "="*50)
print("[6] 各轮次平局率 (2026记忆: R16=32.5%最高)")
print("="*50)
for round_name in ['Round of 16', 'Quarter-final', 'Semi-final', 'Final']:
    subset = [m for m in all_ko if round_name in m['round']]
    if not subset:
        continue
    draws = sum(1 for m in subset if m['is_draw'])/len(subset)*100
    valid_ht = [m for m in subset if m['ht_zz'] is not None]
    htzz = sum(1 for m in valid_ht if m['ht_zz'])/len(valid_ht)*100 if valid_ht else 0
    upset = sum(1 for m in subset if m['is_upset'])/len(subset)*100
    avg_sg = sum(m['sg'] for m in subset)/len(subset)
    weak_pct = sum(1 for m in subset if m['weak_scored'])/len(subset)*100
    print(f"  {round_name} ({len(subset)}场): 平局{draws:.0f}% | HT0-0:{htzz:.0f}% | 冷门{upset:.0f}% | 强队进球{avg_sg:.1f} | 弱队进球率{weak_pct:.0f}%")

# ── CLAIM 7: "了解对手≠优势" 的验证 ──
# 无法用排名数据直接验证，但可以看"同大洲对阵" vs "跨大洲对阵"
print("\n" + "="*50)
print("[7] 同洲 vs 跨洲 淘汰赛冷门率 (代理: '了解对手')")
print("="*50)
europe = {'Germany','Belgium','Portugal','Switzerland','France','Spain','Denmark','England','Croatia',
          'Sweden','Serbia','Iceland','Poland','Netherlands','Wales','Russia'}
samerica = {'Brazil','Argentina','Uruguay','Colombia','Peru'}
africa = {'Senegal','Morocco','Egypt','Nigeria','Tunisia','Ghana','Cameroon'}
asia = {'Japan','South Korea','Iran','Australia','Saudi Arabia','Qatar'}
northam = {'Mexico','USA','Costa Rica','Panama','Canada'}

def continent(team):
    if team in europe: return 'EU'
    if team in samerica: return 'SA'
    if team in africa: return 'AF'
    if team in asia: return 'AS'
    if team in northam: return 'NA'
    return '??'

for label, matches in [("小组赛", all_grp), ("淘汰赛", all_ko)]:
    same_conf = [m for m in matches if continent(m['stronger']) == continent(m['weaker'])]
    cross_conf = [m for m in matches if continent(m['stronger']) != continent(m['weaker'])]
    if same_conf:
        up_same = sum(1 for m in same_conf if m['is_upset'])/len(same_conf)*100
    else:
        up_same = 0
    if cross_conf:
        up_cross = sum(1 for m in cross_conf if m['is_upset'])/len(cross_conf)*100
    else:
        up_cross = 0
    print(f"  {label}: 同洲冷门{up_same:.0f}%({len(same_conf)}场) vs 跨洲冷门{up_cross:.0f}%({len(cross_conf)}场)")

# ── CLAIM 8: 弱队小组赛进球 vs 淘汰赛进球 ──
print("\n" + "="*50)
print("[8] 弱队进球: 小组赛 vs 淘汰赛 (驳'用小组赛总量推淘汰赛')")
print("="*50)
# Group by (year, weaker_team) — compare group stage avg goals to KO goals for the SAME team
from collections import defaultdict
team_grp = defaultdict(list)  # (year, team) -> [goals in group stage]
team_ko = defaultdict(list)   # (year, team) -> [goals in KO]
for m in all_grp:
    team_grp[(m['year'], m['weaker'])].append(m['wg'])
for m in all_ko:
    team_ko[(m['year'], m['weaker'])].append(m['wg'])

# Teams that played BOTH group stage and knockout
both = set(team_grp.keys()) & set(team_ko.keys())
print(f"  两队都打的弱队: {len(both)}支")
higher_in_ko = 0
for key in both:
    grp_avg = sum(team_grp[key])/len(team_grp[key])
    ko_avg = sum(team_ko[key])/len(team_ko[key])
    if ko_avg > grp_avg:
        higher_in_ko += 1
        if ko_avg - grp_avg > 0.5:
            print(f"    {key[0]} {key[1]}: 小组{grp_avg:.1f}球/场 → 淘汰赛{ko_avg:.1f}球/场 [显著提升]")
print(f"  淘汰赛进球>小组赛: {higher_in_ko}/{len(both)} = {higher_in_ko/len(both)*100:.0f}%")

# ── SUMMARY TABLE ──
print("\n" + "="*70)
print("验证结论汇总")
print("="*70)
tests = [
    ("弱队进球率61%", sum(1 for m in all_ko if m['weak_scored'])/len(all_ko)*100, "61%", ">50%为真"),
    ("半场0-0率71%", sum(1 for m in all_ko if m['ht_zz'])/sum(1 for m in all_ko if m['ht_zz'] is not None)*100, "71%", "远低于71%=高估"),
    ("强队进2+球=75%", sum(1 for m in all_ko if m['strong_2plus'])/len(all_ko)*100, "~75%?", ">60%部分支撑"),
    ("强队进0-1球", sum(1 for m in all_ko if m['sg']<=1)/len(all_ko)*100, "~25%?", "22%=少数但不可忽略"),
    ("R16平局率最高", sum(1 for m in all_ko if 'Round of 16' in m['round'] and m['is_draw'])/max(1,sum(1 for m in all_ko if 'Round of 16' in m['round']))*100, "32.5%", ">30%=验证"),
    ("排名差0-5=任何结果都可能", sum(1 for m in all_ko if 0<=m['rank_gap']<=5 and m['sg']>m['wg'])/max(1,sum(1 for m in all_ko if 0<=m['rank_gap']<=5))*100, "~50%", "接近50%=真"),
    ("排名差31+=强队几乎必胜", sum(1 for m in all_ko if m['rank_gap']>=31 and m['sg']>m['wg'])/max(1,sum(1 for m in all_ko if m['rank_gap']>=31))*100, "~90%+?", "<70%=弱"),
]

for name, actual, claimed, judgment in tests:
    bar = '█' * int(actual/5)
    status = '✅' if abs(actual - float(claimed.replace('%','').replace('~','').replace('+','').replace('?','')) if '%' not in claimed else actual - float(claimed.replace('%','').replace('~','')) < 15) else '❌'
    print(f"  {status} {name}: 历史={actual:.0f}% (声称={claimed}) → {judgment} {bar}")
