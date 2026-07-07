const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

const BLUE = "1A3A5C"; const WHITE = "FFFFFF"; const LIGHT_GRAY = "F2F2F2";
const LIGHT_GREEN = "E2EFDA"; const RED = "C00000"; const BLACK = "000000";
const DARK = "333333"; const LIGHT_BLUE = "D6E4F0";

const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };
const cm = { top: 60, bottom: 60, left: 100, right: 100 };

function hc(t, w) { return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: cm, verticalAlign: "center", children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: t, bold: true, font: "Microsoft YaHei", size: 17, color: WHITE })] })] }); }
function c(t, w, o = {}) {
  const kids = [];
  if (t.includes("**")) { t.split("**").forEach((p, i) => { if (p.length) kids.push(new TextRun({ text: p, bold: i % 2 === 1 || !!o.bold, font: "Microsoft YaHei", size: o.s || 16, color: o.col || DARK })); }); }
  else kids.push(new TextRun({ text: t, bold: !!o.bold, font: "Microsoft YaHei", size: o.s || 16, color: o.col || DARK }));
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: o.sh ? { fill: o.sh, type: ShadingType.CLEAR } : undefined, margins: cm, verticalAlign: "center", children: [new Paragraph({ alignment: o.al || AlignmentType.LEFT, children: kids })] });
}
function hr(ts, ws) { return new TableRow({ children: ts.map((t, i) => hc(t, ws[i])) }); }
function dr(ts, ws, g, gr) { const sh = g ? LIGHT_GREEN : (gr ? LIGHT_GRAY : undefined); return new TableRow({ children: ts.map((t, i) => c(t, ws[i], { sh })) }); }
function drB(ts, ws, g, gr) { const sh = g ? LIGHT_GREEN : (gr ? LIGHT_GRAY : undefined); return new TableRow({ children: ts.map((t, i) => c(t, ws[i], { bold: i === 0, sh })) }); }
function sec(t) { return new Paragraph({ spacing: { before: 200, after: 100 }, children: [new TextRun({ text: t, bold: true, font: "Microsoft YaHei", size: 26, color: BLUE })] }); }
function sub(t) { return new Paragraph({ spacing: { before: 140, after: 80 }, children: [new TextRun({ text: t, bold: true, font: "Microsoft YaHei", size: 22, color: DARK })] }); }
function bn(t, o = {}) { return new Paragraph({ spacing: { before: 40, after: 40 }, children: [new TextRun({ text: t, bold: o.bold, font: "Microsoft YaHei", size: 17, color: o.col || DARK })] }); }
function note(t) { return new Paragraph({ spacing: { before: 30, after: 30 }, children: [new TextRun({ text: t, font: "Microsoft YaHei", size: 15, color: "666666", italics: true })] }); }

const SW = 11906, SH = 16838, M = 1440;
const TW = SH - 2 * M; // 13958

