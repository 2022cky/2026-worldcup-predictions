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

### 方法4: 小红书世界杯赛程页 (OpenCLI浏览器控制 — 推荐赛后核实)

> **2026.06.23 修正** — 直播页需登录,改用**赛程页**直接抓取所有完赛比分

```bash
# 前置: OpenCLI Chrome扩展已安装且Chrome打开
# 安装: npm install -g @jackwener/opencli
# 扩展: 从 https://github.com/jackwener/opencli/releases 下载解压 → chrome://extensions 加载
# 验证: opencli doctor → 显示 [OK] Extension: connected

# 步骤1: 打开世界杯赛程页(无需登录,所有完赛比分直接可见)
opencli browser xhs_live open "https://www.xiaohongshu.com/worldcup26/fixtures?wcup_source=web_sidebar_entry"

# 步骤2: 等待数据加载
opencli browser xhs_live wait time 5

# 步骤3: 提取全部赛程数据(含比分/队名/比赛状态/预约人数)
opencli browser xhs_live extract
```

**赛程页数据包含**:
- ✅ 所有已完赛比赛的**比分** (如"挪威 3-1 塞内加尔")
- ✅ 比赛状态 (已完赛显示比分, 未赛显示"---" + 预约人数)
- ✅ 比赛标题 (如"哈兰德对阵马内")
- ✅ 分组/轮次标注 (如"I组第二轮")
- ✅ 开赛时间 (如"08:00")
- ❌ 不含实时控球率/射门等深度统计数据(赛后才更新)
- ❌ 不含换人/红黄牌事件线

**与ESPN API互补**: ESPN API有实时stats但编码问题常见; 小红书赛程页是**最可靠的赛后比分来源**(中文+结构化)。

### 方法4B: 小红书世界杯首页 → 点击直播卡片 (赛中实时数据)

> 如果比赛正在进行中,赛程页可能不显示实时比分 → 用此方法进入直播间

```bash
# 步骤1: 打开世界杯首页
opencli browser xhs_live open "https://www.xiaohongshu.com/worldcup26?wcup_source=web_sidebar_entry"

# 步骤2: 等待加载
opencli browser xhs_live wait time 5

# 步骤3: 找到正在进行的比赛卡片 → 点击"点击进入直播间"按钮
opencli browser xhs_live state    # 搜索 "直播中" 或 "挪威 vs 塞内加尔" 找到按钮索引
opencli browser xhs_live click <按钮索引>

# 步骤4: 等待直播加载 → 提取
opencli browser xhs_live wait time 5
opencli browser xhs_live extract
```

### 方法5: 运行 predict.py 批量刷新

```bash
python predict.py --date 20260623    # 预测单天
python predict.py --all              # 拉取+预测+复盘+回测
python predict.py --review           # 复盘最近完赛
```

### WebFetch 已知限制

- **ESPN/sportingnews/bleacherreport/fifa.com** 等海外域名被安全策略封锁(WebFetch无法访问)
- **懂球帝/zhibo8/虎扑/599比分** 同样被封锁
- **小红书/微博** 直播页WebFetch无法抓取动态JS内容
- **解决方案**: 方法1(Python API) + 方法4(OpenCLI赛程页) + WebSearch 搜索结果摘要

---

## 工作流程

### 自动化部分 (predict.py v11)
```bash
python predict.py --date 20260621    # 预测单天(跨UTC日期拉全4场)
python predict.py --all              # 拉取+预测+复盘+回测
python predict.py --review           # 复盘最近完赛
python predict.py --fetch-only       # 仅拉取数据到 worldcup_data.json
```

predict.py 自动完成:
1. 跨UTC日期查询 (北京时间 d → UTC d-1和UTC d两个日期)
2. 分类: 已完赛/进行中/未赛
3. v9.1模型8维度评分 + R1-R15全部规则 + 教练战术
4. **v11.1 半场修正模式**: 检测到进行中比赛(live)自动运行
   - 提取半场实时数据(控球率/射门/射正/角球/犯规/比分)
   - 调用 `predict_halftime()` 5条修正规则(A1-A5)
   - 输出 `_半场修正预测_{对阵}.md` + `_手机版.txt`
5. 赛前预测: 输出 .md + _手机版.txt + worldcup_data.json
6. 复盘模式: 对比预测vs实际 + 写入 memory_backup/

