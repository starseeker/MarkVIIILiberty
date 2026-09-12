"""Source-led transcription of supplied pages 25–44.

Rows preserve photographed line breaks and cross-page assembly continuations.
Independent proofreading status and doubtful readings are in review.json.
"""
from .parts_tables import row
from .opening_tables import entry, component, composed, bolt, cotter
TABLES={}
def start(page):
 TABLES[page]=[]
 return TABLES[page]
def add(page,content):
 r=start(page)
 for line in content.strip().splitlines():
  fields=line.split('|');assert len(fields)==9,(page,line,len(fields))
  r.append(row(*[f.replace('~','\n') for f in fields]))
 return r

def nut(r,size,typ='plain, S. A. E., hexagon',count='one',end=False):
 component(r,f'{count} —      NUT, {typ}, {size}'+('.)' if end else ','))
def lockwasher(r,size,count='one',end=True):
 component(r,f'{count} —      WASHER, lock, {size}'+('.)' if end else ','))

r=start(25)
bolt(r,'outlet louvre','(1)','.06')
component(r,'*one SH501B outlet louvre BOLT (½″ x 1⅜″, head 3/16″ thick) (1)',price='.03')
nut(r,'½″','plain, U. S. Std., hexagon');lockwasher(r,'½″')
entry(r,'BOLT, peep hole cover plate (½″ x 1 5/16″, head 5/16″ thick)',note='%X',brit='1X90',ord='633',qty='40',price='.03')
bolt(r,'peep hole cover plate operating','(20)','.30')
component(r,'*one 6X90 peep hole cover plate operating BOLT (20)',ord='633',price='.25')
component(r,'one 7X90 peep hole cover plate operating bolt PEG.)')
bolt(r,'removable platform ammunition storage support','(2)','.25')
component(r,'*one SH550A removable platform ammunition storage support BOLT (2)',price='.20')
nut(r,'⅜″','plain, U. S. Std., hexagon');nut(r,'½″','plain, U. S. Std., hexagon');lockwasher(r,'½″')
entry(r,'BOLT, S. A. E., ⅜″ x 2¼″, with plain nut and lock washer.  (For bracket B6205 (8).)',note='%(sh)R',qty='(8)',price='.02 P')
bolt(r,'S. A. E., drilled, ¼″ x 15/16″, threaded 9/16″','(22)','.10',note='&',ident='116',plate='15 &\n19')
composed_row=r[-1];composed_row['space_before']=0.5
component(r,'*one LQ164A BOLT, S. A. E., drilled ¼″ x 15/16″, threaded 9/16″',mfr='712',price='.05')
component(r,'one LQ89A NUT, special, S. A. E., ¼″,');cotter(r,'1/16″ x ½″',False)
component(r,'two LQ113A WASHER, special, ¼″.')
entry(r,'                    For water pump bevel driver housing, assembly (2); oil\n                      pump (10); distributor, assembly (10).)')
bolt(r,'S. A. E., drilled, ¼″ x 1⅛″','(3)','.09',ident='117',plate='15')
component(r,'*one LQ112A BOLT, S. A. E., drilled, ¼″ x 1⅛″ (3)',mfr='117',price='.05')
component(r,'one LQ89A NUT, special, S. A. E., ¼″,');cotter(r,'1/16″ x ½″',False)
component(r,'one LQ113A WASHER, special, ¼″.')
entry(r,'                    For lever LQ111A (1); securing crank case upper half\n                      drain tube, assembly (2).)')
bolt(r,'small planet pinion ring','(6)','.34',note='&',ident='30',plate='22')
component(r,'*one M317 small planet ring BOLT (6)',ord='679',price='.30')
nut(r,'⅝″','castle, S. A. E.');cotter(r,'⅛″ x 1¼″')

r=start(26)
bolt(r,'sponson roller bracket','(2)','$0.15')
component(r,'one SH470D sponson roller bracket bolt NUT,')
component(r,'*one —      BOLT, U. S. Std., hexagon head, ¾″ x 3⅜″ (2)',price='.10')
lockwasher(r,'¾″')
for text,qty in [
('flat head, 3/16″ x 1″, with stove bolt nut and lock washer.  (For brace\n  SH920F (1).)','(1)'),
('round head, 3/16″ x ⅝″, with stove bolt nut and lock washer.  (For\n  hand pressure pump (3).)','(3)'),
('round head, ¼″ x 7/16″, with stove bolt nut and lock washer.\n  (Through boards SH1021A and SH1021B (4).)','(16)'),
('round head, ¼″ x ½″, with stove bolt nut and lock washer.  (For\n  clamp SH1021G (8).)','(8)'),
('round head, ¼″ x ⅝″, with stove bolt nut and lock washer.  (For\n  clamp SH984K (2).)','(2)'),
('round head, ¼″ x ¾″, with two stove bolt nuts and lock washers.\n  (For angle SH152C (2); angle SH152D (2).)','(8)'),
('round head, ¼″ x ¾″, with stove bolt nut and lock washer.  (For\n  bands SH153K and SH153H (3); band SH153M (1); clip SH153T (1).)','(8)'),
('round head, ¼″ x ⅞″, with stove bolt nut and lock washer.  (For\n  clamp SH984G (1).)','(2)'),
('round head, ¼″ x 1″, with stove bolt nut and lock washer.  (For\n  band SH153N (1); clamp SH1021G (2).)','(17)'),
('round head, ¼″ x 1¼″, with stove bolt nut and lock washer.  (For\n  clamp SH920B (1); clamp B101480A (1); clamp B101480P (1); clamp B101480Z\n  (1); instrument board (4).)','(21)'),
('round head, ¼″ x 2″, with stove bolt nut and lock washer and\n  plain washer.  (For switch SH567A (2).)','(2)')]:
 entry(r,'BOLT, stove, '+text,note='%(sh)R',qty=qty,price='.01 P',brit='16' if qty=='(21)' else '')
entry(r,'BOLT, tap, ⅜″ x 2″, threaded ⅞″.  (For gear SH586B (3).)',note='%(gac)X',ord='SH586F',qty='3',price='.01 P')
entry(r,'BOLT, tap, ½″ x 2½″, threaded 1¾″, assembly',note='%(gac)X',qty='(2)',price='.03 P')

