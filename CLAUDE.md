# 2026世界杯预测项目 - 项目规则

> v11.10: 合并重复规则, 修复"偷懒"根因

---

## ⏱️ 时间规范

- **所有时间统一使用北京时间 (UTC+8)**，标注为"北京时间"
- 文档生成时间也标注北京时间

---

## 📐 命名规范

### 球员名
- **所有球员名必须使用中文译名**，禁止英文名
- 不常见球员首次出现时标注: `法伊祖拉耶夫(Fayzullaev)`

### 国家名
- **国家名使用全称**，禁止缩写
- 正确: 阿根廷、葡萄牙、英格兰、克罗地亚、哥伦比亚、刚果民主共和国(刚果金)

### 比分格式
- `阿根廷 2-0 奥地利` (队名+空格+比分+空格+队名) | 半场: `上半场 1-0`
- 进球者: `梅西 38' 90+'` (中文名+分钟)

### 文件命名
- 完整版: `YYYY年M月D日_主题.md` | 手机版: `YYYY年M月D日_主题_手机版.txt`

---

## 📤 输出规范 — 每次生成必须同时输出 .md + .txt

### .md 完整版排版
1. 标题层级: `##` 主标题 -> `###` 比赛标题 -> `####` 小节
2. 表格对齐: md表格每列宽度一致, 中文字符占2个英文字符宽度
3. 重点用 `**粗体**` 标注关键结论、比分、冷门等级

### .txt 手机版排版
1. 行宽: ≤40半角字符 (约20中文字)
2. 分隔符: `=====` `------` `━━━━━`
3. 表格替代: 用 `字段: 值` 逐行格式, 对阵用 `队名 -- 胜/平/负 -- 积分`
4. 序号: 用 `[1]` `[2]`
5. 重点: 用 `*` `->` `>` 前置符号
6. 禁止: emoji国旗、复杂box-drawing、≥3列对齐表格、markdown链接
7. 结论先行 -> 分条简短 -> 底部附参数卡

---

## 📋 每次预测/复盘必须输出的内容 (唯一清单)

> **这就是全部要求，没有分散在其他地方的第二份清单。**

### [必填1] 首轮球员评分回顾
- 两队完整评分表 (中文名 + 评分 + 简要表现)
- 数据源: SportsDunia / The Guardian / SI.com(FotMob)
- 标注评分制 (10分制或FotMob 10分制)
- 高分 (>=7.5) = 关键威胁, 低分 (<=6.0) = 隐患
- 标注 MOTM 和全场最低评分

### [必填2] 因素导向表
- 每个因素标注 **对哪边有利** (方便不熟悉足球的读者)
- 格式: `| 因素 | 对哪边有利 | 理由 |`

### [必填3] 冷门风险评估
- 等级: 低 / 中 / 高 / 极高 + 具体理由

### [必填4] 比分预测
- 首选比分 + 半场比分 + 2个备选比分

### [必填5] 伤病/停赛信息
- 赛前搜索最新阵容新闻 (AnySearch)
- 包含 "已验证可用替补" 一栏

### [必填6] 强队分类标注 (新)
- 标注为: 超级巨星型 / 体系型 / 低效热门

### [必填7] 亚非球队韧性评估 (新·面对强队时)
- 5项: 低位防守/速度反击/定位球高点/前30分钟/被压制不崩盘

### [必填8] 教练博弈分析 (新)
- 落后/领先策略 + 替补改变比赛能力

### [必填9] 定位球攻防简评 (新)

### [必填10] 冷门路径说明 (新)
- 如果翻车, 最可能怎么翻?

---

## 🔬 分析原则

### 三条铁律

1. **亚非球队不低估** — 面对强队时, 亚洲/非洲球队往往防守纪律更强。不做5项韧性评估 = 不合格。
   - 案例: 英格兰 0-0 加纳 — 加纳5项全满分, 大巴战术和1986摩洛哥0-0英格兰完全一致。

2. **强队三类分法** — 超级巨星型(可高看大胜) vs 体系型(防小胜/防平局) vs 低效热门(防冷平)
   - 案例: 英格兰是体系型强队 — 凯恩被锁后无第二爆点。若赛前正确归类就不会预测2-0。

3. **禁止绝对化** — 禁用 "必胜""稳赢""一定打穿""毫无疑问""不可能输"
   - 替代: "更倾向于""大概率""主要判断""首选方向"
   - 每个结论附带: 主要不确定性 + 潜在冷门路径

### 历史基线 (openfootball 1930-2026)

| 比分 | 占比 | 含义 |
|------|------|------|
| 1-1 | 11.3% | 最常见比分 |
| 1-0 | 10.8% | 一球小胜 |
| 0-0 | 9.4% | 近1/10! |
| 2-0 | 7.3% | **比你想象的低** |

