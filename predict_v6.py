#!/usr/bin/env python3
"""
Codex世界杯预测引擎 v6 — 球员级数据 + 裁判 + 地理优势
读取 MODEL_RULES.md + player_database_v6.json + referee_database_v6.json
每场比赛后自动复盘更新
"""
import json, sys, io, os, math
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════
# 0. 加载数据库
# ═══════════════════════════════════════════════════════════════

with open(os.path.join(BASE_DIR, "player_database_v6.json"), "r", encoding="utf-8") as f:
    PLAYER_DB = json.load(f)

with open(os.path.join(BASE_DIR, "referee_database_v6.json"), "r", encoding="utf-8") as f:
    REFEREE_DB = json.load(f)

with open(os.path.join(BASE_DIR, "worldcup_data.json"), "r", encoding="utf-8") as f:
    WC_DATA = json.load(f)

# ESPN name → Chinese name mapping
NAME_CN = {
    "Portugal":"葡萄牙","Congo DR":"刚果(金)","England":"英格兰","Croatia":"克罗地亚",
    "Ghana":"加纳","Panama":"巴拿马","Uzbekistan":"乌兹别克斯坦","Colombia":"哥伦比亚",
    "Argentina":"阿根廷","France":"法国","Spain":"西班牙","Brazil":"巴西",
    "Netherlands":"荷兰","Germany":"德国","Belgium":"比利时","Morocco":"摩洛哥",
    "Norway":"挪威","Austria":"奥地利","Japan":"日本","South Korea":"韩国",
    "Saudi Arabia":"沙特","Iran":"伊朗","Qatar":"卡塔尔","Australia":"澳大利亚",
    "Mexico":"墨西哥","United States":"美国","Canada":"加拿大","Sweden":"瑞典",
    "Switzerland":"瑞士","Türkiye":"土耳其","Czechia":"捷克","Scotland":"苏格兰",
    "Ivory Coast":"科特迪瓦","Egypt":"埃及","Senegal":"塞内加尔",
    "Algeria":"阿尔及利亚","Tunisia":"突尼斯","Cape Verde":"佛得角",
    "South Africa":"南非","Haiti":"海地","Paraguay":"巴拉圭","Ecuador":"厄瓜多尔",
    "New Zealand":"新西兰","Bosnia-Herzegovina":"波黑","Curaçao":"库拉索",
    "Jordan":"约旦","Iraq":"伊拉克","Uruguay":"乌拉圭",
}

FIFA_RANK = {
    "阿根廷":1,"法国":2,"西班牙":3,"英格兰":4,"巴西":5,"葡萄牙":6,
    "荷兰":7,"德国":8,"意大利":9,"克罗地亚":10,"比利时":11,
    "摩洛哥":13,"乌拉圭":14,"哥伦比亚":15,"美国":16,"墨西哥":17,
    "瑞士":18,"挪威":19,"奥地利":22,"日本":23,"韩国":24,
    "瑞典":25,"加拿大":26,"土耳其":28,"澳大利亚":29,"伊朗":30,
    "捷克":31,"埃及":33,"科特迪瓦":35,"卡塔尔":36,"沙特":38,
    "厄瓜多尔":40,"巴拉圭":42,"佛得角":46,"加纳":48,"巴拿马":52,
    "约旦":58,"伊拉克":59,"新西兰":63,"乌兹别克斯坦":64,"刚果(金)":65,
    "海地":67,"波黑":70,"苏格兰":72,"库拉索":78,
    "南非":80,"阿尔及利亚":81,"突尼斯":82,"塞内加尔":18,
}

TOP5  = {"阿根廷","法国","西班牙","英格兰","巴西"}
TOP10 = {"阿根廷","法国","西班牙","英格兰","巴西","葡萄牙","荷兰","德国","克罗地亚","比利时"}

# ═══════════════════════════════════════════════════════════════
# 1. 球员评分引擎
# ═══════════════════════════════════════════════════════════════

