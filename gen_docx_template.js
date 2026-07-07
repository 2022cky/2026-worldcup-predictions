// DOCX 统一模板 — 2026世界杯预测/复盘
// v2.0: 所有表型 + 单场/多场双模式 + 数据驱动
// 用法: const T = require("./gen_docx_template.js"); T.buildPrediction({...});
//       node gen_docx_xxxx.js (直接运行数据文件)

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, HeadingLevel
} = require("docx");

// ═══ 版面 ═══
const FONT = "Microsoft YaHei";
const PW = 11906;               // A4 portrait width (swap → landscape height)
const PH = 16838;               // A4 portrait height (swap → landscape width)
const M = 1300;                 // 1" margin for content
const CW = PH - M * 2;          // 14238 — content width (wider than original)

// ═══ 色板 ═══
const COL = {
  BLUE:       "1A3A5C",
  WHITE:      "FFFFFF",
  GRAY:       "F2F2F2",
  GREEN:      "E2EFDA",
  RED:        "C0392B",
  BLACK:      "1A1A2E",
  DARK:       "333333",
  META:       "888888",
  META2:      "666666",
  ACCENT:     "2E75B6",
  LIGHT_BLUE: "D6E4F0",
  ORANGE:     "F39C12",
};

// ═══ 基础原子 ═══
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const bd = { top: border, bottom: border, left: border, right: border };
const cm = { top: 60, bottom: 60, left: 100, right: 100 };

function T(text, opts = {}) {
  return new TextRun({
    text: String(text), font: FONT,
    size: (opts.sz || 9) * 2,                     // 常规9pt=18 half-pts
    bold: !!opts.b, color: opts.c || COL.BLACK,
    italics: !!opts.i,
  });
}
function P(text, opts = {}) {
  const r = Array.isArray(text) ? text : [T(text, opts)];
  return new Paragraph({
    spacing: { after: opts.a != null ? opts.a : 60, before: opts.bf || 0 },
    alignment: opts.al || AlignmentType.LEFT,
    children: r,
    border: opts.border,
  });
}
function E() { return new Paragraph({ spacing: { after: 40 }, children: [] }); }     // empty
function BR() { return new Paragraph({ children: [new PageBreak()] }); }

// heading
function H1(txt) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 140 }, children: [T(txt, { sz: 15, b: true, c: COL.BLUE })] }); }
function H2(txt) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 }, children: [T(txt, { sz: 12, b: true, c: COL.DARK })] }); }

// metadata / notes
function META(txt) { return P(txt, { sz: 7.5, c: COL.META, i: true }); }
function NOTE(txt) { return P(txt, { sz: 8, c: COL.META2 }); }
function BOLD(txt, c) { return P(txt, { sz: 9, b: true, c: c || COL.DARK }); }

// ═══ 表格单元格 ═══
function HC(txt, w) {       // header cell
  return new TableCell({ borders: bd, width: { size: w, type: WidthType.DXA }, shading: { fill: COL.BLUE, type: ShadingType.CLEAR }, verticalAlign: "center", margins: cm,
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [T(txt, { sz: 8.5, b: true, c: COL.WHITE })] })] });
}
function DC(txt, w, opts = {}) {   // data cell
  const runs = Array.isArray(txt) ? txt : [T(txt, { sz: opts.sz || 8, b: !!opts.b, c: opts.c || COL.DARK })];
  return new TableCell({ borders: bd, width: { size: w, type: WidthType.DXA },
    shading: opts.sh ? { fill: opts.sh, type: ShadingType.CLEAR } : undefined,
    verticalAlign: "center", margins: cm,
    children: [new Paragraph({ alignment: opts.al || AlignmentType.LEFT, children: runs })] });
}
// Multi-line cell: "line1\nline2" → multiple Paragraphs
function DCM(txt, w, opts = {}) {
  const lines = String(txt).split("\n");
  return new TableCell({ borders: bd, width: { size: w, type: WidthType.DXA },
    shading: opts.sh ? { fill: opts.sh, type: ShadingType.CLEAR } : undefined,
    verticalAlign: "top", margins: cm,
    children: lines.map(l => new Paragraph({ spacing: { after: 30 }, alignment: opts.al || AlignmentType.LEFT, children: [T(l, { sz: opts.sz || 8, b: !!opts.b, c: opts.c || COL.DARK })] })) });
}

function ROW(cells) { return new TableRow({ children: cells }); }

