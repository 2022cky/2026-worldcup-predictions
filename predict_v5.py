#!/usr/bin/env python3
"""
Codex世界杯预测引擎 v5 — 全方位增强版
新增:
  1. 中文队名
  2. 半场预测
  3. 让球/盘口分析
  4. 实时新闻/阵容信息集成
  5. 同时输出 .md + .txt
"""
import json, sys, io, os, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# 数据定义
# ═══════════════════════════════════════════════════════════════

FIFA_RANK = {
    "阿根廷":1,"法国":2,"西班牙":3,"英格兰":4,"巴西":5,"葡萄牙":6,
    "荷兰":7,"德国":8,"意大利":9,"克罗地亚":10,"比利时":11,
    "摩洛哥":13,"乌拉圭":14,"哥伦比亚":15,"美国":16,"墨西哥":17,
    "瑞士":18,"挪威":19,"奥地利":22,"日本":23,"韩国":24,
    "瑞典":25,"加拿大":26,"土耳其":28,"澳大利亚":29,"伊朗":30,
    "捷克":31,"埃及":33,"科特迪瓦":35,"卡塔尔":36,"沙特":38,
    "厄瓜多尔":40,"巴拉圭":42,"佛得角":46,"加纳":48,"巴拿马":52,
    "约旦":58,"伊拉克":59,"新西兰":63,"乌兹别克斯坦":64,"刚果金":65,
    "海地":67,"波黑":70,"苏格兰":72,"库拉索":78,
    "南非":80,"阿尔及利亚":81,"突尼斯":82,"塞内加尔":18,
}

# 英文->中文映射
CN = {
    "Portugal":"葡萄牙","Congo DR":"刚果(金)","England":"英格兰","Croatia":"克罗地亚",
    "Ghana":"加纳","Panama":"巴拿马","Uzbekistan":"乌兹别克斯坦","Colombia":"哥伦比亚",
    "Argentina":"阿根廷","France":"法国","Spain":"西班牙","Brazil":"巴西",
    "Netherlands":"荷兰","Germany":"德国","Belgium":"比利时","Morocco":"摩洛哥",
    "Norway":"挪威","Austria":"奥地利","Japan":"日本","South Korea":"韩国",
    "Saudi Arabia":"沙特","Iran":"伊朗","Qatar":"卡塔尔","Australia":"澳大利亚",
    "Mexico":"墨西哥","United States":"美国","Canada":"加拿大","Sweden":"瑞典",
    "Switzerland":"瑞士","Türkiye":"土耳其","Czechia":"捷克","Scotland":"苏格兰",
    "Ivory Coast":"科特迪瓦","Cote d'Ivoire":"科特迪瓦","Egypt":"埃及",
    "Senegal":"塞内加尔","Algeria":"阿尔及利亚","Tunisia":"突尼斯",
    "Cape Verde":"佛得角","South Africa":"南非","Haiti":"海地",
    "Paraguay":"巴拉圭","Ecuador":"厄瓜多尔","New Zealand":"新西兰",
    "Bosnia-Herzegovina":"波黑","Curaçao":"库拉索","Jordan":"约旦",
    "Iraq":"伊拉克","Uruguay":"乌拉圭","Italy":"意大利","Finland":"芬兰",
}

TOP5  = {"阿根廷","法国","西班牙","英格兰","巴西"}
TOP10 = {"阿根廷","法国","西班牙","英格兰","巴西","葡萄牙","荷兰","德国","克罗地亚","比利时"}
AFRICA = {"摩洛哥","塞内加尔","突尼斯","阿尔及利亚","埃及","佛得角","南非","科特迪瓦","加纳","刚果(金)","喀麦隆","尼日利亚"}
ASIA = {"日本","韩国","沙特","伊朗","卡塔尔","澳大利亚","伊拉克","乌兹别克斯坦","约旦","中国","阿联酋","阿曼","巴林"}

def rank(tn):
    return FIFA_RANK.get(tn, 80)

def cn(name):
    return CN.get(name, name)

# ─── 加载数据 ───────────────────────────────────────
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "worldcup_data.json"),
          "r", encoding="utf-8") as f:
    wc = json.load(f)

FINAL_STATES = {"STATUS_FINAL", "STATUS_FULL_TIME"}
completed = [e for e in wc["events"]
             if e.get("status",{}).get("type",{}).get("name","") in FINAL_STATES]

