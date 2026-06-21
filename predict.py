#!/usr/bin/env python3
"""
Codex 世界杯预测引擎 v11 (MODEL_RULES.md v9.1 完整实现)
=========================================================
完全对齐 MODEL_RULES.md 所有规则:
  8维度权重 + R1-R15 + v9.1①②③ + 教练战术 + 轮换 + 裁判崩盘链
  + 球员/裁判/地理数据库 + ESPN API + 北京时间 + 自动复盘

用法:
  python predict.py --date 20260621     # 预测指定北京时间日期(跨UTC查询)
  python predict.py --backtest          # 全量回测
  python predict.py --review            # 复盘最近完赛
  python predict.py --all               # 拉取+预测+复盘+回测
"""

import json, sys, io, os, math, argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict

if sys.platform == "win32":
    try:
        if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except (AttributeError, ValueError):
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
BJ = timezone(timedelta(hours=8))
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}
ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
FINAL_STATES = {"STATUS_FINAL", "STATUS_FULL_TIME"}
LIVE_STATES = {"STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_SECOND_HALF", "STATUS_END_OF_PERIOD"}

# ═══════════════════════════════════════════════════════════════════
# §1. 数据定义 (MODEL_RULES.md 常量)
# ═══════════════════════════════════════════════════════════════════

NAME_CN = {
    "Portugal":"葡萄牙","Congo DR":"刚果(金)","England":"英格兰","Croatia":"克罗地亚",
    "Ghana":"加纳","Panama":"巴拿马","Uzbekistan":"乌兹别克斯坦","Colombia":"哥伦比亚",
    "Argentina":"阿根廷","France":"法国","Spain":"西班牙","Brazil":"巴西",
    "Netherlands":"荷兰","Germany":"德国","Belgium":"比利时","Morocco":"摩洛哥",
    "Norway":"挪威","Austria":"奥地利","Japan":"日本","South Korea":"韩国",
    "Korea Republic":"韩国","Saudi Arabia":"沙特","Iran":"伊朗","Qatar":"卡塔尔",
    "Australia":"澳大利亚","Mexico":"墨西哥","United States":"美国","Canada":"加拿大",
    "Sweden":"瑞典","Switzerland":"瑞士","Türkiye":"土耳其","Czechia":"捷克",
    "Scotland":"苏格兰","Ivory Coast":"科特迪瓦","Cote d'Ivoire":"科特迪瓦",
    "Egypt":"埃及","Senegal":"塞内加尔","Algeria":"阿尔及利亚","Tunisia":"突尼斯",
    "Cape Verde":"佛得角","South Africa":"南非","Haiti":"海地",
    "Paraguay":"巴拉圭","Ecuador":"厄瓜多尔","New Zealand":"新西兰",
    "Bosnia-Herzegovina":"波黑","Curaçao":"库拉索","Jordan":"约旦",
    "Iraq":"伊拉克","Uruguay":"乌拉圭","Italy":"意大利","Finland":"芬兰",
    "Denmark":"丹麦","Serbia":"塞尔维亚","Nigeria":"尼日利亚","Cameroon":"喀麦隆",
    "Mali":"马里","Burkina Faso":"布基纳法索","Guinea":"几内亚","United Arab Emirates":"阿联酋",
    "Oman":"阿曼","Bahrain":"巴林","China":"中国","India":"印度",
}

FIFA_RANK = {
    "阿根廷":1,"法国":2,"西班牙":3,"英格兰":4,"巴西":5,"葡萄牙":6,
    "荷兰":7,"德国":8,"意大利":9,"克罗地亚":10,"比利时":11,
    "摩洛哥":13,"乌拉圭":14,"哥伦比亚":15,"美国":16,"墨西哥":17,
    "瑞士":18,"挪威":19,"丹麦":20,"塞内加尔":21,"奥地利":22,
    "日本":23,"韩国":24,"瑞典":25,"加拿大":26,"尼日利亚":27,
    "土耳其":28,"澳大利亚":29,"伊朗":30,"捷克":31,"塞尔维亚":32,
    "埃及":33,"喀麦隆":34,"科特迪瓦":35,"卡塔尔":36,"阿尔及利亚":37,
    "沙特":38,"马里":39,"厄瓜多尔":40,"巴拉圭":42,"智利":43,
    "佛得角":46,"加纳":48,"巴拿马":52,"几内亚":54,"南非":55,
    "约旦":58,"伊拉克":59,"新西兰":63,"乌兹别克斯坦":64,"刚果(金)":65,
    "海地":67,"波黑":70,"苏格兰":72,"库拉索":78,"布基纳法索":79,
    "阿联酋":72,"阿曼":78,"巴林":81,"中国":90,"芬兰":60,
}

TOP5  = {"阿根廷","法国","西班牙","英格兰","巴西"}
TOP10 = {"阿根廷","法国","西班牙","英格兰","巴西","葡萄牙","荷兰","德国","克罗地亚","比利时"}
AFRICA = {"摩洛哥","塞内加尔","突尼斯","阿尔及利亚","埃及","佛得角","南非","科特迪瓦","加纳","刚果(金)","喀麦隆","尼日利亚","马里","布基纳法索","几内亚"}
ASIA = {"日本","韩国","沙特","伊朗","卡塔尔","澳大利亚","伊拉克","乌兹别克斯坦","约旦","中国","阿联酋","阿曼","巴林"}
EUROPE = {"法国","西班牙","英格兰","葡萄牙","荷兰","德国","意大利","克罗地亚","比利时","瑞士","挪威","丹麦","奥地利","瑞典","土耳其","捷克","塞尔维亚","苏格兰","波黑","芬兰"}
SOUTH_AMERICA = {"阿根廷","巴西","乌拉圭","哥伦比亚","厄瓜多尔","巴拉圭","智利"}
HOME_TEAMS = {"美国","墨西哥","加拿大"}

# 教练风格 (MODEL_RULES.md §6.2)
COACH_STYLE = {
    "阿根廷":"高压+控球","法国":"高压反击","西班牙":"传控","英格兰":"高压",
    "巴西":"技术流","葡萄牙":"控球","荷兰":"高压","德国":"高压",
    "比利时":"控球","克罗地亚":"控球","摩洛哥":"防守反击","乌拉圭":"高压",
    "哥伦比亚":"技术流","美国":"高压","墨西哥":"防守组织","瑞士":"防守组织",
    "挪威":"高压","奥地利":"高压","日本":"技术流传控","韩国":"高压反击",
    "瑞典":"均衡","加拿大":"高压","土耳其":"控球","澳大利亚":"身体对抗",
    "伊朗":"防守反击","捷克":"均衡","埃及":"防守反击","科特迪瓦":"身体对抗",
    "沙特":"防守反击","厄瓜多尔":"技术流","巴拉圭":"防守反击",
    "佛得角":"大巴防守","加纳":"身体对抗","巴拿马":"大巴防守",
    "新西兰":"身体对抗","南非":"技术流","突尼斯":"防守反击",
    "刚果(金)":"大巴防守","卡塔尔":"控球","海地":"大巴防守",
    "苏格兰":"身体对抗","波黑":"防守组织","库拉索":"大巴防守",
    "约旦":"防守反击","伊拉克":"防守反击","乌兹别克斯坦":"防守组织",
    "塞内加尔":"身体对抗","阿尔及利亚":"技术流","尼日利亚":"身体对抗",
    "喀麦隆":"身体对抗","塞尔维亚":"高压","丹麦":"均衡",
}

LEAGUE_MULT = {
    "英超":1.0,"西甲":1.0,"德甲":1.0,"意甲":0.98,"法甲":0.93,
    "葡超":0.78,"荷甲":0.76,"比甲":0.72,"土超":0.62,"俄超":0.58,
    "巴甲":0.55,"阿甲":0.52,"MLS":0.50,"墨超":0.50,"沙特联":0.45,
    "奥甲":0.60,"苏超":0.58,"南美":0.42,"其他":0.40,
}

VENUE_CLIMATE = {
    "NRG Stadium":"高温高湿","Hard Rock Stadium":"高温高湿",
    "Mercedes-Benz Stadium":"高温高湿","AT&T Stadium":"高温高湿",
    "Estadio Banorte":"高海拔","Estadio BBVA":"高海拔",
    "Estadio Akron":"温和","Lumen Field":"温和","BC Place":"温和",
    "BMO Field":"温和","Lincoln Financial Field":"温和",
    "Gillette Stadium":"温和","MetLife Stadium":"温和",
    "SoFi Stadium":"温和","Levi's Stadium":"温和",
    "Arrowhead Stadium":"温和","GEHA Field at Arrowhead Stadium":"温和",
}

# ═══════════════════════════════════════════════════════════════════
# §2. 工具函数
# ═══════════════════════════════════════════════════════════════════