// header row factory
function HR(labels, widths) { return ROW(labels.map((t, i) => HC(t, widths[i]))); }
// data row factory: texts=[...], widths=[...], green/gray
function DR(texts, widths, green, gray) {
  const sh = green ? COL.GREEN : (gray ? COL.GRAY : undefined);
  return ROW(texts.map((t, i) => DC(t, widths[i], { sh })));
}
// data row with first column bold
function DRB(texts, widths, green, gray) {
  const sh = green ? COL.GREEN : (gray ? COL.GRAY : undefined);
  return ROW(texts.map((t, i) => DC(t, widths[i], { b: i === 0, sh })));
}
// data row with specific bold indices
function DRBI(texts, widths, boldIndices, green, gray) {
  const sh = green ? COL.GREEN : (gray ? COL.GRAY : undefined);
  return ROW(texts.map((t, i) => DC(t, widths[i], { b: boldIndices.includes(i), sh })));
}

function TBL(widths, rows) {
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: widths, rows });
}

// ═══════════════════════════════════════════
// 预定义表类型
// ═══════════════════════════════════════════

// --- 封面 ---
function cover({ title, subtitle, tag, lines }) {
  const items = [
    E(), E(),
    P("2026 FIFA 世界杯", { sz: 18, b: true, c: COL.RED, al: AlignmentType.CENTER }),
    P(title, { sz: 22, b: true, al: AlignmentType.CENTER, a: 80 }),
  ];
  if (subtitle) items.push(P(subtitle, { sz: 14, c: COL.META, al: AlignmentType.CENTER, a: 60 }));
  if (tag) items.push(P(tag, { sz: 11, b: true, c: COL.RED, al: AlignmentType.CENTER, a: 40 }));
  if (lines) lines.forEach(l => items.push(P(l, { sz: 9, c: COL.DARK, al: AlignmentType.CENTER, a: 20 })));
  items.push(P("", { sz: 7, c: COL.META2, al: AlignmentType.CENTER, a: 20 }));
  items.push(BR());
  return items;
}

// --- 预测汇总表 (8+1列) ---
// cols: #, 比赛, 身价比, 强队分类, 首选比分, 概率, 备选, 冷门风险
const SUM_W = [500, 3800, 1200, 2400, 2200, 900, 2800, 1500]; // sum check
function summaryTable(rows) {
  const W = SUM_W; // let CW be distributed
  // Actually we need exact sum. Let's recalc: 500+3800+1200+2400+2200+900+2800+1500 = 15300 - too wide for CW=14238
  // Let me fix widths
  // Actually 500+3200+1100+2200+2000+800+2600+1838 = 14238 ✓
  const WW = [500, 3200, 1100, 2200, 2000, 800, 2600, 1838];
  return TBL(WW, [
    HR(["#","比赛","身价比","强队分类","首选比分","概率","备选","冷门风险"], WW),
    ...rows.map((r, i) => DR(r, WW, i === 0, i % 2 === 1)),
  ]);
}

// --- 盘口表 (4列) ---
const ODDS_W = [3400, 1600, 1600, 7638];
function oddsTable(rows) {
  return TBL(ODDS_W, [
    HR(["盘口","赔率","隐含概率","解读"], ODDS_W),
    ...rows.map((r, i) => DR(r, ODDS_W, false, i % 2 === 0)),
  ]);
}

// --- 盘口对比表 (4列) ---
const ODDS_CMP_W = [3200, 3200, 3200, 4638];
function oddsCompareTable(rows) {
  return TBL(ODDS_CMP_W, [
    HR(["维度","市场","我们","分歧"], ODDS_CMP_W),
    ...rows.map((r, i) => DR(r, ODDS_CMP_W, false, i % 2 === 0)),
  ]);
}

// --- 球员评分表 (7列: 空/#/球员/评分/位置/备注) ---
const PS_W = [400, 500, 3000, 700, 1400, 8238]; // 14238
function playerScoreTable(rows) {
  return TBL(PS_W, [
    HR(["","#","球员","评分","位置","表现点评"], PS_W),
    ...rows.map((r, i) => DR(r, PS_W, false, i % 2 === 0)),
  ]);
}

// --- 因素导向表 (3列) ---
function factorTable(rows) {
  const W = [5800, 1800, 6638];
  return TBL(W, [
    HR(["因素","有利方","理由"], W),
    ...rows.map((r, i) => DRB(r, W, false, i % 2 === 0)),
  ]);
}

// --- 比分预测表 (4列: 比分/概率/说明) ---
function scoreTable(rows) {
  const W = [3000, 1000, 10238];
  return TBL(W, [
    HR(["比分","概率","说明"], W),
    ...rows.map((r, i) => DRBI(r, W, [0], i === 0, i % 2 === 1)),
  ]);
}

