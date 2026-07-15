const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, PageOrientation, BorderStyle, WidthType, ShadingType,
        PageNumber, PageBreak } = require('docx');

// Colors
const DEEP_BLUE = '1B3A5C';
const WHITE = 'FFFFFF';
const LIGHT_GRAY = 'F2F2F2';
const LIGHT_GREEN = 'E2EFDA';
const RED = 'C00000';
const BLACK = '000000';
const BORDER_GRAY = 'CCCCCC';

// Font
const FONT = 'Microsoft YaHei';
const FONT_SIZE = 18; // 9pt
const FONT_SIZE_SM = 16; // 8pt
const FONT_SIZE_TITLE = 36; // 18pt
const FONT_SIZE_H1 = 28; // 14pt
const FONT_SIZE_H2 = 24; // 12pt
const FONT_SIZE_H3 = 20; // 10pt

// Borders
const cellBorder = { style: BorderStyle.SINGLE, size: 1, color: BORDER_GRAY };
const borders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const noBorders = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };
const bottomBorder = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.SINGLE, size: 2, color: DEEP_BLUE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

// Helper functions
function txt(text, opts = {}) {
    return new TextRun({ text, font: FONT, size: opts.size || FONT_SIZE, bold: opts.bold || false, color: opts.color || BLACK, ...opts });
}

function p(children, opts = {}) {
    return new Paragraph({ children, spacing: { before: opts.before || 60, after: opts.after || 60 }, alignment: opts.alignment || AlignmentType.LEFT, ...opts });
}

function h1(text) {
    return new Paragraph({
        children: [txt(text, { size: FONT_SIZE_H1, bold: true, color: DEEP_BLUE })],
        spacing: { before: 300, after: 120 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: DEEP_BLUE, space: 4 } }
    });
}

function h2(text) {
    return new Paragraph({
        children: [txt(text, { size: FONT_SIZE_H2, bold: true, color: DEEP_BLUE })],
        spacing: { before: 200, after: 80 }
    });
}

function h3(text) {
    return new Paragraph({
        children: [txt(text, { size: FONT_SIZE_H3, bold: true, color: RED })],
        spacing: { before: 160, after: 60 }
    });
}

function cell(text, opts = {}) {
    const runs = Array.isArray(text) ? text : [txt(text, opts)];
    return new TableCell({
        borders,
        width: opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
        shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
        margins: { top: 50, bottom: 50, left: 80, right: 80 },
        verticalAlign: opts.vAlign || 'center',
        children: [new Paragraph({ children: runs, alignment: opts.alignment || AlignmentType.CENTER })]
    });
}

function headerCell(text, width) {
    return cell([txt(text, { bold: true, color: WHITE, size: FONT_SIZE_SM })], { shading: DEEP_BLUE, width });
}

function dataCell(text, width, isGreen, isBold) {
    return cell([txt(text, { bold: isBold || false, size: FONT_SIZE_SM })], { shading: isGreen ? LIGHT_GREEN : undefined, width });
}

function grayCell(text, width) {
    return cell([txt(text, { size: FONT_SIZE_SM })], { shading: LIGHT_GRAY, width });
}

// Build tables
const A4_CONTENT_WIDTH = 12440; // Landscape A4 content width (297mm - margins in DXA)

function buildFinalTable() {
    const colW = [1800, 2200, 2200, 2200, 2400, 1640]; // sum = 12440
    const hdr = new TableRow({ children: [
        headerCell('项目', colW[0]), headerCell('详情', colW[1]), headerCell('', colW[2]), headerCell('', colW[3]), headerCell('', colW[4]), headerCell('', colW[5])
    ], tableHeader: true });

    const rows = [
        ['比赛', '四分之一决赛 Match 100', '', '', '', ''],
        ['比分', 'ARG 3-1 SUI (加时)', '', '', '', ''],
        ['半场', '1-0 (麦卡利斯特 10\')', '', '', '', ''],
        ['全场 (90\')', '1-1 (恩多耶 67\' 扳平)', '', '', '', ''],
        ['加时', '阿尔瓦雷斯 112\' / 劳塔罗 120+1\'', '', '', '', ''],
        ['红牌', '恩博洛 72\' (两黄变一红)', '', '', '', ''],
        ['场地', 'Arrowhead Stadium, 堪萨斯城', '', '', '', ''],
        ['裁判', 'Joao Pinheiro (葡萄牙) / VAR: Michael Barwegen', '', '', '', ''],
    ].map((r, i) => new TableRow({ children: [
        cell([txt(r[0], { bold: true, size: FONT_SIZE_SM })], { width: colW[0], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[1], { size: FONT_SIZE_SM })], { width: colW[1] + colW[2] + colW[3] + colW[4] + colW[5], alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
    ]}));

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW, rows: [hdr, ...rows] });
}

