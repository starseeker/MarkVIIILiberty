"""Photograph-led transcription of printed pages 265–276.
Original page breaks, blank fields and apparent source errors retained.
"""
from .parts_tables import row
from .opening_tables import entry,component,composed
from .tables_045_064 import assembly
from .tables_065_084 import pieces,stacked
from .tables_225_244 import append_rows,grouped
TABLES={}
def start(page):
 TABLES[page]=[]
 return TABLES[page]
def add(page,content):
 r=start(page);append_rows(r,content);return r

r=start(265)
assembly(r,'UNILET, type T, 1″ x 1″ x 1″, assembly','.56 P',note='(ee)&')
component(r,'*one — UNILET, type T, 1″ x 1″ x 1″ (1)',price='.44')
pieces(r,''' one — unilet COVER, rectangular blank, 1″,
 two — SCREW, machine, round head, brass, No. 8—32 x 7/16″.)''')
append_rows(r,'''%(pf)X|||||B101965B|UNION, 29/64″—28 (brass). (For tube C8012 (1); tube C8013 (4); tube C8014A (2);~  tube C8014C (2); tube C8015 (1); tube C8016 (2); tube C8014B (2).)|16|.20 P
%(pf)X|||||B101965C|UNION, brass 7/16″—20—NF2A. (For tube, assembly B101992A).|2|.20 P
|||||SH102E|UNION, brass, 7/16″—22. (For tubes B101982A, B, C, D, and E (1).)|6|.20 P
%X|||L12367||LQ425A|UNION, carburetor to intake header|4|.05
%(pf)X|||||Q50RA|UNION, flared tube, ¼″, ⅛″ pipe thread, 7/16″ S. A. E. thread. (For oil pressure~  gage (1).)|1|.12 P
%(pf)X||||||UNION, M. I., brass seat, ¼″ (Dart or equal). (For combination valve to flexible~  tube connection (3).)|3|.18 P
%(pf)X||24||||UNION, M. I., brass seat ¾″ (Dart or equal). (For pipe M1229 (1).)|1|.30 P
%(pf)X||24||||UNION, M. I., brass seat, 1″ (Dart or equal). (For pipe M1229 (1).)|1|.36 P''')
assembly(r,'UNIT, distributor resistance, assembly','.20 P',note='&',mfr='D13747',qty='(2)')
pieces(r,'''*one D29656 distributor resistance unit SPOOL (2),
*one D29652 distributor resistance unit spool CLIP (2),
*one D29768 distributor resistance unit spool COIL (2),
*one D20653 distributor resistance unit spool SLEEVE (2),
 one D29654 WASHER, plain, .202″ x .296″ x .015″,
 one D29655 WASHER, plain, .202″ x .396″ x .02″.)''')
assembly(r,'UNIT, ignition switch resistance, left, assembly','.30 P',note='&',mfr='D13780')
pieces(r,'''*one D26135 ignition switch resistance unit clamping TUBE (2),
*one D29806 ignition switch resistance unit COIL (2),
*one D29736 ignition switch resistance unit CONNECTOR, left (1),
*one D29742 ignition switch resistance unit GUARD (2),
*one D26145 ignition switch resistance unit INSULATOR (2),
*one (D30362) ignition switch resistance unit SCREW, assembly (2),
*one D30812 ignition switch resistance unit WASHER (fiber) (2),
 two D20495 WASHER, lock, .195″ x .393″ x .046″,
 one D30813 WASHER, plain, .26″ x ¾″ x .031″.)''')
assembly(r,'UNIT, ignition switch resistance, right, assembly','.30 P',note='&',mfr='D13743')
pieces(r,'''*one D26135 ignition switch resistance unit clamping TUBE (2),
*one D29806 ignition switch resistance unit COIL (2),''')

r=start(266)
entry(r,'UNIT, ignition switch resistance, right assembly—Continued.',note='&',mfr='D13743');composed(r)
pieces(r,'''*one D29737 ignition switch resistance unit CONNECTOR, right (1),
*one D29742 ignition switch resistance unit GUARD (2),
*one D26145 ignition switch resistance unit INSULATOR (2),
*one (D30362) ignition switch resistance unit SCREW, assembly (2),
*one D30812 ignition switch resistance unit WASHER (fiber) (2),
 two D20495 WASHER, lock, .195″ x .393″ x .046″,
 one D30813 WASHER, plain, .26″ x ¾″ x .031″.)''')
assembly(r,'VALVE, carburetor altitude, assembly','$1.63',note='&',qty='(2)')
pieces(r,''' one LQ568A carburetor air valve PLUG,
 one LQ514A carburetor altitude air valve and yoke end NUT,
 one LQ516A carburetor altitude air valve WASHER,''')