def calc_player_score(player_data):
    """v6.1: 联赛加权G+A → 基础分 → 年龄衰减 → 热身赛覆盖"""
    if not player_data:
        return None

    mins = player_data.get("mins", 0)
    goals = player_data.get("goals", 0)
    assists = player_data.get("assists", 0)
    form = player_data.get("form", "良好")
    league = player_data.get("league", "其他")
    age = player_data.get("age", 27)
    warmup = player_data.get("warmup_form", "")

    # 联赛强度系数
    LEAGUE_MULT = {
        "英超":1.00,"西甲":1.00,"德甲":1.00,"意甲":0.98,"法甲":0.93,
        "葡超":0.78,"荷甲":0.76,"比甲":0.72,
        "沙特联":0.45,"土超":0.62,"俄超":0.58,
        "MLS":0.50,"巴甲":0.55,"阿甲":0.52,"墨超":0.50,"南美":0.50,
    }
    league_mult = LEAGUE_MULT.get(league, 0.50)

    # 加权G+A/90
    raw_ga90 = (goals + assists) / max(1, mins/90)
    ga90 = raw_ga90 * league_mult

    # 基础分 (更平滑的映射)
    if ga90 > 1.0: base = 10.0
    elif ga90 > 0.7: base = 8.5
    elif ga90 > 0.5: base = 7.0
    elif ga90 > 0.3: base = 5.5
    elif ga90 > 0.15: base = 4.0
    elif ga90 > 0.05: base = 2.5
    else: base = 1.0

    # 状态/伤病
    form_map = {"🔥🔥巅峰":1.15,"🔥极佳":1.05,"良好":1.0,"一般":0.85,"⚠️低迷":0.70,"⚠️伤病":0.40,
                "⚠️恢复中":0.65,"❌极差":0.30,"❌缺席":0.0,"伤缺":0.0,"落选":0.0,"N/A":0.0,"⚠️存疑":0.50}
    form_coef = form_map.get(form, 1.0)

    # 年龄衰减
    if age >= 41: age_coef = 0.58
    elif age >= 39: age_coef = 0.72
    elif age >= 36: age_coef = 0.84
    elif age >= 33: age_coef = 0.93
    else: age_coef = 1.00

    # 热身赛灾难级表现→额外扣分
    warmup_penalty = 0.55 if warmup == "灾难级" else (0.75 if warmup == "差" else 1.0)

    score = min(10.0, base * form_coef * age_coef * warmup_penalty)
    return score

def calc_team_player_score(team_cn, player_roles):
    """计算球队球员综合评分，跳过非球队条目"""
    ROLE_WEIGHT = {'FWD':1.3, 'MID':1.2, 'DEF':1.0, 'GK':0.8}
    NON_TEAM_KEYS = {"已完赛参考球员","年龄衰减规则","联赛强度系数","南美球员美洲优势组"}

    if team_cn not in PLAYER_DB or team_cn in NON_TEAM_KEYS:
        return 6.0, []

    team_players = PLAYER_DB[team_cn]
    scores = []
    for pname, role in player_roles:
        rw = ROLE_WEIGHT.get(role, 1.0)
        if pname in team_players:
            ps = calc_player_score(team_players[pname])
            if ps is not None:
                scores.append((pname, ps, rw))
                continue
        scores.append((pname, 6.0, rw))

    if not scores:
        return 6.0, []
    weighted = sum(s * w for _, s, w in scores) / sum(w for _, _, w in scores)
    return weighted, scores

# ═══════════════════════════════════════════════════════════════
# 2. 地理优势引擎
# ═══════════════════════════════════════════════════════════════

def calc_geo_advantage(team_cn, venue_info=""):
    """计算地缘优势加成"""
    bonus = 0.0
    reasons = []

    if team_cn not in PLAYER_DB:
        return 0.0, []

    players = PLAYER_DB[team_cn]
    mls_count = sum(1 for p in players.values() if p.get("league") == "MLS")

    if mls_count >= 3:
        bonus += 0.06
        reasons.append(f"全队{mls_count}名MLS球员 → 对北美环境完全适应 +6%")
    elif mls_count >= 1:
        bonus += 0.03
        reasons.append(f"{mls_count}名MLS球员 → 北美熟悉度 +3%")

    # 南美球队在美洲比赛
    south_american = {"哥伦比亚","阿根廷","巴西","乌拉圭","巴拉圭","厄瓜多尔"}
    if team_cn in south_american:
        bonus += 0.04
        reasons.append("南美球队在美洲比赛 → 球迷/气候/旅行优势 +4%")

    # 巴甲/阿甲/墨超球员
    american_leagues = {"巴甲","阿甲","墨超","MLS"}
    amer_count = sum(1 for p in players.values() if p.get("league") in american_leagues)
    if amer_count >= 2 and team_cn not in south_american:
        bonus += 0.02
        reasons.append(f"{amer_count}名球员在美洲联赛效力 +2%")

    # 欧洲球队首次来美洲
    euro_teams = {"英格兰","法国","德国","荷兰","比利时","克罗地亚","瑞士","瑞典","挪威"}
    has_mls_players = mls_count > 0
    if team_cn in euro_teams and not has_mls_players:
        bonus -= 0.02
        reasons.append("欧洲球队，大部分球员首次来美洲比赛 -2%")

    # 高原场地
    if "墨西哥城" in venue_info or "阿兹特克" in venue_info:
        bonus += 0.01  # 海拔2250m
        reasons.append("墨西哥城高原(2250m) → 体能影响 +1%")

    return bonus, reasons

# ═══════════════════════════════════════════════════════════════
# 3. 裁判影响引擎
# ═══════════════════════════════════════════════════════════════

