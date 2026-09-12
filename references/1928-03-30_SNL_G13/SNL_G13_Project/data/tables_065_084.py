"""Source-led transcription of pages 65–84; continuation breaks retained.

The review register records uncertain readings and apparent source inconsistencies.
"""
from .parts_tables import row
from .opening_tables import entry, component, composed
from .tables_045_064 import assembly
TABLES={}
def start(page):
 TABLES[page]=[]
 return TABLES[page]
def add(page,content):
 r=start(page)
 for line in content.strip().splitlines():
  values=line.split('|');assert len(values)==9,(page,line)
  r.append(row(*[v.replace('~','\n') for v in values]))
 return r
def pieces(r,content):
 for line in content.strip().splitlines():component(r,line.replace('~','\n'))
def stacked(r,**cells):
 r[-1].update(cells,space_before=.5,space_after=.5,cell_baseline_offsets={k:-.5 for k in cells})

r=add(65,'''%X|||||SH921G|CLAMP, flexible conduit, I. D. 1 1/16″|1|.15 P
%X|||||SH920E|CLAMP, flexible conduit, offset I. D. 1⅜″|2|.20 P
%X|||||SH921A|CLAMP, flexible conduit, I. D. 1⅜″|1|.15 P
%X|||||SH920B|CLAMP, flexible conduit, I. D. 2 1/16″|1|.16 P
%X|||||SH920D|CLAMP, flexible conduit, I. D. 2¼″|3|.20 P
%X|||||SH984G|CLAMP, gasoline tube|2|.10 P
%X|||||SH984K|CLAMP, gasoline tube|1|.08 P
%X|8450|15|8450||LQ178A|CLAMP, hose, 1 1/16″. (For hose LQ177A (2).)|48|.01 P''')
assembly(r,'CLAMP, hose, 1½″, assembly','.03 P',qty='(2)')
component(r,'*one B101480A hose CLAMP, 1½″ (2)',price='.02 P')
component(r,'one —          BOLT, stove, rd. hd. ¼″ x 1¼″, w/ stove bolt nut and\n                    lock washer.\n                  (For radiator hose, 3 ply, I. D. 1¼″.)')
entry(r,'CLAMP, hose, 1⅝″. (For hose LQ175A (2).)',note='%X',ident='6',plate='14',mfr='8453',ord='LQ176A',qty='12',price='.02 P')
assembly(r,'CLAMP, hose, 2¼″, assembly','.04 P',qty='(2)')
component(r,'*one B101480P hose, CLAMP, 2¼″ (2)',price='.03 P')
component(r,'one —          BOLT, stove, rd. hd. ¼″ x 1¼″, w/ stove bolt nut and\n                    lock washer.\n                  (For radiator hose, 5 ply, I. D. 2″.)')
assembly(r,'CLAMP, hose, 2¾″, assembly','.05 P',qty='(12)')
component(r,'*one B101480Z hose CLAMP, 2¾″ (12)',price='.04 P')
component(r,'one —          BOLT, stove, rd. hd. ¼″ x 1¼″, w/ stove bolt nut and\n                    lock washer.\n                  (For radiator hose, 5 ply, I. D. 2½″, coupling SH975E\n                    (2); coupling SH975C (3) connection SH199B (2).)')
entry(r,'CLAMP, intensifier board',note='%X',ord='SH1021G',qty='8',price='.16')
for brit,ord,text,qty,price in [('M4130','173','control channel angle, left','4','.95'),('M4129','173','control channel angle, right','2','.95'),('M2186','373','control rod casing','6','.18'),('M1583','222','drive chain casing angle, side','8','.28'),('M1593','231','drive chain casing angle, top','4','.25'),('M3310','165','engine oil tank support','4','.38'),('M189','70','engine single point suspension','1','.40'),('','A4025','funnel rack','1','.12')]:
 entry(r,'CLEAT, '+text,note='X',brit=brit,ord=ord,qty=qty,price=price)
entry(r,'CLEVIS, adjustable, S. A. E., ¼″, R. H. thread. (For rod LQ315A (1).)',note='&',mfr='8338',ord='LQ318A',qty='1',price='.50')
entry(r,'CLEVIS, padlock (For padlock No. 840 (1).)',note='(cp) R',ord='A6954',qty='1',price='.08 P')
entry(r,'CLIP, brake spring',note='%X',ord='SH98C',qty='1',price='.75')

r=add(66,'''&|||||A263|CLIP, cable, ¾″. (For cable B177 (6); cable B176 (3); cable B178 (7); cable B179~  (8).)|24|$0.01 P
(gy)&|||||A264|CLIP, cable, double, ¾″. (For cable B177 (2).)|2|.02
(gy)&|||||A265|CLIP, cable, double, 1¼″. (For cable B178 (2).)|2|.05
&|||L13533||LQ174A|CLIP, cylinder water inlet manifold left extension|1|.25
&|||L13532||LQ173A|CLIP, cylinder water inlet manifold right extension|1|.25
X|||||SH291C|CLIP, driver’s seat, length 3½″|1|.20
&|||||SH98B|CLIP (foot brake), bridle|1|1.25
&|||D30267|||CLIP, generator drive shaft end housing binding bolt|1|.03 P
%X|||||SH373M|CLIP, hand lamp spring|1|.18
&|||12283||LQ325A|CLIP, high tension cable tube|6|.03
&|||||SH373J|CLIP, house lamp spare battery box spring|1|.15
&|||||A4055|CLIP, pyrene refill bracket|7|.42
&|||||SH280E|CLIP, radiator cooling fan fastening, No. 1|1|.24
&|||||SH280F|CLIP, radiator cooling fan fastening, No. 2|1|.36
&|||||SH488A|CLIP, spare barrel lower (left sponson)|1|.36
&|||||SH488B|CLIP, spare barrel upper (left sponson)|1|.40
%X|||||SH372C|CLIP, spare barrel lower (main hull)|4|.40
%X|||||SH372A|CLIP, spare barrel upper (main hull)|4|.70
&||||M2835|488|CLIP, sponson ramrod bracket|4|.18
&||||M2437|424|CLIP, spring. (On machinegunner’s seat (1); main turret (4); sponson, right (2);~  left (2).)|14|.22
&|||D25647|||CLIP, switch and voltage regulator terminal|4|.01 P
&|6|30||M365|698|CLIP, transmission high-speed brake band|2|.48''')
assembly(r,'CLIP, voltage regulator, with contact, assembly','.54 P',note='&',mfr='D13611')
component(r,'*one D11426 voltage regulator CONTACT,')
component(r,'*one D29455 voltage regulator terminal CLIP.)')
entry(r,'CLIP, water pipe',note='&',ident='—',plate='24',ord='SH976A',price='.48')
entry(r,'CLIP, water pipe connection',note='&',ident='—',plate='24',ord='SH975C',price='.58')