component(r,'*one LQ567A carburetor altitude VALVE (2)',mfr='13361',price='1.49')
component(r,' one —       PIN, split, 1/16″ x ½″.)')
assembly(r,'VALVE, carburetor needle, assembly','.33',note='&',qty='(2)')
component(r,'*one LQ544A carburetor needle VALVE (2)',mfr='13398',price='.31')
component(r,'*one LQ545A carburetor needle valve COLLAR (2).)',mfr='13399',price='.02')
append_rows(r,'''%(pf)X|||||B101941A|VALVE, check, vertical, ¼″ pipe thread (bronze). (For tube SH982B (1).)|3|1.00 P
%(pf)X|||||B101946A|VALVE, horizontal check, brass, ¼″. (For combination valve to flexible tube~  connection (3); tube C8015 (1).)|4|1.00 P
&|||B8021||LQ292A|VALVE (inlet or exhaust)|24|3.10
&|—|33|8192||LQ448A|VALVE, oil pump pressure relief|1|.82
&|6|6|||SH950E|VALVE, regulating tank|1|.78 P''')
assembly(r,'VALVE, triple combination, assembly','11.72',ident='11',plate='8')
pieces(r,''' one SH951C triple combination tap BODY,
three —     triple combination tap PLUG, assembly,''')

r=start(267)
pieces(r,'''three SH951F triple combination valve plug WASHER,
three SH951G triple combination valve plug WASHER,
three SH951A triple combination valve tap plug thackray WASHER.)''')
append_rows(r,'''(mh)X|||||—|VELLUMOID, 1/16″ sheet. (For oil pressure gauge.)|—|
&|||D28929|||WASHER, ball bearing felt (.67″ x .895″ x .072″)|2|.01 P
&||||MX13|713|WASHER, bevel|24|.05
&|||||SH196C|WASHER, bevel gear. (For spindle M1132; spindle M1131.)|2|.05
&||||M4137|173|WASHER, brake gear spring, large|8|.22
&|—|6||M567|219|WASHER, brake gear spring, small|8|.18
&|||13365||LQ516A|WASHER, carburetor altitude air valve|2|.05
&|||13373||LQ519A|WASHER, carburetor butterfly shaft|2|.05
&|||13375||LQ517A|WASHER, carburetor cap jet and main jet|8|.01
&|||13377||LQ527A|WASHER, carburetor channel screw|4|.01
&|||13380||LQ530A|WASHER, carburetor compensating jet needle valve seat fiber|6|.01
&|||13391||LQ538A|WASHER, carburetor gasoline plug fiber|2|.01
&|||13396||LQ542A|WASHER, carburetor internal body fiber|8|.01
&|||13415||LQ556A|WASHER, carburetor throttle shaft yoke end bolt|4|.03
&|||||SH943C|WASHER, clutch throwout ball bearing|4|.18
%X|||||SH943B|WASHER, clutch throwout bearing retainer|2|.05
%X|||||SH955A|WASHER, clutch throwout stop eyebolt (I. D. ½″, O. D. 1⅜″, thickness ⅛″)|2|.02
&|||||SH976R|WASHER, cooling system drain plug swivel pin|2|.02
&|24|14|B12237||LQ231A|WASHER, crank case oil retaining (flywheel end)|1|.05
(gy)&|||S10||586|WASHER, distance recorder drive pinion|1|.02
(gy)&|||S4040||586|WASHER, distance recorder drive pinion shaft|1|.02
(gy)&|||S35||586|WASHER, distance recorder drive shaft|2|.01
X|||D28928|||WASHER, distributor ball bearing (felt) (.670″ x .895″ x .062″)|4|.01 P
&|||D30146|||WASHER, distributor contact arm dismounting stud insulating (.265″ x .437″ x~  .04″)|12|.04 P
&|||D30373|||WASHER, distributor cup insulating|8|.01 P
&|||D20241|||WASHER, distributor head high tension terminal lock|24|.03 P
&|||D29765|||WASHER, distributor ignition coil and distributor head insulating (large)|2|.01 P
&|||D29577|||WASHER, distributor ignition coil and distributor head insulating (small)|2|.02 P
&|||D20791|||WASHER, distributor ignition coil and distributor head stud lock|2|.01 P
&|||D29578|||WASHER, distributor resistance unit mounting screw insulating (.144″ x .531″~  x .031″)|2|.01 P
%X|||||SH233G|WASHER, driving pulley|1|.21
&||||M190|70|WASHER, engine suspension bevel|4|.08
%X|||||SH152F|WASHER, exhaust manifold guard (asbestos)|8|.02 P
&|||H20/21195||538|WASHER, gasoline tank cover lock|2|.22''')

