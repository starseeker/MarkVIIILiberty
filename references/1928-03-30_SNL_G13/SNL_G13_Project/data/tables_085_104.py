"""Source-led transcription of photographed pages 85–104.

Original page breaks, blank fields and source inconsistencies are retained.
See review.json for uncertain readings and cross-page evidence.
"""
from .parts_tables import row
from .opening_tables import entry, component, composed
from .tables_045_064 import assembly
from .tables_065_084 import pieces, stacked
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

r=start(85)
component(r,'*three SH153F exhaust manifold guard inside connecting STRAP, small\n                     (6)',price='.05')
component(r,'two SH153X exhaust manifold guard pipe CLAMP,')
component(r,'*one SH154N exhaust pipe COVER (2)',price='.70')
pieces(r,'''twenty-five — RIVET, button head, 3/16″ x ½″,
eight —          RIVET, button head, 3/16″ x ⅝″,
four —           RIVET, button head, 3/16″ x ¾″.)''')
assembly(r,'ELBOW, exhaust manifold guard, outer assembly','3.70')
for text,price in [
 ('*one SH153S exhaust manifold BAND, bottom, inner (2)','.08'),
 ('*one SH153M exhaust manifold BAND, bottom (with holes) (1)','.18'),
 ('*one SH153H exhaust manifold BAND, top and bottom (with holes) (2)','.18'),
 ('*one SH153K exhaust manifold BAND, top and bottom (without holes)\n                    (2)','.18'),
 ('*one SH154K exhaust manifold elbow COVER (2)','.50'),
 ('*two SH153Z exhaust manifold guard band CLIP, inner (4)','.05'),
 ('*three SH153T exhaust manifold guard connecting CLIP (3)','.06'),
 ('*one SH153C exhaust manifold guard inside connecting STRAP, long (2)','.20'),
 ('*three SH153F exhaust manifold guard inside connecting STRAP, small\n                     (6)','.05'),
 ('*one SH153A exhaust manifold guard outside connecting STRAP, long\n                    (1)','.30'),
 ('*one SH153D exhaust manifold guard outside connecting STRAP, small\n                    (with hole) (1)','.18')]:component(r,text,price=price)
component(r,'two SH153X exhaust manifold guard pipe CLAMP,')
component(r,'*four SH153G exhaust manifold guard strap CLAMP (4)',price='.06 P')
component(r,'*one SH154N exhaust pipe COVER (2)',price='.70')
pieces(r,'''twenty-five — RIVET, button head, 3/16″ x ½″,
eight —          RIVET, button head, 3/16″ x ⅝″,
four —           RIVET, button head, 3/16″ x ¾″.)''')
assembly(r,'ELBOW, intake header water inlet, assembly','.49',qty='(12)',note='&')
component(r,'*one LQ309A FLANGE, ¾″ tube (12)',mfr='8171',price='.44')
component(r,'*one LQ308A intake header water inlet ELBOW (12).)',mfr='8170',price='.05')
entry(r,'ELBOW, M. I., 45°, beaded, ½″. (For housing M250 (1).)',note='(pf)&',ord='Q51QD',qty='1',price='.08 P')
entry(r,'ELBOW, M. I., 45°, beaded, ¾″. (For pipe M1229 (1).)',note='(pf)&',ident='—',plate='24',ord='Q51DD',qty='1',price='.10 P')
entry(r,'ELBOW, M. I., 90°, beaded, ¼″. (For combination valve to flexible tube con-\n  nection, assembly (2).)',note='(pf)&',ord='Q51QC',qty='2',price='.04 P')

r=add(86,'''%(pf) X|||||Q51SC|ELBOW, M. I., 90°, beaded, ½″. (For pipe SH199C (1); combination valve to~  flexible tube connection, assembly (2).)|3|$0.08 P
%(pf) X|—|24|||Q51RD|ELBOW, M. I., 90°, beaded, ¾″. (For pipe M1229 (2).)|2|.10 P
(pf)&|—|24|||Q51WC|ELBOW, M. I., 90°, beaded, 1″. (For pipe M1229 (2).)|2|.09 P
(pf)&|||||Q51MC|ELBOW, M. I., 90°, beaded, 2″. (For pipe SH199F (1).)|1|.32 P
%(pf) X|||||Q51CC|ELBOW, plain, ⅛″ pipe thread (M. I.). (For ventilating fan, assembly (1)~  Tube C8014A (1); tube C8014B (1); Tube C8014C (1); tube C8016 (1).)|5|.03 P
%X|||||SH664A|ELBOW, pipe, ¼″ (Herring Motor Co. type, No. 69F). (For cap M298 (1); cap~  M294 (1).)|4|.04
%X|||||SH976W|ELBOW, radiator drain pipe (Std. 90°, ½″ modified)|1|.09 P
(pf)&|||||Q51PE|ELBOW, street, M. I., 45°, ½″. (For combination valve to flexible tube con-~  nection, assembly (1).)|1|.08 P
%(mh)|||||Q51AE|ELBOW, street, ⅛″, (M. I.), 90°. (For hand pressure pump (1).)|1|
%(pf) X|||||Q51BE|ELBOW, street, M. I., 90°, ¼″. (For pipe SH976E (1); regulating tank flexible~  tube connection, assembly (2).)|4|.04 P
%(pf) X|||||Q51DE|ELBOW, street, M. I., 90° ½″. (For combination valve to flexible tube connec-~  tion, assembly (2); pipe SH976K (1).)|3|.08 P
&||||||ELECTROLITE, 1.255 S. G., qt. (1 quart required for starting and lighting bat-~  tery; approximately ½ pint required for battery.)|—|.60 P
%(mh) X|—|12|||967|END, adjustable yoke rod, S. A. E., 5/16″. (For control rods.)|2|.10 P
%(mh) X|—|12|||967|END, adjustable yoke rod, S. A. E., ⅜″. (For control rods.)|5|.12 P
%(mh) X|—|12|||967|END, adjustable yoke rod, S. A. E., ½″. (For control rods.)|12|.16 P''')
assembly(r,'END, carburetor throttle shaft yoke, assembly','1.27',qty='(4)')
component(r,'*one LQ554A carburetor throttle shaft yoke END (4)',mfr='13414',price='.85')
pieces(r,'''two —           carburetor throttle shaft yoke end BOLT, assembly,
two LQ557A carburetor throttle shaft yoke end SCREW.)''')
entry(r,'END, control rod fork. (For (2) rods M576 (1).)',note='%X',ord='SH946F',qty='2',price='.25 P')
entry(r,'END, control rod fork. (For rod M789A (2); rod M789B (2); rod M581 (1);\n  rod M574 (2); rod M573 (2); rod M575 (1); rod M579 (2); rod M578 (2);\n  (3) rod M576 (2); rod SH946D (2); rod SH229A (2).)',note='%X',ident='M569',plate='6',brit='M569C',ord='946',qty='41',price='.25 P')