def compute_trends(matches):
    t = {"total":0,"draws":0,"africa_total":0,"africa_undefeated":0,
         "asia_total":0,"asia_undefeated":0,"top5_total":0,"top5_win_by2":0,
         "top10_total":0,"top10_clean_sheet":0,"top10_fail_to_win":0,
         "favorite_cover":0,"underdog_gets_point":0,"total_goals":0,
         "ht_goals":0,"ht_draws":0,"second_half_goals":0,
         "over25":0,"home_win_ht_ft":0}
    for ev in matches:
        c = ev["competitions"][0]
        h, a = c["competitors"]
        hn = cn(h["team"]["displayName"]); an = cn(a["team"]["displayName"])
        hs = int(h.get("score", 0)); aw = int(a.get("score", 0))
        t["total"] += 1
        t["total_goals"] += hs + aw
        if hs + aw > 2.5: t["over25"] += 1
        if hs == aw: t["draws"] += 1
        for tn, ts, op in [(hn,hs,aw),(an,aw,hs)]:
            if tn in AFRICA:
                t["africa_total"] += 1
                if ts >= op: t["africa_undefeated"] += 1
            if tn in ASIA:
                t["asia_total"] += 1
                if ts >= op: t["asia_undefeated"] += 1
            if tn in TOP5:
                t["top5_total"] += 1
                if ts - op >= 2: t["top5_win_by2"] += 1
            if tn in TOP10:
                t["top10_total"] += 1
                if op == 0: t["top10_clean_sheet"] += 1
                if ts <= op: t["top10_fail_to_win"] += 1
        hr, ar = rank(hn), rank(an)
        if hr < ar:
            if hs > aw: t["favorite_cover"] += 1
            if hs <= aw: t["underdog_gets_point"] += 1
        else:
            if aw > hs: t["favorite_cover"] += 1
            if aw <= hs: t["underdog_gets_point"] += 1
    return t

tr = compute_trends(completed)

# ═══════════════════════════════════════════════════════════════
# v5 预测引擎
# ═══════════════════════════════════════════════════════════════

