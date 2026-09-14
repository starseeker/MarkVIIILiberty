"""Photograph-led transcription of printed pages 125–144.
Original page breaks, blank fields and apparent source errors retained.
"""
from .parts_tables import row
from .opening_tables import entry,component,composed
from .tables_045_064 import assembly
from .tables_065_084 import pieces,stacked
TABLES={}
def start(page):
 TABLES[page]=[]
 return TABLES[page]
def continued(r,text,note='&',**kw):
 entry(r,text,note=note,**kw);composed(r)

r=start(125)
entry(r,'NUT, castle, No. 6—32 x .218″ x .188″ thick. (For distributor resistance unit\n   mounting stud D29663; distributor contact arm spring screw D29574.)',note='&',mfr='D29573',qty='6',price='.03 P')
entry(r,'NUT, castle, No. 10—30 x .437″ x .218″ thick. (For voltage regulator terminal\n   stud D30366; ignition switch, assembly D1120 (9); distributor advance lever\n   stud D29896; ignition switch screw D30362; generator field coil stud D29829;\n   generator field coil stud D30383.)',note='&',mfr='D29864',qty='19',price='.06 P')
entry(r,'NUT, castle, No. 10—30 x .437″ x .406″ thick. (For distributor condenser and\n   breaker plate stud D29595.)',note='&',mfr='D30646',qty='2',price='.03 P')
entry(r,'NUT, castle, ¼″—28 x .437″ x .281″ thick. (For voltage regulator, assembly\n   D5721; voltage regulator terminal stud D30380; generator brush arm mounting\n   stud D29811; distributor ignition coil and distributor head stud D29635.)',note='&',mfr='D29917',qty='7',price='.03 P')
entry(r,'NUT, castle, ¼″—28 x .437″ x .281″ thick. (For regulator voltage, assembly\n   D5718.)',note='&',mfr='D30527',qty='1',price='.03 P')
entry(r,'NUT, castle, ⅜″—24 x 9/16″ x 13/32″ thick. (For generator armature shaft (commu-\n   tator end).)',note='&',mfr='D30309',qty='1',price='.03 P')
entry(r,'NUT, clutch stop eyebolt (plain, U. S. Std., hexagon, ⅜″ thick)',note='%X',ord='SH955B',qty='2',price='.02 P')
entry(r,'NUT, clutch throwout stop rod',note='%X',ord='SH955D',qty='4',price='.04 P')
for size,code,price in [('½','A8406','.02 P'),('¾','A8405','.03 P'),('1','A8404','.04 P'),('1½','A8403','.06 P')]:
 entry(r,'NUT, conduit lock, '+size+'″. (For conduit '+code+'.)',note='(ee)&',qty='2',price=price)
entry(r,'NUT, connecting forked end rod bolt',note='&',ident='13220',plate='18',mfr='B14284',ord='LQ126A',qty='24',price='.03')
entry(r,'NUT, connecting plain end rod bolt',note='&',ident='13251',plate='18',mfr='14283',ord='LQ134A',qty='12',price='.04')
entry(r,'NUT, crank case lower to upper bolt',note='&',mfr='B265',ord='LQ244A',qty='50',price='.07')
entry(r,'NUT, crank shaft',note='&',ident='26',plate='21',ord='SH136A',qty='1',price='.72')
entry(r,'NUT, crank shaft flywheel hub thrust bearing retaining',note='&',mfr='B12222',ord='LQ275A',qty='1',price='1.87')
entry(r,'NUT, crown, U. S. Std., 7/16″. (For sprocket X257 (1); shaft X266 (1).)',note='&(sh)R',qty='3',price='.01 P')
entry(r,'NUT, crown, U. S. Std., ½″. (For separator SH234G (2); axle SH234K (2); axle\n   SH234L (1).)',note='%(sh)R',qty='5',price='.01 P')
entry(r,'NUT, crown, U. S. Std., ⅝″. (For pin M4165 (1).)',note='%(sh)R',qty='1',price='.01 P')
entry(r,'NUT, cylinder to crank case stud (flanged). (For stud LQ247A (1).)',note='%X',mfr='B13535',ord='LQ249A',qty='28',price='.10')
entry(r,'NUT, distance recorder cable casing coupling',note='&',mfr='P300',ord='586',qty='2',price='.12 P')
entry(r,'NUT, distance recorder drive pinion',note='(gy)&',mfr='S11',ord='586',qty='1',price='.04 P')
entry(r,'NUT, distributor contact arm dismounting stud',note='&',mfr='D29494',qty='6',price='.15 P')
entry(r,'NUT, distributor cup stud',note='&',mfr='D30535',qty='8',price='.05 P')
assembly(r,'NUT, distributor head, with connector, assembly','.16 P',note='&',mfr='D13811',qty='(4)')
pieces(r,'''*one D29694 distributor head attaching SPRING,
*one D13738 distributor head terminal NUT,
*one D29664 distributor induction coil CONNECTOR.)''')

r=start(126)
entry(r,'NUT, distributor head high tension terminal',note='%X',mfr='D31698',qty='12',price='$0.01 P')
entry(r,'NUT, distributor terminal screw (brass, round, No. 10—35 x .36″ x .171″ thread)',note='&',mfr='D30996',qty='4',price='.02 P')
entry(r,'NUT, (engine) oil tank suction oil tube nipple',note='&',ord='SH207D',qty='2',price='.08')
entry(r,'NUT, flared tube union, S. A. E., ¼″. (For oil pressure gage SH559C (1); pipe\n   SH99H (1); pipe (assembly) SH99G (1); pipe (assembly) SH559D (1).)',note='%(pf)R',ord='Q50AA',qty='4',price='.11 P')
entry(r,'NUT, generator drive shaft end housing packing',note='&',mfr='D29763',qty='1',price='.06 P')
entry(r,'NUT, generator driving shaft',note='&',ident='8151',plate='16',mfr='13478',ord='LQ401A',qty='1',price='.35 P')
entry(r,'NUT, governor arm bushing set screw (jam, ⅜″)',note='&',ord='SH142C',qty='1',price='.02 P')
entry(r,'NUT, jam, U. S. Std., 5/16″. (For screw B33N (2).)',note='%(sh)R',qty='20',price='.01 P')
entry(r,'NUT, jam, U. S. Std., 1″. (For foot M391 (1).)',note='%(sh)R',qty='2',price='.02 P')
entry(r,'NUT, large planet pinion. (For shaft M782 (2); pin M284 (1).)',note='&',ident='13',plate='22',brit='M313',ord='679',qty='8',price='.24')
entry(r,'NUT, lower crank case bearing bolt',note='&',ord='LQ192A',qty='16',price='.08')
entry(r,'NUT, machine screw, No. 8 (5/32″)—30. (For screw, machine, round head, No. 8 x\n   ⅜″; airplane watch mat screw; machine screw, NC round head, No. 8 x 1 (1).)',note='%(sh)R',qty='14',price='.01 P')
entry(r,'NUT, machine screw, No. 10 (3/16″)—24. (For screw, machine, round head, No. 10\n   x ½″; screw, machine, round head, No. 10 x ¾″; screw, machine, round head,\n   No. 10 x 1″.)',note='%(sh)R',qty='7',price='.01 P')
entry(r,'NUT, oil pump upper screen',note='%X',ident='—',plate='33',mfr='8535',ord='LQ458A',qty='1',price='.03')
entry(r,'NUT, pigeon basket hook (U. S. Std., hexagon, ½″, 5/16″ thick)',note='%X',ord='SH373Q',qty='1',price='.02 P')
entry(r,'NUT, pipe, elbow, ¼″ (Herring Motor Co. type No. 61F). (For cap M298;\n   cap M294)',note='%X',ord='SH664B',qty='4',price='.02 P')
entry(r,'NUT, pipe lock, ⅝″. (For eyebolt M3190.)',note='%(sh)R',qty='2',price='.03 P')
entry(r,'NUT, pipe lock, ¾″. (For rod M566 (2); rod M571 (2).)',note='%(sh)R',qty='4',price='.04 P')
entry(r,'NUT, plain, S. A. E., hexagon, ¼″. (For bolt SH101Q.)',note='%(sh)R',qty='6',price='.01 P')
entry(r,'NUT, plain, S. A. E., hexagon, 5/16″. (For rod SH993A; rod SH968H)',note='%(sh)R',qty='2',price='.01 P')
entry(r,'NUT, plain, S. A. E., hexagon, ⅜″. (For bolt MX22 (2); stud MX99; screw\n   M400; bolt, S. A. E., ⅜″ x 2¼″; rod SH968D (2); rod SH993K; rod SH968A (2);\n   rod SH969B (2).)',note='%(sh)R',qty='31',price='.01 P')
entry(r,'NUT, plain, S. A. E., hexagon, ½″. (For stud MX99; screw MX88; screw M343;\n   rod SH969C (2); rod SH969D (2); rod SH969A (2).)',note='%(sh)R',qty='20',price='.01 P')