r=add(87,'''%X|||||SH953E|END, control rod fork. (For rod M581 (1); rod SH953D (2).)|3|.25 P
%X|M569|6||M569A|170|END, control rod fork, length 1″. (For rod SH946E (2).)|4|.25 P
%X|M569|6||M569B|170|END, control rod fork, length 1½″. (For band M575 (2).)|2|.25 P
%X|—|12|||SH993G|END, engine control spring rod|1|.30 P
%X|—|6||M570||END, fork. (For rod M571 (2); rod M566 (1).)|3|.25 P
&|||||B4024|END, funnel rack strap|1|.22
&|15|30||M361|699|END, high speed brake band anchor|2|2.58
%X|||||SH1021F|END, intensifier ball|24|.02 P''')
assembly(r,'END, platform ammunition storage fork, assembly','.49 P',qty='(2)')
component(r,'*one M3189 platform ammunition storage fork END (2)',ident='—',plate='6',ord='573',price='.25 P')
pieces(r,'''one —       NUT, plain, U. S. Std., hexagon, ⅝″,
one —       PIN, type A, .610″ x 2 3/16″, with two split pins,
one —       WASHER, lock, ⅝″.)''')
entry(r,'END, terminal cover',note='%X',ord='SH922A',qty='6',price='.22')
assembly(r,'ENGINE, Ordnance Liberty, (Trego, 5. x 7., 12 cylinders), assembly','3,128.99 P',note='(gw)&')
pieces(r,'''two —              cam shaft driving SHAFT, lower, with container, as-~                        sembly,
two —              cam shaft driving shaft bearing container COVER, as-~                        sembly,
two LQ98A      cam shaft driving shaft lower bearing container GASKET,
(gu) LQ101A    cam shaft driving shaft lower bearing container SHIM,~                        medium,
(gu) LQ100A    cam shaft driving shaft lower bearing container SHIM,~                        thick,
(gu) LQ99A      cam shaft driving shaft lower bearing container SHIM,~                        thin,
one —              cam shaft HOUSING, with cam shaft, left, assembly,
one —              cam shaft HOUSING, with cam shaft, right, assembly,
(gu) LQ504A    cam shaft housing cylinder SHIM, medium,
(gu) LQ505A    cam shaft housing cylinder, SHIM, thick,
(gu) LQ503A    cam shaft housing cylinder SHIM, thin,
two —              CARBURETOR (Zenith type, No. 52, modified), as-~                        sembly,
one —              carburetor throttle control connecting SHAFT, assembly,
one —              carburetor throttle control SHAFT, assembly,
one LQ108A     carburetor throttle control shaft BRACKET,
two (LQ114A) carburetor throttle control shaft bracket BOLT, assembly,''')

def engine_continued(r):
 entry(r,'ENGINE, Ordnance Liberty, (Trego, 5. x 7., 12 cylinders), assembly—Contd.',note='(gw)&');composed(r)

r=start(88);engine_continued(r)
pieces(r,'''one (LQ111A) carburetor throttle control shaft LEVER, assembly,
one LQ119A   carburetor throttle control tube end COLLAR, assembly,
two LQ424A  carburetor to intake header GASKET,
one LQ420A   carburetor to intake header SCREW, long,
one LQ419A   carburetor to intake header SCREW, short,
four LQ425A  carburetor to intake header UNION,
one —             crank CASE, with crank shaft and connecting rods,~                       assembly,
one LQ232A    crank case cover GASKET,
one —              crank case lower half oil sump STRAINER, assembly,
two —              crank case oil FILLER, assembly,
two LQ228A    crank case oil filler GASKET,
one —              crank case oil filler SCREEN, assembly,
one LQ464A    crank case oil tube union CONNECTION,
one LQ465A    crank case oil tube union connection GASKET,
two —              crank case to cam shaft housing oil TUBE, assembly,
twelve —          CYLINDER, with valves and piston, assembly,
four LQ250A    cylinder to crank case GASKET,
twenty-four LQ177A cylinder water HOSE,
two LQ168A    cylinder water inlet MANIFOLD,
one LQ172A    cylinder water inlet manifold EXTENSION, left,
one LQ170A    cylinder water inlet manifold EXTENSION, right,
one LQ174A    cylinder water inlet manifold left extension CLIP,
one LQ173A    cylinder water inlet manifold right extension CLIP,
two —              DISTRIBUTOR, assembly,
one —              distributor control connecting ROD, assembly,
two LQ312A    distributor to cam shaft housing GASKET,
twelve LQ306A exhaust header GASKET,
one SH868A    FLYWHEEL,''')

r=start(89)
pieces(r,'''one —              GENERATOR, assembly,
one —              generator drive SHAFT, assembly,
one LQ406A     generator driving shaft ball bearing container GASKET,
(gu) LQ405A    generator driving shaft ball bearing upper container~                        SHIM, medium,
(gu) LQ404A    generator driving shaft ball bearing upper container~                        SHIM, thick,
(gu) LQ403A    generator driving shaft ball bearing upper container~                        SHIM, thin,
one LQ251A     generator GASKET,
one LQ232A     governor to crank case GASKET,
one —              high tension cable TUBE, with cables, assembly,
one LQ416A     inlet header water outlet EXTENSION,
four —             intake HEADER, assembly,
twelve LQ411A intake header GASKET,
twelve —         intake header water inlet ELBOW, assembly,
one (LQ413A) intake header water OUTLET, double, assembly,
one LQ415A     intake header water OUTLET, single,
one LQ414A     intake header water outlet GASKET,
one LQ200A     lower crank case sump COVER,
one —              oil PUMP, assembly,
one LQ195A     oil pump body GASKET,
one SH993E     throttle release SPRING,
one (SH993C)  throttle release spring COLLAR, assembly,
one —              water PUMP, assembly,
one —              water pump bevel driver HOUSING, with driver,~                        assembly,
one LQ165A     water pump bevel driver housing SCREW,
(gu) LQ153A    water pump shaft bearing retainer SHIM, medium,
(gu) LQ152A    water pump shaft bearing retainer SHIM, thick,
(gu) LQ151A    water pump shaft bearing retainer SHIM, thin,
ten LQ164A     BOLT, S. A. E., drilled, ¼″ x 15/16″, threaded 9/16″, as-~                        sembly,
forty-eight LQ178A CLAMP, hose, 1 1/16″,
twelve —         CLAMP, hose, 1⅝″,
twelve LQ410A CUP, priming, No. 00 x ⅛″,
twelve LQ417A GASKET, flange, ¾″ tube,
six LQ175A      HOSE, rubber, 3 ply, I. D. 1⅜″, O. D. 1 9/16″, length 2⅝″,
twenty-four LQ299A PLUG, spark, with gasket,''')

