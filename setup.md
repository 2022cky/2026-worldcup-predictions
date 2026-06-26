# 2026世界杯预测项目 — 新机器完整初始化指南

> 适用: Windows / macOS / Linux
> 预计时间: 20 分钟
> 前置: Python 3.6+, Git, Claude Code

---

## ⚠️ 先理解：为什么 git clone 不够

本项目依赖**两套存储**，git 只管其中之一：

```
┌─ Git 仓库 (跨机器同步) ─────────────────────┐
│  E:\ai\世界杯\                               │
│  ├── CLAUDE.md          ← 项目规则（核心）     │
│  ├── memory_backup/     ← 记忆备份（14个文件） │
│  ├── match_analysis_template.md                │
│  ├── historical_upset_patterns.md              │
│  ├── MODEL_RULES.md                           │
│  ├── predict.py / openfootball_data.py / ...   │
│  └── data/openfootball/  ← 需单独 clone       │
└──────────────────────────────────────────────┘

┌─ Claude Code 持久记忆 (每台机器独立) ────────┐
│  C:\Users\...\memory\                         │
│  ├── MEMORY.md          ← 索引（AI读取入口）   │
│  ├── project-overview.md                       │
│  ├── model-evolution.md                        │
│  ├── june-17-review.md ~ june-21-22-predictions.md │
│  └── ...                                       │
└──────────────────────────────────────────────┘
```

**git clone 后，持久记忆是空的。** Claude Code 读不到项目历史，每次都得从零开始。

**本指南的两条铁律：**
1. **新机器**: git clone → 恢复记忆到 Claude Code
2. **每次会话结束**: 新记忆 → 写回 `memory_backup/` → git commit → git push

---

## 0. 前置检查

```bash
python --version     # >= 3.6
git --version
claude --version     # Claude Code CLI
```

缺 Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

---

## 1. 克隆项目 + 初始化

### 1.1 克隆项目

```bash
git clone https://github.com/2022cky/2026-worldcup-predictions.git
cd 2026-worldcup-predictions
```

### 1.2 恢复 Claude Code 持久记忆

> **这是最容易被跳过的步骤，跳过 = Claude Code 不知道项目历史。**

```bash
# Linux / macOS
MEMORY_DIR="$HOME/.claude/projects/$(echo $(pwd) | sed 's/[\/\\]/--/g')/memory"
mkdir -p "$MEMORY_DIR"
cp memory_backup/*.md "$MEMORY_DIR/"

# Windows PowerShell
$projectPath = (Get-Location).Path -replace '[\\/:]', '--'
$memoryDir = "$env:USERPROFILE\.claude\projects\$projectPath\memory"
New-Item -ItemType Directory -Force -Path $memoryDir | Out-Null
Copy-Item -Path "memory_backup\*.md" -Destination $memoryDir -Force
```

验证:
```bash
# 确认 MEMORY.md 已复制。Claude Code 下次启动时会自动读取。
ls "$MEMORY_DIR/MEMORY.md"   # 应该存在
```

> **注意**: Claude Code 的 memory 目录路径规则是项目绝对路径的 `/` 和 `\` 替换为 `--`。如果你的项目在 `E:\ai\世界杯`，则路径为 `~\.claude\projects\E--ai----\memory\`。

---

## 2. 获取 openfootball 历史数据库

openfootball 是独立的开源项目，包含 1930-2026 全部世界杯结构化数据。不在本项目 git 中，需单独 clone。

```bash
mkdir -p data
cd data
git clone --depth 1 https://github.com/openfootball/worldcup.json.git openfootball
cd ..
```

> `--depth 1` 只拉最新版本 (~1.1MB)。数据质量: 1930-2022 100% 真实完整，2026 已完赛场次有真实比分。

验证:
```bash
python openfootball_data.py 2026 --standings
```

---

## 3. 安装 AnySearch Skill

用于搜索赛前阵容/伤病/赛后评分/战术分析。

```bash
# Linux / macOS
curl -L -o /tmp/anysearch-skill.zip \
  https://github.com/anysearch-ai/anysearch-skill/archive/refs/tags/v2.1.0.zip
unzip -o /tmp/anysearch-skill.zip -d /tmp/
mv /tmp/anysearch-skill-* ~/.claude/skills/anysearch

# Windows PowerShell
Invoke-WebRequest -Uri "https://github.com/anysearch-ai/anysearch-skill/archive/refs/tags/v2.1.0.zip" -OutFile "$env:TEMP\anysearch-skill.zip"
Expand-Archive -Path "$env:TEMP\anysearch-skill.zip" -DestinationPath "$env:TEMP" -Force
Move-Item -Path "$env:TEMP\anysearch-skill-*" -Destination "$env:USERPROFILE\.claude\skills\anysearch"
```

可选配置 API Key:
```bash
echo "ANYSEARCH_API_KEY=你的key" > ~/.claude/skills/anysearch/.env
```

验证:
```bash
python ~/.claude/skills/anysearch/scripts/anysearch_cli.py search "World Cup test" --max_results 2
```

---

## 4. 完整验证

```bash
# 1) 数据库引擎
python openfootball_data.py 2026 --standings | head -5

# 2) 历史分析引擎
python historical_analyzer.py --trends

# 3) 确认记忆已恢复
# 在 Claude Code 中运行 /memory，应看到 14 条记忆条目