// --- 比分详情表 (4列: 类型/比分/半场/进球者) ---
function scoreDetailTable(rows) {
  const W = [1600, 2800, 1200, 8638];
  return TBL(W, [
    HR(["类型","比分","半场","进球者"], W),
    ...rows.map((r, i) => DRBI(r, W, [0, 1], i === 0, i % 2 === 1)),
  ]);
}

// --- 伤病表 (3列: 球队/球员/状态) ---
function injuryTable(rows) {
  const W = [1200, 4800, 8238];
  return TBL(W, [
    HR(["球队","球员","状态"], W),
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}
// 伤病扩展表 (4列: 球队/球员/状态/影响)
function injuryTableEx(rows) {
  const W = [1200, 3800, 4600, 4638];
  return TBL(W, [
    HR(["球队","球员","状态","影响评级"], W),
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// --- 信息表 (2列: 标签/值) ---
function infoTable(rows) {
  const W = [2800, CW - 2800];
  return TBL(W, rows.map(([k, v], i) => ROW([DC(k, W[0], { b: true, sh: COL.GRAY }), DC(v, W[1])])));
}

// --- 韧性评估表 (3列) ---
function resilienceTable(items) {
  const W = [2800, 1400, CW - 4200];
  return TBL(W, [
    HR(["维度","评级","说明"], W),
    ...items.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// --- 强队分类表 (4列) ---
function classificationTable(rows) {
  const W = [2800, 3800, 3800, 3838];
  return TBL(W, [
    HR(["维度","球队A","球队B","?"], W),  // header overridden in use
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// --- 教练博弈表 (4列) ---
function coachingTable(rows) {
  const W = [2400, 5000, 5000];
  // sum = 12400 < CW, let's distribute: 2400, 5000, 4838 = 12238? No, need to match CW=14238
  // Actually CW = 16838 - 2600 = 14238. Let's do: 2400, 5200, 6638 = 14238
  const WW = [2400, 5200, 6638];
  return TBL(WW, [
    HR(["场景","球队A","球队B"], WW),
    ...rows.map((r, i) => DR(r, WW, false, i % 2 === 0)),
  ]);
}

// --- 定位球表 (4列) ---
function setPiecesTable(rows) {
  const W = [2800, 3800, 3800, 3838];
  return TBL(W, [
    HR(["维度","球队A","球队B","?"]),
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// --- 总结对比表 (4列) ---
function summaryCompareTable(rows) {
  const W = [3200, 3800, 3800, 3438];
  return TBL(W, [
    HR(["维度","球队A","球队B","优势"], W),
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// --- 首发变动对比表 (4列) ---
function lineupChangeTable(rows) {
  const W = [1800, 3600, 3600, 5238];
  return TBL(W, [
    HR(["位置","原预测","实际首发","影响"], W),
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// --- 通用灵活表: 传入headers+widths+rows ---
function flexTable(headers, widths, rows, greenFirst) {
  return TBL(widths, [
    HR(headers, widths),
    ...rows.map((r, i) => DR(r, widths, greenFirst && i === 0, !greenFirst && i % 2 === 0)),
  ]);
}

// --- 关键对位表 — 对位1专用 (4列: 维度/球员A/球员B) ---
function matchupTable(rows) {
  const W = [3000, 5619, 5619];
  return TBL(W, [
    HR(["维度","球员A","球员B"], W),
    ...rows.map((r, i) => DR(r, W, false, i % 2 === 0)),
  ]);
}

// ═══════════════════════════════════════════
// 文档构建器
// ═══════════════════════════════════════════

/**
 * 构建单场比赛预测文档
 * @param {Object} opts
 * @param {string} opts.title        - 标题如 "瑞士 vs 哥伦比亚"
 * @param {string} opts.subtitle     - 副标题如 "SUI vs COL"
 * @param {string} opts.tag          - 红色标签
 * @param {string[]} opts.metaLines  - 封面信息行
 * @param {string[][]} opts.summary  - 汇总表数据行
 * @param {string} opts.summaryNote  - 汇总备注
 * @param {Object[]} opts.sections   - [{ title, subtitle, note, table: {type, rows, headers, widths}, text, texts }]
 */
function buildPrediction(opts) {
  if (!opts.outFile) throw new Error("buildPrediction requires opts.outFile");
  const children = [];

  // Cover
  children.push(...cover({
    title: opts.title,
    subtitle: opts.subtitle,
    tag: opts.tag,
    lines: opts.metaLines,
  }));

  // Summary
  if (opts.summary) {
    children.push(H1("预测汇总"));
    children.push(summaryTable(opts.summary));
    if (opts.summaryNote) children.push(META(opts.summaryNote));
    children.push(E());
  }

  // Sections
  for (const sec of (opts.sections || [])) {
    if (sec.title) children.push(H1(sec.title));
    if (sec.subtitle) children.push(H2(sec.subtitle));
    if (sec.text) children.push(P(sec.text));
    if (sec.note) children.push(META(sec.note));
    if (sec.bold) children.push(BOLD(sec.bold, COL.BLUE));

    // Multiple texts
    if (sec.texts) {
      for (const t of sec.texts) {
        if (typeof t === "string") children.push(P(t));
        else if (t.bold) children.push(BOLD(t.text || t, t.color));
        else if (t.meta) children.push(META(t.text || t));
        else children.push(P(t.text || t, t.opts || {}));
      }
    }

    // Table
    if (sec.table) {
      const t = sec.table;
      if (t.type === "flex") {
        children.push(flexTable(t.headers, t.widths, t.rows, t.greenFirst));
      } else if (t.type === "summary") {
        children.push(summaryTable(t.rows));
      } else if (t.type === "odds") {
        children.push(oddsTable(t.rows));
      } else if (t.type === "oddsCompare") {
        children.push(oddsCompareTable(t.rows));
      } else if (t.type === "playerScore") {
        children.push(playerScoreTable(t.rows));
      } else if (t.type === "factor") {
        children.push(factorTable(t.rows));
      } else if (t.type === "score") {
        children.push(scoreTable(t.rows));
      } else if (t.type === "scoreDetail") {
        children.push(scoreDetailTable(t.rows));
      } else if (t.type === "injury") {
        children.push(injuryTable(t.rows));
      } else if (t.type === "injuryEx") {
        children.push(injuryTableEx(t.rows));
      } else if (t.type === "info") {
        children.push(infoTable(t.rows));
      } else if (t.type === "resilience") {
        children.push(resilienceTable(t.rows));
      } else if (t.type === "classification") {
        children.push(classificationTable(t.rows));
      } else if (t.type === "coaching") {
        children.push(coachingTable(t.rows));
      } else if (t.type === "setPieces") {
        children.push(setPiecesTable(t.rows));
      } else if (t.type === "matchup") {
        children.push(matchupTable(t.rows));
      } else if (t.type === "summaryCompare") {
        children.push(summaryCompareTable(t.rows));
      } else if (t.type === "lineupChange") {
        children.push(lineupChangeTable(t.rows));
      }
    }

    if (sec.space) children.push(E());
  }

  // Footer
  children.push(E());
  children.push(META(opts.footer || ""));
  children.push(META(`生成时间: ${new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" })} 北京时间`));

  return save(opts.outFile, buildWrapper(opts.title, children));
}

function buildWrapper(title, children) {
  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 18 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: FONT, color: COL.BLUE },
          paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: COL.DARK },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
      ],
    },
    sections: [{
      properties: {
        page: {
          size: { width: PW, height: PH, orientation: PageOrientation.LANDSCAPE },
          margin: { top: 1100, right: M, bottom: 1100, left: M },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: COL.ACCENT, space: 4 } },
            children: [T(`${title}  |  2026 FIFA 世界杯`, { sz: 7, c: COL.META, i: true })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              T("— 第 ", { sz: 7, c: COL.META }),
              new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: COL.META }),
              T(" 页 —", { sz: 7, c: COL.META }),
            ],
          })],
        }),
      },
      children,
    }],
  });
}

// ═══ 便捷: 直接打包写入 ═══
function save(filename, doc) {
  return Packer.toBuffer(doc).then(buf => {
    fs.writeFileSync(filename, buf);
    console.log(`[OK] ${filename} (${(buf.length / 1024).toFixed(1)} KB)`);
    return buf;
  });
}

// ═══ 导出 ═══
module.exports = {
  // atoms
  T, P, E, BR, H1, H2, META, NOTE, BOLD,
  // table primitives
  HC, DC, DCM, ROW, HR, DR, DRB, DRBI, TBL, flexTable,
  // pre-built tables
  summaryTable, oddsTable, oddsCompareTable, playerScoreTable,
  factorTable, scoreTable, scoreDetailTable, injuryTable, injuryTableEx,
  infoTable, resilienceTable, classificationTable, coachingTable,
  setPiecesTable, matchupTable, summaryCompareTable, lineupChangeTable,
  // builders
  cover, buildPrediction, buildWrapper,
  // output
  save,
  // constants
  COL, CW, FONT,
};