r=start(90);engine_continued(r)
pieces(r,'''one LQ393A     SCREW, cap, U. S. Std., flat head, ¼″ x ¾″,
twenty-four LQ418A SCREW, special, 5/16″ x 11/16″,
two LQ52A      WASHER, special, 5/16″,
one LQ166A     WASHER, special, ⅜″,''')
component(r,'*two LQ512E WIRE, lock, soft iron, W. & M. Ga. No. 18 x 4″ (2)',price='$0.01')
component(r,'*thirteen LQ31A WIRE, lock, W. & M. Ga. No. 18 x 8″ (22)',mfr='177',price='.01')
component(r,'*two LQ167A WIRE, lock, W. & M. Ga. No. 18 x 10″ (6).)',mfr='L209',price='.01')
for cells in [
 dict(note='&',ident='12097',plate='15',mfr='C12097',ord='LQ172A',item='EXTENSION, cylinder water inlet manifold, left',qty='1',price='1.04'),
 dict(note='&',ident='12096',plate='15',mfr='C12096',ord='LQ170A',item='EXTENSION, cylinder water inlet manifold, right',qty='1',price='1.04'),
 dict(note='&',ident='5',plate='14',mfr='B12436',ord='LQ416A',item='EXTENSION, inlet header water outlet',qty='1',price='.95'),
 dict(note='%X',ord='B5877',item='EXTENSION, instrument board',qty='1',price='.48'),
 dict(note='&',ident='29',plate='14',mfr='8040',ord='LQ187A',item='EXTENSION, lower crank case oil pump suction tube',qty='1',price='.35'),
 dict(note='&',ord='SH963B',item='EXTENSION, ventilating fan (discharge) box, lower',qty='1',price='.70'),
 dict(note='&',ord='SH963A',item='EXTENSION, ventilating fan (discharge) box, upper',qty='1',price='5.35')]:r.append(row(**cells))
assembly(r,'EYEBOLT, clutch throwout stop rod, assembly','.94')
component(r,'*one M4156 clutch stop rod EYEBOLT (1)',ord='955',price='.82')
pieces(r,'''two SH955B clutch stop rod eyebolt NUT,
two SH955A clutch stop rod eyebolt WASHER,
two —           NUT, plain, U. S. Std., hexagon, ½″.)''')
assembly(r,'EYEBOLT, control spring adjusting, assembly','.92',qty='(2)')
component(r,'*one M754 control spring adjusting EYEBOLT (2)',ord='224',price='.88')
component(r,'two —       NUT, plain, U. S. Std., ½″.)')
entry(r,'EYEBOLT, driver’s turret flap',note='%X',brit='M2427',ord='412',qty='2',price='.32')
assembly(r,'EYEBOLT, platform ammunition storage, assembly','.48',qty='(2)')
component(r,'*one M3190 platform ammunition storage EYEBOLT (2)',ord='573',price='.45')

r=start(91)
component(r,'one —       NUT, pipe lock, ⅝″.)')
entry(r,'EYE, screw. (For exterior telephone head cord snap.)',note='&',ord='C65',qty='1',price='.03')
for code,text,qty,price in [('D29869','generator brush arm mounting','1','.03 P'),('D30263','generator field coil long stud','1','.02 P'),('D30367','voltage regulator housing','3','.02 P')]:entry(r,'EYELET, '+text,note='&',mfr=code,qty=qty,price=price)
assembly(r,'FAN, radiator cooling, with housing, assembly','163.95',note='&')
pieces(r,'''two SKF1308 BEARING, ball, radial, dia. 3.5433″, bore 1.5748″, height~                         .9055″,
one —              radiator cooling FAN, assembly,
one SH281A     radiator cooling fan ball race COVER,
one SH282B     radiator cooling fan ball race HOUSING,
two SH281B     radiator cooling fan ball race housing GASKET,
one SH279E     radiator cooling fan distance PIECE,
one SH281D     radiator cooling fan drive distance TUBE,
one —              radiator cooling fan HOUSING, assembly,
one SH281C     radiator cooling fan housing spider cover PLATE,
one SH279F     radiator cooling fan inside bearing oil PIPE,
one —              radiator cooling fan PULLEY, assembly,
one —              radiator cooling fan SPINDLE, assembly,
twenty-one — BOLT, U. S. Std., hexagon head, ⅜″ x ¾″, with plain~                        nut and lock washer,
six —              BOLT, U. S. Std., hexagon head, ⅜″ x 1″, with plain~                        nut and lock washer,
one —             BOLT, U. S. Std., hexagon head, ½″ x 1″, with plain~                        nut and lock washer,
one —             KEY, Woodruff, No. A,
one —             KEY, Woodruff, No. G,
eight —           SCREW, machine, round head, No. 14–20 x ½″.)''')
assembly(r,'FAN, radiator cooling (24″), assembly','30.55',note='&')
pieces(r,'''sixty-four SH278A radiator cooling fan BLADE,
one SH278B radiator cooling fan HUB,
one SH278D radiator cooling fan PLATE,
one SH278E radiator cooling fan RIM,''')
component(r,'two hundred }— RIVET, button head, 3/16″ x ⅝″,\nand fifty-six }')
r[-1]['item_layout']=[dict(text='two hundred\nand fifty-six',x=25,width=47),dict(text='}—',x=73,width=12,y=.5),dict(text='RIVET, button head, 3/16″ x ⅝″,',x=85,width=164,y=.5)]
component(r,'twelve — RIVET, button head, 5/16″ x 1¼″.)')

r=start(92)
assembly(r,'FAN, ventilating, (7½″), with housing, assembly','$75.92',note='')
pieces(r,'''two SKF1204 BEARING, ball, radial, dia. 1.8504″, bore .7874″, height~                         .5512″,
one SH204A     generator coupling FLANGE,
one —              ventilating FAN, assembly,
one SH959B     ventilating fan ball bearing HOLDER,
one SH959D     ventilating fan bearing CAP,
three SH959E   ventilating fan bearing CAP,
one SH958B     ventilating fan coupling SLEEVE,
one SH957A     ventilating fan HOUSING,
one SH959A     ventilating fan inlet CONE,
one SH959H     ventilating fan inner bearing grease PIPE, (length 4¼″),
one SH959G     ventilating fan inner bearing grease PIPE, (length 5″),
one SH960B     ventilating fan intake BOX,
one SH959F     ventilating fan outer bearing grease PIPE,
one —              ventilating fan SPINDLE, assembly,
one SH958N     ventilating fan spindle KEY,
one SH193B     ventilating fan SPROCKET,
one SH958C     ventilating fan sprocket SLEEVE,
three —            BOLT, U. S. Std., hexagon head, ⅜″ x 2¼″, with plain~                         nut and lock washer,
three —            BOLT, U. S. Std., hexagon head, ⅜″ x 2¾″, with plain~                         nut and lock washer,
one —              BOLT, U. S. Std., hexagon head, ½″ x 1⅛″, with plain~                         nut and lock washer,
five —              BOLT, U. S. Std., hexagon head, ½″ x 1½″, with plain~                         nut and lock washer,
two —              COUPLING, pipe, ⅛″,
two —              CUP, grease, No. 0 x ⅛″,''')