function buildTimelineTable() {
    const colW = [800, 1800, 9860]; // sum = 12460 ~ close enough
    const events = [
        ['0\'', '开球', '上半场开始'],
        ['10\'', '[GOAL] 麦卡利斯特 1-0', '梅西角球传中->麦卡利斯特头球破门(左下角)'],
        ['23\'', '补水暂停', '强制补水'],
        ['44\'', '[黄] 恩博洛 (SUI)', '恶劣犯规->第一张黄牌'],
        ['45\'+4\'', '恩多耶受伤', '短暂治疗后继续'],
        ['HT', 'ARG 1-0 SUI', '射门 3-3 / 控球 40.5%-59.5%'],
        ['45\'', '下半场开始', '—'],
        ['56\'', '帕雷德斯受伤', '短暂治疗后继续'],
        ['67\'', '[GOAL] 恩多耶 1-1', 'R.罗德里格斯直塞->恩多耶右脚小角度破门. SUI 5射正 vs ARG 1射正'],
        ['72\'', '[红] 恩博洛 罚下', '两黄变一红. SUI 10人应战'],
        ['75\'', '下半场补水', '—'],
        ['78\'', '[换] ARG', '尼科-冈萨雷斯 IN / 塔利亚菲科 OUT'],
        ['85\'', '[换] ARG 双换', '劳塔罗 IN / 德保罗 OUT; 蒙铁尔 IN / 莫利纳 OUT'],
        ['86\'', '[换] SUI 三连换', '维德默/阿姆杜尼/穆海姆 IN; 索乌/恩多耶/里德 OUT'],
        ['90\'+5\'', '[换] SUI', '科梅特 IN / R.罗德里格斯 OUT'],
        ['FT', 'ARG 1-1 SUI', '90分钟结束->进入加时'],
        ['90\' ET', '[换] ARG', '阿尔马达 IN / 恩佐 OUT'],
        ['96\' ET', '[换] SUI', '亚沙里 IN / 扎卡里亚 OUT'],
        ['97\' ET', '[黄] 阿尔马达 (ARG)', '恶劣犯规'],
        ['98\' ET', '[黄] 劳塔罗 (ARG)', '恶劣犯规'],
        ['105\' ET', '[换] ARG', '奥塔门迪 IN / 罗梅罗 OUT'],
        ['110\' ET', '[换] ARG', 'J.M.洛佩斯 IN / 帕雷德斯 OUT (受伤)'],
        ['112\' ET', '[GOAL] 阿尔瓦雷斯 2-1', 'J.M.洛佩斯助攻->禁区外右脚打入右上角. 世界波!'],
        ['114\' ET', '[黄] J.M.洛佩斯 (ARG)', '黄牌'],
        ['115\' ET', '[换] SUI', '巴尔加斯 IN / 弗罗伊勒 OUT'],
        ['120+1\' ET', '[GOAL] 劳塔罗 3-1', '快速反击->禁区中路右脚打入右下角. 杀死比赛'],
        ['120+4\'', '全场结束', 'ARG 3-1 SUI (AET)'],
    ];

    const rows = events.map((e, i) => new TableRow({ children: [
        cell([txt(e[0], { bold: true, size: FONT_SIZE_SM })], { width: colW[0], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(e[1], { size: FONT_SIZE_SM })], { width: colW[1], alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(e[2], { size: FONT_SIZE_SM })], { width: colW[2], alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
    ]}));

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW, rows: [new TableRow({ tableHeader: true, children: [
        headerCell('分钟', colW[0]), headerCell('事件', colW[1]), headerCell('细节', colW[2])
    ]}), ...rows] });
}

