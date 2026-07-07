const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

// === COLOR PALETTE ===
const BLUE = "1A3A5C";
const WHITE = "FFFFFF";
const LIGHT_GRAY = "F2F2F2";
const LIGHT_GREEN = "E2EFDA";
const RED = "C00000";
const BLACK = "000000";
const DARK = "333333";
const LIGHT_BLUE = "D6E4F0";

// === HELPERS ===
const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorders = {
  top: { style: BorderStyle.NONE, size: 0 },
  bottom: { style: BorderStyle.NONE, size: 0 },
  left: { style: BorderStyle.NONE, size: 0 },
  right: { style: BorderStyle.NONE, size: 0 },
};
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: BLUE, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, font: "Microsoft YaHei", size: 18, color: WHITE })] })],
  });
}

function cell(text, width, opts = {}) {
  const { bold, align, color, shade, size } = opts;
  const children = [];
  // Split by ** to handle bold inline
  if (text.includes("**")) {
    const parts = text.split("**");
    parts.forEach((p, i) => {
      if (p.length === 0) return;
      children.push(new TextRun({ text: p, bold: i % 2 === 1 || !!bold, font: "Microsoft YaHei", size: size || 17, color: color || DARK }));
    });
  } else {
    children.push(new TextRun({ text, bold: !!bold, font: "Microsoft YaHei", size: size || 17, color: color || DARK }));
  }
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { fill: shade, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({ alignment: align || AlignmentType.LEFT, children })],
  });
}

function row(cells) {
  return new TableRow({ children: cells });
}

function blueHeaderRow(texts, widths) {
  return new TableRow({
    children: texts.map((t, i) => headerCell(t, widths[i])),
  });
}

function dataRow(texts, widths, isGreen, isGray) {
  const shade = isGreen ? LIGHT_GREEN : (isGray ? LIGHT_GRAY : undefined);
  return new TableRow({
    children: texts.map((t, i) => cell(t, widths[i], { shade })),
  });
}

function dataRowBoldFirst(texts, widths, isGreen, isGray) {
  const shade = isGreen ? LIGHT_GREEN : (isGray ? LIGHT_GRAY : undefined);
  return new TableRow({
    children: texts.map((t, i) => cell(t, widths[i], { bold: i === 0, shade })),
  });
}

function sectionTitle(text) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, font: "Microsoft YaHei", size: 26, color: BLUE })],
  });
}

function subTitle(text) {
  return new Paragraph({
    spacing: { before: 140, after: 80 },
    children: [new TextRun({ text, bold: true, font: "Microsoft YaHei", size: 22, color: DARK })],
  });
}

function bodyText(text, opts = {}) {
  const { bold, color } = opts;
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, bold, font: "Microsoft YaHei", size: 18, color: color || DARK })],
  });
}

function noteText(text) {
  return new Paragraph({
    spacing: { before: 30, after: 30 },
    children: [new TextRun({ text, font: "Microsoft YaHei", size: 16, color: "666666", italics: true })],
  });
}

// === BUILD DOCUMENT ===

const contentWidth = 15840 - 1440 - 1440; // landscape A4: long edge minus 1" margins each side
// Actually landscape A4: width ~16838, height ~11906
// Let's use: page width = 16838 (landscape long edge), content = 16838 - 2880 = 13958
const PAGE_W = 11906;  // A4 short edge
const PAGE_H = 16838;  // A4 long edge
const MARGIN = 1440;
const CT_W = PAGE_H - 2 * MARGIN; // 13958