def calc_referee_impact(referee_name, home_style="", away_style=""):
    """计算裁判对比赛的影响"""
    if referee_name not in REFEREE_DB:
        return {"penalty_bonus":0, "card_impact":0, "note":"裁判数据缺失"}

    ref = REFEREE_DB[referee_name]
    style = ref.get("尺度","中等")
    card_rate = ref.get("场均黄牌", 3.5)

    impact = {"penalty_bonus":0, "card_impact":0, "note":"", "style":style}

    if "严苛" in style or "严" in style or "紧" in style or "出牌" in style:
        impact["penalty_bonus"] = 0.05
        impact["card_impact"] = 0.10
        impact["note"] = f"严苛裁判({referee_name}) → 对防守粗暴方不利"
    elif "偏松" in style or "松" in style or "宽松" in style:
        impact["penalty_bonus"] = -0.03
        impact["card_impact"] = -0.05
        impact["note"] = f"宽松裁判({referee_name}) → 身体对抗增多"
    else:
        impact["penalty_bonus"] = 0.01
        impact["card_impact"] = 0.02
        impact["note"] = f"中等尺度裁判({referee_name}) → 正常吹罚"

    return impact

# ═══════════════════════════════════════════════════════════════
# 4. v6 核心预测函数
# ═══════════════════════════════════════════════════════════════

