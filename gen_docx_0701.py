# -*- coding: utf-8 -*-
"""Generate 7月1日 3场预测 as .docx"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2026年7月1日_3场预测.docx")
doc = Document()

for section in doc.sections:
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Cm(29.7); section.page_height = Cm(21.0)
    section.left_margin = Cm(1.5); section.right_margin = Cm(1.5)
    section.top_margin = Cm(1.2); section.bottom_margin = Cm(1.2)

style = doc.styles['Normal']; font = style.font
font.name = '微软雅黑'; font.size = Pt(9)
style.element.rPr.rFonts.set(qn('w:eastAsia'),'微软雅黑')

DARK=RGBColor(0x1A,0x1A,0x2E);RED=RGBColor(0xC0,0x39,0x2B);WHITE=RGBColor(0xFF,0xFF,0xFF)
GRAY=RGBColor(0xF2,0xF2,0xF2);HDR_BG=RGBColor(0x1A,0x1A,0x2E);GREEN=RGBColor(0x27,0xAE,0x60)

def sc(cell,text,bold=False,size=Pt(9),color=None,bg=None,align='center'):
    cell.text='';p=cell.paragraphs[0]
    p.alignment={'center':WD_ALIGN_PARAGRAPH.CENTER,'left':WD_ALIGN_PARAGRAPH.LEFT,'right':WD_ALIGN_PARAGRAPH.RIGHT}.get(align,WD_ALIGN_PARAGRAPH.CENTER)
    r=p.add_run(str(text));r.bold=bold;r.font.size=size;r.font.name='微软雅黑'
    r._element.rPr.rFonts.set(qn('w:eastAsia'),'微软雅黑')
    if color:r.font.color.rgb=color
    if bg:
        shading=parse_xml(f'<w:shd {nsdecls("w")} w:fill="{str(bg)}"/>')
        cell._tc.get_or_add_tcPr().append(shading)
    tc=cell._tc;tcPr=tc.get_or_add_tcPr()
    vAlign=parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>');tcPr.append(vAlign)

def hdr(t,row,texts,size=Pt(9)):
    for i,txt in enumerate(texts):sc(t.cell(row,i),txt,bold=True,size=size,color=WHITE,bg=HDR_BG)

def dat(t,row,texts,bold_cols=None,bg=None,size=Pt(9)):
    for i,txt in enumerate(texts):
        b=bold_cols and i in bold_cols;sc(t.cell(row,i),txt,bold=b,size=size,bg=bg)

def heading(text,size=Pt(14),color=DARK):
    p=doc.add_paragraph();p.space_before=Pt(8);p.space_after=Pt(4)
    r=p.add_run(text);r.bold=True;r.font.size=size;r.font.color.rgb=color
    r.font.name='微软雅黑';r._element.rPr.rFonts.set(qn('w:eastAsia'),'微软雅黑')

def txt(text,size=Pt(9),bold=False,color=None):
    p=doc.add_paragraph();p.space_before=Pt(1);p.space_after=Pt(1)
    r=p.add_run(text);r.bold=bold;r.font.size=size;r.font.name='微软雅黑'
    r._element.rPr.rFonts.set(qn('w:eastAsia'),'微软雅黑')
    if color:r.font.color.rgb=color

# ═══════════════ COVER ═══════════════
heading('2026世界杯 — 7月1日淘汰赛 R32 三场预测',Pt(16),DARK)
txt('生成时间: 2026年6月30日 北京时间 16:00',Pt(8),color=RGBColor(0x66,0x66,0x66))
txt('数据来源: ESPN API + Sports Mole + SI + RotoWire + Transfermarkt (Mundo Deportivo)',Pt(8),color=RGBColor(0x66,0x66,0x66))
txt('分析框架: CLAUDE.md v17 + 6月30日复盘教训(身价比阈值提高+备选覆盖冷平+点球门将加权)',Pt(8),color=RGBColor(0x66,0x66,0x66))
doc.add_paragraph()

# ═══════════════ SUMMARY ═══════════════
heading('预测汇总',Pt(12),DARK)
t=doc.add_table(rows=4,cols=8);t.style='Table Grid';t.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(t,0,['#','时间 (BJT)','阶段','比赛','身价比','首选比分','半场','冷门风险'])
for i,row in enumerate([
    ['1','01:00','R32','科特迪瓦 vs 挪威','2.1:1 (挪威占优)','挪威 2-1','1-0','中高'],
    ['2','05:00','R32','法国 vs 瑞典','5.9:1','法国 3-0','2-0','低'],
    ['3','09:00','R32','墨西哥 vs 厄瓜多尔','1.4:1','墨西哥 1-0','0-0','中'],
]): dat(t,i+1,row,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

# ═══════════════ BRACKET ═══════════════
heading('淘汰赛路径 (含6/30冷门更新)',Pt(12),DARK)
tb=doc.add_table(rows=4,cols=2);tb.style='Table Grid';tb.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tb,0,['路径','难度'])
dat(tb,1,['科特迪瓦/挪威 → R16 → 巴西 → 八强可能碰法国区','高'])
dat(tb,2,['法国 → R16 → 巴拉圭(非德国!) → 八强','大幅降低! [火]'],bold_cols={1})
dat(tb,3,['墨西哥/厄瓜多尔 → R16 → 英格兰/刚果民主共和国 胜者','中高'])
doc.add_paragraph()
txt('德国出局→法国R16仅需过巴拉圭。八强避开德国。法国夺冠路径大幅简化。',Pt(9),bold=True,color=RED)
doc.add_paragraph()

# ═══════════════ MATCH 1 ═══════════════
heading('比赛1: 科特迪瓦 vs 挪威 — 01:00 BJT, 达拉斯体育场',Pt(12),RED)

info1=[['项目','内容'],['FIFA排名','科特迪瓦 #31 vs 挪威 #17'],['身价比','科特迪瓦~€280M vs 挪威€601M ≈ 1:2.1 (挪威优)'],
       ['历史交锋','首次世界杯交锋'],['晋级奖励','16强对阵 巴西 (巴西2-1淘汰日本已在等待)'],
       ['强队分类','挪威: 超级巨星型(偏单一) | 科特迪瓦: 大巴+双爆点反击型'],
       ['冷门风险','中高 — 科特迪瓦首次淘汰赛, 但挪威防线10场仅1零封']]
ti=doc.add_table(rows=len(info1),cols=2);ti.style='Table Grid';ti.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(ti,0,info1[0])
for i,r in enumerate(info1[1:]):dat(ti,i+1,r,bold_cols={0},bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('小组赛回顾',Pt(10),DARK)
tg=doc.add_table(rows=3+3+3,cols=4);tg.style='Table Grid';tg.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tg,0,['球队','对手','比分','关键'])
tg.cell(1,0).merge(tg.cell(1,3));sc(tg.cell(1,0),'科特迪瓦 (E组第2, 6分, +1GD)',bold=True,color=DARK,align='left')
for i,r in enumerate([['厄瓜多尔','1-0','迪亚洛90\'绝杀'],['德国','1-2','凯西先破门→昂达夫双响逆转'],['库拉索','2-0','佩佩梅开二度, 零封']]):
    dat(tg,i+2,['']+r,bg=GRAY if i%2==0 else None)
tg.cell(5,0).merge(tg.cell(5,3));sc(tg.cell(5,0),'挪威 (I组第2, 6分, +3GD)',bold=True,color=DARK,align='left')
for i,r in enumerate([['伊拉克','4-1','哈兰德2球'],['塞内加尔','3-2','哈兰德再2球, 防线失2球'],['法国(轮换)','1-4','无哈兰德=0威胁, 登贝莱帽子戏法']]):
    dat(tg,i+6,['']+r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('因素导向表',Pt(10),DARK)
tf=doc.add_table(rows=9,cols=3);tf.style='Table Grid';tf.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tf,0,['因素','有利方','理由'])
for i,r in enumerate([
    ['哈兰德个人能力(52场59球)','挪威 ★★★','科特迪瓦防线从未面对过此级别终结者'],
    ['挪威防线脆弱(10场仅1零封)','科特迪瓦 ★★','佩佩+迪奥曼德双爆点可击穿'],
    ['雷尔森伤缺→右后卫漏洞','科特迪瓦 ★★','挪威RB被迫用中场奥尔斯内斯客串'],
    ['辛戈伤疑→科特迪瓦右中卫缺口','挪威 ★★','科特迪瓦最强防线一环缺失'],
    ['科特迪瓦3场2零封','科特迪瓦 ★★','对比挪威防守, 非洲大象更稳'],
    ['哈兰德缺席时挪威=另一支队','科特迪瓦 ★★','无哈兰德时对法国0威胁'],
    ['科特迪瓦首次淘汰赛','挪威 ★','心理经验不足'],
    ['身价比1:2.1(3:1~10:1区间偏下)','挪威 ★','挪威占优但不足以碾压'],
]): dat(tf,i+1,r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('伤病/停赛',Pt(10),DARK)
tj=doc.add_table(rows=5,cols=4);tj.style='Table Grid';tj.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tj,0,['球队','球员','状态','影响'])
for i,r in enumerate([
    ['科特迪瓦','辛戈(Singo)','[注意]伤疑','右中卫, 腿筋问题'],
    ['挪威','雷尔森(Ryerson)','[缺]确认缺阵','多特右后卫, 大腿伤→奥尔斯内斯客串'],
    ['挪威','哈兰德','[可]','对法国轮休→满血出战'],
    ['挪威','厄德高','[可]','需找回状态(本届0球0助)'],
]): dat(tj,i+1,r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('非洲韧性评估(科特迪瓦)',Pt(10),DARK)
txt('4/5 — 低位防守:良好 | 速度反击:特优(佩佩+迪奥曼德) | 定位球:良好 | 前30分钟:良好 | 被压制不崩盘:良好',Pt(9))
txt('唯一瑕疵: 对德国的下半场被逆转暴露被持续压制时的脆弱。',Pt(9),color=RGBColor(0x66,0x66,0x66))
doc.add_paragraph()

heading('比分预测',Pt(10),DARK)
tp=doc.add_table(rows=5,cols=4);tp.style='Table Grid';tp.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tp,0,['类型','比分','半场','说明'])
for i,r in enumerate([
    ['首选','挪威 2-1','1-0','哈兰德破门→科特迪瓦扳平→挪威锁定'],
    ['备选','挪威 1-0','0-0','僵持大半场→哈兰德个人能力解决'],
    ['备选','挪威 3-1','1-0','科特迪瓦防线被哈兰德连续击穿'],
    ['备选','1-1(挪威加时晋级)','0-0','科特迪瓦大巴成功→加时挪威深度优势'],
]): dat(tp,i+1,r,bold_cols={0} if r[0]=='首选' else None,bg=GREEN if r[0]=='首选' else (GRAY if i%2==0 else None))
doc.add_paragraph()

heading('冷门路径',Pt(10),RED)
txt('科特迪瓦大巴守住65分钟→挪威急躁→佩佩反击1v1过掉客串RB奥尔斯内斯→1-0→升级大巴→锁死哈兰德→1-0或1-1(加时/点球)。最可能冷门比分: 1-1(科特迪瓦点球胜)',Pt(9))
doc.add_paragraph()

# ═══════════════ MATCH 2 ═══════════════
heading('比赛2: 法国 vs 瑞典 — 05:00 BJT, 纽约新泽西体育场 (决赛场地!)',Pt(12),RED)

info2=[['项目','内容'],['FIFA排名','法国 #2 vs 瑞典 #36'],['身价比','法国€1.476B vs 瑞典~€250M ≈ 5.9:1'],
       ['历史交锋','法国近6战5胜1负, 近4胜中3场仅赢1球'],
       ['晋级奖励','16强对阵 巴拉圭! (德国出局后的巨大奖励)'],
       ['强队分类','法国: 超级巨星型(超级版) | 瑞典: 非大巴的攻击型弱队'],
       ['冷门风险','低 — 瑞典对荷兰丢5球, 不具备大巴能力']]
ti2=doc.add_table(rows=len(info2),cols=2);ti2.style='Table Grid';ti2.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(ti2,0,info2[0])
for i,r in enumerate(info2[1:]):dat(ti2,i+1,r,bold_cols={0},bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('小组赛回顾',Pt(10),DARK)
tg2=doc.add_table(rows=3+3+3,cols=4);tg2.style='Table Grid';tg2.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tg2,0,['球队','对手','比分','关键'])
tg2.cell(1,0).merge(tg2.cell(1,3));sc(tg2.cell(1,0),'法国 (I组第1, 9分, +8GD) 3战全胜!',bold=True,color=DARK,align='left')
for i,r in enumerate([['伊拉克','3-0','姆巴佩2球, 轻松'],['塞内加尔','3-1','姆巴佩+登贝莱+奥利塞'],['挪威(轮换)','4-1','登贝莱帽子戏法! 无哈兰德的挪威被打穿']]):
    dat(tg2,i+2,['']+r,bg=GRAY if i%2==0 else None)
tg2.cell(5,0).merge(tg2.cell(5,3));sc(tg2.cell(5,0),'瑞典 (F组第3, 4分, 0GD) 最佳第三名勉强晋级',bold=True,color=DARK,align='left')
for i,r in enumerate([['突尼斯','2-1','小胜'],['荷兰','1-5','防线被荷兰完全打穿!'],['日本','1-1','埃兰加远射, 勉强守平']]):
    dat(tg2,i+6,['']+r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('因素导向表',Pt(10),DARK)
tf2=doc.add_table(rows=8,cols=3);tf2.style='Table Grid';tf2.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tf2,0,['因素','有利方','理由'])
for i,r in enumerate([
    ['身价比5.9:1','法国 ★★★','大差距。瑞典不是大巴型(对荷兰丢5球)'],
    ['姆巴佩+登贝莱状态(合计7球)','法国 ★★★','瑞典防线无法同时应对两个爆点'],
    ['伊萨克·希恩伤缺(瑞典防线核心)','法国 ★★★','林德洛夫被迫从中场回撤→防区混乱'],
    ['瑞典三叉戟(伊萨克+哲凯赖什+埃兰加)','瑞典 ★★','有能力攻破任何防线'],
    ['法国无球时被动(小组赛未暴露)','瑞典 ★★','如果瑞典先进球, 走势可能不同'],
    ['法国R16打巴拉圭(非德国)','法国 ★','路径大幅简化, 心态更放松'],
    ['德尚赛末离任→"最后一舞"','法国 ★','全队为教练而战的额外动力'],
]): dat(tf2,i+1,r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('伤病/停赛',Pt(10),DARK)
tj2=doc.add_table(rows=3,cols=4);tj2.style='Table Grid';tj2.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tj2,0,['球队','球员','状态','影响'])
dat(tj2,1,['法国','萨利巴(Saliba)','[可]带伤','背伤, 大概率首发'])
dat(tj2,2,['瑞典','伊萨克·希恩(Hien)','[缺]腿筋','防线核心缺阵! 林德洛夫被迫中场回撤后卫'])
doc.add_paragraph()

heading('瑞典韧性评估',Pt(10),DARK)
txt('2/5 — 低位防守:差(对荷兰丢5球) | 速度反击:良好 | 定位球:良好 | 前30分钟:差(对荷兰17分钟丢2球) | 被压制不崩盘:差',Pt(9))
txt('瑞典不擅长也不愿意摆大巴。这正是法国大胜的底层逻辑。',Pt(9),color=RED)
doc.add_paragraph()

heading('比分预测',Pt(10),DARK)
tp2=doc.add_table(rows=5,cols=4);tp2.style='Table Grid';tp2.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tp2,0,['类型','比分','半场','说明'])
for i,r in enumerate([
    ['首选','法国 3-0','2-0','上半场解决→下半场控制节奏'],
    ['备选','法国 2-0','1-0','开场保守→姆巴佩下半场破局'],
    ['备选','法国 3-1','2-1','瑞典反击偷一个→法国实力碾压'],
    ['备选','法国 2-1','1-1','最接近冷门: 伊萨克先破门→法国逆转'],
]): dat(tp2,i+1,r,bold_cols={0} if r[0]=='首选' else None,bg=GREEN if r[0]=='首选' else (GRAY if i%2==0 else None))
doc.add_paragraph()

heading('冷门路径',Pt(10),RED)
txt('法国极度轻敌+瑞典三叉戟高速反击→伊萨克先破门→法国陷入困境→1-0。概率极低: 需同时满足轻敌+防线超常+迈尼昂失误。最可能"冷门": 法国2-1(瑞典先进→法国逆转), 这不是真正的冷门。',Pt(9))
doc.add_paragraph()

# ═══════════════ MATCH 3 ═══════════════
heading('比赛3: 墨西哥 vs 厄瓜多尔 — 09:00 BJT, 墨西哥城阿兹台克体育场',Pt(12),RED)

info3=[['项目','内容'],['FIFA排名','墨西哥 #14 vs 厄瓜多尔 #30'],['身价比','墨西哥~€250M vs 厄瓜多尔~€180M ≈ 1.4:1'],
       ['历史交锋','墨西哥17胜7平4负。世界杯: 2002小组赛墨西哥2-1'],
       ['晋级奖励','16强对阵 英格兰 vs 刚果民主共和国 的胜者(大概率英格兰)'],
       ['强队分类','墨西哥: 体系型(主场加成版) | 厄瓜多尔: 不稳定爆冷型'],
       ['冷门风险','中 — 墨西哥主场9场不败+0丢球 vs 厄瓜多尔刚击败德国']]
ti3=doc.add_table(rows=len(info3),cols=2);ti3.style='Table Grid';ti3.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(ti3,0,info3[0])
for i,r in enumerate(info3[1:]):dat(ti3,i+1,r,bold_cols={0},bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('小组赛回顾',Pt(10),DARK)
tg3=doc.add_table(rows=3+3+3,cols=4);tg3.style='Table Grid';tg3.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tg3,0,['球队','对手','比分','关键'])
tg3.cell(1,0).merge(tg3.cell(1,3));sc(tg3.cell(1,0),'墨西哥 (A组第1, 9分, +6GD) 3战全胜+0丢球! 唯一满零封球队',bold=True,color=DARK,align='left')
for i,r in enumerate([['南非','2-0','基尼奥内斯+希门尼斯, 3红牌'],['韩国','1-0','小胜, 零封'],['捷克','3-0','碾压, 希门尼斯+阿尔瓦拉多']]):
    dat(tg3,i+2,['']+r,bg=GRAY if i%2==0 else None)
tg3.cell(5,0).merge(tg3.cell(5,3));sc(tg3.cell(5,0),'厄瓜多尔 (E组第3, 4分, 0GD) 击败德国逆袭晋级',bold=True,color=DARK,align='left')
for i,r in enumerate([['科特迪瓦','0-1','90\'被绝杀, 0射正'],['库拉索','0-0','27射0球! 攻击效率灾难'],['德国','2-1','安古洛扳平→普拉塔77\'制胜!']]):
    dat(tg3,i+6,['']+r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('因素导向表',Pt(10),DARK)
tf3=doc.add_table(rows=9,cols=3);tf3.style='Table Grid';tf3.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tf3,0,['因素','有利方','理由'])
for i,r in enumerate([
    ['墨西哥主场(阿兹台克80000+2240m)','墨西哥 ★★★','世界杯主场9场不败! 海拔体能加成'],
    ['墨西哥3场零封(唯一全零封球队)','墨西哥 ★★★','防线默契+主场防守信心'],
    ['厄瓜多尔击败德国(信心爆棚)','厄瓜多尔 ★★','证明能击败任何对手, 但可能消耗体能'],
    ['厄瓜多尔极度不稳定(27射0球vs0-1→2-1胜德国)','墨西哥 ★★','无法预测哪个版本出现'],
    ['身价比1.4:1','墨西哥 ★','接近比赛, 任何结果都可能(6/30教训)'],
    ['凯塞多vs墨西哥中场','双方 ★★','如果凯塞多统治中场→厄瓜多尔有戏'],
    ['历史交锋(墨西哥17胜)','墨西哥 ★','心理优势明确'],
    ['厄瓜多尔对科特迪瓦0射正','墨西哥 ★★','面对大巴型防守时厄瓜多尔毫无办法'],
]): dat(tf3,i+1,r,bg=GRAY if i%2==0 else None)
doc.add_paragraph()

heading('伤病/停赛',Pt(10),DARK)
tj3=doc.add_table(rows=3,cols=4);tj3.style='Table Grid';tj3.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tj3,0,['球队','球员','状态','影响'])
dat(tj3,1,['墨西哥','—','[可]全员可用','希门尼斯对捷克轮休→满血首发'])
dat(tj3,2,['厄瓜多尔','—','[可]全员可用','击败德国的首发11人均可用'])
doc.add_paragraph()

heading('厄瓜多尔韧性评估',Pt(10),DARK)
txt('3.5/5 — 低位防守:良好 | 速度反击:良好(普拉塔+安古洛) | 定位球:良好 | 前30分钟:一般 | 被压制不崩盘:良好(对德国逆转)',Pt(9))
txt('介于"不稳定"和"能爆冷"之间的灰色地带。对库拉索0-0和对德国2-1的差距是世界杯最大的方差。',Pt(9),color=RGBColor(0x66,0x66,0x66))
doc.add_paragraph()

heading('比分预测',Pt(10),DARK)
tp3=doc.add_table(rows=5,cols=4);tp3.style='Table Grid';tp3.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr(tp3,0,['类型','比分','半场','说明'])
for i,r in enumerate([
    ['首选','墨西哥 1-0','0-0','主场僵持→希门尼斯定位球/头球破局→零封保持'],
    ['备选','墨西哥 2-0','1-0','上半场破门→下半场反击锁定'],
    ['备选','1-1(墨西哥加时晋级)','0-0','厄瓜多尔大巴→凯塞多反击→墨追平→加时主場'],
    ['备选','0-0(墨西哥点球晋级)','0-0','极度僵持→加时无建树→兰赫尔扑点'],
]): dat(tp3,i+1,r,bold_cols={0} if r[0]=='首选' else None,bg=GREEN if r[0]=='首选' else (GRAY if i%2==0 else None))
doc.add_paragraph()

heading('冷门路径',Pt(10),RED)
txt('墨西哥久攻不下→主场焦虑→凯塞多抢断→普拉塔反击→0-1→墨西哥全压→厄瓜多尔5-4-1大巴→0-1或1-1(加时/点球胜)。最可能冷门比分: 1-1(厄瓜多尔加时或点球晋级) — 与荷兰vs摩洛哥高度相似。',Pt(9))
doc.add_paragraph()

# ═══════════════ RISK WARNINGS ═══════════════
heading('风险提示',Pt(12),RED)
txt('1. 科特迪瓦vs挪威: "一个人的球队"vs"没有超巨但更均衡"的经典对决。哈兰德是否被锁死决定一切。',Pt(9),bold=True)
txt('2. 法国vs瑞典: 本日最没悬念, 但不是0悬念。瑞典三叉戟有能力进球。R16对手是巴拉圭=巨大奖励。',Pt(9),bold=True)
txt('3. 墨西哥vs厄瓜多尔: 本日最胶着。1.4:1身价比+淘汰赛=任何结果可能。阿兹台克是最大变量。',Pt(9),bold=True)

txt('—',Pt(8),color=RGBColor(0xAA,0xAA,0xAA))
txt('数据: ESPN API + Sports Mole + SI + RotoWire + Transfermarkt | 身价: Transfermarkt via Mundo Deportivo (2026年6月)',Pt(7),color=RGBColor(0x99,0x99,0x99))
txt('分析框架: CLAUDE.md v17 + 6月30日复盘教训 | 预测时间: 2026年6月30日 16:00 BJT',Pt(7),color=RGBColor(0x99,0x99,0x99))
txt('Co-Authored-By: Claude Opus 4.8',Pt(7),color=RGBColor(0x99,0x99,0x99))

doc.save(OUT)
print(f'[OK] DOCX saved to: {OUT}')