r=start(127)
entry(r,'NUT, plain, S. A. E., hexagon, ¾″. (For bolt M388)',note='%(sh)R',qty='2',price='.01 P')
entry(r,'NUT, plain, U. S. Std., hexagon, 3/16″. (For bolt, U. S. Std., hexagon head,\n   3/16″ x ⅝″)',note='%(sh)R',qty='4',price='.01 P')
entry(r,'''NUT, plain, U. S. Std., hexagon, ¼″. (For rod M743; rod M778; bolt, U. S.
   Std., hexagon head, ¼″ x ⅝″; bolt, U. S. Std., hexagon head, ¼″ x ¾″; bolt,
   U. S. Std., hexagon head, ¼″ x ⅞″ for strap SH569P (2); bolt, U. S. Std., hex-
   agon head, ¼″ x 1″; bolt, U. S. Std., hexagon head, ¼″ x 1⅜″; bolt, U. S. Std.,
   hexagon head, ¼″ x 1½″; bolt, U. S. Std., hexagon head, ¼″ x 1 7/16″; bolt, U. S.
   Std., hexagon head, ¼″ x 1⅝″; screw, cap, U. S. Std., button head, ¼″ x 2″;
   brace SH960C (2).)''',note='%(sh)R',qty='61',price='.01 P')
entry(r,'''NUT, plain, U. S. Std., hexagon, 5/16″. (For stud X251; block X263 (2); block X262
   (2); bolt, U. S. Std., hexagon head, 5/16″ x ⅞″; bolt, U. S. Std., hexagon head,
   5/16″ x ¾″; bolt, U. S. Std., hexagon head, 5/16″ x 1″; bolt, U. S. Std., hexagon head,
   5/16″ x 1¼″; screw, cap, U. S. Std., hexagon head, 5/16″ x ⅞″; screw, cap, U. S. Std.,
   hexagon head, 5/16″ x 1″; screw, cap, round head, 5/16″ x 1″ (2).)''',note='%(sh)R',qty='101',price='.01 P')
entry(r,'NUT, plain, U. S. Std., hexagon, 5/16″, bronze. (For plug SH951E.)',note='%(sh)R',qty='3',price='.03 P')
entry(r,'''NUT, plain, U. S. Std., hexagon, ⅜″. (For stud SH194D; bolt SH550A; bolt
   SH402L (2); bolt, U. S. Std., countersunk head, ⅜″ x ⅞″; bolt, U. S. Std.,
   countersunk head, ⅜″ x 1⅜″; bolt, U. S. Std., countersunk head, ⅜″ x 1½″;
   bolt, U. S. Std., hexagon head, ⅜″ x ¾″; bolt, U. S. Std., hexagon head, ⅜″ x
   ⅞″; bolt, U. S. Std., hexagon head, ⅜″ x 1″; bolt, U. S. Std., hexagon head,
   ⅜″ x 1 1/16″; bolt, U. S. Std., hexagon head, ⅜″ x 1⅛″ for housing SH145A; bolt,
   U. S. Std., hexagon head, ⅜″ x 1¼″; bolt, U. S. Std., hexagon head, ⅜″ x 1⅜″;
   bolt, U. S. Std., hexagon head, ⅜″ x 1 5/16″; bolt, U. S. Std., hexagon head, ⅜″ x
   1½″; bolt, U. S. Std., hexagon head, ⅜″ x 1⅝″; bolt, U. S. Std., hexagon head,
   ⅜″ x 2″; bolt, U. S. Std., hexagon head, ⅜″ x 2¼″; bolt, U. S. Std., hexagon
   head, ⅜″ x 2¾″; bolt, U. S. Std., hexagon head, ⅜″ x 3½″; pin M2149; screw,
   cap, U. S. Std., flat head, ⅜″ x 1⅛″; screw cap, U. S. Std., flat head, ⅜″ x 1 5/16″;
   screw, cap, U. S. Std., flat head, ⅜″ x 1½″.)''',note='%(sh)R',qty='226',price='.01 P')
entry(r,'NUT, plain, U. S. Std., hexagon, brass, ⅜″. (For clamp SH154A (2); clamp\n   SH154C (2).)',note='%(sh)R',qty='8',price='.03 P')
entry(r,'NUT, plain, U. S. Std., hexagon, 7/16″. (For screw M4175; bolt, U. S. Std., hexagon\n   head, 7/16″ x 1″; bolt, U. S. Std., hexagon head, 7/16″ x 1⅛″; screw, cap, U. S. Std.,\n   round head, 7/16″ x 1¼″.)',note='%(sh)R',qty='29',price='.02 P')

r=start(128)
entry(r,'''NUT, plain, U. S. Std., hexagon, ½″. (For eyebolt M754 (2); stop M799; stud
   SH279D; eyebolt M4156 (2); shaft SH900D; bolt SH501B; bolt SH550A; bolt
   SH942C; bolt SH586G; bolt, U. S. Std., hexagon head, ½″ x ⅞″; bolt, U. S. Std.,
   hexagon head, ½″ x 1″; bolt, U. S. Std., hexagon head, ½″ x 1⅛″; bolt, U. S. Std.,
   hexagon head, ½″ x 1¼″; bolt, U. S. Std., hexagon head, ½″ x 1⅜″; bolt, U. S.
   Std., hexagon head, ½″ x 1 7/16″; bolt, U. S. Std., hexagon head, ½″ x 1½″; bolt,
   U. S. Std., hexagon head, ½″ x 1⅝″; bolt, U. S. Std., hexagon head, ½″ x 1¾″;
   bolt, U. S. Std., hexagon head, ½″ x 2⅛″; bolt, U. S. Std., hexagon head, ½″ x
   2½″; bolt, U. S. Std., hexagon head, ½″ x 2 13/16″; bolt, U. S. Std., hexagon head,
   ½″ x 2⅞″; bolt, U. S. Std., hexagon head, ½″ x 3″; bolt, U. S. Std., hexagon
   head, ½″ x 3 1/16″; bolt, U. S. Std., hexagon head, ½″ x 3½″; bolt, U. S. Std.,
   hexagon head, ½″ x 3 9/16″; bolt, U. S. Std., hexagon head, ½″ x 3⅝″; bolt, U. S.
   Std., hexagon head, ½″ x 6¾″; bolt, U. S. Std., hexagon head, ½″ x 7¼″; pin
   M2405 (2); pin M2411; pin M2425; pin M2770; pin M2627; screw, set, square
   head, cup point, ½″ x 2″; staple M1338 (2); stud SH970D; stud SH970B; stud
   SH279D; stud SH996G)''',note='%(sh)R',qty='518',price='$0.01 P')
entry(r,'''NUT, plain, U. S. Std., hexagon, ⅝″. (For pin SH943A; bolt, U. S. Std., coun-
   tersunk head, ⅝″ x 1¾″; bolt, U. S. Std., hexagon head, ⅝″ x 1⅜″; bolt, U. S.
   Std., hexagon head, ⅝″ x 1½″ for angles SH573M, M2793 and bracket M891;
   bolt, U. S. Std., hexagon head, ⅝″ x 1 9/16″; bolt, U. S. Std., hexagon head, ⅝″
   x 1 11/16″; bolt, U. S. Std., hexagon head, ⅝″ x 1¾″; bolt, U. S. Std., hexagon head,
   ⅝″ x 2 5/16″; bolt, U. S. Std., hexagon head, ⅝″ x 2″; bolt, U. S. Std., hexagon head,
   ⅝″ x 2¼″; bolt, U. S. Std., hexagon head, ⅝″ x 2½″; bolt, U. S. Std., hexagon
   head, ⅝″ x 2¾″; bolt, U. S. Std., hexagon head, ⅝″ x 3⅞″; end M3189; screw,
   cap, U. S. Std., flat head, ⅝″ x ½″; screw, cap, U. S. Std., flat head, ⅝″ x 1¾″;
   screw, cap, U. S. Std., flat head, ⅝″ x 1⅞″; screw, cap, U. S. Std., flat head,
   ⅝″ x 2⅛″; screw, cap, U. S. Std., flat head, ⅝″ x 2 3/16″; screw, cap, U. S. Std.,
   flat head, ⅝″ x 2¼″; screw, cap, U. S. Std., flat head, ⅝″ x 2⅜″; screw, cap, U. S.
   Std., flat head, ⅝″ x 2½″; screw, cap, U. S. Std., flat head, ⅝″ x 2⅝″; screw, cap,
   U. S. Std., flat head, ⅝″ x 2⅞″; screw, cap, U. S. Std., flat head, ⅝″ x 3½″;''',note='%(sh)R')