function buildPredictionComparisonTable() {
    const colW = [800, 2200, 1200, 2200, 1200, 1440, 1440, 1440];
    // Using a simpler layout
    const colW2 = [800, 2500, 1200, 2500, 1200, 2340];

    const predictions = [
        ['首选', 'ARG 1-0', '~22%', '—', '', '[错]'],
        ['备选1', '0-0 (加时)', '~20%', '—', '', '[错]'],
        ['备选2', 'ARG 2-0', '~16%', '—', '', '[错]'],
        ['备选3', '1-1 (加时)', '~13%', '—', '', '[错]'],
        ['备选4', 'ARG 2-1', '~10%', '—', '', '[错]'],
        ['备选5', 'SUI 1-0', '~8%', '—', '', '[错]'],
        ['备选6', 'ARG 3-0', '~6%', '—', '', '[错]'],
        ['备选7', 'ARG 3-1', '~4%', '3-1 (AET)', '', '[对]'],
        ['半场', '0-0', '~35%', '1-0 (10\')', '', '[错]'],
        ['方向', 'ARG晋级', '~70-73%', 'ARG晋级', '', '[对]'],
    ];

    const rows = predictions.map((r, i) => {
        const isGreen = r[5] === '[对]';
        const isRed = r[5] === '[错]';
        return new TableRow({ children: [
            cell([txt(r[0], { bold: true, size: FONT_SIZE_SM })], { width: colW2[0], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[1], { size: FONT_SIZE_SM })], { width: colW2[1], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[2], { size: FONT_SIZE_SM })], { width: colW2[2], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[3], { size: FONT_SIZE_SM, bold: r[5] === '[对]' })], { width: colW2[3], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[4], { size: FONT_SIZE_SM })], { width: colW2[4], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[5], { size: FONT_SIZE_SM, color: isGreen ? '006100' : (isRed ? RED : BLACK), bold: true })], { width: colW2[5], shading: isGreen ? LIGHT_GREEN : (i % 2 === 1 ? LIGHT_GRAY : undefined) }),
        ]});
    });

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW2, rows: [new TableRow({ tableHeader: true, children: [
        headerCell('#', colW2[0]), headerCell('预测', colW2[1]), headerCell('概率', colW2[2]), headerCell('实际', colW2[3]), headerCell('', colW2[4]), headerCell('判定', colW2[5])
    ]}), ...rows] });
}

function buildTacticalTable() {
    const colW = [1200, 5240, 4000, 2000];

    const items = [
        ['1', '扎卡里亚RB客串 vs 梅西 = QF最大对位错配', '梅西10\'角球助攻--定位球而非对位突破. 扎卡里亚96\'被换下. 对位错配存在但不是进球来源', '半对'],
        ['2', 'SUI大巴防守 = 精英级 (5/5满分)', 'SUI控球53.9%--完全不是大巴! 9射门5射正 vs ARG 5射1射正. SUI主动进攻', '[大错]'],
        ['3', 'ARG慢开局 (半场0-0 35%)', '10\'就破门. 20元+7元投注10分钟归零', '[大错]'],
        ['4', '曼扎姆比缺席->SUI反击锐减40%', '恩多耶67\'进球+R.罗德里格斯助攻. SUI反击不仅存在且比ARG更危险', '[大错]'],
        ['5', '0-0半场 = 最大分析优势 (+5-10%)', '半场1-0. 优势方向完全反向', '[大错]'],
        ['6', '恩博洛vs利桑德罗身体优势', '恩博洛仅44\'犯规+72\'红牌. 但SUI其他攻击手(恩多耶/R.罗德里格斯)填补', '半对'],
        ['7', '科贝尔世界级门将', 'ARG 3球但1球角球(门将难救)/2球加时. 科贝尔非拯救者但也不丢脸', '中性'],
        ['8', '梅西 anytime 进球', '0进球 (10\'助攻)--39岁梅西未破门', '[错]'],
        ['9', 'ARG阵容完整 > SUI缺核', 'ARG加时深度兑现--阿尔瓦雷斯112\'+劳塔罗120+1\'替补决胜. 板凳差价最终兑现', '[对]'],
        ['10', '恩多耶速度 vs 塔利亚菲科 32岁', '恩多耶67\'进球(对手侧边路)+制造多次威胁', '[对]'],
    ];

    const rows = items.map((r, i) => {
        let shade = i % 2 === 1 ? LIGHT_GRAY : undefined;
        let verdictColor = BLACK;
        if (r[3] === '[对]') verdictColor = '006100';
        else if (r[3].includes('大错') || r[3] === '[错]') verdictColor = RED;
        return new TableRow({ children: [
            cell([txt(r[0], { bold: true, size: FONT_SIZE_SM })], { width: colW[0], shading: shade }),
            cell([txt(r[1], { size: FONT_SIZE_SM })], { width: colW[1], alignment: AlignmentType.LEFT, shading: shade }),
            cell([txt(r[2], { size: FONT_SIZE_SM })], { width: colW[2], alignment: AlignmentType.LEFT, shading: shade }),
            cell([txt(r[3], { size: FONT_SIZE_SM, bold: true, color: verdictColor })], { width: colW[3], shading: shade }),
        ]});
    });

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW, rows: [new TableRow({ tableHeader: true, children: [
        headerCell('#', colW[0]), headerCell('赛前核心判断', colW[1]), headerCell('场上实际', colW[2]), headerCell('判定', colW[3])
    ]}), ...rows] });
}