r=add(67,'''%(pf) X||||||COCK, drain, ¼″ pipe thread, tee handle. (For tube C8015 (1).)|1|.17 P
%(pf) X|—|24|||A16484|COCK, drain, ½″, tee handle. (For flange M3311 (1); pipe SH976E (1); pipe~  SH976K (1); pipe SH976V (1).)|5|.21 P
%X|||||SH962H|COCK, regulating tank air, No. 1 (Lunkenheimer type, ⅛″, modified)|1|.60
%(pf) X||||||COCK, stop, ¼″, lever handle. (For regulating tank flexible tube connection,~  assembly (2).)|2|.23 P
&|||||B101964A|COCK, soldering, ¼″ (brass). (For tube C8013 (3).)|3|.75 P''')
assembly(r,'COIL, distributor induction, assembly','.20 P',qty='(2)',note='(b)&',mfr='D13740')
component(r,'two (D31012) distributor terminal nut SCREW, assembly.)')
assembly(r,'COIL, generator field, assembly','5.66 P',note='&',mfr='D13784')
component(r,'*one —          generator field COIL (1)',price='4.99')
pieces(r,'''one (D29829) generator field coil STUD, long, assembly,
one (D30383) generator field coil STUD, short, assembly.)''')
assembly(r,'COLLAR, carburetor throttle control tube end, assembly','.09 P')
component(r,'*one LQ119A carburetor throttle control tube end COLLAR (1)',mfr='L13236',price='.08')
component(r,'one —          PIN, split, 3/32″ x ¾″.)')
for ident,ord,text,price in [('9','SH869A','clutch cone supporting','8.25'),('11','SH999A','clutch sliding','15.78'),('28','SH998B','clutch spring thrust','5.00')]:
 entry(r,'COLLAR, '+text,note='&',ident=ident,plate='21',ord=ord,qty='1',price=price)
for mfr in ['P55','P29']:entry(r,'COLLAR, distance recorder cable coupling',note='&',mfr=mfr,qty='1',price='.02')
entry(r,'COLLAR, engine control rocker shaft',note='&',ord='SH965C',qty='2',price='.38')
entry(r,'COLLAR, generator brush arm',note='&',mfr='D30314',qty='1',price='.02 P')
entry(r,'COLLAR, generator field coil stud spacing',note='&',mfr='D30313',qty='1',price='.01 P')
assembly(r,'COLLAR, throttle release spring, assembly','.50')
component(r,'*one SH993C throttle release spring COLLAR, threaded',ident='—',plate='12',price='.22')
pieces(r,'''one —          BOLT, U. S. Std., hexagon head, ¼″ x ⅞″,
one —          WASHER, lock, ¼″.)''')
entry(r,'COLLAR, transmission mechanical lubricator shaft stop (large)',note='&',ord='SH102K',qty='1',price='.24')
entry(r,'COLLAR, transmission mechanical lubricator shaft stop (small). (For shaft\n  SH101H (1); cam shaft SH101P (1).)',note='&',ord='SH101F',qty='2',price='.09')
entry(r,'COLLAR, valve spring, lower',note='&',ord='LQ296A',qty='24',price='.02')
entry(r,'COLLAR, valve spring, upper',note='&',ord='LQ297A',qty='24',price='.50')
entry(r,'COLLET, pipe, ¼″ (brass). (For sprocket cap, M298 (1); elbow SH664A (1)\n  tubes, B101982A, B, C, D, and E (1), tube B101992A (2).)',ord='A16323',qty='12',price='.05 P')

r=start(68)
entry(r,'COMPOUND, sealing, lb. (1 lb. required for starting and lighting battery; ap-\n  proximately ½-lb. required for ignition battery)',note='&',qty='—',price='$0.40')
for size,length,code,price in [('½″','28″','A8406','.24 P'),('¾″','23″','A8405','.26 P'),('1″','15½″','A8404','.28 P'),('1½″','6½ ft.','A8403','2.28 P')]:
 entry(r,f'CONDUIT, flexible steel, {size} x {length}',note='&',ord=code,qty='1',price=price)
for size,length,code,price in [('½″','28″','A8406','.10 P'),('¾″','23″','A8405','.13 P'),('1″','15½″','A8404','.21 P'),('1½″','6½ ft.','A8403','.35 P')]:
 entry(r,f'CONDUIT, flexible steel, {size}, ft. (1 piece {length} long required for conduit {code})',note='(ee)&',qty='—',price=price)
assembly(r,'CONE, clutch, assembly','20.76',note='&',ident='3',plate='21')
component(r,'*one SH876A clutch CONE (1)',price='7.50')
pieces(r,'''one SH869A clutch cone supporting COLLAR,
one SH997C clutch LINING,
one Q52A     PLUG, pipe, square head, ⅛″,
six —           RIVET, button head, 5/16″ x 1⅛″,
forty-three — RIVET, countersunk head, copper, 3/16″ x 11/16″.)''')
entry(r,'CONE, engine oil tank delivery pipe',note='&',brit='M3298',ord='166',qty='1',price='.38')
entry(r,'CONE, male union. (For tube LQ461A (1).)',note='&',mfr='L8458',ord='LQ463A',qty='2',price='.07')
entry(r,'CONE, roller bearing, bore 1.1875″, length 0.873″',note='(c)&',qty='4',price='2.00 P');stacked(r,mfr='{Timken 316 or\n  equal.             }')
entry(r,'CONE, roller bearing, bore 2.75″, length 2.135″',note='(c)&',qty='2',price='8.60 P');stacked(r,mfr='{Timken 6454 or\n  equal.              }')
entry(r,'CONE, ventilating fan inlet',note='&',ord='SH959A',qty='1',price='3.75')
entry(r,'CONNECTION, air pipe regulating tank',note='&',ord='SH950D',qty='1',price='.42')
entry(r,'CONNECTION, cam shaft housing end cover oil',note='&',ident='12',plate='14',mfr='8462',ord='LQ56A',qty='2',price='.43')
assembly(r,'CONNECTION, combination valve to flexible tube, assembly','4.43 P',note='&')
component(r,'two Q51QC ELBOW, M. I., 90°, beaded, ¼″,')