### 手动增强部分 (Claude 负责)
1. **赛前2小时内**: WebSearch获取首发阵容 → 与预测对比,差异大则更新
2. **半场/赛中实时预测**:
   - ⚠️ **必须先拉大名单**: WebSearch搜索"{球队1} {球队2} 首发阵容 替补" → 确认可用球员
   - **禁止**在未验证大名单的情况下推荐替补球员上场或战术调整
   - 任何"换谁上"的建议,该球员必须确认在大名单且在替补席
3. **完赛后**: WebSearch获取详细统计(ESPN API stats字段不全)
4. **冷门预警**: 赛前WebSearch搜索突发伤病/场外新闻
5. **深度复盘**: 分析v9.1误差原因 → 更新 MODEL_RULES.md 参数
6. **记忆同步**: 关键发现写入 memory/ 目录

---

## 🛡️ 防幻觉自查清单 (每次复盘/预测前强制执行)

> ⚠️ **铁律: 禁止凭记忆或"合理推测"编造任何比赛结果、比分、对阵信息。**
> 6月21日复盘中出现"丹麦0-0中国"幻觉——该比赛从未发生。

### 复盘自查 (生成任何复盘内容前)

按顺序完成以下验证，**未完成禁止输出**:

```
[1] 拉取 ESPN API 确认当天实际比赛列表和比分
    python -c "import urllib.request, json; ... scoreboard?dates=YYYYMMDD"
[2] 用 Glob 搜索已有的当天复盘文件 (如 2026年M月D日_复盘*.md)
    如果已有复盘文件 → 以文件中的数据为唯一事实来源
[3] 用 WebSearch 搜索 "{日期} 世界杯 比赛结果 比分" 交叉验证
[4] 对比 predict.py 的预测 vs 实际 → 计算方向/比分准确率
[5] 所有列出的历史比赛必须是步骤[1][2][3]中实际确认过的
```

### 预测自查 (生成预测内容前)

```
[1] 拉取 ESPN API 确认当天赛程 (不能自行增减比赛)
[2] WebSearch 搜索 "{日期} 世界杯 赛程 前瞻" 获取:
    - 小组形势 (积分/净胜球)
    - 伤病/阵容更新
    - 场外新闻 (签证/换帅等)
[3] 预测总表中的每场比赛必须出现在步骤[1]的API返回中
[4] 任何关于"之前比赛结果"的引用(如"首轮X胜X")必须来自已验证数据
```

### 赛中/半场实时分析自查 (新增 — 2026.06.22 比利时vs伊朗教训)

```
[0] ⚠️ 铁律: 拉实时数据 ≠ 拉阵容。比分确认 ≠ 大名单确认。
[1] WebSearch 搜索 "{球队1} {球队2} 世界杯 首发阵容 替补" → 确认26人大名单+本场替补
[2] 任何"建议换XX上场" → XX必须出现在步骤[1]的替补名单中
[3] 任何"XX缺阵/伤病" → 必须有搜索结果支撑,不准凭足球常识推断
[4] 最终版预测文档必须包含"已验证可用替补"一栏
[5] 如有疑问(某球员是否在大名单) → 搜,不准猜
```

### 复盘累计数据自查

```
[1] 累计方向准确率等统计 → 必须逐日重新计算,不得凭印象填写
[2] "最大误判"栏 → 只能填实际发生且已验证的比赛
[3] 如有疑问 → 运行 grep 搜索已有复盘文件中的统计数字
```

### 幻觉高危场景 (遇到这些信号必须暂停并验证)

- 🚨 试图填写某个日期的"最大误判"但想不起具体比赛 → **立刻搜索,不准编**
- 🚨 需要写"N战N胜"类累计统计 → **逐日相加,不准心算**
- 🚨 引用某个球队"之前X-Y战胜了Z" → **确认该比赛真实存在**
- 🚨 填写表格时某格空白→想填个"合理的"内容 → **不填,去查**
- 🚨 觉得"应该有一场冷门"来让叙述更完整 → **数据说了算,不编故事**
- 🚨 **推荐换人或提及"替补球员上场"但未搜索大名单** → 2026.06.22 比利时vs伊朗: 多库(因病缺阵)/奥蓬达(未入选) → **"XX应该上场"必须来自已验证的替补名单,不准凭足球常识编**

### 犯错后处理

如不幸出现幻觉并被发现:
1. 立刻确认错误,不辩解
2. 追溯幻觉来源 (是记忆错误？WebSearch误导？)
3. 修正所有受影响文件
4. 更新本清单 (防止同类错误重现)