r=start(129)
entry(r,'   screw, cap, U. S. Std., flat head, ⅝″ x 3⅝″; stud SH964E.)',qty='170',price='.01 P')
entry(r,'''NUT, plain, U. S. Std., hexagon, ¾″. (For rod M789A (2); rod M789B (2); rod
   SH953D (2); bolt M3128; bolt, U. S. Std., hexagon head, ¾″ x 2¼″; bolt, U. S.
   Std., hexagon head, ¾″ x 2⅜″; bolt, U. S. Std., hexagon head, ¾″ x 2½″; bolt,
   U. S. Std., hexagon head, ¾″ x 1⅝″; bolt, U. S. Std., hexagon head, ¾″ x 1¾″;
   bolt, U. S. Std., hexagon head, ¾″ x 2″; rod SH229A (2); rod M581 (2); rod M576
   (2); rod M579 (2); rod M578 (2); rod SH946D (2); rod M575 (2); rod M574 (2);
   rod M573 (2); rod SH946E (2); screw, cap, U. S. Std., flat head, ¾″ x 3⅜″; stud
   SH964E (2).)''',note='%(sh)R',qty='81',price='.01 P')
entry(r,'NUT, plain, No. 5–50 x 7/32″ x 7/64″ thick. (For voltage regulator screw D13795; dis-\n   tributor contact screw D13687)',note='&',mfr='D21748',qty='7',price='.01 P')
entry(r,'NUT, plain, brass, No. 8–36 x 19/64″ x .125″ thick. (For voltage regulator armature\n   regulating spring adjusting screw.)',note='&',mfr='D30142',qty='1',price='.01 P')
entry(r,'NUT, plain, No. 10–30 x .437″ x .125″ thick. (For generator field coil stud D29829;\n   generator brush arm mounting stud D30135.)',note='&',mfr='D26715',qty='2',price='.01 P')
entry(r,'NUT, plain, ¼″—28 x .437″ x .125″ thick. (For voltage regulator terminal stud\n   D30366; voltage regulator terminal stud D30380; generator brush arm mounting\n   stud.)',note='&',mfr='D29991',qty='4',price='.01 P')
entry(r,'NUT, platform ammunition special storage',note='%X',brit='M3191A',ord='573',qty='2',price='.45')
entry(r,'NUT, selector lever stop',note='%X',ord='B5307',qty='4',price='.05')
entry(r,'NUT, shaft. (For shaft M1474 (2); shaft M1402 (2).)',note='%X',ident='4',plate='28',brit='M1477',ord='62',qty='8',price='1.23')
entry(r,'NUT, side door hinge pin (plain, ¾″, thick ½″)',note='%X',ord='SH545A',qty='4',price='.04 P')
entry(r,'NUT, small planet pinion. (For shaft M783 (2); pin M274; shaft M302.)',note='&',ident='37',plate='22',brit='M314',ord='679',qty='9',price='.19')
entry(r,'NUT, special',note='&',ord='LQ430A',price='.04')
entry(r,'NUT, special, S. A. E., ¼″. (For stud LQ88A; bolt, LQ112A; bolt LQ114A; bolt\n   LQ164A; stud LQ196A; bolt LQ443A.)',note='%X',ident='—\n101',plate='33\n17\n19',mfr='101',ord='LQ89A',qty='80',price='.02');stacked(r,ident='—\n101',plate='33\n17\n19')
entry(r,'NUT, special, S. A. E., ¼″. (For bolt LQ40A.)',note='%X',mfr='200',ord='LQ41A',qty='14',price='.02')
entry(r,'NUT, special, S. A. E., 5/16″. (For bolt LQ50A; lever LQ62A; stud LQ302A; bolt\n   LQ262A; stud LQ301A; tappet LQ67A.)',note='%X',mfr='102',ord='LQ51A',qty='102',price='.02')
entry(r,'NUT, special, S. A. E., ⅜″. (For stud LQ302A; stud LQ270A; bolt LQ246A;\n   bolt LQ245A; stud LQ233A; stud LQ197A; stud LQ269A; stud LQ271A.)',note='%X',mfr='103',ord='LQ198A',qty='50',price='.06')
entry(r,'NUT, special, S. A. E., ⅜″. (For stud LQ247A.)',note='%X',mfr='B266',ord='LQ248A',qty='72',price='.06')
entry(r,'NUT, special, S. A. E., ⅜″. (For Stud LQ270A; stud LQ269A.)',note='%X',ord='LQ272A',qty='7',price='.06')
entry(r,'NUT, special, S. A. E., ⅜″ bronze. (For stud LQ303A.)',note='%X',ident='167',plate='15',mfr='B167',ord='LQ305A',qty='24',price='.05')
entry(r,'NUT, special (castle, S. A. E., ⅝″). (For spindle M1131; spindle M1132.)',note='%X',ord='SH196B',qty='2',price='.03')
entry(r,'NUT, special (crown, U. S. Std., ⅞″, ½″ thick). (For bolt M767; bolt M776.)',note='%X',qty='3',price='.07')
entry(r,'NUT, special jam (S. A. E., ¼″). (For rod LQ315A.)',note='%X',mfr='8340',ord='LQ319A',qty='1',price='.03')
entry(r,'NUT, sponson hinge pin',note='%X',brit='M2831',ord='478',qty='4',price='.22')
entry(r,'NUT, sponson roller bracket (plain, U. S. Std., ¾″, ⅝″ thick)',note='%X',ord='SH470D',qty='2',price='.04')

r=start(130)
entry(r,'NUT, starting and lighting battery sealing (lead, single thread)',note='&',mfr='W–S1029',qty='12',price='$0.08 P')
entry(r,'NUT, stove bolt, 3/16″. (For stove bolt, flat head, 3/16″ x 1″; stove bolt, round head,\n   3/16″ x ⅝″.)',note='%(sh)R',qty='4',price='.01 P')
entry(r,'''NUT, stove bolt, ¼″. (For stove bolt, round head, ¼″ x 7/16″; stove bolt, round
   head, ¼″ x ½″; stove bolt, round head, ¼″ x ⅝″; stove bolt, round head, ¼″ x
   ¾″; stove bolt, round head, ¼″ x ⅞″; stove bolt, round head, ¼″ x ¾″ (2);
   stove bolt, round head, ¼″ x 1″; stove bolt, round head, ¼″ x 1¼″; stove bolt,
   round head, ¼″ x 2″.)''',note='%(sh)R',qty='92',price='.01 P')
entry(r,'NUT, switch and voltage regulator stud',note='%X',mfr='D30360',qty='2',price='.06 P')
entry(r,'NUT, towing shackle pin',note='%X',brit='M3921',ord='647',qty='8',price='.25')
entry(r,'NUT, transmission bevel pinion shaft',note='&',brit='MX33',ord='705',qty='1',price='.26')
entry(r,'NUT, transmission brake adjusting',note='%X',brit='M332',ord='687',qty='4',price='1.58');stacked(r,ident='7\n—',plate='31\n32')
entry(r,'NUT, transmission high speed brake adjusting',note='%X',ident='5',plate='30',brit='M357',ord='698',qty='2',price='1.05')
entry(r,'NUT, transmission mechanical lubricator delivery tube',note='%X',ord='SH102E',qty='6',price='.24')
entry(r,'NUT, transmission mechanical lubricator stuffing box gland',note='&',ord='SH101D',qty='1',price='.07')
entry(r,'NUT, tube union, ¼″. (For tube LQ461A.)',note='%X',mfr='L8459',ord='LQ462A',qty='4',price='.03')
entry(r,'NUT, turret roof door fastener pin',note='%X',ord='SH412A',qty='4')
entry(r,'NUT, U. S. Std., round, 3/16″. (For bolt, U. S. Std., countersunk head, 3/16″ x 9/16″.)',note='%(sh)R',qty='6',price='.01 P')
entry(r,'NUT, U. S. Std., round, ¼″. (For bolt, U. S. Std., countersunk head, ¼″ x ⅞″.)',note='%(sh)R',qty='12',price='.01 P')
entry(r,'NUT, U. S. Std., square, ¼″. (For bolt, carriage, ¼″ x 1 9/16″.)',note='%(sh)R',qty='86',price='.01 P')
entry(r,'NUT, U. S. Std., square, ⅜″. (For bolt, carriage, ⅜″ x 1½″; bolt, U. S. Std.,\n   square head, ⅜″ x 1¼″.)',note='%(sh)R',qty='16',price='.01 P')
entry(r,'''NUT, U. S. Std., square, ⅝″. (For bolt, U. S. Std., square head, ⅝″ x 1½″;
   bolt, U. S. Std., square head, ⅝″ x 1¾″; bolt, U. S. Std., square head, ⅝″ x 2 1/16″;
   bolt, U. S. Std., square head, ⅝″ x 2¼″; bolt, U. S. Std., square head, ⅝″ x
   2⅜″.)''',note='%(sh)R',qty='25',price='.01 P')
