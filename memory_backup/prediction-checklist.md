# 预测任务执行检查表

> 目的: 防止凭记忆跑流程 → 每次预测必须逐项打钩
> 教训来源: 7月6日预测 — 多处偏离 CLAUDE.md 因为无检查表

---

## 阶段0: 开工前 (5分钟)

- [ ] Read CLAUDE.md 第三节(输出规范) — 确认 .md + .docx 双输出
- [ ] Read CLAUDE.md 第九节(关联框架) — 确认本次需要读哪些关联文件
- [ ] Read 本检查表 — 确认无新增项

## 阶段1: 数据拉取 (10分钟)

- [ ] ESPN API scoreboard → 确认当天比赛、event_id、UTC→BJT 换算
- [ ] ESPN API summary?event={id} → 拉 roster (可能为空)
- [ ] 若 roster 为空 → 尝试 FIFA API calendar/matches
- [ ] AnySearch 搜索每场 "[队名] starting lineup confirmed World Cup 2026"
- [ ] WebSearch 交叉验证

## 阶段2: 关联框架 (必须读)

- [ ] Read `match_analysis_template.md` — 4模块框架
- [ ] Read `historical_upset_patterns.md` — 冷门模式
- [ ] Read `memory/team-market-values.md` — 身价数据
- [ ] Glob 已有球员数据库 (`player_database_*.md` / `player_database_v7.json`)
- [ ] Read 相关球队的历史预测/复盘文件

## 阶段3: 写 .md 预测 (10项必填)

- [ ] 1. 球员评分 (中文名 + 评分 + 标注数据来源)
- [ ] 2. 因素导向表 (每行必须标方向)
- [ ] 3. 冷门风险评估
- [ ] 4. 比分预测 (首选+半场+≥2备选)
- [ ] 5. 伤病/停赛
- [ ] 6. 强队分类
- [ ] 7. 亚非韧性评估 (仅亚非球队)
- [ ] 8. 教练博弈
- [ ] 9. 定位球攻防
- [ ] 10. 冷门路径

## 阶段4: 写球员数据库

- [ ] 检查是否已有球员数据库文件
- [ ] 若有 → 增量更新，不重写
- [ ] 保存为 `player_database_MMDD.md`

## 阶段5: 生成 .docx

- [ ] 复制最近的 `gen_docx_*.py` → 改日期
- [ ] 填入预测数据
- [ ] 跑 `python gen_docx_MMDD.py`
- [ ] 确认输出文件存在且 > 40KB

## 阶段6: 防幻觉扫描 (输出前)

- [ ] grep 扫描单字缩写: `grep -n '[法挪塞伊沙佛西乌埃新比日韩英克巴摩加葡哥苏]'`
- [ ] 禁止 emoji → 用三位缩写和[对]/[错]/[注意]
- [ ] 禁止"必胜""稳赢""一定"等绝对化用语

## 阶段7: 善后

- [ ] 设置 cron 提醒: 开赛前1小时拉 roster 验证首发
- [ ] 若有教训 → 更新 memory

---

## 本次经验教训 (7月6日)

| 问题 | 原因 | 修复 |
|------|------|------|
| 只输出 .md 无 .docx | 凭记忆，不查第三节 | 阶段5强制生成 |
| 没读关联框架 | 自作主张跳过 | 阶段2强制读取 |
| 没跑 grep 扫描 | 当成"写完再说" | 阶段6输出前强制 |
| 没读已有球员DB | 不知道存在 | 阶段2 Glob |
| 没设 cron 提醒 | 没意识到需要 | 阶段7善后 |
| ESPN roster 为空但未尝试 FIFA API | 退到媒体预测就停了 | 阶段1多源尝试 |

---

> 版本: v1 | 基于 7月6日预测偏离分析
> 下次更新: 发现新偏离时