r=start(93)
pieces(r,'''one —       ELBOW, M. I., 90°, plain, ⅛″,
two —       KEY, Woodruff, No. 9,
two —       PIN, steel, ⅛″ x ¼″,
four —      SCREW, cap, U. S. Std., hexagon head, ½″ x ⅝″,
one —       SCREW, cap, U. S. Std., hexagon head, ½″ x 1″,
two —       SCREW, set, square head, cup point, 5/16″ x 1″,
five —       WASHER, lock, ½″.)''')
assembly(r,'FAN, ventilating, assembly','25.00',note='&')
component(r,'four SH960C ventilating fan BRACE,')
component(r,'*one SH960A ventilating fan WHEEL (1)',price='24.04')
component(r,'eight —       NUT, plain, U. S. Std., hexagon, ¼″.)')
for code,text,price in [('SH445D','distance recorder flexible tube, No. 1','.08'),('SH445E','distance recorder flexible tube, No. 2','.12'),('SH445L','(gas air and distance recorder) tube, No. 1','.09'),('SH445H','(gas air and distance recorder) tube, No. 2','.18')]:entry(r,'FASTENER, '+text,note='%X',ord=code,qty='1',price=price)
assembly(r,'FASTENER, strap, No. 2, with loop No. 1, assembly','.17',note='(mh)&',ord='15–2KN–1',qty='(4)')
pieces(r,'''*one NBIB strap FASTENER, No. 2 (4),
one A8177  strap LOOP, No. 1.~                   (For stop SH293E (4).)''')
entry(r,'FASTENER, strap, No. 2. (For holder SH285A (2).)',note='(mh)&',ord='15–2KN–1',qty='2',price='.10')
entry(r,'FASTENER, strap, No. 10. (For bracket, inner SH293A (4); holder SH443A\n  (2); holder SH285A (1).)',note='(mh)&',ord='A8174',qty='7',price='.15')
entry(r,'FASTENER, turret roof door',note='%X',brit='F19/2121C',ord='377',qty='2',price='1.05')
for code,n,desc,qty,price in [('SH445B','1','lighting','24','.09'),('SH445A','2','telephone','4','.10'),('SH445G','3','telephone','12','.05')]:entry(r,f'FASTENER, wire, No. {n}. (For {desc} cable.)',note='&',ord=code,qty=qty,price=price)
entry(r,'FERRULE, switch and voltage regulator terminal fiber',note='&',mfr='D30382',qty='4',price='.03 P')
assembly(r,'FILLER, crank case oil, assembly','2.96',ident='8156',plate='15',qty='(2)')
component(r,'*one LQ214A crank case oil FILLER (2)',mfr='C8155',price='1.77')
pieces(r,'''one —          crank case oil filler COVER, assembly,
one LQ217A crank case oil filler cover HINGE,
one LQ218A crank case oil filler cover hinge PIN,
one LQ219A crank case oil filler cover LOCK,
one —          crank case oil filler STRAINER, assembly,
five LQ221A escutcheon PIN, No. 13 x ⅜″.)''')
entry(r,'FILLER, flexible electric conduit clamp',note='%X',ord='SH920C',qty='1',price='.08 P')

r=start(94)
assembly(r,'FILTER, engine oil tank, assembly','$3.21')
component(r,'one M3298 engine oil tank delivery pipe CONE,')
component(r,'*one M3299 engine oil tank filter BODY (1)',ord='165',price='1.09')
component(r,'one M3300 engine oil tank filter GAUZE,')
component(r,'*one M3297 engine oil tank filter RING, bottom (1)',ord='166',price='.48')
component(r,'*one M3296 engine oil tank filter RING, top (1).)',ord='166',price='.48')
for cells in [
 ('X','','','','B/20793','637','FLANGE, ball mount, inner (on main turret)','2','10.18'),
 ('%X','','','','M3119','429','FLANGE, ball mount, inner','3','9.75'),
 ('%X','','','','A/20793','637','FLANGE, ball mount, outer (on main turret)','2','12.38'),
 ('%X','','','','M3118','429','FLANGE, ball mount, outer','3','10.35'),
 ('%X','13006','13','B13006','','LQ43A','FLANGE, cam shaft distributor driving','2','2.70'),
 ('&','22','21','','','SH849A','FLANGE, clutch spring (half)','2','2.15'),
 ('&','','','D30538','','','FLANGE, distributor coupling','2','.18 P'),
 ('&','','','','','SH978M','FLANGE, engine oil tank filler plug','1','.10'),
 ('&','','','','M3293','164','FLANGE, engine oil tank filling cover','1','1.38'),
 ('&','','','','M3315','164','FLANGE, engine oil tank suction and delivery','2','.78'),
 ('&','','','','','SH207C','FLANGE (engine oil tank) suction oil tube','2','.48'),
 ('&','','','','M1757','187','FLANGE, gasoline tank drain plug','3','.48')]:r.append(row(*cells))
assembly(r,'FLANGE, gasoline tank filler cap, assembly','6.27',note='&',qty='(3)')
component(r,'*one SH951B gasoline tank filler cap FLANGE (3)',ord='951',price='6.24')
component(r,'one Q52D     PLUG, pipe, square head, ½″.)')
entry(r,'FLANGE, generator coupling',note='&',ord='SH204A',qty='2',price='.88')
entry(r,'FLANGE, indicator',note='&',brit='M3304',ord='164',qty='2',price='.78')
entry(r,'FLANGE, radiator pipe',note='&',brit='M1195',ord='167',qty='1',price='.58')
entry(r,'FLANGE, water tank filler pipe',note='&',ident='—',plate='24',brit='M1194',ord='167',qty='1',price='1.45')
assembly(r,'FLAP, main turret, side, assembly','49.27',note='&',ident='45',plate='2',qty='(2)')
component(r,'two M1789   door HINGE, female,')