r=start(69)
pieces(r,'''one Q51SC ELBOW, M. I., 90°, beaded, ½″,
one Q51DE ELBOW, street, M. I., 90°, ½″,
one —          NIPPLE, pipe, W. I., ¼″ x 1⅛″,
two —          NIPPLE, pipe, W. I., ¼″ x 1¼″,
six —           NIPPLE, pipe, W. I., ¼″ x 1½″,
one —          NIPPLE, pipe, W. I., ¼″ x 2⅝″,
one —          NIPPLE, pipe, W. I., ¼″ x 3½″,
one —          NIPPLE, pipe, W. I., ⅜″ x 1¼″,
one —          NIPPLE, pipe, W. I., ½″ x 3½″,
one —          TEE, reducing, M. I., beaded, ⅜″ x ¼″ x ¼″,
one —          TEE, reducing, M. I., beaded, ½″ x ⅜″ x ¼″,
three —        UNION, M. I., brass seat, ¼″,
three —        VALVE, horizontal check, brass, ¼″.)''')
entry(r,'CONNECTION, crank case oil tube union',note='&',ident='15',plate='14',mfr='B8463',ord='LQ464A',qty='1',price='1.50')
entry(r,'CONNECTION, exhaust pipe',note='%X',ord='SH402H',qty='2',price='2.50')
assembly(r,'CONNECTION, regulating tank flexible, assembly','1.79 P',ident='13',plate='8')
pieces(r,'''two —          BUSHING, pipe, ⅜″ x ¼″, faced,
two —          COCK, stop, brass, ¼″, lever handle,
two Q51BE ELBOW, street, M. I., 90°, ¼″,
two —          NIPPLE, pipe, close, W. I., ¼″,
one —          TEE, M. I., beaded, ⅜″ x ⅜″ x ½″.)''')
assembly(r,'CONNECTION, spark and throttle control engine lever, assembly','.38',qty='(2)',note='&')
component(r,'*one SH964G spark and throttle control engine lever CONNECTION\n                    (2)',price='.36')
component(r,'one —          SCREW, set, square head, cup point, ¼″ x ⅝″.)')
entry(r,'CONNECTION, transmission mechanical lubricator delivery',note='&',ord='SH102B',qty='6',price='.38')
assembly(r,'CONNECTION, water pipe to pump, assembly','4.64 P',note='&')
pieces(r,'''one —          water pipe drain PLUG, assembly,
one SH976L water pipe drain plug pipe COUPLING,''')
component(r,'*one SH974A water pipe to pump CONNECTION (1).)',ident='—',plate='24',price='4.35')
entry(r,'CONNECTION, water tank outlet',note='&',ident='—',plate='24',brit='M1231',ord='167',qty='1',price='2.75')
assembly(r,'CONNECTOR, conduit, ½″, assembly','.22 P',qty='(2)',note='(ee)&')
component(r,'one — conduit CONNECTOR, ½″ (2)',price='.18')
pieces(r,'''one — conduit lock NUT, ½″,
one — BOLT, stove, 3/16″ x 1″, with stove bolt nut and lock washer.~            For conduit A8406 (2).)''')

r=start(70)
for size,length,code,price,partprice in [('¾″','1″','A8405','$0.30 P','.25'),('1″','1¼″','A8404','.37 P','.30'),('1½″','1½″','A8403','.64 P','.50')]:
 assembly(r,f'CONNECTOR, conduit, {size}, assembly',price,qty='(2)',note='(ee)&')
 component(r,f'*one — conduit CONNECTOR, {size} (2)'+(',' if size=='¾″' else ''),price='' if size=='¾″' else partprice)
 component(r,f'one — conduit lock NUT, {size},')
 component(r,f'one — BOLT, stove, 3/16″ x {length}, with stove bolt nut and lock washer'+('' if size=='¾″' else '.'),price=partprice if size=='¾″' else '')
 component(r,f'            For conduit {code} (2).)')
for mfr,text,qty,price in [('D29603','distributor ignition coil and distributor head stud and plate','2','.03 P'),('D30316','generator brush arm mounting stud','1','.02 P'),('W–C153','ignition battery','4','.10 P'),('D30370','ignition switch ammeter terminal (left)','1','.02 P'),('D30057','ignition switch terminal (between ammeter and switch handle\n  stud)','1','.01 P'),('D30055','ignition switch terminal (between switch handle stud)','1','.01 P'),('W–O511','starting and lighting battery, top','4','.15 P'),('W—','starting and lighting battery negative terminal','2','.10 P'),('W—','starting and lighting battery positive terminal','2','.10 P')]:
 entry(r,'CONNECTOR, '+text,note='&',mfr=mfr,qty=qty,price=price)
entry(r,'CONTAINER, cam shaft driving shaft lower bearing',note='&',mfr='C8070',ord='LQ97A',qty='2',price='5.25')
entry(r,'CONTAINER, generator driving shaft upper ball bearing',note='&',ident='8154',plate='16',mfr='B8154',ord='LQ392A',qty='1',price='1.25')

r=start(71)
assembly(r,'CONTAINER, spare parts, assembly','4.70',note='&')
component(r,'*one SH286A spare parts CONTAINER (1)',price='4.50')
pieces(r,'''two SH286C spare parts container SUPPORT,
four —          RIVET, button head, ¼″ x 11/16″.)''')
assembly(r,'CONTROL, front, assembly','261.06',note='')
pieces(r,'''eight M771     brake connecting LINK,
one M764A    brake PEDAL,
one SH98D    brake pedal SPRING,
one SH98C    brake spring CLIP,
one —            clutch connecting ROD, front, assembly,
one —            clutch lever STOP, assembly,
one M772       clutch operating LEVER,
one M752       control GATE, left,
one M751       control GATE, right,
two M749       control lever LOCK,
two —            control lever lock PIN, assembly,
two M753       control lever SPRING,
eight M569C  control rod fork END,
two —            control spring adjusting EYEBOLT, assembly,
one M786       driver’s seat support PLATE, left,
one M787       driver’s seat support PLATE, right,
one M765       foot brake BRIDLE,
one SH98B     (foot brake) bridle CLIP,
one M766       foot brake bridle distance PIECE,
two M769       foot brake LINK,
one M770       foot brake suspension LINK,
one M795       foot brake suspension link SLEEVE,
eight (M568C) fork end PIN, length 1 9/16″, assembly,
eight (M568A) fork end PIN, length 1⅞″, assembly,
two (M568B)  fork end PIN, length 2¼″, assembly,
three —           front control connecting ROD, assembly,
one M747        front control lever FULCRUM, left,
one M746        front control lever FULCRUM, right,
four M784       front control swing LINK,
one —             front control swing link SHAFT, assembly,
one —             fulcrum SHAFT, assembly,
one —             high and low speed control LEVER, left, assembly,''')