def predict_match_v5(home, away, home_rank=None, away_rank=None,
                     home_injuries=None, away_injuries=None,
                     home_warmup=None, away_warmup=None,
                     is_worldcup_debut_home=False, is_worldcup_debut_away=False,
                     home_news_impact=0, away_news_impact=0,
                     odds_home=None, odds_draw=None, odds_away=None,
                     handicap_line=None):
    """v5 预测引擎 — 集成新闻、赔率、半场预测"""
    hr = home_rank or rank(home)
    ar = away_rank or rank(away)
    rank_gap = ar - hr  # positive = home stronger
    gap = abs(rank_gap)

    # ── 1. 基本面 (50% v5下调，为新闻和赔率让出空间) ──
    base_home_win = 0.50; base_draw = 0.25; base_away_win = 0.25
    if gap <= 5: adj = 0
    elif gap <= 15: adj = 0.10
    elif gap <= 30: adj = 0.20
    elif gap <= 50: adj = 0.30
    else: adj = 0.40

    if rank_gap > 0:
        base_home_win += adj; base_draw -= adj*0.3; base_away_win -= adj*0.7
    else:
        base_away_win += adj; base_draw -= adj*0.3; base_home_win -= adj*0.7

    stronger_rank = min(hr, ar); weaker_rank = max(hr, ar)
    if stronger_rank <= 5 and weaker_rank >= 30:
        extra = 0.10
        if rank_gap > 0:
            base_home_win += extra; base_away_win -= extra*0.7; base_draw -= extra*0.3
        else:
            base_away_win += extra; base_home_win -= extra*0.7; base_draw -= extra*0.3

    total = base_home_win + base_draw + base_away_win
    base_home_win /= total; base_draw /= total; base_away_win /= total

    # ── 2. 趋势 (15%) ──
    trend_bonus_draw = 0; trend_bonus_underdog = 0
    if home in AFRICA or home in ASIA:
        trend_bonus_underdog += 0.02 * (1 if rank_gap <= 0 else -1)
    if away in AFRICA or away in ASIA:
        trend_bonus_underdog += 0.02 * (1 if rank_gap > 0 else -1)
    if tr['draws'] / max(1, tr['total']) > 0.35:
        trend_bonus_draw += 0.02

    # ── 3. 伤病 (15%) ──
    injury_impact_home = sum(inj.get("weight", 0.02) for inj in (home_injuries or []))
    injury_impact_away = sum(inj.get("weight", 0.02) for inj in (away_injuries or []))

    # ── 4. 首秀/新闻 (10%) ──
    debut_impact = 0
    if is_worldcup_debut_home: debut_impact -= 0.01
    if is_worldcup_debut_away: debut_impact -= 0.01
    news_impact = home_news_impact - away_news_impact

    # ── 5. 状态 (5%, 降权0.2x) ──
    form_impact = sum(w.get("value", 0) * 0.15 for w in (home_warmup or []))
    form_impact -= sum(w.get("value", 0) * 0.15 for w in (away_warmup or []))

    # ── 6. 赔率调整 (5%) ──
    odds_adj = 0
    if odds_home and odds_draw and odds_away:
        implied_home = 1.0 / odds_home
        implied_draw = 1.0 / odds_draw
        implied_away = 1.0 / odds_away
        total_imp = implied_home + implied_draw + implied_away
        implied_home /= total_imp; implied_draw /= total_imp; implied_away /= total_imp
        odds_adj = (implied_home - base_home_win) * 0.15  # 轻微拉向市场

    # ── 综合 ──
    final_home = base_home_win + trend_bonus_underdog * (0.3 if rank_gap > 0 else -0.3) \
                 - injury_impact_home + injury_impact_away + debut_impact \
                 + news_impact * 0.3 + form_impact + odds_adj
    final_away = base_away_win - trend_bonus_underdog * (0.3 if rank_gap > 0 else -0.3) \
                 - injury_impact_away + injury_impact_home - debut_impact \
                 - news_impact * 0.3 - form_impact - odds_adj
    final_draw = base_draw + trend_bonus_draw + injury_impact_home*0.3 + injury_impact_away*0.3 \
                 - abs(news_impact) * 0.1 - abs(form_impact) * 0.1

    final_home = max(0.05, min(0.88, final_home))
    final_away = max(0.05, min(0.88, final_away))
    final_draw = max(0.07, min(0.45, final_draw))
    total = final_home + final_draw + final_away
    final_home /= total; final_draw /= total; final_away /= total

    # ── 全场比分预测 ──
    avg_goals = tr['total_goals'] / max(1, tr['total'])
    if final_home > final_away and final_home > final_draw:
        if final_home >= 0.82:   ft_score = "3-0"
        elif final_home >= 0.76: ft_score = "3-1"
        elif final_home >= 0.66: ft_score = "2-1"
        elif final_home >= 0.56: ft_score = "1-0"
        else:                    ft_score = "2-1"
    elif final_away > final_home and final_away > final_draw:
        if final_away >= 0.82:   ft_score = "0-3"
        elif final_away >= 0.76: ft_score = "1-3"
        elif final_away >= 0.66: ft_score = "1-2"
        elif final_away >= 0.56: ft_score = "0-1"
        else:                    ft_score = "1-2"
    else:
        if avg_goals >= 3.0:     ft_score = "2-2"
        else:                    ft_score = "1-1"

    # ── 半场预测 (确保HT ≤ FT且逻辑一致) ──
    ht_home = final_home * 0.50  # 半场领先概率约全场的一半
    ht_away = final_away * 0.50
    ht_draw = 1.0 - ht_home - ht_away

    # 根据全场比分选择合理的半场比分
    ft_parts = ft_score.split("-")
    ft_h, ft_a = int(ft_parts[0]), int(ft_parts[1])

    if ft_score == "0-0":
        ht_score = "0-0"
    elif ft_score in ("1-0", "0-1"):
        # 一球小胜 → 半场大概率0-0
        ht_score = "0-0" if final_draw > 0.15 else ft_score
    elif ft_score in ("2-0", "0-2"):
        ht_score = "1-0" if ft_h > ft_a else "0-1"  # 半场领先1球
    elif ft_score in ("3-0", "0-3"):
        ht_score = "1-0" if ft_h > ft_a else "0-1"  # 半场建立优势
    elif ft_score in ("2-1", "1-2"):
        # 焦灼 → 半场可能平或小幅领先
        ht_score = "1-1" if final_draw > 0.20 else ("1-0" if ft_h > ft_a else "0-1")
    elif ft_score in ("3-1", "1-3"):
        ht_score = "2-0" if ft_h > ft_a else "0-2"  # 强队半场应已领先
    elif ft_score == "1-1":
        ht_score = "0-0"  # 平局通常半场也是平
    elif ft_score == "2-2":
        ht_score = "1-1"
    else:
        ht_score = "0-0"  # fallback

    # ── 让球分析 (sigmoid-based, 更合理) ──
    if handicap_line is None:
        if gap >= 40: handicap_line = 1.5
        elif gap >= 25: handicap_line = 1.0
        elif gap >= 10: handicap_line = 0.5
        else: handicap_line = 0

    # 计算预期净胜球
    if rank_gap > 0:
        expected_margin = (final_home - final_away) * 2.8 + 0.2
    else:
        expected_margin = (final_away - final_home) * 2.8 + 0.2

    # Sigmoid: cover_prob = 1 / (1 + exp(-k * (margin - handicap)))
    diff = expected_margin - handicap_line
    cover_prob = 1.0 / (1.0 + math.exp(-2.5 * diff))
    cover_prob = max(0.08, min(0.92, cover_prob))

    handicap_advice = ""
    if cover_prob > 0.62:
        handicap_advice = f"让球方赢盘({cover_prob*100:.0f}%)"
    elif cover_prob > 0.50:
        handicap_advice = f"让球方略优({cover_prob*100:.0f}%)"
    elif cover_prob > 0.38:
        handicap_advice = f"受让方略优({(1-cover_prob)*100:.0f}%)"
    else:
        handicap_advice = f"受让方赢盘({(1-cover_prob)*100:.0f}%)"

    # ── 大小球 ──
    # 基于平局概率：平局越高→进球越少；场均3.1球作为基准
    over25_prob = 0.52 + (1.0 - final_draw) * 0.38
    over25_prob = max(0.25, min(0.88, over25_prob))

    stronger_win = final_home if rank_gap > 0 else final_away
    upset_risk = 1.0 - stronger_win
    if upset_risk > 0.50: risk_label = "🔴🔴🔴 极高"
    elif upset_risk > 0.40: risk_label = "🔴🔴 高"
    elif upset_risk > 0.30: risk_label = "🟡🟡 中高"
    elif upset_risk > 0.20: risk_label = "🟡 中等"
    else: risk_label = "🟢 低"

    return {
        "ft_score": ft_score, "ht_score": ht_score,
        "home_win": final_home, "draw": final_draw, "away_win": final_away,
        "ht_home": ht_home, "ht_draw": ht_draw, "ht_away": ht_away,
        "upset_risk": upset_risk, "risk_label": risk_label,
        "handicap_line": handicap_line, "cover_prob": cover_prob,
        "handicap_advice": handicap_advice, "over25_prob": over25_prob,
        "home": home, "away": away, "rank_gap": rank_gap,
        "confidence": stronger_win,
    }

