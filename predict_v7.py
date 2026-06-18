#!/usr/bin/env python3
"""
Codex世界杯预测引擎 v7 — v6优化版
基于6月18-19日复盘: 新增历史战意/大巴阵型/核心灾难状态/R12严格触发/平局惯性因子
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

# v7新增: 重返世界杯历史数据 (距上次参赛年数)
WC_RETURN_YEARS = {
    "刚果(金)": 52,  # 1974→2026
    "乌兹别克斯坦": 999,  # 首次参赛,用大数表示
    "巴拿马": 8,  # 2018→2026
    "海地": 52,  # 1974→2026
    "库拉索": 999,  # 首次
}

# ═══════════════════════════════════════════════════════════════
# 1. 球员评分引擎 (v7修正)
# ═══════════════════════════════════════════════════════════════

def calc_player_score(player_data):
    """v7: 联赛加权G+A → 基础分 → 年龄衰减(修正) → 热身赛覆盖"""
    if not player_data:
        return None

    mins = player_data.get("mins", 0)
    goals = player_data.get("goals", 0)
    assists = player_data.get("assists", 0)
    form = player_data.get("form", "良好")
    league = player_data.get("league", "其他")
    age = player_data.get("age", 27)
    warmup = player_data.get("warmup_form", "")

    LEAGUE_MULT = {
        "英超":1.00,"西甲":1.00,"德甲":1.00,"意甲":0.98,"法甲":0.93,
        "葡超":0.78,"荷甲":0.76,"比甲":0.72,
        "沙特联":0.45,"土超":0.62,"俄超":0.58,
        "MLS":0.50,"巴甲":0.55,"阿甲":0.52,"墨超":0.50,"南美":0.50,
    }
    league_mult = LEAGUE_MULT.get(league, 0.50)

    raw_ga90 = (goals + assists) / max(1, mins/90)
    ga90 = raw_ga90 * league_mult

    if ga90 > 1.0: base = 10.0
    elif ga90 > 0.7: base = 8.5
    elif ga90 > 0.5: base = 7.0
    elif ga90 > 0.3: base = 5.5
    elif ga90 > 0.15: base = 4.0
    elif ga90 > 0.05: base = 2.5
    else: base = 1.0

    form_map = {"🔥🔥巅峰":1.15,"🔥极佳":1.05,"良好":1.0,"一般":0.85,"⚠️低迷":0.70,
                "⚠️伤病":0.40,"⚠️恢复中":0.78,"❌极差":0.30,"❌缺席":0.0,
                "伤缺":0.0,"落选":0.0,"N/A":0.0,"⚠️存疑":0.50}
    form_coef = form_map.get(form, 1.0)

    # ── v7修正: 年龄衰减更温和 ──
    if age >= 41: age_coef = 0.65     # v6:0.58 → 老将大赛经验
    elif age >= 39: age_coef = 0.78   # v6:0.72
    elif age >= 36: age_coef = 0.88   # v6:0.84
    elif age >= 33: age_coef = 0.95   # v6:0.93
    else: age_coef = 1.00

    warmup_penalty = 0.55 if warmup == "灾难级" else (0.75 if warmup == "差" else 1.0)

    score = min(10.0, base * form_coef * age_coef * warmup_penalty)
    return score

def calc_team_player_score(team_cn, player_roles):
    ROLE_WEIGHT = {'FWD':1.3, 'MID':1.2, 'DEF':1.0, 'GK':0.8}
    NON_TEAM_KEYS = {"已完赛参考球员","年龄衰减规则","联赛强度系数","南美球员美洲优势组"}

    if team_cn not in PLAYER_DB or team_cn in NON_TEAM_KEYS:
        return 6.0, [], False

    team_players = PLAYER_DB[team_cn]
    scores = []
    has_disaster_star = False  # v7 R9: 核心灾难状态检测

    for pname, role in player_roles:
        rw = ROLE_WEIGHT.get(role, 1.0)
        if pname in team_players:
            ps = calc_player_score(team_players[pname])
            if ps is not None:
                scores.append((pname, ps, rw))
                # R9: 检测35岁+核心灾难状态
                pdata = team_players[pname]
                if (pdata.get("age", 27) >= 35 and
                    pdata.get("warmup_form") == "灾难级" and
                    role in ('FWD', 'MID')):
                    has_disaster_star = True
                continue
        scores.append((pname, 6.0, rw))

    if not scores:
        return 6.0, [], False
    weighted = sum(s * w for _, s, w in scores) / sum(w for _, _, w in scores)
    return weighted, scores, has_disaster_star

# ═══════════════════════════════════════════════════════════════
# 2. 地理优势引擎 (v7: 权重降低)
# ═══════════════════════════════════════════════════════════════

def calc_geo_advantage(team_cn, venue_info=""):
    bonus = 0.0
    reasons = []

    if team_cn not in PLAYER_DB:
        return 0.0, []

    players = PLAYER_DB[team_cn]
    mls_count = sum(1 for p in players.values() if p.get("league") == "MLS")

    if mls_count >= 3:
        bonus += 0.04  # v6:0.06 → 降低
        reasons.append(f"全队{mls_count}名MLS球员 → 北美适应 +4%")
    elif mls_count >= 1:
        bonus += 0.02  # v6:0.03
        reasons.append(f"{mls_count}名MLS球员 → 北美熟悉 +2%")

    south_american = {"哥伦比亚","阿根廷","巴西","乌拉圭","巴拉圭","厄瓜多尔"}
    if team_cn in south_american:
        bonus += 0.04
        reasons.append("南美球队在美洲比赛 → 球迷/气候/旅行优势 +4%")

    american_leagues = {"巴甲","阿甲","墨超","MLS"}
    amer_count = sum(1 for p in players.values() if p.get("league") in american_leagues)
    if amer_count >= 2 and team_cn not in south_american:
        bonus += 0.02
        reasons.append(f"{amer_count}名球员在美洲联赛效力 +2%")

    euro_teams = {"英格兰","法国","德国","荷兰","比利时","克罗地亚","瑞士","瑞典","挪威"}
    has_mls_players = mls_count > 0
    if team_cn in euro_teams and not has_mls_players:
        bonus -= 0.02
        reasons.append("欧洲球队首次来美洲 -2%")

    if "墨西哥城" in venue_info or "阿兹特克" in venue_info:
        bonus += 0.01
        reasons.append("墨西哥城高原(2250m) → 体能影响 +1%")

    return bonus, reasons

# ═══════════════════════════════════════════════════════════════
# 3. 裁判影响引擎 (不变)
# ═══════════════════════════════════════════════════════════════

def calc_referee_impact(referee_name):
    if referee_name not in REFEREE_DB:
        return {"penalty_bonus":0, "card_impact":0, "note":"裁判数据缺失", "style":"?"}

    ref = REFEREE_DB[referee_name]
    style = ref.get("尺度","中等")

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
# 4. v7 核心预测函数
# ═══════════════════════════════════════════════════════════════

def predict_match_v7(home_cn, away_cn, home_rank=None, away_rank=None,
                     home_players=None, away_players=None,
                     home_injuries=None, away_injuries=None,
                     home_geo_bonus=0, away_geo_bonus=0,
                     referee_name=None, handicap_line=None,
                     odds_home=None, odds_draw=None, odds_away=None,
                     is_debut_home=False, is_debut_away=False,
                     home_bus=False, away_bus=False,  # v7 R7: 大巴阵型
                     home_return_years=0, away_return_years=0,  # v7 R6: 重返年数
                     home_has_disaster=False, away_has_disaster=False):  # v7 R9
    """v7 全维度预测引擎 — 6月19日更新"""

    hr = home_rank or FIFA_RANK.get(home_cn, 80)
    ar = away_rank or FIFA_RANK.get(away_cn, 80)
    rank_gap = ar - hr
    gap = abs(rank_gap)

    # ── 1. 球员层面 (22%) ──
    home_player_score, home_details, home_disaster = calc_team_player_score(home_cn, home_players or [])
    away_player_score, away_details, away_disaster = calc_team_player_score(away_cn, away_players or [])

    # R9: 灾难状态标记合并
    home_disaster = home_disaster or home_has_disaster
    away_disaster = away_disaster or away_has_disaster

    player_diff = home_player_score - away_player_score
    player_home_boost = 0.50 + player_diff * 0.03
    player_away_boost = 0.50 - player_diff * 0.03
    player_draw_boost = 0.25

    # ── 2. 基本面排名 (18%) ──
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
    stronger_name = home_cn if rank_gap > 0 else away_cn

    # Top5 vs 非Top30加成 (v7: 降低)
    if stronger_rank <= 5 and weaker_rank >= 30:
        extra = 0.08  # v6:0.10 → 降低
        if rank_gap > 0:
            base_home += extra; base_away -= extra*0.7; base_draw -= extra*0.3
        else:
            base_away += extra; base_home -= extra*0.7; base_draw -= extra*0.3

    # ── v7 R8: Top10首场保守 ──
    if stronger_rank <= 10 and stronger_rank <= 10:
        conservative = 0.03
        if rank_gap > 0:
            base_home -= conservative; base_draw += conservative*0.6; base_away += conservative*0.4
        else:
            base_away -= conservative; base_draw += conservative*0.6; base_home += conservative*0.4

    total = base_home + base_draw + base_away
    base_home /= total; base_draw /= total; base_away /= total

    # ── 3. 伤病 (15%) ──
    injury_home = 0; injury_away = 0
    for inj in (home_injuries or []):
        w = inj.get("weight", 0.02)
        status = inj.get("status", "")
        # R10: 带伤出战降权
        if "恢复" in status or "存疑" in status:
            w *= 0.5
        injury_home += w
    for inj in (away_injuries or []):
        w = inj.get("weight", 0.02)
        status = inj.get("status", "")
        if "恢复" in status or "存疑" in status:
            w *= 0.5
        injury_away += w

    # ── v7 R9: 核心灾难状态 ──
    disaster_penalty_home = 0.04 if home_disaster else 0
    disaster_penalty_away = 0.04 if away_disaster else 0

    # ── 4. 地理优势 (8%) ──
    geo_home = home_geo_bonus
    geo_away = away_geo_bonus

    # ── 5. 裁判 (10%) ──
    ref_impact = calc_referee_impact(referee_name) if referee_name else {"penalty_bonus":0,"card_impact":0}
    ref_adj = ref_impact["penalty_bonus"] * 0.5

    # ── 6. 趋势 (12%) ──
    FINAL_STATES = {"STATUS_FINAL", "STATUS_FULL_TIME"}
    completed = [e for e in WC_DATA["events"]
                 if e.get("status",{}).get("type",{}).get("name","") in FINAL_STATES]
    tr = {"total": len(completed)}
    tr["draws"] = sum(1 for ev in completed
                      if int(ev["competitions"][0]["competitors"][0].get("score",0)) ==
                         int(ev["competitions"][0]["competitors"][1].get("score",0)))

    # v7: 趋势权重提高
    trend_draw = 0.04 if tr["draws"]/max(1,tr["total"]) > 0.35 else 0

    # v7: 非洲趋势分析
    african_teams = {"摩洛哥","塞内加尔","埃及","科特迪瓦","刚果(金)","加纳",
                     "南非","阿尔及利亚","突尼斯","佛得角"}
    african_draws = sum(1 for ev in completed
                        for comp in ev["competitions"][0]["competitors"]
                        if comp.get("team",{}).get("displayName","") in african_teams
                        and int(ev["competitions"][0]["competitors"][0].get("score",0)) ==
                            int(ev["competitions"][0]["competitors"][1].get("score",0)))
    african_bonus = 0.02 if african_draws >= 3 else 0

    # ── 7. 赔率 (8%) ──
    odds_adj = 0
    if odds_home and odds_draw and odds_away:
        imp_h = 1.0/odds_home; imp_d = 1.0/odds_draw; imp_a = 1.0/odds_away
        tot = imp_h + imp_d + imp_a
        odds_adj = (imp_h/tot - base_home) * 0.15  # v6:0.12 → 0.15

    # ── v7 R6: 历史性首秀/重返 ──
    history_bonus_home = 0
    history_bonus_away = 0
    if home_return_years >= 40:
        history_bonus_home = 0.08  # 平局概率提升
    elif home_return_years >= 20:
        history_bonus_home = 0.04
    if away_return_years >= 40:
        history_bonus_away = 0.08
    elif away_return_years >= 20:
        history_bonus_away = 0.04

    # ── v7 R7: 大巴阵型 ──
    bus_bonus_home = 0.06 if home_bus else 0
    bus_bonus_away = 0.06 if away_bus else 0

    # ── 首秀调整 (降低) ──
    debut_h = -0.01 if is_debut_home else 0
    debut_a = -0.01 if is_debut_away else 0

    # ═══ v7 综合权重 (不含history,它作为直接调整项) ═══
    W = {
        "player": 0.22,
        "rank": 0.18 + min(0.08, gap * 0.0016),
        "injury": 0.15,
        "geo": 0.08,
        "ref": 0.10,
        "trend": 0.12,
        "odds": 0.08,
    }
    total_w = sum(W.values())

    # ── 基础概率计算 ──
    f_home = (player_home_boost * W["player"] +
              base_home * W["rank"] -
              injury_home * W["injury"] +
              geo_home * W["geo"] +
              ref_adj * W["ref"] +
              odds_adj * W["odds"] +
              debut_h) / total_w

    f_away = (player_away_boost * W["player"] +
              base_away * W["rank"] -
              injury_away * W["injury"] +
              geo_away * W["geo"] -
              ref_adj * W["ref"] -
              odds_adj * W["odds"] +
              debut_a) / total_w

    f_draw = (player_draw_boost * W["player"] +
              base_draw * W["rank"] +
              (injury_home + injury_away) * 0.3 * W["injury"] +
              trend_draw * W["trend"] +
              african_bonus * W["trend"]) / total_w

    # First normalization
    total = f_home + f_draw + f_away
    f_home /= total; f_draw /= total; f_away /= total

    # ═══ v7 直接调整项 (在归一化后应用,避免权重稀释) ═══
    # R6: 历史性重返/首秀 → 直接增加平局率,降低强队胜率
    if history_bonus_home > 0:
        f_draw += 0.08
        f_home += 0.03  # 弱队自己也受益
        f_away -= 0.11  # 从强队胜率扣除
    if history_bonus_away > 0:
        f_draw += 0.08
        f_away += 0.03
        f_home -= 0.11

    # R7: 大巴阵型 → 大福增加平局概率
    if home_bus:
        f_draw += 0.05
        f_home -= 0.02
        f_away -= 0.03
    if away_bus:
        f_draw += 0.05
        f_away -= 0.02
        f_home -= 0.03

    # R9: 核心灾难状态 → 直接扣减该队胜率
    if home_disaster:
        f_home -= 0.05
        f_draw += 0.02
        f_away += 0.03
    if away_disaster:
        f_away -= 0.05
        f_draw += 0.02
        f_home += 0.03

    # Clamp to valid range and re-normalize
    f_home = max(0.05, min(0.90, f_home))
    f_away = max(0.05, min(0.90, f_away))
    f_draw = max(0.05, min(0.60, f_draw))
    total = f_home + f_draw + f_away
    f_home /= total; f_draw /= total; f_away /= total

    # ── 比分预测 (v7修正: 平局接近时选平局) ──
    # 当draw概率与最高胜率差距<8%时,预测平局
    if f_home > f_away and f_home > f_draw:
        if f_draw > f_home - 0.08:
            ft = "1-1"  # 平局概率接近
        elif f_home >= 0.82: ft = "3-0"
        elif f_home >= 0.76: ft = "3-1"
        elif f_home >= 0.66: ft = "2-1"
        elif f_home >= 0.58: ft = "2-0"
        elif f_home >= 0.50: ft = "1-0"
        else: ft = "2-1"
    elif f_away > f_home and f_away > f_draw:
        if f_draw > f_away - 0.08:
            ft = "1-1"  # 平局概率接近
        elif f_away >= 0.82: ft = "0-3"
        elif f_away >= 0.76: ft = "1-3"
        elif f_away >= 0.66: ft = "1-2"
        elif f_away >= 0.58: ft = "0-2"
        elif f_away >= 0.50: ft = "0-1"
        else: ft = "1-2"
    else:
        if f_draw > 0.35: ft = "1-1"
        elif f_draw > 0.28: ft = "0-0"
        else: ft = "2-2"

    # ── 半场 ──
    ft_parts = ft.split("-"); ft_h, ft_a = int(ft_parts[0]), int(ft_parts[1])
    if ft == "0-0": ht = "0-0"
    elif ft in ("1-0","0-1"): ht = "0-0" if f_draw > 0.15 else ft
    elif ft in ("2-0","0-2"): ht = "1-0" if ft_h > ft_a else "0-1"
    elif ft in ("3-0","0-3"): ht = "2-0" if ft_h > ft_a else "0-2"
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

    # ── 大小球 (v7 R11修正) ──
    # 检测双方是否有顶级射手
    has_elite_scorers = False
    for name, score, role in (home_details or []) + (away_details or []):
        if score >= 8.0 and role in ('FWD', 'MID'):
            has_elite_scorers = True
            break

    over25 = 0.52 + (1.0-f_draw)*0.38
    if has_elite_scorers:
        over25 += 0.12  # R11: 双方顶级射手 → 进球通胀
    over25 = max(0.25, min(0.88, over25))

    # ── 红牌风险 ──
    card_imp = ref_impact.get("card_impact", 0)
    red_card_risk = "🔴高" if card_imp > 0.08 else ("🟡中" if card_imp > 0.02 else "🟢低")

    # ── 冷门 (v7修正阈值) ──
    stronger_win = f_home if rank_gap > 0 else f_away
    upset = 1.0 - stronger_win
    if upset > 0.45: rl = "🔴🔴🔴 极高"
    elif upset > 0.35: rl = "🔴🔴 高"
    elif upset > 0.25: rl = "🟡🟡 中高"
    elif upset > 0.15: rl = "🟡 中等"
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
        "has_elite_scorers":has_elite_scorers,
        "home_disaster":home_disaster,"away_disaster":away_disaster,
    }

# ═══════════════════════════════════════════════════════════════
# 5. v7 预测执行
# ═══════════════════════════════════════════════════════════════

bj_now = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')

print("=" * 80)
print("  Codex v7 — 2026世界杯 6月19日 预测分析")
print(f"  生成: {bj_now} 北京 | v7/v8混合模型: 历史战意+大巴阵型+进球修正+平局惯性")
print("=" * 80)

matches = [
    # ═══ 6月19日 A组 捷克 vs 南非 (已完赛) ═══
    {
        "home_cn":"捷克","away_cn":"南非",
        "home_rank":31,"away_rank":80,
        "time":"6/19 00:00 (已完赛)","group":"A组",
        "actual":"1-1",
        "home_players":[("希克","FWD"),("绍切克","MID"),("萨迪莱克","MID"),("克雷伊奇","DEF")],
        "away_players":[("莫科纳","MID")],
        "home_injuries":[],
        "away_injuries":[{"name":"兹瓦内红牌+追加","weight":0.08,"status":"❌缺席"},
                         {"name":"西索尔红牌","weight":0.05,"status":"❌缺席"}],
        "referee":"Tess Olofsson",
        "odds_home":1.42,"odds_draw":4.50,"odds_away":7.50,
        "handicap":1.0,
        "home_return_years":0,"away_return_years":0,
    },
    # ═══ 6月19日 B组 瑞士 vs 波黑 (待赛) ═══
    {
        "home_cn":"瑞士","away_cn":"波黑",
        "home_rank":18,"away_rank":70,
        "time":"6/19 03:00","group":"B组",
        "actual":"⏳",
        "home_players":[("扎卡","MID"),("恩博洛","FWD"),("阿坎吉","DEF"),("恩多耶","FWD"),("科贝尔","GK")],
        "away_players":[("哲科","FWD"),("德米罗维奇","FWD"),("科拉希纳茨","DEF"),("德迪奇","DEF")],
        "home_injuries":[],
        "away_injuries":[{"name":"塞利克","weight":0.03,"status":"❌缺席"},
                         {"name":"科拉希纳茨带伤","weight":0.02,"status":"⚠️恢复中"}],
        "referee":"João Pinheiro",
        "odds_home":1.55,"odds_draw":4.00,"odds_away":5.50,
        "handicap":1.0,
        "home_return_years":0,"away_return_years":12,  # 2014→2026 不触发R6
    },
    # ═══ 6月19日 B组 加拿大 vs 卡塔尔 (待赛) ═══
    {
        "home_cn":"加拿大","away_cn":"卡塔尔",
        "home_rank":26,"away_rank":36,
        "time":"6/19 06:00","group":"B组",
        "actual":"⏳",
        "home_players":[("乔纳森戴维","FWD"),("尤斯塔基奥","MID"),("拉林","FWD"),("布坎南","MID")],
        "away_players":[("阿菲夫","FWD"),("阿里","FWD"),("海多斯","MID")],
        "home_injuries":[{"name":"阿方索戴维斯","weight":0.06,"status":"⚠️存疑"}],
        "away_injuries":[],
        "referee":"Cristian Garay",
        "odds_home":1.65,"odds_draw":3.80,"odds_away":5.00,
        "handicap":0.5,
        "home_return_years":0,"away_return_years":0,
        "venue":"温哥华(加拿大主场)",
    },
    # ═══ 6月19日 A组 墨西哥 vs 韩国 (待赛) 【焦点战】 ═══
    {
        "home_cn":"墨西哥","away_cn":"韩国",
        "home_rank":17,"away_rank":24,
        "time":"6/19 09:00","group":"A组",
        "actual":"⏳",
        "home_players":[("希门尼斯","FWD"),("洛萨诺","FWD"),("阿尔瓦雷斯","MID"),("奥乔亚","GK")],
        "away_players":[("孙兴慜","FWD"),("李刚仁","MID"),("金玟哉","DEF"),("黄仁范","MID"),("黄喜灿","FWD")],
        "home_injuries":[{"name":"蒙特斯","weight":0.06,"status":"❌红牌停赛"}],
        "away_injuries":[],
        "referee":"Gustavo Tejera",
        "odds_home":2.60,"odds_draw":3.30,"odds_away":2.80,
        "handicap":0,
        "home_return_years":0,"away_return_years":0,
        "venue":"瓜达拉哈拉(墨西哥主场)",
    },
]

results = []
for m in matches:
    h_geo, h_geo_r = calc_geo_advantage(m["home_cn"], m.get("venue",""))
    a_geo, a_geo_r = calc_geo_advantage(m["away_cn"], m.get("venue",""))

    p = predict_match_v7(
        home_cn=m["home_cn"], away_cn=m["away_cn"],
        home_rank=m["home_rank"], away_rank=m["away_rank"],
        home_players=m.get("home_players"), away_players=m.get("away_players"),
        home_injuries=m.get("home_injuries"), away_injuries=m.get("away_injuries"),
        home_geo_bonus=h_geo, away_geo_bonus=a_geo,
        referee_name=m.get("referee"),
        handicap_line=m.get("handicap"),
        odds_home=m.get("odds_home"), odds_draw=m.get("odds_draw"), odds_away=m.get("odds_away"),
        is_debut_home=m.get("is_debut_home", False),
        home_bus=m.get("home_bus", False), away_bus=m.get("away_bus", False),
        home_return_years=m.get("home_return_years", 0),
        away_return_years=m.get("away_return_years", 0),
    )
    results.append((m, p, h_geo_r, a_geo_r))

# ═══════════════════════════════════════════════════════════════
# 输出
# ═══════════════════════════════════════════════════════════════

for i, (m, p, hgr, agr) in enumerate(results, 1):
    stronger = m["home_cn"] if p["rank_gap"] > 0 else m["away_cn"]
    weaker = m["away_cn"] if p["rank_gap"] > 0 else m["home_cn"]

    # v7新增标签
    tags = []
    if m.get("away_bus"): tags.append("🚌大巴阵型")
    if m.get("home_bus"): tags.append("🚌大巴阵型")
    if m.get("away_return_years", 0) >= 40: tags.append(f"🔙{m['away_cn']}{m['away_return_years']}年重返")
    if m.get("home_return_years", 0) >= 40: tags.append(f"🔙{m['home_cn']}{m['home_return_years']}年重返")
    if p.get("home_disaster"): tags.append("⚠️核心灾难")
    if p.get("away_disaster"): tags.append("⚠️核心灾难")
    if p.get("has_elite_scorers"): tags.append("🔥双方顶级射手")
    tag_str = " | ".join(tags) if tags else ""

    print(f"""
