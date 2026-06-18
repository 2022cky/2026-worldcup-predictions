---
name: predict-v5-py
description: v5预测引擎 — 中文队名、半场预测、让球分析、实时新闻集成
metadata: 
  node_type: memory
  type: reference
  originSessionId: 971ff02c-c006-434b-8223-dd30d5a2bffc
---

# predict_v5.py — v5全方位预测引擎

位置: E:\ai\世界杯\predict_v5.py

## v5 vs v4 新增功能
1. **中文队名** — 所有输出使用中文
2. **半场比分预测** — HT与FT逻辑一致性验证
3. **让球/盘口分析** — sigmoid-based赢盘概率
4. **大小球分析** — 基于平局概率的O/U 2.5预测
5. **实时新闻集成** — WebSearch采集阵容/伤病/赔率
6. **赔率数据纳入模型** — 市场隐含概率5%权重
7. **同时输出.md + .txt**

## 权重体系 (v5)
- 基本面: 50% (v4的55%→50%, 为新闻赔率让路)
- 趋势信号: 15%
- 伤病/缺阵: 15%
- 新闻/阵容: 10% (新增)
- 近期状态: 5% (降权)
- 赔率校准: 5% (新增)
