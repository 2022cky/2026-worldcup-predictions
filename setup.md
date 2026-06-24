# 2026世界杯预测项目 — 新机器完整初始化指南

> 适用: Windows / macOS / Linux
> 预计时间: 15 分钟
> 前置: 已安装 Python 3.6+, Git, Claude Code

---

## 0. 前置检查

开始之前, 确认以下工具可用:

```bash
python --version     # 需要 >= 3.6
git --version        # 任意版本
claude --version     # Claude Code CLI
```

如果缺 Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

---

## 1. 克隆项目

```bash
git clone https://github.com/2022cky/2026-worldcup-predictions.git
cd 2026-worldcup-predictions
```

克隆后你应该看到:
```
CLAUDE.md
openfootball_data.py
historical_analyzer.py
match_analysis_template.md
setup.md          # 就是本文件
.gitignore
```

---

## 2. 获取比赛数据库

openfootball 是独立的开源项目, 包含 1930-2026 全部世界杯结构化数据。它不在本项目 git 仓库中, 需要单独 clone。

```bash
mkdir -p data
cd data
git clone --depth 1 https://github.com/openfootball/worldcup.json.git openfootball
cd ..
```

> `--depth 1` 只拉最新版本, 节省空间 (~1.1MB)。

验证:
```bash
python openfootball_data.py 2026 --standings
```

预期输出:
```
=== World Cup 2026 === 已赛XX场 | 场均进球X.XX ===
=== Group A ===
  1. Mexico  2场 6分 ...
```

如果报错 `data/openfootball/2026/worldcup.json not found`:
```bash
ls data/openfootball/2026/worldcup.json   # 确认文件存在
# 如果不存在, 重新执行步骤2的 git clone
```

---

## 3. 安装 AnySearch Skill

AnySearch 是 Claude Code 的搜索插件, 用于获取:
- 赛前阵容 / 伤病 / 停赛新闻
- 赛后球员评分
- 战术分析文章
- FIFA 官方数据

### 3.1 下载并解压

```bash
# Linux / macOS
curl -L -o /tmp/anysearch-skill.zip \
  https://github.com/anysearch-ai/anysearch-skill/archive/refs/tags/v2.1.0.zip
unzip -o /tmp/anysearch-skill.zip -d /tmp/
mv /tmp/anysearch-skill-* ~/.claude/skills/anysearch

# Windows PowerShell
# Invoke-WebRequest -Uri "https://github.com/anysearch-ai/anysearch-skill/archive/refs/tags/v2.1.0.zip" -OutFile "$env:TEMP\anysearch-skill.zip"
# Expand-Archive -Path "$env:TEMP\anysearch-skill.zip" -DestinationPath "$env:TEMP" -Force
# Move-Item -Path "$env:TEMP\anysearch-skill-*" -Destination "$env:USERPROFILE\.claude\skills\anysearch"
```

### 3.2 (推荐) 配置 API Key

不用 Key 也能用, 但免费 Key 提供更高限额。

1. 访问 https://anysearch.com/console/api-keys
2. 注册并获取 Key
3. 写入配置:

```bash
# Linux / macOS
echo "ANYSEARCH_API_KEY=你的key" > ~/.claude/skills/anysearch/.env

# Windows PowerShell
# "ANYSEARCH_API_KEY=你的key" | Out-File -FilePath "$env:USERPROFILE\.claude\skills\anysearch\.env" -Encoding utf8
```

### 3.3 验证

```bash
python ~/.claude/skills/anysearch/scripts/anysearch_cli.py search "World Cup 2026 test" --max_results 2
```

预期输出: 搜索结果列表 (JSON 格式)。

---

## 4. Claude Code 配置 (可选)

本项目 `.claude/settings.json` 已预设权限, clone 后自动生效。

如果需要调整:
```bash
claude config              # 交互式配置
# 或手动编辑 .claude/settings.json
```

> `.claude/settings.local.json` 包含本机特定路径, 已在 `.gitignore` 中, 不会上传。

---

## 5. 完整验证

按顺序运行以下命令, 全部成功则配置完毕:

```bash
# 1) 数据库引擎
python openfootball_data.py 2026 --standings | head -5

# 2) 射手榜
python openfootball_data.py 2026 --scorers | head -10

# 3) 历史分析
python historical_analyzer.py --trends

# 4) 自动复盘 (如已有预测文件)
python openfootball_data.py 2026 --review "复盘6月23日_预测6月24日.md"
```

---

## 6. 日常使用流程

### 每天赛前
```
在 Claude Code 中:
  "搜索今天世界杯阵容新闻和伤病信息"
  -> 自动调用 AnySearch + ESPN API
  -> 输出 latest_team_news.md
```

### 赛后复盘
```bash
python openfootball_data.py 2026 --review "预测文件.md"
# 自动提取文件中的预测, 对比 openfootball JSON 中的实际比分,
# 输出方向准确率/比分命中率/每场详情
```

### 更新数据库
```bash
cd data/openfootball && git pull && cd ../..
# openfootball 社区会在赛后几小时内更新比分+进球者
```

### 更新 AnySearch
```bash
# 查看最新版本: https://github.com/anysearch-ai/anysearch-skill/releases
# 重复步骤 3.1, 用新 tag
```

---

## 7. 常见问题

### Q: `python` 命令不存在?
```bash
python3 --version              # macOS/Linux 尝试 python3
# 如果 python3 可用, 后续命令替换 python 为 python3
```

### Q: `openfootball_data.py` 报 GBK 编码错误?
```bash
# Windows 特有, 代码已内置修复 (sys.stdout UTF-8 wrapper)
# 如果仍报错: chcp 65001  (切换终端到 UTF-8)
```

### Q: AnySearch 搜索无结果?
```bash
# 检查网络: ping api.anysearch.com
# 检查 Key: cat ~/.claude/skills/anysearch/.env
# 匿名模式有更低限额, 可能需要注册 Key
```

### Q: data/openfootball 目录被误删?
```bash
cd data
git clone --depth 1 https://github.com/openfootball/worldcup.json.git openfootball
cd ..
```

### Q: 另一台机器已经 clone 过 openfootball, 能复制吗?
```bash
# 可以, 直接复制整个 data/openfootball 目录过去
scp -r data/openfootball user@new-machine:~/2026-worldcup-predictions/data/
```

---

## 目录结构 (配置完成后)

```
2026-worldcup-predictions/
├── CLAUDE.md                    # 项目规则 — 所有行为准则
├── setup.md                     # 本文件 — 新机器初始化指南
├── openfootball_data.py         # 数据引擎 (积分榜/射手榜/复盘)
├── historical_analyzer.py       # 历史分析 (冷门频率/比分分布/趋势)
├── match_analysis_template.md   # 深度分析模板
├── .claude/
│   ├── settings.json            # 权限配置 (仓库内, 通用)
│   └── settings.local.json      # 本机配置 (gitignore, 不上传)
├── data/
│   └── openfootball/            # 1930-2026 JSON (手动 clone)
├── *.md                         # 预测 / 复盘 / 分析文档
└── *_手机版.txt                  # 手机版同步输出
```