r=start(95)
component(r,'*one M2353   main turret FLAP, side (2)',ord='407',price='45.04')
pieces(r,'''one M2377   main turret flap catch PLATE,
one —           main turret flap ring BOLT, assembly,
one M2375   main turret flap splash PLATE, bottom,
two M2374   main turret flap splash PLATE, side,
one SH420A main turret flap splash PLATE, top,
eleven —       RIVET, button head, 7/16″ x 1⅞″,
four —          RIVET, button head, 7/16″ x 2⅛″.)''')
entry(r,'FLOAT, carburetor',note='&',mfr='13381',ord='LQ531A',qty='2',price='.43')
assembly(r,'FLOAT, regulating tank, assembly','.63',note='&')
component(r,'*one SH950C regulating tank FLOAT (1)',price='.25')
component(r,'*one SH950F regulating tank float ROD (1).)',price='.38')
entry(r,'FLOAT, regulating tank relief valve',note='&',ord='SH962C',qty='1',price='.10')
entry(r,'FLYWHEEL',note='&',ident='16',plate='21',ord='SH868A',qty='1',price='175.00')
for code,text,price in [('SH280D','outlet end, inside','.88'),('SH280B','outlet end, outside','.88'),('SH280C','rear inside','1.15'),('SH280A','rear outside','1.15')]:entry(r,'FOOT, radiator cooling fan, '+text,note='&',ord=code,qty='1',price=price)
assembly(r,'FOOT, transmission sprocket bearing outside bracket support, assembly','1.94',qty='(2)')
component(r,'*one M391 transmission sprocket bearing outside bracket support FOOT\n                   (2)',ord='669',price='1.89')
component(r,'one —       NUT, jam, U. S. Std., 1″.)')
entry(r,'FORK, transmission shifter',note='&',brit='M301',ord='714',qty='1',price='7.80');stacked(r,ident='13\n47',plate='23\n22')
assembly(r,'FRAME, generator, with pole piece and field coil, assembly','12.23 P',note='&')
pieces(r,'''one D13784 generator field COIL, assembly,
four D30521 generator field coil insulating STRIP,
one D13823 generator FRAME, with pole piece, assembly.)''')
assembly(r,'FRAME, generator, with pole piece, assembly','6.45 P',note='&',mfr='D13823')
component(r,'*one D29805 generator FRAME (1)',price='3.75')
pieces(r,'''four D29804 generator frame pole PIECE,
two D29225 generator housing PIN (.0945″ x .218″),
eight D25673 SCREW, slotted head, 5/16″–24 x .562″.)''')
entry(r,'FRAME, inlet louvre, left side',note='&',brit='M983',ord='499',qty='1',price='22.50')
entry(r,'FRAME, inlet louvre, right side',note='&',brit='M982',ord='499',qty='1',price='22.50')

r=start(96)
assembly(r,'FRAME, regulating tank relief valve guide, assembly','$0.66',note='&')
component(r,'*one SH962D regulating tank relief valve guide FRAME (1)',price='.65')
component(r,'one SH962E regulating tank relief valve guide PIN.)')
assembly(r,'FRAME, transmission, with brackets and caps, assembly','749.09',note='(gq)&')
pieces(r,'''twenty MX13 bevel WASHER,
one —               transmission bevel gear CASE, assembly,
one —               transmission FRAME, assembly,
two —               transmission sprocket bearing BRACKET, inside, assembly,
two —               transmission sprocket bearing BRACKET, outside, assem-~                          bly,
twenty —           transmission sprocket bearing bracket to channel BOLT,~                          assembly,
two —               transmission sprocket shaft inside bearing CAP, assembly,
two —               transmission sprocket shaft outside bearing CAP, assembly.)''')
assembly(r,'FRAME, transmission, assembly','99.89',note='&')
for text,code,price in [
 ('*four M338 transmission brake suspension BRACKET (4)','686','2.75'),
 ('*two M385 transmission brake suspension STOP (2)','669','1.52'),
 ('*one M374 transmission frame CHANNEL, bottom (1)','667','20.75'),
 ('*one M373 transmission frame CHANNEL, top (1)','667','20.75'),
 ('*one M375 transmission frame DIAPHRAGM, middle (1)','666','15.65'),
 ('*one M377 transmission frame diaphragm ANGLE, inner, left (1)','666','4.78'),
 ('*one M376 transmission frame diaphragm ANGLE, inner, right (1)','666','4.78'),
 ('*two M378 transmission frame diaphragm ANGLE, outer (2)','666','4.78'),
 ('*two M380 transmission frame diaphragm GUSSET, inner (left top and\n                    right bottom) (2)','668','.88'),
 ('*two M382 transmission frame diaphragm GUSSET, inner (right top\n                    and left bottom) (2)','668','.88')]:component(r,text,ord=code,price=price)

r=start(97)
component(r,'*two M384 transmission frame diaphragm GUSSET, outer (left top and\n                    right bottom) (2)',ord='668',price='1.12')
component(r,'*two M383 transmission frame diaphragm GUSSET, outer (right top\n                    and left bottom) (2)',ord='668',price='1.12')
pieces(r,'''four —          RIVET, button head, ½″ x 1½″,
four —          RIVET, button head, ½″ x 1⅝″,
twelve —       RIVET, button head, ½″ x 1¾″,
thirty-two — RIVET, button head, 11/16″ x 1½″,
four —          RIVET, button head, 11/16″ x 1⅝″,
six —            RIVET, button head, 11/16″ x 2″,
four —          RIVET, button head, 11/16″ x 2¼″,
twelve —       RIVET, button head, 11/16″ x 2⅝″.)''')
for cells in [
 ('&','—','6','','M747','224','FULCRUM, front control lever, left','1','4.50'),
 ('&','—','6','','M746','224','FULCRUM, front control lever, right','1','4.50'),
 ('%X','','','','','31–37–2T','FUZE, type 4A, 2 ampere, 1 to 50 volt (for lights) (Chicago Fuze Mfg. Co. type)','4','.10 P'),
 ('%X','','','','','','FUZE (for telephone)','',''),
 ('%(gt) X','','','','','SH980C','GAGE, air pressure (Edelman or equal)','4','2.50 P'),
 ('%X','','','','','SH559C','GAGE, oil pressure (Edelman type), assembly','1','2.50 P'),
 ('&','','','8379','','LQ32A','GASKET, cam shaft bearing end','2','.01'),
 ('&','','','8348','','LQ98A','GASKET, cam shaft driving shaft lower bearing container','2','.01'),
 ('&','—','34','8139','','LQ84A','GASKET, cam shaft driving shaft upper flange','2','.02'),
 ('&','','','L13356','','LQ424A','GASKET, carburetor to intake header','2','.05'),
 ('&','','','254','','LQ509A','GASKET, copper asbestos, 17/64″. (For well LQ561A (1).)','4','.01 P'),
 ('%(c) X','13','14','(157)','','','GASKET, copper asbestos, ⅜″. (For screw LQ33A (1); stud LQ269A (2); plug\n  LQ182A (1); stud LQ270A (2); stud LQ271A (2); connection LQ56A (2).)','43','.01 P')]:r.append(row(*cells))