r=start(72)
entry(r,'CONTROL, front, assembly—Continued.');composed(r)
pieces(r,'''one —            high and low speed control LEVER, right, assembly,
one M759       high speed selector LEVER, left,
one M758       high speed selector LEVER, right,
three —          joint PIN, assembly,
two M763       low speed brake LINK,
two —            low speed brake suspension LINK, assembly,
two M762       low speed connecting LINK,
one M756       low speed selector LEVER, left,
one M757       low speed selector LEVER, right,
one M779       reverse lever QUADRANT,
one —            reverse operating LEVER, assembly,
two M781       reverse quadrant distance PIECE,
four —           selector lever STOP, assembly,
one M785       spring anchor ANGLE,
four M775      spring link distance PIECE,
two —            BOLT, U. S. Std., hexagon head, ⅜″ x 2¼″, with plain~                      nut and lock washer,
eight —          BOLT, U. S. Std., hexagon head, ½″ x 1¼″, with plain~                      nut and lock washer,
four —           BOLT, U. S. Std., hexagon head, ½″ x 1⅜″, with plain~                      nut and lock washer,
two —            BOLT, U. S. Std., hexagon head, ½″ x 3½″, with plain~                      nut and lock washer,
two —            BOLT, U. S. Std., hexagon head, ½″ x 6¾″, with plain~                      nut and lock washer,
two —            BOLT, U. S. Std., hexagon head, ½″ x 7¼″, with plain~                      nut and lock washer.)''')
assembly(r,'CONTROL, rear, assembly','$41.54',note='&')
component(r,'four M4137 brake gear spring WASHER, large,')

r=start(73)
pieces(r,'''two M4132 foot brake horizontal LEVER,
one M4133 low speed brake horizontal LEVER, left,
one M4134 low speed brake horizontal LEVER, right,
one —         rear control CHANNEL, assembly.)''')
assembly(r,'CORE, radiator, front, assembly','124.11 P',note='&')
component(r,'*one SH611A radiator tank intermediate tube PLATE (front)',price='6.50')
entry(r,'three hundred } SH607C radiator TUBE,\n      and three }')
r[-1]['item_layout']=[dict(text='three hundred\n      and three',x=0,width=47),dict(text='}',x=47,y=.5,width=6),dict(text='SH607C radiator TUBE,',x=53,y=.5,width=180)]
component(r,'*one SH606A radiator tube PLATE, right (front).)',price='5.50')
assembly(r,'CORE, radiator, rear, assembly','124.11 P',note='&')
component(r,'*one                 SH611B radiator tank intermediate tube PLATE (rear) (1).',price='6.50')
component(r,'{three hundred } SH607C radiator TUBE,\n    and three }')
r[-1]['item_layout']=[dict(text='{three hundred\n    and three',x=28,width=49),dict(text='}',x=77,y=.5,width=6),dict(text='SH607C radiator TUBE,',x=83,y=.5,width=164)]
component(r,'*one                 SH606B radiator tube PLATE, left (rear) (1).)',price='5.50')
entry(r,'COUNTERWEIGHT, 7½″ ball mount',note='%X',ord='SH711B',qty='5',price='11.70')
entry(r,'COUPLING, clutch',note='&',ident='12',plate='21',ord='SH945A',qty='1',price='35.50')
for mfr,text,price in [('P59','distance recorder cable end','.22 P'),('P27','distance recorder cable end','.25 P'),('P299','distance recorder end, large','.25 P'),('P333','distance recorder end, small','.25 P')]:
 entry(r,'COUPLING, '+text,note='&',mfr=mfr,ord='586',qty='1',price=price)
entry(r,'COUPLING, M. I., ½″. (For combination valve to flexible tube connection (1).)',note='(pf)&',ord='Q52SA',qty='1',price='.06 P')
entry(r,'COUPLING, pipe, ⅛″. (For cover M264 (2); ventilating fan, assembly (2);\n  tube C8013 (1).)',note='%(pf) X',ord='Q52PA',qty='5',price='.04 P')
entry(r,'COUPLING, pipe, 2½″. (For pipes SH140H and SH140L (1).)',note='%(pf) X',ord='Q52AB',qty='2',price='.12 P')
entry(r,'COUPLING, soldering, 29/64″–28. (For tube C8012 (1); tube C8015 (1).)',note='X',ord='B101958A',qty='4')
entry(r,'COUPLING, soldering, ½″–14 pipe thread. (For tube SH981A (2); tube SH981B\n  (2); tube SH981C (2); tube SH984A (2); tube SH984B (2); tube SH984C (2);\n  tube SH984D (2).)',note='&',ord='B5932C',qty='14',price='.95 P')
entry(r,'COUPLING, soldering, 9/16″–24 SAE. (For tube SH981E (2); tube SH981F (1);\n  tube SH981G (2); tube C8011 (1); tube SH984E (1); tube SH984F (2).)',note='&',ord='B101363A',qty='15',price='.60 P')
entry(r,'COUPLING, soldering, 1″–16 U. S. F. (Titeflex type). (For tube SH207A (2);\n  tube SH207B (2).)',note='&',mfr='T–U12–13',qty='4',price='1.25 P')
entry(r,'COUPLING, soldering elbow, 9/16″–24 SAE (brass) (For tube SH981F (1); tube\n  SH982A (1); tube SH984E (1))',note='&',ord='B101364A',qty='3',price='.80 P')
entry(r,'COUPLING, transmission bevel pinion shaft flange',note='&',brit='M246',ord='704',qty='1',price='24.00');stacked(r,ident='67\n1',plate='22\n23')