const mainTblW = CT_W;

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Microsoft YaHei", size: 18 } } },
  },
  sections: [
    // === COVER PAGE ===
    {
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H, orientation: PageOrientation.LANDSCAPE },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      children: [
        new Paragraph({ spacing: { before: 2400 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          children: [new TextRun({ text: "2026世界杯 16强淘汰赛", font: "Microsoft YaHei", size: 36, bold: true, color: BLUE })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          children: [new TextRun({ text: "阿根廷 vs 埃及", font: "Microsoft YaHei", size: 44, bold: true, color: BLACK })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [new TextRun({ text: "ARG vs EGY", font: "Microsoft YaHei", size: 28, color: "666666" })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200, after: 40 },
          children: [new TextRun({ text: "首发确认后重写版本", font: "Microsoft YaHei", size: 24, bold: true, color: RED })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 20 },
          children: [new TextRun({ text: "北京时间 2026年7月8日 00:00 | 梅赛德斯-奔驰球场, 亚特兰大", font: "Microsoft YaHei", size: 20, color: DARK })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 20 },
          children: [new TextRun({ text: "阵容来源: ESPN API roster (760509) 已确认首发 | 数据截止: 7月7日 23:30 BJT", font: "Microsoft YaHei", size: 18, color: "888888" })],
        }),
        new Paragraph({ children: [new PageBreak()] }),
      ],
    },

    // === MAIN CONTENT ===
    {
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H, orientation: PageOrientation.LANDSCAPE },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "ARG vs EGY | 7月8日首发更新预测", font: "Microsoft YaHei", size: 14, color: "999999", italics: true })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "第 ", font: "Microsoft YaHei", size: 14, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 14, color: "999999" })],
          })],
        }),
      },
      children: [
        // ===== PREDICTION SUMMARY =====
        sectionTitle("预测汇总"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [2400, 1400, 2400, 2400, 1200, 3600, 1800],
          rows: [
            blueHeaderRow(["比赛", "身价比", "强队分类", "预测首选", "概率", "备选(按概率)", "冷门风险"], [2400, 1400, 2400, 2400, 1200, 3600, 1800]),
            dataRow(["ARG vs EGY", "6.9:1", "ARG: 超级巨星型", "阿根廷 2-1 埃及", "~30%", "2-0(~25%) / 1-0(~20%) / 3-1(~12%) / 1-1加时(~8%)", "中"], [2400, 1400, 2400, 2400, 1200, 3600, 1800], true),
          ],
        }),
        noteText("[注意] 首发确认后重写版: 原预测基于媒体预测阵容, 与ESPN确认首发存在重大差异。方向不变但比分下调(3-1→2-1)。"),

        // ===== REAL-TIME ODDS =====
        sectionTitle("实时盘口分析 (DraftKings via ESPN API)"),
        noteText("数据截止: 7月7日 23:45 BJT | 来源: ESPN API odds event=760509"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [3600, 1800, 1800, 6758],
          rows: [
            blueHeaderRow(["盘口", "赔率", "隐含概率", "解读"], [3600, 1800, 1800, 6758]),
            dataRow(["阿根廷 ML", "-310", "75.6%", "市场定价阿根廷极大概率常规时间胜出"], [3600, 1800, 1800, 6758], false, true),
            dataRow(["平局", " — ", "~15.3%", "隐含推算值"], [3600, 1800, 1800, 6758]),
            dataRow(["埃及 ML", "+1000", "9.1%", "市场基本不考虑埃及常规时间赢球"], [3600, 1800, 1800, 6758], false, true),
            dataRow(["阿根廷 -1.5 (让球)", "+100", "50.0%", "让1.5球平赔, 市场认为净胜2球概率50%, 与我们的2-1首选(净胜1球)一致"], [3600, 1800, 1800, 6758]),
            dataRow(["埃及 +1.5", "-125", "55.6%", "埃及受让方向更受青睐, 市场预期小比分"], [3600, 1800, 1800, 6758], false, true),
            dataRow(["Over 2.5 (大球)", "+105", "48.8%", "市场预期2-3球, 与我们预测一致"], [3600, 1800, 1800, 6758]),
            dataRow(["Under 2.5 (小球)", "-130", "56.5%", "小球略受偏爱, 反映淘汰赛防守优先心理"], [3600, 1800, 1800, 6758], false, true),
          ],
        }),
        noteText(""),
        subTitle("盘口与预测对比"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [3500, 3500, 3500, 3458],
          rows: [
            blueHeaderRow(["维度", "市场", "我们", "分歧"], [3500, 3500, 3500, 3458]),
            dataRow(["阿根廷胜方向", "75.6%", "~83%", "一致: 阿根廷胜"], [3500, 3500, 3500, 3458], false, true),
            dataRow(["进球数", "Over 2.5 49%", "3球(首选)", "一致: 中等进球"], [3500, 3500, 3500, 3458]),
            dataRow(["让球方向", "-1.5 50%", "净胜1球首选", "我们比市场更保守(2-1 vs -1.5覆盖)"], [3500, 3500, 3500, 3458], false, true),
            dataRow(["埃及进球概率", "隐含较低", "~55%认为双方进球", "我们给埃及进球概率更高, 基于阿根廷防线结构性问题"], [3500, 3500, 3500, 3458]),
          ],
        }),
        bodyText("盘口要点: 市场方向与我们完全一致(阿根廷胜, 中等进球), 但我们在比分上更谨慎。市场给-1.5五五开, 我们认为埃及三后腰大巴足够把比分差距控制在1球。DraftKings +1000埃及ML = 9.1%隐含概率, 我们的8%冷门概率与市场极为接近。", { bold: true }),

        // ===== LINEUP CHANGES: ARG =====
        sectionTitle("首发变动 vs 原预测"),
        subTitle("阿根廷 (4-4-2, 3处变更)"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [2000, 3500, 3500, 4958],
          rows: [
            blueHeaderRow(["位置", "原预测", "实际首发", "影响"], [2000, 3500, 3500, 4958]),
            dataRow(["CM", "#16 阿尔马达", "#5 帕雷德斯", "[首发变动] 防守型中场入替, 解放麦卡前压"], [2000, 3500, 3500, 4958], false, true),
            dataRow(["ST", "#22 劳塔罗", "#9 阿尔瓦雷斯", "更灵活的前场跑动, 体能更好"], [2000, 3500, 3500, 4958]),
            dataRow(["CB", "#25 利桑德罗", "#6 利桑德罗", "同一人, 号码不同"], [2000, 3500, 3500, 4958], false, true),
          ],
        }),
        noteText("斯卡洛尼三处调整逻辑: 佛得角恐慌后加强中场防守(帕雷德斯), 同时阿尔瓦雷斯体能优于劳塔罗(120分钟消耗仅4天恢复)"),

        // ===== LINEUP CHANGES: EGY =====
        subTitle("埃及 (4-3-3, 7处与实际不符)"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [1800, 3800, 3800, 4558],
          rows: [
            blueHeaderRow(["位置", "原预测", "实际首发", "影响"], [1800, 3800, 3800, 4558]),
            dataRow(["CB", "阿卜杜勒莫内姆(替伊布拉希姆)", "#2 亚西尔·伊布拉希姆", "[关键] 预测写停赛/Out, 实际首发! 防线提升1档"], [1800, 3800, 3800, 4558], false, true),
            dataRow(["ST", "马尔穆什(7.5分)", "#11 穆斯塔法·齐科", "[关键] 第二攻击核心替补! 反击速度减半"], [1800, 3800, 3800, 4558]),
            dataRow(["CM", "哈姆迪·法蒂", "#14 哈姆迪·法蒂", "修正: 法蒂确实首发, 原号码错"], [1800, 3800, 3800, 4558], false, true),
            dataRow(["CM", "马尔万·阿提亚", "#19 马尔万·阿提亚", "一致, 号码不同"], [1800, 3800, 3800, 4558]),
            dataRow(["CM", "(未列)", "#17 莫哈纳德·拉辛", "[新增] 解禁复出, 三后腰信号"], [1800, 3800, 3800, 4558], false, true),
            dataRow(["LM/RM", "泽科(7.0)/—", "#8 阿舒尔 / #11 齐科", "位置和人员均不同"], [1800, 3800, 3800, 4558]),
          ],
        }),
        noteText("[关键] 埃及核心变化: (1) 伊布拉希姆回归=防线增强 (2) 马尔穆什替补=反击仅剩萨拉赫单核 (3) 三后腰=明确大巴信号"),

        // ===== PLAYER RATINGS =====
        sectionTitle("1. 球员评分 [ESPN API 已确认]"),
        subTitle("阿根廷 (4-4-2 / 4-3-3 混合)"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [600, 800, 3400, 700, 1200, 7258],
          rows: [
            blueHeaderRow(["#", "号码", "球员", "评分", "位置", "表现点评"], [600, 800, 3400, 700, 1200, 7258]),
            // Row: GK
            dataRowBoldFirst(["", "23", "埃米利亚诺·马丁内斯", "8.5", "门将", "2022金手套。对佛得角失2球, 但一对一仍是顶级"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "26", "纳韦尔·莫利纳", "7.0", "右后卫", "马竞。速度可覆盖齐科"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "13", "克里斯蒂安·罗梅罗", "8.0", "中后卫(右)", "热刺核心。防空顶级。对萨拉赫关键对位"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "6", "利桑德罗·马丁内斯", "8.0", "中后卫(左)", "曼联。对佛得角92'制胜球+59'被穿裆"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "3", "尼古拉斯·塔利亚菲科", "7.0", "左后卫", "里昂老将。对阿舒尔右路速度"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "7", "罗德里戈·德保罗", "7.5", "右中场", "马竞。120分钟消耗最大"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "5", "莱安德罗·帕雷德斯", "7.5", "防守中场", "[首发变动] 入替阿尔马达, 防守硬度提升。斯卡洛尼: '健康时是世界最佳DM之一'"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "24", "恩佐·费尔南德斯", "7.5", "左中场", "切尔西。搭档帕雷德斯后更多参与进攻组织"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "20", "亚历克西斯·麦克阿利斯特", "8.0", "前腰", "[战术关键] 帕雷德斯入替后前压至10号位。利物浦核心"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "9", "胡利安·阿尔瓦雷斯", "7.5", "前锋", "[首发变动] 替劳塔罗。更灵活跑动+高位压迫"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "10", "利昂内尔·梅西 [C]", "9.0", "前锋", "20球世界杯纪录。连续8场进球。淘汰赛模式"], [600, 800, 3400, 700, 1200, 7258], false, true),
          ],
        }),
        bodyText("替补: 劳塔罗(禁区终结者) / 阿尔马达(MLS知悉球场) / 迪马利亚(10分钟魔力) / 帕拉西奥斯(中场体能) / 奥塔门迪(防空)"),

        subTitle("埃及 (4-5-1 防守阵型)"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [600, 800, 3400, 700, 1200, 7258],
          rows: [
            blueHeaderRow(["#", "号码", "球员", "评分", "位置", "表现点评"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "23", "穆斯塔法·舒贝尔", "6.5", "门将", "对澳大利亚点球战扑出2球"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "3", "穆罕默德·哈尼", "6.0", "右后卫", "对麦卡前压考验巨大"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "5", "拉米·拉比亚", "6.0", "中后卫(左)", "速度不足, 对阿尔瓦雷斯灵活跑动"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "2", "亚西尔·伊布拉希姆", "6.5", "中后卫(右)", "[关键] 原预测停赛, 实际首发! 身背黄牌须收敛"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "15", "卡里姆·哈菲兹", "6.0", "左后卫", "对德保罗/莫利纳右路, 压力大"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "14", "哈姆迪·法蒂", "6.5", "中场", "35岁队长。120分钟消耗, 仅4天恢复"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "19", "马尔万·阿提亚", "6.0", "中场", "拦截者。对恩佐+麦卡级别差距明显"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "17", "莫哈纳德·拉辛", "6.0", "中场", "[新增] 解禁复出。三后腰大巴信号"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "8", "埃马姆·阿舒尔", "6.5", "右边锋", "对塔利亚菲科, 右路最可能突破点"], [600, 800, 3400, 700, 1200, 7258], false, true),
            dataRowBoldFirst(["", "11", "穆斯塔法·齐科", "6.0", "左边锋", "替马尔穆什先发。攻击力显著下降"], [600, 800, 3400, 700, 1200, 7258]),
            dataRowBoldFirst(["", "10", "穆罕默德·萨拉赫 [C]", "9.0", "中锋", "16次创造机会赛事最高。但马尔穆什替补后埃及仅萨拉赫单核"], [600, 800, 3400, 700, 1200, 7258], false, true),
          ],
        }),
        bodyText("替补: 马尔穆什(€25M/德甲, 最大变数) / 特雷泽盖(经验) / 齐佐(创造力)"),

        // ===== FACTORS =====
        new Paragraph({ children: [new PageBreak()] }),
        sectionTitle("2. 因素导向表"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [5400, 1800, 6758],
          rows: [
            blueHeaderRow(["因素", "有利方", "理由"], [5400, 1800, 6758]),
            dataRowBoldFirst(["梅西=超巨破局能力: 20球+连续8场进球", "ARG ★★★", "任何人任何时刻可改变比分"], [5400, 1800, 6758], false, true),
            dataRowBoldFirst(["帕雷德斯入替: 阿根廷中场防守提升", "ARG ★★", "[新增] 佛得角恐慌后对症下药。麦卡前压释放进攻"], [5400, 1800, 6758]),
            dataRowBoldFirst(["阿尔瓦雷斯替劳塔罗: 更灵活跑动+压迫", "ARG ★", "[新增] 劳塔罗替补待命, 下半场可针对体能下降防线"], [5400, 1800, 6758], false, true),
            dataRowBoldFirst(["伊布拉希姆回归: 埃及最好中卫首发", "EGY ★★", "[注意] 原预测错误。埃及防线比预期强1档"], [5400, 1800, 6758]),
            dataRowBoldFirst(["马尔穆什替补: 埃及第二攻击核心缺阵", "ARG ★★★", "[最大利好] 萨拉赫失去最可靠搭档。反击速度减半。马尔穆什60'后出场方可发挥作用"], [5400, 1800, 6758], false, true),
            dataRowBoldFirst(["埃及三后腰(法蒂+阿提亚+拉辛): 大巴信号", "EGY ★★", "哈桑明确策略: 死守+萨拉赫单箭头"], [5400, 1800, 6758]),
            dataRowBoldFirst(["双方120分钟消耗: 均仅4天恢复", "均势偏ARG", "但阿根廷板凳深度远超埃及(劳塔罗/迪马利亚 vs 马尔穆什)"], [5400, 1800, 6758], false, true),
            dataRowBoldFirst(["身价比 6.9:1: EUR 807.5M vs EUR 116.48M", "ARG ★★", "明显差距(3:1-10:1), 阿根廷占优"], [5400, 1800, 6758]),
            dataRowBoldFirst(["室内球场: 气候受控", "均势", "纯实力对决。阿尔马达替补出场=准主场"], [5400, 1800, 6758], false, true),
            dataRowBoldFirst(["裁判: 弗朗索瓦·勒特谢尔(法国)", "均势", "法甲裁判, 身体对抗容忍度中等"], [5400, 1800, 6758]),
            dataRowBoldFirst(["伊布拉希姆身背黄牌: 再一黄=QF停赛", "ARG ★", "埃及防线核心须收敛铲球, 对梅西禁区突破不敢全力拦截"], [5400, 1800, 6758], false, true),
          ],
        }),

        // ===== UPSET RISK =====
        sectionTitle("3. 冷门风险评估: 中"),
        bodyText("1. 埃及三后腰大巴: 拉辛解禁+法蒂+阿提亚=纯防守型中场三人组。埃及明确来死守"),
        bodyText("2. 伊布拉希姆回归: 防线比原预测强, 埃及有能力守60分钟0-0"),
        bodyText("3. 但马尔穆什替补: 埃及反击仅剩萨拉赫一人, 爆冷所需的反击效率大幅下降"),
        bodyText("4. 阿根廷帕雷德斯入替: 更稳健但破大巴创造力相应下降(阿尔马达在替补席)"),
        bodyText("5. 梅西一人可破任何大巴: 这是阿根廷与其他强队不同的地方"),

        // ===== SCORE PREDICTION =====
        sectionTitle("4. 比分预测"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [3000, 1200, 9758],
          rows: [
            blueHeaderRow(["比分", "概率", "说明"], [3000, 1200, 9758]),
            dataRowBoldFirst(["阿根廷 2-1 埃及 [首选]", "~30%", "31'梅西远射先破。58'萨拉赫反击单刀扳平。72'替补劳塔罗角球头球锁定。埃及三后腰够好, 阿根廷难大胜"], [3000, 1200, 9758], true),
            dataRowBoldFirst(["阿根廷 2-0 埃及", "~25%", "梅西上半场破门。埃及体能下降后65'迪马利亚传中, 劳塔罗替补头球。马尔穆什75'才上场=太晚"], [3000, 1200, 9758], false, true),
            dataRowBoldFirst(["阿根廷 1-0", "~20%", "铁律15: 淘汰赛最常见比分(27%)。埃及大巴奏效。梅西38'任意球/点球制胜。埃及0射正"], [3000, 1200, 9758]),
            dataRowBoldFirst(["阿根廷 3-1 埃及", "~12%", "梅西23'+阿尔瓦雷斯39'=2-0半场。萨拉赫55'扳1球。劳塔罗79'锁定"], [3000, 1200, 9758], false, true),
            dataRowBoldFirst(["1-1 (加时)", "~8%", "铁律15: 必须入列。埃及大巴完美死守。萨拉赫75'反击先破, 梅西85'扳平。加时阿根廷板凳优势"], [3000, 1200, 9758]),
            dataRowBoldFirst(["0-0 (加时/点球)", "~5%", "互交白卷。萨拉赫被罗梅罗锁死。加时点球阿根廷马丁内斯优势"], [3000, 1200, 9758], false, true),
          ],
        }),
        bodyText(""),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [2000, 2800, 1200, 7958],
          rows: [
            blueHeaderRow(["类型", "比分", "半场", "进球者"], [2000, 2800, 1200, 7958]),
            dataRow(["首选", "ARG 2-1 EGY", "1-0", "梅西 31'(远射) / 萨拉赫 58'(反击单刀) / 劳塔罗 72'(角球头球,替补)"], [2000, 2800, 1200, 7958], true),
            dataRow(["备选1", "ARG 2-0 EGY", "1-0", "梅西 28'(禁区混战) / 劳塔罗 76'(迪马利亚传中头球)"], [2000, 2800, 1200, 7958], false, true),
            dataRow(["备选2", "ARG 1-0 EGY", "0-0", "梅西 55'(任意球)"], [2000, 2800, 1200, 7958]),
            dataRow(["备选3", "ARG 3-1 EGY", "2-0", "梅西 23' / 阿尔瓦雷斯 39' / 萨拉赫 55' / 劳塔罗 79'"], [2000, 2800, 1200, 7958], false, true),
            dataRow(["冷门", "1-1 (ARG点球胜)", "0-0", "萨拉赫 75'(反击) / 梅西 85'(禁区外)"], [2000, 2800, 1200, 7958]),
          ],
        }),

        // ===== INJURIES =====
        new Paragraph({ children: [new PageBreak()] }),
        sectionTitle("5. 伤病/停赛"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [1400, 4800, 7758],
          rows: [
            blueHeaderRow(["球队", "球员", "状态"], [1400, 4800, 7758]),
            dataRow(["EGY", "穆罕默德·阿卜杜勒莫内姆 CB", "[Out] 踝关节挫伤, 缺席本届"], [1400, 4800, 7758], false, true),
            dataRow(["EGY", "艾哈迈德·法图 LB", "[Out] 十字韧带断裂, 世界杯报销"], [1400, 4800, 7758]),
            dataRow(["EGY", "亚西尔·伊布拉希姆 CB", "[注意] 可出战, 身背黄牌! 再一黄=QF停赛"], [1400, 4800, 7758], false, true),
            dataRow(["EGY", "卡里姆·哈菲兹 LB", "[注意] 训练通过, R32肌肉轻伤已恢复"], [1400, 4800, 7758]),
            dataRow(["ARG", "尼古拉斯·冈萨雷斯 LW", "[注意] 踝关节问题。AS USA: '唯一真正伤病疑虑'"], [1400, 4800, 7758], false, true),
            dataRow(["ARG", "全队120分钟消耗", "[注意] 梅西/德保罗/奥塔门迪仅4天恢复"], [1400, 4800, 7758]),
          ],
        }),

        // ===== TEAM CLASSIFICATION =====
        sectionTitle("6. 强队分类"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [3500, 5229, 5229],
          rows: [
            blueHeaderRow(["维度", "阿根廷", "埃及"], [3500, 5229, 5229]),
            dataRow(["阵容总身价", "EUR 807.5M (T1)", "EUR 116.48M (T3)"], [3500, 5229, 5229], false, true),
            dataRow(["超巨密度", "梅西(超巨)+劳塔罗(核心)+麦卡(核心)", "萨拉赫(超巨), 但马尔穆什替补"], [3500, 5229, 5229]),
            dataRow(["分型", "超级巨星型: 梅西+多点攻击", "三后腰大巴策略, 专克体系型但对超级巨星型效果有限"], [3500, 5229, 5229], false, true),
            dataRow(["结论", "超级巨星型可高看破大巴", "大巴+萨拉赫单核: 防守可扛60分钟但进攻乏力"], [3500, 5229, 5229]),
          ],
        }),

        // ===== AFRICAN RESILIENCE =====
        sectionTitle("7. 亚非韧性评估: 埃及"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [3000, 1400, 9558],
          rows: [
            blueHeaderRow(["维度", "评级", "说明"], [3000, 1400, 9558]),
            dataRow(["低位防守", "★★★☆☆", "三后腰配置=明确大巴信号。伊布拉希姆回归。但4场0零封"], [3000, 1400, 9558], false, true),
            dataRow(["速度反击", "★★☆☆☆", "[降级] 马尔穆什替补, 萨拉赫单核。齐科+阿舒尔速度不如马尔穆什"], [3000, 1400, 9558]),
            dataRow(["定位球高点", "★★★☆☆", "伊布拉希姆+拉比亚提供身高。萨拉赫任意球直接威胁"], [3000, 1400, 9558], false, true),
            dataRow(["前30分钟", "★★★★☆", "对比利时1-1+点球胜澳大利亚, 抗压能力已证明"], [3000, 1400, 9558]),
            dataRow(["被压制不崩盘", "★★★★☆", "首支赢得世界杯点球的非洲球队, 加时+点球=完美压力测试"], [3000, 1400, 9558], false, true),
          ],
        }),
        bodyText("总分: 16/25 — 比原预测(17/25)降1分, 主因马尔穆什替补导致反击效率下降", { bold: true }),

        // ===== COACHING =====
        sectionTitle("8. 教练博弈"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [2800, 5580, 5578],
          rows: [
            blueHeaderRow(["场景", "斯卡洛尼 (ARG)", "哈桑 (EGY)"], [2800, 5580, 5578]),
            dataRow(["落后时", "迪马利亚换帕雷德斯→4-2-4; 劳塔罗+阿尔瓦雷斯双前锋; 阿尔马达换恩佐→创造力提升", "马尔穆什换齐科(60')→双核反击; 特雷泽盖换阿舒尔→边路加速"], [2800, 5580, 5578], false, true),
            dataRow(["领先时", "帕拉西奥斯换德保罗→中场体能; 奥塔门迪换利桑德罗→防空加固", "阿卜杜勒马吉德换拉比亚→5后卫; 全队10人回收"], [2800, 5580, 5578]),
            dataRow(["替补能力", "[高] 迪马利亚(10分钟魔力)/劳塔罗(终结者)/阿尔马达(MLS球场)", "[中] 马尔穆什出场时机=关键。60'前0-0出场=埃及反击升级。75'+才出场=太晚"], [2800, 5580, 5578], false, true),
            dataRow(["关键窗口", "上半场30-45': 帕雷德斯首发后麦卡前压", "60': 马尔穆什出场最可能时间。若0-0则爆冷窗口打开"], [2800, 5580, 5578]),
          ],
        }),

        // ===== SET PIECES =====
        sectionTitle("9. 定位球攻防"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [2800, 5580, 5578],
          rows: [
            blueHeaderRow(["维度", "阿根廷", "埃及"], [2800, 5580, 5578]),
            dataRow(["角球进攻", "罗梅罗+利桑德罗+劳塔罗(替补)=顶级头球", "伊布拉希姆+拉比亚=身高优势"], [2800, 5580, 5578], false, true),
            dataRow(["任意球", "梅西直接射门(淘汰赛模式)", "萨拉赫直接射门"], [2800, 5580, 5578]),
            dataRow(["防守", "佛得角失2球, 角球防守存在漏洞", "4场0零封"], [2800, 5580, 5578], false, true),
            dataRow(["结论", "阿根廷占优, 但角球防守需注意", " — "], [2800, 5580, 5578]),
          ],
        }),

        // ===== UPSET PATH =====
        sectionTitle("10. 冷门路径"),
        bodyText("如果埃及爆冷, 最可能路径:", { bold: true }),
        bodyText("1. 三后腰大巴死守前60分钟, 阿根廷围攻无果(类似佛得角上半场)"),
        bodyText("2. 55-65'萨拉赫利用反击, 利桑德罗/塔利亚菲科速度不足, 单刀破门"),
        bodyText("3. 伊布拉希姆(虽身背黄牌)指挥防线扛住阿根廷最后30分钟围攻"),
        bodyText("4. 马尔穆什65'出场, 双核反击, 阿根廷不敢全力压上"),
        bodyText("5. 拖入加时, 阿根廷老将(梅西38/迪马利亚38/奥塔门迪37)体能崩溃, 点球埃及胜"),
        bodyText("关键变量: 马尔穆什出场时间。若60分钟前出场且当时埃及0-0, 爆冷概率从8%升至15%。若75分钟才出场则为时太晚。", { bold: true, color: RED }),

        // ===== SUMMARY COMPARISON =====
        new Paragraph({ children: [new PageBreak()] }),
        sectionTitle("总结: 原预测 vs 首发修正"),
        new Table({
          width: { size: mainTblW, type: WidthType.DXA },
          columnWidths: [3000, 3800, 3800, 3358],
          rows: [
            blueHeaderRow(["维度", "原预测(媒体预测版)", "首发修正版", "变化"], [3000, 3800, 3800, 3358]),
            dataRow(["方向", "阿根廷胜", "阿根廷胜", "不变"], [3000, 3800, 3800, 3358], true),
            dataRow(["首选比分", "阿根廷 3-1", "阿根廷 2-1", "下调1球"], [3000, 3800, 3800, 3358], false, true),
            dataRow(["概率", "~35%", "~30%", "下降"], [3000, 3800, 3800, 3358]),
            dataRow(["核心逻辑", "萨拉赫+马尔穆什双核可取1球", "马尔穆什替补, 埃及反击减半+三后腰大巴更耐打", "更谨慎"], [3000, 3800, 3800, 3358], false, true),
            dataRow(["冷门风险", "中低", "中", "上调"], [3000, 3800, 3800, 3358]),
          ],
        }),
        noteText(""),
        bodyText("v20规则应用: 球员从ESPN API验证(非媒体预测) / 伊布拉希姆=突发利好埃及防线 / 马尔穆什替补=利好阿根廷 / 帕雷德斯+阿尔瓦雷斯=斯卡洛尼对症下药 / 铁律15: 1-0和1-1都列入", { bold: false }),
        bodyText(""),
        bodyText("生成: 北京时间 2026年7月7日 23:40 | ESPN API confirmed starters v2.0 | 裁判: Francois Letexier (FRA)", { color: "888888" }),
        bodyText("来源: ESPN API event=760509 / AS USA / Sporting News / FIFA官网 / CLAUDE.md v21", { color: "888888" }),
        bodyText("原预测文件: 2026年7月8日_两场预测.md (已废弃阿根廷部分)", { color: "888888" }),
      ],
    },
  ],
});

const outPath = "D:/ai/世界杯/2026-worldcup-predictions/2026年7月8日_阿根廷vs埃及_首发更新预测.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log("DOCX created: " + outPath + " (" + (buf.length / 1024).toFixed(1) + " KB)");
}).catch(err => {
  console.error("Error: " + err.message);
  process.exit(1);
});