# 4) 确认项目规则已加载
# 在 Claude Code 中运行 /context，Memory files 下应有 CLAUDE.md
```

---

## 5. 日常使用流程

### 每天赛前
```
在 Claude Code 中:
  1. 说"拉取今天赛程" → ESPN API 确认比赛
  2. 说"搜索XX vs XX 首发阵容和伤病" → AnySearch 搜新闻
  3. 说"预测今天比赛" → 自动读取 CLAUDE.md + 记忆 + 模板
```

### 赛后复盘
```
在 Claude Code 中:
  1. 说"复盘今天比赛" → 自动 Glob 原始预测 + ESPN API 实际比分
  2. 说"把新教训写入记忆" → 更新 memory_backup/ + 持久记忆
```

### 更新 openfootball 数据库
```bash
cd data/openfootball && git pull && cd ../..
# openfootball 社区会在赛后几小时内更新比分+进球者
```

---

## 6. 🚨 会话结束时必做：同步记忆

> **不做这一步 = 其他机器下次 git pull 后看不到你这次的教训。**

```
在 Claude Code 中:
  1. 说"把新记忆同步到 memory_backup" → 自动复制持久记忆到项目目录
  2. git add memory_backup/ && git commit -m "记忆: 6月XX日复盘教训" && git push
```

同步脚本（也可手动执行）:

```bash
# Linux / macOS: 从持久记忆复制回项目
MEMORY_DIR="$HOME/.claude/projects/E--ai----/memory"
cp "$MEMORY_DIR"/*.md memory_backup/
cd memory_backup && git diff --stat

# Windows PowerShell:
$memoryDir = "$env:USERPROFILE\.claude\projects\E--ai----\memory"
Copy-Item -Path "$memoryDir\*.md" -Destination "memory_backup\" -Force
```

> ⚠️ 如果你本机的项目路径不是 `E:\ai\世界杯`，`--` 转换规则会不同。运行 `/context` 可看到 Memory files 的实际路径。

---

## 7. 记忆架构总结

```
┌─────────────────────────────────────────────────────────┐
│              日常会话中的记忆流向                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Claude Code 会话                                        │
│    │ 读取 /memory                                         │
│    ▼                                                     │
│  持久记忆 (C:\Users\...\memory\)  ← 每次启动自动加载      │
│    │ 新教训写入                                           │
│    ▼                                                     │
│  持久记忆 (更新)                                          │
│    │ 🚨 会话结束前必须手动同步!                             │
│    ▼                                                     │
│  项目目录 memory_backup/  ← git 管理, 跨机器共享          │
│    │ git commit + git push                                │
│    ▼                                                     │
│  GitHub                                                  │
│    │ git pull (另一台机器)                                 │
│    ▼                                                     │
│  另一台机器的 memory_backup/                              │
│    │ 恢复记忆 (setup 步骤 1.2)                             │
│    ▼                                                     │
│  另一台机器的 持久记忆 → Claude Code 知道了所有历史        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 8. 常见问题

### Q: 为什么 Claude Code 显示"没有记忆"？
执行步骤 1.2，把 `memory_backup/*.md` 复制到 Claude Code 的 memory 目录。

### Q: 如何找到 Claude Code 的 memory 路径？
在 Claude Code 中运行 `/context`，看 Memory files 部分。

### Q: openfootball_data.py 报 GBK 编码错误？
Windows 特有。代码已内置 UTF-8 wrapper。如果仍报错: `chcp 65001`

### Q: AnySearch 搜索无结果？
检查网络。匿名模式有更低限额，可注册 Key 解决。

### Q: 项目路径变了，memory 路径怎么找？
规则: 绝对路径把 `/` 和 `\` 替换为 `--`。如 `E:\ai\世界杯` → `E--ai----`

### Q: data/openfootball 被误删？
```bash
cd data && git clone --depth 1 https://github.com/openfootball/worldcup.json.git openfootball && cd ..
```

---

## 目录结构 (配置完成后)

```
2026-worldcup-predictions/
├── CLAUDE.md                    # 项目规则 (v14)
├── setup.md                     # 本文件
├── match_analysis_template.md   # 深度分析模板
├── historical_upset_patterns.md # 历史冷门数据库
├── MODEL_RULES.md               # v9.1 规则书
├── MODEL_VALIDATION_BACKTEST.md # 27场回测
├── predict.py                   # v11预测引擎
├── openfootball_data.py         # 历史数据引擎
├── historical_analyzer.py       # 历史冷门分析
├── live.py                      # 实时比分查询
├── memory_backup/               # 记忆备份 (14个.md, git 管理)
│   ├── MEMORY.md                # 记忆索引
│   ├── model-evolution.md       # v1→v9.1 演进
│   ├── project-overview.md      # 项目概览
│   └── june-*-review.md         # 各日期复盘
├── player_database_v7.json      # 球员数据库
├── referee_database_v7.json     # 裁判数据库
├── location_advantage_v1.json   # 地理优势
├── .claude/                     # Claude Code 配置
│   ├── settings.json            # 权限配置（通用）
│   └── settings.local.json      # 本机配置（gitignore）
├── data/
│   └── openfootball/            # 1930-2026 JSON (手动 clone)
├── *.md                         # 预测/复盘文档
└── *_手机版.txt                  # 手机版同步输出
```