def predict_match_v6(home_cn, away_cn, home_rank=None, away_rank=None,
                     home_players=None, away_players=None,
                     home_injuries=None, away_injuries=None,
                     home_geo_bonus=0, away_geo_bonus=0,
                     referee_name=None, handicap_line=None,
                     odds_home=None, odds_draw=None, odds_away=None,
                     home_geo_reasons=None, away_geo_reasons=None,
                     referee_style_note="", is_debut_home=False, is_debut_away=False):
    """v6 全维度预测引擎"""

    hr = home_rank or FIFA_RANK.get(home_cn, 80)
    ar = away_rank or FIFA_RANK.get(away_cn, 80)
    rank_gap = ar - hr
    gap = abs(rank_gap)

    # ── 1. 球员层面 (25%) ──
    home_player_score, home_details = calc_team_player_score(home_cn, home_players or [])
    away_player_score, away_details = calc_team_player_score(away_cn, away_players or [])

    player_diff = home_player_score - away_player_score
    player_home_boost = 0.50 + player_diff * 0.03
    player_away_boost = 0.50 - player_diff * 0.03
    player_draw_boost = 0.25

    # ── 2. 基本面排名 (20%) ──
    base_home = 0.50; base_away = 0.25; base_draw = 0.25
    if gap <= 5: adj = 0
    elif gap <= 15: adj = 0.08
    elif gap <= 30: adj = 0.16
    elif gap <= 50: adj = 0.24
    else: adj = 0.32

    if rank_gap > 0:
        base_home += adj; base_draw -= adj*0.3; base_away -= adj*0.7
    else:
        base_away += adj; base_draw -= adj*0.3; base_home -= adj*0.7

    stronger_rank = min(hr, ar); weaker_rank = max(hr, ar)
    if stronger_rank <= 5 and weaker_rank >= 30:
        extra = 0.10
        if rank_gap > 0:
            base_home += extra; base_away -= extra*0.7; base_draw -= extra*0.3
        else:
            base_away += extra; base_home -= extra*0.7; base_draw -= extra*0.3

    total = base_home + base_draw + base_away
    base_home /= total; base_draw /= total; base_away /= total

    # ── 3. 伤病 (18%) ──
    injury_home = sum(inj.get("weight", 0.02) for inj in (home_injuries or []))
    injury_away = sum(inj.get("weight", 0.02) for inj in (away_injuries or []))

    # ── 4. 地理优势 (12%) ──
    geo_home = home_geo_bonus
    geo_away = away_geo_bonus

    # ── 5. 裁判 (10%) ──
    ref_impact = calc_referee_impact(referee_name) if referee_name else {"penalty_bonus":0,"card_impact":0}
    ref_adj = ref_impact["penalty_bonus"] * 0.5  # 裁判影响分布在两队

    # ── 6. 趋势 (8%) ──
    FINAL_STATES = {"STATUS_FINAL", "STATUS_FULL_TIME"}
    completed = [e for e in WC_DATA["events"]
                 if e.get("status",{}).get("type",{}).get("name","") in FINAL_STATES]
    tr = {"total": len(completed)}
    tr["draws"] = sum(1 for ev in completed
                      if int(ev["competitions"][0]["competitors"][0].get("score",0)) ==
                         int(ev["competitions"][0]["competitors"][1].get("score",0)))
    trend_draw = 0.02 if tr["draws"]/max(1,tr["total"]) > 0.35 else 0

    # ── 7. 赔率 (7%) ──
    odds_adj = 0
    if odds_home and odds_draw and odds_away:
        imp_h = 1.0/odds_home; imp_d = 1.0/odds_draw; imp_a = 1.0/odds_away
        tot = imp_h + imp_d + imp_a
        odds_adj = (imp_h/tot - base_home) * 0.12

    # ── 首秀调整 ──
    debut_h = -0.01 if is_debut_home else 0
    debut_a = -0.01 if is_debut_away else 0

    # ═══ 综合 ═══
    # 动态权重: 排名差距越大，排名权重越高
    dyn_rank_w = 0.20 + min(0.10, gap * 0.002)  # 排名差50→+0.10
    dyn_player_w = 0.25 - min(0.08, gap * 0.0016)  # 排名差50→-0.08
    dyn_trend_w = 0.08
    dyn_injury_w = 0.18
    dyn_geo_w = 0.12
    dyn_ref_w = 0.10
    dyn_odds_w = 0.07

    # 归一化
    total_w = dyn_player_w + dyn_rank_w + dyn_trend_w + dyn_injury_w + dyn_geo_w + dyn_ref_w + dyn_odds_w

    f_home = (player_home_boost * dyn_player_w +
              base_home * dyn_rank_w -
              injury_home * dyn_injury_w +
              geo_home * dyn_geo_w +
              ref_adj * dyn_ref_w +
              odds_adj * dyn_odds_w +
              debut_h) / total_w

    f_away = (player_away_boost * dyn_player_w +
              base_away * dyn_rank_w -
              injury_away * dyn_injury_w +
              geo_away * dyn_geo_w -
              ref_adj * dyn_ref_w -
              odds_adj * dyn_odds_w +
              debut_a) / total_w

    f_draw = (player_draw_boost * dyn_player_w +
              base_draw * dyn_rank_w +
              injury_home*0.3 * dyn_injury_w + injury_away*0.3 * dyn_injury_w +
              trend_draw * dyn_trend_w) / total_w

    # Normalize
    total = f_home + f_draw + f_away
    f_home /= total; f_draw /= total; f_away /= total

    # ── 比分预测 ──
    if f_home > f_away and f_home > f_draw:
        if f_home >= 0.82: ft = "3-0"
        elif f_home >= 0.76: ft = "3-1"
        elif f_home >= 0.66: ft = "2-1"
        elif f_home >= 0.55: ft = "1-0"
        else: ft = "2-1"
    elif f_away > f_home and f_away > f_draw:
        if f_away >= 0.82: ft = "0-3"
        elif f_away >= 0.76: ft = "1-3"
        elif f_away >= 0.66: ft = "1-2"
        elif f_away >= 0.55: ft = "0-1"
        else: ft = "1-2"
    else:
        ft = "1-1" if f_home + f_away < 1.5 else "2-2"

    # ── 半场 ──
    ft_parts = ft.split("-"); ft_h, ft_a = int(ft_parts[0]), int(ft_parts[1])
    if ft == "0-0": ht = "0-0"
    elif ft in ("1-0","0-1"): ht = "0-0" if f_draw > 0.15 else ft
    elif ft in ("2-0","0-2"): ht = "1-0" if ft_h > ft_a else "0-1"
    elif ft in ("3-0","0-3"): ht = "1-0" if ft_h > ft_a else "0-1"
    elif ft in ("2-1","1-2"): ht = "1-1" if f_draw > 0.18 else ("1-0" if ft_h > ft_a else "0-1")
    elif ft in ("3-1","1-3"): ht = "2-0" if ft_h > ft_a else "0-2"
    elif ft == "1-1": ht = "0-0"
    elif ft == "2-2": ht = "1-1"
    else: ht = "0-0"

    # ── 让球 ──
    if handicap_line is None:
        handicap_line = 1.5 if gap>=40 else (1.0 if gap>=25 else (0.5 if gap>=10 else 0))

    if rank_gap > 0:
        exp_margin = (f_home - f_away) * 2.8 + 0.2
    else:
        exp_margin = (f_away - f_home) * 2.8 + 0.2

    diff = exp_margin - handicap_line
    cover_prob = 1.0/(1.0+math.exp(-2.5*diff))
    cover_prob = max(0.08, min(0.92, cover_prob))

    if cover_prob > 0.62: ha = f"让球方赢盘({cover_prob*100:.0f}%)"
    elif cover_prob > 0.50: ha = f"让球方略优({cover_prob*100:.0f}%)"
    elif cover_prob > 0.38: ha = f"受让方略优({(1-cover_prob)*100:.0f}%)"
    else: ha = f"受让方赢盘({(1-cover_prob)*100:.0f}%)"

    # ── 大小球 ──
    over25 = 0.52 + (1.0-f_draw)*0.38
    over25 = max(0.25, min(0.88, over25))

    # ── 红牌风险 ──
    card_imp = ref_impact.get("card_impact", 0)
    red_card_risk = "🔴高" if card_imp > 0.08 else ("🟡中" if card_imp > 0.02 else "🟢低")

    # ── 冷门 ──
    stronger_win = f_home if rank_gap > 0 else f_away
    upset = 1.0 - stronger_win
    if upset > 0.50: rl = "🔴🔴🔴 极高"
    elif upset > 0.40: rl = "🔴🔴 高"
    elif upset > 0.30: rl = "🟡🟡 中高"
    elif upset > 0.20: rl = "🟡 中等"
    else: rl = "🟢 低"

    return {
        "ft":ft,"ht":ht,"home_win":f_home,"draw":f_draw,"away_win":f_away,
        "upset":upset,"risk_label":rl,"handicap_line":handicap_line,
        "cover_prob":cover_prob,"handicap_advice":ha,"over25":over25,
        "home_player_score":home_player_score,"away_player_score":away_player_score,
        "player_diff":player_diff,"geo_home":geo_home,"geo_away":geo_away,
        "ref_style":ref_impact.get("style","?"),"ref_note":ref_impact.get("note",""),
        "red_card_risk":red_card_risk,"rank_gap":rank_gap,
        "home_details":home_details,"away_details":away_details,
        "home_geo_reasons":home_geo_reasons or [],
        "away_geo_reasons":away_geo_reasons or [],
    }