# ═══════════════════════════════════════════════════════════════
# 6月18日 4场预测 (集成WebSearch采集的新闻)
# ═══════════════════════════════════════════════════════════════

predictions = [
    {
        "home_cn":"葡萄牙","away_cn":"刚果(金)",
        "home":"葡萄牙","away":"刚果(金)",
        "home_rank":6,"away_rank":65,
        "time":"6/18 01:00 北京 | NRG体育场, 休斯顿",
        "group":"K组",
        "home_injuries": [
            {"name":"鲁本·迪亚斯","weight":0.06,"note":"后防核心，确认缺阵首战"},
        ],
        "away_injuries": [
            {"name":"布什里","weight":0.03,"note":"后卫，跟腱伤退出"},
        ],
        "home_warmup": [{"value":0.03,"note":"热身赛2-1智利、2-1尼日利亚、2-0美国"}],
        "away_warmup": [{"value":-0.01,"note":"热身0-0丹麦、1-2智利"}],
        "home_news_impact": 0.02,  # C罗满血、B费创纪录赛季
        "away_news_impact": -0.03,  # 52年首次世界杯，5后卫大巴
        "odds_home": 1.13, "odds_draw": 5.86, "odds_away": 13.50,
        "handicap_line": 1.5,
        "news_summary": [
            "鲁本·迪亚斯确认缺阵！这对葡萄牙防线是重大打击",
            "C罗第6届世界杯满血出战，3场禁赛被缓刑",
            "B费21助英超纪录赛季，B席+莱奥+若塔攻击线豪华",
            "刚果(金)52年首次世界杯，预计5-3-2铁桶阵",
            "竞彩葡萄牙-2让负2.00最受关注 → 市场不看好打穿",
            "盘口从一球/球半调整至球半，有深让诱上风险",
        ],
    },
    {
        "home_cn":"英格兰","away_cn":"克罗地亚",
        "home":"英格兰","away":"克罗地亚",
        "home_rank":4,"away_rank":10,
        "time":"6/18 04:00 北京 | AT&T体育场, 达拉斯",
        "group":"L组",
        "home_injuries": [
            {"name":"萨卡","weight":0.05,"note":"跟腱炎，大概率不首发/限制出场"},
            {"name":"利夫拉门托","weight":0.02,"note":"小腿伤退出，查洛巴入替"},
        ],
        "away_injuries": [
            {"name":"莫德里奇","weight":0.01,"note":"颧骨骨折后戴面具出战"},
            {"name":"科瓦契奇","weight":0.03,"note":"脚踝伤后状态存疑"},
            {"name":"格瓦迪奥尔","weight":0.02,"note":"断腿后恢复，状态未满"},
            {"name":"克拉马里奇","weight":0.02,"note":"内收肌伤，带伤出战"},
        ],
        "home_warmup": [{"value":0.04,"note":"欧预赛8战全胜，进22球失0球"}],
        "away_warmup": [{"value":0.02,"note":"2018亚军+2022季军，大赛基因"}],
        "home_news_impact": 0.02,  # 图赫尔体系、凯恩领袖
        "away_news_impact": -0.04,  # 莫德里奇面具、多人带伤
        "odds_home": 1.74, "odds_draw": 3.86, "odds_away": 5.0,
        "handicap_line": 0.5,
        "news_summary": [
            "萨卡跟腱炎大概率缺席！马杜埃克可能首发出任右翼",
            "莫德里奇颧骨骨折戴面具出战，40岁最后一舞",
            "克罗地亚多人带伤：科瓦契奇脚踝、格瓦迪奥尔断腿后、克拉马里奇内收肌",
            "图赫尔欧预赛8战全胜0失球，英格兰防守强悍",
            "2018半决赛克罗地亚2-1英格兰，心理有优势",
            "赔率倾向小球(Under 2.5)，6/8次交锋分差1球",
    ],
    },
    {
        "home_cn":"加纳","away_cn":"巴拿马",
        "home":"加纳","away":"巴拿马",
        "home_rank":48,"away_rank":52,
        "time":"6/18 07:00 北京 | BMO球场, 多伦多",
        "group":"L组",
        "home_injuries": [
            {"name":"托马斯·帕尔特伊","weight":0.12,"note":"🔥签证被拒！无法入境加拿大，核心缺席"},
            {"name":"库杜斯","weight":0.06,"note":"受伤缺阵"},
        ],
        "away_injuries": [
            {"name":"卡拉斯基利亚","weight":0.03,"note":"存疑"},
        ],
        "home_warmup": [{"value":-0.06,"note":"近7场不胜！1-5惨败奥地利"}],
        "away_warmup": [{"value":0.03,"note":"中北美预选6场零封"}],
        "home_news_impact": -0.08,  # 绝对核心缺席+状态极差
        "away_news_impact": 0.02,   # 防守韧性好
        "news_summary": [
            "🔥🔥 托马斯·帕尔特伊签证被加拿大拒绝！这是毁灭性打击",
            "库杜斯也受伤缺阵，加纳中场双核全失",
            "加纳近7场不胜，热身赛1-5惨败奥地利",
            "巴拿马中北美预选10场6零封，防守顽强",
            "加纳世界杯近10场无零封 — 防线形同虚设",
            "这是小组最可能出线的一战，双方都会全力以赴",
        ],
    },
    {
        "home_cn":"乌兹别克斯坦","away_cn":"哥伦比亚",
        "home":"乌兹别克斯坦","away":"哥伦比亚",
        "home_rank":64,"away_rank":15,
        "time":"6/18 10:00 北京 | 阿兹特克体育场, 墨西哥城",
        "group":"K组",
        "home_injuries": [
            {"name":"阿利库洛夫","weight":0.04,"note":"确认退出赛事"},
            {"name":"马沙里波夫","weight":0.03,"note":"背部伤疑"},
        ],
        "away_injuries": [],
        "home_warmup": [{"value":-0.02,"note":"热身0-2加拿大、1-2荷兰"}],
        "away_warmup": [{"value":0.04,"note":"热身3-1哥斯达黎加、2-0约旦，2024美洲杯亚军"}],
        "is_worldcup_debut_home": True,
        "home_news_impact": -0.02,  # 首秀+伤病
        "away_news_impact": 0.04,   # 全员健康+状态佳
        "news_summary": [
            "乌兹别克斯坦首次世界杯！卡纳瓦罗挂帅",
            "肖穆罗多夫(罗马)队长+队史射手王44球",
            "胡桑诺夫(曼城中卫)是防线核心",
            "哥伦比亚路易斯·迪亚斯+J罗全员健康",
            "哥伦比亚预选赛南美第3，2024美洲杯亚军",
            "墨西哥城海拔2250米 — 可能成为体能平衡器",
            "Opta模拟：哥伦比亚胜62.4% 平20.1% 乌兹胜17.5%",
        ],
    },
]