entry(r,'GASKET, copper asbestos, ⅝″. (For (under) plug LQ145A (1); crank case, lower\n  half, assembly (1); (under) plug LQ48A (1).)',note='%(c) X',mfr='(158)',qty='6',price='.01 P');stacked(r,ident='—\n158',plate='12\n13\n18')
r[-1]['cell_baseline_offsets']['plate']=-.5
for cells in [
 ('%(c) X','','','','','','GASKET, copper asbestos, ⅞″. (For oil pump suction and overflow tube nut.)','2','.01 P'),
 ('%(c) X','','','(208)','','','GASKET, copper asbestos, 1¼″. (For (under) plug LQ266A (1).)','12','.05 P'),
 ('%(c) X','','','','','','GASKET, copper asbestos, 1⅜″. (For (under) plug LQ265A (1).)','11','.05'),
 ('%(c) X','','','(169)','','','GASKET, copper asbestos, 1⅞″. (For (under) cover LQ54A (1).)','2','.05 P'),
 ('%X','','','8172','','LQ236A','GASKET, crank case breather','1','.01'),
 ('%X','','','8158','','LQ228A','GASKET, crank case oil filler','2','.05'),
 ('%X','','','8236','','LQ465A','GASKET, crank case oil tube union connection','1','.01'),
 ('&','','','13482','','LQ264A','GASKET, crank shaft gear end plug','1','.10'),
 ('&','','','13483','','LQ265A','GASKET, crank shaft main bearing','11','.12'),
 ('&','','','B12346','','LQ250A','GASKET, cylinder to crank case','4','.25'),
 ('&','8358','15','B8358','','LQ312A','GASKET, distributor to cam shaft housing','2','.04')]:r.append(row(*cells))

r=add(98,'''&|||D29782|||GASKET, distributor cup|2|$0.03 P
&|||D30274|||GASKET, distributor ignition coil and distributor head stud insulator|4|.01 P
%X||||M3295|166|GASKET, engine oil tank filler cap (leather)|1|.12
&|||||SH207G|GASKET (engine), oil (tank) pipe flange|2|.08
%X|||8176||LQ306A|GASKET, exhaust header|12|.03
%X|||||SH146A|GASKET, fan bevel gear box bearing cover plate|1|.18
%X|||||SH194B|GASKET, fan bevel gear housing side cover|2|.08
%X|||||SH194A|GASKET, fan bevel gear housing upper cover|1|.12
&|||||LQ417A|GASKET, flange, ¾″ tube. (For elbow LQ308A (1).)|12|.01
%X|||8389||LQ251A|GASKET, generator|1|.01
&|8347|16|8347||LQ406A|GASKET, generator driving shaft ball bearing container|1|.50
&|8205|15|B8205||LQ232A|GASKET, governor to crank case|1|.02
&|||8175||LQ411A|GASKET, intake header|12|.01
%X|2|14|B8153||LQ414A|GASKET, intake header water outlet|2|.05
%X|8348|15|B8348|||GASKET, oil pressure gage (see vellumoid)|1|.10''')
entry(r,'GASKET, oil pump body',note='%X',mfr='B8382',ord='LQ195A',qty='1',price='.10');stacked(r,ident='8382\n—',plate='15\n12')
for cells in [
 ('*','','','','','LQ454A','GASKET, oil pump lower half body cover','—',''),
 ('&','','','','','SH281B','GASKET, radiator cooling fan ball race housing','2','.10'),
 ('&','','','','','SH607A','GASKET, radiator core','1','.98'),
 ('&','','','','M888','607','GASKET, radiator header','2','1.25'),
 ('&','','','','M1241','168','GASKET, radiator inlet and outlet pipe','2','.28'),
 ('&','','','','','SH950M','GASKET, regulating tank cap (vellum)','1','.35'),
 ('&','','','','','SH608F','GASKET, rubber, 2¾″ x 2¾″ x ⅛″. (For plate M880 (1); plate SH608B (1);\n  plate SH608A (1).)','4','.12'),
 ('%X','','','','','LQ300A','GASKET, spark plug','—','.01'),
 ('&','12','22','','M326','672','GASKET, transmission bevel gear case','2','.50'),
 ('&','','','','M315','678','GASKET, transmission gear case','4','.50'),
 ('%X','28','22','','M316','672','GASKET, transmission (gear case) oil filling plug','3','.08'),
 ('&','','','','','SH104G','GASKET, transmission mechanical lubricator cover','1','.12')]:r.append(row(*cells))

r=add(99,'''&|||||SH104A|GASKET, transmission mechanical lubricator stuffing box|1|.04
&|8215|17|8215||LQ149A|GASKET, water pump cover|1|.01
&|8345|14|8345||LQ154A|GASKET, water pump shaft bearing retainer|1|.01
&||||M1240|168|GASKET, water tank outlet pipe|1|.25
&|—|6||M752|237|GATE, control, left|1|11.80
&|—|6||M751|237|GATE, control, right|1|11.80
&||||M3300|166|GAUZE, engine oil tank filter|1|.78
&|||||SH188D|GAUZE, wire, brass, 7¼″ x 10⅝″, No. B & S gage 31, mesh 30. (For gasoline tank~  strainer, assembly (2).)|6|.35 P
&|||||SH188E|GAUZE, wire, brass, 7¼″ x 10⅝″, No. B & S gage 45, mesh 80. (For gasoline tank~  strainer, assembly (1).)|3|.50 P
&|8093|13|C8093||LQ36A|GEAR, cam shaft|2|17.00
&|||B8076||LQ104A|GEAR, cam shaft driving shaft, lower|2|3.10''')
entry(r,'GEAR, cam shaft driving shaft, upper',note='&',mfr='C8094',ord='LQ77A',qty='2',price='1.30');stacked(r,ident='8094\n—',plate='13\n34')
for cells in [
 ('&','','','C8067','','LQ258A','GEAR, crank shaft','1','15.00'),
 ('%X','','','','','SH586B','GEAR, distance recorder','1','7.45'),
 ('&','4','20','','M1125','195','GEAR, fan bevel','2','3.60'),
 ('&','8074','16','B8074','','LQ400A','GEAR, generator driving shaft, lower','1','4.12'),
 ('&','8080','16','B8080','','LQ395A','GEAR, generator driving shaft, upper','1','4.20'),
 ('&','—','33','8178','','LQ434A','GEAR, oil pump driven, lower','1','2.00'),
 ('&','—','33','8177','','LQ438A','GEAR, oil pump driven, upper','2','2.00'),
 ('&','—','33','8186','','LQ433A','GEAR, oil pump driving, lower','1','.75'),
 ('&','—','33','8187','','LQ439A','GEAR, oil pump driving, upper','1','.77'),
 ('&','','','','','SH66A','GEAR, starting crank counter shaft','1','5.97'),
 ('&','','','D29845','','','GEAR, tachometer drive shaft','1','.41 P')]:r.append(row(*cells))