entry(r,'NUT, ventilating fan coupling (S. A. E., ½″, 3/16″ thick)',note='%X',ord='SH958E',qty='2',price='.04')
entry(r,'NUT, ventilating fan sprocket (S. A. E., ½″, 3/16″ thick)',note='%X',ord='SH958F',qty='2',price='.04')
entry(r,'NUT, water pump shaft',note='&',ident='8214',plate='17',mfr='8214',ord='LQ147A',qty='1',price='.14')

r=start(131)
entry(r,'OILER, generator end cover',note='%X',mfr='D13838',qty='1',price='.06 P')
assembly(r,'OUTLET, intake header water, double, assembly','4.47',ident='8',plate='14')
pieces(r,'''two (LQ422A) carburetor to intake header BOLT, assembly,
one LQ423A  carburetor to intake header stud nut LOCK,''')
component(r,'one LQ413A  intake header water OUTLET, double (1)',mfr='C12428',price='3.50')
pieces(r,'''one —           GASKET, copper asbestos, ⅝″,
one LQ145A PLUG, hexagon head, ⅝″).''')
entry(r,'OUTLET, intake header water, single',note='%X',ident='4',plate='14',mfr='C12427',ord='LQ415A',qty='1',price='2.84')
entry(r,'PACKER, transmission frame, fiber (additional)',note='%X',brit='M387',ord='669',qty='4',price='.15')
entry(r,'PACKER, transmission frame, fiber (main)',note='%X',brit='M386',ord='669',qty='6',price='.15')
entry(r,'PACKING, asbestos-graphite, 3/16″, spool (2 pieces 11 9/16″ long required for water\n   pump packing)',note='(mh)&',qty='—',price='.50 P')
entry(r,'PACKING, cam shaft driving shaft upper housing',note='&',mfr='8068',ord='LQ90A',qty='2',price='.10');stacked(r,ident='11\n8068',plate='14\n13')
for brit,ord_,item,qty,price in [
 ('M188','70','engine double point suspension','2','.18'),('M187','70','engine single point suspension','1','.12'),
 ('M1753D','653','gasoline tank, No. 1','2','.40'),('M1753E','653','gasoline tank, No. 2','2','.35'),('M1753F','653','gasoline tank, No. 3','2','.30'),
 ('M1753G','654','gasoline tank, floor','1','5.25'),('M1753H','655','gasoline tank, front end (assembled)','3','.75'),('M1753A','654','gasoline tank, front end','1','3.00'),
 ('M1753J','655','gasoline tank, rear end','3','.60'),('M1753M','655','gasoline tank, rear end','1','2.25'),('M1753L','655','gasoline tank casing, side, left','1','3.25'),('M1753K','655','gasoline tank casing, side, right','1','3.25')]:
 entry(r,'PACKING, '+item,note='&',brit=brit,ord=ord_,qty=qty,price=price)
entry(r,'PACKING, generator drive shaft end housing',note='&',mfr='D30374',qty='1',price='.02 P')
entry(r,'PACKING, hemispherical turret anti-splash half, top',note='&',ord='SH424A',qty='6',price='1.75')
entry(r,'PACKING (hemispherical turret support) bracket',note='&',brit='M3124',ord='428',qty='(gd) 24',price='.18')
entry(r,'PACKING, machine gunner’s seat hinge',note='&',brit='M2160',ord='270',qty='4',price='.18')
entry(r,'PACKING, main turret periscope clip',note='*',brit='M2438',ord='424',qty='(4)',price='.05')
entry(r,'PACKING, roof (behind front louvre)',note='*',brit='M1907',ord='534',qty='(1)',price='3.40')
entry(r,'PACKING, sponson seat hinge',note='&',brit='M2817',ord='473',qty='4',price='.24')
entry(r,'PACKING, trunnion',note='&',brit='M3125',ord='428',qty='(gd) 24',price='.72')
entry(r,'PACKING (under left side deflector channel)',note='&',brit='M2109',ord='380',qty='1',price='1.82')
entry(r,'PACKING (under rear deflector channels)',note='&',brit='M2112',ord='380',qty='2',price='.82')
entry(r,'PACKING, upper and lower spare barrel clip (sponson)',note='%X',brit='M2823',ord='473',qty='2',price='.18')
entry(r,'PACKING, 3/16″ x 6″. (For shaft SH101P (1).)',note='&',ord='101',qty='1',price='.05')

r=start(132)
entry(r,'PADLOCK, No. 840, with padlock clevis. (For outside tool chest (1).)',note='%(cp)X',qty='(1)',price='$2.10 P')
assembly(r,'PADLOCK, No. 840, with standard chain No. 1, assembly','2.54 P',note='(cp)*')
pieces(r,'''one —        CHAIN, standard, No. 1, assembly,
one JB5F  PADLOCK, No. 840, with padlock clevis.)''')
entry(r,'PAN, transmission mechanical lubricator oil',note='&',ord='SH105E',qty='6',price='.08')
entry(r,'PAWL, high and low speed control lever',note='&',brit='M741',ord='227',qty='2',price='.68')
entry(r,'PAWL, reverse lever',note='&',brit='M780',ord='219',qty='1',price='.44')
entry(r,'PEDAL, brake',note='&',brit='M764A',ord='98',qty='1',price='10.00');stacked(r,ident='—\n49',plate='6\n2')
entry(r,'PEG, peep hole cover plate operating',note='%X',brit='7X90',ord='633',qty='20',price='.05')
entry(r,'PIECE (exhaust pipe) filler',note='%X',ord='SH402M',qty='4',price='.28')
entry(r,'PIECE, extension, ½″. (For tube SH984B.)',note='%X',ord='SH985L',qty='1',price='.10')
entry(r,'PIECE, fan bevel gear box pulley distance',note='&',ident='2',plate='20',brit='M1129',ord='196',qty='1',price='.22')
entry(r,'PIECE, foot brake bridle distance',note='&',brit='M766',ord='217',qty='1',price='.74')
assembly(r,'PIECE, gasoline tank cover hinge, left, assembly','5.11',note='&')
component(r,'two SH537B gasoline tank cover HINGE, female,')
component(r,'*one SH536B gasoline tank cover hinge PIECE (1)',price='3.72')
component(r,'four —          RIVET, button head, ⅜″ x 1⅜″.)')
assembly(r,'PIECE, gasoline tank cover hinge, right, assembly','5.11',note='&')
component(r,'two SH537B gasoline tank cover HINGE, female,')
component(r,'*one SH536A gasoline tank cover hinge PIECE (1)',price='3.72')
component(r,'four —          RIVET, button head, ⅜″ x 1⅜″.)')
assembly(r,'PIECE, gasoline tank packing, top (front), assembly','1.25',note='&')
component(r,'*one M1753C gasoline tank packing PIECE, top (1)',ord='653',price='.80')
component(r,'one —           STRIP, felt, 4½″ x 38″ x ¼″.)')
entry(r,'PIECE, gasoline tank packing, top (rear), assembly',note='&',qty='(1)',price='.95')