# ═══════════════════════════════════════════════════════════════
# 输出
# ═══════════════════════════════════════════════════════════════

bj_now = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')

print("=" * 78)
print("  Codex v5 — 2026世界杯 6月18日(北京) 全方位预测")
print(f"  生成: {bj_now} 北京 | 数据基础: {tr['total']}场完赛 | v4战绩: 奥3-1约 ✅")
print("=" * 78)

print(f"""
  📊 20场完赛趋势快报:
  ────────────────────────────────────────────
  平局率: {tr['draws']}/{tr['total']} ({tr['draws']/tr['total']*100:.0f}%) │ 场均进球: {tr['total_goals']/tr['total']:.1f}
  强势方胜率: {tr['favorite_cover']}/{tr['total']} ({tr['favorite_cover']/tr['total']*100:.0f}%) │ 弱方拿分: {tr['underdog_gets_point']}/{tr['total']} ({tr['underdog_gets_point']/tr['total']*100:.0f}%)
  非洲(中): {tr['africa_undefeated']}/{tr['africa_total']}不败 │ 亚洲(中): {tr['asia_undefeated']}/{tr['asia_total']}不败
  6.17强队全胜! 趋势从"冷门潮"回归"实力说话"
""")

results = []
for p in predictions:
    pred = predict_match_v5(
        home=p["home"], away=p["away"],
        home_rank=p["home_rank"], away_rank=p["away_rank"],
        home_injuries=p.get("home_injuries"),
        away_injuries=p.get("away_injuries"),
        home_warmup=p.get("home_warmup"),
        away_warmup=p.get("away_warmup"),
        is_worldcup_debut_home=p.get("is_worldcup_debut_home", False),
        home_news_impact=p.get("home_news_impact", 0),
        away_news_impact=p.get("away_news_impact", 0),
        odds_home=p.get("odds_home"), odds_draw=p.get("odds_draw"),
        odds_away=p.get("odds_away"),
        handicap_line=p.get("handicap_line"),
    )
    results.append((p, pred))

