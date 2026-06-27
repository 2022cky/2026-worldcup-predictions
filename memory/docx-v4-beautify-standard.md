---
name: docx-v6-beautify-standard
description: DOCX美化v6规范 — 正确横向尺寸 + 连续流 + 全10项清单
metadata:
  type: workflow
---

# DOCX v6 美化规范

> 2026-06-28 用户反馈后确认。关联: [[project-overview]]

## 🚨 横向页面 — 致命教训

**docx-js landscape 必须传入 PORTRAIT 尺寸:**

```javascript
// ✅ 正确
PW = 11906;  // 短边 (portrait width)
PH = 16838;  // 长边 (portrait height)
CW = PH - MG * 2;  // 16838 - 1700 = 15138 ← 真正可打印宽度
size: { width: PW, height: PH, orientation: PageOrientation.LANDSCAPE }
// → XML 输出: w:w="16838" w:h="11906" (正确横向)

// ❌ 错误 (v3-v5 的 bug)
PW = 16838; PH = 11906;
size: { width: PW, height: PH, orientation: PageOrientation.LANDSCAPE }
// → XML 输出: w:w="11906" w:h="16838" (竖屏! 表格全部溢出!)
```

**Why v3-v5 表格溢出:** 传入横向尺寸 → docx-js 又交换一次 → 页面变成了竖屏 11906 宽, 但表格按 15038 宽生成 → 溢出 4132 DXA。

## 国家名规则
- 🚨 禁止三位字母缩写 → 直接用中文全称
- 🚨 全文禁止单字缩写
- "刚果金"可作为"刚果民主共和国"的简称

## 优势/警示标记
| 旧标记 | 新标记 | 含义 |
|--------|--------|------|
| `[火]`… | ★ ★★ ★★★ | 有利程度 |
| `[注意]`… | ※ | 警示 |

## 汇总表 (8列, 无半场)
列宽: #(400) / 时间(720) / 组(420) / 比赛(5900) / 形势(3200) / 首选比分(1280) / 备选比分(2158) / 冷门风险(1060) = 15138 DXA

## 页面与流
- 横向A4: 传入 11906×16838, margin 850, CW=15138
- 🚨 不插入 PageBreak — 让内容自然流动
- 页眉右对齐灰字+蓝色底线, 页脚居中 "— Page X —"

## 必填清单 (10项, 每场必全)
1. 基本信息 2. 因素导向 3. 强队分类 4. 亚非韧性 5. 伤病与停赛 6. 教练博弈 7. 定位球攻防 8. 冷门风险评估 9. 冷门路径 10. 比分预测

## 模板文件
`gen_docx_template.js` — 已修复横向尺寸, 可复用