r=start(27)
composed(r)
component(r,'*one SH586G BOLT, tap, ½″ x 2½″, threaded 1¾″',price='.01 P')
nut(r,'½″','plain, U. S. Std., hexagon');lockwasher(r,'½″',end=False)
entry(r,'                    For gear SH586C (2).)')
for part,text,qty,price in [
('SH380B','⅝″ x 15/16″, threaded ½″.  (For bracket SH380A (2).)','2','.02 P'),
('SH505B','⅝″ x 1″, threaded ¾″.  (For channel M990 (9).)','9','.02 P'),
('SH503A','⅝″ x 1¼″, threaded ⅞″.  (For piece M992 (6); plate M991 (7);\n  plate M1908 (17); piece M985 (7).)','37','.02 P'),
('SH303C','⅝″ x 1¼″, threaded 1″.  (For plate SH303A (4).)','4','.02 P'),
('SH380C','⅝″ x 1½″, threaded 1″.  (For channel M2110 (11); channel M2111\n  (11); channel M990 (1).)','23','.02 P'),
('SH499B','⅝″ x 1¾″, threaded 1″.  (For frame M982 (17); frame M983 (17);\n  channel M990 (1); plate M989 (10).)','45','.02 P'),
('SH303B','¾″ x 1¼″, threaded 1″.  (For plate M1991 (14); strap (left) M2001\n  (10); strap (right) M2001 (8); plate M2077 (14).)','46','.03 P')]:
 entry(r,'BOLT, tap, '+text,note='%(gac)X',ord=part,qty=qty,price=price)
bolt(r,'transmission bevel gear case cover to case','(14)','.08 P')
component(r,'*one MX8 transmission bevel gear case cover to case BOLT',ord='112',price='.04')
nut(r,'½″','castle, S. A. E.');cotter(r,'3/32″ x 1″')
bolt(r,'transmission frame holding','(2)','.10 P')
component(r,'*one M388 transmission frame holding BOLT (2)',price='.05')
nut(r,'¾″');lockwasher(r,'¾″')
bolt(r,'transmission gear case to brake','(32)','.08 P')
component(r,'*one MX26 transmission gear case to brake BOLT (32)',ord='712',price='.04')
nut(r,'7/16″','castle, S. A. E.');cotter(r,'3/32″ x ⅞″')
bolt(r,'transmission mechanical lubricator yoke','(6)','.03 P')
component(r,'*one SH101Q transmission mechanical lubricator yoke BOLT (6)',price='.01')
nut(r,'¼″');lockwasher(r,'¼″')
bolt(r,'transmission pinion shaft packing gland','(4)','.09')
component(r,'*one MX22 transmission pinion shaft packing gland BOLT (4)',ord='712',price='.07')
nut(r,'⅜″',count='two',end=True)

r=start(28)
bolt(r,'transmission sprocket bearing bracket to channel','(20)','$0.14',note='&')
component(r,'*one MX1 transmission sprocket bearing bracket to channel BOLT (20)',ord='712',price='.08')
nut(r,'¾″','castle, S. A. E.');cotter(r,'⅛″ x 1½″')
bolt(r,'transmission vertical shifter shaft bearing to bevel gear case','(2)','.09',note='&')
component(r,'*one MX11 transmission vertical shifter shaft bearing to bevel gear case\n                         BOLT (2)',ord='712',price='.06')
nut(r,'½″','castle, S. A. E.');cotter(r,'3/32″ x 1″')
bolt(r,'trunnion','(6)','.22')
component(r,'*one M3128 trunnion BOLT (6)',ord='428',price='.18')
nut(r,'¾″','plain, U. S. Std., hexagon',end=True)
bolt(r,'U, exhaust pipe','(4)','.41')
component(r,'*one SH402L exhaust pipe U BOLT (4)',price='.35')
nut(r,'⅜″','plain, U. S. Std., hexagon',count='two');lockwasher(r,'⅜″',count='two')
for text,note,qty in [
('3/16″ x 9/16″, with round nut.  (For ignition\n  battery case (6).)','&(sh)R','(6)'),
('¼″ x ⅞″, with round nut.  (For starting\n  and lighting battery case X854 (6).)','&(sh)R','(12)'),
('⅜″ x ⅞″, with plain nut.  (For bracket\n  M2432 (2).)','%(sh)R','(2)'),
('⅜″ x 1⅜″, with plain nut and lock washer.\n  (For bracket SH967A (3).)','%(sh)R','(3)'),
('⅜″ x 1½″, with plain nut and lock washer.\n  (For radiator (13).)','%(sh)R','(13)')]:
 entry(r,'BOLT, U. S. Std., countersunk head, '+text,note=note,qty=qty,price='.01 P')