r=add(74,'''&|||||SH976L|COUPLING, water pipe drain plug pipe (¼″, modified, ⅝″ long)|2|$0.02 P
%X||||M1038|197|COVER, air duct mud hole (between radiator and roof)|1|.88
%X|||||SH901F|COVER, air pressure pump air hole|1|.08''')
assembly(r,'COVER, cam shaft driving shaft lower bearing container, assembly','4.14',qty='(2)',note='&')
pieces(r,'''one LQ91A   cam shaft driving shaft housing packing NUT,
one LQ102A cam shaft driving shaft lower bearing container COVER,
one LQ90A   cam shaft driving shaft upper housing PACKING.)''')
entry(r,'COVER, cam shaft driving shaft lower bearing container',note='&',mfr='B8072',ord='LQ102A',qty='2',price='3.50')
entry(r,'COVER, cam shaft housing',note='&',ident='8095',plate='13',mfr='C8095',ord='LQ46A',qty='10',price='.82')
assembly(r,'COVER, cam shaft housing end, assembly','1.96',qty='(2)',note='&')
component(r,'one LQ57A cam shaft housing cover oil connection NUT,')
component(r,'*one LQ54A cam shaft housing end COVER (2)',price='1.37')
pieces(r,'''one LQ56A cam shaft housing end cover oil CONNECTION,
two —         GASKET, copper asbestos, ⅜″.)''')
entry(r,'COVER, cam shaft housing, flywheel end',note='&',ident='8467',plate='13',mfr='C8467',ord='LQ47A',qty='2',price='2.75')
assembly(r,'COVER, carburetor float, assembly','.99',qty='(2)',note='&')
pieces(r,'''one LQ532A carburetor float COVER,
one LQ534A carburetor float dust CAP,
two LQ535A carburetor float WEIGHT,
two LQ536A carburetor float weight AXLE,
one —           carburetor needle VALVE, assembly,
one —           WIRE, lock, brass, B. & S. Ga., No. 20 x 1¼″.)''')
entry(r,'COVER, carburetor float',note='&',mfr='13382',ord='LQ532A',qty='2',price='.50')
entry(r,'COVER, clutch coupling (half)',note='&',ident='27',plate='21',brit='M856',ord='870',qty='2',price='.80')
assembly(r,'COVER, crank case oil filler, assembly','.57',note='&')
component(r,'*one LQ219A crank case oil filler COVER (1)',ident='8129',plate='14',price='.45')

r=start(75)
pieces(r,'''one LQ220A crank case oil filler cover SPRING,
two LQ221A PIN, escutcheon, No. 13 x ⅜″.)''')
entry(r,'COVER, engine room removable plate hand hole (on left side)',note='%X',ord='SH363A',qty='1',price='10.25')
entry(r,'COVER, fan bevel gear box',note='%X',ident='11',plate='20',brit='M1124',ord='194',qty='1',price='.97')
entry(r,'COVER, fan bevel gear box side',note='%X',ord='SH146B',qty='2',price='.24')
for side,code,price in [('left','M1785','36.89'),('right','M1786','35.20')]:
 assembly(r,f'COVER, gasoline tank, {side}, assembly',price,note='&')
 component(r,'two M1789       door HINGE, female,')
 component(r,f'*one {code}      gasoline tank COVER, {side} (1)',ord='536',price='28.36')
 pieces(r,'''two SH537A    gasoline tank cover HINGE, male,
one —              gasoline tank cover LOCK, assembly,
one H20/21195 gasoline tank cover lock WASHER,''')
 if side=='left':component(r,'one M1787       gasoline tank left cover STOP,')
 pieces(r,'''one J206/21067 HANDLE,
six —               RIVET, button head, ⅜″ x 1⅜″,
two —              RIVET, button head, ⅜″ x 1½″,''')
 component(r,('four' if side=='left' else 'one')+' —              RIVET, button head, 7/16″ x 1⅛″,')
 component(r,'five —              RIVET, button head, 7/16″ x 1⅝″.)')
assembly(r,'COVER, generator end, assembly','.90 P',note='%X',mfr='D13826')
pieces(r,'''*one D29838 generator end COVER (1),
one D30510 generator end cover INSULATOR,
one D13838 generator end cover OILER,
one D31239 generator end cover oiler WASHER,
one D30323 generator end cover oiler WICK,
one D30263 generator field coil long stud EYELET.)''')

r=start(76)
assembly(r,'COVER, ignition switch, with ammeter, assembly','$2.24 P',note='&',mfr='D13817')
pieces(r,'''*one D6061  ignition switch AMMETER,
*one D29687 ignition switch COVER,
three D24247 RIVET, button head, .078″ x .156″.)''')
entry(r,'COVER, lower crack case sump',note='%X',ident='32',plate='14',mfr='B8129',ord='LQ200A',qty='1',price='1.50')
entry(r,'COVER, oil pump lower half body',note='%X',plate='33',mfr='B8381',ord='LQ453A',qty='1',price='3.00')
entry(r,'COVER, periscope hole. (On outlook turret (2); driver’s turret (1); roof door (1).)',note='%X',brit='M2409',ord='438',qty='4',price='.98')
entry(r,'COVER, radiator cooling fan ball race',note='%X',ord='SH281A',qty='1',price='.34')
entry(r,'COVER, radiator cooling fan driving pulley (leather belting, .2″ single ply, 3⅛″\n  wide, length 32 11/16″)',note='&',ord='SH233B',qty='1',price='2.25 P')
entry(r,'COVER, radiator cooling fan pulley (leather, .2″ x 3⅛″ x 26⅜″, single ply)',note='&',ord='SH233D',qty='1',price='1.98 P')
entry(r,'COVER, sponson hole, bottom',note='*',brit='M2628',ord='642',qty='(2)',price='3.00')
entry(r,'COVER, starting and lighting battery jar (hard rubber)',note='&',mfr='W–C154',qty='6',price='.23 P')
assembly(r,'COVER, sponson periscope hole, assembly','.46',qty='(2)',note='&')
component(r,'*one SH438D periscope hole cover lever locking LUG (6)',price='.05')
component(r,'one SH438C periscope lever RING,')
component(r,'*one M2769   sponson periscope hole COVER (2)',ord='490',price='.32')
component(r,'one —          RIVET, button head, 5/16″ x ⅝″.)')
entry(r,'COVER, starting crank housing',note='&',ord='SH399A',qty='1',price='3.88')
assembly(r,'COVER, terminal, assembly','.88 P',qty='(3)')
pieces(r,'''two SH922A terminal cover END,
two SH922B terminal cover SPRING,
one SH922C terminal cover TUBE,
four —          PIN, steel, ⅛″ x 5/16″.)''')
entry(r,'COVER, transmission bevel gear case, assembly',note='&',qty='(1)',price='82.30');stacked(r,ident='59\n10',plate='22\n23');composed(r)