r=add(268,'''%X||||M1758|188|WASHER, gasoline tank strainer drain plug (leather)|3|$0.03 P
&|||D153/21256||188|WASHER, gasoline tank strainer flange (leather)|3|.08
&|||D29852|||WASHER, generator armature shaft plain|1|.01 P
&|||D29862|||WASHER, generator brush arm mounting stud insulation|1|.01 P
&|||D22645|||WASHER, generator brush arm small spring plain|8|.01 P
&|||D30152|||WASHER, generator brush arm stud insulating (inner)|1|.01 P
&|||D30138|||WASHER, generator brush arm stud insulating|1|.01 P
%X|||||SH204B|WASHER, generator coupling|1|.88
&|8209|16|8209||LQ399A|WASHER, generator driving shaft ball bearing oil retaining|1|.02 P
&|||D31239|||WASHER, generator end cover oiler|1|.01 P
&|||D30085|||WASHER, generator field coil insulating (.312″ x .5″ x .062″)|3|.02 P
&|||D22616|||WASHER, generator field coil stud (large)|2|.01 P
&|||D27193|||WASHER, generator insulating (.312″ x .5″ x .062″)|1|.01 P
&|||||SH142G|WASHER, governor felt retaining|2|.24
&|||||SH142H|WASHER, governor oil retaining|1|.15
&|||||SH142D|WASHER, governor spindle|1|.04
&|||||SH65L|WASHER, hand starter (1/16″ x 41/64″ x 1⅝″)|1|.03
&|||W–AD17|||WASHER, ignition battery jar cover plate (soft rubber)|8|.03 P
%X|||W–M8|||WASHER, ignition battery vent plug|4|.01 P
&|||D30808|||WASHER, ignition switch resistance stud plain (brass, .195″ x .344″ x .078″)|2|.01 P
&|||D27132|||WASHER, lock, .140″ x 5/16″ x .031″. (For ignition switch screw D26948.)|1|.01 P
%(sh)R||||||WASHER, lock, 3/16″. (For stove bolt, flathead, 3/16″ x 1″; stove volt, round head,~  3/16″ x ⅝″; screw, machine, round head, No. 10 (3/16″)—24 x ½″; screw, machine,~  round head, No. 10 (3/16″)—24 x ¾″; screw, machine, round head, No. 10 (3/16″)—24~  x 1″; screw, machine, round head, No. 10 (3/16″)—32 x 5/16″.)|13|.01 P
&|||D20241|||WASHER, lock, .195″ x .33″ x .046″. (For distributor head D13725 (12).)|24|.01 P''')

r=add(269,'''&|||D20495|||WASHER, lock, .195″ x .393″ x .046″. (For voltage regulator stud D30365; igni-~  tion switch and voltage regulator screw D30369; ignition switch castle nut~  D29864; generator field coil stud D29829 (2); generator field coil stud D30383;~  generator brush arm mounting stud D30135; ignition switch resistance unit~  D13780 (2); ignition switch resistance unit D13743 (2).)|21|.01 P
%X|||D30060|||WASHER, lock, .195″ x .453″ x .046″. (For distributor rotor screw D29616; dis-~  tributor condenser and breaker plate stud D29595.)|4|.01 P
%(sh)R||||||WASHER, lock, ¼″. (For bolt SH101Q; bolt, carriage, ¼″ x 1 9/16″; stove bolt,~  round head, ¼″ x 7/16″; stove bolt, round head, ¼″ x ½″; stove bolt, round head,~  ¼″ x ⅝″; bolt, stove, round head, ¼″ x ¾″, for angle SH152D and angle SH152C~  (2); stove bolt, round head, ¼″ x ⅞″; stove bolt, round head, ¼″ x 1″; stove~  bolt, round head, ¼″ x ¾″; instrument board stove bolt, round head, ¼″ x 1¼″;~  stove bolt, round head, ¼″ x 2″; bolt, U. S. Std., hexagon head, ¼″ x ⅝″; bolt,~  U. S. Std., hexagon head, ¼″ x ¾″; bolt, U. S. Std., hexagon head, ¼″ x ⅞″,~  for strap SH569P; bolt, U. S. Std., hexagon head, ¼″ x 1″; bolt, U. S. Std., hex-~  agon head, ¼″ x 1⅜″; bolt, U. S. Std., hexagon head, ¼″ x 1½″; bolt, U. S.~  Std., hexagon head, ¼″ x 1 9/16″; bolt, U. S. Std., hexagon head, ¼″ x 1⅝″; screw,~  cap, U. S. Std., button head, ¼″ x 2″; screw, cap, U. S. Std., round head, ¼″ x~  ⅜″; screw SH424E; screw, cap, U. S. Std., hexagon head, ¼″ x ⅝″; screw, cap,~  U. S. Std., hexagon head, ¼″ x 7/16″; bolt, U. S. Std., hexagon head, ¼″ x ⅞″;~  screw cap, U. S. Std., round head, ¼″ x ½″; screw, machine, round head, No.~  14—20 x ½″; bolt, U. S. Std., hexagon head, ¼″ x ½″; screw, cap, U. S. Std.,~  hexagon head, ¼″ x ½″; screw LQ510A.)|342|.01 P
&|||D21717|||WASHER, lock, .256″ x .429″ x .062″. (For voltage regulator terminal stud~  D30380; voltage regulator terminal stud D30366; generator drive shaft end hous-~  ing binding bolt D29848; generator brush arm mounting (long terminal) stud~  D29811; 2 distributor ignition coil and distributor head studs D29635.)|9|.01 P
&|||D24953|||WASHER, lock, .275″ x .454″ x .031″. (For voltage regulator mounting coil nut~  lock.)|1|.01 P
%(sh)R||||||WASHER, lock, 5/16″. (For bolt, U. S. Std., hexagon head, 5/16″ x ⅞″; bolt, U. S.~  Std., hexagon head, 5/16″ x ¾″; bolt, U. S. Std., hexagon head, 5/16″ x 1″; bolt,~  U. S. Std., hexagon head, 5/16″ x 1¼″; screw, cap, U. S. Std., flathead, 5/16″ x ⅞″;~  screw, cap, U. S. Std., flathead, 5/16″ x 1″; screw, cap, U. S. Std., round head,~  5/16″ x 1″; screw, cap, U. S. Std., hexagon head, 5/16″ x ⅝″; screw, cap, U. S. Std.,~  hexagon head, 5/16″ x ⅜″; screw, cap, U. S. Std., hexagon head, 5/16″ x ⅞″; screw,~  cap, U. S. Std., hexagon head, 5/16″ x ¾″, for funnel rack; screw, cap, U. S. Std.,~  hexagon head, 5/16″ x ½″.)|127|.01 P''')