add(29,r'''
%(sh)R||||||BOLT, U. S. Std., countersunk head, ⅝″ x 1¾″, with plain nut and lock washer.~  (For guide M2114 (1).)|(1)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, 3/16″ x ⅝″, with plain nut.  (For bracket M2432~  (4).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x ½″.  (For tachometer support SH585B~  (4).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x ⅝″, with plain nut and lock washer.  (For~  cap SH950L (20).)|(20)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x ¾″, with plain nut and lock washer.  (For~  clamp SH920D (1).)|(2)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x ⅞″, with plain nut and lock washer.  (For~  officer’s chest fastening strap SH569P (2).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x ⅞″.  (For collar SH993C (1).)|(1)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x 1″, with plain nut and lock washer.  (For~  cap SH950L (4).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x 1⅜″, with plain nut, plain washer and lock~  washer.  (For board SH994G (4).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x 1½″, with plain nut and lock washer.~  (For box SH961A (10).)|(10)|.01 P
&(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x 1 9/16″, with plain nut and lock washer.  (For~  governor lever (1).)|(1)|.01 P
&(sh)R||||||BOLT, U. S. Std., hexagon head, ¼″ x 1⅝″, with plain nut.  (For sprocket X269~  (1); sprocket X270 (1).)|(2)|.01 P
&(sh)R||||||BOLT, U. S. Std., hexagon head, 5/16″ x ¾″, with plain nut and lock washer.  (For~  plate SH611A (6); plate SH611B (6).)|(12)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, 5/16″ x ⅞″, with plain nut and lock washer.  (For~  duct M1054 (10).)|(10)|.01 P
&(sh)R||||||BOLT, U. S. Std., hexagon head, 5/16″ x 1″, with plain nut and lock washer.  (For~  plate SH611A (15); plate SH611B (15); plate SH485C (6).)|(36)|.01 P
&(sh)R||||||BOLT, U. S. Std., hexagon head, 5/16″ x 1¼″, with plain nut and lock washer.  (For~  plate SH611A (6); plate SH611B (6).)|(12)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x ¾″.  (For rest 5X90 (2); plate M1033 (9).)|(49)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x ¾″, with plain nut and lock washer.  (For~  plate M1034 (4); plate M1035A (5); foot SH280A (2); foot SH280B (2); foot~  SH280C (2); foot SH280D (2); housing SH276A (13).)|(30)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x ⅞″, with plain nut and lock washer.  (For~  brace SH958K (2).)|(2)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1″, with plain nut and lock washer.  (For~  cleat M2186 (1); housing SH282B (6).)|(12)|.01 P
''')
add(30,r'''
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1 1/16″, with plain nut and lock washer.~  (For cap SH168E (2).)|(2)|$0.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1⅛″, with plain nut and lock washer.~  (For housing SH145A (5).)|(5)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1⅛″.  (For cap SH137B (4).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1¼″, with plain nut and lock washer.~  (For base SH903A (4).)|(4)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1 5/16″, with plain nut and lock washer.~  (For support SH168G (1).)|(1)|.01 P
&(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1⅜″, with plain nut and lock washer.~  (For header M879 (15); header M878 (28).)|(43)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1½″, with plain nut and lock washer.~  (For header M879 (8); header M878 (8); bracket SH966E (2); support B181 (2);~  support C69 (3).)|(23)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 1⅝″, with plain nut and lock washer.~  (For through (2) supports SH972A (3).)|(3)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 2″, with plain nut and lock washer.  (For~  support M179 (6); support M178 (6).)|(12)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 2¼″, with plain nut and lock washer.~  (For through (2) caps SH959E (1); quadrant M779 (2).)|(5)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 2¾″, with plain nut and lock washer.~  (For starting motor bracket SH137A (2); through two caps SH959D (3).)|(5)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 3½″, with plain nut.  (For post M4022 (1).)|(1)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅜″ x 3½″, with plain nut and lock washer.~  (For bracket SH137A (2).)|(2)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, 7/16″ x 1″, with plain nut and lock washer.  (For~  plate M2134B (5); plate M2134A (5).)|(10)|.01 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, 7/16″ x 1⅛″, with plain nut and lock washer.~  (For securing rear shell storage (16).)|(16)|.01 P
''')
add(31,r'''
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x ⅞″.  (For angle M2078 (1); angle M2080~  (1); angle M2079 (1); angle M2175 (3); angle M2176 (1); angle M2081B (4); angle~  M2081A (4); angle M2082B (4); angle M2082A (4); angle M2083B (3); angle~  M2083A (3); angle M2084B (3); angle M2084A (3); angle M2085 (2).)|(76)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1″, with nut and lock washer.  (For~  body SH951C (2); securing cap M1591 to casing M1590 (14); housing SH277A (1).)|(17)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1⅛″, with plain nut and lock washer.  (For~  cone SH959A (1).)|(1)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1¼″, with plain nut and lock washer.~  (For brace SH958K (1); strip SH978F (1); plate M786 (4); plate M787 (4).)|(10)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1⅜″, with plain nut and lock washer.~  (For stay SH289B (1); strip SH978T (1); angle SH978C (2); stay SH289D (1);~  securing outlet louvre (3); angle M785 (4).)|(14)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1 7/16″, with plain nut and lock washer.~  (For elbow SH402K (2).)|(4)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1½″, with plain nut and lock washer.~  (For clip SH976A (1); clip SH976C (1); strip SH978R (1); housing SH399B (2);~  box SH960B (5).)|(12)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1⅝″, with plain nut and lock washer.~  (For plate M1949 (4); angle M788 (4).)|(12)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 1¾″, with plain nut and lock washer.~  (For housing SH399B (2); bracket M184 (2); bracket M182 (4); bracket M183~  (4); angle M2090B (4); angle M2090A (4); angle M2091B (5); angle M2091A (5);~  hangar SH992B (8); bracket SH944A (4).)|(42)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 2⅛″, with plain nut and lock washer.~  (For securing sleeve M4023 to hull (2).)|(2)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 2½″, with plain nut and lock washer.~  (For link SH944B (1); link SH944C (1).)|(2)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 2 13/16″, with plain nut, plain and lock washer.~  (For block M3064B (4); block M3064A (4).)|(8)|.02 P
%(sh)R|21|21||||BOLT, U. S. Std., hexagon head, ½″ x 2⅞″, with plain nut and lock washer.~  (For plate M4160 (2); box M855 (8).)|(10)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 3″, with plain nut.  (For connection~  SH402H (1); manifold SH599A (1).)|(4)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 3 1/16″, with plain nut, plain and lock washer.~  (For block M3065A (3); block M3065B (3).)|(6)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 3⅜″, with plain nut and plain washer.~  (For block M3806B (2); block M3806A (2).)|(4)|.02 P
''')
add(32,r'''
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 3½″, with plain nut and lock washer.~  (For gate M751 (1); gate M752 (1).)|(2)|$0.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 3 9/16″, with plain nut and lock washer.~  (For through (2) brackets M3032 (1).)|(3)|.02 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 6¾″, with plain nut and lock washer.~  (For gate M751 (1); gate M752 (1).)|(2)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ½″ x 7¼″, with plain nut and lock washer.~  (For gate M751 (1); gate M752 (1).)|(2)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 1″.  (For plate M2801 (3).)|(3)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 1⅜″, with plain nut and lock washer.~  (For foot SH573B (2); foot SH573A (2); support SH574D (4).)|(8)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 1½″, with plain nut and lock washer.~  (For angle SH573M (2); angle M2793 (8); bracket M891 (1).)|(22)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 1½″.  (For angle M2794B (6); angle~  M2794A (6).)|(12)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 1 9/16″, with plain nut and lock washer.~  (For angle M2794A (5); angle M2794B (5).)|(10)|.03 P
%(sh)R||||||OLT, U. S. Std., hexagon head, ⅝″ x 1 11/16″, with plain nut and lock washer.~  (For angle M2794B (2); angle M2794A (2); angle M2793 (2).)|(8)|.03 P
%(sh)R||||||OLT, U. S. Std., hexagon head, ⅝″ x 1¾″, with plain nut and lock washer.~  (For plate M2116 (3); plate M1911 (4); securing (1) louvre front angle and piece~  SH535A (7).)|(14)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 2″, with plain nut and lock washer.  (For~  support C68 (2).)|(2)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 2¼″, with plain nut and lock washer.~  (For plate M1911 (2); bracket SH964A (1); securing (1) louvre front angle to~  bracket SH966A (2).)|(8)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 2 5/16″, with plain nut and lock washer.~  (For angle M2794A (1); angle M2794B (1).)|(2)|.03
''')