r=start(77)
component(r,'*one M264     transmission bevel gear case COVER (1)',ord='671',price='80.00')
pieces(r,'''four (MX25) STUD, ½″ x 2 17/32″, threaded U. S. Std. 1″ and S. A. E. ⅞″,~                    assembly,
two (MX98) STUD, ½″ x 2⅞″, threaded U. S. Std. 1″ and S. A. E. ⅞″,~                    assembly,
two M300     DOWEL, bronze, ⅝″ x ½″.)''')
entry(r,'COVER, transmission mechanical lubricator',note='&',ord='SH105A',qty='1',price='.48')
entry(r,'COVER, transmission sprocket bearing cap oil box',note='%X',brit='M295',ord='713',qty='4',price='.68')
entry(r,'COVER, unilet, rectangular blank, 1″. (For 1″ x 1″ x 1″ type T unilet)',note='%(ee) X',qty='1',price='.08 P')
entry(r,'COVER, unilet, 2 holes. (For 1½″ type L unilet)',note='(ee)&',qty='1',price='.18 P')
entry(r,'COVER, water pump',note='&',ident='12435',plate='17',mfr='12435',ord='LQ150A',qty='1',price='3.45')
assembly(r,'CRADLE, 9″ ball mount gun, assembly','16.29',qty='(5)',note='%(c) X')
pieces(r,'''one B39A      9″ ball mount gun CRADLE,
two (B33N) 9″ ball mount gun cradle set SCREW, assembly,
one B33L      9″ ball mount key stop SCREW,
one B33A      9″ ball mount trunnion PIN.)''')
entry(r,'CRADLE, 9″ ball mount gun (1–52)',note='%(c) X',ord='B39A',qty='5',price='15.98')
entry(r,'CRANK, bell, clutch throwout stop',note='&',ord='SH87A',qty='1',price='2.08')
assembly(r,'CRANK, starting, assembly','4.07',note='&')
pieces(r,'''one SH67B starting crank LEVER,
one SH65G starting crank lever HANDLE,
one SH66D starting crank lever handle GRIP.)''')
entry(r,'CROSS, plain, ¼″ (MI). (For tube C8015 (1))',note='%(pf) X',ord='Q51EA',qty='1',price='.05 P')
entry(r,'CUP, crank shaft thrust bearing oil',note='%X',mfr='8390',ord='LQ242A',qty='1',price='.12 P')
assembly(r,'CUP, distributor, assembly','8.13 P',qty='(2)',note='&',mfr='D14180')
component(r,'four {N. D. 1200} BEARING, ball, radial, dia. 1.1811″, bore .3937″, face\n       {or equal}       .3543″,')
r[-1]['item_layout']=[dict(text='four',x=28,y=.5,width=16),dict(text='{N. D. 1200}\n{or equal}',x=44,width=45),dict(text='BEARING, ball, radial, dia. 1.1811″, bore .3937″, face\n    .3543″,',x=89,width=158)]
pieces(r,'''one D29734     ball bearing retaining NUT,
one D29609     ball bearing spacing SLEEVE,
two (D29896) distributor advance lever attaching STUD, assembly,
one D14181     distributor condenser and breaker PLATE, with contact~                       arm stud, assembly,
three (D29874) distributor condenser and breaker plate attaching STUD,~                       assembly,
one (D29595)  distributor condenser and breaker plate STUD, assembly,
*one D29730    distributor connector PLATE (2),''')

r=start(78)
entry(r,'CUP, distributor, assembly—Continued.',note='&',mfr='D14180');composed(r)
pieces(r,'''one D29729     distributor connector plate INSULATOR,
two D29630    distributor connector plate screw insulating BUSHING,
*one D29787    distributor CUP (2),
four (D30536) distributor cup STUD, assembly,
three —           PIN, split, brass, 1/16″ x ⅜″,
two D29598    SCREW, slotted head No. 8–32 x .391″,
two D26441    WASHER, plain, .173″ x .344″ x .025″.)''')
entry(r,'CUP, governor ball',note='&X',ord='SH987B',qty='1',price='$1.52')
entry(r,'CUP, governor thrust bearing',note='&',ord='SH143A',qty='1',price='.68 P')
entry(r,'CUP, grease, No. 0 x ⅛″. (For cover M264 (2); ventilating fan, assembly (2))',note='%(mh) X',qty='4',price='.07 P')
entry(r,'CUP, grease, No. 4 x ½″. (For housing M250 (1))',note='%(mh) X',qty='1',price='1.60 P')
entry(r,'CUP, priming, No. 00 x ⅛″, lever handle. (For liberty engine)',note='%(mh) X',mfr='(8009)',qty='12',price='.12 P')
entry(r,'CUP, roller bearing, dia. 2.8593″, width 15/16″',note='(c)&',qty='4',price='.90 P');stacked(r,mfr='Timken 312 or\n  equal.')
entry(r,'CUP, roller bearing, dia. 5.875″, width 1¾″',note='(c)&',qty='2',price='3.30 P');stacked(r,mfr='Timken 6420 or\n  equal.')
entry(r,'CUP, tachometer drive shaft oil, assembly',note='%(b) X',mfr='D13974',qty='(1)',price='.11 P')
r[-1]['space_after']=1
entry(r,'CUTOUT, single pole (auto fiber 1 to 50 volts, 20 amperes)',note='%(ee) X',ord='31–37–2T',qty='4',price='.30 P')
assembly(r,'CYLINDER, assembly','24.81',qty='(12)',note='&')
component(r,'*one LQ281A cylinder BARREL (12)',mfr='8098',price='15.00')
component(r,'*one LQ65D  cylinder elbow BRACE (12)',price='.05')
component(r,'*two LQ284A cylinder elbow FLANGE (24)',mfr='8030',price='.50')
component(r,'*one LQ282A cylinder exhaust ELBOW (12)',mfr='8031',price='2.50')
component(r,'*one LQ283A cylinder inlet ELBOW (12)',mfr='8032',price='2.50')
component(r,'*one LQ290A cylinder water inlet PIPE (12)',price='.25')
component(r,'*one LQ291A cylinder water outlet PIPE (12)',price='.20')