function buildBettingTable() {
    const colW = [900, 2200, 800, 1000, 800, 1200, 5340];

    const bets = [
        ['1', 'ARG晋级', '30', '~1.33', '[赢]', '+9.9', '方向正确--最可靠的锚'],
        ['2', '0-0半场', '20', '~2.50', '[输]', '-20', '铁律19--10\'破门'],
        ['3', '小于2.5球', '15', '~1.69', '[输]', '-15', '3-1 = 4球. 加时120+1\'杀死'],
        ['4', 'SUI +1.5', '10', '~1.43', '[输]', '-10', 'ARG加时净胜2球= -1.5 AET'],
        ['5', 'ARG 1-0波胆', '8', '~5.50', '[输]', '-8', '恩多耶67\'扳平'],
        ['6', '0-0波胆', '7', '~5.50', '[输]', '-7', '10\'即死'],
        ['7', 'ARG 2-0波胆', '5', '~7.00', '[输]', '-5', '恩多耶进球杀死'],
        ['8', '梅西anytime进球', '5', '~1.50', '[输]', '-5', '有助攻但未进球'],
    ];

    const rows = bets.map((r, i) => {
        const isWin = r[4] === '[赢]';
        return new TableRow({ children: [
            cell([txt(r[0], { size: FONT_SIZE_SM })], { width: colW[0], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[1], { size: FONT_SIZE_SM })], { width: colW[1], alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[2], { size: FONT_SIZE_SM })], { width: colW[2], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[3], { size: FONT_SIZE_SM })], { width: colW[3], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[4], { size: FONT_SIZE_SM, bold: true, color: isWin ? '006100' : RED })], { width: colW[4], shading: isWin ? LIGHT_GREEN : (i % 2 === 1 ? LIGHT_GRAY : undefined) }),
            cell([txt(r[5], { size: FONT_SIZE_SM, color: r[5].startsWith('+') ? '006100' : RED, bold: true })], { width: colW[5], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
            cell([txt(r[6], { size: FONT_SIZE_SM })], { width: colW[6], alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        ]});
    });

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW, rows: [new TableRow({ tableHeader: true, children: [
        headerCell('#', colW[0]), headerCell('投注', colW[1]), headerCell('金额', colW[2]), headerCell('赔率', colW[3]), headerCell('结果', colW[4]), headerCell('盈亏', colW[5]), headerCell('原因', colW[6])
    ]}), ...rows] });
}