r=add(33,r'''
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 2½″, with plain nut and lock washer.~  (For bracket M182 (2); bracket M183 (2).)|(4)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 2½″.  (For block M3806A (2); block~  M3806B (2).)|(4)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 2¾″, with plain nut and lock washer.~  (For tank M1193 (2).)|(2)|.03 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ⅝″ x 3⅞″, with plain nut and lock washer.~  (For flange SH849A (1).)|(2)|.03 P
%(sh)R|25|21||||BOLT, U. S. Std., hexagon head, ¾″ x 1⅝″, with plain nut and lock washer.~  (For cleat M4129 (1).)|(2)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¾″ x 1¾″, with plain nut and lock washer.~  (For guide M2114 (4).)|(4)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¾″ x 2″, with plain nut and lock washer.  (For~  cleat M4130 (1).)|(4)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¾″ x 2¼″, with plain nut and lock washer.~  (For bracket SH971A (1); bracket SH971B (1).)|(2)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¾″ x 2⅜″, with plain nut and lock washer.~  (For securing driver’s seat to stays SH289A and SH289B (4).)|(4)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, ¾″ x 2½″, with plain nut and lock washer.~  (For bracket M184 (1).)|(1)|.04 P
%(sh)R||||||BOLT, U. S. Std., hexagon head, 1″ x 1½″.  (For bracket M3922 (1).)|(1)|.07 P
%(sh)R||||||BOLT, U. S. Std., square head, ⅜″ x 1¼″, with square nut and lock washer.~  (For cleat M1945B (2); cleat M1945A (2); cleat M1946A (2); cleat M1946B (2);~  cleat M1947 (2).)|(12)|.02 P
%(sh)R||||||BOLT, U. S. Std., square head, ⅝″ x 1½″, with square nut and lock washer.~  (For angle M2371 (2); angle M2370A (2); angle M2370B (2).)|(8)|.03 P
%(sh)R||||||BOLT, U. S. Std., square head, ⅝″ x 1¾″, with square nut and lock washer.~  (For piece M984 (7).)|(7)|.03 P
%(sh)R||||||BOLT, U. S. Std., square head, ⅝″ x 2 1/16″, with square nut and lock washer.~  (For angle M2072 (2).)|(6)|.03 P
%(sh)R||||||BOLT, U. S. Std., square head, ⅝″ x 2¼″, with square nut and lock washer.~  (For (1) angle M2072 (2).)|(2)|.03 P
%(sh)R||||||BOLT, U. S. Std., square head, ⅝″ x 2⅜″, with square nut and lock washer.~  (For (1) angle M2072 (1); hanger SH424B (1).)|(2)|.03 P
''')
bolt(r,'6-pdr. spare parts box','(2)','.29',note='&')
component(r,'*one SH942C 6-pdr. spare parts box BOLT (2)',price='.25')
nut(r,'½″','plain, U. S. Std., hexagon');lockwasher(r,'½″',end=False)
component(r,'one —      WASHER, plain, ⅝″.)')

r=start(34)
entry(r,'BOTTOM, gasoline tank strainer',note='&',ord='SH188C',qty='3',price='$0.24')
entry(r,'BOTTOM, transmission mechanical lubricator suction tube screen',note='&',ord='SH104E',qty='6',price='.06')
entry(r,'BOX, accessories or ration, assembly',note='(gv)&',ident='60',plate='2',qty='(2)',price='14.79');composed(r)
for part,desc,q,price in [('M4040D','BODY','2','5.28'),('M4040F','bottom ANGLE, long','2','.85'),('M4040E','bottom ANGLE, short','4','.38')]:
 component(r,f'*'+('two' if part=='M4040E' else 'one')+f' {part} accessories or ration box {desc} ({q})',ord='592',price=price)
component(r,'one —      accessories or ration box LID, assembly,')
component(r,'*one M4040C accessories or ration box lid supporting ANGLE, long (2)',ord='592',price='.65')
component(r,'*two M4040B accessories or ration box lid supporting ANGLE, short (4)',ord='592',price='.22')
entry(r,'twenty-eight —      RIVET, button head, ¼″ x ¾″.)')
entry(r,'BOX, clutch coupling',note='&',ident='17',plate='21',brit='M855',ord='870',qty='1',price='5.51')
entry(r,'BOX, cutout fuze, 6″ x 6″ x 3″',note='(ee)&',qty='1',price='.90')
entry(r,'BOX, fan bevel gear, assembly',note='%X',qty='(1)',price='52.18');composed(r)
component(r,'four {Timken\n                316–312}   BEARING, roller, assembly,')
for text in ['one —      chain wheel SPINDLE, assembly,','one SH233G driving pulley WASHER,','two M1125  fan bevel GEAR,','one M1123  fan bevel gear BOX,','one M1126  fan bevel gear box bearing cover PLATE,','one SH146A fan bevel gear box bearing cover plate GASKET,','one SH193C fan bevel gear box chain SPROCKET,','one M1124  fan bevel gear box COVER,','one M1128  fan bevel gear box long distance TUBE,','one M1129  fan bevel gear box pulley distance PIECE,','one —      fan bevel gear box pulley SPINDLE, assembly,','one M1127  fan bevel gear box short distance TUBE,','two SH146B fan bevel gear box side COVER,']:component(r,text)

r=start(35)
for text in ['two SH196A fan bevel gear box spindle KEY,','two SH194B fan bevel gear housing side cover GASKET,','one SH194A fan bevel gear housing upper cover GASKET,','one —      radiator cooling fan driving PULLEY, assembly,','two (SH194D) STUD, ⅜″ x 1½″, threaded U. S. Std. ½″ assembly,','two —      KEY, Woodruff, No. 18,','one Q52B   PLUG, pipe, square head, ¼″,','twelve —   SCREW, cap, U. S. Std., hexagon head, ¼″ x ½″,','two —      SCREW, cap, U. S. Std., hexagon head, ⅜″ x 1″,','twelve —   WASHER, lock, ¼″,','two —      WASHER, lock, ⅜″.)']:component(r,text)
entry(r,'BOX, fan bevel gear',note='&',ident='5',plate='20',brit='M1123',ord='194',qty='1',price='4.38')
entry(r,'BOX, house lamp spare battery, assembly',note='%X',ord='SH373A',qty='(1)',price='.99');composed(r)
for part,desc,price in [('SH373E','BACK','.10'),('SH373C','BOTTOM','.08'),('SH373L','corner iron HINGE, left','.08'),('SH373K','corner iron HINGE, right','.08'),('SH373G','DOOR','.10'),('SH373H','END, left','.08'),('SH373D','END, right','.08')]:
 component(r,f'*one {part} house lamp spare battery box {desc} (1)',price=price)
component(r,'one SH373J house lamp spare battery box spring CLIP,')
component(r,'*one SH373F house lamp spare battery box TOP (1)',price='.08')
component(r,'six —      BRAD, wire, No. 16 x 1¼″,')
component(r,'six —      RIVET, wagon box, ⅛″ x ½″,')
component(r,'two —      SCREW, wood, countersunk head, No. 6 (9/64−″) x ½″,')
component(r,'two —      SCREW, wood, round head, No. 6 (9/64−″) x 1″.)')
entry(r,'BOX, switch panel, assembly',note='(gy)&',qty='(1)',price='.66')
entry(r,'BOX, transmission mechanical lubricator stuffing',note='&',ord='SH102C',qty='1',price='.48')
entry(r,'BOX, (ventilating) fan discharge',note='&',ord='SH961A',qty='1',price='8.50')
entry(r,'BOX, ventilating fan intake',note='&',ord='SH960B',qty='1',price='12.50')
entry(r,'BOX, 6-pdr. gun tool, left, assembly',note='%X',ident='56',plate='2',qty='(1)',price='13.00');composed(r)
component(r,'*one SH942B 6-pdr. gun tool BOX, left (1)',price='9.00')
component(r,'one SH942E 6-pdr. gun tool box LID, left,')
component(r,'two SH942F 6-pdr. gun tool box lid HINGE,')
component(r,'six —      RIVET, button head, copper, ⅛″ x ⅜″,')
entry(r,'twenty-eight —      SCREW, wood, round head, No. 10 (3/16+″) x ¾″.)')