r=start(79)
component(r,'*one LQ286A cylinder water JACKET, inlet half (12)',mfr='8099',price='.60')
component(r,'*one LQ287A cylinder water JACKET, outlet half (12)',mfr='8359',price='.60')
pieces(r,'''one (LQ301A) STUD, 5/16″ x 2½″, threaded U. S. Std. ½″ and S. A. E.~                     ⅝″, assembly,
one LQ302A  STUD, 5/16″ x 4⅜″, threaded U. S. Std. ½″ and S. A. E.~                     ⅝″, assembly,
two LQ303A STUD, ⅜″ x 1 7/16″, threaded U. S. Std. 13/32″ and S. A. E.~                     ⅝″, assembly,
two (LQ304A) STUD, ⅜″ x 1 17/32″, threaded S. A. E. 13/32″ and 21/32″, assembly,
one LQ289A valve stem GUIDE, exhaust,
one LQ288A valve stem GUIDE, inlet,
two LQ52A   WASHER, special, 5/16″,
four LQ166A WASHER, special, ⅜″.)''')
assembly(r,'CYLINDER, with valves and piston, assembly','45.43',qty='(12)',note='(gaf)&')
pieces(r,'''one — CYLINDER, with valves, assembly,
one — PISTON, assembly.)''')
assembly(r,'CYLINDER, with valves, assembly','32.88',qty='(12)',note='&',ident='8385',plate='15')
pieces(r,'''one —          CYLINDER, assembly,
two LQ292A (inlet or exhaust) VALVE,
one LQ295A valve SPRING, exhaust, outside,
one LQ294A valve SPRING, inlet, outside,
two LQ293A valve SPRING, inside,
two LQ297A valve spring COLLAR, lower,
two LQ296A valve spring COLLAR, upper,
four LQ298A valve spring collar KEY.)''')
entry(r,'CYLINDER, air pressure pump',note='&',ident='2',plate='5',ord='SH900C',qty='4',price='1.48')
for brit,ord,text,qty,price in [('M2055','338','No. 2','(2)','6.60'),('M2056B','338','No. 3, left','(1)','6.48'),('M2056A','338','No. 3, right','(1)','6.48'),('M2057B','338','No. 4 and 6, left','(2)','6.48'),('M2057A','338','No. 4 and 6, right','(2)','6.48'),('M2173B','338','No. 5, left','(1)','6.48'),('M2173A','338','No. 5, right','(1)','6.48'),('M2058B','339','No. 7, left','(1)','6.48'),('M2058A','339','No. 7, right','(1)','6.48'),('M2059B','339','No. 8, left','(1)','6.48'),('M2059A','339','No. 8, right','(1)','6.48')]:
 entry(r,'DIAPHRAGM, '+text,note='*',brit=brit,ord=ord,qty=qty,price=price)

def engine_door(r,side,code):
 assembly(r,f'DOOR, engine room (sliding), {side}, assembly','13.95',note='&')
 component(r,'one M2151     door HANDLE,')
 component(r,f'*one {code} engine room (sliding) DOOR, {side} (1)',ord='363',price='8.50')
 pieces(r,'''one M2154     engine room sliding door catch BEARING,
two M2147    engine room sliding door roller BRACKET,
one M2164     machine gunner’s seat CATCH,
one —            machine gunner’s seat PLATE, assembly,
six —             RIVET, button head, ¼″ x ⅞″,
two —            RIVET, button head, 5/16″ x 1″,
two —            RIVET, button head, ⅜″ x 1⅛″,
four —           RIVET, button head, 7/16″ x 1⅜″.)''')

r=add(80,'''*||||M2071B|339|DIAPHRAGM, No. 9, left|(1)|$6.75
*||||M2071A|339|DIAPHRAGM, No. 9, right|(1)|6.75
&|16|22||M286|680|DISK, large plant pinion|2|35.00
&||||X267|802|DISK, semaphore register|1|1.08
&|||||SH964C|DISK, spark and throttle control lever friction|2|1.75''')
entry(r,'DISK, transmission pinion shaft bearing housing packing',note='&',brit='M252',ord='703',qty='1',price='1.56');stacked(r,ident='5\n64',plate='23\n22')
entry(r,'DISK, transmission small spur ring',note='&',ident='31',plate='22',brit='M276',ord='676',qty='2',price='51.00')
entry(r,'DISTRIBUTOR, assembly',note='&',mfr='D5180',qty='(2)',price='35.18 P');stacked(r,ident='12229\n10',plate='15\n14');composed(r)
pieces(r,'''one —            distributor adapter BASE, with cup, assembly,
two D29899 distributor advance LEVER,
one D14181  distributor condenser breaker PLATE, with contact arm~                    stud, assembly,
one D13725  distributor HEAD, assembly,
twelve D31698 distributor head high tension terminal NUT,
twelve D20241 WASHER, lock, .195″ x .33″ x .046″.)''')
engine_door(r,'left','M2146B')

r=start(81)
engine_door(r,'right','M2146A')
assembly(r,'DOOR, ignition inspection, assembly','3.69',note='&')
component(r,'*one M2167A ignition inspection DOOR (1)',ord='370',price='2.70')
pieces(r,'''two M2151     door HANDLE,
two —            RIVET, button head, 3/16″ x ⅞″,''')
component(r,'*one M2167B WIRE, steel, 3/16″ x 92⅝″.)',ord='370',price='.01 P')
assembly(r,'DOOR, outside tool chest, assembly','19.55',note='&')
component(r,'one C114E      door HANDLE,')
component(r,'three GB3L    door HINGE, female,')
component(r,'*one SH583B outside tool chest DOOR (1)',price='2.36')
pieces(r,'''two GB5K    STAPLE,
one —           CHAIN, standard, No. 1, assembly,
one —           PADLOCK, No. 840, with standard chain No. 1, assembly,
nine —          RIVET, button head, ¼″ x ¾″,
four —          RIVET, button head, ¼″ x ⅞″,
four —          WASHER, plain, ¼″.)''')
assembly(r,'DOOR, main turret roof, left, assembly','16.74')
pieces(r,'''two M1790 door HINGE, male,
one M2357 main turret roof door apron PLATE,''')
component(r,'*one M2356 main turret roof door PLATE, left (1)',ident='7',plate='9',ord='410',price='12.89')
pieces(r,'''four —          RIVET, button head, 3/16″ x 1⅜″,
six —            RIVET, button head, 7/16″ x 1 7/16″.)''')

def side_door_rivets(r):
 pieces(r,'''eighteen —   RIVET, button head, 3/16″ x 1″,
eight —        RIVET, button head, ⅜″ x 1⅝″,
four —         RIVET, button head, 9/16″ x 2″,
four —         RIVET, button head, 9/16″ x 2⅜″,
four —         RIVET, button head, 9/16″ x 2½″,
two —          RIVET, button head, 11/16″ x 2⅝″,
four —         RIVET, button head, 11/16″ x 3″.)''')