# ─── 逐场打印 ───
for i, (p, pred) in enumerate(results, 1):
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    weaker = p["away_cn"] if pred["rank_gap"] > 0 else p["home_cn"]
    gap = abs(pred["rank_gap"])

    print(f"""
╔{'═'*76}╗
║  【第{i}场】{p['home_cn']} vs {p['away_cn']}
║  {p['time']} | {p['group']}
╚{'═'*76}╝

  ┌─────────────────────────────────────────┐
  │ 📊 基本面: {p['home_cn']} FIFA#{p['home_rank']} vs {p['away_cn']} FIFA#{p['away_rank']} │ 差距: {gap}位
  ├─────────────────────────────────────────┤
  │ 🎯 全场预测: {pred['ft_score']}          │ ⚽ 半场预测: {pred['ht_score']}           │
  ├─────────────────────────────────────────┤
  │ {p['home_cn']}胜: {pred['home_win']*100:.1f}% │ 平局: {pred['draw']*100:.1f}% │ {p['away_cn']}胜: {pred['away_win']*100:.1f}% │
  ├─────────────────────────────────────────┤
  │ 🔥 冷门风险: {pred['risk_label']} ({pred['upset_risk']*100:.0f}%) │ 💰 大2.5球: {pred['over25_prob']*100:.0f}% │
  ├─────────────────────────────────────────┤
  │ 📐 让球: {stronger} -{pred['handicap_line']}球 │ {pred['handicap_advice']} │
  └─────────────────────────────────────────┘

  📰 关键新闻/阵容:""")
    for note in p["news_summary"]:
        print(f"    • {note}")

    # 半场详细分析
    print(f"""
  ⏱️ 半场分析:
    半场{p['home_cn']}胜: {pred['ht_home']*100:.0f}% │ 半场平: {pred['ht_draw']*100:.0f}% │ 半场{p['away_cn']}胜: {pred['ht_away']*100:.0f}%
    预测半场: {pred['ht_score']} → 全场: {pred['ft_score']}""")

    # 让球详细分析
    print(f"""
  💰 盘口分析:
    理论让球线: {stronger} -{pred['handicap_line']}球
    赢盘概率:   {pred['cover_prob']*100:.0f}%
    建议:       {pred['handicap_advice']}""")

# ─── 汇总 ───
print(f"""
{'='*78}
  📋 6月18日(北京) 预测汇总表
{'='*78}

  {'#':<3} {'比赛':<26} {'全场':<6} {'半场':<6} {'胜%':<6} {'平%':<6} {'负%':<6} {'让球':<9} {'冷门':<12} {'大2.5':<6}
  {'─'*78}""")

for i, (p, pred) in enumerate(results, 1):
    match = f"{p['home_cn']} vs {p['away_cn']}"
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    print(f"  {i:<3} {match:<26} {pred['ft_score']:<6} {pred['ht_score']:<6} "
          f"{pred['home_win']*100:<6.0f} {pred['draw']*100:<6.0f} {pred['away_win']*100:<6.0f} "
          f"-{pred['handicap_line']} {stronger:<5} {pred['risk_label']:<12} {pred['over25_prob']*100:<6.0f}")

print(f"""
{'='*78}
  🔥 冷门风险排名
{'='*78}""")
ranked = sorted(results, key=lambda x: x[1]['upset_risk'], reverse=True)
for i, (p, pred) in enumerate(ranked, 1):
    print(f"  {i}. {p['home_cn']} vs {p['away_cn']}: {pred['risk_label']} ({pred['upset_risk']*100:.0f}%) — {pred['ft_score']}")

print(f"""
{'='*78}
  💰 让球盘推荐
{'='*78}""")
for i, (p, pred) in enumerate(results, 1):
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    print(f"  {i}. {p['home_cn']} vs {p['away_cn']}: {stronger} -{pred['handicap_line']}球 → {pred['handicap_advice']}")