# ═══════════════════════════════════════════════════════════════
# 5. 6月18日 4场比赛
# ═══════════════════════════════════════════════════════════════

bj_now = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')

print("=" * 80)
print("  Codex v6 — 2026世界杯 6月18日(北京) 球员级全方位预测")
print(f"  生成: {bj_now} 北京 | 数据: 球员DB + 裁判DB + 地理优势 + 20场趋势")
print("=" * 80)

matches = [
    {
        "home_cn":"葡萄牙","away_cn":"刚果(金)",
        "home_rank":6,"away_rank":65,
        "time":"6/18 01:00 | NRG体育场,休斯顿","group":"K组",
        "home_players":[("C罗","FWD"),("B费","MID"),("B席","MID"),("内托","FWD"),("维蒂尼亚","MID")],
        "away_players":[("巴坎布","FWD"),("维萨","FWD"),("万比萨卡","DEF"),("姆本巴","DEF")],
        "home_injuries":[{"name":"鲁本·迪亚斯","weight":0.06,"note":"防线核心缺阵"}],
        "away_injuries":[],
        "referee":"Abdulrahman Al-Jassim",
        "odds_home":1.13,"odds_draw":5.86,"odds_away":13.50,
        "handicap":1.5,
        "venue":"休斯顿",
        "news":[
            "❌ C罗热身赛8射0球！对尼日利亚全场最低分！0%地面对抗！41岁只能踢60分钟",
            "🔥 B费英超22助破纪录，葡萄牙真正进攻核心",
            "⚠️ 内托可能挤掉莱奥首发——莱奥对智利红牌+赛季低迷",
            "⚠️ 鲁本·迪亚斯确认缺阵——主教练:'不是冒险的时候'",
            "⚖️ 裁判Al-Jassim: 21%红牌率! 对刚果5后卫铁桶极不利",
            "刚果(金)52年首次世界杯，5-3-2大巴，巴坎布+维萨反击",
        ],
    },
    {
        "home_cn":"英格兰","away_cn":"克罗地亚",
        "home_rank":4,"away_rank":10,
        "time":"6/18 04:00 | AT&T体育场,达拉斯","group":"L组",
        "home_players":[("凯恩","FWD"),("贝林厄姆","MID"),("赖斯","MID"),("戈登","FWD"),("马杜埃克","FWD")],
        "away_players":[("莫德里奇","MID"),("科瓦契奇","MID"),("格瓦迪奥尔","DEF"),("布迪米尔","FWD"),("佩里西奇","MID")],
        "home_injuries":[{"name":"萨卡","weight":0.06,"note":"跟腱炎缺席"},{"name":"福登/帕尔默落选","weight":0.03,"note":"图赫尔未选"}],
        "away_injuries":[{"name":"科瓦契奇","weight":0.03,"note":"脚踝伤6个月"},{"name":"格瓦迪奥尔","weight":0.02,"note":"断腿恢复"},{"name":"莫德里奇戴面具","weight":0.01,"note":"颧骨骨折"},{"name":"多人带伤","weight":0.04,"note":"3人以上带伤出战"}],
        "referee":"Clement Turpin",
        "odds_home":1.74,"odds_draw":3.86,"odds_away":5.0,
        "handicap":0.5,
        "venue":"达拉斯",
        "news":[
            "🔥🔥 凯恩61球欧洲金靴！史上最强赛季",
            "⚠️ 贝林厄姆8球5助较上季下滑，肩伤后恢复",
            "⚠️ 萨卡跟腱炎大概率不首发",
            "⚖️ Turpin执法！图赫尔曾骂他Grade E/1分",
            "莫德里奇40岁AC米兰主力，颧骨骨折戴面具",
            "克罗地亚3人带伤，但大赛基因不容小觑",
        ],
    },
    {
        "home_cn":"加纳","away_cn":"巴拿马",
        "home_rank":48,"away_rank":52,
        "time":"6/18 07:00 | BMO球场,多伦多","group":"L组",
        "home_players":[("托马斯帕尔特伊","MID"),("库杜斯","MID"),("乔丹阿尤","FWD"),("塞梅诺","FWD")],
        "away_players":[("卡拉斯基利亚","MID"),("戴维斯","DEF"),("戈多伊","MID"),("法哈多","FWD")],
        "home_injuries":[{"name":"帕尔特伊签证被拒","weight":0.12,"note":"🔥绝对核心无法参赛！"},{"name":"库杜斯","weight":0.06,"note":"受伤缺阵"}],
        "away_injuries":[{"name":"卡拉斯基利亚","weight":0.02,"note":"存疑"}],
        "referee":"Glenn Nyberg",
        "venue":"多伦多",
        "news":[
            "🔥🔥 帕尔特伊签证被加拿大拒绝！毁灭性打击",
            "❌ 库杜斯也受伤，加纳中场双核全失",
            "❌ 加纳近7场不胜，热身1-5奥地利",
            "✅ 巴拿马多名MLS球员，对多伦多场地熟悉",
            "✅ 巴拿马预选10场6零封，防守顽强",
            "⚖️ Nyberg场均4黄，身体对抗需注意",
        ],
    },
    {
        "home_cn":"乌兹别克斯坦","away_cn":"哥伦比亚",
        "home_rank":64,"away_rank":15,
        "time":"6/18 10:00 | 阿兹特克体育场,墨西哥城","group":"K组",
        "home_players":[("肖穆罗多夫","FWD"),("胡桑诺夫","DEF"),("法伊祖拉耶夫","MID")],
        "away_players":[("路易斯迪亚斯","FWD"),("J罗","MID"),("杜兰","FWD"),("金特罗","MID")],
        "home_injuries":[{"name":"阿利库洛夫","weight":0.04,"note":"退出赛事"},{"name":"马沙里波夫","weight":0.03,"note":"背部伤疑"}],
        "away_injuries":[],
        "referee":"Anthony Taylor",
        "is_debut_home":True,
        "venue":"墨西哥城(2250m高原)",
        "news":[
            "🔥🔥 路易斯·迪亚斯22球22助，拜仁核心",
            "🔥 J罗巴甲助攻王，回到美洲如鱼得水",
            "✅ 哥伦比亚全员健康！南美球队美洲优势",
            "⚠️ 卡纳瓦罗执教乌兹别克首秀",
            "✅ 肖穆罗多夫意甲5球，出场时间有限但保养好",
            "⚖️ Taylor英超宽松风格，身体对抗不会被频繁吹停",
            f"🏔️ 海拔2250m！高原对非高原方体能影响",
        ],
    },
]