r=start(133);composed(r)
component(r,'*one M1753B gasoline tank packing PIECE, top (1)',ord='653',price='.50')
component(r,'one —           STRIP, felt, 4½″ x 38″ x ¼″.)')
entry(r,'PIECE, generator frame pole',note='&',mfr='D29804',qty='4',price='.01 P')
entry(r,'PIECE (governor) control bracket filler',note='&',ident='—',plate='12',ord='SH535A',qty='1',price='1.62')
assembly(r,'PIECE, inlet louvre frame back end, assembly','18.08',note='&')
component(r,'*one M985 inlet louvre frame back end PIECE (1)',ord='500',price='17.60')
component(r,'*two M999 louvre frame plate securing PIECE (8)',ord='501',price='.22')
component(r,'four —       RIVET, button head, ½″ x 1¼″.)')
assembly(r,'PIECE, inlet louvre frame front end, assembly','3.40',note='&')
component(r,'*one M984 inlet louvre frame front end PIECE (1)',ord='500',price='2.92')
component(r,'*two M999 louvre frame plate securing PIECE (8)',ord='501',price='.22')
component(r,'four —       RIVET, button head, ½″ x 1¼″.)')
entry(r,'PIECE, louvre distance. (For outlet louvre (54); inlet louvre (68).)',note='%X',brit='M997',ord='501',qty='122',price='.12')
entry(r,'PIECE, louvre end packing. (For outlet louvre (2); inlet louvre (2).)',note='%X',brit='M998',ord='501',qty='4',price='.20')
entry(r,'PIECE, main turret side plate junction',note='*',brit='M2354',ord='407',qty='(2)',price='18.39')
assembly(r,'PIECE, outlet louvre frame back end, assembly','16.22',note='&')
component(r,'*two M999 louvre frame plate securing PIECE (8)',ord='501',price='.22')
component(r,'*one M991 outlet louvre frame PLATE, back end (1)',ord='503',price='14.78')
pieces(r,'''one M988 outlet louvre retaining PIECE,
eight —     RIVET, button head, ⅜″ x ⅞″,
four —      RIVET, button head, ½″ x 1¼″.)''')
assembly(r,'PIECE, outlet louvre frame front end, assembly','3.40',note='&')
component(r,'*two M999 louvre frame plate securing PIECE (8)',ord='501',price='.22')
component(r,'*one M992 outlet louvre frame front end PIECE (1)',ord='503',price='1.96')
pieces(r,'''one M988 outlet louvre retaining PIECE,
eight —     RIVET, button head, ⅜″ x ⅞″,
four —      RIVET, button head, ½″ x 1¼″.)''')
entry(r,'PIECE, outlet louvre retaining',note='&',brit='M988',ord='503',qty='2',price='.88')
for brit,ord_,item,qty,price in [('M1906B','533','left (in way of front mud chute)','(1)','1.80'),('M1906A','533','right (in way of front mud chute)','(1)','1.80'),('M2086','315','(between floor beam and floor plates No. 3)','(1)','3.86'),('M2076','343','(plate under driver’s turret)','(2)','.45')]:
 entry(r,'PIECE, packing, '+item if item[0]!='(' else 'PIECE, packing '+item,note='*',brit=brit,ord=ord_,qty=qty,price=price)
entry(r,'PIECE, radiator cooling fan distance',note='&',ord='SH279E',qty='1',price='.09')
entry(r,'PIECE, reverse quadrant distance',note='&',ident='—',plate='6',brit='M781',ord='217',qty='2',price='.22')

r=start(134)
entry(r,'PIECE, roof plate packing (behind rear louvre)',note='*',brit='M1910',ord='534',qty='(1)',price='$1.76')
entry(r,'PIECE, sponson stiffener packing',note='*',brit='M2036',ord='330',qty='(2)',price='14.76')
entry(r,'PIECE, swing link distance',note='&',brit='M775',ord='217',qty='4',price='.22')
entry(r,'PIECE, transmission bevel pinion shaft bearing distance',note='&',brit='M249',ord='705',qty='2',price='.35');stacked(r,ident='55\n8',plate='22\n23')
entry(r,'PIN, ball mount ball locking',note='%(c)X',brit='B34G',qty='5',price='.38')
entry(r,'PIN, brass, 1/16″ x ⅛″. (For cover SH105A (6).)',note='&(sh)R',qty='6',price='.01 P')
entry(r,'PIN, brass, .09″ x .210″. (For voltage regulator, assembly D5718.)',note='&',mfr='D30515',qty='1',price='.01 P')
entry(r,'PIN, brazing (see nail 2d finishing)',ord='LQ120A',qty='—',price='.01 P')
entry(r,'PIN, brazing (see nail 8d finishing)',ord='LQ83A',qty='—',price='.01 P')
entry(r,'PIN, cam shaft rocker roller sleeve. (For lever LQ62A (1); Lever LQ60A (1).)',note='&',ord='LQ65C',qty='24',price='.08')
entry(r,'PIN, carburetor air intake dowel',note='%X',mfr='13358',ord='LQ513A',qty='4',price='.01')
entry(r,'PIN, carburetor bail hook (screw for scoup spring)',note='&',mfr='13411',ord='LQ552A',qty='4',price='.27')
entry(r,'PIN, carburetor bail hook pin taper',note='&',mfr='13412',ord='LQ553A',qty='4',price='.01')
assembly(r,'PIN, carburetor float cover clamp bolt, assembly','.06',note='&',qty='(4)')
component(r,'*one LQ533A carburetor float cover clamp bolt PIN (4).',mfr='13384',price='.05')
component(r,'one —           PIN, split, 1/16″ x ½″.)')
assembly(r,'PIN, clutch throwout bell crank, assembly','.56')
component(r,'*one M4165 clutch throwout bell crank PIN (1)',ord='955',price='.51')
pieces(r,'''one —         NUT, crown, U. S. Std., ⅝″,
one —         PIN, split, 5/32″ x 1″.)''')
assembly(r,'PIN, clutch throwout lever, assembly','.82',qty='(2)')
component(r,'*one SH943A clutch throwout lever PIN (2)',price='.78')
pieces(r,'''one —           NUT, plain, U. S. Std., hexagon, ⅝″,
one —           WASHER, lock, ⅝″.)''')
assembly(r,'PIN, clutch throwout stop band, assembly','.26')

r=start(135)
component(r,'*one M4157 clutch throwout stop band PIN (1)',ord='955',price='.25')
component(r,'one —         PIN, split, ⅛″ x ⅞″.)')
assembly(r,'PIN, clutch throwout stop rod, assembly','.42')
component(r,'*one M4152 clutch throwout stop rod PIN (1)',ord='955',price='.41')
component(r,'one —         PIN, split, ⅛″ x 1″.)')
assembly(r,'PIN, control lever lock, assembly','.19',qty='(2)')
component(r,'*one M750 control lever lock PIN (2)',ord='227',price='.18')
component(r,'one —       PIN, split, 3/32″ x ⅝″.)')
assembly(r,'PIN, control lever trigger, assembly','.21',qty='(6)')
component(r,'*one M740 control lever trigger PIN (6)',ord='227',price='.20')
component(r,'one —       PIN, split, 1/16″ x ⅜″.\n                  For high and low speed lever, left, assembly (2); high and\n                     low speed lever, right, assembly (2); reverse operating\n                     lever, assembly (2).)')
entry(r,'PIN, cooling system drain plug swivel',note='%X',ord='SH976P',qty='2',price='.09')
entry(r,'PIN, crank case oil filler cover hinge',note='&',mfr='8159',ord='LQ218A',qty='2',price='.01')
entry(r,'PIN, distributor cam',note='&',mfr='D30059',qty='2',price='.01 P')
entry(r,'PIN, distributor head clamp',note='&',mfr='D29802',qty='8',price='.03 P')
entry(r,'PIN, door hinge. (For hinges M1789 and M1790.)',note='&',brit='M1791',ord='537',qty='12',price='.15')
entry(r,'PIN, door hinge. (For hinges GB3L and GB3J.)',note='(c)&',ord='GB3K',qty='3',price='.03 P')
assembly(r,'PIN, drive sprocket collar bushing, assembly','1.26',qty='(50)')
component(r,'*one SH40AE drive sprocket collar bushing PIN (50)',price='1.25')
component(r,'one —           PIN, split, ⅜″ x 1¾″.)')
assembly(r,'PIN, driver’s turret flap hinge, assembly','.93',note='&')
component(r,'*one M2405 driver’s turret flap hinge PIN (1)',ord='417',price='.89')
component(r,'two —         NUT, plain, U. S. Std., hexagon, ½″.)')
assembly(r,'PIN, driver’s turret flap locking lever, assembly','.30',note='&')
component(r,'*one M2430 driver’s turret flap locking lever PIN (1)',ord='412',price='.28')
pieces(r,'''one —         PIN, split, ⅛″ x 1½″,
one —         WASHER, plain, ⅝″.)''')
entry(r,'PIN, escutcheon, No. 13 x ⅜″ (brass, round head). (For spring LQ220A (2);\n   hinge LQ217A (3); lock LQ219A (2).)',note='&',mfr='261',ord='LQ221A',qty='14',price='.01')