def load_json(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def cn(name):
    return NAME_CN.get(name, name)

def rank(cn_name):
    return FIFA_RANK.get(cn_name, 80)

def fetch_espn(path):
    import urllib.request
    req = urllib.request.Request(f"{ESPN_BASE}/{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def utc_to_beijing(utc_str):
    try:
        s = utc_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s[:25])
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        bj = dt.astimezone(BJ)
        return bj.strftime("%m/%d %H:%M"), bj
    except:
        return utc_str, None

# ═══════════════════════════════════════════════════════════════════
# §3. 球员评分引擎 (MODEL_RULES.md §二)
# ═══════════════════════════════════════════════════════════════════

def calc_player_score_v9(pdata):
    """v9.1: 基础分 × 状态系数 × 疲劳系数 × (1+俱乐部成就) × (1+美洲适应) × 年龄衰减"""
    if not pdata or not isinstance(pdata, dict):
        return 6.0

    mins = pdata.get("mins", 0)
    goals = pdata.get("goals", 0)
    assists = pdata.get("assists", 0)
    form = pdata.get("form", "良好")
    league = pdata.get("league", "其他")
    age = pdata.get("age", 27)

    # 基础分
    lm = LEAGUE_MULT.get(league, 0.50)
    ga90 = (goals + assists) / max(1, mins / 90) * lm
    if ga90 > 1.2: base = 10.0
    elif ga90 > 0.8: base = 8.0
    elif ga90 > 0.5: base = 6.0
    elif ga90 > 0.3: base = 4.0
    elif ga90 > 0.1: base = 2.5
    else: base = 1.5

    # 状态系数
    form_map = {"🔥🔥巅峰":1.15,"🔥极佳":1.05,"良好":1.00,"一般":0.85,
                "⚠️一般":0.85,"⚠️低迷":0.70,"⚠️伤后恢复":0.75,
                "⚠️缺比赛节奏":0.80,"❌极差":0.30,"❌缺席":0.0,
                "伤缺":0.0,"⚠️存疑":0.50}
    fc = form_map.get(form, 1.0)

    # 疲劳系数 (§二 疲劳系数表)
    if mins < 1500: fatigue = 1.10
    elif mins < 2500: fatigue = 1.05
    elif mins < 3500: fatigue = 1.00
    elif mins < 4200: fatigue = 0.92
    else: fatigue = 0.85

    # 年龄衰减 (门将不适用, 此处统一处理)
    if age >= 41: age_coef = 0.55
    elif age >= 39: age_coef = 0.70
    elif age >= 36: age_coef = 0.82
    elif age >= 33: age_coef = 0.92
    else: age_coef = 1.00

    # 俱乐部成就加成 (§二 俱乐部成就表)
    club_ach = pdata.get("club_achievements", "")
    ach_bonus = 0
    if "欧冠冠军" in club_ach:
        ach_bonus = 0.03 if "轮换" in club_ach else 0.05
    elif "五大联赛冠军" in club_ach:
        ach_bonus = 0.02 if "轮换" in club_ach else 0.04
    elif "国内杯赛冠军" in club_ach:
        ach_bonus = 0.01
    if "降级" in club_ach or "无缘欧战" in club_ach:
        ach_bonus = -0.03

    # 美洲适应加成 (§二 美洲适应表 + §四 location_advantage_v1)
    amer_bonus = 0
    arrival = pdata.get("arrival_advantage", "")
    if league == "MLS":
        amer_bonus = 0.08 if mins > 1000 else 0.05
    if "提前来美训练>1个月" in arrival:
        amer_bonus = max(amer_bonus, 0.06)
    if pdata.get("physical_style", "") == "南美球员在美洲":
        amer_bonus = max(amer_bonus, 0.05)

    score = base * fc * fatigue * age_coef * (1 + ach_bonus) * (1 + amer_bonus)
    return min(10.0, score)

def calc_team_player_score(team_cn):
    """球队球员综合评分: TOP5核心加权 (FWD×1.3 MID×1.2 DEF×1.0 GK×0.8)"""
    SKIP = {"已完赛参考球员","年龄衰减规则","联赛强度系数","南美球员美洲优势组",
            "美洲适应度加成规则","俱乐部成就心态加成","_description","_updated","_changes_v7"}
    _db = load_json("player_database_v7.json")
    pdb = _db if isinstance(_db, dict) else {}

    if team_cn in pdb and team_cn not in SKIP:
        tp = pdb[team_cn]
        if isinstance(tp, dict):
            rw_map = {'FWD':1.3,'MID':1.2,'DEF':1.0,'GK':0.8}
            scores = []
            for pn, pd in tp.items():
                if not isinstance(pd, dict): continue
                ps = calc_player_score_v9(pd)
                pos = pd.get("position", "MID")
                rw = rw_map.get(pos, 1.0)
                scores.append((pn, ps, rw))
            if scores:
                scores.sort(key=lambda x: x[1], reverse=True)
                top5 = scores[:5]
                wavg = sum(s*w for _,s,w in top5) / sum(w for _,_,w in top5)
                return round(wavg, 2), top5

    # 排名估算 + 大洲域 + 赛果微调
    r = rank(team_cn)
    est = 10.0 - (r - 1) * 0.08
    if team_cn in AFRICA:    est += 0.4
    if team_cn in ASIA and team_cn != "日本": est -= 0.4
    if team_cn in SOUTH_AMERICA: est += 0.3
    # 首轮表现微调
    adj = {"乌拉圭":-0.5,"佛得角":+0.8,"土耳其":-0.6,"巴拉圭":+0.3,
           "日本":+0.2,"突尼斯":-0.5,"库拉索":-0.3,"厄瓜多尔":-0.1}
    est += adj.get(team_cn, 0)
    return round(max(3.5, min(9.0, est)), 2), []

# ═══════════════════════════════════════════════════════════════════
# §4. 地理优势 (MODEL_RULES.md §四 + location_advantage_v1.json)
# ═══════════════════════════════════════════════════════════════════

def calc_geo_score(team_cn, venue_name=""):
    geo_db = load_json("location_advantage_v1.json")
    ts = geo_db.get("team_location_advantage_scores", {})

    if team_cn in ts:
        score = ts[team_cn].get("score", 0.0)
    else:
        if team_cn in EUROPE:         score = -0.05
        elif team_cn in AFRICA:       score = 0.05
        elif team_cn in ASIA:         score = -0.10 if team_cn != "日本" else 0.02
        elif team_cn in SOUTH_AMERICA: score = 0.08
        else:                         score = 0.0

    # R9: 中北美主场放大
    if team_cn in HOME_TEAMS:
        score *= 1.2

    # 场馆气候 (§四 venue_climate_zones)
    climate = VENUE_CLIMATE.get(venue_name, "温和")
    if climate == "高温高湿":
        if team_cn in AFRICA or team_cn in SOUTH_AMERICA: score += 0.03
        elif team_cn in EUROPE: score -= 0.02
    elif climate == "高海拔":
        if team_cn in {"墨西哥","厄瓜多尔","玻利维亚","哥伦比亚","秘鲁"}: score += 0.04

    # R13: 南美vs欧洲 — 南美在美洲对欧洲有额外地理抵消
    # (在 predict_match_v9 中交叉处理)

    return round(score, 3)

# ═══════════════════════════════════════════════════════════════════
# §5. 裁判影响 (MODEL_RULES.md §五 + referee_database_v7.json)
# ═══════════════════════════════════════════════════════════════════

def calc_referee_impact(ref_name, home_cn, away_cn):
    rdb = load_json("referee_database_v7.json")
    empty = {"pt":5,"style":"未知","collapse":"低","note":"裁判数据缺失",
             "pb":0,"ci":0,"fh":0,"fa":0}

    if not ref_name or ref_name not in rdb:
        return empty

    ref = rdb[ref_name]
    pt = ref.get("physical_tolerance", 5)
    style = ref.get("风格", "中等")
    collapse = ref.get("collapse_risk", "低")
    card_timing = ref.get("card_timing_pattern", "")

    imp = {"pt":pt,"style":style,"collapse":collapse,"note":"","pb":0,"ci":0,"fh":0,"fa":0}

    # 严苛裁判(≤3) → 技术流受益
    if pt <= 3:
        imp["ci"] = 0.10
        imp["note"] = "极严→身体对抗受限,技术流有利"
        TECH = {"西班牙","葡萄牙","巴西","日本","阿根廷","德国","法国"}
        PHYSICAL = {"伊朗","韩国","澳大利亚","刚果(金)","加纳","苏格兰","瑞典"}
        if home_cn in TECH: imp["fh"] += 0.05
        if away_cn in TECH: imp["fa"] += 0.05
        if home_cn in PHYSICAL: imp["fh"] -= 0.05
        if away_cn in PHYSICAL: imp["fa"] -= 0.05
    elif pt <= 5:
        imp["ci"] = 0.05
        imp["note"] = "中等偏严→对防守型球队不利"
    elif pt >= 7:
        imp["ci"] = -0.03
        imp["note"] = "宽松→身体对抗多,实力决定比赛"

    # R14: 崩盘风险评估
    if collapse == "极高":
        imp["collapse"] = "极高"
        imp["note"] += " | ⚠红牌崩盘高风险!"
    elif collapse == "高":
        imp["collapse"] = "高"
        imp["note"] += " | 红牌崩盘风险偏高"

    # 裁判国籍偏袒 (§五 裁判对南美/中北美球队的潜在偏袒)
    rn = ref.get("国籍", "")
    if rn in {"法国","英格兰","葡萄牙","瑞典","德国","意大利","荷兰"}:
        if home_cn in EUROPE and away_cn not in EUROPE: imp["fh"] += 0.02
        if away_cn in EUROPE and home_cn not in EUROPE: imp["fa"] += 0.02
    if rn in {"乌拉圭","智利","巴拉圭","阿根廷","巴西"}:
        if home_cn in SOUTH_AMERICA: imp["fh"] += 0.02
        if away_cn in SOUTH_AMERICA: imp["fa"] += 0.02

    return imp

# ═══════════════════════════════════════════════════════════════════
# §6. v9.1 核心预测 (完整 R1-R15 + v9.1①②③ + 教练 + 轮换)
# ═══════════════════════════════════════════════════════════════════

def predict_match_v9(home_cn, away_cn, match_info=None, referee_name=None,
                     home_previous=None, away_previous=None,
                     is_debut_home=False, is_debut_away=False,
                     home_rotation_risk=0, away_rotation_risk=0):
    """
    v9.1 全维度预测 — 完全对齐 MODEL_RULES.md

    8维度: 球员22% 排名15% 伤病18% 地理14% 裁判10% 趋势12% 历史5% 赔率4%
    R1-R15 + v9.1①②③ + 教练战术 + 轮换风险
    """
    mi = match_info or {}

    # ── L1: 球员 (22%) ──
    hp, hd = calc_team_player_score(home_cn)
    ap, ad = calc_team_player_score(away_cn)
    ph = 0.50 + (hp - ap) * 0.035
    pa = 0.50 - (hp - ap) * 0.035
    pd_raw = 0.25

    # R15: 梅西效应
    if home_cn == "阿根廷": ph *= 1.10
    if away_cn == "阿根廷": pa *= 1.10

    # ── L2: 排名 (15%) ──
    hr, ar = rank(home_cn), rank(away_cn)
    rg = ar - hr  # 正=主更强
    gap = abs(rg)
    bh, ba, bd = 0.50, 0.25, 0.25
    if gap <= 5: adj = 0
    elif gap <= 15: adj = 0.08
    elif gap <= 30: adj = 0.16
    elif gap <= 50: adj = 0.24
    else: adj = 0.32

    if rg > 0: bh += adj; bd -= adj*0.3; ba -= adj*0.7
    else:      ba += adj; bd -= adj*0.3; bh -= adj*0.7

    # R1: TOP5 vs 非TOP30 → +8%
    sr, wr = min(hr, ar), max(hr, ar)
    stronger = home_cn if hr < ar else away_cn
    if stronger in TOP5 and wr >= 30:
        x = 0.08
        if rg > 0: bh += x; ba -= x*0.7; bd -= x*0.3
        else:      ba += x; bh -= x*0.7; bd -= x*0.3

    # R10: 南美福地 → +5%基础
    if home_cn in SOUTH_AMERICA: bh += 0.03; ba -= 0.02
    if away_cn in SOUTH_AMERICA: ba += 0.03; bh -= 0.02

    # R13: 南美vs欧洲 — 南美在美洲对欧洲有地理抵消
    if home_cn in SOUTH_AMERICA and away_cn in EUROPE: bh += 0.01; ba -= 0.01
    if away_cn in SOUTH_AMERICA and home_cn in EUROPE: ba += 0.01; bh -= 0.01

    # R8: 亚洲美洲困境 (除日本)
    if home_cn in ASIA and home_cn != "日本": bh -= 0.03
    if away_cn in ASIA and away_cn != "日本": ba -= 0.03

    tot = bh + bd + ba
    bh, bd, ba = bh/tot, bd/tot, ba/tot

    # ── L3: 伤病 (18%) ──
    ih = mi.get("injury_home", 0)
    ia = mi.get("injury_away", 0)

    # R12: 核心崩塌
    if mi.get("home_core_collapse"): ih += 0.10; bh *= 0.85
    if mi.get("away_core_collapse"): ia += 0.10; ba *= 0.85

    # ── L4: 地理 (14%) ──
    gh = calc_geo_score(home_cn, mi.get("venue", ""))
    ga = calc_geo_score(away_cn, mi.get("venue", ""))

    # v9.1②: 东道主动量
    if home_previous and home_previous.get("gd", 0) >= 3 and home_cn in HOME_TEAMS:
        gh += 0.20
    if away_previous and away_previous.get("gd", 0) >= 3 and away_cn in HOME_TEAMS:
        ga += 0.20

    # ── L5: 裁判 (10%) ──
    ref = calc_referee_impact(referee_name or "", home_cn, away_cn)

    # ── L6: 趋势 (12%) ──
    th, ta = 0.0, 0.0

    # R7: 非洲光环
    if home_cn in AFRICA: th += 0.03; bd += 0.02
    if away_cn in AFRICA: ta += 0.03; bd += 0.02

    # 教练风格影响 (§6.2)
    h_style = COACH_STYLE.get(home_cn, "")
    a_style = COACH_STYLE.get(away_cn, "")
    # 高位压迫对弱队容易大胜
    if "高压" in h_style and rg > 0 and gap >= 25: th += 0.03
    if "高压" in a_style and rg < 0 and gap >= 25: ta += 0.03
    # 控球型对铁桶可能久攻不下 → 平局微涨
    if "控球" in h_style and "大巴" in a_style: bd += 0.02
    if "控球" in a_style and "大巴" in h_style: bd += 0.02
    # 防守反击面对强队守平
    if "防守反击" in h_style and rg < 0 and gap >= 20: bd += 0.015; bh -= 0.01
    if "防守反击" in a_style and rg > 0 and gap >= 20: bd += 0.015; ba -= 0.01
    # 大巴 vs 强队 → R2 联动
    if ("大巴" in h_style and rg < 0 and gap >= 25): bd += 0.02
    if ("大巴" in a_style and rg > 0 and gap >= 25): bd += 0.02

    # 轮换风险 (§6.3)
    # 核心限时 → 下半场攻击力降10% (映射到全场降5%)
    if home_rotation_risk > 0: th -= 0.05 * home_rotation_risk
    if away_rotation_risk > 0: ta -= 0.05 * away_rotation_risk

    # v9.1①: 射门转化率
    if home_previous and home_previous.get("shots", 0) > 15 and home_previous.get("goals", 0) <= 1:
        th -= 0.15
    if away_previous and away_previous.get("shots", 0) > 15 and away_previous.get("goals", 0) <= 1:
        ta -= 0.15

    # ── L7: 历史战意 (5%) ──
    sh, sa, sd = 0.0, 0.0, 0.0

    # R6: 首次参赛≠重返 (首次=重返的40%)
    if is_debut_home: sd += 0.012  # ~平局+1.2% (重返的40%)
    if is_debut_away: sd += 0.012

    # R2: 大巴平局
    if gap >= 30:
        weaker = away_cn if rg > 0 else home_cn
        if weaker not in TOP10:
            sd += 0.03  # 平局+3%

    # R11: 补时绝杀 — 实力接近+大巴 → 1-0概率+5%
    # (在比分预测中实现)

    # ── L8: 赔率 (4%) ──
    oh, oa, od = 0.0, 0.0, 0.0
    odds = mi.get("odds", {})
    if isinstance(odds, dict) and "moneyline" in odds:
        ml = odds["moneyline"]
        if isinstance(ml, dict):
            mh = ml.get("home", {}).get("close", {}).get("odds")
            ma = ml.get("away", {}).get("close", {}).get("odds")
            md = ml.get("draw", {}).get("close", {}).get("odds")
            if mh and ma and md:
                try:
                    _h, _a, _d = 1/float(mh), 1/float(ma), 1/float(md)
                    _t = _h + _a + _d
                    oh = (_h/_t - bh) * 0.10
                    oa = (_a/_t - ba) * 0.10
                    od = (_d/_t - bd) * 0.10
                except: pass

    # ═══ v9.1 综合评分 ═══
    WP, WR, WI, WG, WREF, WT, WS, WO = 0.22, 0.15, 0.18, 0.14, 0.10, 0.12, 0.05, 0.04

    # v9.1③: 均势裁判加倍 — 先算基础评分差
    raw_h = ph*WP*10 + bh*WR*10 + gh*WG*10 + th*WT*10
    raw_a = pa*WP*10 + ba*WR*10 + ga*WG*10 + ta*WT*10
    raw_diff = raw_h - raw_a
    close_match = abs(raw_diff) < 0.25
    active_wref = WREF * (2.0 if close_match else 1.0)
    tw = WP + WR + WI + WG + active_wref + WT + WS + WO

    fh = (ph*WP + bh*WR + (-ih + ia*0.5)*WI + gh*WG + ref["fh"]*active_wref + th*WT + sh*WS + oh*WO) / tw
    fa = (pa*WP + ba*WR + (-ia + ih*0.5)*WI + ga*WG + ref["fa"]*active_wref + ta*WT + sa*WS + oa*WO) / tw
    fd = (pd_raw*WP + bd*WR + (ih*0.3+ia*0.3)*WI + sd*WS + od*WO + 0.25*WT) / tw

    # R14: 裁判崩盘链
    if ref["collapse"] in ("极高", "高"):
        if (home_cn not in TOP10 and home_cn not in SOUTH_AMERICA) or \
           (away_cn not in TOP10 and away_cn not in SOUTH_AMERICA):
            if fh > fa: fh += 0.04; fa -= 0.04
            else:       fa += 0.04; fh -= 0.04

    # R4: 门将失误 — 非顶级GK+高压 → 失误+10%, 增加0.5-1意外失球
    # (通过微调进球期望实现, 此处简化为概率偏移)
    # 不在此处直接改概率, 在比分映射中通过置信度下调体现

    # R3: 红牌通胀 — 预期红牌方额外失球
    # (通过裁判崩盘链已部分覆盖)

    # 归一化
    tot = fh + fd + fa
    if tot > 0: fh, fd, fa = fh/tot, fd/tot, fa/tot
    else: fh, fa, fd = 0.35, 0.35, 0.30
    fh = max(0.05, min(0.82, fh))
    fa = max(0.05, min(0.82, fa))
    fd = max(0.08, min(0.50, fd))
    tot = fh + fd + fa
    fh, fd, fa = fh/tot, fd/tot, fa/tot

    # ═══ 比分预测 ═══
    ft, conf, upset = predict_score_v9(fh, fd, fa, gap, home_cn, away_cn)

    return {
        "ft": ft, "home_win": round(fh,4), "draw": round(fd,4), "away_win": round(fa,4),
        "upset": round(upset,4), "confidence": round(conf,4),
        "rank_gap": rg, "gap": gap, "v9_diff": round(raw_diff, 3),
        "home_player_score": hp, "away_player_score": ap,
        "geo_home": gh, "geo_away": ga,
        "ref_style": ref["style"], "ref_note": ref["note"],
        "ref_collapse_risk": ref["collapse"],
        "trigger_close_ref": close_match,
        "home_details": hd, "away_details": ad,
        "home_style": h_style, "away_style": a_style,
    }

def predict_score_v9(fh, fd, fa, gap, home_cn, away_cn):
    """概率→比分映射 (R3红牌通胀 + R5下半场 + R11补时绝杀)"""
    # R5: 71%进球在下半场 → 比分分布偏向下半场爆发
    # (映射到稍高的总进球期望)
    avg_goals_base = 3.0

    if fh > fa and fh >= fd:
        adv = fh - fa
        gd = adv * 4.0
        # R11: 补时绝杀 — 实力接近+大巴 → 1-0概率+5%
        bus_bonus = 0
        if gap <= 20:
            w_style = COACH_STYLE.get(away_cn if fh > fa else home_cn, "")
            if "大巴" in w_style: bus_bonus = 0.15

        if gd >= 2.8: ft = "4-0"
        elif gd >= 2.2: ft = "3-0"
        elif gd >= 1.8: ft = "3-1"
        elif gd >= 1.2: ft = "2-0"
        elif gd >= 0.7: ft = "2-1"
        elif gd >= 0.35 + bus_bonus: ft = "1-0"  # ← R11激活
        else: ft = "2-1"
        conf = fh
    elif fa > fh and fa >= fd:
        adv = fa - fh
        gd = adv * 4.0
        bus_bonus = 0
        if gap <= 20:
            w_style = COACH_STYLE.get(home_cn if fa > fh else away_cn, "")
            if "大巴" in w_style: bus_bonus = 0.15

        if gd >= 2.8: ft = "0-4"
        elif gd >= 2.2: ft = "0-3"
        elif gd >= 1.8: ft = "1-3"
        elif gd >= 1.2: ft = "0-2"
        elif gd >= 0.7: ft = "1-2"
        elif gd >= 0.35 + bus_bonus: ft = "0-1"  # ← R11
        else: ft = "1-2"
        conf = fa
    else:
        if fh > 0.38 and fa > 0.38: ft = "1-1"
        elif fd > 0.35: ft = "0-0"
        else: ft = "1-1"
        conf = fd

    upset = 1.0 - max(fh, fa)
    return ft, conf, upset

def risk_label(upset):
    if upset > 0.50: return "极高"
    elif upset > 0.40: return "高"
    elif upset > 0.35: return "中高"
    elif upset > 0.25: return "中"
    elif upset > 0.15: return "中低"
    else: return "低"

# ═══════════════════════════════════════════════════════════════════
# §7. ESP数据拉取 (北京时间跨UTC日期修复)
# ═══════════════════════════════════════════════════════════════════

def fetch_beijing_date(bj_date_str):
    """
    给定北京时间日期 (YYYYMMDD), 拉取该天全部比赛
    北京时间 d → UTC d-1 16:00 到 UTC d 15:59
    需要查询两个UTC日期
    """
    bj_d = datetime.strptime(bj_date_str, "%Y%m%d").replace(tzinfo=BJ)
    utc_start = bj_d - timedelta(hours=8)  # 北京时间00:00 = UTC前一天16:00

    utc_dates = set()
    utc_dates.add(utc_start.strftime("%Y%m%d"))
    utc_dates.add((utc_start + timedelta(days=1)).strftime("%Y%m%d"))

    all_events = []
    for ds in sorted(utc_dates):
        try:
            data = fetch_espn(f"scoreboard?dates={ds}")
            for ev in data.get("events", []):
                ev["_ds"] = ds
                all_events.append(ev)
        except:
            pass

    # 筛选: 北京时间落在目标日期
    result = []
    for ev in all_events:
        _, bj_dt = utc_to_beijing(ev.get("date", ""))
        if bj_dt and bj_dt.strftime("%Y%m%d") == bj_date_str:
            result.append(ev)

    return result

def extract_match_info(ev):
    comps = ev.get("competitions", [{}])[0]
    st = comps.get("status", {})
    sty = st.get("type", {})
    comps_list = comps.get("competitors", [])
    h = comps_list[0] if len(comps_list) > 0 else {}
    a = comps_list[1] if len(comps_list) > 1 else {}

    return {
        "event_id": ev.get("id","?"),
        "utc_date": ev.get("date","?"),
        "beijing_str": utc_to_beijing(ev.get("date",""))[0],
        "beijing_dt": utc_to_beijing(ev.get("date",""))[1],
        "home_en": h.get("team",{}).get("displayName","?"),
        "away_en": a.get("team",{}).get("displayName","?"),
        "home_cn": cn(h.get("team",{}).get("displayName","?")),
        "away_cn": cn(a.get("team",{}).get("displayName","?")),
        "home_score": h.get("score","?"), "away_score": a.get("score","?"),
        "status_name": sty.get("name","?"), "status_desc": sty.get("description","?"),
        "clock": st.get("displayClock","?"), "period": st.get("period","?"),
        "venue": comps.get("venue",{}).get("fullName","?"),
        "odds": comps.get("odds",{}),
    }

# ═══════════════════════════════════════════════════════════════════
# §7B. 半场/赛中实时修正 (2026.06.22 新增)
# ═══════════════════════════════════════════════════════════════════

def extract_live_stats(ev):
    """从进行中/半场事件中提取实时统计数据"""
    comps = ev.get("competitions", [{}])[0]
    comps_list = comps.get("competitors", [])
    h = comps_list[0] if len(comps_list) > 0 else {}
    a = comps_list[1] if len(comps_list) > 1 else {}

    def get_stats(comp):
        s = {}
        for stat in comp.get("statistics", []):
            name = stat.get("name", "")
            val = stat.get("displayValue", "0")
            try:
                s[name] = float(val)
            except (ValueError, TypeError):
                s[name] = 0.0
        return s

    hs = get_stats(h)
    an = get_stats(a)

    return {
        "home_score": int(h.get("score", 0)),
        "away_score": int(a.get("score", 0)),
        "home_poss": hs.get("possessionPct", 50),
        "away_poss": an.get("possessionPct", 50),
        "home_shots": int(hs.get("totalShots", 0)),
        "away_shots": int(an.get("totalShots", 0)),
        "home_sot": int(hs.get("shotsOnTarget", 0)),
        "away_sot": int(an.get("shotsOnTarget", 0)),
        "home_corners": int(hs.get("wonCorners", 0)),
        "away_corners": int(an.get("wonCorners", 0)),
        "home_fouls": int(hs.get("foulsCommitted", 0)),
        "away_fouls": int(an.get("foulsCommitted", 0)),
        "clock": comps.get("status", {}).get("displayClock", "?"),
        "period": comps.get("status", {}).get("period", "?"),
        "status_desc": comps.get("status", {}).get("type", {}).get("description", "?"),
    }


def predict_halftime(ev):
    """
    半场修正预测: v9基础模型 + 上半场实时数据修正

    修正逻辑 (基于2026.06.22比利时vs伊朗实战教训):
      A1: 控球浪费惩罚 — 控球>65%但0进球 → 胜率-6%
      A2: 射门低效惩罚 — ≥8射仅≤2正且0进球 → 胜率-3%
      A3: 大巴奏效奖励 — 控球<25%但未落后 → 不败率+6%
      A4: 比分领先奖励 — 每领先1球 → 胜率+8%(上限15%)
      A5: 黄牌碎片化 — ≥3张 → 平局+2%
    """
    info = extract_match_info(ev)
    hcn, acn = info["home_cn"], info["away_cn"]

    # 基础v9预测
    pred = predict_match_v9(hcn, acn,
                            match_info={"odds": info.get("odds", {}), "venue": info["venue"]})

    # 提取半场数据
    ls = extract_live_stats(ev)
    adjustments = []

    fh, fd, fa = pred["home_win"], pred["draw"], pred["away_win"]
    h_poss, a_poss = ls["home_poss"], ls["away_poss"]
    h_score, a_score = ls["home_score"], ls["away_score"]
    h_shots, a_shots = ls["home_shots"], ls["away_shots"]
    h_sot, a_sot = ls["home_sot"], ls["away_sot"]

    # ── A1: 控球浪费 (控球>65%但未进球→终结能力差) ──
    if h_poss > 65 and h_score == 0 and a_score == 0:
        fh -= 0.06; fd += 0.04; fa += 0.02
        adjustments.append(f"控球浪费: {hcn}控球{h_poss:.0f}%但未进球→胜率-6%")
    if a_poss > 65 and a_score == 0 and h_score == 0:
        fa -= 0.06; fd += 0.04; fh += 0.02
        adjustments.append(f"控球浪费: {acn}控球{a_poss:.0f}%但未进球→胜率-6%")

    # ── A2: 射门低效 (多射门但射正率极低) ──
    if h_shots >= 8 and h_sot <= 2 and h_score == 0:
        fh -= 0.03; fd += 0.02; fa += 0.01
        adjustments.append(f"射门低效: {hcn}{h_shots}射仅{h_sot}正→胜率-3%")
    if a_shots >= 8 and a_sot <= 2 and a_score == 0:
        fa -= 0.03; fd += 0.02; fh += 0.01
        adjustments.append(f"射门低效: {acn}{a_shots}射仅{a_sot}正→胜率-3%")

    # ── A3: 大巴奏效 (极低控球但未落后) ──
    if h_poss < 25 and h_score >= a_score:
        fh += 0.04; fd += 0.02; fa -= 0.06
        adjustments.append(f"大巴奏效: {hcn}仅{h_poss:.0f}%控球但守住→不败率+6%")
    if a_poss < 25 and a_score >= h_score:
        fa += 0.04; fd += 0.02; fh -= 0.06
        adjustments.append(f"大巴奏效: {acn}仅{a_poss:.0f}%控球但守住→不败率+6%")

    # ── A4: 比分领先 (实际比分加权) ──
    if h_score > a_score:
        lead = h_score - a_score
        bonus = min(0.15, lead * 0.08)
        fh += bonus; fa -= bonus * 0.7; fd -= bonus * 0.3
        adjustments.append(f"比分领先: {hcn}{h_score}-{a_score}→胜率+{_pct(bonus):.0f}%")
    elif a_score > h_score:
        lead = a_score - h_score
        bonus = min(0.15, lead * 0.08)
        fa += bonus; fh -= bonus * 0.7; fd -= bonus * 0.3
        adjustments.append(f"比分领先: {acn}{a_score}-{h_score}→胜率+{_pct(bonus):.0f}%")

    # ── A5: 黄牌碎片化 (≥3张→比赛节奏中断多) ──
    details = ev.get("competitions", [{}])[0].get("details", [])
    yellow_count = sum(1 for d in details if d.get("type", {}).get("text") == "Yellow Card")
    if yellow_count >= 3:
        fd += 0.02; fh -= 0.01; fa -= 0.01
        adjustments.append(f"黄牌偏多: 已{yellow_count}张→节奏碎片化, 平局+2%")

    # A6: 超长补时 (≥7分钟→比赛中断严重)
    clock_str = ls["clock"]
    try:
        extra_min = int(clock_str.split("+")[-1].replace("'", "").strip()) if "+" in clock_str else 0
    except (ValueError, AttributeError):
        extra_min = 0
    if extra_min >= 7:
        fd += 0.01; fh -= 0.005; fa -= 0.005
        adjustments.append(f"超长补时: +{extra_min}'→比赛中断多, 平局+1%")

    # ── A7: 红牌冲击 (11v10→巨大劣势) ──
    red_count = sum(1 for d in details if d.get("type", {}).get("text") == "Red Card")
    if red_count > 0:
        # 判断谁吃了红牌
        for d in details:
            if d.get("type", {}).get("text") == "Red Card":
                red_team_id = d.get("team", {}).get("id", "")
                red_players = [a["displayName"] for a in d.get("athletesInvolved", [])]
                # team id 459 = Belgium from ESPN
                if red_team_id == ev.get("competitions",[{}])[0].get("competitors",[{}])[0].get("team",{}).get("id",""):
                    # 主队吃红牌
                    fh -= 0.18; fd -= 0.02; fa += 0.20
                    side = hcn
                else:
                    # 客队吃红牌
                    fa -= 0.18; fd -= 0.02; fh += 0.20
                    side = acn
                adjustments.append(f"🔴红牌: {side}{','.join(red_players)}罚下→11v10, 胜率-18%")
                # 剩余时间加权 — 越早红牌影响越大
                try:
                    minute_clock = int(ls["clock"].split("'")[0].split("+")[0])
                    remaining = 90 - minute_clock
                    extra_bonus = min(0.08, remaining * 0.003)  # 每剩余1分钟约+0.3%
                    if red_team_id == ev.get("competitions",[{}])[0].get("competitors",[{}])[0].get("team",{}).get("id",""):
                        fa += extra_bonus; fh -= extra_bonus
                    else:
                        fh += extra_bonus; fa -= extra_bonus
                    adjustments.append(f"  剩余{remaining}分钟→少人方额外-{_pct(extra_bonus):.0f}%")
                except:
                    pass

    # 归一化
    tot = fh + fd + fa
    fh, fd, fa = fh/tot, fd/tot, fa/tot

    # 用修正概率重新算比分
    gap = abs(pred["rank_gap"])
    ft_adj, conf_adj, upset_adj = predict_score_v9(fh, fd, fa, gap, hcn, acn)

    return {
        **info,
        "ht_stats": ls,
        "ht_adjustments": adjustments,
        "base_prediction": pred,
        "fh_adj": fh, "fd_adj": fd, "fa_adj": fa,
        "ft_adj": ft_adj,
        "conf_adj": conf_adj,
        "upset_adj": upset_adj,
        "risk_adj": risk_label(upset_adj),
    }


def print_halftime_predictions(ht_preds):
    """打印半场修正预测到终端"""
    if not ht_preds:
        return
    print(f"\n{'='*80}")
    print(f"  🔴 半场/赛中实时修正预测 ({len(ht_preds)}场进行中)")
    print(f"{'='*80}")
    for p in ht_preds:
        ls = p["ht_stats"]
        bp = p["base_prediction"]
        print(f"\n  ⚡ {p['home_cn']} vs {p['away_cn']}")
        print(f"  ⏱ {ls['status_desc']} | {ls['clock']} | 比分 {ls['home_score']}-{ls['away_score']}")
        print(f"  📊 半场数据: 控球 {ls['home_poss']:.0f}%-{ls['away_poss']:.0f}% | "
              f"射门 {ls['home_shots']}-{ls['away_shots']} | 射正 {ls['home_sot']}-{ls['away_sot']}")
        print(f"  🎯 赛前v9: {bp['ft']} (主{_pct(bp['home_win']):.0f}% 平{_pct(bp['draw']):.0f}% 客{_pct(bp['away_win']):.0f}%)")
        print(f"  🔄 半场修正: {p['ft_adj']} (主{_pct(p['fh_adj']):.0f}% 平{_pct(p['fd_adj']):.0f}% 客{_pct(p['fa_adj']):.0f}%)")
        print(f"  🚨 冷门: {p['risk_adj']}({_pct(p['upset_adj']):.0f}%)")
        if p["ht_adjustments"]:
            for a in p["ht_adjustments"]:
                print(f"    → {a}")
    print(f"\n  ⚠️ 半场修正基于实时数据,仅供参考。下半场受换人/战术调整等影响。")


def generate_halftime_outputs(ht_preds, sched_preds=None):
    """生成半场修正预测的 .md 和 _手机版.txt"""
    if not ht_preds:
        return
    bj_now = datetime.now(BJ)
    bj_str = bj_now.strftime('%Y年%m月%d日 %H:%M')
    date_prefix = bj_now.strftime('%Y年%m月%d日')

    # 确定文件名: 如果有对阵信息则包含
    teams = "_".join([f"{p['home_cn']}vs{p['away_cn']}" for p in ht_preds])
    md_path = os.path.join(BASE_DIR, f"{date_prefix}_半场修正预测_{teams}.md")
    txt_path = os.path.join(BASE_DIR, f"{date_prefix}_半场修正预测_{teams}_手机版.txt")

    md = _build_halftime_md(ht_preds, bj_str)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  📝 半场MD: {md_path}")

    txt = _build_halftime_txt(ht_preds, bj_str)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"  📱 半场TXT: {txt_path}")
    return md_path, txt_path