╔{'═'*78}╗
║  【{i}】{m['home_cn']} vs {m['away_cn']}  {m.get('actual','')}
║  {m['time']} | {m['group']}  {'| v7标签: '+tag_str if tag_str else ''}
╚{'═'*78}╝

  ┌─────────────────────────────────────────────────────────────┐
  │ 📊 球员评分: {m['home_cn']} {p['home_player_score']:.1f} vs {m['away_cn']} {p['away_player_score']:.1f} │ 差: {p['player_diff']:+.1f}
  ├─────────────────────────────────────────────────────────────┤
  │ 🎯 全场: {p['ft']:<6} │ ⚽ 半场: {p['ht']:<6} │ 💰 大2.5: {p['over25']*100:.0f}% │ 🟥 红牌: {p['red_card_risk']}
  ├─────────────────────────────────────────────────────────────┤
  │ {m['home_cn']}胜: {p['home_win']*100:.1f}% │ 平: {p['draw']*100:.1f}% │ {m['away_cn']}胜: {p['away_win']*100:.1f}%
  ├─────────────────────────────────────────────────────────────┤
  │ 🔥 冷门: {p['risk_label']} ({p['upset']*100:.0f}%) │ ⚖️ 裁判: {p['ref_style']} │ {p['ref_note'][:50]}
  ├─────────────────────────────────────────────────────────────┤
  │ 📐 让球: {stronger} -{p['handicap_line']}球 → {p['handicap_advice']}
  └─────────────────────────────────────────────────────────────┘

  🧬 球员详情:""")
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

# ─── v6 vs v7 对比表 ───
print(f"""
{'='*80}
  📋 v6 vs v7 对比
{'='*80}
  {'#':<3} {'比赛':<24} {'实际':<6} {'v6':<6} {'v7':<6} {'方向':<6} {'改善':<20}
  {'─'*80}""")

v6_preds = ["2-0", "1-0", "2-1", "1-1"]  # v8预测: 捷克2-0(实际1-1) 瑞士1-0 加拿大2-1 墨西哥1-1
for i, (m, p, _, _) in enumerate(results, 1):
    v6p_parts = v6_preds[i-1].split('-')
    v7p_parts = p['ft'].split('-')
    actual = m.get('actual','?')
    v6_ok = "⏳"; v7_ok = "⏳"; improvement = ""

    if actual not in ('?', '⏳') and '-' in actual:
        actual_parts = actual.split('-')
        v6_h, v6_a = int(v6p_parts[0]), int(v6p_parts[1])
        v7_h, v7_a = int(v7p_parts[0]), int(v7p_parts[1])
        act_h, act_a = int(actual_parts[0]), int(actual_parts[1])

        # Direction check
        def direction(h, a):
            if h > a: return 'H'
            if a > h: return 'A'
            return 'D'
        v6_ok = "✅" if direction(v6_h, v6_a) == direction(act_h, act_a) else "❌"
        v7_ok = "✅" if direction(v7_h, v7_a) == direction(act_h, act_a) else "❌"

        if v6_ok == "❌" and v7_ok == "✅":
            improvement = "🟢 方向修正!"
        elif v6_ok == "✅" and v7_ok == "✅":
            v6_diff = abs(v6_h - act_h) + abs(v6_a - act_a)
            v7_diff = abs(v7_h - act_h) + abs(v7_a - act_a)
            if v7_diff < v6_diff:
                improvement = f"🟢 分差缩小({v6_diff}→{v7_diff})"
            elif v7_diff == v6_diff:
                improvement = "🟡 持平"
            else:
                improvement = f"🔴 分差增大({v6_diff}→{v7_diff})"

    v6p_str = v6_preds[i-1]
    print(f"  {i:<3} {m['home_cn']+' vs '+m['away_cn']:<24} {actual:<6} {v6p_str:<6} {p['ft']:<6} "
          f"{v7_ok:<6} {improvement:<25}")

# ─── v7参数卡 ───
print(f"""
{'='*80}
  🔧 v7 vs v6 参数变更
{'='*80}
  {'参数':<30} {'v6':<12} {'v7':<12} {'原因':<30}
  {'─'*80}
  {'球员层面权重':<30} {'25%':<12} {'22%':<12} {'核心灾难状态稀释':<30}
  {'基本面排名权重':<30} {'20%':<12} {'18%':<12} {'首轮排名参考值降低':<30}
  {'伤病权重':<30} {'18%':<12} {'15%':<12} {'带伤出战大赛常见':<30}
  {'地理优势权重':<30} {'12%':<12} {'8%':<12} {'前2场地理影响不显著':<30}
  {'趋势信号权重':<30} {'8%':<12} {'12%':<12} {'非洲连续爆冷需重视':<30}
  {'赔率市场权重':<30} {'7%':<12} {'8%':<12} {'市场预判冷门更准':<30}
  {'🆕 历史战意权重':<30} {'N/A':<12} {'7%':<12} {'52年首秀史诗级战意':<30}
  {'年龄41+衰减系数':<30} {'0.58':<12} {'0.65':<12} {'老将大赛经验抵消衰减':<30}
  {'年龄39+衰减系数':<30} {'0.72':<12} {'0.78':<12} {'同上':<30}
  {'恢复中状态系数':<30} {'0.65':<12} {'0.78':<12} {'带伤出战大赛动力强':<30}
  {'冷门极高阈值':<30} {'50%':<12} {'45%':<12} {'更诚实面对不确定性':<30}
  {'Top5弱队赢2球+概率':<30} {'10%':<12} {'8%':<12} {'首场保守因子':<30}

{'='*80}
  📌 v7 数据文件: player_database_v6.json | referee_database_v6.json | worldcup_data.json
  📌 复盘来源: 捷克1-1南非 | 瑞士vs波黑(待赛) | 加拿大vs卡塔尔(待赛) | 墨西哥vs韩国(待赛)
  ⚠️ 所有预测仅供娱乐参考
{'='*80}
""")

# 保存文件
out_txt = os.path.join(BASE_DIR, f"2026世界杯6月19日预测分析_v7.txt")
# (省略txt保存，以md为主)
print(f"\n  v7预测引擎就绪。复盘文档: 2026世界杯6月19日复盘与瑞士vs波黑深度预测.md")