assembly(r,'GEAR, transmission bevel, assembly','73.86',note='&',ident='61',plate='22',qty='(2)')
pieces(r,'''one M258A transmission bevel GEAR,
one M258B transmission bevel gear clutch RING,
one —         transmission flanged SLEEVE, assembly,
six —           RIVET, button head, ⅝″ x 2⅛″,
six —           RIVET, button head, ⅝″ x 2⅜″,
one —         SCREW, set, headless, 5/16″ x ½″.)''')
entry(r,'GEAR, transmission bevel',note='&',brit='M258A',ord='948',qty='2',price='35.60')
entry(r,'GEAR, transmission mechanical lubricator worm',note='&',ord='SH103B',qty='1',price='1.08')
entry(r,'GEAR, transmission shifter',note='&',ident='19',plate='23',brit='M257A',ord='948',qty='1',price='24.75')

r=start(100)
entry(r,'GENERATOR, 8 volt (Delco type, No. 136), assembly',note='%X',mfr='D132',qty='(1)',price='$48.00 P');stacked(r,ident='8245\n38',plate='15\n14');composed(r)
pieces(r,'''one D13754 generator ARMATURE,
one D29852 generator armature shaft plain WASHER,
one —          generator drive shaft end HOUSING, with tachometer drive~                      shaft, assembly,
four D29848 generator drive shaft end housing binding BOLT,
one D30267 generator drive shaft end housing binding bolt CLIP,
one D13826 generator end COVER, assembly,
one —          generator FRAME, with pole piece and field coil, assembly,
one D27193 generator insulating WASHER,
one D13827 generator top end HOUSING, with brush arms, assembly,
one D30267 generator WIRE,
one D30309 NUT, castle, ⅜″–24 x 9/16″ x 13/32″ thick,
one —          PIN, split, 7/64″ x ¾″,
four D21717 WASHER, lock, .256″ x .291″ x .429″ x .062″,
one D26616 WASHER, plain, .380″ x .875″ x .032″.)''')
assembly(r,'GENERATOR, 12 volt, with flange, assembly','125.89')
pieces(r,'''one SH80A 12 volt GENERATOR,
one SH204A generator coupling FLANGE,
one —          KEY, Woodruff, No. 9.)''')
entry(r,'GENERATOR, 12 volt (Bijur Motor Lighting Co. type)',note='(gy)&',ord='SH80A',qty='1',price='125.00 P')
entry(r,'GLAND, soldering, 5/16″ O. D. x ½″ over all (brass). (For tube C8012 (1); tube\n  C8013 (4); tube C8014A (2); tube C8014B (2); tube C8014C (2); tube C8015 (1);\n  tube C8016 (2).)',note='X',ord='B101966B',qty='16',price='.03 P')
entry(r,'GLAND, transmission mechanical lubricator tank stuffing box',note='&',ord='SH103C',qty='1',price='.34')
entry(r,'GLAND, transmission pinion shaft packing',note='&',brit='M251',ord='703',qty='1',price='4.78');stacked(r,ident='1\n66',plate='23\n22')
entry(r,'GLAND, water pump shaft',note='&',ident='8059',plate='17',mfr='8059',ord='LQ142A',qty='2',price='1.25')

r=start(101)
entry(r,'GLASS, oil pressure gage. (For Edelman type, SH559C).',note='X',ord='—',qty='1')
entry(r,'GLASS, transmission mechanical lubricator sight feed hood (7/64″ x 1¼″ x 5⅞″)',note='&',ord='SH104H',qty='1',price='.05 P')
assembly(r,'GOVERNOR, with sprocket, assembly','52.70',note='&')
pieces(r,'''one SH193A fan double drive SPROCKET,
one —          GOVERNOR, assembly,
one SH144A governor LEVER,
one SH144C governor spindle KEY,
one —          BOLT, U. S. Std., hexagon head, ¼″ x 1 9/16″, with plain~                      nut and lock washer,
one Q74H     KEY, Woodruff, No. 7.)''')
assembly(r,'GOVERNOR, assembly','44.10 P',note='&')
pieces(r,'''one Gurney 306 BEARING, ball, thrust, dia. 2.8347″, bore 1.1811″,~                             height .9449″,
one S. K. F. 1109F BEARING, ball, thrust, dia. 2.87″, bore 1.7717″,~                             height .79″,
one SH142E         governor ARM,
one SH142A         governor arm BUSHING,
one SH142B         governor arm bushing set SCREW,
one SH142C         governor arm bushing set screw NUT,
one SH987B         governor ball CAP,
one SH987A         governor ball retaining RING,
one SH142F         governor bearing SPACER,
two SH142G         governor felt retaining WASHER,
one SH141A         governor HOUSING, front half,
one SH145A         governor housing, rear half,
one SH142H         governor oil retaining WASHER,
one —                  governor SPINDLE, assembly,
one SH143A         governor thrust bearing CUP,
one SH143B         governor thrust bearing MOUNT,
four —                 BALL, steel, 1″,
five —                  BOLT, U. S. Std., hexagon head, ⅜″ x 1⅛″, with plain~                             nut and lock washer,
one Q74R             KEY, Woodruff, No. A,
one Q52A             PLUG, pipe, square head ⅛″.)''')
entry(r,'GRIP, starting crank lever handle',note='&',ord='SH66D',qty='1',price='.48')

# Shared opening rows visibly repeated for the left and right exhaust guards.
def guard_start(r):
 for text,price in [
  ('*one SH154E    exhaust manifold clamping STRAP, large (2)','.15'),
  ('*one SH154F    exhaust manifold clamping STRAP, small (2)','.14'),
  ('*one SH152D   exhaust manifold connecting ANGLE, left (2)','.60'),
  ('*one SH152C    exhaust manifold connecting ANGLE, right (2)','.60')]:component(r,text,price=price)