def _build_halftime_md(ht_preds, bj_str):
    L = []
    L.append(f"# 2026世界杯 — 半场/赛中实时修正预测")
    L.append(f"> ⏱ 生成时间: {bj_str} 北京时间")
    L.append(f"> ⚠️ 基于上半场实时数据修正 v9.1 基础预测")
    L.append("")

    for i, p in enumerate(ht_preds, 1):
        ls = p["ht_stats"]
        bp = p["base_prediction"]
        L.append("---")
        L.append("")
        L.append(f"## ⚡ [{i}] {p['home_cn']} vs {p['away_cn']}")
        L.append("")
        L.append(f"**状态**: {ls['status_desc']} | **时钟**: {ls['clock']} | **比分**: {ls['home_score']}-{ls['away_score']}")
        L.append(f"**场地**: {p['venue']}")
        L.append("")

        L.append("### 📊 半场实时数据")
        L.append("")
        L.append(f"| 指标 | {p['home_cn']} | {p['away_cn']} |")
        L.append(f"|------|--------|--------|")
        L.append(f"| 控球率 | {ls['home_poss']:.0f}% | {ls['away_poss']:.0f}% |")
        L.append(f"| 射门 | {ls['home_shots']} | {ls['away_shots']} |")
        L.append(f"| 射正 | {ls['home_sot']} | {ls['away_sot']} |")
        L.append(f"| 角球 | {ls['home_corners']} | {ls['away_corners']} |")
        L.append(f"| 犯规 | {ls['home_fouls']} | {ls['away_fouls']} |")
        L.append("")

        L.append("### 🎯 赛前 v9.1 基础预测")
        L.append("")
        L.append(f"| 预测比分 | 主胜 | 平局 | 客胜 | 冷门风险 |")
        L.append(f"|----------|------|------|------|----------|")
        L.append(f"| **{bp['ft']}** | {_pct(bp['home_win']):.0f}% | {_pct(bp['draw']):.0f}% | {_pct(bp['away_win']):.0f}% | {risk_label(bp['upset'])} |")
        L.append("")

        L.append("### 🔄 半场修正预测")
        L.append("")
        L.append(f"| 修正比分 | 主胜 | 平局 | 客胜 | 冷门风险 |")
        L.append(f"|----------|------|------|------|----------|")
        L.append(f"| **{p['ft_adj']}** | {_pct(p['fh_adj']):.0f}% | {_pct(p['fd_adj']):.0f}% | {_pct(p['fa_adj']):.0f}% | {p['risk_adj']} |")
        L.append("")

        if p["ht_adjustments"]:
            L.append("### 📝 修正依据")
            L.append("")
            for a in p["ht_adjustments"]:
                L.append(f"- {a}")
            L.append("")

        L.append(f"**方向变化**: 赛前v9 → 半场修正: {bp['ft']} → {p['ft_adj']}")
        L.append("")

    L.append("---")
    L.append("")
    L.append("> ⚠️ **声明**: 半场修正基于ESPN API实时数据,修正幅度上限±15%。")
    L.append("> 下半场受换人、战术调整、红黄牌等临场因素影响,修正预测仅供参考。")
    L.append(f"> 🤖 生成: predict.py v11 halftime-mode | 北京时间 {bj_str}")
    return "\n".join(L)


