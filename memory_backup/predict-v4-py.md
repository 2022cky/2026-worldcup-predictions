---
name: predict-v4-py
description: v4预测引擎核心文件，包含预测函数和参数
metadata: 
  node_type: memory
  type: reference
  originSessionId: 971ff02c-c006-434b-8223-dd30d5a2bffc
---

# predict_v4.py — v4预测引擎

位置: E:\ai\世界杯\predict_v4.py

## 核心函数
`predict_match(home, away, home_rank, away_rank, home_injuries, away_injuries, home_warmup, away_warmup, is_worldcup_debut_home, is_worldcup_debut_away)`

返回: {score_pred, confidence, upset_risk, home_win%, draw%, away_win%}

## 参数权重
- 基本面差距: 55%
- 趋势信号: 20%
- 伤病/缺阵: 15%
- 冷门溢价: 5%
- 历史交锋: 3%
- 门将超神: 2%

## 关键规则
- R1: FIFA Top5 vs 非Top30 → 赢2球+概率55%
- R2: 非洲/亚洲光环降权至0.3x
- R3: 核心限时衰减0.5x
- R4: 铁桶阵保平从+12%降为+5%
- R5: 友好赛降权至0.2x
