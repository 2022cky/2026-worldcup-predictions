#!/usr/bin/env python3
"""
openfootball_data.py — 世界杯结构化数据加载引擎
=====================================================
数据源: openfootball/worldcup.json (https://github.com/openfootball/worldcup.json)
License: Public Domain

功能:
  1. 加载任意年份世界杯数据 (1930-2026)
  2. 按日期/球队/小组查询比赛
  3. 自动计算小组积分榜
  4. 提取进球者列表 (含点球/乌龙标记)
  5. 赛后自动对比预测 vs 实际
  6. 历史冷门分析

使用示例:
    from openfootball_data import WorldCupData

    wc = WorldCupData(2026)
    matches = wc.matches_on_date('2026-06-23')
    standings = wc.group_standings('Group L')
    results = wc.compare_predictions('复盘6月23日_预测6月24日.md')

    历史数据:
    wc_hist = WorldCupData(2022)
    all_qatar = wc_hist.get_all_matches()
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Literal

# ─── 数据路径 ─────────────────────────────────────────
DATA_DIR = Path(__file__).parent / 'data' / 'openfootball'

# ─── 中文球员名映射 ───────────────────────────────────
# 从 squads.json + 预测文件积累的映射表
NAME_CN_MAP = {
    # Mexico
    'Julián Quiñones': '胡利安·基尼奥内斯',
    'Raúl Jiménez': '劳尔·希门尼斯',
    'Luis Romo': '路易斯·罗莫',
    # South Korea
    'Hwang In-Beom': '黄仁范',
    'Oh Hyeon-Gyu': '吴贤揆',
    'Son Heung-Min': '孙兴慜',
    'Lee Kang-In': '李刚仁',
    # Czech Republic
    'Ladislav Krejčí': '拉迪斯拉夫·克雷伊奇',
    'Michal Sadílek': '米哈尔·萨迪莱克',
    # Brazil
    'Vinícius Júnior': '维尼修斯',
    'Matheus Cunha': '马特乌斯·库尼亚',
    'Neymar': '内马尔',
    'Raphinha': '拉菲尼亚',
    # Argentina
    'Lionel Messi': '梅西',
    # France
    'Kylian Mbappé': '姆巴佩',
    'Ousmane Dembélé': '登贝莱',
    'Bradley Barcola': '巴尔科拉',
    # Norway
    'Erling Haaland': '哈兰德',
    'Marcus Holmgren Pedersen': '霍姆格伦·佩德森',
    # England
    'Harry Kane': '哈里·凯恩',
    'Jude Bellingham': '祖德·贝林厄姆',
    'Marcus Rashford': '马库斯·拉什福德',
    # Croatia
    'Martin Baturina': '马丁·巴图里纳',
    'Petar Musa': '佩塔尔·穆萨',
    'Ante Budimir': '安特·布迪米尔',
    # Portugal
    'Cristiano Ronaldo': '克里斯蒂亚诺·罗纳尔多',
    'João Neves': '若昂·内维斯',
    'Rafael Leão': '拉斐尔·莱昂',
    'Nuno Mendes': '努诺·门德斯',
    # Colombia
    'Luis Díaz': '路易斯·迪亚斯',
    'Daniel Muñoz': '丹尼尔·穆尼奥斯',
    'Jáminton Campaz': '哈明顿·坎帕斯',
    # Ghana
    'Caleb Yirenkyi': '卡莱布·伊伦基',
    # DR Congo / 刚果民主共和国
    'Yoane Wissa': '约阿内·维萨',
    # USA
    'Folarin Balogun': '弗拉林·巴洛贡',
    'Giovanni Reyna': '吉奧瓦尼·雷纳',
    'Alex Freeman': '亚历克斯·弗里曼',
    # Germany
    'Felix Nmecha': '费利克斯·恩梅查',
    'Nico Schlotterbeck': '尼科·施洛特贝克',
    'Kai Havertz': '凯·哈弗茨',
    'Jamal Musiala': '贾马尔·穆夏拉',
    'Nathaniel Brown': '纳撒尼尔·布朗',
    'Deniz Undav': '德尼兹·翁达夫',
    # Netherlands
    'Virgil van Dijk': '维吉尔·范戴克',
    'Crysencio Summerville': '克赖森西奥·萨默维尔',
    'Brian Brobbey': '布莱恩·布罗比',
    'Cody Gakpo': '科迪·加克波',
    # Sweden
    'Yasin Ayari': '亚辛·阿亚里',
    'Alexander Isak': '亚历山大·伊萨克',
    'Viktor Gyökeres': '维克多·吉奥克雷斯',
    'Mattias Svanberg': '马蒂亚斯·斯万贝里',
    'Anthony Elanga': '安东尼·埃兰加',
    # Japan
    'Keito Nakamura': '中村敬斗',
    'Daichi Kamada': '鎌田大地',
    'Ayase Ueda': '上田绮世',
    'Junya Ito': '伊东纯也',
    # Spain
    'Lamine Yamal': '拉明·亚马尔',
    'Mikel Oyarzabal': '米克尔·奥亚萨瓦尔',
    # Morocco
    'Ismael Saibari': '伊斯梅尔·赛巴里',
    # USA more
    'Damian Bobadilla': '达米安·博巴迪利亚',
    'Cameron Burgess': '卡梅伦·伯吉斯',
}


def cn_name(english_name: str) -> str:
    """将英文球员名转为中文名，未知时保留原文"""
    return NAME_CN_MAP.get(english_name, english_name)


# ─── 核心数据类 ───────────────────────────────────────

class WorldCupData:
    """加载并查询单届世界杯数据"""

    def __init__(self, year: int = 2026):
        self.year = year
        self.data_dir = DATA_DIR / str(year)

        # 核心数据
        self.name: str = ""
        self.matches: list[dict] = []
        self.squads: list[dict] = []        # 26人名单
        self.teams: list[dict] = []         # 48队信息
        self.groups: list[dict] = []        # 小组定义
        self.stadiums: list[dict] = []      # 场馆
        self.quali_matches: list[dict] = [] # 预选赛附加赛

        self._load()
        self._build_index()

    # ─── 加载 ──────────────────────────────────────

    def _load(self):
        """加载所有JSON文件"""
        base = self.data_dir

        # worldcup.json (主文件: 104场比赛)
        f = base / 'worldcup.json'
        if f.exists():
            d = json.loads(f.read_text(encoding='utf-8'))
            self.name = d.get('name', '')
            self.matches = d.get('matches', [])

        # squads.json (48队26人大名单)
        f = base / 'worldcup.squads.json'
        if f.exists():
            self.squads = json.loads(f.read_text(encoding='utf-8'))

        # teams.json (48队基本信息)
        f = base / 'worldcup.teams.json'
        if f.exists():
            self.teams = json.loads(f.read_text(encoding='utf-8'))

        # groups.json (小组定义)
        f = base / 'worldcup.groups.json'
        if f.exists():
            d = json.loads(f.read_text(encoding='utf-8'))
            self.groups = d.get('groups', [])

        # stadiums.json
        f = base / 'worldcup.stadiums.json'
        if f.exists():
            d = json.loads(f.read_text(encoding='utf-8'))
            self.stadiums = d.get('stadiums', [])

        # quali_playoffs.json
        f = base / 'worldcup.quali_playoffs.json'
        if f.exists():
            d = json.loads(f.read_text(encoding='utf-8'))
            self.quali_matches = d.get('matches', [])

    def _build_index(self):
        """构建查询索引"""
        self._by_date: dict[str, list[dict]] = {}
        self._by_group: dict[str, list[dict]] = {}
        self._by_team: dict[str, list[dict]] = {}
        self._completed: list[dict] = []
        self._fixtures: list[dict] = []

        for m in self.matches:
            # 按日期
            d = m.get('date', '')
            self._by_date.setdefault(d, []).append(m)

            # 按小组
            g = m.get('group', '')
            if g:
                self._by_group.setdefault(g, []).append(m)

            # 按球队
            for t in [m.get('team1', ''), m.get('team2', '')]:
                if t:
                    self._by_team.setdefault(t, []).append(m)

            # 完赛 vs 未赛
            if 'score' in m:
                self._completed.append(m)
            elif 'Round' not in m.get('round', ''):
                self._fixtures.append(m)

    # ─── 查询 API ───────────────────────────────────

    def matches_on_date(self, date_str: str) -> list[dict]:
        """返回某天的所有比赛"""
        return self._by_date.get(date_str, [])

    def matches_in_group(self, group: str) -> list[dict]:
        """返回某组所有比赛"""
        return self._by_group.get(group, [])

    def matches_for_team(self, team_name: str) -> list[dict]:
        """返回某队所有比赛"""
        return self._by_team.get(team_name, [])

    def completed(self) -> list[dict]:
        """返回所有已完赛比赛"""
        return self._completed

    def upcoming(self) -> list[dict]:
        """返回所有未赛小组赛"""
        return self._fixtures

    def find_match(self, team1: str, team2: str) -> Optional[dict]:
        """查找特定对阵 (支持中文名模糊匹配)"""
        # 直接精确匹配
        for m in self.matches:
            t1 = m.get('team1', '')
            t2 = m.get('team2', '')
            if (team1 in t1 or team1 in t2) and (team2 in t1 or team2 in t2):
                return m

        # 中文名 → 英文名映射
        cn_to_en = {
            '葡萄牙': 'Portugal',
            '乌兹别克斯坦': 'Uzbekistan',
            '英格兰': 'England',
            '加纳': 'Ghana',
            '克罗地亚': 'Croatia',
            '巴拿马': 'Panama',
            '哥伦比亚': 'Colombia',
            '刚果民主共和国': 'DR Congo',
            '刚果金': 'DR Congo',
            '刚果': 'DR Congo',
            '阿根廷': 'Argentina',
            '法国': 'France',
            '挪威': 'Norway',
            '塞内加尔': 'Senegal',
            '伊拉克': 'Iraq',
            '奥地利': 'Austria',
            '约旦': 'Jordan',
            '阿尔及利亚': 'Algeria',
            '巴西': 'Brazil',
            '摩洛哥': 'Morocco',
            '苏格兰': 'Scotland',
            '海地': 'Haiti',
            '德国': 'Germany',
            '西班牙': 'Spain',
            '佛得角': 'Cape Verde',
            '美国': 'USA',
            '墨西哥': 'Mexico',
            '捷克': 'Czech Republic',
            '韩国': 'South Korea',
            '南非': 'South Africa',
            '日本': 'Japan',
            '瑞典': 'Sweden',
            '荷兰': 'Netherlands',
            '突尼斯': 'Tunisia',
            '加拿大': 'Canada',
            '瑞士': 'Switzerland',
            '卡塔尔': 'Qatar',
            '波黑': 'Bosnia & Herzegovina',
            '澳大利亚': 'Australia',
            '巴拉圭': 'Paraguay',
            '土耳其': 'Turkey',
            '厄瓜多尔': 'Ecuador',
            '科特迪瓦': 'Ivory Coast',
            '库拉索': 'Curaçao',
            '伊朗': 'Iran',
            '比利时': 'Belgium',
            '埃及': 'Egypt',
            '新西兰': 'New Zealand',
            '沙特阿拉伯': 'Saudi Arabia',
            '沙特': 'Saudi Arabia',
            '乌拉圭': 'Uruguay',
        }

        en1 = cn_to_en.get(team1, team1)
        en2 = cn_to_en.get(team2, team2)

        for m in self.matches:
            t1 = m.get('team1', '')
            t2 = m.get('team2', '')
            if (en1 in t1 or en1 in t2) and (en2 in t1 or en2 in t2):
                return m

        return None

    # ─── 进球者分析 ─────────────────────────────────

    def goals_in_match(self, match: dict) -> list[dict]:
        """提取一场比赛所有进球详情"""
        goals = []
        for side, team_key in [('goals1', 'team1'), ('goals2', 'team2')]:
            for g in match.get(side, []):
                goals.append({
                    'name': g['name'],
                    'name_cn': cn_name(g['name']),
                    'minute': g.get('minute', '?'),
                    'team': match.get(team_key, '?'),
                    'penalty': g.get('penalty', False),
                    'owngoal': g.get('owngoal', False),
                    'offset': g.get('offset', 0),
                })
        return sorted(goals, key=lambda x: (
            str(x['minute']).replace('+', '').replace("'", ''),
            x.get('offset', 0)
        ))

    def goal_summary(self, match: dict) -> str:
        """一场比赛的进球摘要 (中文)"""
        goals = self.goals_in_match(match)
        if not goals:
            return "无进球"
        lines = []
        for g in goals:
            tag = ''
            if g['penalty']:
                tag += '(点球)'
            if g['owngoal']:
                tag += '(乌龙)'
            lines.append(f"{g['name_cn']} {g['minute']}'{tag} [{g['team']}]")
        return ' | '.join(lines)

    # ─── 积分榜计算 ─────────────────────────────────

    def group_standings(self, group: str) -> list[dict]:
        """计算小组积分榜 (仅含已完赛比赛)"""
        teams: dict[str, dict] = {}
        group_matches = [m for m in self._by_group.get(group, []) if 'score' in m]

        for m in group_matches:
            t1, t2 = m['team1'], m['team2']
            s1, s2 = m['score']['ft']

            for t in [t1, t2]:
                if t not in teams:
                    teams[t] = {'name': t, 'played': 0, 'w': 0, 'd': 0, 'l': 0,
                                'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}

            teams[t1]['played'] += 1
            teams[t2]['played'] += 1
            teams[t1]['gf'] += s1
            teams[t1]['ga'] += s2
            teams[t2]['gf'] += s2
            teams[t2]['ga'] += s1

            if s1 > s2:
                teams[t1]['w'] += 1
                teams[t1]['pts'] += 3
                teams[t2]['l'] += 1
            elif s2 > s1:
                teams[t2]['w'] += 1
                teams[t2]['pts'] += 3
                teams[t1]['l'] += 1
            else:
                teams[t1]['d'] += 1
                teams[t2]['d'] += 1
                teams[t1]['pts'] += 1
                teams[t2]['pts'] += 1

        for t in teams.values():
            t['gd'] = t['gf'] - t['ga']

        return sorted(teams.values(), key=lambda x: (-x['pts'], -x['gd'], -x['gf']))

    def print_standings(self, group: str) -> str:
        """打印小组积分榜"""
        s = self.group_standings(group)
        lines = [f"=== {group} ==="]
        for i, t in enumerate(s):
            lines.append(f"  {i+1}. {t['name']}  {t['played']}场 {t['pts']}分 "
                         f"({t['w']}W {t['d']}D {t['l']}L) GF:{t['gf']} GA:{t['ga']} GD:{t['gd']:+.0f}")
        return '\n'.join(lines)

    # ─── 复盘: 预测 vs 实际 ─────────────────────────

    def extract_predictions_from_file(self, md_path: str) -> list[dict]:
        """从预测 .md 文件中提取原始预测 (表格格式)

        支持两种表格式:
          1) 赛程总表: | 场次 | 北京时间 | 比赛 | 小组 | 场地 |
          2) 预测总表: | 场次 | 北京时间 | 比赛 | 预测比分 | 半场 | 冷门风险 | 胜率估算 |
        """
        predictions = []
        try:
            text = Path(md_path).read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"⚠️ 文件未找到: {md_path}")
            return predictions

        # 策略: 逐行解析, 跳过标题行和分隔行
        lines = text.split('\n')
        in_table = False
        for line in lines:
            line = line.strip()
            if not line.startswith('|'):
                in_table = False
                continue

            # 跳过表头分隔行
            if re.match(r'^\|[\s\-:]+\|', line) or '---' in line:
                in_table = True
                continue

            # 检测是否是预测总表 (表头含"预测比分")
            if '预测比分' in line or '预测' in line:
                in_table = True
                continue
            # 检测是否是赛程总表
            if '小组' in line and '场地' in line:
                in_table = True
                continue

            if not in_table:
                continue

            cells = [c.strip() for c in line.split('|')]
            # 去掉首尾空元素
            cells = [c for c in cells if c]

            if len(cells) < 5:
                continue

            # 第1列: 场次 (数字)
            if not cells[0].isdigit():
                continue

            num = int(cells[0])

            # 第2列: 时间 (含冒号)
            time_val = cells[1] if ':' in cells[1] else ''

            # 第3列: 比赛对阵 (含 vs)
            matchup = cells[2] if 'vs' in cells[2].lower() else ''
            if not matchup:
                continue

            # 分割对阵
            parts = re.split(r'\s+vs\s+', matchup, flags=re.IGNORECASE)
            if len(parts) != 2:
                continue

            team1, team2 = parts[0].strip(), parts[1].strip()

            # 第4列: 预测比分 (如果是预测总表)
            pred = ''
            if len(cells) >= 4 and cells[3] and ('-' in cells[3] or '胜' in cells[3]):
                pred = cells[3]
            elif len(cells) >= 5 and cells[4] and ('-' in cells[4] or '胜' in cells[4]):
                pred = cells[4]

            if not pred:
                # 可能是赛程总表, 跳过
                continue

            predictions.append({
                'num': num,
                'time': time_val,
                'team1': team1,
                'team2': team2,
                'prediction': pred,
                'source': str(md_path),
            })

        return predictions

    def compare_predictions(self, md_path: str) -> list[dict]:
        """对比预测文件 vs 实际结果"""
        predictions = self.extract_predictions_from_file(md_path)
        results = []

        for pred in predictions:
            pred_str_val = pred.get('prediction', '?')
            match = self.find_match(pred['team1'], pred['team2'])
            if not match:
                results.append({
                    'date': '',
                    'team1': pred['team1'],
                    'team2': pred['team2'],
                    'group': '?',
                    'predicted': pred_str_val,
                    'actual': 'NOT FOUND',
                    'actual_full': 'NOT FOUND',
                    'goals': '',
                    'direction_correct': None,
                    'score_correct': False,
                })
                continue

            score = match.get('score', {})
            if 'ft' not in score:
                results.append({
                    'date': match.get('date', ''),
                    'team1': pred['team1'],
                    'team2': pred['team2'],
                    'group': match.get('group', ''),
                    'predicted': pred_str_val,
                    'actual': 'TBD',
                    'actual_full': 'TBD',
                    'goals': '',
                    'direction_correct': None,
                    'score_correct': False,
                })
                continue

            ft = score['ft']
            # 判断实际比分中 pred_team1 是 JSON 中的 team1 还是 team2
            json_team1 = match.get('team1', '')
            json_team2 = match.get('team2', '')

            # 用模糊匹配判断预测的team1对应JSON中的哪一边
            cn_to_en = {
                '葡萄牙': 'Portugal', '乌兹别克斯坦': 'Uzbekistan',
                '英格兰': 'England', '加纳': 'Ghana',
                '克罗地亚': 'Croatia', '巴拿马': 'Panama',
                '哥伦比亚': 'Colombia', '刚果民主共和国': 'DR Congo', '刚果金': 'DR Congo', '刚果': 'DR Congo',
                '阿根廷': 'Argentina', '法国': 'France', '挪威': 'Norway',
                '塞内加尔': 'Senegal', '伊拉克': 'Iraq', '奥地利': 'Austria',
                '约旦': 'Jordan', '阿尔及利亚': 'Algeria', '巴西': 'Brazil',
                '摩洛哥': 'Morocco', '苏格兰': 'Scotland', '海地': 'Haiti',
                '德国': 'Germany', '西班牙': 'Spain', '美国': 'USA',
                '墨西哥': 'Mexico', '捷克': 'Czech Republic', '韩国': 'South Korea',
                '南非': 'South Africa', '日本': 'Japan', '瑞典': 'Sweden',
                '荷兰': 'Netherlands', '突尼斯': 'Tunisia', '加拿大': 'Canada',
                '瑞士': 'Switzerland', '卡塔尔': 'Qatar', '波黑': 'Bosnia & Herzegovina',
                '澳大利亚': 'Australia', '巴拉圭': 'Paraguay', '土耳其': 'Turkey',
            }
            en1 = cn_to_en.get(pred['team1'], pred['team1'])
            en2 = cn_to_en.get(pred['team2'], pred['team2'])

            # 判断pred_team1在JSON中是哪个队
            pred_t1_is_json_t1 = (en1.lower() in json_team1.lower() or json_team1.lower() in en1.lower())

            # 从预测角度构建实际比分
            if pred_t1_is_json_t1:
                actual_str = f"{ft[0]}-{ft[1]}"
                a1, a2 = ft[0], ft[1]
            else:
                actual_str = f"{ft[1]}-{ft[0]}"
                a1, a2 = ft[1], ft[0]

            goals = self.goal_summary(match)

            # 判断方向
            dir_correct = self._check_direction_ordered(pred_str_val, a1, a2)

            results.append({
                'date': match.get('date', ''),
                'team1': pred['team1'],
                'team2': pred['team2'],
                'group': match.get('group', ''),
                'predicted': pred_str_val,
                'actual': actual_str,
                'actual_full': f"{a1}-{a2} (HT: {score.get('ht', ['?','?'])[0] if pred_t1_is_json_t1 else score.get('ht', ['?','?'])[1]}-{score.get('ht', ['?','?'])[1] if pred_t1_is_json_t1 else score.get('ht', ['?','?'])[0]})",
                'goals': goals,
                'direction_correct': dir_correct,
                'score_correct': pred_str_val.strip() == actual_str or self._check_score_match(pred_str_val, actual_str),
            })

        return results

    @staticmethod
    def _check_score_match(pred_str: str, actual_str: str) -> bool:
        """检查预测比分是否与实际比分匹配 (宽松匹配)"""
        # 提取预测中的分数
        score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', pred_str)
        if not score_match:
            return False
        p_score = f"{score_match.group(1)}-{score_match.group(2)}"
        return p_score == actual_str

    @staticmethod
    def _check_direction_ordered(pred_str: str, a1: int, a2: int) -> bool:
        """判断方向：pred_str以预测的team1视角，a1/a2是同一视角的实际比分"""
        score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', pred_str)
        if not score_match:
            return False

        # 如果预测以"平局"开头
        starts_draw = pred_str.strip().startswith('平局')

        try:
            p1, p2 = int(score_match.group(1)), int(score_match.group(2))
        except ValueError:
            return False

        # 预测结果: team1 胜/平/负
        if starts_draw or p1 == p2:
            pred_result = 'draw'
        elif p1 > p2:
            pred_result = 'win'
        else:
            pred_result = 'lose'

        # 实际结果
        if a1 > a2:
            actual_result = 'win'
        elif a1 == a2:
            actual_result = 'draw'
        else:
            actual_result = 'lose'

        return pred_result == actual_result

    def print_comparison_report(self, results: list[dict]) -> str:
        """生成复盘报告文本"""
        lines = []
        total = len(results)
        completed = [r for r in results if r.get('direction_correct') is not None]
        dir_ok = sum(1 for r in completed if r['direction_correct'])
        score_ok = sum(1 for r in completed if r['score_correct'])

        lines.append(f"## 预测复盘 (Auto-generated by openfootball_data.py)")
        lines.append(f"")
        lines.append(f"方向准确率: {dir_ok}/{len(completed)} ({dir_ok/max(len(completed),1)*100:.0f}%)")
        lines.append(f"比分命中率: {score_ok}/{len(completed)} ({score_ok/max(len(completed),1)*100:.0f}%)")
        lines.append(f"")

        for r in results:
            status = 'TBD' if r['direction_correct'] is None else (
                '✅' if r['direction_correct'] else '❌'
            )
            score_mark = '🎯' if r['score_correct'] else ''
            lines.append(f"| {status} {score_mark} | **{r['team1']} vs {r['team2']}** | "
                         f"预测 {r['predicted']} | 实际 **{r['actual']}** | {r.get('group','?')} |")
            if r.get('goals'):
                lines.append(f"| | 进球: {r['goals']} |")

        return '\n'.join(lines)

    # ─── 球员查询 ───────────────────────────────────

    def get_team_squad(self, team_name: str) -> Optional[dict]:
        """获取某队26人大名单"""
        # 尝试精确匹配
        for s in self.squads:
            if s['name'].lower() == team_name.lower():
                return s
        # 模糊匹配
        for s in self.squads:
            if team_name.lower() in s['name'].lower() or s['name'].lower() in team_name.lower():
                return s
        # 按fifa_code
        if len(team_name) == 3:
            for s in self.squads:
                if s.get('fifa_code', '').upper() == team_name.upper():
                    return s
        return None

    def find_player(self, name: str, team: str = None) -> Optional[dict]:
        """在squads中搜索球员"""
        name_lower = name.lower()
        squads_to_search = [self.get_team_squad(team)] if team else self.squads
        for squad in squads_to_search:
            if not squad:
                continue
            for p in squad.get('players', []):
                if name_lower in p['name'].lower():
                    return {**p, 'team': squad['name']}
        return None

    # ─── 统计 ───────────────────────────────────────

    def top_scorers(self, min_goals: int = 2) -> list[dict]:
        """射手榜"""
        tally: dict[str, dict] = {}
        for m in self._completed:
            for side in ['goals1', 'goals2']:
                for g in m.get(side, []):
                    if g.get('owngoal'):
                        continue
                    name = g['name']
                    if name not in tally:
                        tally[name] = {'name': name, 'name_cn': cn_name(name), 'goals': 0, 'penalties': 0}
                    tally[name]['goals'] += 1
                    if g.get('penalty'):
                        tally[name]['penalties'] += 1

        return sorted(
            [v for v in tally.values() if v['goals'] >= min_goals],
            key=lambda x: -x['goals']
        )

    def stats_summary(self) -> dict:
        """全局统计"""
        total = len(self._completed)
        total_goals = sum(
            len(m.get('goals1', [])) + len(m.get('goals2', []))
            for m in self._completed
        )
        draws = sum(1 for m in self._completed
                    if m['score']['ft'][0] == m['score']['ft'][1])
        home_wins = sum(1 for m in self._completed
                        if m['score']['ft'][0] > m['score']['ft'][1])

        return {
            'matches_played': total,
            'total_goals': total_goals,
            'goals_per_match': round(total_goals / max(total, 1), 2),
            'draws': draws,
            'draw_pct': round(draws / max(total, 1) * 100, 1),
            'home_wins': home_wins,
        }


# ─── 历史分析引擎 ─────────────────────────────────────

class WorldCupHistory:
    """加载全部世界杯年份数据，进行历史分析"""

    def __init__(self):
        self.years: dict[int, WorldCupData] = {}
        for year_dir in sorted(DATA_DIR.iterdir()):
            if year_dir.is_dir() and year_dir.name.isdigit():
                try:
                    y = int(year_dir.name)
                    self.years[y] = None  # lazy load
                except ValueError:
                    pass

    def load_year(self, year: int) -> Optional[WorldCupData]:
        """懒加载某一年"""
        if year not in self.years:
            return None
        if self.years[year] is None:
            try:
                self.years[year] = WorldCupData(year)
            except Exception as e:
                print(f"⚠️ 加载 {year} 失败: {e}")
                self.years[year] = None
        return self.years[year]

    def available_years(self) -> list[int]:
        return sorted([y for y, v in self.years.items() if v is not None or
                       (DATA_DIR / str(y) / 'worldcup.json').exists()])

    def find_upsets(self, year: int, min_rank_gap: int = 20) -> list[dict]:
        """
        查找冷门比赛 (基于进球差预测 vs 实际)
        简化版: 如果强队预期净胜≥2球但实际平局或输球 → 冷门
        """
        wc = self.load_year(year)
        if not wc:
            return []

        upsets = []
        for m in wc.completed():
            ft = m['score']['ft']
            gd = abs(ft[0] - ft[1])

            # 简单冷门定义: 零封平局 (0-0) 即视为潜在冷门
            if ft[0] == 0 and ft[1] == 0:
                upsets.append({
                    'date': m['date'],
                    'match': f"{m['team1']} 0-0 {m['team2']}",
                    'group': m.get('group', ''),
                    'type': 'goalless_draw',
                    'round': m.get('round', ''),
                })

        return upsets

    def score_distribution(self, year: int = None) -> dict[str, int]:
        """比分分布统计 (支持多届合并)"""
        years = [year] if year else [y for y in self.years.keys() if self.load_year(y)]
        dist: dict[str, int] = {}

        for y in years:
            wc = self.load_year(y)
            if not wc:
                continue
            for m in wc.completed():
                s = m['score']['ft']
                key = f"{s[0]}-{s[1]}"
                dist[key] = dist.get(key, 0) + 1

        return dict(sorted(dist.items(), key=lambda x: -x[1]))

    def goals_per_tournament_trend(self) -> list[dict]:
        """每届世界杯场均进球趋势"""
        trend = []
        for year in sorted(self.years.keys()):
            wc = self.load_year(year)
            if wc:
                s = wc.stats_summary()
                trend.append({'year': year, **s})
        return trend


# ─── 命令行入口 ──────────────────────────────────────

if __name__ == '__main__':
    import sys
    import io
    # Fix GBK encoding on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\n用法:")
        print("  python openfootball_data.py 2026              # 打印2026概览")
        print("  python openfootball_data.py 2026 --standings  # 打印全部小组积分榜")
        print("  python openfootball_data.py 2026 --scorers    # 射手榜")
        print("  python openfootball_data.py 2026 --review复盘文件.md  # 复盘")
        print("  python openfootball_data.py --history         # 历史趋势")
        sys.exit(0)

    year = 2026
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        year = int(sys.argv[1])

    wc = WorldCupData(year)
    print(f"=== {wc.name} === 已赛{wc.stats_summary()['matches_played']}场 | 场均进球{wc.stats_summary()['goals_per_match']} ===")

    if '--standings' in sys.argv:
        for g in sorted(wc._by_group.keys()):
            print()
            print(wc.print_standings(g))

    if '--scorers' in sys.argv:
        print("\n=== 射手榜 (≥2球) ===")
        for s in wc.top_scorers(2):
            pen_str = f" (含{s['penalties']}点球)" if s['penalties'] else ""
            print(f"  {s['name_cn']}: {s['goals']}球{pen_str}")

    if '--review' in sys.argv:
        idx = sys.argv.index('--review')
        if idx + 1 < len(sys.argv):
            md_path = sys.argv[idx + 1]
            results = wc.compare_predictions(md_path)
            print(wc.print_comparison_report(results))

    if '--history' in sys.argv:
        hist = WorldCupHistory()
        print("\n=== 世界杯历史场均进球趋势 ===")
        for t in hist.goals_per_tournament_trend():
            print(f"  {t['year']}: {t['goals_per_match']}球/场 ({t['matches_played']}场, 平局率{t['draw_pct']}%)")