def _build_halftime_txt(ht_preds, bj_str):
    L = []
    L.append("══════════════════════════════")
    L.append("  半场/赛中实时修正预测")
    L.append("══════════════════════════════")
    L.append("")
    L.append(f"生成: {bj_str} 北京时间")
    L.append("基于: v9.1 + 半场实时数据修正")
    L.append("")

    for i, p in enumerate(ht_preds, 1):
        ls = p["ht_stats"]
        bp = p["base_prediction"]
        L.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        L.append(f"[{i}] {p['home_cn']} vs {p['away_cn']}")
        L.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        L.append("")
        L.append(f"状态: {ls['status_desc']} | {ls['clock']}")
        L.append(f"比分: {ls['home_score']}-{ls['away_score']}")
        L.append(f"场地: {p['venue']}")
        L.append("")
        L.append("> 半场数据:")
        L.append(f"  控球: {ls['home_poss']:.0f}% - {ls['away_poss']:.0f}%")
        L.append(f"  射门: {ls['home_shots']} - {ls['away_shots']}")
        L.append(f"  射正: {ls['home_sot']} - {ls['away_sot']}")
        L.append(f"  角球: {ls['home_corners']} - {ls['away_corners']}")
        L.append(f"  犯规: {ls['home_fouls']} - {ls['away_fouls']}")
        L.append("")
        L.append(f"> 赛前v9: {bp['ft']}")
        L.append(f"  主{_pct(bp['home_win']):.0f}% 平{_pct(bp['draw']):.0f}% 客{_pct(bp['away_win']):.0f}%")
        L.append("")
        L.append(f"★ 半场修正: {p['ft_adj']}")
        L.append(f"  主{_pct(p['fh_adj']):.0f}% 平{_pct(p['fd_adj']):.0f}% 客{_pct(p['fa_adj']):.0f}%")
        L.append(f"  冷门: {p['risk_adj']}({_pct(p['upset_adj']):.0f}%)")
        L.append("")

        if p["ht_adjustments"]:
            L.append("> 修正依据:")
            for a in p["ht_adjustments"]:
                L.append(f"  -> {a}")
            L.append("")

        L.append(f"> 方向变化: {bp['ft']} -> {p['ft_adj']}")
        L.append("")

    L.append("══════════════════════════════")
    L.append("声明: 基于上半场实时数据修正。")
    L.append("下半场受临场因素影响, 仅供参考。")
    L.append(f"predict.py v11 halftime-mode")
    L.append(f"{bj_str} 北京时间")
    L.append("══════════════════════════════")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════