r=start(136)
assembly(r,'PIN, fork end, length 1 9/16″, assembly','$0.10',qty='44')
component(r,'*one M568C fork end PIN, length 1 9/16″ (44)',ord='171',price='.09')
component(r,'one —         PIN, split, ⅛″ x 1″.\n                     For end M569C (1); end M570 (1).)')
assembly(r,'PIN, fork end, length 1⅝″, assembly','.11',qty='(15)')
component(r,'*one M568A fork end PIN, length 1⅝″ (15)',ord='171',price='.10')
component(r,'one —         PIN, split, ⅛″ x 1″.\n                     For end M569A (1); end M569B (1); rod M565 (1); link\n                        M771 (1).)')
assembly(r,'PIN, fork end, length 1⅞″, assembly','.23',qty='(3)')
component(r,'*one SH953F fork end PIN, length 1⅞″ (3)',price='.22')
component(r,'one —           PIN, split, ⅛″ x ⅞″.\n                       For end SH953E (1).)')
assembly(r,'PIN, fork end, length 2¼″, assembly','.13',qty='(2)')
component(r,'*one M568B fork end PIN, length 2¼″ (2)',ord='171',price='.12')
component(r,'one —         PIN, split, ⅛″ x 1″.\n                     For shaft M783 (2).)')
assembly(r,'PIN, gasoline tank cover hinge, assembly','.93',qty='(2)')
component(r,'*one SH537C gasoline tank cover hinge PIN (2)',price='.92')
component(r,'one —           PIN, split, ⅛″ x 1″.)')
entry(r,'PIN, generator housing (.0945″ x .218″)',note='&',mfr='D29225',qty='2',price='.01 P')
assembly(r,'PIN, gun hanger bracket, assembly','.96',qty='(5)')
component(r,'*one SH395H gun hanger bracket PIN (5)',price='.60')
component(r,'*one —           standard CHAIN, No. 8, assembly.)',price='.36')

r=start(137)
assembly(r,'PIN, high speed brake anchor, assembly','.43',ident='14',plate='30',qty='(2)')
component(r,'*one M363 high speed brake anchor PIN (2)',ord='698',price='.42')
component(r,'one —       PIN, split, 3/16″ x 2″.)')
entry(r,'PIN, high speed free end brake band',note='%X',brit='M356',ord='698',qty='4',price='.38')
entry(r,'PIN, high and low speed control lever spring',note='&',ident='—',plate='6',brit='M748',ord='227',qty='2',price='.25')
assembly(r,'PIN, joint, assembly','.29',qty='(3)')
component(r,'*one M790 joint PIN (3)',ord='220',price='.28')
component(r,'one —       PIN, split, 3/16″ x 1¼″.)')
assembly(r,'PIN, large planet pinion, assembly','3.38',note='&',ident='26',plate='22',qty='(6)')
component(r,'one M313 large planet pinion NUT,')
component(r,'*one M284 large planet pinion PIN (6)',ord='679',price='3.12')
pieces(r,'''one —       PIN, split, 3/16″ x 2½″,
one —       PLUG, expansion, ½″.)''')
entry(r,'PIN, low speed brake anchor',note='%X',ident='10',plate='32',brit='M348',ord='681',qty='2',price='.78')
assembly(r,'PIN, low speed brake suspension link, assembly','.49',qty='(2)')
component(r,'*one M761 low speed brake suspension link PIN (2)',ord='220',price='.48')
component(r,'one —       PIN, split, 3/16″ x 1¼″.)')
assembly(r,'PIN, low speed and track brake suspension, assembly','2.52',ident='12',plate='32',qty='(4)')
component(r,'*one M339 low speed and track brake suspension PIN (4)',ord='687',price='2.50')
component(r,'two —       PIN, split, ¼″ x 1½″.\n                  For low speed (2); track brake (2).)')
entry(r,'PIN, low speed free end brake band, assembly',note='%X',qty='(8)',price='.49');stacked(r,ident='2\n5',plate='31\n32');composed(r)
component(r,'*one M336 low speed free end brake band PIN (8)',ord='687',price='.48')
component(r,'one —       PIN, split, ¼″ x 1½″.)')
assembly(r,'PIN, machine gunner’s seat strut fulcrum, assembly','.19',qty='(2)')
component(r,'*one M2161 machine gunner’s seat strut fulcrum PIN (2)',ord='362',price='.18')
component(r,'one —         PIN, split, ⅛″ x ¾″.)')
entry(r,'PIN, oil pump driven, long',note='&',ident='—',plate='33',mfr='8383',ord='LQ436A',qty='1',price='.12')
entry(r,'PIN, oil pump driven, short',note='&',ident='—',plate='33',mfr='8179',ord='LQ437A',qty='1',price='.07')

r=start(138)
assembly(r,'PIN, periscope hole cover, length over all 1 15/16″, assembly','$0.51',qty='(3)')
component(r,'*one M2411 periscope hole cover PIN (3)',ord='438',price='.48')
pieces(r,'''one —         NUT, plain, U. S. Std., hexagon, ½″,
one —         WASHER, lock, ½″.~                     On outlook turret (2); roof door (1).)''')
assembly(r,'PIN, periscope hole cover, length over all 2 5/16″, assembly','.61')
component(r,'*one M2425 periscope hole cover PIN (1)',ord='438',price='.58')
pieces(r,'''one —         NUT, plain, U. S. Std., hexagon, ½″,
one —         WASHER, lock, ½″.~                     On driver’s turret.)''')
entry(r,'PIN, piston',note='&',ord='LQ467A',qty='12',price='.93')
assembly(r,'PIN, radiator support swivel (rear), assembly','.29',note='&')
component(r,'*one M889 radiator support swivel PIN (1)',ord='178',price='.28')
component(r,'one —       PIN, split, 3/16″ x 1½″.)')
entry(r,'PIN, regulating tank relief valve guide',note='&',ord='SH962E',qty='1',price='.08')
assembly(r,'PIN, regulating tank valve bracket, assembly','.13',note='&')
component(r,'*one SH950G regulating tank valve bracket PIN (1)',ord='950',price='.12')
component(r,'one —           PIN, split, 1/16″ x ⅜″.)')
entry(r,'PIN, revolver hole cover operating handle',note='&',ord='SH642A',qty='9',price='.02')
assembly(r,'PIN, revolver hole cover swivel, assembly','2.57',note='&',qty='(9)')
pieces(r,'''one D42/21221 revolver hole cover handle SPRING,
one A42/21221 revolver hole cover operating HANDLE,
one SH642A   revolver hole cover operating handle PIN,''')
component(r,'*one M2627 revolver hole cover swivel PIN (9)',price='1.00')
component(r,'three SH642B   SPRING, Bellville, I. D. 13/16″, O. D. 1½″, 1″ thick,')

r=start(139)
component(r,'one —         NUT, plain, U. S. Std., hexagon, ½″.)')
entry(r,'PIN, revolver hole stop',note='&',mfr='F42/21221',ord='642',qty='18',price='.12')
assembly(r,'PIN, rod end, ¼″ x 51/64″, assembly','.14 P',note='%(mh)X',ident='196',plate='15',qty='(4)')
component(r,'*one A8035 rod end PIN, ¼″ x 51/64″ (2)',price='.13')
component(r,'one —       PIN, split, 1/16″ x ½″.\n                  For rod SH993K (1); rod SH993A (1); engine (2).)')
assembly(r,'PIN, rod end, 5/16″ x 31/32″, assembly','.15 P',note='%(mh)X',qty='(4)')
component(r,'*one A1810 rod end PIN, 5/16″ x 31/32″ (4)',ident='—',plate='12',price='.14')
component(r,'one —       PIN, split, 3/32″ x ½″.\n                  For 5/16″ adjustable yoke rod end, (1), 2 used in engine.)')
assembly(r,'PIN, rod end, ⅜″ x 1 3/32″, assembly','.15 P',note='%(mh)X',qty='(5)')
component(r,'*one A8036 rod end PIN, ⅜″ x 1 3/32″ (5)',ident='—',plate='12',price='.14')
component(r,'one —       PIN, split, 3/32″ x ¾″.\n                  For ⅜″ adjustable yoke rod end (1).)')
assembly(r,'PIN, rod end, ½″ x 1 27/64″, assembly','.15 P',note='%(mh)X',qty='(12)')
component(r,'*one A1547 rod end PIN, ½″ x 1 27/64″ (12)',ident='—',plate='12',price='.14')
component(r,'one —       PIN, split, ⅛ x ⅞″.\n                  For ½″ adjustable yoke rod end (1).)')
assembly(r,'PIN, roller sliding door, assembly','.43',note='&',qty='(4)')
component(r,'*one M2149 roller sliding door PIN (4)',ord='362',price='.40')
pieces(r,'''one —         NUT, plain, U. S. Std., hexagon, ⅜″,
one —         WASHER, lock ⅜″.)''')
entry(r,'PIN, semaphore handle, long',note='&',brit='X246',ord='802',qty='1',price='.58')
entry(r,'PIN, semaphore handle, short',note='&',brit='X271',ord='802',qty='1',price='.58')
assembly(r,'PIN, shell holder, assembly','.09',qty='(44)')
component(r,'*one M3025 shell holder PIN (44)',ord='550',price='.08')
component(r,'one —         PIN, split, 1/16″ x ⅜″.)')
assembly(r,'PIN, side door hinge, assembly','1.04',qty='(4)')
component(r,'*one M707 side door hinge PIN (4)',ord='545',price='1.00')
component(r,'one SH545A side door hinge pin NUT (plain, U. S. Std., hexagon, ¾″,\n                      ½″ thick).)')