function buildQfSummaryTable() {
    const colW = [800, 2500, 2200, 2200, 800, 1200, 1200, 2040];

    const matches = [
        ['97', 'FRA vs MAR', 'FRA 2-0 (~24%)', 'FRA 2-0', '[对]', '[对]', '0-0', '[对]'],
        ['98', 'ESP vs BEL', 'ESP 1-0 (~22%)', 'ESP 2-1', '[对]', '[错]', '1-1', '[错]'],
        ['99', 'NOR vs ENG', 'ENG 2-1 (~21%)', 'NOR 2-1', '[错]', '[错]', '1-1', '[错]'],
        ['100', 'ARG vs SUI', 'ARG 1-0 (~22%)', 'ARG 3-1 (AET)', '[对]', '备选7', '1-0', '[错]'],
    ];

    const rows = matches.map((r, i) => new TableRow({ children: [
        cell([txt(r[0], { size: FONT_SIZE_SM })], { width: colW[0], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[1], { size: FONT_SIZE_SM })], { width: colW[1], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[2], { size: FONT_SIZE_SM })], { width: colW[2], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[3], { size: FONT_SIZE_SM, bold: true })], { width: colW[3], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[4], { size: FONT_SIZE_SM, color: r[4] === '[对]' ? '006100' : RED, bold: true })], { width: colW[4], shading: r[4] === '[对]' ? LIGHT_GREEN : (i % 2 === 1 ? LIGHT_GRAY : undefined) }),
        cell([txt(r[5], { size: FONT_SIZE_SM, color: r[5] === '[对]' ? '006100' : RED, bold: true })], { width: colW[5], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[6], { size: FONT_SIZE_SM })], { width: colW[6], shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
        cell([txt(r[7], { size: FONT_SIZE_SM, color: r[7] === '[对]' ? '006100' : RED, bold: true })], { width: colW[7], shading: r[7] === '[对]' ? LIGHT_GREEN : (i % 2 === 1 ? LIGHT_GRAY : undefined) }),
    ]}));

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW, rows: [new TableRow({ tableHeader: true, children: [
        headerCell('#', colW[0]), headerCell('比赛', colW[1]), headerCell('预测首选', colW[2]), headerCell('实际', colW[3]), headerCell('方向', colW[4]), headerCell('比分', colW[5]), headerCell('HT', colW[6]), headerCell('HT对?', colW[7])
    ]}), ...rows] });
}

function buildStatsSummaryTable() {
    const colW = [3000, 4720, 4720];
    const data = [
        ['维度', 'QF战绩'],
        ['方向', '3/4 (75%)'],
        ['精确比分 (常规时间)', '1/4 (25% -- 仅FRA 2-0)'],
        ['含加时比分', '2/4 (50% -- FRA 2-0 + ARG 3-1)'],
        ['半场预测', '1/4 (25%) -- 仅FRA-MAR'],
        ['半场0-0专门', '1/3 (33%) -- 系统性错误'],
        ['100元合计', '约-150元'],
    ];

    const rows = data.map((r, i) => new TableRow({ children: [
        cell([txt(r[0], { bold: i === 0, size: FONT_SIZE_SM, color: i === 0 ? WHITE : BLACK })], { width: colW[0], shading: i === 0 ? DEEP_BLUE : (i % 2 === 1 ? LIGHT_GRAY : undefined) }),
        cell([txt(r[1], { bold: i === 0, size: FONT_SIZE_SM, color: i === 0 ? WHITE : BLACK })], { width: colW[1] + colW[2], alignment: AlignmentType.LEFT, shading: i === 0 ? DEEP_BLUE : (i % 2 === 1 ? LIGHT_GRAY : undefined) }),
    ]}));

    return new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: colW, rows });
}