const doc = new Document({
  styles: { default: { document: { run: { font: "Microsoft YaHei", size: 18 } } } },
  sections: [
    // COVER
    { properties: { page: { size: { width: SW, height: SH, orientation: PageOrientation.LANDSCAPE }, margin: { top: M, right: M, bottom: M, left: M } } },
      children: [
        new Paragraph({ spacing: { before: 2600 }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "2026世界杯 16强淘汰赛 复盘", font: "Microsoft YaHei", size: 36, bold: true, color: BLUE })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "阿根廷 3-2 埃及", font: "Microsoft YaHei", size: 44, bold: true, color: BLACK })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [new TextRun({ text: "ARG 3-2 EGY", font: "Microsoft YaHei", size: 28, color: "666666" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 160, after: 30 }, children: [new TextRun({ text: "0-2 到 3-2 — 79'/83'/90'+2' 13分钟3球世纪逆转", font: "Microsoft YaHei", size: 22, bold: true, color: RED })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "北京时间 2026年7月8日 00:00 | 梅赛德斯-奔驰球场, 亚特兰大 | 裁判: Francois Letexier (FRA)", font: "Microsoft YaHei", size: 18, color: DARK })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "数据来源: FIFA API (400021528) + ESPN API (760509)", font: "Microsoft YaHei", size: 16, color: "888888" })] }),
        new Paragraph({ children: [new PageBreak()] }),
      ] },
    // MAIN
    { properties: { page: { size: { width: SW, height: SH, orientation: PageOrientation.LANDSCAPE }, margin: { top: M, right: M, bottom: M, left: M } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "ARG 3-2 EGY | 7月8日复盘", font: "Microsoft YaHei", size: 14, color: "999999", italics: true })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "第 ", font: "Microsoft YaHei", size: 14, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 14, color: "999999" })] })] }) },
      children: [
        // SUMMARY
        sec("复盘汇总"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [2400, 11558], rows: [
          hr(["维度", "结果"], [2400, 11558]),
          drB(["最终比分", "阿根廷 3-2 埃及 (常规时间, 无需加时)"], [2400, 11558], false, true),
          drB(["半场", "0-1"], [2400, 11558]),
          drB(["方向", "[对] 阿根廷胜"], [2400, 11558], false, true),
          drB(["首选比分", "[错] 预测 2-1, 实际 3-2 (方向对, 进球数看低1球)"], [2400, 11558]),
          drB(["冷门风险", "中 — 即时一度90%埃及晋级, 最终阿根廷逆转 [对: 风险确实高]"], [2400, 11558], false, true),
        ] }),
        note(""),

        // TIMELINE
        sec("完整时间线"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [1200, 2000, 3400, 7158], rows: [
          hr(["时间", "事件", "球员", "比分"], [1200, 2000, 3400, 7158]),
          dr(["15'", "头球(角球)", "亚西尔·伊布拉希姆 (EGY)", "0-1"], [1200, 2000, 3400, 7158], false, true),
          dr(["21'", "黄牌", "埃及教练组成员", "—"], [1200, 2000, 3400, 7158]),
          dr(["~30'", "[关键] 点球罚丢!", "阿根廷 (球员待确认)", "仍是0-1"], [1200, 2000, 3400, 7158], false, true),
          dr(["HT", "半场 | 换人", "法蒂 IN / 阿舒尔 OUT (EGY)", "0-1"], [1200, 2000, 3400, 7158]),
          dr(["66'", "[关键] 双换人", "劳塔罗+冈萨雷斯 IN / 德保罗+塔利亚菲科 OUT (ARG)", "—"], [1200, 2000, 3400, 7158], false, true),
          dr(["67'", "[关键] 反击进球", "穆斯塔法·齐科 (EGY)", "0-2"], [1200, 2000, 3400, 7158]),
          dr(["73'", "换人 x2", "蒙铁尔 IN/莫利纳 OUT (ARG) | 特雷泽盖 IN/哈桑 OUT (EGY)", "—"], [1200, 2000, 3400, 7158], false, true),
          dr(["79'", "[逆转起点] 角球头球", "克里斯蒂安·罗梅罗 (ARG)", "1-2"], [1200, 2000, 3400, 7158]),
          dr(["80'", "换人", "马尔穆什 IN / 齐科 OUT (EGY)", "—"], [1200, 2000, 3400, 7158], false, true),
          dr(["83'", "[扳平] 禁区混战", "利昂内尔·梅西 (ARG)", "2-2"], [1200, 2000, 3400, 7158]),
          dr(["90'+2'", "[绝杀] 禁区外远射", "恩佐·费尔南德斯 (ARG)", "3-2"], [1200, 2000, 3400, 7158], false, true),
          dr(["90'+3'-90'+8'", "4黄牌 (EGY) / 换人x4", "舒贝尔/法蒂/教练组/阿提亚 黄牌", "—"], [1200, 2000, 3400, 7158]),
          dr(["FT", "完场", "阿根廷 3-2 埃及", "—"], [1200, 2000, 3400, 7158], false, true),
        ] }),
        note(""),

        // FINAL STATS
        new Paragraph({ children: [new PageBreak()] }),
        sec("最终数据对比"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [3500, 2400, 2400, 5658], rows: [
          hr(["统计", "阿根廷", "埃及", "解读"], [3500, 2400, 2400, 5658]),
          dr(["控球率", "63.6%", "36.4%", "阿根廷全程掌控球权"], [3500, 2400, 2400, 5658], false, true),
          dr(["射门/射正", "19/7", "5/2", "19射7正 vs 5射2正=2进球"], [3500, 2400, 2400, 5658]),
          dr(["被封堵", "4", "1", "埃及大巴用身体封了4次"], [3500, 2400, 2400, 5658], false, true),
          dr(["点球", "1射0进", "0", "[关键] 比赛的#1转折点"], [3500, 2400, 2400, 5658]),
          dr(["角球", "6", "1", "罗梅罗79'角球破门"], [3500, 2400, 2400, 5658], false, true),
          dr(["传中", "26 (8精准)", "8 (2精准)", "26次传中=阿根廷边路主导"], [3500, 2400, 2400, 5658]),
          dr(["扑救", "0", "4", "舒贝尔4扑救但仍失3球"], [3500, 2400, 2400, 5658], false, true),
          dr(["犯规", "13", "11", "—"], [3500, 2400, 2400, 5658]),
          dr(["黄牌", "0", "4+2(教练组)", "埃及在压力下崩溃"], [3500, 2400, 2400, 5658], false, true),
          dr(["传球", "602 (90%)", "349 (83%)", "—"], [3500, 2400, 2400, 5658]),
          dr(["解围", "14", "43", "43次解围=绝对大巴"], [3500, 2400, 2400, 5658], false, true),
          dr(["拦截", "7", "10", "三后腰最后的数据遗产"], [3500, 2400, 2400, 5658]),
          dr(["抢断(成功率)", "20 (75%)", "15 (53%)", "—"], [3500, 2400, 2400, 5658], false, true),
        ] }),
        note(""),

        // FACTOR REVIEW
        sec("预测因素核查"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [4800, 1200, 5158, 2800], rows: [
          hr(["赛前因素", "方向", "实际兑现", "评分"], [4800, 1200, 5158, 2800]),
          dr(["梅西=超巨破局能力", "ARG ★★★", "83'扳平球。0-2落后时全队唯一保持冷静的人", "[对]"], [4800, 1200, 5158, 2800], false, true),
          dr(["帕雷德斯入替: 防守提升", "ARG ★★", "半场前0射门, 但定位球丢球与他无关", "[半对]"], [4800, 1200, 5158, 2800]),
          dr(["阿尔瓦雷斯替劳塔罗", "ARG ★", "阿尔瓦雷斯0威胁, 劳塔罗66'上场改变比赛", "[错: 劳塔罗才该首发]"], [4800, 1200, 5158, 2800], false, true),
          dr(["伊布拉希姆回归", "EGY ★★", "15'头球! 1球+防线核心", "[对]"], [4800, 1200, 5158, 2800]),
          dr(["马尔穆什替补", "ARG ★★★", "80'才上场时已2-2, 因子正确但被齐科打脸", "[半对]"], [4800, 1200, 5158, 2800], false, true),
          dr(["埃及三后腰大巴", "EGY ★★", "43次解围=完美执行, 撑了79分钟", "[对]"], [4800, 1200, 5158, 2800]),
          dr(["定位球: 伊布拉希姆身高", "EGY ★★★", "15'头球破门! 预测中最强调的埃及武器", "[对]"], [4800, 1200, 5158, 2800], false, true),
          dr(["埃及速度反击: 降为★★☆☆☆", "EGY", "齐科67'反击进球: 降级错了", "[错]"], [4800, 1200, 5158, 2800]),
          dr(["齐科评分6.0", "—", "1球, 决定性表现。6.0是本场最大评分错误", "[错]"], [4800, 1200, 5158, 2800], false, true),
          dr(["舒贝尔评分6.5", "—", "4次扑救+扑出点球。至少应该7.5-8.0", "[错]"], [4800, 1200, 5158, 2800]),
        ] }),
        note(""),

        // KEY TURNING POINTS
        new Paragraph({ children: [new PageBreak()] }),
        sec("比赛四大转折点"),
        sub("转折点1 (~30'): 阿根廷点球罚丢 — 心理崩盘"),
        bn("此时0-1落后, 点球是黄金扳平机会。舒贝尔扑出/迫使打飞: 这是他的第三场世界杯扑出点球(对澳大利亚已证明)。如果进了=1-1, 完全不同的比赛。阿根廷随后长达37分钟无进球(30'到67'还被埃及再进一球)。"),
        sub("转折点2 (66'): 斯卡洛尼双换人 — 比赛的真正起点"),
        bn("劳塔罗换德保罗+冈萨雷斯换塔利亚菲科=从4-1-3-2变成3-4-3。但换人后1分钟, 齐科就进了0-2。看似灾难, 实际上这释放了阿根廷的进攻本能。"),
        sub("转折点3 (79'-83'): 4分钟2球 — 从0-2到2-2"),
        bn("79': 罗梅罗角球头球, 定位球终于兑现(6个角球, 这个进了)。83': 梅西禁区混战: 不是最漂亮的进球, 但这是梅西在0-2落后时做的事。4分钟内从'卫冕冠军出局'到'世纪逆转在望'。埃及在83'后精神崩溃: 舒贝尔/法蒂/教练组黄牌=全线失控。"),
        sub("转折点4 (90'+2'): 恩佐绝杀 — 历史"),
        bn("禁区外远射。26次传中中最不可能是这一次, 但恩佐把球砸进了。阿根廷第19脚射门, 第7次射正, 第3个进球。埃及43次解围, 最后1次没做到。"),

        // TACTICAL REVIEW
        sec("战术回顾"),
        sub("上半场: 斯卡洛尼的帕雷德斯陷阱"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [3500, 10458], rows: [
          hr(["问题", "详情"], [3500, 10458]),
          drB(["阵型 4-1-3-2", "帕雷德斯单后腰, 恩佐+德保罗+麦卡三人挤在中路"], [3500, 10458], false, true),
          drB(["0射门(前25分钟)", "埃及三后腰一对一贴死阿根廷中场"], [3500, 10458]),
          drB(["梅西回撤过深", "必须到中圈才能接球, 远离禁区"], [3500, 10458], false, true),
          drB(["边路宽度为零", "莫利纳+塔利亚菲科双双被封锁"], [3500, 10458]),
          drB(["定位球防守崩盘", "利桑德罗(175cm) vs 伊布拉希姆=身高错位"], [3500, 10458], false, true),
        ] }),
        note(""),
        sub("下半场: 三后卫赌赢"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [4800, 9158], rows: [
          hr(["调整", "效果"], [4800, 9158]),
          drB(["冈萨雷斯打左翼卫", "提供边路宽度, 全场26次传中"], [4800, 9158], false, true),
          drB(["蒙铁尔换莫利纳(73')", "右路新鲜体能"], [4800, 9158]),
          drB(["劳塔罗进禁区", "支点作用 vs 阿尔瓦雷斯的无存在感"], [4800, 9158], false, true),
          drB(["梅西移到右路", "避开三后腰中央绞杀"], [4800, 9158]),
          drB(["最终形态: 3-4-3全线压上", "19射7正, 6角球, 26传中"], [4800, 9158], false, true),
        ] }),
        note(""),
        sub("埃及: 哈桑的79分钟大师课 + 13分钟噩梦"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [2400, 11558], rows: [
          hr(["阶段", "表现"], [2400, 11558]),
          drB(["0-79'", "完美大巴: 43次解围, 10次拦截。定位球1-0。反击2-0。"], [2400, 11558], false, true),
          drB(["79'-90'+", "全线崩溃。4张黄牌(含2张教练组)。舒贝尔从神变凡人。"], [2400, 11558]),
          drB(["核心错误", "法蒂(35岁/120分钟消耗)换阿舒尔=反击速度降为零。哈桑过早放弃进攻。"], [2400, 11558], false, true),
        ] }),
        note(""),

        // PLAYER RATINGS
        new Paragraph({ children: [new PageBreak()] }),
        sec("球员评分 (赛后修正)"),
        sub("阿根廷"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [600, 800, 2800, 900, 900, 800, 6158], rows: [
          hr(["#", "号码", "球员", "赛前", "赛后", "变化", "理由"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "23", "埃米利亚诺·马丁内斯", "8.5", "7.0", "↓", "2次被射正=2个丢球。没有重要扑救"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "26", "莫利纳", "7.0", "6.0", "↓", "73'被换下, 边路进攻无效"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "13", "克里斯蒂安·罗梅罗", "8.0", "9.0", "↑", "[MOTM候选] 79'角球头球=逆转起点。全场最佳中卫"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "6", "利桑德罗·马丁内斯", "8.0", "7.0", "↓", "15'对伊布拉希姆失位。身高问题无法回避"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "3", "塔利亚菲科", "7.0", "5.5", "↓", "66'被换下=承认失败。上半场左路完全无进攻贡献"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "7", "德保罗", "7.5", "6.0", "↓", "120分钟消耗兑现。66'被换下前0关键传球"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "5", "帕雷德斯", "7.5", "6.5", "↓", "上半场0进攻贡献。斯卡洛尼的战术选择问题"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "24", "恩佐·费尔南德斯", "7.5", "9.0", "↑", "[MOTM] 90'+2'绝杀! 全场跑动最多"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "20", "麦克阿利斯特", "8.0", "7.0", "↓", "上半场被三后腰锁死。下半场好转但非决定性"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "9", "阿尔瓦雷斯", "7.5", "5.5", "↓", "0射门。埃及大巴对他无效"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "10", "梅西 [C]", "9.0", "9.0", "—", "83'扳平。21球纪录。0-2落后时唯一不慌乱的人"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "22", "劳塔罗 (66'替补)", "7.5", "8.5", "↑", "上场后改变比赛。禁区支点=阿根廷进攻质变"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "15", "冈萨雷斯 (66'替补)", "—", "8.0", "—", "左翼宽度=26传中的来源"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "4", "蒙铁尔 (73'替补)", "—", "7.0", "—", "右路新鲜体能"], [600, 800, 2800, 900, 900, 800, 6158]),
        ] }),
        note(""),
        sub("埃及"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [600, 800, 2800, 900, 900, 800, 6158], rows: [
          hr(["#", "号码", "球员", "赛前", "赛后", "变化", "理由"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "23", "穆斯塔法·舒贝尔", "6.5", "8.0", "↑", "4次扑救+扑出点球。79'前是MOTM。3丢球不是他的错"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "2", "亚西尔·伊布拉希姆", "6.5", "8.5", "↑", "15'头球! 43次解围的核心。但身背黄牌后79'角球失位"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "5", "拉米·拉比亚", "6.0", "7.0", "↑", "上半场对阿尔瓦雷斯完美。79'后体能崩溃"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "3", "哈尼", "6.0", "6.0", "—", "被冈萨雷斯打爆"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "15", "哈菲兹", "6.0", "6.0", "—", "26次传中=左路是阿根廷主攻方向"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "14", "哈姆迪·法蒂", "6.5", "6.0", "↓", "HT上场加固中场, 35岁+120分钟消耗=79'后消失"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "19", "阿提亚", "6.0", "7.0", "↑", "10次拦截。三后腰最好的一环。90'+8'黄牌=崩溃标志"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "17", "拉辛", "6.0", "6.5", "↑", "上半场锁死麦卡。90'+6'被换下时已经耗尽"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "8", "阿舒尔", "6.5", "5.5", "↓", "HT被换下=上半场右路无贡献"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
          dr(["", "11", "穆斯塔法·齐科", "6.0→低估", "8.0", "↑↑", "1球。67'打进0-2。本场最大的个人打脸。赛后评分低估了€8M"], [600, 800, 2800, 900, 900, 800, 6158]),
          dr(["", "10", "萨拉赫", "9.0", "6.5", "↓", "0射门。被罗梅罗锁死一整场。马尔穆什80'才上, 太晚了"], [600, 800, 2800, 900, 900, 800, 6158], false, true),
        ] }),
        note(""),

        // LESSONS
        new Paragraph({ children: [new PageBreak()] }),
        sec("七大教训"),
        sub("1. [关键] 齐科6.0 — 禁止用身价单维度给非欧洲球员评分"),
        bn("我们的评分: '替马尔穆什先发。EUR 8M=攻击力相比马尔穆什显著下降' = 6.0。实际: 1球, 67'打进0-2。整场埃及最有威胁的攻击手。教训: 身价是欧洲联赛的市场定价, 不等于球员在国家队模式下的实际能力。对非欧洲联赛球员的身价折价必须设下限(如最低6.5, 除非有明确数据证明其无能)。"),
        sub("2. [对] 定位球高度差=可预测的进球路径 — 下次必须写入首选进球方式"),
        bn("预测明确写了'伊布拉希姆+拉比亚=身高优势'+'罗梅罗(185cm)+利桑德罗(175cm)'。15'伊布拉希姆头球=此因子完全兑现。但没有写入'最可能的进球方式'。教训: 当定位球有明确身高错位时, 不仅写入因素表(EGY [重要][重要][重要]), 还要写入比分预测的进球详情。"),
        sub("3. 斯卡洛尼用帕雷德斯换阿尔马达=0射门前25分钟 — '防守优先'在落后时是毒药"),
        bn("帕雷德斯首发=4-1-3-2=上半场前25分钟0射门。比赛进程完全推翻了斯卡洛尼的逻辑: 定位球先丢了, 防守没稳住, 进攻创造力也没了。教训: 淘汰赛中'先稳后攻'策略只有在0-0时有效。一旦定位球先丢, 必须立刻换回攻击阵。斯卡洛尼等到66分钟才换=太晚。"),
        sub("4. 劳塔罗必须首发 — 阿尔瓦雷斯对大巴无效"),
        bn("阿尔瓦雷斯0射门, 66'被战术性替换。劳塔罗上场后=阿根廷禁区有了支点+头球威胁=进攻质变。教训: 面对明确的大巴球队, 需要禁区支点型中锋(劳塔罗), 不需要空间跑动型前锋(阿尔瓦雷斯)。这是斯卡洛尼的首发选择错误。"),
        sub("5. 42次解围=79'后崩盘 — 大巴的体能瓶颈是真实存在的"),
        bn("埃及撑了79分钟(42次解围)。79'角球失守=4分钟内连丢2球=精神崩溃。研究支撑: 大巴的物理极限约75-80分钟。持续解围+无球跑动+心理压力=肌肉疲劳+注意力下降。42次解围后的注意力断崖不是偶然, 是生理现象。"),
        sub("6. 哈桑的换人错误: 法蒂上/阿舒尔下+马尔穆什80'才上=自断反击"),
        bn("哈桑HT换上35岁法蒂加固中场=主动放弃右路反击。马尔穆什80'才上=0-2后唯一的反击希望来得太晚。教训: 对超级巨星型强队, 2-0领先时反击武器比防守武器更重要。哈桑应该60'上马尔穆什而非80'。"),
        sub("7. [待验证] 点球罚丢的心理传染 — 未来预测需要'点球后遗症'因子"),
        bn("阿根廷约30'点球罚丢。此后长达37分钟无进球, 直到79'罗梅罗角球才破荒。点球罚丢不仅是少了一个进球, 更是全队心理被打击。舒贝尔扑出点球后, 埃及防线信心爆棚, 这是他们撑到67'的精神燃料。待验证假设: 淘汰赛中点球罚丢=后续进攻效率下降=需要至少30分钟恢复。本场是1个数据点, 需要更多样本。"),
        note(""),

        // ACCURACY
        sec("预测准确度评分"),
        new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [3800, 3200, 3200, 3758], rows: [
          hr(["维度", "赛前预测", "实际", "评分"], [3800, 3200, 3200, 3758]),
          dr(["方向", "阿根廷胜", "阿根廷胜", "[对]"], [3800, 3200, 3200, 3758], false, true),
          dr(["首选定性", "双方进球", "双方进球(3+2=5球)", "[对]"], [3800, 3200, 3200, 3758]),
          dr(["首选比分", "2-1", "3-2", "[错] 看低1球"], [3800, 3200, 3200, 3758], false, true),
          dr(["埃及进球来源", "定位球(伊布拉希姆)", "定位球(伊布拉希姆15')", "[对]"], [3800, 3200, 3200, 3758]),
          dr(["逆转路径", "劳塔罗+冈萨雷斯替补", "劳塔罗+冈萨雷斯66'上场", "[对]"], [3800, 3200, 3200, 3758], false, true),
          dr(["冷门风险", "中", "即时一度90%埃及晋级", "[对]"], [3800, 3200, 3200, 3758]),
          dr(["埃及大巴", "三后腰 [重要][重要]", "43次解围", "[对]"], [3800, 3200, 3200, 3758], false, true),
          dr(["埃及反击", "降为[重要][重要][重要][重要][重要]", "齐科67'进球=打脸", "[错]"], [3800, 3200, 3200, 3758]),
          dr(["齐科评分", "6.0", "8.0", "[错]"], [3800, 3200, 3200, 3758], false, true),
          dr(["舒贝尔评分", "6.5", "8.0", "[错]"], [3800, 3200, 3200, 3758]),
          dr(["阿尔瓦雷斯vs劳塔罗", "阿尔瓦雷斯合理", "劳塔罗才该首发", "[错]"], [3800, 3200, 3200, 3758], false, true),
        ] }),
        bn("综合: 5对 / 6错。方向对, 过程对, 比分错, 球员评分两个严重错误。"),
        note(""),

        // CONCLUSION
        new Paragraph({ children: [new PageBreak()] }),
        sec("最终总结"),
        bn("埃及打了79分钟他们人生中最伟大的比赛。伊布拉希姆的头球、舒贝尔的神扑、齐科的反击: 42次解围, 10次拦截, 一部完美的防守反击电影。", { bold: false }),
        bn("然后梅西出现了。83分钟, 0-2落后, 21个世界杯进球, 一个扳平球。4分钟后恩佐远射绝杀。", { bold: false }),
        bn("这不是战术的胜利, 这是超级巨星型球队的定义: 即使大巴完美执行了79分钟, 即使点球罚丢了, 即使0-2落后了, 梅西+恩佐+罗梅罗三个人在13分钟内用三个进球告诉你: 体系可以锁死99%的球队, 但超级巨星型是那1%的例外。", { bold: true }),
        bn("埃及值得全世界的尊重。他们不是输给了战术, 他们输给了梅西。", { bold: true }),
        bn(""),
        bn("阿根廷晋级QF, 对手: 瑞士 vs 哥伦比亚 胜者。", { bold: true, col: BLUE }),
        bn(""),
        note("复盘生成: 北京时间 2026年7月8日 01:30 | 数据来源: FIFA API (400021528) + ESPN API (760509)"),
        note("预测文件: 2026年7月8日_阿根廷vs埃及_首发更新预测.md"),
      ],
    },
  ],
});

const out = "D:/ai/世界杯/2026-worldcup-predictions/2026年7月8日_阿根廷vs埃及_复盘.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(out, buf);
  console.log(`DOCX: ${out} (${(buf.length/1024).toFixed(1)} KB)`);
}).catch(e => { console.error(e.message); process.exit(1); });
