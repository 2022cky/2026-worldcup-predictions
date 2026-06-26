---
name: project-overview
description: 2026世界杯预测项目总览 — CLAUDE.md v13规则驱动 + v9.1模型辅助
metadata: 
  node_type: memory
  type: project
  originSessionId: 971ff02c-c006-434b-8223-dd30d5a2bffc
---

# 2026世界杯预测项目

## 项目位置
E:\ai\世界杯

## 核心目标
用ESPN实时API采集比赛数据，结合统计模型和结构化规则预测世界杯比赛结果。每场比赛后复盘对比预测与实际，持续优化。

## 当前工作流 (CLAUDE.md v13)

### 数据源
- **主力**: ESPN API (`scoreboard` endpoint) — UTC时间→北京时间(+8小时)
- **搜索**: AnySearch CLI (`python ~/.claude/skills/anysearch/scripts/anysearch_cli.py`)
- **赛后验证**: openfootball JSON (1930-2022可靠, 2026 6/23后不可用)

### 工作流程
1. **预测前**: ESPN API确认赛程 → AnySearch搜伤病/首发/小组形势 → 淘汰赛路径验证(第3轮)
2. **预测中**: 覆盖10项必填清单 → 生成.md+.txt双输出 → 防幻觉自查
3. **赛后复盘**: Glob原始预测 → ESPN API确认实际比分 → 对比预测vs实际 → 提取教训
4. **赛中**: 实时数据监控 → 调整预测 → 记录偏差原因

### 10项必填清单
1. 首轮球员评分(中文名+评分+MOTM)
2. 因素导向表(每行标方向)
3. 冷门风险评估(低/中/高/极高+理由)
4. 比分预测(首选+半场+≥2备选)
5. 伤病/停赛(含已验证可用替补)
6. 强队分类(超级巨星型/体系型/低效热门)
7. 亚非韧性评估(5项)
8. 教练博弈(落后/领先策略+替补能力)
9. 定位球攻防(简评)
10. 冷门路径(最可能怎么翻)

### 关键文件
- `CLAUDE.md` — v13项目规则(当前活跃框架)
- `predict_v4.py` ~ `predict_v7.py` — 历代预测引擎(v1→v9.1)
- `player_database_v7.json` — 24队116人球员数据
- `referee_database_v7.json` — 裁判出牌率+肢体容忍度
- `location_advantage_v1.json` — 地理优势量化
- `MODEL_RULES.md` — v9完整规则书(R1-R16)
- `MODEL_VALIDATION_BACKTEST.md` — 27场全量回测

### 模型状态
- 量化模型: v9.1 (方向71%, 但均势0/2盲区)
- 当前框架: CLAUDE.md v13 (规则驱动, 覆盖模型的均势盲区)

## 输出规范
- `.md` + `.txt` 双输出，内容完全一致
- 文件命名: `YYYY年M月D日_主题.md`
- 球员中文名，国家全称，时间北京时间