r=start(140)
assembly(r,'PIN, small planet pinion, assembly','$1.96',note='&',ident='36',plate='22',qty='(6)')
component(r,'one M314 small planet pinion NUT,')
component(r,'*one M274 small planet pinion PIN (6)',ord='679',price='1.75')
pieces(r,'''one —       PIN, split, 3/16″ x 2″,
one —       PLUG, expansion, ½″.)''')
entry(r,'PIN, split, 1/16″ x ⅜″. (For pin M740; plunger X273; pin M3025; pin SH950G;\n   seat LQ546A.)',note='%(sh)R',qty='54',price='.01 P')
entry(r,'''PIN, split, 1/16″ x ½″. (For stud LQ88A; stud LQ196A; bolt LQ164A; pin
   LQ321A; pin LQ533A; valve LQ567A; shaft LQ520A; bolt LQ585A; bolt
   LQ40A; bolt LQ114A; bolt LQ125A; bolt LQ443A; bolt LQ112A; pin A8035;
   pin LQ229A (2).)''',note='%(sh)R',qty='144',price='.01 P')
entry(r,'PIN, split, 1/16″ x ⅝″. (For stud LQ302A; bolt LQ50A; bolt LQ262A; tappet\n   LQ67A; stud LQ301A.)',note='%(sh)R',qty='90',price='.01 P')
entry(r,'Pin, split, 3/32″ x ⅜″. (For plunger SH101K.)',note='%(sh)R',qty='6',price='.01 P')
entry(r,'PIN, split, 3/32″ x ½″. (For pin A1810.)',note='%(sh)R',qty='4',price='.01 P')
entry(r,'PIN, split, 3/32″ x ⅝″. (For stud LQ304A; stud LQ197A; stud LQ269A; stud\n   LQ270A; stud LQ271A; bolt LQ246A; bolt LQ245A; pin M750; stud LQ303A.)',note='%(sh)R',qty='70',price='.01 P')
entry(r,'PIN, split, 3/32″ x ⅝″, bronze. (For shaft LQ138A.)',note='%(sh)R',qty='1',price='.01 P')
entry(r,'PIN, split, 3/32″ x ¾″. (For bolt LQ133A; collar LQ119A; pin A8036.)',note='%(sh)R',qty='18',price='.01 P')
entry(r,'PIN, split, 3/32″ x ⅞″. (For bolt MX26: bolt LQ189A (2); bolt LQ190A (2).)',note='%(sh)R',qty='64',price='.01 P')
entry(r,'PIN, split, 3/32″ x 1″. (For stud MX14; stud MX25; stud MX98; bolt MX8; bolt\n   MX11; stud MX12.)',note='%(sh)R',qty='28',price='.01 P')
entry(r,'PIN, split, 3/32″ x 1¼″. (For spindle SH282D (2).)',note='%(sh)R',qty='2',price='.01 P')
entry(r,'PIN, split, ⅛ x ½″. (For shaft SH65C.)',note='%(sh)R',qty='1',price='.01 P')
entry(r,'PIN, split, ⅛″ x ⅝″. (For shaft X266.)',note='%(sh)R',qty='1',price='.01 P')
entry(r,'PIN, split, ⅛″ x ¾″. (For spindle M1131; pin M2161.)',note='%(sh)R',qty='3',price='.01 P')
entry(r,'PIN, split, ⅛″ x ⅞″. (For pin M4157; pin SH953F; pin A1547.)',note='%(sh)R',qty='6',price='.01 P')
entry(r,'PIN, split, ⅛″ x 1″. (For separator SH234G (2); axle SH234K (2); axle SH234L;\n   sprocket X257; pin M4152; bracket M641; pin M568A; pin M568B; pin M568C;',note='%(sh)R')

r=start(141)
entry(r,'   pin SH537C; shaft LQ94A.)',qty='113',price='.01 P')
for size,refs,qty in [
 ('⅛″ x 1¼″','spindle M1132; stud A7681; bolt M317','9'),
 ('⅛″ x 1⅜″','stud MX10; stud MX36; stud MX9; stud MX5','20'),
 ('⅛″ x 1½″','spring SH65D; bolt MX1; pin M2430, shaft, SH66C','22'),
 ('⅛″ x 1¾″','bolt M318','6'),
 ('5/32″ x 1″','pin, type A, .610 x 2 3/16″ (2); pin M4165','3'),
 ('5/32″ x 1½″','spindle SH144B','1'),
 ('3/16″ x 1″','bolt M776','2'),
 ('3/16″ x 1⅛″','bracket SH956B','2'),
 ('3/16″ x 1¼″','pin M790; pin M761','5'),
 ('3/16″ x 1½″','shaft M782 (2); bolt M767; bolt M776; pin M889','7'),
 ('3/16″ x 2″','shaft M783 (2); pin M274; shaft M302; pin M363; shaft\n   M638 (2)','13'),
 ('3/16″ x 2½″','shaft M247; pin M284','7'),
 ('¼″ x 1½″','pin M336; pin M339 (2); pin M1262','328'),
 ('¼″ x 1¾″','bracket M641','2'),
 ('¼″ x 2″','bracket M4131','4'),
 ('¼″ x 3″','nut SH136A','1'),
 ('5/16″ x 1¾″','pin M1543','36'),
 ('5/16″ x 3″','pin M3920 (2)','8'),
 ('⅜″ x 1¾″','pin SH40AE','50')]:
 entry(r,'PIN, split, '+size+'. (For '+refs+'.)',note='%(sh)R',qty=qty,price='.01 P')
entry(r,'''PIN, split, brass, 1/16″ x ⅜″. (For ignition switch terminal nut D29864; generator
   brush arm mounting stud D30070; distributor condenser and breaker plate stud
   D29595; distributor condenser and breaker plate stud D29784; distributor igni-
   tion coil and distributor head D29635; distributor advance lever attaching stud
   D29896; distributor cup stud D30536; generator brush arm mounting stud
   D29811; generator brush arm mounting stud D30135; distributor cup, assembly
   D14180 (3); generator top end housing D13827 (4); ignition switch nut D29864;
   generator field coil stud D29829; generator field coil stud D30383.)''',note='&(sh)R',qty='46',price='.01 P')
entry(r,'''PIN, split, brass, 1/16″ x ⅝″. (For ignition switch screw D29864; ignition switch
   screw D30362; voltage regulator terminal stud D30366; voltage regulator terminal
   stud D30380.)''',note='&(sh)R',qty='7',price='.01 P')
entry(r,'PIN, split, brass, 7/64″ x ¾″. (For generator.)',note='&(sh)R',qty='1',price='.01 P')
assembly(r,'PIN, sponson hinge, assembly','6.35',note='X',qty='(4)')
component(r,'*one M2829 sponson hinge PIN (4)',ord='478',price='5.93')
pieces(r,'''one M2831 sponson hinge pin NUT,
one M2830 sponson hinge pin WASHER.)''')