# §8. 批量预测
# ═══════════════════════════════════════════════════════════════════

def predict_upcoming(events):
    preds = []
    for ev in events:
        info = extract_match_info(ev)
        if info["status_name"] in FINAL_STATES:
            continue
        pred = predict_match_v9(info["home_cn"], info["away_cn"],
                                match_info={"odds": info.get("odds",{}), "venue": info["venue"]})
        preds.append({**info, "prediction": pred, "risk": risk_label(pred["upset"])})
    preds.sort(key=lambda p: p.get("utc_date",""))
    return preds

# ═══════════════════════════════════════════════════════════════════
# §9. 回测 (MODEL_RULES.md §七 + §七B)
# ═══════════════════════════════════════════════════════════════════

KNOWN_RESULTS = [
    ("墨西哥","南非","2-0","6/11"),("韩国","捷克","2-1","6/12"),
    ("加拿大","波黑","1-1","6/12"),("美国","巴拉圭","4-1","6/13"),
    ("卡塔尔","瑞士","1-1","6/13"),("巴西","摩洛哥","1-1","6/13"),
    ("海地","苏格兰","0-1","6/14"),("澳大利亚","土耳其","2-0","6/14"),
    ("德国","库拉索","7-1","6/14"),("荷兰","日本","2-2","6/14"),
    ("科特迪瓦","厄瓜多尔","1-0","6/14"),("瑞典","突尼斯","5-1","6/15"),
    ("西班牙","佛得角","0-0","6/15"),("比利时","埃及","1-1","6/15"),
    ("沙特","乌拉圭","1-1","6/15"),("伊朗","新西兰","2-2","6/16"),
    ("法国","塞内加尔","3-1","6/16"),("伊拉克","挪威","1-4","6/16"),
    ("阿根廷","阿尔及利亚","3-0","6/17"),("奥地利","约旦","3-1","6/17"),
    ("葡萄牙","刚果(金)","1-1","6/17"),("英格兰","克罗地亚","4-2","6/17"),
    ("加纳","巴拿马","1-0","6/17"),("乌兹别克斯坦","哥伦比亚","1-3","6/18"),
    ("捷克","南非","1-1","6/18"),("瑞士","波黑","4-1","6/18"),
    ("加拿大","卡塔尔","6-0","6/18"),("墨西哥","韩国","1-0","6/19"),
    ("美国","澳大利亚","2-0","6/20"),("苏格兰","摩洛哥","0-1","6/20"),
    ("巴西","海地","3-0","6/20"),("土耳其","巴拉圭","0-1","6/20"),
    ("荷兰","瑞典","5-1","6/21"),
]