r=add(270,'''%(sh)R||||||WASHER, lock, ⅜″. (For stud SH194D; stud MX99 (2); stud LQ233A; bolt,~  S. A. E., ⅜″ x 2¼″; bolt SH402L (2); bolt, U. S. Std., countersunk head, ⅜″~  x 1⅜″; bolt, U. S. Std., countersunk head, ⅜″ x 1½″; bolt, U. S. Std., hexagon~  head, ⅜″ x ¾″; bolt, U. S. Std., hexagon head, ⅜″ x ⅞″; bolt, U. S. Std., hexagon~  head, ⅜″ x 1″; bolt, U. S. Std., hexagon head, ⅜″ x 1 1/16″; bolt, U. S. Std., hexagon~  head, ⅜″ x 1⅛″, for housing SH145A; bolt, U. S. Std., hexagon head, ⅜″ x 1¼″;~  bolt, U. S. Std., hexagon head, ⅜″ x 1⅜″; bolt, U. S. Std., hexagon head, ⅜″~  x 1 5/16″; bolt, U. S. Std., ⅜″ x 1½″; bolt, U. S. Std., hexagon head, ⅜″ x 1⅝″;~  bolt, U. S. Std., hexagon head, ⅜″ x 2″; bolt, U. S. Std., hexagon head, ⅜″ x 2¼″;~  bolt, U. S. Std., hexagon head, ⅜″ x 2¾″; bolt, U. S. Std., hexagon head, ⅜″~  x 3½″, for bracket SH137A; bolt, U. S. Std., square head, ⅜″ x 1¼″; catch M2153;~  pin M2149; screw, cap, U. S. Std., flathead, ⅜″ x 1⅛″; screw, cap, U. S. Std.,~  flathead, ⅜″ x 1½″; screw, cap, U. S. Std., hexagon head, ⅜″ x 1 3/16″; screw, cap,~  U. S. Std., hexagon head, ⅜″ x ¾″, (except for bearing SH900A); screw, cap,~  U. S. Std., hexagon head, ⅜″ x 1″; screw, cap, U. S. Std., hexagon head, ⅜″ x ½″~  (except for plate SH608A); screw, cap, U. S. Std., hexagon head, ⅜″ x ⅝″, for~  plates M995A and M995B; screw, cap, U. S. Std. fillister head, ⅜″ x ½″; tap bolt~  SH586F; screw MX38.)|373|$0.01 P
%(sh)R||||||WASHER, lock, 7/16″. (For bolt, U. S. Std., hexagon head, 7/16″ x 1″; bolt, U. S.~  Std., hexagon head, 7/16″ x 1⅛″; screw, cap, U. S. Std., round head, 7/16″ x 1¼″.)|27|.01 P
%(sh)R||||||WASHER, lock, ½″. (For stud SH279D; bolt SH501B; bolt SH550A; bolt~  SH942C; bolt SH586G; bolt, U. S. Std., hexagon head, ½″ x ⅞″; bolt, U. S. Std.,~  hexagon head, ½″ x 1″; bolt, U. S. Std., hexagon head, ½″ x 1⅛″; bolt, U. S. Std.,~  hexagon head, ½″ x 1¼″; bolt, U. S. Std., hexagon head, ½″ x 1⅜″; bolt, U. S.~  Std., hexagon head, ½″ x 1 7/16″; bolt, U. S. Std., hexagon head, ½″ x 1½″; bolt,~  U. S. Std., hexagon head, ½″ x 1⅝″; bolt, U. S. Std., hexagon head, ½″ x 1¾″;~  bolt, U. S. Std., hexagon head, ½″ x 2⅛″; bolt, U. S. Std., hexagon head, ½″ x~  2½″; bolt, U. S. Std., hexagon head, ½″ x 2 13/16″; bolt, U. S. Std., hexagon head,~  ½″ x 2⅞″; bolt, U. S. Std., hexagon head, ½″ x 3″; bolt, U. S. Std., hexagon head,~  ½″ x 3½″; bolt, U. S. Std., hexagon head, ½″ x 3 3/16″; bolt, U. S. Std., hexagon~  head, ½″ x 3 9/16″; bolt, U. S. Std., hexagon head, ½″ x 3⅝″; bolt, U. S. Std.,||''')