r=start(142)
assembly(r,'PIN, sponson periscope hole cover, assembly','$0.21',note='&',qty='(2)')
component(r,'*one M2770 sponson periscope hole cover PIN (2)',ord='490',price='.18')
pieces(r,'''one —         NUT, plain, U. S. Std., hexagon, ½″,
one —         WASHER, plain, ½″.)''')
entry(r,'PIN, sponson seat hinge',note='&',brit='M2816',ord='472',qty='4',price='.06')
for size,refs,qty,price in [
 ('⅛″ x ¼″','housing SH957A (2)','2','.01'),
 ('⅛″ x ⅜″','shank LQ422A and head LQ421A (1)','2','.01 P'),
 ('⅛″ x 5/16″','end SH922A (2)','12','.01 P'),
 ('⅛″ x 15/16″','hub SH964B','2','.01 P'),
 ('⅛″ x 1 5/16″','cam shaft LQ73A','2','.01 P'),
 ('3/16″ x 1″','stud SH964E','2','.01 P'),
 ('3/16″ x 2½″','cover M295','4','.01 P'),
 ('¼″ x ⅝″','bracket SH964A','2','.01 P'),
 ('¼″ x 1″','hook M2169A','1','.01 P'),
 ('¼″ x 3″','hasp GB5G','2','.01 P')]:
 entry(r,'PIN, steel, '+size+'. (For '+refs+'.)',note='&(sh)R',qty=qty,price=price)
entry(r,'PIN, tachometer drive shaft gear attaching',note='&',mfr='D29846',qty='1',price='.01 P')
entry(r,'PIN, taper, type A, No. 0 x ⅝″. (For worm SH103D.)',note='&(sh)R',qty='1',price='.01 P')
entry(r,'PIN, taper, type A, No. 2 x 1¼″. (For shaft SH965B (2).)',note='&(sh)R',qty='4',price='.02 P')
entry(r,'PIN, taper, type A, No. 2 x 1½″. (For shaft SH965B; shaft SH966D (2); shaft\n   LQ386A.)',note='&(sh)R',qty='5',price='.02 P')
entry(r,'PIN, taper, type A, No. 6 x 3″. (For lever SH953B.)',note='(sh)R',qty='2',price='.04 P')
assembly(r,'PIN, towing shackle, assembly','1.52',qty='(4)')
component(r,'*one M3920 towing shackle PIN (4)',ord='647',price='1.00')
pieces(r,'''two M3921 towing shackle pin NUT,
two —         PIN, split, 5/16″ x 3″.)''')
entry(r,'PIN, track brake anchor',note='%X',brit='M353',ord='692',qty='2',price='.58')
assembly(r,'PIN, track link, assembly','1.60',qty='(312)')

r=start(143)
component(r,'*one M1262 track link PIN (312)',ord='50',price='1.59')
component(r,'one —         PIN, split, ¼″ x 1½″.)')
assembly(r,'PIN, track roller, assembly','22.53',ident='13',plate='29',qty='(58)')
component(r,'*one M1337 track roller PIN (58)',ord='57',price='22.50')
component(r,'one Q52C   PLUG, pipe, square head, ⅜″.)')
assembly(r,'PIN, track roller pinion, assembly','3.15',note='&',qty='(36)')
component(r,'*one M1543 track roller pinion PIN (36)',ord='53',price='3.08')
pieces(r,'''one —         PIN, split, 5/16″ x 1¾″,
one —         PLUG, pipe, square head, ⅛″, brass.)''')
entry(r,'PIN, transmission brake adjusting swivel',note='%X',ident='6',brit='M331',ord='687',qty='4',price='1.50');stacked(r,plate='31\n32')
entry(r,'PIN, transmission mechanical lubricator eccentric',note='&',ord='SH101M',qty='6',price='.01')
entry(r,'PIN, transmission mechanical lubricator snap',note='&',ord='SH105G',qty='6',price='.06')
entry(r,'PIN, trigger spring. (For lever M738A; lever M738B; lever M177.)',note='&',ident='—',plate='6',brit='M745',ord='227',qty='3',price='.20')
assembly(r,'PIN, turret roof door fastener, assembly','.65',note='X',qty='(2)')
component(r,'*one M2366   turret roof door fastener PIN (2)',ord='412',price='.55')
component(r,'two SH412A turret roof door fastener pin NUT.)')
entry(r,'PIN, type A, .610″ x 2 3/16″, with two split pins. (For end M3189.)',note='%(sh)R',qty='2',price='.20')
entry(r,'PIN, voltage regulator armature retaining (German silver, .062″ x 1″)',note='&',mfr='D24082',qty='1',price='.02 P')
entry(r,'PIN, voltage regulator mounting coil nut (wire)',note='&',mfr='D30528',qty='1',price='.01')
entry(r,'PIN, voltage regulator terminal stud split',note='&',mfr='D22578',qty='3',price='.01')
entry(r,'PIN, wire, .031″ x .625″. (For distributor contact arm spring.)',note='&',mfr='D30816',qty='4',price='.01 P')
assembly(r,'PIN, 7½″ ball mount ball locking (hemispherical turret), assembly','.64',qty='(3)')
pieces(r,'''one B34G     ball mount ball locking PIN,
one SH1712K ball mount ball locking pin HOOK, 17/32″ hole,
one B34F     CHAIN, steel, length 4″,
two B34D    steel chain RING.)''')
assembly(r,'PIN, 7½″ ball mount ball locking (main turret), assembly','.64',qty='(2)')
pieces(r,'''one B34G     ball mount ball locking PIN,
one SH1712B ball mount ball locking pin HOOK, 11/16″ hole,
one B34F     CHAIN, steel, length 4″,
two B34D    steel chain RING.)''')

r=start(144)
entry(r,'PIN, 9″ ball mount trunnion',note='(c)%X',ord='B33A',qty='5',price='$3.74')
entry(r,'PINION, chain sprocket and roller, assembly',note='&',qty='(2)',price='277.60');stacked(r,ident='1\n17',plate='25\n2');composed(r)
pieces(r,'''one M1541 chain sprocket and roller PINION,
eighteen —       track roller pinion PIN, assembly,
eighteen M1542 track roller pinion ROLLER.)''')
entry(r,'PINION, chain sprocket and roller',note='&',brit='M1541',ord='55',qty='2',price='205.60')
entry(r,'PINION, distance recorder drive',note='(gy)&',mfr='S114',ord='586',qty='1',price='1.25')
entry(r,'PINION, planet, large',note='&',ident='25',plate='22',brit='M280',ord='679A',qty='6',price='32.00')
entry(r,'PINION, planet, small',note='&',ident='35',plate='22',brit='M270',ord='679A',qty='6',price='18.00')
entry(r,'PINION, transmission chain sprocket',note='&',ident='6',plate='22',brit='M291',ord='706',qty='2',price='95.00')
entry(r,'PINION, transmission sun, large',note='X',ident='20',plate='22',brit='M287',ord='704',qty='2',price='24.00')
assembly(r,'PINION, transmission sun, small, assembly','37.40',note='X',ident='44',plate='22',qty='(2)')
component(r,'one M268 sun pinion BUSHING, small,')
component(r,'*one M267 transmission sun PINION, small (2).)',ord='704',price='35.00')
entry(r,'PIPE, engine oil tank delivery',note='X',brit='M3301',ord='165',qty='1',price='.38')
entry(r,'PIPE, engine outlet (developed length 26¼″)',note='X',ident='—',plate='24',brit='M1228',ord='169',qty='1',price='3.00')
entry(r,'PIPE, exhaust (flexible, O. D. 3 11/32″, length 14½″)',note='X',ident='23',plate='2',ord='SH403B',qty='2',price='4.07 P')
entry(r,'PIPE, exhaust, long',note='X',ident='3',plate='2',ord='SH140H',qty='2',price='3.50 P')
entry(r,'PIPE, exhaust, short',note='X',ident='2',plate='2',ord='SH140L',qty='2',price='1.75 P')
entry(r,'PIPE, gasoline tank suction',note='X',brit='M1765',ord='236',qty='3',price='.38 P')
entry(r,'PIPE, radiator cooling fan inside bearing oil',note='X',qty='1',price='.12 P')
assembly(r,'PIPE, radiator drain, long, assembly','1.54 P',note='X',qty='(2)')
pieces(r,'''one —           BUSHING, reducing pipe, M. I., ½″ x ¼″,
one —           COCK, drain, tee handle, ½″,
one Q51BE   ELBOW, street, M. I., 90°, ¼″,''')
component(r,'*one SH976E PIPE, W. I., ¼″ x 31″ (2).)',ident='—',plate='24',price='.25')