r=start(36)
entry(r,'BOX, 6-pdr. gun tool, right, assembly',note='X',qty='(1)',price='$13.00');composed(r)
component(r,'*one SH942A 6-pdr. gun tool BOX, right (1)',price='9.00')
component(r,'one SH942D 6-pdr. gun tool box LID, right,')
component(r,'two SH942F 6-pdr. gun tool box lid HINGE,')
component(r,'six —      RIVET, button head, copper, ⅛″ x ⅜″,')
entry(r,'twenty-eight —      SCREW, wood, round head, No. 10 (3/16+″) x ¾″.)')
for part,desc,q,price in [('SH920F','flexible conduit','1','.98'),('SH958K','inlet duct','1','1.18'),('SH960C','ventilating fan','4','.22')]:entry(r,'BRACE, '+desc,note='%X',ord=part,qty=q,price=price)
entry(r,'BRACKET, air gage board',note='%X',ord='SH980D',qty='2',price='.68')
for part,side in [('MX101','left'),('MX100','right')]:entry(r,'BRACKET, air pressure pump, '+side,note='%X',brit=part,ord='672',qty='1',price='.89')
entry(r,'BRACKET, angle (under driver’s turret)',note='*',ident='4',plate='10',brit='M2075',ord='343',qty='(1)',price='1.95')
entry(r,'BRACKET, brake lever fulcrum, assembly',note='%X',qty='(4)',price='2.53');composed(r)
component(r,'*one M4131 brake lever fulcrum BRACKET (4)',ord='172',price='2.52');cotter(r,'¼″ x 2″')
for part,ordn,desc,price,ident,plate in [
('M2126','477','(net support), left (sponson)','.88','',''),
('M2127','477','(net support), right (sponson)','.88','',''),
('M2128','359','(net support), left (main hull, rear)','.98','',''),
('M2129','359','(net support), right (main hull, rear)','.98','',''),
('M2132','359','(net support), left (main hull, front)','.98','6','10'),
('M2133','359','(net support), right (main hull, front)','.98','',''),
('M2130','359','(net support), left (main hull, intermediate)','.98','',''),
('M2131','359','(net support), right (main hull, intermediate)','.98','',''),
('M2440B','413','net support, left (main turret)','.97','',''),
('M2440A','413','net support, right (main turret)','.97','9','9'),
('M2439B','414','net support, left (front, main turret)','.86','',''),
('M2439A','414','net support, right (front, main turret)','.86','','')]:
 entry(r,'BRACKET, camouflage '+desc,note='(gai)&',ident=ident,plate=plate,brit=part,ord=ordn,qty='1',price=price)

r=start(37)
entry(r,'BRACKET, camp kettle, assembly',note='&',qty='(1)',price='2.99');composed(r)
component(r,'*one SH285B camp kettle BRACKET (1)',price='1.14')
component(r,'one —      spare fan belt HOLDER, assembly,')
component(r,'four —     RIVET, button head, ¼″ x ¾″.)')
entry(r,'BRACKET, carburetor throttle control shaft',note='%X',ident='8492',plate='15',mfr='B13354',ord='LQ108A',qty='1',price='.75')
entry(r,'BRACKET, (center control) intermediate shaft',note='&',brit='M639',ord='170',qty='3',price='.98')
entry(r,'BRACKET, clutch lever fulcrum',note='&',ord='SH944A',qty='1',price='2.55')
entry(r,'BRACKET, clutch throwout shaft',note='&',brit='M4148',ord='954',qty='1',price='2.58')
entry(r,'BRACKET, clutch throwout shaft (left), assembly',note='%X',qty='(1)',price='8.76');composed(r)
for text in ['two SH953B clutch throwout auxiliary operating LEVER,','one SH953C clutch throwout auxiliary operating SHAFT,','one SH953A clutch throwout shaft BRACKET,','two —      PIN, taper, type A, No. 6 x 3.″','two M4172  clutch throwout lever feather KEY.)']:component(r,text)
entry(r,'BRACKET, clutch throwout shaft, (left)',note='&',ord='SH953A',qty='1',price='2.18')
entry(r,'BRACKET, connecting lever fulcrum, assembly',note='&',qty='(2)',price='1.09');composed(r)
component(r,'*one SH956B connecting lever fulcrum BRACKET (2)',price='1.08');cotter(r,'3/16″ x 1⅛″')
entry(r,'BRACKET, deflector plate',note='%X',ord='SH380A',qty='1',price='3.18')
entry(r,'BRACKET, drive chain casing supporting, left',note='&',brit='M1588',ord='222',qty='2',price='1.44')
entry(r,'BRACKET, drive chain casing supporting, right',note='&',brit='M1587',ord='222',qty='2',price='1.44')
entry(r,'BRACKET, electric light (main turret)',note='%X',brit='M2434',ord='424',qty='2',price='.30')
entry(r,'BRACKET, engine control rocker arm, assembly',note='&',qty='(1)',price='3.11');composed(r)
component(r,'*one SH965A engine control rocker arm BRACKET, long (1)',price='2.25')
component(r,'*two SH965D engine control rocker arm BRACKET, short (2)',price='.40')
component(r,'six —      RIVET, button head, ⅜ x 1¼″.)')
for part,ordn,desc,qty,price in [('M182','70','engine double point suspension, left','1','2.25'),('M183','70','engine double point suspension, right','1','2.25'),('M2147','362','engine room sliding door roller','4','1.07'),('M184','70','engine single point suspension','1','7.76')]:
 entry(r,'BRACKET, '+desc,note='&',brit=part,ord=ordn,qty=qty,price=price)
entry(r,'BRACKET, fire extinguisher, with bottom cut off',note='%(gak)X',ord='SH544B',qty='2',price='2.25')
entry(r,'BRACKET, fire extinguisher (Bracket FF39A, w/holes drilled special for tank)',note='%(gak)X',ord='SH544A',qty='7',price='2.25')
entry(r,'BRACKET, foot brake lever fulcrum, assembly',note='&',qty='(2)',price='3.01');composed(r)
component(r,'*one M641 foot brake lever fulcrum BRACKET (triangular) (2)',ord='171',price='3.00');cotter(r,'¼″ x 1¾″')

r=start(38)
for part,ordn,desc,qty,price in [('M4136','173','foot and low speed brake rod spring','2','$1.12'),('M3067','451','forward ammunition storage, 30° angle','(2)','.38'),('M3068','451','forward ammunition storage, 60° angle','(2)','.38'),('M3066','451','forward ammunition storage, 90° angle','(10)','.32')]:
 entry(r,'BRACKET, '+desc,note='*',brit=part,ord=ordn,qty=qty,price=price)
entry(r,'BRACKET, funnel rack (front)',note='%X',ord='A3997',qty='1',price='.30')
entry(r,'BRACKET, funnel rack (rear)',note='%X',ord='A3998',qty='1',price='.36')
for desc,part,side in [('left, (front and right rear) (main hull)','SH395B','left'),('right (front and left rear) (main hull)','SH395A','right')]:
 entry(r,'BRACKET, gun hanger, '+desc+', assembly',note='&',qty='(2)',price='2.94');composed(r)
 component(r,f'*one {part} gun hanger BRACKET, {side} (2)',price='1.78')
 component(r,'one SH395E gun hanger bracket CAP,')
 component(r,'one —      gun hanger bracket PIN, assembly,')
 component(r,'one SH395G gun hanger compression SPRING,')
 component(r,'one SH395F gun hanger PLUNGER.)')
