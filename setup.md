# 项目初始化指南

> 在新机器上 clone 本项目后, 按以下步骤配置。

---

## 1. 克隆项目

```bash
git clone https://github.com/2022cky/2026-worldcup-predictions.git
cd 2026-worldcup-predictions
```

---

## 2. 获取数据库 (openfootball)

```bash
mkdir -p data
cd data
git clone --depth 1 https://github.com/openfootball/worldcup.json.git openfootball
cd ..
```

> `data/openfootball/` 已在 `.gitignore` 中, 不会随项目上传。
> 每次拉取最新数据: `cd data/openfootball && git pull`

验证:
```bash
python openfootball_data.py 2026 --standings | head -10
```

---

## 3. 安装 AnySearch Skill

```bash
# 下载最新版
curl -L -o anysearch-skill.zip https://github.com/anysearch-ai/anysearch-skill/archive/refs/tags/v2.1.0.zip

# 解压到 Claude Code skills 目录
# Linux/macOS:
unzip anysearch-skill.zip -d ~/.claude/skills/
# Windows PowerShell:
# Expand-Archive anysearch-skill.zip -DestinationPath ~/.claude/skills/

# (可选) 配置 API Key 提高限额
# 访问 https://anysearch.com/console/api-keys 注册免费 key
# echo "ANYSEARCH_API_KEY=你的key" > ~/.claude/skills/anysearch/.env
```

> AnySearch 是必装项 — CLAUDE.md 依赖它获取阵容/伤病/球员评分。

---

## 4. 依赖检查

Python 标准库即可, 无需 pip install:
- `json`, `urllib.request`, `re`, `pathlib`

如需运行 `predict.py`:
```bash
pip install -r requirements.txt  # 如存在
```

---

## 5. 验证

```bash
python openfootball_data.py 2026 --scorers
python historical_analyzer.py --trends
```

---

## 目录结构

```
2026-worldcup-predictions/
├── CLAUDE.md                  # 项目规则 (每台机器通用)
├── setup.md                   # 本文件
├── openfootball_data.py       # 数据引擎
├── historical_analyzer.py     # 历史分析
├── match_analysis_template.md # 深度分析模板
├── data/
│   └── openfootball/          # (手动 clone, 不随 git 上传)
├── *.md                       # 预测/复盘文档
└── *_手机版.txt                # 手机版同步输出
```