def guard_finish(r):
 pieces(r,'''one —              exhaust manifold guard CLAMP, large, assembly,
one —              exhaust manifold guard CLAMP, small, assembly,
two SH154G    exhaust manifold guard SPACER, ⅜″ x ⅜″,
two SH154H    exhaust manifold guard SPACER, ⅜″ x ⅝″,''')
 component(r,'*two SH152G   exhaust manifold guard STRIP, inner (4)',price='.20')
 pieces(r,'''four SH152F    exhaust manifold guard WASHER,
four —             BOLT, stove, round head, ¼″ x ¾″, with two stove bolt~                          nuts and washers,
twenty-six —    RIVET, button head, 3/16″ x ½″.)''')

r=start(102)
assembly(r,'GUARD, exhaust manifold, left, assembly','$6.86');guard_start(r)
for text,price in [
 ('*one SH154M   exhaust manifold COVER, left (1)','1.50'),
 ('*one SH152BB exhaust manifold guard BAND, inner, large (without\n                          holes) (1)','.18'),
 ('*one SH152K    exhaust manifold guard BAND, inner, small (2)','.15'),
 ('*one SH152AA exhaust manifold guard BAND, outer, large (without\n                          holes) (1)','.28'),
 ('*one SH152H    exhaust manifold guard BAND, outer, small (2)','.25'),
 ('*one SH152L    exhaust manifold guard BRACE, large (2)','.25'),
 ('*one SH152M   exhaust manifold guard BRACE, small (2)','.20')]:component(r,text,price=price)
guard_finish(r)
assembly(r,'GUARD, exhaust manifold, right, assembly','6.86');guard_start(r)

r=start(103)
for text,price in [
 ('*one SH154L exhaust manifold COVER, right (1)','1.50'),
 ('*one SH152B exhaust manifold guard BAND, inner, large (with holes) (1)','.18'),
 ('*one SH152K exhaust manifold guard BAND, inner, small (2)','.15'),
 ('*one SH152A exhaust manifold guard BAND, outer, large (with holes) (1)','.28'),
 ('*one SH152H exhaust manifold guard BAND, outer, small (2)','.25'),
 ('*one SH152L exhaust manifold guard BRACE, large (2)','.25'),
 ('*one SH152M exhaust manifold guard BRACE, small (2)','.20')]:component(r,text,price=price)
guard_finish(r)
for cells in [
 ('%X','10','28','','M1479','62','GUARD, track adjusting screw (hull plate)','4','.95'),
 ('&','','','D30898','','','GUARD, voltage regulator armature regulating spring','1','.02 P'),
 ('&','','','','M2428','412','GUIDE, driver’s turret flap raising lever','1','.52'),
 ('&','','','','M2155B','364','GUIDE, engine room door, bottom, left','1','.95'),
 ('&','','','','M2155A','364','GUIDE, engine room door, bottom, right','1','.95'),
 ('*','','','','M2156','364','GUIDE, engine room door, top','(1)','1.08'),
 ('&','','','','M2208','374','GUIDE, fan discharge door, top','1','.75'),
 ('&','','','','','SH65H','GUIDE, hand starter lock plunger','1','.22'),
 ('*','','','','M2166','370','GUIDE, ignition inspection door, bottom','(1)','.58'),
 ('*','','','','M2165','370','GUIDE, ignition inspection door, side','(2)','.78'),
 ('&','—','12','8384','','LQ446A','GUIDE, oil pump pressure relief valve','1','1.51'),
 ('&','—','6','','M742','228','GUIDE, pawl. (For lever M738A (1); lever M738B (1); lever M177 (1).)','3','.18'),
 ('&','2','3','','M2114','378','GUIDE, towing cable','1','4.31'),
 ('&','','','8025','','LQ288A','GUIDE, valve stem, exhaust','12','.43'),
 ('&','','','8026','','LQ289A','GUIDE, valve stem, inlet','12','.43'),
 ('&','','','','M2209','374','GUIDE, ventilating shutter, bottom','1','.68'),
 ('&','','','','M2208','374','GUIDE, ventilating shutter, top','1','.75'),
 ('*','','','','M2068','340','GUSSET, roof channel to side (right)','(1)','3.75'),
 ('&','','','','M2151','363','HANDLE, door. (For door M2146A (1); door M2146B (1); inspection door (1).)','3','.48'),
 ('&','','','','C114E','582','HANDLE, door. (For outside tool chest.)','1','1.25')]:r.append(row(*cells))
entry(r,'HANDLE, door lock. (For door lock, left, assembly (1); right, assembly (1).)',note='&',ord='412',qty='6',price='.48');stacked(r,brit='E20/\n21195')
entry(r,'HANDLE, engine room door catch',note='&',brit='M2152',ord='363',qty='2',price='1.00')

r=start(104)
entry(r,'HANDLE, hemispherical turret',note='%X',brit='M3131',ord='434',qty='6',price='$1.52')
entry(r,'HANDLE (holes 6″ apart). (On main turret (3); cover M1785 (1); cover M1786\n  (1).)',note='&',brit='J206/\n21067',ord='538',qty='5',price='.28')
entry(r,'HANDLE, ignition battery case',note='&',mfr='W–V12',qty='2',price='.08')
entry(r,'HANDLE, revolver hole cover operating',note='&',ord='642',qty='9',price='.40');stacked(r,brit='A42/\n21221')
assembly(r,'HANDLE, semaphore sprocket, near side, assembly','2.81',note='&')
pieces(r,'''one —      semaphore detent PLUNGER, assembly,
one X274 semaphore detent SPRING,
one X271 semaphore handle PIN, short,
one X272 semaphore handle TUBE, short,
one X275 semaphore spring WASHER,''')
component(r,'*one X269 semaphore sprocket HANDLE, near side (1)',ord='802',price='1.60')
pieces(r,'''one —      BOLT, U. S. Std., hexagon head, ¼″ x 1⅝″, with plain nut,
one —      WASHER, plain, 5/16″.)''')
assembly(r,'HANDLE, semaphore sprocket, off side, assembly','2.09',note='&')
pieces(r,'''one X246 semaphore handle PIN, long,
one X247 semaphore handle TUBE, long,''')
component(r,'*one X270 semaphore sprocket HANDLE, off side (1)',ord='802',price='1.38')
pieces(r,'''one —      BOLT, U. S. Std., hexagon head, ¼″ x 1⅝″, with plain nut,
one —      WASHER, plain, 5/16″.)''')
entry(r,'HANDLE, starting and ignition battery case',note='&',mfr='W–V14',qty='4',price='.08')
entry(r,'HANDLE, starting crank lever',note='&',ord='SH65G',qty='1',price='.44')
entry(r,'HANGER, battery shelf',note='%X',ord='SH992B',qty='1',price='2.28')
entry(r,'HANGER, map board buckle',note='%X',ord='SH424B',qty='1',price='.22')
assembly(r,'HASP, tool chest, assembly','.19 P',note='(n)&',qty='(2)')
component(r,'one GB5G tool chest HASP,')