entry(r,'BRACKET, gun hanger (turret), assembly',note='&',ident='38',plate='2',qty='(1)',price='4.48');composed(r)
component(r,'*one SH395C gun hanger BRACKET (1)',price='1.78')
for text in ['one SH395E gun hanger bracket CAP,','one —      gun hanger bracket PIN, assembly,','one SH395G gun hanger compression SPRING,','one SH395F gun hanger PLUNGER,','one SH395D gun rest PLATE,','one SH395K gun retaining SPRING,','one —      RIVET, button head, 11/16″ x 2¼″,']:component(r,text)

r=start(39)
component(r,'two —      SCREW, cap, U. S. Std., round head, ¼″ x ⅜″,');lockwasher(r,'¼″',count='two')
entry(r,'BRACKET, hand lamp',note='%X',ord='SH373N',qty='2',price='.18')
entry(r,'BRACKET, hemispherical turret, assembly',note='&',qty='(6)',price='2.18');composed(r)
component(r,'*one M3121 hemispherical turret BRACKET (6)',ord='431',price='2.17')
component(r,'one M3127 locking SCREW.)')
entry(r,'BRACKET, high speed brake rod spring',note='*',brit='M4135',ord='173',qty='(2)',price='.49')
entry(r,'BRACKET, hot food container, assembly',note='&',qty='(1)',price='7.76');composed(r)
for part,desc,price in [('SH239D','BRACE (1)','2.28'),('SH239C','BRACE (1)','2.28'),('SH239B','PLATE, bottom','.42'),('SH239A','PLATE, top','1.18')]:component(r,f'*one {part} hot food container bracket {desc}',price=price)
component(r,'one —      hot food container bracket STRAP, buckle end, assembly,')
component(r,'one SH239E hot food container bracket STRAP, plain end,')
component(r,'six —      RIVET, belt, brass, No. 10 x ¾″,')
component(r,'eight —    RIVET, button head, ½″ x 1⅛″.)')
entry(r,'BRACKET, intermediate shaft',note='%X',brit='M631',ord='170',qty='3',price='.98')
entry(r,'BRACKET, jockey pulley',note='%X',brit='M1048',ord='234',qty='1',price='.54')
entry(r,'BRACKET, low speed brake band, assembly',note='&',qty='(2)',price='1.22');composed(r)
component(r,'one MX82 low speed brake band bracket SPACER,')
component(r,'one MX49 low speed brake band support BRACKET,')
component(r,'one MX81 brake band pin retainer SPRING,')
component(r,'one —      RIVET, button head, 3/16″ x 1⅜″.)')
entry(r,'BRACKET, low speed brake band support',note='&',brit='MX49',ord='683',qty='4',price='1.06')
entry(r,'BRACKET (machine gun), cleaning rod',note='%X',ord='B5926',qty='1',price='.38')
entry(r,'BRACKET, machine gunner’s seat strut fulcrum',note='&',brit='M2163',ord='362',qty='4',price='.22')
entry(r,'BRACKET, main turret flap suspension',note='*',brit='M2393',ord='423',qty='(1)',price='.38')
entry(r,'BRACKET, medical outfit, assembly',note='&',qty='(1)',price='1.87');composed(r)
component(r,'*one M2170 medical outfit BRACKET (1)',ord='365',price='1.08')
component(r,'one —      medical outfit bracket STRAP, buckle end, assembly')
component(r,'one SH365B medical outfit bracket STRAP, plain end,')
component(r,'four —     RIVET, button head, 3/16″ x ½″,')
component(r,'four —     RIVET, button head, ¼″ x ½″.)')
entry(r,'BRACKET, oil can.  (For left front and rear machine gun oiler)',note='%X',ord='B5925',qty='2',price='.45')
entry(r,'BRACKET, oil can.  (For right front machine gun oiler)',note='%X',ord='B5718',qty='1',price='.45')

r=start(40)
entry(r,'BRACKET, oil can.  (For left side machine gun oiler)',note='%X',ord='B5929',qty='1',price='$0.45')
entry(r,'BRACKET, oil can.  (For right side machine gun oiler)',note='%X',ord='B5924',qty='1',price='.45')
entry(r,'BRACKET, outlook turret compass',note='%X',brit='M2432',ord='413',qty='1',price='.42')
entry(r,'BRACKET, pyrene refill, assembly',note='%X',ord='C1905',qty='(1)',price='.672 P');composed(r)
for text in ['three A4044 pyrene refill BRACKET,','one B5933 pyrene refill bracket BAR, ½″ x 28⅞″ (front),','one B5934 pyrene refill bracket BAR, ¾″ x 28⅞″ (bottom),','one B5935 pyrene refill bracket BAR, ¾″ x 28⅞″ (rear),','seven A4055 pyrene refill bracket CLIP,','twelve —   RIVET, button head, ⅛″ x ½″,','nine —     RIVET, button head, ¼″ x 1″.)']:component(r,text)
entry(r,'BRACKET, pyrene refill',note='&',ord='A4044',qty='3',price='.48 P')
entry(r,'BRACKET, radiator support, front',note='&',ident='2',plate='11',brit='M891',ord='177',qty='2',price='1.12')
entry(r,'BRACKET, radiator support, rear',note='&',brit='M982',ord='177',qty='1',price='.98')
entry(r,'BRACKET, rear shell storage',note='&',brit='M3026',ord='550',qty='4',price='.25')
entry(r,'BRACKET, regulating tank valve',note='&',ord='SH950B',qty='1',price='.32')
entry(r,'BRACKET, rocker shaft (throttle control)',note='%X',ident='—',plate='12',ord='SH966A',qty='2',price='1.58')
entry(r,'BRACKET, shell holder',note='&',brit='M3024',ord='550',qty='44',price='.32')
entry(r,'BRACKET, spark and throttle control lever',note='&',ord='SH964A',qty='2',price='2.25')
entry(r,'BRACKET, spark control bell crank lever, top',note='&',ident='—',plate='12',ord='SH967A',qty='1',price='2.08')
entry(r,'BRACKET, sponson ram rod, assembly',note='&',qty='(4)',price='.59');composed(r)
component(r,'*one M2834 sponson ram rod BRACKET (4)',ord='471',price='.38')
component(r,'one M2835 sponson ram rod bracket CLIP,')
component(r,'three —    RIVET, countersunk head, ⅛″ x ½″.)')
entry(r,'BRACKET, sponson roller',note='&',brit='M2382',ord='470',qty='2',price='2.28')
entry(r,'BRACKET, starting motor',note='%X',ord='SH137A',qty='1',price='5.37')
entry(r,'BRACKET, switchboard (large)',note='%X',ord='SH994E',qty='1',price='.48')
entry(r,'BRACKET, switchboard (small)',note='%X',ord='SH994D',qty='1',price='.38')