r=add(271,'''||||||  hexagon head, ½″ x 6¾″; pin M2411; pin M2425; staple M1338 (2); screw, U. S.~  Std., hexagon head, ½″ x ⅞″; screw, cap, U. S. Std., hexagon head, ½″ x 1¼″;~  screw, cap, U. S. Std., hexagon head, ½″ x 1″; screw, cap, U. S. Std., hexagon~  head, ½″ x ½″; screw, MX76; screw, cap, U. S. Std., hexagon head, ½″ x ⅞″;~  screw, cap, U. S. Std., hexagon head, ½″ x ¾″; screw, cap, U. S. Std., hexagon~  head, ½″ x 2″; screw, cap, U. S. Std., hexagon head, ½″ x ⅝″; screw, cap, U. S.~  Std., hexagon head, ½″ x 1½″; screw, cap, U. S. Std., hexagon head, ½″ x~  1¾″.)|619|.01 P
%(sh)R||||||WASHER, lock, ⅝″. (For pin SH943A; bolt, U. S. Std., countersunk head,~  ⅝″ x 1¾″; bolt, U. S. Std., hexagon head, ⅝″ x 1⅜″; bolt, U. S. Std., hexagon~  head, ⅝″ x 1½″ for angles SH573M, M2793, and bracket M891; bolt, U. S. Std.,~  hexagon head, ⅝″ x 1 9/16″; bolt, U. S. Std., hexagon head, ⅝″ x 1 11/16″; bolt, U. S.~  Std., hexagon head, ⅝″ x 1¾″; bolt, U. S. Std., hexagon head, ⅝″ x 2 5/16″; bolt,~  U. S. Std., hexagon head, ⅝″ x 2″; bolt, U. S. Std., hexagon head, ⅝″ x 2¼″;~  bolt, U. S. Std., hexagon head, ⅝″ x 2½″ for brackets M183 and M182; bolt, U. S.~  Std., hexagon head, ⅝″ x 2¾″; bolt, U. S. Std., hexagon head, ⅝″ x 3⅞″; bolt,~  U. S. Std., square head, ⅝″ x 1½″; bolt, U. S. Std., square head, ⅝″ x 1¾″; bolt,~  U. S. Std., square head, ⅝″ x 2 1/16″; bolt, U. S. Std., square head, ⅝″ x 2¼″; bolt,~  U. S. Std., square head, ⅝″ x 2⅜″; end M3189; screw, cap, U. S. Std., flathead,~  ⅝″ x 1½″; screw, cap, U. S. Std., flathead, ⅝″ x 1¾″; screw, cap, U. S. Std.,~  flathead, ⅝″ x 1⅞″; screw, cap, U. S. Std., flathead, ⅝″ x 2⅛″; screw, cap,~  U. S. Std., flat-head, ⅝″ x 2 3/16″; screw, cap, U. S. Std., flathead, ⅝″ x 2¼″;~  screw, cap, U. S. Std., flathead, ⅝″ x 2⅜″; screw, cap, U. S. Std., flathead, ⅝″~  x 2½″; screw, cap, U. S. Std., flathead, ⅝″ x 2⅝″; screw, cap, U. S. Std., flat-~  head, ⅝″ x 2⅞″; screw, cap, U. S. Std., flathead, ⅝″ x 3½″; screw, cap, U. S.~  Std., flathead, ⅝″ x 3⅝″; tap bolt SH303C; tap bolt SH380C; tap bolt SH503A;~  tap bolt SH499B; screw, cap, U. S. Std., hexagon head, ⅝″ x 1¼″; screw, cap,~  U. S. Std., hexagon head, ⅝″ x 2″; screw, cap, U. S. Std., hexagon head, ⅝″ x~  ⅞″; tap bolt SH380B; bolt, U. S. Std., hexagon head, ⅝″ x 1½″; bolt, U. S.~  Std., hexagon head, ⅝″ x 1″; bolt, U. S. Std., hexagon head, ⅝″ x 1⅞″; screw~  MX60; screw, cap, U. S. Std., hexagon head, ⅝″ x ¾″; screw, cap, U. S. Std.,~  hexagon head, ⅝″ x 2¼″.)|617|.01 P
%(sh)R||||||WASHER, lock, ¾″. (For bolt SH470D; bolt M383; bolt, U. S. Std., hexagon~  head, ¾″ x 2¼″; bolt, U. S. Std., hexagon head, ¾″ x 2⅜″; bolt, U. S. Std.,~  hexagon head, ¾″ x 2½″; bolt, U. S. Std., hexagon head, ¾″ x 1⅝″; bolt, U. S.~  Std., hexagon head, ¾″ x 1¾″; bolt, U. S. Std., hexagon head, ¾″ x 2″; screw,~  cap, U. S. Std., flathead, ¾″ x 3 9/16″; screw, cap, U. S. Std., hexagon head, ¾″ x~  2¼″; tap bolt SH303B; screw, cap, U. S. Std., hexagon head, ¾″ x 1⅝″; screw,~  cap, U. S. Std., hexagon head, ¾″ x 1¾″; screw M390.)|127|.01 P''')