> **预测2-0的基线概率仅7.3%。1-1比2-0更常见。**

### 小组赛轮次效应

| 轮次 | 场均进球 | 0-0率 | 特征 |
|------|---------|--------|------|
| 第1轮 | 2.63 | 9.3% | 试探 |
| 第2轮 | 2.81 | **10.4%** | 高0-0! 大巴+松懈 |
| 第3轮 | 2.63 | 8.1% | 出线明朗 |

---

## 🛡️ 防幻觉自查 (生成任何内容前必须完成)

### 复盘前
```
[1] ESPN API 确认当天实际比赛 + 比分
    python -c "import urllib.request, json; ... scoreboard?dates=YYYYMMDD"
[2] Glob 搜索 + Read 原始预测文件 — 不准凭记忆!
[3] AnySearch 交叉验证比分 + 球员评分
[4] 对比原始预测 vs 实际 -> 计算准确率
[4.5] 复查: 复盘表格写的预测 = 步骤[2]读到的原始预测
[5] 所有历史比赛必须是[1][2][3]中确认过的
```

### 预测前
```
[1] ESPN API 确认当天赛程
[2] AnySearch 获取: 小组形势/伤病/场外新闻
[3] 每场比赛必须出现在[1]的返回中
[4] "之前X胜X"类引用必须来自已验证数据
```

### 赛中/半场
```
[0] 比分确认 != 大名单确认
[1] AnySearch 确认26人大名单+本场替补
[2] "建议换XX" -> XX必须在替补名单中
[3] "XX缺阵" -> 必须有搜索结果支撑
[4] 预测文档必须包含"已验证可用替补"
[5] 不确定 -> 搜, 不准猜
```

### 幻觉高危场景
- 想填"最大误判"但想不起 -> 立刻搜索
- 写"N战N胜" -> 逐日相加
- 引用"之前X-Y胜Z" -> 确认该比赛真实存在
- 表格空白想填 -> 不填, 去查
- 觉得"该有冷门" -> 数据说了算
- 推荐换人但未搜大名单 -> 不准凭常识编
- 复盘写预测但未对照原文件 -> 逐项复制

### 犯错后
1. 确认错误 2. 追溯来源 3. 修正所有文件 4. 更新本清单

---

## 🔧 数据获取工具

### 主力: AnySearch (Skill)
> 前置: 每台新机器需安装 AnySearch Skill → 见 `setup.md`
```bash
# 统一入口: 用 Skill 名调用, 不用写死路径
# Claude Code 会通过 runtime.conf 自动定位 CLI
```
日常命令:
```bash
# search:    python ~/.claude/skills/anysearch/scripts/anysearch_cli.py search "query" --max_results 5
# batch:     python ~/.claude/skills/anysearch/scripts/anysearch_cli.py batch_search --queries '[...]'
# extract:   python ~/.claude/skills/anysearch/scripts/anysearch_cli.py extract "URL"
```

### 实时: ESPN API
```bash
python -c "
import urllib.request, json
url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=15).read()
j = json.loads(data)
# ... 按需过滤
"
```
- 按日: `scoreboard?dates=YYYYMMDD`
- `status.type.state='in'` = 正在踢, `'pre'` = 未开始

### 赛后验证: openfootball JSON
> 前置: 每台新机器需 `cd data && git clone --depth 1 https://github.com/openfootball/worldcup.json.git openfootball`
```bash
python openfootball_data.py 2026 --standings    # 积分榜
python openfootball_data.py 2026 --scorers       # 射手榜
python openfootball_data.py 2026 --review "file" # 自动复盘
```

### 赛后比分: 小红书赛程页 (OpenCLI)
```bash
opencli browser xhs_live open "https://www.xiaohongshu.com/worldcup26/fixtures?wcup_source=web_sidebar_entry"
opencli browser xhs_live wait time 5
opencli browser xhs_live extract
```

---

## 📂 关键文件路径

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | 本文件 — 项目所有规则 |
| `setup.md` | 新机器初始化指南 |
| `openfootball_data.py` | 结构化数据引擎 (积分榜/复盘/射手榜) |
| `historical_analyzer.py` | 历史分析 (冷门频率/比分分布/趋势) |
| `match_analysis_template.md` | 4模块26子项标准模板 (配合 CLAUDE.md 使用) |
| `data/openfootball/` | 1930-2026 JSON (需手动 clone, 见 setup.md) |
| `latest_team_news.md` | 最新伤病/阵容汇总 |
| `historical_upset_patterns.md` | 历史冷门模式数据库 |