r=start(41)
entry(r,'BRACKET, tail light',note='&',ord='SH584K',qty='1',price='.55')
entry(r,'BRACKET, telescopic sight case carrier (sponson), assembly',note='&',qty='(2)',price='.78');composed(r)
component(r,'one M2837 telescopic sight case CARRIER,')
component(r,'one M2836 telescopic sight case carrier BRACKET,')
component(r,'two —      RIVET, button head, ⅛″ x 7/16″.)')
entry(r,'BRACKET, telescopic sight case carrier (sponson)',note='&',ident='37\n3&7',plate='2\n28',brit='M2836',ord='471',qty='2',price='.38')
r[-1].update(space_before=0.5,space_after=0.5,cell_baseline_offsets=dict(ident=-.5,plate=-.5))
entry(r,'BRACKET, tension adjusting screw',note='%X',brit='M1472',ord='60',qty='4',price='15.75')
entry(r,'BRACKET, throttle control bell crank lever',note='%X',ident='—',plate='12',ord='SH966E',qty='1',price='.98')
entry(r,'BRACKET, throttle control bell crank lever',note='%X',ident='—',plate='12',ord='SH967D',qty='1',price='1.15')
entry(r,'BRACKET, tool chest fastening',note='&',ord='SH486A',qty='1',price='1.08')
entry(r,'BRACKET, towing, back',note='&',ident='1',plate='3',brit='M3918',ord='648',qty='1',price='12.75')
entry(r,'BRACKET, towing, front',note='&',ident='1',plate='10',brit='M3917',ord='648',qty='1',price='12.75')
entry(r,'BRACKET, towing, roof',note='&',ident='30',plate='2',brit='M3922',ord='649',qty='1',price='12.65')
entry(r,'BRACKET, towing, side',note='&',ident='1\n8',plate='4\n9',brit='M3919',ord='647',qty='2',price='8.78')
r[-1].update(space_before=0.5,space_after=0.5,cell_baseline_offsets=dict(ident=-.5,plate=-.5))
entry(r,'BRACKET, track brake band, assembly',note='&',qty='(2)',price='1.17');composed(r)
component(r,'one MX81 brake band pin retainer SPRING,')
component(r,'one MX47 track brake band BRACKET,')
component(r,'one —      RIVET, button head, 3/16″ x ⅞″.)')
entry(r,'BRACKET, track brake band',note='&',brit='MX47',ord='692',qty='4',price='1.08')
entry(r,'BRACKET, transmission brake band stop, assembly',note='&',qty='(2)',price='4.80');composed(r)
component(r,'one M342 transmission brake band stop BAR,')
component(r,'*one M341 transmission brake band stop BRACKET (2)',ord='683',price='.98')
component(r,'four —     RIVET, button head, ¼″ x 1¼″.)')
entry(r,'BRACKET, transmission high speed brake anchor',note='&',ident='13',plate='30',brit='M362',ord='697',qty='2',price='3.75')
entry(r,'BRACKET (transmission mechanical lubricator tank), supporting',note='%X',ord='SH971A',qty='1',price='.98')
entry(r,'BRACKET (transmission mechanical lubricator tank), supporting',note='%X',ord='SH971B',qty='1',price='1.08')
entry(r,'BRACKET, transmission pinion shaft bearing housing, assembly',note='&',ord='C7535',qty='(1)',price='9.05');composed(r)
component(r,'*one B6205 transmission pinion shaft bearing housing BRACKET (1)',price='7.75')
component(r,'one A7679 transmission pinion shaft bearing housing bracket CAP,')
component(r,'two (A7681) STUD, ⅝″ x 2¼″, threaded U. S. Std. 1″ and S. A. E. 1″,\n                         assembly.)')

r=start(42)
entry(r,'BRACKET, transmission sprocket bearing, inside, assembly',note='(gq)&',ident='9',plate='22',qty='(2)',price='$57.10');composed(r)
component(r,'*one M293 transmission sprocket bearing BRACKET, inside (2)',ord='662',price='55.00')
component(r,'two (MX10) STUD, ¾″ x 4⅞″, threaded U. S. Std. 1½″ and S. A. E.\n                         1⅛″, assembly,')
component(r,'two (MX36) STUD, ¾″ x 5½″, threaded U. S. Std. 1½″ and S. A. E.\n                         1⅛″, assembly.)')
entry(r,'BRACKET, transmission sprocket bearing, outside, assembly',note='(gq)&',ident='1',plate='22',qty='(2)',price='70.68');composed(r)
component(r,'*one M297 transmission sprocket bearing BRACKET, outside (2)',ord='662',price='65.00')
component(r,'two —      transmission sprocket bearing outside bracket support\n                         FOOT, assembly,')
component(r,'four (MX9) STUD, ¾″ x 3⅝″, threaded U. S. Std. 1½″ and S. A. E.\n                         1⅛″, assembly.)')
entry(r,'BRACKET, water can, inner, assembly',note='%X',qty='(1)',price='2.76');composed(r)
component(r,'*one SH293A water can BRACKET, inner (1)',price='2.08')
component(r,'four A8174 FASTENER, strap, No. 10,')
component(r,'eight —    RIVET, button head, 3/16″ x ¾″.)')
entry(r,'BRACKET, water can, outer, assembly',note='%X',qty='(1)',price='7.68');composed(r)
component(r,'*one SH293B water can BRACKET, outer (1)',price='2.08')
component(r,'four —     water can STOP, assembly,')
component(r,'eight —    RIVET, countersunk head, ¼″ x 1″.)')
entry(r,'BRACKET, 6-pdr. gun pedestal stop, left',note='&',brit='M3798B',ord='511',qty='2',price='.50')
entry(r,'BRACKET, 6-pdr. gun pedestal stop, right',note='&',brit='M3798A',ord='511',qty='2',price='.50')
entry(r,'BRAD, wire, No. 16, 1¼″, lb.  (For house lamp spare battery box (6).)',note='&(mh)R',qty='6',price='.09 P')
entry(r,'BREATHER, crank case',note='%X',mfr='B8365',ord='LQ234A',qty='1',price='1.50')
entry(r,'BRIDLE, foot brake',note='&',ident='—',plate='6',brit='M765',ord='215',qty='1',price='6.75')
entry(r,'BRUSH, distributor rotor, with spring, assembly',note='%X',mfr='D14182',qty='(2)',price='.06 P')

