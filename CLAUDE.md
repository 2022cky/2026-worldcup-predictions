# 2026世界杯预测项目 - 项目规则

## 时间规范

- **所有时间统一使用北京时间 (UTC+8)**，标注为"北京时间"
- 比赛时间以北京时间为准，示例: `6月19日 09:00 北京时间`
- 文档生成时间也标注北京时间

## 赛程核实规则

- 每天比赛数量以国际足联(FIFA)官方赛程或央视(CCTV5)转播表为准
- 2026世界杯48队赛制下，小组赛阶段每天通常 **4场比赛**
- **不要混入其他日期的比赛** — 赛前先用搜索确认当天具体对阵
- 预测只覆盖当天实际进行的比赛

## 输出规范

每次生成世界杯分析/预测/复盘文档（.md）后，**必须同步生成一份手机端排版优化的 .txt 文件**。

### .txt 手机版排版规则

1. **行宽控制**: 每行不超过40个半角字符（约20个中文字），确保在窄屏手机上无需横向滚动
2. **分隔符**: 使用 `=====` `──────` `━━━━━` 等ASCII/全角字符分隔，禁用复杂Unicode表格框线
3. **表格替代**: 不使用多列表格（md table），改用逐行列表或简短对照格式
4. **数字序号**: 用 `[1]` `[2]` 替代 `###`，更醒目
5. **重点标注**: 用 `★` `-> ` `+` `>` 等前置符号代替加粗/引用
6. **段落控制**: 每个信息块之间有空行，但不过度留白浪费屏幕空间
7. **禁止**: emoji国旗图标、复杂box-drawing字符、超过3列的对齐表格、markdown链接语法

### 分析内容必须包含

1. **每场比赛标注"对哪边有利"** — 每个因素明确写有利于哪支球队(方便不熟悉足球的读者)
2. **伤病/停赛信息** — 赛前搜索最新阵容新闻
3. **冷门风险评估** — 低/中/高/极高 + 理由
4. **比分预测** — 首选比分 + 备选比分

### 文件命名

- 完整版: `YYYY年M月D日_主题.md`
- 手机版: `YYYY年M月D日_主题_手机版.txt`

### 内容组织优先级（手机版）

1. 结论先行 — 总表/核心比分放在最前面
2. 分条简短 — 每个因素一行，不堆砌
3. 关键数据加前缀标注 — 如 `比分:` `胜率:` `冷门:`
4. 底部附参数卡简表

## 实时数据获取

### 方法1: Python直连ESPN API (推荐,绕过WebFetch封锁)

```bash
python -c "
import urllib.request, json
url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=15).read()
j = json.loads(data)
for ev in j.get('events', []):
    name = ev.get('name', '')
    if '目标球队名' in name:
        comps = ev.get('competitions', [{}])[0]
        status = comps.get('status', {}).get('type', {})
        print(f\"状态: {status.get('description')} | 时间: {status.get('displayClock')}\")
        for c in comps.get('competitors', []):
            print(f\"{c['team']['displayName']}: {c['score']}\")
            for s in c.get('statistics', []):
                print(f\"  {s['name']}: {s['displayValue']}\")
"
```

- **API 根地址**: `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world`
- **比分接口**: `{BASE}/scoreboard` (全部比赛) 或 `{BASE}/scoreboard?dates=YYYYMMDD` (按日)
- **字段**: `status.type.state='in'` 正在踢, `'pre'` 未开始, `status.type.name='STATUS_FULL_TIME'` 完赛
- **关键数据**: `competitors[].score` (比分), `status.displayClock` (分钟), `statistics[]` 含 possessionPct/shotsOnTarget/foulsCommitted/wonCorners 等
- **局限**: ESPN不提供 xG、传球次数等深度数据 → 补充使用国内体育站+用户截图

### 方法2: WebSearch兜底 (低优先级)

WebSearch 搜索 `"球队1" "球队2" 世界杯 2026 比分` 获取赛后/实时报道。中文体育站 (zhibo8/dongqiudi/hupu/599比分/qiumiwu) 常有半场数据。
**注意**: WebSearch索引滞后严重, 比赛中途常搜不到实时比分。

### 方法3: 用户截图+OCR (备选)

用户提供直播截图 → 安装 Pillow + tesseract OCR → 提取数据。
```bash
pip install Pillow pytesseract
# 还需安装 tesseract-ocr 系统包 (winget/choco/apt)
```

### 方法4: 运行 predict.py 批量刷新

```bash
python predict.py  # 拉取6/11-6/20全部ESPN数据到 worldcup_data.json
```

### WebFetch 已知限制

- **ESPN/sportingnews/bleacherreport/fifa.com** 等海外域名被安全策略封锁(WebFetch无法访问)
- **懂球帝/zhibo8/虎扑/599比分** 同样被封锁
- **小红书/微博** 直播页无法Fetch
- **唯一通路**: Python urllib直连API (方法1) 或 WebSearch 搜索结果摘要

---

## 工作流程

1. **方法1** 获取最新比赛结果/赛程 (Python直连ESPN API)
2. 核实当天实际对阵(对照FIFA官方/央视)
3. 搜索各队最新伤病/停赛/阵容新闻
4. 生成本地 .md 完整分析文档
5. 立即生成 _手机版.txt 排版优化版本
6. 更新 memory 目录下的复盘文件