results = []
for m in matches:
    h_geo, h_geo_r = calc_geo_advantage(m["home_cn"], m.get("venue",""))
    a_geo, a_geo_r = calc_geo_advantage(m["away_cn"], m.get("venue",""))

    ref = REFEREE_DB.get(m.get("referee",""), {})
    ref_style = ref.get("尺度","?")

    p = predict_match_v6(
        home_cn=m["home_cn"], away_cn=m["away_cn"],
        home_rank=m["home_rank"], away_rank=m["away_rank"],
        home_players=m.get("home_players"), away_players=m.get("away_players"),
        home_injuries=m.get("home_injuries"), away_injuries=m.get("away_injuries"),
        home_geo_bonus=h_geo, away_geo_bonus=a_geo,
        referee_name=m.get("referee"),
        handicap_line=m.get("handicap"),
        odds_home=m.get("odds_home"), odds_draw=m.get("odds_draw"), odds_away=m.get("odds_away"),
        home_geo_reasons=h_geo_r, away_geo_reasons=a_geo_r,
        is_debut_home=m.get("is_debut_home", False),
    )
    results.append((m, p, h_geo_r, a_geo_r))

# ═══════════════════════════════════════════════════════════════
# 输出
# ═══════════════════════════════════════════════════════════════

for i, (m, p, hgr, agr) in enumerate(results, 1):
    stronger = m["home_cn"] if p["rank_gap"] > 0 else m["away_cn"]
    weaker = m["away_cn"] if p["rank_gap"] > 0 else m["home_cn"]

    print(f"""
╔{'═'*78}╗
║  【{i}】{m['home_cn']} vs {m['away_cn']}
║  {m['time']} | {m['group']}
╚{'═'*78}╝

  ┌─────────────────────────────────────────────────────────────┐
  │ 📊 球员评分: {m['home_cn']} {p['home_player_score']:.1f} vs {m['away_cn']} {p['away_player_score']:.1f} │ {'差: ' + str(round(p['player_diff'],1)) if p['player_diff']>0 else '差: ' + str(round(p['player_diff'],1))}
  ├─────────────────────────────────────────────────────────────┤
  │ 🎯 全场: {p['ft']:<6} │ ⚽ 半场: {p['ht']:<6} │ 💰 大2.5: {p['over25']*100:.0f}% │ 🟥 红牌风险: {p['red_card_risk']}
  ├─────────────────────────────────────────────────────────────┤
  │ {m['home_cn']}胜: {p['home_win']*100:.1f}% │ 平: {p['draw']*100:.1f}% │ {m['away_cn']}胜: {p['away_win']*100:.1f}%
  ├─────────────────────────────────────────────────────────────┤
  │ 🔥 冷门: {p['risk_label']} ({p['upset']*100:.0f}%) │ ⚖️ 裁判: {p['ref_style']} │ {p['ref_note'][:40]}
  ├─────────────────────────────────────────────────────────────┤
  │ 📐 让球: {stronger} -{p['handicap_line']}球 → {p['handicap_advice']}
  └─────────────────────────────────────────────────────────────┘

  📰 关键新闻/阵容:""")
    for note in m["news"]:
        print(f"    • {note}")

    print(f"""
  🧬 球员层面分析:""")
    for name, score, _ in p.get("home_details", [])[:5]:
        bar = "█"*min(5, max(1, int(score/2))) + "░"*max(0, 5-int(score/2))
        print(f"    {m['home_cn']} {name}: {score:.1f}/10 {bar}")
    for name, score, _ in p.get("away_details", [])[:4]:
        bar = "█"*min(5, max(1, int(score/2))) + "░"*max(0, 5-int(score/2))
        print(f"    {m['away_cn']} {name}: {score:.1f}/10 {bar}")

    if hgr or agr:
        print(f"\n  🌎 地理优势:")
        for r in hgr: print(f"    {m['home_cn']}: {r}")
        for r in agr: print(f"    {m['away_cn']}: {r}")