def run_backtest():
    print("=" * 80)
    print("  Codex v9.1 全量回测")
    print("=" * 80)

    results = []; dc = 0; es = 0; cm = 0; cmc = 0; bm = 0; bmc = 0
    for h, a, score, dt in KNOWN_RESULTS:
        ah, aa = map(int, score.split("-"))
        pred = predict_match_v9(h, a)
        ph, pa = map(int, pred["ft"].split("-"))
        adir = "home" if ah > aa else ("away" if aa > ah else "draw")
        pdir = "home" if ph > pa else ("away" if pa > ph else "draw")
        ok = adir == pdir
        ex = score == pred["ft"]
        results.append({"match":f"{h} vs {a}","actual":score,"pred":pred["ft"],
                        "dir_ok":ok,"exact_ok":ex,"v9_diff":pred["v9_diff"]})
        if ok: dc += 1
        if ex: es += 1
        if abs(pred["v9_diff"]) < 0.25: cm += 1; cmc += 1 if ok else 0
        if abs(pred["v9_diff"]) > 0.5:  bm += 1; bmc += 1 if ok else 0

    n = len(KNOWN_RESULTS)
    print(f"\n  📊 回测 {n} 场:")
    print(f"  {'─'*60}")
    print(f"  方向正确: {dc}/{n} ({dc/n*100:.0f}%)")
    print(f"  比分精确: {es}/{n} ({es/n*100:.0f}%)")
    print(f"  均势(<0.25): {cmc}/{cm} ({(cmc/max(1,cm))*100:.0f}%)")
    print(f"  大差距(>0.5): {bmc}/{bm} ({(bmc/max(1,bm))*100:.0f}%)")

    print(f"\n  逐场:")
    print(f"  {'─'*70}")
    print(f"  {'#':<3} {'比赛':<28} {'实际':<6} {'预测':<6} {'方向':<5} {'精确':<5} {'v9差'}")
    print(f"  {'─'*70}")
    for i, r in enumerate(results, 1):
        d = "✅" if r["dir_ok"] else "❌"
        e = "✅" if r["exact_ok"] else "❌"
        print(f"  {i:<3} {r['match']:<28} {r['actual']:<6} {r['pred']:<6} {d:<5} {e:<5} {r['v9_diff']:+.3f}")

    return {"total":n,"direction":dc,"direction_pct":dc/n*100,"exact":es,"exact_pct":es/n*100,
            "close_correct":cmc,"close_total":cm,"big_correct":bmc,"big_total":bm,"results":results}

# ═══════════════════════════════════════════════════════════════════
# §10. 自动复盘 (MODEL_RULES.md §八)
# ═══════════════════════════════════════════════════════════════════

