---
name: project-overview
description: 2026世界杯预测项目 — 用ESPN API数据 + 统计学习优化预测模型
metadata: 
  node_type: memory
  type: project
  originSessionId: 971ff02c-c006-434b-8223-dd30d5a2bffc
---

# 2026 World Cup Prediction Project

## 项目位置
E:\ai\世界杯

## 核心目标
用ESPN实时API采集比赛数据，结合统计模型预测世界杯比赛结果。每场比赛后复盘对比预测与实际，持续优化模型参数。

## 关键文件
- [[predict-py]] — ESPN数据采集器 v3
- [[predict-v4-py]] — 预测引擎 v4
- [[worldcup-data]] — 实时比赛JSON数据

## 工作流程
1. `python predict.py` → 刷新ESPN数据到 worldcup_data.json
2. `python predict_v4.py` → v4模型分析+预测
3. 比赛后回测 → 对比预测vs实际 → 调参
4. 下一轮预测使用优化后的参数

## 当前模型版本: v4
核心改动：基本面权重 40→55%，趋势信号 35→20%，冷门溢价减半