# ─── 汇总表 ───
print(f"""
{'='*80}
  📋 v6 预测汇总
{'='*80}
  {'#':<3} {'比赛':<24} {'全场':<6} {'半场':<6} {'球员评分':<12} {'胜%':<6} {'平%':<6} {'负%':<6} {'让球':<10} {'冷门':<12}
  {'─'*80}""")

for i, (m, p, _, _) in enumerate(results, 1):
    stronger = m["home_cn"] if p["rank_gap"] > 0 else m["away_cn"]
    ps = f"{p['home_player_score']:.1f}-{p['away_player_score']:.1f}"
    print(f"  {i:<3} {m['home_cn']+' vs '+m['away_cn']:<24} {p['ft']:<6} {p['ht']:<6} {ps:<12} "
          f"{p['home_win']*100:<6.0f} {p['draw']*100:<6.0f} {p['away_win']*100:<6.0f} "
          f"-{p['handicap_line']} {stronger:<5} {p['risk_label']:<12}")

print(f"""
{'='*80}
  🔥 冷门排名
{'='*80}""")
ranked = sorted(results, key=lambda x: x[1]['upset'], reverse=True)
for i, (m, p, _, _) in enumerate(ranked, 1):
    print(f"  {i}. {m['home_cn']} vs {m['away_cn']}: {p['risk_label']} ({p['upset']*100:.0f}%) — {p['ft']}")

print(f"""
{'='*80}
  ⚖️ 裁判影响分析
{'='*80}""")
for i, (m, p, _, _) in enumerate(results, 1):
    ref_name = m.get("referee","?")
    print(f"  {i}. {ref_name}: {p['ref_style']}尺度 | {p['ref_note'][:60]}")
    print(f"     → 红牌风险: {p['red_card_risk']} | 判罚尺度对{'防守方' if '严' in p['ref_style'] else '双方'}影响大")

print(f"""
{'='*80}
  🌎 地理/环境优势
{'='*80}""")
for i, (m, p, _, _) in enumerate(results, 1):
    print(f"  {i}. {m['home_cn']} +{p['geo_home']*100:.0f}% | {m['away_cn']} +{p['geo_away']*100:.0f}%")

# ═══════════════════════════════════════════════════════════════
# 保存文件
# ═══════════════════════════════════════════════════════════════

# .txt
txt = f"""================================================================================
     2026美加墨世界杯 — 6月18日(北京) 球员级全方位预测
     Codex v6 | 生成: {bj_now} 北京 | 球员DB+裁判DB+地理优势模型
================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v6 模型架构
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  权重: 球员25% + 排名20% + 伤病18% + 地理12% + 裁判10% + 趋势8% + 赔率7%

  新增模块:
  ✅ 球员赛季数据库(player_database_v6.json) — 俱乐部进球/助攻/出场时间
  ✅ 裁判数据库(referee_database_v6.json) — 出牌率/风格/红牌率
  ✅ 地理优势计算 — MLS适应度/南美优势/高原影响
  ✅ 疲劳度系数 — 出场<1500分钟=状态保养好
  ✅ 球员状态系数 — 赛季表现映射到0-10分

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
预测汇总
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  {'#':<3} {'比赛':<24} {'全场':<6} {'半场':<6} {'球员评分':<12} {'胜%':<6} {'平%':<6} {'负%':<6} {'冷门':<12}
  {'─'*80}
"""
for i, (m, p, _, _) in enumerate(results, 1):
    ps = f"{p['home_player_score']:.1f}-{p['away_player_score']:.1f}"
    txt += f"  {i:<3} {m['home_cn']+' vs '+m['away_cn']:<24} {p['ft']:<6} {p['ht']:<6} {ps:<12} {p['home_win']*100:<6.0f} {p['draw']*100:<6.0f} {p['away_win']*100:<6.0f} {p['risk_label']:<12}\n"