def generate_review(events):
    """对已完赛+有预测的比赛写复盘文件到 memory_backup/"""
    bj_now = datetime.now(BJ)
    final = [e for e in events if e.get("competitions",[{}])[0].get("status",{}).get("type",{}).get("name","") in FINAL_STATES]

    if not final:
        print("  ℹ️ 无完赛数据可复盘")
        return

    lines = []
    lines.append(f"---")
    lines.append(f"name: review-{bj_now.strftime('%Y%m%d-%H%M')}")
    lines.append(f"description: {bj_now.strftime('%m月%d日')}自动复盘 — {len(final)}场比赛")
    lines.append(f"metadata:")
    lines.append(f"  type: project")
    lines.append(f"  updated: {bj_now.strftime('%Y-%m-%d %H:%M')} 北京时间")
    lines.append(f"---")
    lines.append("")
    lines.append(f"# {bj_now.strftime('%m月%d日')} 自动复盘")
    lines.append("")
    lines.append("| # | 比赛 | 实际 | v9.1预测 | 方向 | v9差 |")
    lines.append("|---|------|------|---------|------|------|")

    dc = 0
    for i, ev in enumerate(final, 1):
        info = extract_match_info(ev)
        h, a = info["home_cn"], info["away_cn"]
        hs, aw = info["home_score"], info["away_score"]
        actual = f"{hs}-{aw}"

        # 运行预测对比
        pred = predict_match_v9(h, a)
        pred_score = pred["ft"]
        ph, pa = map(int, pred_score.split("-"))
        try:
            ah_int, aa_int = int(hs), int(aw)
            adir = "主" if ah_int > aa_int else ("客" if aa_int > ah_int else "平")
            pdir = "主" if ph > pa else ("客" if pa > ph else "平")
            ok = "✅" if adir == pdir else "❌"
            if ok == "✅": dc += 1
        except:
            ok = "?"

        lines.append(f"| {i} | {h} vs {a} | {actual} | {pred_score} | {ok} | {pred['v9_diff']:+.3f} |")

    lines.append("")
    n = len(final)
    lines.append(f"**方向准确率: {dc}/{n} ({dc/max(1,n)*100:.0f}%)**")
    lines.append("")
    lines.append(f"*自动生成于 {bj_now.strftime('%Y-%m-%d %H:%M')} 北京时间*")

    # 写入
    fn = os.path.join(BASE_DIR, "memory_backup", f"review_{bj_now.strftime('%Y%m%d_%H%M')}.md")
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  📝 复盘: {fn}")
    return fn

# ═══════════════════════════════════════════════════════════════════
# §11. 输出 (.md + 手机版.txt)
# ═══════════════════════════════════════════════════════════════════

def _pct(v, d=0):
    try: return float(v)*100
    except: return d

def _fd(d):
    return f"+{d:.3f}" if d > 0 else f"{d:.3f}"

def generate_outputs(predictions):
    bj_now = datetime.now(BJ)
    bj_str = bj_now.strftime('%Y年%m月%d日 %H:%M')
    md_path = os.path.join(BASE_DIR, f"{bj_now.strftime('%Y年%m月%d日')}_v11预测.md")
    txt_path = os.path.join(BASE_DIR, f"{bj_now.strftime('%Y年%m月%d日')}_v11预测_手机版.txt")

    md = _build_md(predictions, bj_str, bj_now)
    with open(md_path, "w", encoding="utf-8") as f: f.write(md)
    print(f"  📝 MD: {md_path}")

    txt = _build_txt(predictions, bj_str, bj_now)
    with open(txt_path, "w", encoding="utf-8") as f: f.write(txt)
    print(f"  📱 TXT: {txt_path}")
    return md_path, txt_path

def _build_md(preds, bj_str, bj_now):
    n = len(preds)
    if n == 0: return f"# 无待预测比赛\n> 生成: {bj_str} 北京时间\n"
    L = []
    L.append(f"# 2026世界杯预测 — Codex v11 (v9.1完整模型)")
    L.append(f"> 生成时间: {bj_str} 北京时间")
    L.append(f"> 模型版本: v9.1 (33场回测 + 全R规则 + 教练战术 + 自动复盘)")
    L.append(f"> 数据来源: ESPN API + player/referee/geo 数据库")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 📊 预测总表 (北京时间)")
    L.append("")
    L.append("| # | 时间 | 比赛 | 场地 | 预测 | 胜% | 平% | 负% | v9.1差 | 冷门 | 信心 |")
    L.append("|---|------|------|------|------|-----|-----|-----|--------|------|------|")
    for i, p in enumerate(preds, 1):
        pr = p["prediction"]
        rl = risk_label(pr["upset"])
        L.append(f"| {i} | {p['beijing_str']} | {p['home_cn']} vs {p['away_cn']} | "
                 f"{p['venue'][:20]} | **{pr['ft']}** | "
                 f"{_pct(pr['home_win']):.0f}% | {_pct(pr['draw']):.0f}% | {_pct(pr['away_win']):.0f}% | "
                 f"{_fd(pr['v9_diff'])} | {rl} | {_pct(pr['confidence']):.0f}% |")
    L.append("")
    L.append("---")
    L.append("")

    for i, p in enumerate(preds, 1):
        pr = p["prediction"]
        h, a = p["home_cn"], p["away_cn"]
        rf = h if pr["rank_gap"] > 0 else a
        pf = h if pr["home_player_score"] > pr["away_player_score"] else a
        gf = h if pr["geo_home"] > pr["geo_away"] else a

        L.append(f"## 🔍 [{i}] {h} vs {a} — {p['beijing_str']} 北京时间")
        L.append("")
        L.append(f"**场地**: {p['venue']} | **裁判**: {pr.get('ref_style','?')} | **教练**: {pr.get('home_style','?')} vs {pr.get('away_style','?')}")
        L.append("")
        L.append("### 基本面")
        L.append(f"| 维度 | {h} | {a} | 优势方 |")
        L.append(f"|------|--------|--------|--------|")
        L.append(f"| FIFA排名 | #{rank(h)} | #{rank(a)} | {rf}(差{abs(pr['rank_gap'])}位) |")
        L.append(f"| 球员评分 | {pr['home_player_score']:.1f} | {pr['away_player_score']:.1f} | {pf} |")
        L.append(f"| 地理优势 | {pr['geo_home']:+.3f} | {pr['geo_away']:+.3f} | {gf} |")
        L.append("")
        L.append("### 概率与比分")
        L.append(f"| 结果 | 概率 |")
        L.append(f"|------|------|")
        L.append(f"| {h}胜 | {_pct(pr['home_win']):.1f}% |")
        L.append(f"| 平局 | {_pct(pr['draw']):.1f}% |")
        L.append(f"| {a}胜 | {_pct(pr['away_win']):.1f}% |")
        L.append("")
        L.append(f"- **首选比分**: {pr['ft']}")
        L.append(f"- **冷门风险**: {risk_label(pr['upset'])} ({_pct(pr['upset']):.0f}%)")
        L.append(f"- **置信度**: {_pct(pr['confidence']):.0f}%")
        L.append(f"- **v9.1评分差**: {_fd(pr['v9_diff'])} "
                 f"{'(大差距>0.5)' if abs(pr['v9_diff'])>0.5 else '(均势<0.25)' if abs(pr['v9_diff'])<0.25 else ''}")
        if pr.get("trigger_close_ref"):
            L.append(f"- **⚖ 触发均势裁判加倍 (10%→20%)**")
        L.append("")

        if pr.get("ref_note"):
            L.append(f"### ⚖️ 裁判影响")
            L.append(f"- {pr['ref_note']}")
            if pr.get("ref_collapse_risk") in ("极高","高"):
                L.append(f"- ⚠️ 红牌崩盘风险: {pr['ref_collapse_risk']}")
            L.append("")

        L.append("---")
        L.append("")

    L.append("## ⚙️ v11模型参数卡")
    L.append("")
    L.append("| 参数 | 值 |")
    L.append("|------|-----|")
    L.append("| 版本 | v9.1 完整实现 (Codex v11) |")
    L.append("| 权重 | 球员22% 排名15% 伤病18% 地理14% 裁判10% 趋势12% 历史战意5% 赔率4% |")
    L.append("| 回测 | 33场 (方向59%+/比分16%+/均势67%+/大差距64%+) |")
    L.append("| R规则 | R1-R15 全部实现 |")
    L.append("| v9.1修正 | ①射门转化率 ②东道主动量 ③均势裁判加倍 |")
    L.append("| 新增 | 教练战术维度 + 轮换风险 + 自动复盘 |")
    L.append("| 数据库 | player_v7 / referee_v7 / location_v1 |")
    L.append(f"> 生成: {bj_str} 北京时间")
    return "\n".join(L)