r=start(43)
composed(r)
component(r,'*one D29615 distributor rotor BRUSH (2)',price='.03 P')
component(r,'*one D29617 distributor rotor brush SPRING (2).)',price='.03 P')
entry(r,'BRUSH, generator',note='&',mfr='D30449',qty='4',price='.01 P')
entry(r,'BUCKLE, barrel roller, 1¼″.  (For strap SH443C (1); strap SH285D (1); strap\n  SH365A (1).)',note='&(mh)R',brit='B6496F',qty='3',price='.04 P')
entry(r,'BUCKLE, barrel roller, 1½″.  (For strap SH239F (1).)',note='&(mh)R',brit='ZA1GAABA',qty='1',price='.05 P')
entry(r,'BUCKLE, barrel roller, 2″.  (For strap A3990 (1).)',note='&(mh)R',brit='ZA1HCADA',qty='1',price='.06 P')
entry(r,'BUCKLE, map board.  (For board M2441 (1).)',note='X',brit='M2443',ord='424',qty='2',price='.06 P')
entry(r,'BURR, copper, No. 8.  (For wood screw securing funnel rack web strap (1).)',note='%(sh)R',qty='7',price='.01 P')
entry(r,'BUSHING, air pressure pump',note='&',ord='SH901C',qty='2',price='.35')
entry(r,'BUSHING, bronze, O. D. 5.118″, I. D. 4 7/16″, over-all length, 8″.  (For shaft\n  M1544 (2); shaft M1402 (2); shaft M1474 (2).)',note='%X',ident='2',plate='28',brit='M1409',ord='56',qty='12',price='12.00')
entry(r,'BUSHING, cam shaft driving shaft, upper, large',note='&',ident='—\n8092',plate='34\n13',mfr='8092',ord='LQ76A',qty='2',price='.17')
r[-1].update(space_before=0.5,space_after=0.5,cell_baseline_offsets=dict(ident=-.5,plate=-.5))
entry(r,'BUSHING, cam shaft driving shaft, upper, small',note='&',ident='8107\n—',plate='13\n34',mfr='8107',ord='LQ75A',qty='2',price='.10')
r[-1].update(space_before=0.5,space_after=0.5,cell_baseline_offsets=dict(ident=-.5,plate=-.5))
entry(r,'BUSHING, clutch end bearing',note='&',ident='14',plate='21',ord='SH997B',qty='1',price='1.25')
for size,part,price in [('½″','A8406A','.05 P'),('¾″','A8405A','.07 P'),('1½″','A8403','.21 P')]:
 entry(r,f'BUSHING, conduit, {size}.  (For conduit {part} (1).)',note='%(ee)X',qty='1',price=price)
entry(r,'BUSHING, connecting rod piston pin',note='&',ident='8007',plate='18',mfr='8007',ord='LQ136A',qty='12',price='.20')
for part,text,qty,price in [('D29785','distributor condenser and breaker plate stud','6','.01 P'),('D29630','distributor connector plate screw insulating','4','.02 P'),('D29596','distributor contact arm dismounting stud insulating','6','.08 P')]:
 entry(r,'BUSHING, '+text,note='&',mfr=part,qty=qty,price=price)
entry(r,'BUSHING, drive sprocket chain collar',note='%X',ord='SH40A1D',qty='50',price='.90')
entry(r,'BUSHING, engine oil tank (bottom)',note='&',ord='SH978S',qty='1',price='.08')
for part,text,qty,price in [('D30136','generator brush arm mounting stud insulating','1','.06 P'),('D30079','generator brush arm mounting stud insulating','1','.04 P'),('D29868','generator brush arm mounting stud insulating','1','.04 P'),('D29849','generator brush arm spring stud','4','.04 P'),('D30140','generator field coil insulating','2','.02 P'),('D30262','generator field coil long stud','1','.02 P')]:
 entry(r,'BUSHING, '+text,note='&',mfr=part,qty=qty,price=price)
entry(r,'BUSHING, governor arm',note='&',ord='SH142A',qty='1',price='.24')
entry(r,'BUSHING, hemispherical turret supporting bracket',note='&',brit='M3126',ord='428',qty='6',price='.42')
entry(r,'BUSHING, large planet pinion, bronze',note='&',ident='23',plate='22',brit='M282',ord='680',qty='6',price='2.00')
entry(r,'BUSHING, large planet pinion, steel',note='&',ident='24',plate='22',brit='M283',ord='680',qty='6',price='1.50')
entry(r,'BUSHING, pipe, ¼″ x ⅛″ (M. I.).  (For tube C8012 (1); tube C8015 (1).)',note='%(pf)X',ord='B6495X',qty='4',price='.04 P')
entry(r,'BUSHING, oil pump driving shaft, lower',note='&',mfr='8185',ord='LQ432A',qty='1',price='.10')

r=add(44,r'''
&|—|33|8201||LQ442A|BUSHING, oil pump driving shaft, upper|1|$0.50
(pf)&||||||BUSHING, reducing, pipe, ⅜″ x ¼″ (beaded).  (For connection SH950D (2).)|2|.02 P
(pf)&||||||BUSHING, reducing, pipe, M. I., ½″ x ¼″.  (For pipe SH976E (1).)|2|.04 P
&||||X248|801|BUSHING, semaphore bottom bearing block|1|.38
&|32|22||M272|680|BUSHING, small planet pinion, bronze|6|1.25
&|33|22||M271|680|BUSHING, small planet pinion, steel|6|1.00
&|43|22||M268|703|BUSHING, sun pinion, small|2|2.40
&|||D29843|||BUSHING, tachometer drive shaft|1|.04 P
&|||D22921|||BUSHING, tachometer drive shaft flanged|1|.04 P
&|||D22920|||BUSHING, tachometer drive shaft plain|1|.04 P
&|2|26||M1263|50|BUSHING, track link|312|1.25
&|12|29||M1339|56|BUSHING, track roller tube|116|4.00
&|41|22||M265|707|BUSHING, transmission brake bearing|2|6.50
&|50|22||M261|703|BUSHING, transmission flanged sleeve, inner|2|3.50
&|57|22||M262|707|BUSHING, transmission flanged sleeve, outer|2|5.50
''')
for desc,ident,part,price,cp in [('inside','8','M296','8.58','8.50'),('outside','5','M299','6.58','6.50')]:
 entry(r,'BUSHING, transmission sprocket bearing, '+desc+', assembly',note='&',ident=ident,plate='22',qty='(2)',price=price);composed(r)
 component(r,f'*one {part} transmission sprocket bearing BUSHING, {desc} (2)',ord='707',price=cp)
 component(r,'one M300 DOWEL, bronze, ⅝″ x ½″.)')
for part,desc,qty,price in [('D30368','voltage regulator housing insulating','3','.02 P'),('D25469','voltage regulator, insulating, thick','1','.03 P'),('D25468','voltage regulator insulating, thin','6','.03 P')]:
 entry(r,'BUSHING, '+desc,note='&',mfr=part,qty=qty,price=price)
entry(r,'BUSHING, water pump bevel driver',note='&',ident='8062',plate='19',mfr='B8062',ord='LQ159A',qty='2',price='.90')
entry(r,'BUTTERFLY, carburetor',note='&',mfr='13368',ord='LQ523A',qty='4',price='.22')
entry(r,'BUTTON, transmission mechanical lubricator adjusting',note='&',ord='SH102H',qty='6',price='.20')