// === BUILD DOCUMENT ===
const doc = new Document({
    styles: {
        default: { document: { run: { font: FONT, size: FONT_SIZE } } }
    },
    sections: [{
        properties: {
            page: {
                size: { width: 16838, height: 11906, orientation: PageOrientation.LANDSCAPE },
                margin: { top: 800, right: 800, bottom: 800, left: 800 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    children: [txt('2026世界杯 QF复盘 | ARG vs SUI | 2026年7月12日', { size: 14, color: '888888' })],
                    alignment: AlignmentType.RIGHT,
                    border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: BORDER_GRAY, space: 4 } }
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    children: [txt('Page ', { size: 14, color: '888888' }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: '888888' })],
                    alignment: AlignmentType.CENTER
                })]
            })
        },
        children: [
            // TITLE
            new Paragraph({
                children: [txt('2026世界杯 四分之一决赛', { size: FONT_SIZE_TITLE, bold: true, color: DEEP_BLUE })],
                spacing: { before: 100, after: 60 }
            }),
            new Paragraph({
                children: [txt('阿根廷 vs 瑞士 复盘报告', { size: FONT_SIZE_H1, bold: true, color: RED })],
                spacing: { before: 0, after: 200 },
                border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: DEEP_BLUE, space: 6 } }
            }),

            p([txt('最终比分: ARG 3-1 SUI (AET, 90分钟 1-1)', { bold: true, size: FONT_SIZE_H3 }), txt(' | 半场: 1-0 | 红牌: 恩博洛 72\'', { size: FONT_SIZE })], { before: 60, after: 200 }),

            // SECTION 1: Final Report
            h1('一、最终战报'),
            buildFinalTable(),

            // SECTION 2: Timeline
            new Paragraph({ children: [new PageBreak()] }),
            h1('二、完整时间线'),
            buildTimelineTable(),

            // SECTION 3: Prediction vs Actual
            new Paragraph({ children: [new PageBreak()] }),
            h1('三、预测 vs 实际'),
            h2('3.1 比分预测对比'),
            buildPredictionComparisonTable(),
            p([txt('备选7(ARG 3-1, ~4%)命中--但在加时120+1\'才达成，并非常规时间。8个选项中7个预测常规时间结束、均未命中。精确比分命中但路径完全不同。', { size: FONT_SIZE_SM, color: '666666' })], { before: 40, after: 80 }),

            h2('3.2 战术判断验证'),
            buildTacticalTable(),

            // SECTION 4: Core Errors
            new Paragraph({ children: [new PageBreak()] }),
            h1('四、核心错误分析'),

            h2('[大错1] SUI大巴画像完全错误'),
            p([txt('本场最大的认知错误。我们给了SUI 5/5大巴满分(低位防守/前30分钟)，但SUI实际战术: 53.9%控球率(比ARG多控球) / 9射门5射正(vs ARG 5射1射正) / 主动进攻而非被动挨打。', { size: FONT_SIZE })], { before: 40, after: 40 }),
            p([txt('根因: ', { bold: true }), txt('被SUI对哥伦比亚的0-0(120分钟)锚定，将"面对弱攻击力大巴成功"外推到"面对任何对手都是大巴"。与铁律18完全同构--防守表现取决于对手攻击力。', { size: FONT_SIZE })], { before: 40, after: 120 }),

            h2('[大错2] 半场0-0再犯 -- 铁律19诞生'),
            p([txt('三种偏见叠加:', { bold: true, size: FONT_SIZE })], { before: 40 }),
            p([txt('1. 慢开局外推: ', { bold: true }), txt('ARG对佛得角ET+对埃及0-2 -> "ARG总是慢开局" -> 0-0半场35% -> 10\'已死', { size: FONT_SIZE })], { before: 20 }),
            p([txt('2. 前30分钟神话: ', { bold: true }), txt('SUI前30分钟5星(基于对哥伦比亚0-0) -> 10\'被角球头球破门', { size: FONT_SIZE })], { before: 20 }),
            p([txt('3. 确认偏误: ', { bold: true }), txt('FRA vs MAR 0-0半场预测成功 -> 强化了对ARG半场0-0的信心', { size: FONT_SIZE })], { before: 20, after: 40 }),
            p([txt('铁律19(本场新增) -- 五条修正规则已写入CLAUDE.md v24。', { bold: true, color: RED, size: FONT_SIZE })], { before: 40, after: 120 }),

            h2('[大错3] 替补球员因子贡献错估'),
            p([txt('正确判断了ARG板凳深度优势(替补~200M vs SUI~60M)，但:', { size: FONT_SIZE })], { before: 40 }),
            p([txt('用于"ARG晋级概率70-73%"的方向判断 -- 正确。但未考虑板凳优势在加时才完全兑现 -- 常规时间90分钟0运动战进球(仅角球破门)。阿尔瓦雷斯112\'+劳塔罗120+1\'=两个加时进球来自板凳深度。优势真实但路径被低估。', { size: FONT_SIZE })], { before: 20, after: 120 }),

            // SECTION 5: Correct Parts
            h1('五、正确的部分'),
            new Table({ width: { size: A4_CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: [800, 5500, 6140], rows: [
                new TableRow({ tableHeader: true, children: [headerCell('#', 800), headerCell('判断', 5500), headerCell('评价', 6140)] }),
                ...[
                    ['1', 'ARG晋级 (~70-73%)', '方向正确. 与市场75%接近--但路径完全不同(加时非90分钟)'],
                    ['2', '备选7: ARG 3-1 (~4%)', '最终比分命中 (虽需加时). 8个选项中唯一对的一个'],
                    ['3', 'ARG板凳深度优势', '两个加时进球来自替补--"板凳200M vs 60M"差距的兑现'],
                    ['4', '恩多耶速度威胁', '恩多耶67\'进球+SUI最优攻击手'],
                    ['5', '首发11/11命中', 'ARG "unchanged side"全中'],
                    ['6', '裁判Pinheiro无偏见', 'SUI 14犯规仅2黄+恩博洛拿第二黄--但整体尺度一致'],
                ].map((r, i) => new TableRow({ children: [
                    cell([txt(r[0], { bold: true, size: FONT_SIZE_SM })], { width: 800, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
                    cell([txt(r[1], { size: FONT_SIZE_SM })], { width: 5500, alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
                    cell([txt(r[2], { size: FONT_SIZE_SM, color: '006100' })], { width: 6140, alignment: AlignmentType.LEFT, shading: i % 2 === 1 ? LIGHT_GRAY : undefined }),
                ]})),
            ]}),

            // SECTION 6: Betting
            new Paragraph({ children: [new PageBreak()] }),
            h1('六、100元投注结果'),
            buildBettingTable(),
            p([txt('总结果: ', { bold: true }), txt('-50.1元 (仅回收39.9元)', { bold: true, color: RED }), txt('. 唯一赢的是ARG晋级(30元->39.9元)。安全锚+分析优势方向全错模式。', { size: FONT_SIZE })], { before: 80 }),

            // SECTION 7: Lessons
            h1('七、本场核心教训'),

            h3('教训1: "大巴"标签必须用控球/射门数据验证'),
            p([txt('SUI的"大巴"是我们贴的标签--不是场上实际。53.9%控球+9射门5射正说明了相反的故事。以后给任何球队贴"大巴"标签前，必须查证: 该队本届平均控球率/该队本届平均射门数/上一轮的战术是否与本轮一致。', { size: FONT_SIZE })], { before: 40, after: 80 }),

            h3('教训2: "板凳在加时兑现"应写入投注'),
            p([txt('我们正确判断了板凳差距但未在投注中表达。正确的表达方式应该是"晋级+加时"组合--而非波胆+半场。ARG加分时方向的赔率可能远高于1.33。', { size: FONT_SIZE })], { before: 40, after: 80 }),

            h3('教训3: 冷门对冲在淘汰赛加时中完全失效'),
            p([txt('10元SUI+1.5 = 对冲手段--但ARG加时2球打穿了+1.5。淘汰赛中，少一人的弱队可能在加时崩溃->受让盘在加时阶段风险增加。对冲应考虑"常规时间受让"而非"含加时"。', { size: FONT_SIZE })], { before: 40, after: 80 }),

            h3('教训4: 定位球进球--与"大巴"标签的矛盾'),
            p([txt('我们给SUI 5星定位球进攻--但第一个进球是ARG角球破门。面对超巨级攻击力，定位球攻防的优势方可能反转--因为超巨星球队的定位球质量(梅西传中)可比对手的防守高点更具决定性。', { size: FONT_SIZE })], { before: 40, after: 120 }),

            // SECTION 8: QF Summary
            h1('八、四场QF复盘汇总'),
            buildQfSummaryTable(),
            p([], { before: 60 }),
            buildStatsSummaryTable(),

            // FOOTER NOTE
            p([], { before: 200 }),
            p([txt('数据源: ESPN API (760510/760511/760512/760513) + Polymarket ($7.84M) + FIFA API | 复盘时间: 2026年7月12日 BJT', { size: 14, color: '888888' })], { alignment: AlignmentType.CENTER }),
            p([txt('风险提示: 半场0-0预测 1/3 = 系统性反模式. 铁律19已写死不再犯. 板凳深度优势在淘汰赛加时阶段至关重要但应在投注中表达为"加时/晋级"而非"波胆".', { size: 14, color: '888888' })], { alignment: AlignmentType.CENTER }),
        ]
    }]
});

// Generate
const outputPath = 'D:\\ai\\世界杯\\2026-worldcup-predictions\\2026年7月12日_阿根廷vs瑞士_复盘.docx';
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log('DOCX generated: ' + outputPath);
}).catch(err => {
    console.error('Error:', err);
});