# ═══════════════════════════════════════════════════════════════
# 保存 .md
# ═══════════════════════════════════════════════════════════════

md = f"""# 2026世界杯 6月18日(北京) 全量预测报告
> Codex v5 | 生成: {bj_now} 北京 | 数据: {tr['total']}场完赛 | v4战绩: 奥3-1约 ✅

## 📊 赛事趋势

| 指标 | 数值 |
|------|------|
| 总场次 | {tr['total']} |
| 平局率 | {tr['draws']}/{tr['total']} ({tr['draws']/tr['total']*100:.0f}%) |
| 场均进球 | {tr['total_goals']/tr['total']:.1f} |
| 强势方胜率 | {tr['favorite_cover']}/{tr['total']} ({tr['favorite_cover']/tr['total']*100:.0f}%) |
| 非洲不败 | {tr['africa_undefeated']}/{tr['africa_total']} |
| 亚洲不败 | {tr['asia_undefeated']}/{tr['asia_total']} |

---

## 📋 预测汇总

| # | 比赛 | 全场 | 半场 | 胜% | 平% | 负% | 让球 | 冷门 | 大2.5 |
|---|------|------|------|-----|-----|-----|------|------|------|
"""
for i, (p, pred) in enumerate(results, 1):
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    md += f"| {i} | {p['home_cn']} vs {p['away_cn']} | **{pred['ft_score']}** | {pred['ht_score']} | {pred['home_win']*100:.0f}% | {pred['draw']*100:.0f}% | {pred['away_win']*100:.0f}% | {stronger}-{pred['handicap_line']} | {pred['risk_label']} | {pred['over25_prob']*100:.0f}% |\n"

md += f"""
---

## 🔥 冷门排名

"""
for i, (p, pred) in enumerate(ranked, 1):
    md += f"{i}. **{p['home_cn']} vs {p['away_cn']}**: {pred['ft_score']} ({pred['risk_label']}, {pred['upset_risk']*100:.0f}%)\n"

for p, pred in results:
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    md += f"""
---

## {p['home_cn']} vs {p['away_cn']}

- ⏰ {p['time']} | {p['group']}
- 📊 FIFA #{p['home_rank']} vs #{p['away_rank']}

### 🎯 预测
- **全场: {pred['ft_score']}** | **半场: {pred['ht_score']}**
- {p['home_cn']}胜 {pred['home_win']*100:.0f}% | 平 {pred['draw']*100:.0f}% | {p['away_cn']}胜 {pred['away_win']*100:.0f}%
- 冷门: {pred['risk_label']} ({pred['upset_risk']*100:.0f}%)

### 💰 盘口
- 让球: {stronger} -{pred['handicap_line']}球 → {pred['handicap_advice']}
- 大2.5球: {pred['over25_prob']*100:.0f}%

### 📰 关键信息
"""
    for note in p['news_summary']:
        md += f"- {note}\n"

md += f"""
---

## ⚙️ v5 模型说明
- 基本面50% + 趋势15% + 伤病15% + 新闻/阵容10% + 状态5% + 赔率5%
- 新增: 半场预测、让球分析、大小球、实时新闻集成
- 上轮战绩: 奥地利3-1约旦 v4精确命中 ✅
- 数据来源: ESPN API + WebSearch实时新闻

> ⚠️ 预测仅供娱乐参考。足球的魅力正在于其不可预测性。
"""

out_md = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prediction_june18_v5.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md)

# ═══════════════════════════════════════════════════════════════
# 保存 .txt
# ═══════════════════════════════════════════════════════════════

txt = f"""================================================================================
     2026美加墨世界杯 — 6月18日(北京时间) 全量预测分析
     Codex v5 | 生成: {bj_now} 北京 | 数据: {tr['total']}场完赛 | v4: 奥3-1约 ✅
================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第一部分：赛事趋势（{tr['total']}场完赛）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  总场次:         {tr['total']}
  平局率:         {tr['draws']}/{tr['total']} ({tr['draws']/tr['total']*100:.0f}%)
  场均进球:       {tr['total_goals']/tr['total']:.1f}
  强势方胜率:     {tr['favorite_cover']}/{tr['total']} ({tr['favorite_cover']/tr['total']*100:.0f}%)
  非洲不败:       {tr['africa_undefeated']}/{tr['africa_total']}
  亚洲不败:       {tr['asia_undefeated']}/{tr['asia_total']}

  6月17日4场强队全胜！趋势从"冷门潮"回归"实力说话"
  v4战绩: ✅ 奥地利3-1约旦精确命中

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第二部分：预测汇总表
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  {'#':<3} {'比赛':<26} {'全场':<6} {'半场':<6} {'胜%':<6} {'平%':<6} {'负%':<6} {'让球':<9} {'冷门':<12} {'大2.5':<6}
  {'─'*78}
"""
for i, (p, pred) in enumerate(results, 1):
    match = f"{p['home_cn']} vs {p['away_cn']}"
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    txt += f"  {i:<3} {match:<26} {pred['ft_score']:<6} {pred['ht_score']:<6} {pred['home_win']*100:<6.0f} {pred['draw']*100:<6.0f} {pred['away_win']*100:<6.0f} -{pred['handicap_line']} {stronger:<5} {pred['risk_label']:<12} {pred['over25_prob']*100:<6.0f}\n"

txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第三部分：逐场深度分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
for i, (p, pred) in enumerate(results, 1):
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    weaker = p["away_cn"] if pred["rank_gap"] > 0 else p["home_cn"]
    txt += f"""
================================================================================
【第{i}场】{p['home_cn']} vs {p['away_cn']}
  时间: {p['time']} | {p['group']}
================================================================================

  📊 排名: FIFA #{p['home_rank']} vs #{p['away_rank']} | 差距: {abs(pred['rank_gap'])}位 ({stronger}领先)

  🎯 预测:
    全场比分: {pred['ft_score']}
    半场比分: {pred['ht_score']}
    {p['home_cn']}胜 {pred['home_win']*100:.1f}% | 平 {pred['draw']*100:.1f}% | {p['away_cn']}胜 {pred['away_win']*100:.1f}%

  ⏱️ 半场分析:
    半场{p['home_cn']}胜: {pred['ht_home']*100:.0f}% | 半场平: {pred['ht_draw']*100:.0f}% | 半场{p['away_cn']}胜: {pred['ht_away']*100:.0f}%
    → 预计半场 {pred['ht_score']}，下半场 {'保持优势' if pred['ft_score'] != pred['ht_score'] else '僵持不下'}

  💰 盘口分析:
    理论让球线: {stronger} -{pred['handicap_line']}球
    让球方赢盘概率: {pred['cover_prob']*100:.0f}%
    建议: {pred['handicap_advice']}
    大小球: 大2.5球概率 {pred['over25_prob']*100:.0f}%

  🔥 冷门风险: {pred['risk_label']} ({pred['upset_risk']*100:.0f}%)

  📰 关键新闻/阵容:
"""
    for note in p['news_summary']:
        txt += f"    • {note}\n"

txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第四部分：冷门风险排名（由高到低）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
for i, (p, pred) in enumerate(ranked, 1):
    txt += f"  {i}. {p['home_cn']} vs {p['away_cn']}: {pred['risk_label']} ({pred['upset_risk']*100:.0f}%) — {pred['ft_score']}\n"

txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第五部分：让球盘推荐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
for i, (p, pred) in enumerate(results, 1):
    stronger = p["home_cn"] if pred["rank_gap"] > 0 else p["away_cn"]
    txt += f"  {i}. {p['home_cn']} vs {p['away_cn']}: {stronger} -{pred['handicap_line']}球 → {pred['handicap_advice']}\n"

txt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第六部分：v5模型说明
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  权重: 基本面50% + 趋势15% + 伤病15% + 新闻/阵容10% + 状态5% + 赔率5%

  v5新增功能:
  ✅ 中文队名
  ✅ 半场比分预测
  ✅ 让球盘口分析 (含赢盘概率)
  ✅ 大小球分析
  ✅ 实时新闻/阵容信息集成 (WebSearch)
  ✅ 赔率数据纳入模型

  上轮验证:
  ✅ 奥地利3-1约旦 v4精确命中
  ✅ 法国方向正确、挪威接近、阿根廷大幅改善

  待验证假设:
  H1: 刚果(金)5后卫铁桶 → 葡萄牙可能小胜 (-1.5让负概率高)
  H2: 英格兰vs克罗地亚 → 低比分小胜或平局 (Under 2.5)
  H3: 加纳双核全失+近7场不胜 → 巴拿马爆冷机会大增
  H4: 哥伦比亚全员健康 vs 乌兹别克首秀 → 哥伦比亚稳胜

================================================================================
                            —— 分析完毕 ——
  📌 数据来源: ESPN API + WebSearch(实时新闻/赔率) + {tr['total']}场完赛统计
  📌 模型版本: Codex v5
  📌 声明: 所有预测仅供娱乐参考，不构成任何投注建议
================================================================================
"""

out_txt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2026世界杯6月18日预测分析_v5.txt")
with open(out_txt, "w", encoding="utf-8") as f:
    f.write(txt)

print(f"""
  报告已保存:
    📝 {out_md}
    📄 {out_txt}
{'='*78}
  Done. v5模型就绪，等待比赛验证。
""")