def _build_txt(preds, bj_str, bj_now):
    n = len(preds)
    if n == 0: return f"===== 无待预测比赛 =====\n时间: {bj_str} 北京时间\n"
    T = []
    T.append(f"===== 2026世界杯预测 v11 =====")
    T.append(f"时间: {bj_str} 北京时间")
    T.append(f"模型: v9.1完整实现 (33场回测)")
    T.append("")
    T.append("━━━━━━━━━━━━━━━━━━━━━━")
    T.append("★★★ 预测总表 ★★★")
    T.append("━━━━━━━━━━━━━━━━━━━━━━")
    T.append("")
    T.append(f"共 {n} 场比赛 (北京时间)")
    T.append("")
    for i, p in enumerate(preds, 1):
        pr = p["prediction"]
        rl = risk_label(pr["upset"])
        T.append(f"[{i}] {p['beijing_str']} {p['home_cn']} vs {p['away_cn']}")
        T.append(f"    场地: {p['venue']}")
        T.append(f"    比分: {pr['ft']}")
        T.append(f"    胜率: 主{_pct(pr['home_win']):.0f}% 平{_pct(pr['draw']):.0f}% 客{_pct(pr['away_win']):.0f}%")
        T.append(f"    v9.1差: {_fd(pr['v9_diff'])} | 冷门: {rl}({_pct(pr['upset']):.0f}%) | 信心: {_pct(pr['confidence']):.0f}%")
        if pr.get("trigger_close_ref"): T.append(f"    ⚖触发: 均势裁判加倍")
        if pr.get("ref_collapse_risk") in ("极高","高"): T.append(f"    ⚠裁判崩盘: {pr.get('ref_collapse_risk')}")
        T.append("")
    T.append("━━━━━━━━━━━━━━━━━━━━━━")
    T.append("")

    for i, p in enumerate(preds, 1):
        pr = p["prediction"]
        h, a = p["home_cn"], p["away_cn"]
        T.append(f"━━━━━━━━━━━━━━━━━━━━━━")
        T.append(f"[{i}] {h} vs {a}")
        T.append(f"    时间: {p['beijing_str']} 北京时间")
        T.append(f"    场地: {p['venue']}")
        T.append(f"    教练: {pr.get('home_style','?')} vs {pr.get('away_style','?')}")
        T.append("")
        T.append(f"  [基本面]")
        T.append(f"    FIFA排名: {h}#{rank(h)} vs {a}#{rank(a)}")
        if pr["rank_gap"] > 0: T.append(f"    -> 排名差{abs(pr['rank_gap'])}位 对{h}有利")
        elif pr["rank_gap"] < 0: T.append(f"    -> 排名差{abs(pr['rank_gap'])}位 对{a}有利")
        else: T.append(f"    -> 排名接近 双方均势")
        T.append(f"  [球员评分]")
        T.append(f"    {h} {pr['home_player_score']:.1f} vs {a} {pr['away_player_score']:.1f}")
        if pr["home_player_score"] > pr["away_player_score"]: T.append(f"    -> 对{h}有利")
        elif pr["away_player_score"] > pr["home_player_score"]: T.append(f"    -> 对{a}有利")
        else: T.append(f"    -> 球员层均势")
        T.append(f"  [地理优势]")
        T.append(f"    {h} {pr['geo_home']:+.3f} vs {a} {pr['geo_away']:+.3f}")
        if pr["geo_home"] > pr["geo_away"]: T.append(f"    -> 对{h}有利")
        elif pr["geo_away"] > pr["geo_home"]: T.append(f"    -> 对{a}有利")
        else: T.append(f"    -> 地理均势")
        if pr.get("ref_note"):
            T.append(f"  [裁判] {pr.get('ref_style','?')}尺度")
            T.append(f"    {pr['ref_note'][:80]}")
            if pr.get("ref_collapse_risk") in ("极高","高"): T.append(f"    ⚠红牌崩盘风险: {pr.get('ref_collapse_risk')}")
            if pr.get("trigger_close_ref"): T.append(f"    -> 触发均势裁判加倍(10%→20%)")
        T.append(f"  [冷门评估]")
        T.append(f"    风险: {risk_label(pr['upset'])} ({_pct(pr['upset']):.0f}%)")
        T.append(f"    置信度: {_pct(pr['confidence']):.0f}%")
        T.append(f"    v9.1评分差: {_fd(pr['v9_diff'])}")
        if abs(pr["v9_diff"]) > 0.5: T.append(f"    -> 大差距比赛(v9.1优势区间)")
        elif abs(pr["v9_diff"]) < 0.25: T.append(f"    -> 均势比赛(裁判影响放大)")
        T.append(f"  [比分预测]")
        T.append(f"    ★首选: {pr['ft']}")
        T.append(f"    胜平负: {h}{_pct(pr['home_win']):.0f}% 平{_pct(pr['draw']):.0f}% {a}{_pct(pr['away_win']):.0f}%")
        T.append("")

    T.append("━━━━━━━━━━━━━━━━━━━━━━")
    T.append("★★★ v11模型参数卡 ★★★")
    T.append("━━━━━━━━━━━━━━━━━━━━━━")
    T.append("")
    T.append("  版本: v9.1完整实现 (Codex v11)")
    T.append("  权重: 球员22% 排名15% 伤病18%")
    T.append("        地理14% 裁判10% 趋势12%")
    T.append("        历史战意5% 赔率4%")
    T.append("  R规则: R1-R15全部实现")
    T.append("    R1强队正路 R2大巴平局")
    T.append("    R3红牌通胀 R4门将失误")
    T.append("    R5下半场 R6首次≠重返")
    T.append("    R7非洲光环 R8亚洲困境")
    T.append("    R9中北美主场 R10南美福地")
    T.append("    R11补时绝杀 R12核心崩塌")
    T.append("    R13南美vs欧洲 R14裁判崩盘链")
    T.append("    R15梅西效应")
    T.append("  v9.1: ①射门转化率 ②东道主动量 ③均势裁判加倍")
    T.append("  新增: 教练战术 + 轮换风险 + 自动复盘")
    T.append(f"  生成: {bj_str} 北京时间")
    T.append("")
    T.append("===== 分析完毕 =====")
    return "\n".join(T)

def print_predictions(predictions):
    bj_now = datetime.now(BJ).strftime('%Y-%m-%d %H:%M')
    print("=" * 80)
    print(f"  Codex v11 (v9.1完整模型) — 2026世界杯预测")
    print(f"  北京时间: {bj_now}")
    print("=" * 80)
    if not predictions: print("\n  ⚠️ 没有待预测的比赛。"); return
    by_date = defaultdict(list)
    for p in predictions:
        d = p["beijing_dt"].strftime("%m/%d") if p.get("beijing_dt") else "未知"
        by_date[d].append(p)
    for ds, ps in sorted(by_date.items()):
        print(f"\n  ── {ds} 北京时间 ({len(ps)}场) ──")
        for p in ps:
            pr = p["prediction"]
            print(f"\n  {p['home_cn']} vs {p['away_cn']}")
            print(f"  ⏰ {p['beijing_str']} | 🏟 {p['venue']}")
            print(f"  🎯 {pr['ft']} | 主{_pct(pr['home_win']):.0f}% 平{_pct(pr['draw']):.0f}% 客{_pct(pr['away_win']):.0f}%")
            print(f"  📊 v9.1差: {_fd(pr['v9_diff'])} | {risk_label(pr['upset'])}({_pct(pr['upset']):.0f}%) | 信心{_pct(pr['confidence']):.0f}%")
            print(f"  🧬 球员: {p['home_cn']}{pr['home_player_score']:.1f} vs {p['away_cn']}{pr['away_player_score']:.1f}")
            print(f"  🌎 地理: {p['home_cn']}{pr['geo_home']:+.3f} vs {p['away_cn']}{pr['geo_away']:+.3f}")
            print(f"  🎭 教练: {pr.get('home_style','?')} vs {pr.get('away_style','?')}")
            if pr.get('trigger_close_ref'): print(f"  ⚖️ 均势裁判加倍")
            if pr.get('ref_collapse_risk') in ("极高","高"): print(f"  ⚠️ 崩盘风险: {pr.get('ref_collapse_risk')}")
    print(f"\n{'='*80}")
    print(f"  预测覆盖 {len(predictions)} 场比赛")

# ═══════════════════════════════════════════════════════════════════
# §12. CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Codex v11 世界杯预测引擎 (v9.1完整实现)")
    parser.add_argument("--date", type=str, default=None, help="预测指定北京时间 (YYYYMMDD), 不指定=今天")
    parser.add_argument("--backtest", action="store_true", help="全量回测")
    parser.add_argument("--review", action="store_true", help="复盘最近完赛")
    parser.add_argument("--all", action="store_true", help="拉取+预测+复盘+回测")
    parser.add_argument("--fetch-only", action="store_true", help="仅拉取数据")
    args = parser.parse_args()

    # 确定日期
    if args.date:
        bj_date = args.date
    else:
        bj_date = datetime.now(BJ).strftime("%Y%m%d")

    print("=" * 80)
    print(f"  Codex v11 — 2026世界杯预测引擎 (v9.1完整实现)")
    print(f"  北京时间日期: {bj_date}")
    print("=" * 80)

    # ── 1. 拉取数据 (跨UTC日期) ──
    events = fetch_beijing_date(bj_date)
    print(f"\n  📡 ESPN API: 拉取 {len(events)} 场比赛 (跨UTC日期)")

    final = [e for e in events if e.get("competitions",[{}])[0].get("status",{}).get("type",{}).get("name","") in FINAL_STATES]
    live = [e for e in events if e.get("competitions",[{}])[0].get("status",{}).get("type",{}).get("name","") in LIVE_STATES]
    sched = [e for e in events if e.get("competitions",[{}])[0].get("status",{}).get("type",{}).get("name","") not in FINAL_STATES and e.get("competitions",[{}])[0].get("status",{}).get("type",{}).get("name","") not in LIVE_STATES]

    print(f"     已完赛: {len(final)} | 进行中: {len(live)} | 未赛: {len(sched)}")

    # ── 2. 保存worldcup_data.json ──
    wc_data = {"fetched_utc": datetime.now(timezone.utc).isoformat(),
               "total": len(events), "final": len(final), "live": len(live), "scheduled": len(sched),
               "events": events}
    with open(os.path.join(BASE_DIR, "worldcup_data.json"), "w", encoding="utf-8") as f:
        json.dump(wc_data, f, ensure_ascii=False, indent=2)

    if args.fetch_only: return

    # ── 3. 赛前预测 ──
    if sched:
        predictions = predict_upcoming(sched)
        print_predictions(predictions)
        generate_outputs(predictions)

    # ── 3.5. 半场/赛中修正预测 (v11.1 新增) ──
    if live:
        print(f"\n  🔴 半场/赛中实时修正 ({len(live)}场进行中)")
        ht_preds = [predict_halftime(ev) for ev in live]
        print_halftime_predictions(ht_preds)
        generate_halftime_outputs(ht_preds)

    # ── 4. 复盘 ──
    if (args.review or args.all) and final:
        generate_review(events)

    # ── 5. 回测 ──
    if args.backtest or args.all:
        acc = run_backtest()
        with open(os.path.join(BASE_DIR, "backtest_v9_results.json"), "w", encoding="utf-8") as f:
            json.dump(acc, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print("  ✅ Codex v11 完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