r=add(272,'''%X|||||SH220A|WASHER, low-speed connecting link|2|$0.06
&|||E43/21220||438|WASHER, periscope hole cover (driver’s turret)|1|.22
&|||D29766|||WASHER, plain, .0635″ x 5/32″ x .02″. (For distributor contact arm spring D13803~  (2).)|8|.01 P
&|||D29576|||WASHER, plain, .144″ x .469″ x .022″. (For distributor resistance unit mounting~  stud D29663; distributor contact arm spring screw D29574.)|8|.01 P
&|||D25116|||WASHER, plain, .147″ x .313″ x .022″. (For distributor resistance unit mounting~  screw D29663; distributor rotor screw D29616.)|4|.01 P
&|||D26441|||WASHER, plain, .173″ x .344″ x .025″. (For distributor screw D29598.)|2|.01 P
&|||D30061|||WASHER, plain, .178″ x .504″ x .031″. (For distributor.)|2|.01 P
%(sh)R||||||WASHER, plain, 3/16″. (For screw, machine, round head, No. 10 (3/16″)—24 x ¾″.)|2|.01 P
&|||D29777|||WASHER, plain, .194″ x .375″ x .031″. (For distributor condenser and breaker~  plate stud (2).)|12|.01 P
&|||D30139|||WASHER, plain, .194″ x .406″ x .031″. (For generator field coil.)|1|.01 P
&|||D29654|||WASHER, plain, .202″ x .296″ x .015″. (For distributor resistance unit, assembly~  D13747.)|2|.01 P
&|||D29655|||WASHER, plain, .202″ x .396″ x .02″. (For distributor resistance unit, assembly~  D13747.)|2|.01 P
&|||D26503|||WASHER, plain, .221″ x .468″ x .031″. (For distributor condenser and breaker~  plate stud D29595; distributor cup stud D39536.)|10|.01 P
%(sh)R||||||WASHER, plain, ¼″. (For stove bolt, round head, ¼″ x 2″; guide M2156 cap~  screw; handle C114E (4); screw, cap, button head, ¼″ x 2″; machine screw,~  NC, round head, No. 8 (.164″) x 1″ (1).)|23|.01 P
&|||D29662|||WASHER, plain, .257″ x .5″ x .031″. (For distributor ignition coil and distributor~  head stud D29635; distributor head stud D29635 (2).)|8|.01 P
&|||D30813|||WASHER, plain, .26″ x ¾″ x .031″. (For ignition switch resistance unit D13780;~  ignition switch resistance unit D13743.)|2|.01 P
%(sh)R||||||WASHER, plain, 5/16″. (For bolt SH996G; bolt SH996C; screw, cap, U. S. Std.,~  flathead, ⅜″ x 1 5/16″; handle pin X246; handle pin X271.)|14|.01 P''')

r=add(273,'''&|||D20915|||WASHER, plain, .314″ x .625″ x .031″. (For voltage housing, assembly (3);~  generator brush arm mounting stud D29811.)|4|.01 P
%(sh)R||||||WASHER, plain, ⅜″. (For bolt, carriage, ⅜″ x 11½″; catch M2153; rest M2842~  cap screw.)|10|.01 P
&|||D26616|||WASHER, plain, .380″ x .875″ x .032″. (For generator armature shaft nut.)|1|.01 P
%(sh)R||||||WASHER, plain, ½″. (For sprocket X257; bolt, U. S. Std., hexagon head, ½″ x~  2 13/16″; pin M2770.)|12|.01 P
%(sh)R||||||WASHER, plain, ⅝″. (For bolt SH942C; pin M2430; 6-pdr. gun pedestal shell~  block bolt.)|7|.01 P
%(sh)R||||||WASHER, plain, ¾″. (For spindle SH282D (2); spindle SH144B.)|3|.01 P
%(sh)R||||||WASHER, plain, 1″. (For bolt, U. S. Std., hexagon head, ¼″ x 1⅜″.)|4|.01 P
%(sh)R||||||WASHER, plain, brass, 5/32″. (For screw, wood, round head, brass, No. 8 x ¾″.)|10|.01 P
&|||D24336|||WASHER, plain, brass, .147″ x .312″ x .0254″. (For voltage regulator mounting~  terminal screw D30143.)|7|.01 P
%|||||SH979E|WASHER, plain, I. D. .18″, O. D. .5″, .05″ thick. (For airplane watch mat~  machine screw (2).)|8|.01 P
%X||||X261|803|WASHER, semaphore arm|2|.04
&||||X310|801|WASHER, semaphore ratchet spring|1|.12
&||||X275|802|WASHER, semaphore spring|1|.03
&|||||SH964F|WASHER, spark and throttle control friction|4|.18
&|—~111|33~17~19|111||LQ113A|WASHER, special, ¼″. (For bolt LQ112A (1); bolt LQ114A (1); stud LQ88A~  in crank case, upper half, assembly (1); stud LQ196A (1); stud LQ229A (1); bolt~  LQ164A (2); bolt LQ443A (2); stud LQ88A (water pump body) (1); bolt LQ243A~  (2).)|202|.01 P''')
r[-1]['cell_baseline_offsets']={'ident':1.5,'plate':1,'mfr':2,'ord':2,'note':2}
r[-1]['cell_braces']={'ident':['left'],'plate':['left','right']}
append_rows(r,'''&|||112||LQ52A|WASHER, special, 5/16″. (For bolt LQ50A (2); stud LQ302A (1); stud LQ301A~  (1); screw LQ419A (1); screw LQ420A (1).)|98|.01 P
&|||113||LQ166A|WASHER, special, ⅝″. (For screw LQ165A (1); stud LQ304A (1); stud LQ303A~  (1); bolt LQ246A (2); stud LQ269A (1); stud LQ270A (1); stud LQ197A (1);~  stud LQ271A (1); bolt LQ245 A (2).)|73|.01 P
&|||115||LQ471A|WASHER, special, I. D. 33/64″, O. D. 15/16″, 1/16″ thick. (For bolt LQ189A (1); bolt~  LQ190A (1).)|16|.01 P
&|||12548||LQ191A|WASHER, special, I. D. 33/64″, O. D. 1 1/16″, ⅛″ thick. (For bolt LQ189A (1); bolt~  LQ190A (1).)|16|.01 P
&|||||SH373T|WASHER, special, steel, O. D. 1⅜″ x 3/32″ thick. (For cap screw, U. S. Std.,~  flathead, 5/16″ x ¾″ (1).)|2|.02
&||||M2830|478|WASHER, sponson hinge pin|4|.20
&|||W–AD18|||WASHER, starting and lighting battery terminal post|12|.01
&|||||SH921B|WASHER, steel, I. D. 1 1/16″, O. D. 1¾″ x ⅛″. (For ¾″ flexible conduit.)|1|.08
&|||D30385|||WASHER, switch and voltage regulator retaining|2|.01''')