r=start(82)
assembly(r,'DOOR, main turret roof, right, assembly','$17.80')
component(r,'two M1790       door HINGE, male,')
component(r,'*one M2355      main turret roof door PLATE, right (1)',ident='6',plate='9',ord='410',price='12.89')
pieces(r,'''one M45/21421 turret roof door chubb LOCK, with three keys,
one M2414       turret roof door PLATE,
four —             RIVET, button head, ¼″ x ⅞″,
six —               RIVET, button head, 7/16″ x 1 7/16″.)''')
assembly(r,'DOOR, side, left, assembly','258.43')
pieces(r,'''two —            door LOCK, left, assembly,
two SH544A fire extinguisher BRACKET,
one SH544B fire extinguisher BRACKET, w/bottom cut off,''')
component(r,'*one M3120   hemispherical turret cover PLATE (3)',ident='5',plate='9',ord='431',price='55.75')
component(r,'*one M704     side DOOR, lower part, left (1)',ord='542',price='127.00')
component(r,'*one M702     side DOOR, upper part, left (1)',ord='543',price='56.69')
component(r,'*two M709     side door butt STRAP (4)',price='.89')
component(r,'*one M708     side door CLIP',price='.41')
component(r,'two M706      side door HINGE,');side_door_rivets(r)
assembly(r,'DOOR, side, right, assembly','258.43')
pieces(r,'''two —            door LOCK, right, assembly,
two SH544A fire extinguisher BRACKET,''')

r=start(83)
component(r,'one SH544B fire extinguisher BRACKET, w/bottom cut off,')
component(r,'*one M3120   hemispherical turret cover PLATE (3)',ident='5',plate='9',ord='431',price='55.75')
component(r,'*one M705     side DOOR, lower part, right (1)',price='127.00')
component(r,'*one M703     side DOOR, upper part, right (1)',price='56.69')
component(r,'*two M709     side door butt STRAP (4)',price='.89')
component(r,'*two M708     side door CLIP (4)',price='.41')
component(r,'two M706      side door HINGE,');side_door_rivets(r)
entry(r,'DOWEL, bronze, ⅝″ x ½″. (For cap M266 (1); cover M264 (2); bushing M296\n                          (1); bushing M299 (1).)',note='&',ident='4',plate='22',brit='M300',ord='713',qty='8',price='.08')
entry(r,'DOWEL, connecting-rod crank shaft bearing',note='&',mfr='8028',ord='LQ129A',qty='12',price='.02')
entry(r,'DOWEL, crank shaft bearing',note='&',ident='26',plate='14',mfr='8018',ord='LQ194A',qty='14',price='.05')
entry(r,'DOWEL, hand starter (housing)',note='&',ord='SH65F',qty='2',price='.03')
entry(r,'DOWEL, 3/16″ x ⅜″. (For housing LQ162A (1); body LQ427A (1).)',note='&',ident='174',plate='19',mfr='174',ord='LQ163A',qty='2',price='.01')
assembly(r,'DRIVE, distance recorder (Johns-Manville Co. type), assembly','6.23 P',note='%(gy) X')
pieces(r,'''one S30A    distance recorder drive cable SHAFT, with gear,
one S23      distance recorder drive cable shaft INSERT,''')
component(r,'*one S374F distance recorder drive HOUSING (1)',price='1.00')
pieces(r,'''one S34      distance recorder drive housing CAP,
one S114    distance recorder drive PINION,
one S11      distance recorder drive pinion NUT,
one S372A distance recorder drive pinion SHAFT, with gear,
one S375    distance recorder drive pinion shaft BEARING,
one S4040  distance recorder drive pinion shaft WASHER,
one S10      distance recorder drive pinion WASHER,
two S35      distance recorder drive shaft WASHER.)''')
entry(r,'DRIVER, water pump bevel',note='&',ident='40',plate='14',mfr='C8077',ord='LQ156A',qty='1',price='6.98')
entry(r,'DRUM, clutch',note='&',ident='2',plate='21',ord='SH866A',qty='1',price='8.76')
entry(r,'DRUM, clutch stop',note='&',ident='16',plate='21',brit='M858',ord='870',qty='1',price='5.25')
entry(r,'DRUM, track brake',note='&',ident='7',plate='22',brit='M292',ord='691',qty='2',price='78.00')
entry(r,'DRUM, transmission high speed brake',note='&',ident='42',plate='22',brit='M269',ord='699',qty='2',price='26.00')

r=start(84)
assembly(r,'DUCT, air (between radiator and roof), assembly','$20.13')
component(r,'*one M1036   air DUCT (1)',ord='156',price='17.28')
pieces(r,'''one M1038   air duct mud hole COVER,
one M1039   air duct mud hole JOINT,
one M1036A air duct mud hole RING,
eight —         SCREW, cap, U. S. Std., hexagon head, ⅜″ x ¾″,
eight —         WASHER, lock, ⅜″.)''')
entry(r,'DUCT, ventilating inlet fan',note='%X',ident='26',plate='2',brit='M1054',ord='186',qty='1',price='10.71')
entry(r,'EAR, low speed brake band',note='&',brit='MX48',ord='683',qty='4',price='1.08')
entry(r,'EAR, track brake band',note='&',brit='MX46',ord='693',qty='4',price='1.08')
entry(r,'ECCENTRIC, transmission mechanical lubricator',note='&',ord='SH101L',qty='6',price='.08')
entry(r,'ECCENTRIC, transmission mechanical lubricator force feed',note='&',ord='SH102G',qty='6',price='.25')
entry(r,'ELBOW, (engine) oil tank suction oil tube',note='%X',ord='SH207F',qty='1',price='.50 P')
entry(r,'ELBOW, (exhaust) (flanged) connection',note='%X',ident='3',plate='4',ord='SH402',qty='2',price='5.00 P')
assembly(r,'ELBOW, exhaust manifold guard, inner, assembly','3.28')
component(r,'*one SH153S exhaust manifold BAND, bottom, inner (2)',price='.08')
component(r,'*one SH153N exhaust manifold BAND, bottom (with holes) (1)',price='.18')
component(r,'*one SH153K exhaust manifold BAND, top and bottom (without holes)\n                    (2)',price='.18')
component(r,'*one SH153H exhaust manifold BAND, top and bottom (with holes) (2)',price='.18')
component(r,'*one SH154K exhaust manifold elbow COVER (2)',price='.50')
component(r,'*two SH153Z exhaust manifold guard band CLIP, inner (4)',price='.05')
component(r,'*one SH153C exhaust manifold guard inside connecting STRAP, long\n                    (2)',price='.20')
component(r,'*one SH153B exhaust manifold guard outside connecting STRAP, long\n                    (without holes) (1)',price='.30')
component(r,'*one SH153E exhaust manifold guard outside connecting STRAP, small\n                    (without holes) (1)',price='.18')

assert sorted(TABLES)==list(range(65,85))