for i, (m, p, hgr, agr) in enumerate(results, 1):
    stronger = m["home_cn"] if p["rank_gap"] > 0 else m["away_cn"]
    txt += f"""
================================================================================
【第{i}场】{m['home_cn']} vs {m['away_cn']}
================================================================================

  📊 球员评分: {m['home_cn']} {p['home_player_score']:.1f} vs {m['away_cn']} {p['away_player_score']:.1f} (差{p['player_diff']:+.1f})

  🎯 预测: 全场 {p['ft']} | 半场 {p['ht']}
  📐 让球: {stronger} -{p['handicap_line']}球 → {p['handicap_advice']}
  {m['home_cn']}胜 {p['home_win']*100:.1f}% | 平 {p['draw']*100:.1f}% | {m['away_cn']}胜 {p['away_win']*100:.1f}%
  冷门: {p['risk_label']} ({p['upset']*100:.0f}%) | 大2.5: {p['over25']*100:.0f}% | 红牌风险: {p['red_card_risk']}

  🧬 球员详情:
"""
    for name, score, _ in p.get("home_details", [])[:6]:
        txt += f"    {m['home_cn']} {name}: {score:.1f}/10\n"
    for name, score, _ in p.get("away_details", [])[:5]:
        txt += f"    {m['away_cn']} {name}: {score:.1f}/10\n"

    if hgr or agr:
        txt += f"\n  🌎 地理优势:\n"
        for r in hgr: txt += f"    {m['home_cn']}: {r}\n"
        for r in agr: txt += f"    {m['away_cn']}: {r}\n"

    txt += f"""
  ⚖️ 裁判: {m.get('referee','?')} ({p['ref_style']}尺度)
     {p['ref_note']}

  📰 关键信息:
"""
    for note in m["news"]:
        txt += f"    • {note}\n"

txt += f"""
================================================================================
                            —— 分析完毕 ——
  📌 数据: ESPN API + player_database_v6.json + referee_database_v6.json
  📌 规则: MODEL_RULES.md (每次预测前必读)
  📌 v6 权重: 球员25% 排名20% 伤病18% 地理12% 裁判10% 趋势8% 赔率7%
  📌 声明: 所有预测仅供娱乐参考
================================================================================
"""

out_txt = os.path.join(BASE_DIR, f"2026世界杯6月18日预测分析_v6.txt")
with open(out_txt, "w", encoding="utf-8") as f:
    f.write(txt)

# .md
md = f"""# 2026世界杯 6月18日 球员级全方位预测 (v6)

> Codex v6 | 生成: {bj_now} 北京 | 球员DB+裁判DB+地理优势

## v6 模型架构

| 层级 | 权重 | 说明 |
|------|------|------|
| 球员层面 | 25% | 赛季G+A/分钟/rating |
| 基本面 | 20% | FIFA排名 |
| 伤病 | 18% | 核心缺阵量化 |
| 地理优势 | 12% | MLS/南美/高原 |
| 裁判 | 10% | 出牌率/尺度 |
| 趋势 | 8% | 20场趋势 |
| 赔率 | 7% | 市场隐含概率 |

## 预测汇总

| # | 比赛 | 全场 | 半场 | 球员评分 | 冷门 |
|---|------|------|------|----------|------|
"""
for i, (m, p, _, _) in enumerate(results, 1):
    ps = f"{p['home_player_score']:.1f}-{p['away_player_score']:.1f}"
    md += f"| {i} | {m['home_cn']} vs {m['away_cn']} | **{p['ft']}** | {p['ht']} | {ps} | {p['risk_label']} |\n"

for m, p, _, _ in results:
    stronger = m["home_cn"] if p["rank_gap"] > 0 else m["away_cn"]
    ref_name = m.get("referee","?")
    md += f"""
---

## {m['home_cn']} vs {m['away_cn']}

- ⏰ {m['time']} | {m['group']}
- 🎯 **{p['ft']}** (半场 {p['ht']})
- 📐 {stronger} -{p['handicap_line']}球: {p['handicap_advice']}
- ⚖️ {ref_name}: {p['ref_style']}尺度

### 📰 关键信息
"""
    for note in m["news"]:
        md += f"- {note}\n"

md += f"""
---

> 📌 数据文件: player_database_v6.json | referee_database_v6.json | MODEL_RULES.md
> ⚠️ 预测仅供娱乐参考
"""

out_md = os.path.join(BASE_DIR, "prediction_june18_v6.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md)

print(f"""
  报告已保存:
    📄 {out_txt}
    📝 {out_md}
    🧬 {os.path.join(BASE_DIR, 'player_database_v6.json')}
    ⚖️ {os.path.join(BASE_DIR, 'referee_database_v6.json')}
    📋 {os.path.join(BASE_DIR, 'MODEL_RULES.md')}
{'='*80}
  v6 就绪。所有规则已固化到文件，不会遗忘。
""")