r=add(274,'''%X||||M1483|60|WASHER, track adjusting shaft|4|$0.88
&|66|22||M248|705|WASHER, transmission bevel pinion shaft|1|.22
%X||||MX78A|698|WASHER, transmission high speed brake adjusting spring, I. D. 11/16″|2|.04
%X||||MX78B|698|WASHER, transmission high speed brake adjusting spring, I. D. 13/16″|2|.05
&|||||SH101G|WASHER, transmission mechanical lubricator center piece|6|.02
&|63~1|22~23||M253|703|WASHER, transmission pinion shaft bearing housing oil retaining (felt)|1|.48''')
r[-1].update(space_before=.5,space_after=.5,cell_baseline_offsets={'ident':-.5,'plate':-.5},cell_braces={'ident':['left'],'plate':['right']})
append_rows(r,'''&|11|22||M288|680|WASHER, transmission planet disk|2|.89
%X|||||SH951F|WASHER, triple combination valve plug, (⅜″ square hole)|3|.05
&|||||SH951G|WASHER, triple combination valve plug, (13/32″ round hole)|3|.01
%X|||||SH951A|WASHER, triple combination valve plug thackray|3|.18
%(gh)X|||||SH412B|WASHER (turret roof door fastener), thackray|2|.15
X|||||SH958D|WASHER, ventilating fan sprocket|1|.03
&|||D29340|||WASHER, voltage housing insulating|6|.01 P
&|||D24046|||WASHER, voltage regulator mounting terminal screw plain|7|.01
%(mh)R||||||WASTE, wool, oz. (For cap M294 (2); cap M298 (2).)|8|.01
&|||W–AF49|||WEDGE, starting and lighting battery (wood)|4|.01
&|||15387||LQ535A|WEIGHT, carburetor float|4|.03''')
assembly(r,'WELL, carburetor secondary, assembly','.38',note='&',qty='(4)')
component(r,'*one LQ562A carburetor secondary well restriction COLLAR (4)',mfr='14683',price='.13')
component(r,'*one LQ561A carburetor secondary well TUBE (4)',mfr='14882',price='.23')
component(r,' one LQ509A GASKET, copper, asbestos, 17/64″.)')
assembly(r,'WHEEL, track adjusting, assembly','290.39',note='&',qty='(2)',ident='53\n—',plate='2\n28')
r[-2].update(space_before=.5,space_after=.5,cell_baseline_offsets={'ident':-.5,'plate':-.5},cell_braces={'ident':['left'],'plate':['right']})
component(r,'*two     M147 track adjusting wheel RIM (4)',ord='52',price='65.75')
component(r,'*one   M1403 track wheel BOSS (4)',ident='6',plate='28',ord='56',price='34.75')
component(r,'*five M1405X track wheel DIAPHRAGM (20)',ident='13',plate='28',ord='58',price='4.25')
component(r,'*one M1405Y track wheel DIAPHRAGM (4)',ident='12',plate='28',ord='59',price='4.25')

r=start(275)
component(r,'*two    M1404 track wheel DISK (8)',ident='1',plate='28',ord='59',price='48.00')
pieces(r,''' thirty-six       — RIVET, button head, ⅝″ x 1⅞″,
twenty-four       — RIVET, button head, ⅝″ x 2⅝″,
 forty-eight      — RIVET, button head, ¾″ x 2⅛″.)''')
assembly(r,'WHEEL, track driving, assembly','244.69',note='&',qty='(2)',ident='18\n—\n5',plate='2\n27\n25')
r[-2].update(space_before=1,space_after=1,cell_baseline_offsets={'ident':-1,'plate':-1},cell_braces={'ident':['left'],'plate':['right']})
component(r,'*two     M1401 track driving wheel RIM (4)',ident='2',plate='27',ord='52',price='93.00')
component(r,'*one   M1403 track wheel BOSS (4)',ident='5',plate='27',ord='56',price='34.75')
component(r,'*five M1405X track wheel DIAPHRAGM (20)',ident='3',plate='27',ord='59',price='4.25')
component(r,'*one M1405Y track wheel DIAPHRAGM (4)',price='4.25')
component(r,'*two    M1404 track wheel DISK (8)',ident='4',plate='27',ord='59',price='48.00')
pieces(r,''' thirty-six       — RIVET, button head, ⅝″ x 1⅞″,
twenty-four       — RIVET, button head, ⅝″ x 2⅝″,
 forty-eight      — RIVET, button head, ¾″ x 2⅛″.)''')
append_rows(r,'''&|||D30323|||WICK, generator end cover oiler|1|.01 P
&|||D30528|||WIRE, copper, .0403″ x 1 1/16″. (For voltage regulator, assembly D5718 (1).)|1|.01 P
&(mh)R||||||WIRE, copper, B. & S. gage, No. 16, spool (2 pieces 10″ long required for retainer~  SH434B; 2 pieces 10″ long required for retainer SH434C.)|—|.25
&(mh)R||||||WIRE, lock, brass, No. 20 x 1¼″. For (cover LQ532A)|2|.01 P
*||||||WIRE, lock, soft steel, W. & M. Ga. No. 16 x 4″. (For screw LQ557A (2).)|(4)|.01 P
*|176|15|177||LQ31A|WIRE, lock, W. & M. Ga. No. 18 x 8″. (For screw LQ419A and LQ420A (1);~  screw LQ418A (12); plug LQ428A (1); valve LQ446A (1); screw LQ33A (1).)|22|.10 P
*|||||234|WIRE, lock, W. & M. Ga. No. 20, 10″ long. (For plate M1047 cap screw (1).)|(1)|.01 P
&(mh)R||||||WIRE, screen, B. & S. Ga. #30, #20 mesh yd. (2 pieces 1⅛″ x 14 13/16″ for screen~  LQ451A; 1 piece 4⅜″ dia.; 1 piece 4⅜″ dia; for screen LQ457A.)|—|.75 P
&(mh)R||||||WIRE, soft iron, W. & M. Ga. No. 16, spool (1 piece 10¾″ long required for crank~  shaft thrust bearing retaining nut; 1 piece 48″ long required for clutch drum~  cap screw; 1 piece 26″ long required for clutch sliding collar cap screw; 1 piece~  30″ long required for clutch spring plunger; 1 piece 4″ long required for screw~  LQ557A (2).)|—|.08 P
*|||||SH861K|WIRE, soft iron, W. & M. Ga. No. 16, length 30″. (For clutch spring plunger~  SH861A.)|(1)|.01 P''')

r=add(276,'''&(mh)R||||||WIRE, soft iron, W. & M. Ga. No. 18, spool (1 piece 10″ long required for hand~  starter screws (SH65A); 16 pieces 8″ long required for cam shaft bearing lock~  screws; 1 piece 8″ long required for screw LQ419A and LQ420A; 1 piece 8″ long~  required for screw LQ418A; 1 piece 10″ long required for screw LQ165A; 1 piece~  10″ long required for plug LQ145A; 2 pieces 8″ long required for plug LQ541A;~  2 pieces 19″ long required for screws LQ510A; 2 pieces 10″ long required for bolts~  LQ526A; 4 pieces 5″ long required for lock LQ559A; 2 pieces 4″ long required~  for carburetor)|—|$0.10 P
*|||||713A|WIRE, soft steel, W. & M. Ga. No. 16, length 2″. (For oil box cover.)|(4)|.01 P
*|||||SH999C|WIRE, soft steel, W. & M. Ga. No. 16, length 26″. (For clutch sliding collar~  SH999A cap screws.)|(1)|.01 P
*|||||SH866C|WIRE, soft steel, W. & M. Ga. No. 16, length 48″. (For clutch drum cap screws.)|(1)|.02 P
&(mh)R||||||WIRE, soft steel, W. & M. Ga. No. 20, spool (1 piece 10″ long required for plate~  M1047 cap screws (1).)|—|.12 P
&(mh)R||||||WIRE, steel, 3/16″, ft., (1 piece 92⅝″ long required for wire M2167B (1).)|—|.03 P
&|||||SH103D|WORM, transmission mechanical lubricator|1|.78
&|||||SH105C|YOKE, transmission mechanical lubricator lower plunger|6|.38
&|||||SH105B|YOKE, transmission mechanical lubricator (upper plunger)|6|.38''')

END_NOTICE='The Set of Spare Parts, Accessories, Parts for Accessories, and Addendum covering basic spare parts will be published as Changes No. 1 to this list.'
