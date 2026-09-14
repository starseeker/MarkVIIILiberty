"""Photograph-led transcription of printed pages 105–124.

Original page breaks, blank fields and apparent source errors are preserved.
Specific uncertain readings are recorded in review.json.
"""
from .parts_tables import row
from .opening_tables import entry,component,composed
from .tables_045_064 import assembly
from .tables_065_084 import pieces,stacked
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

def continued(r,text,note='&'):
 entry(r,text,note=note);composed(r)

r=start(105)
component(r,'*one GB5E tool chest hasp HINGE (2)',price='.09')
component(r,'one —       PIN, steel, ¼″ x 2¼″. (For outside tool chest (2).)')
entry(r,'HASP, tool chest (1¼″ x 2½″). (For outside tool chest) (15–2KG)',note='(n)&',ord='GB5G',qty='2',price='.09 P')
entry(r,'HEAD, carburetor to intake header bolt',note='%X',mfr='14380',ord='LQ421A',qty='2',price='.04')
assembly(r,'HEAD, distributor, assembly','12.00 P',mfr='D13725',qty='(2)')
pieces(r,'''*one D13776 distributor HEAD (2),
two D13811 distributor head NUT, with connector, assembly,
one D13740 distributor induction COIL, assembly.)''')
assembly(r,'HEADER, intake, assembly','12.76',note='&',ident='1&9',plate='14',qty='(4)')
component(r,'*one LQ408A intake HEADER (4)',mfr='C12045',price='12.30')
component(r,'*two LQ409A intake header core PLUG (8)',mfr='8391',price='.05')
pieces(r,'''two (LQ196A) STUD, ¼″ x 1 9/16″, threaded U. S. Std. 7/16″ and S. A. E.~                         9/16″, assembly,
two LQ113A WASHER, special, ¼″.)''')
assembly(r,'HEADER, radiator, front, assembly','11.86',note='&')
pieces(r,'''one SH608B radiator drain pipe connection stiffening PLATE (tapped~                      for countersunk head bolt),
one M880     radiator drain pipe connection stiffening PLATE (tapped~                      ½″),''')
component(r,'*one M878   radiator HEADER, front (1)',ord='118',price='9.00')
pieces(r,'''one M887     radiator steam pipe connection stiffening PLATE (tapped~                      1″),
one M886     radiator water connection stiffening PLATE,
two SH608F rubber GASKET, 2¾″ x 2¾″ x ⅛″,
ten —           RIVET, button head, 5/16″ x 1⅛″,
four —         SCREW, cap, U. S. Std., flat head, ⅜″ x ½″,
four —         SCREW, cap, U. S. Std., hexagon head, ⅜″ x ⅝″.)''')
assembly(r,'HEADER, radiator, rear, assembly','8.44',note='&')
pieces(r,'''one SH608A radiator drain pipe connection stiffening PLATE (tapped~                       ¼″),
one M880      radiator drain pipe connection stiffening PLATE (tapped~                       ½″),
one M897      radiator steam pipe connection stiffening PLATE (tapped~                       ¾″),''')
component(r,'*one M879    radiator HEADER, rear (1)',ord='117',price='6.75')

r=start(106);continued(r,'HEADER, radiator, rear, assembly—Continued.')
pieces(r,'''two SH608F rubber GASKET, 2¾″ x 2¾″ x ⅛″,
four —         RIVET, button head, 5/16″ x 1⅛″,
four —         SCREW, cap, U. S. Std., hexagon head, ⅜″ x ½″,
four —         SCREW, cap, U. S. Std., hexagon head, ⅜″ x ⅝″.)''')
for cells in [
 ('&','','','','','SH101A','HEADER, transmission mechanical lubricator cylinder pump','6','$0.58'),
 ('&','','','','','SH103A','HEADER, transmission mechanical lubricator feed pump, M–G','6','1.18'),
 ('&','','','','M2158','362','HINGE, butt, 2″ x 4¼″. (For machine gunner’s seat plate, assembly (2); (Offi-\n  cer’s) map board M2441 (2); lid M4040A (2).)','10','.45'),
 ('&','','','8157','','LQ217A','HINGE, crank case oil filler cover','2','.10'),
 ('&','','','','M1789','537','HINGE, door, female. (For flap M2353 (2); cover M1785 (2); cover M1786 (2);\n  main turret roof door (2).)','12','1.50'),
 ('(c)&','','','','','GB3L','HINGE, door, female (2½″ wide). (For outside tool chest.)','3','1.06'),
 ('&','','','','M1790','537','HINGE, door, male. (For plate M2355 (2); plate M2356 (2); cover M1785 (2); main\n  turret roof door (2); cover M1786 (2).)','12','1.50'),
 ('(c)&','','','','','GB3J','HINGE, door, male. (For outside tool chest.)','3','1.60'),
 ('&','','','','M2403','417','HINGE, driver’s turret flap','4','.52'),
 ('&','','','','','SH537B','HINGE, gasoline tank cover, female','4','1.35'),
 ('&','','','','','SH537A','HINGE, gasoline tank cover, male','4','1.18'),
 ('%X','','','','M2444','424','HINGE, map board buckle. (For board M2441 (1).)','2','.15 P'),
 ('&','','','','M706','544','HINGE, side door','8','2.25'),
 ('&','','','','M2826','477','HINGE, sponson','4','5.75'),
 ('&','','','','M2828','477','HINGE, sponson, left hull (lower right and upper left)','2','10.00'),
 ('&','','','','M2827','477','HINGE, sponson, right hull (lower left and upper right)','2','10.00'),
 ('&','','','','M2814','472','HINGE, sponson seat, female','4','1.00'),
 ('&','','','','M2815','472','HINGE, sponson seat, male','4','1.00'),
 ('&','','','','','SH576K','HINGE, 2½″ x 2½″ (Stanley type, No. 808). (For lid SH576G (2).)','4','.08'),
 ('&','','','','','SH942F','HINGE, 6-pdr. spare parts box','4','.12 P')]:r.append(row(*cells))
entry(r,'HOLDER, spare fan belt, assembly',note='&',qty='(1)',price='1.78')

r=start(107);composed(r)
pieces(r,'''two NB1B      FASTENER, strap, No. 2,
one A8174     FASTENER, strap, No. 10,''')
component(r,'*one SH285A spare fan belt HOLDER',price='.75')
pieces(r,'''one (SH285D) spare fan belt holder STRAP, buckle end, assembly,
two ZA7M      RING, D, 1″ x 1¼″,
two —            RIVET, belt, brass, No. 10 x ¾″,
six —              RIVET, button head, 3/16″ x ⅜″.)''')
for code,text,qty,price in [('SH443E','spare track shoe','2','2.89'),('SH550H','spring case shell','2','.48'),('SH471A','telescopic sight case strap (sponson)','2','.29'),('SH959B','ventilating fan ball bearing','1','2.75')]:entry(r,'HOLDER, '+text,note='&',ord=code,qty=qty,price=price)
assembly(r,'HOLDER, water bucket, assembly','2.96')
component(r,'two A8174    FASTENER, strap, No. 10,')
component(r,'*one SH443A water bucket HOLDER (1)',price='1.72')
pieces(r,'''one —             water bucket holder STRAP, buckle end, assembly,
one SH443D   water bucket holder STRAP, plain end,
four —            RIVET, belt, brass, No. 10 x ⅝″,
four —            RIVET, button head, ¼″ x ¾″.)''')
assembly(r,'HOOD, transmission mechanical lubricator sight feed, assembly','.56')
component(r,'*one SH105D transmission mechanical lubricator sight feed HOOD (1)',price='.42 P')
component(r,'*nine SH105F transmission mechanical lubricator sight feed hood CLIP (9)',price='.01')
component(r,'one SH104H transmission mechanical lubricator sight feed hood GLASS.)',price='.05 P')
entry(r,'HOOK, ball mount ball locking pin, 17/32″ hole',note='%X',ord='SH1712K',qty='3',price='.18')
entry(r,'HOOK, ball mount ball locking pin, 11/16″ hole',note='%X',ord='SH1712B',qty='2',price='.18')
assembly(r,'HOOK, ignition inspection door, assembly','.52',note='&')
component(r,'*one M2168    ignition inspection door HOOK (1)',ord='370',price='.25')
component(r,'*one M2169A ignition inspection door hook BRACKET (1)',ord='370',price='.25')
component(r,'one —            PIN, steel, ¼″ x 1″.)')
entry(r,'HOOK, jockey pulley chain',note='&',ord='SH234M',qty='1',price='.28')
entry(r,'HOOK, map board',note='%X',ord='SH424A',qty='2',price='.20')
assembly(r,'HOOK, pigeon basket, assembly','.27')
component(r,'*one M2187   pigeon basket HOOK (1)',ord='373',price='.25')
component(r,'one SH373Q pigeon basket hook NUT.)')
entry(r,'HOOK, S, standard chain. (For chain JB5C (2); chain JB5D (2).)',note='%(cp) (d) R',ord='A4478',qty='14',price='.05 P')

r=add(108,'''&|||||SH649A|HOOK, towing cable carrying, front (holes 5 11/16″ apart)|2|$4.72
&|||||SH649B|HOOK, towing cable carrying, rear (holes 5⅞″ apart)|2|4.72
%X|8152|15|8152||LQ177A|HOSE, cylinder water|24|.02 P
%X|||||SH199B|HOSE (engine outlet pipe) connection, short (5 ply, 2½″ hose, length 3½″)|(2)|.20 P
%X|—|24|||SH168U|HOSE, radiator inlet (3 ply hose, 1¼″, length 6″)|(1)|.20 P
%X|—|24|||SH975C|HOSE, radiator outlet (5 ply hose, 2½″, length 6″)|(3)|.25 P
&(mh) R||||||HOSE, rubber, 1¼″, 3 ply, ft. (1 piece 6″ long required for hose SH168U)|—|.35 P''')
entry(r,'HOSE, rubber, 3 ply, 1⅜″, O. D. 1 9/16″, length 2⅝″ (ends dipped in cement). (For\n  extension LQ172A (2); header LQ413A (1); header LQ415A (1); extension LQ170A\n  (2).)',note='%X',ident='12128\n7',plate='15\n14',mfr='267',ord='LQ175A',qty='6',price='.08 P')
entry(r,'HOSE, rubber, 2″, 5 ply, ft. (1 piece 3½″ long required for hose SH975D)',note='&(mh) R',qty='—',price='.40 P')
entry(r,'HOSE, rubber, 2½″, 5 ply, ft. (3 pieces 6″ long required for hose SH975C; 1 piece\n  12½″ long required for hose SH975E; 2 pieces 3½″ long required for hose SH199B)',note='&(mh) R',qty='—',price='.50 P')
entry(r,'HOSE, water pipe (5 ply hose, 2½″, 12½″ long)',note='%X',ident='—',plate='24',ord='SH975E',qty='(1)',price='.50 P')
entry(r,'HOSE, (water) pump outlet (5 ply hose, 2″, length 3½″)',note='%X',ord='SH975D',qty='(1)',price='.20 P');stacked(r,ident='8109\n—',plate='13\n24')
assembly(r,'HOUSING, cam, with camshaft, left, assembly','259.10',note='&')
pieces(r,'''one —               cam SHAFT, left, with bearings, assembly,
seven (LQ40A) cam shaft BOLT, assembly,
one LQ43A       cam shaft distributor driving FLANGE,
one —               cam shaft driving SHAFT, upper, assembly,
one —               cam shaft driving shaft HOUSING, upper, assembly,
(gu) LQ86A      cam shaft driving shaft housing flange SHIM, medium,
(gu) LQ85A      cam shaft driving shaft housing flange SHIM, thick,
(gu) LQ87A      cam shaft driving shaft housing flange SHIM, thin,
one LQ84A       cam shaft driving shaft upper flange GASKET,
one LQ36A       cam shaft GEAR,
(gd) one LQ38A cam shaft gear SHIM, medium,
(gd) one LQ39A cam shaft gear SHIM, thick,''')

r=start(109)
pieces(r,'''(gd) one LQ37A cam shaft gear SHIM, thin,
one —               cam shaft HOUSING, assembly,
six —                 cam shaft rocker LEVER, left, assembly,
six —                 cam shaft rocker LEVER, right, assembly,
four (LQ88A)   STUD, ¼″ x 1 3/16″, threaded U. S. Std., 7/16″ and S. A. E.~                         9/16″, assembly,''')
component(r,'*seven LQ31A WIRE, lock, W & M Ga. No. 18 x 8″ (22).)',price='.01')
assembly(r,'HOUSING, cam, with cam shaft, right, assembly','259.10',note='&')
pieces(r,'''one —               cam SHAFT, right, with bearings, assembly,
seven (LQ40A) cam shaft BOLT, assembly,
one LQ43A       cam shaft distributor driving FLANGE,
one —               cam shaft driving SHAFT, upper, assembly,
one —               cam shaft driving shaft HOUSING, upper, assembly,
(gu) LQ86A      cam shaft driving shaft housing flange SHIM, medium,
(gu) LQ85A      cam shaft driving shaft housing flange SHIM, thick,
(gu) LQ87A      cam shaft driving shaft housing flange SHIM, thin,
one LQ84A       cam shaft driving shaft upper flange GASKET,
one LQ36A       cam shaft GEAR,
(gd) one LQ38A cam shaft gear SHIM, medium,
(gd) one LQ39A cam shaft gear SHIM, thick,
(gd) one LQ37A cam shaft gear SHIM, thin,
one —               cam shaft HOUSING, assembly,
six —                 cam shaft rocker LEVER, left, assembly,
six —                 cam shaft rocker LEVER, right, assembly,
four (LQ88A)   STUD, ¼″ x 1 3/16″, threaded U. S. Std. 7/16″ and S. A. E.~                         9/16″, assembly,''')
component(r,'*seven LQ31A WIRE, lock, W & M Ga. No. 18 x 8″ (22).)',price='.01')
assembly(r,'HOUSING, cam shaft, assembly','106.06',note='&',ident='12486',plate='13',qty='(2)')
pieces(r,'''seven LQ33A    cam shaft bearing lock SCREW,
one LQ75A       cam shaft driving shaft BUSHING, upper, small,''')
component(r,'*one LQ45A     cam shaft HOUSING (2)',ident='12124',plate='13',mfr='D12124',price='90.34')
component(r,'eighteen (LQ50A) cam shaft housing BOLT, assembly,')
component(r,'*two LQ35A     cam shaft housing core hole PLUG (4)',mfr='L50569',price='.10')
pieces(r,'''five LQ46A       cam shaft housing COVER,
one LQ47A       cam shaft housing COVER, (flywheel end),
one —               cam shaft housing end COVER, assembly,
one —               cam shaft housing PLUG,''')

r=start(110)
entry(r,'HOUSING, cam shaft, assembly—Continued.',note='&',ident='12486');composed(r)
pieces(r,'''seven — GASKET, copper asbestos, ⅜″,
one —    GASKET, copper asbestos, ⅝″,
one —    GASKET, copper asbestos, 1⅞″.)''')
assembly(r,'HOUSING, generator drive shaft end, with tachometer drive shaft bearing,\n  assembly','$5.01 P',note='&')
pieces(r,'''one —          generator drive shaft end HOUSING, lower, assembly,
one —          tachometer drive SHAFT, assembly,
one D13830 tachometer drive shaft BEARING,
one D29843 tachometer drive shaft BUSHING,
one D22921 tachometer drive shaft bushing inner BUSHING, flanged,
one D29920 tachometer drive shaft bushing inner BUSHING, plain,
one D29844 tachometer drive shaft gear pin SPRING.)''')
assembly(r,'HOUSING, generator drive shaft end, lower, assembly','3.15 P',note='&')
pieces(r,'''*one D29880 generator drive shaft end HOUSING, lower (1),
one D30374 generator drive shaft end housing PACKING,
one D29763 generator drive shaft end housing packing NUT,
one D13974 tachometer drive shaft oil cup.)''')
assembly(r,'HOUSING, cam shaft driving shaft, upper, assembly','2.18',note='&',qty='(2)')
component(r,'one LQ76A cam shaft driving shaft BUSHING, upper, small,')
component(r,'*one LQ81A cam shaft driving shaft HOUSING, upper (2)',mfr='8103',price='1.75')
component(r,'*one LQ82A cam shaft upper housing FLANGE (2)',mfr='B8109',price='.25')
component(r,'one —         NAIL, wire, finishing, 8d.)')
assembly(r,'HOUSING, generator top end, with brush arms, assembly','6.90 P',note='&',mfr='D13827')
component(r,'one {N. D. #1200} BEARING ball, radial, dia. 1.1811″, bore .3937″, face\n       {or equal}       .3543″,')
r[-1]['item_layout']=[dict(text='one',x=28,y=.5,width=16),dict(text='{N. D. #1200}\n{or equal}',x=44,width=45),dict(text='BEARING ball, radial, dia. 1.1811″, bore .3937″, face\n    .3543″,',x=89,width=158)]

r=start(111)
pieces(r,'''two D28929     ball bearing felt WASHER,
one D30134     generator ball bearing RETAINER (inner),
four D30449    generator BRUSH,
four D13829    generator brush ARM, assembly,
one D30314     generator brush arm COLLAR,
two (D30070) generator brush arm mounting STUD, (grounded), as-~                         sembly,
one (D29811)  generator brush arm mounting STUD, (long terminal),~                         assembly,
one (D30135)  generator brush arm mounting STUD, assembly,
one D30316     generator brush arm mounting stud CONNECTOR,
one D30315     generator brush arm mounting stud INSULATOR,
four D22645    generator brush arm small spring plain WASHER,
four D29818    generator brush arm SPRING (large),
four D30193    generator brush arm SPRING (small),
one D14178     generator top end HOUSING, assembly,
four —             PIN, split, brass, 1/16″ x ⅜″.)''')
assembly(r,'HOUSING, generator top end, assembly','6.87 P',note='&',mfr='D14178')
pieces(r,'''four D29855 generator brush arm spring STUD,
four D29849 generator brush arm spring stud BUSHING,
one D30152 generator brush arm stud insulating WASHER (inner),
one D30138 generator brush arm stud insulating WASHER,
*one D29803 generator top end HOUSING (1).)''')
entry(r,'HOUSING, governor, front half',note='&',ord='SH141A',qty='1',price='5.38')
entry(r,'HOUSING, governor, rear half',note='&',ord='SH145A',qty='1',price='2.97')
assembly(r,'HOUSING, radiator cooling fan, assembly','74.83',note='&')
pieces(r,'''one SH279B   radiator cooling fan ANGLE, outlet, bottom,
one SH279C   radiator cooling fan ANGLE, outlet, outside,
one SH279A   radiator cooling fan ANGLE, outlet, rear side,''')
component(r,'*one SH282C radiator cooling fan cut-off SHEET (1)',price='2.56')
pieces(r,'''one SH280D   radiator cooling fan FOOT, outlet end, inside,
one SH280B   radiator cooling fan FOOT, outlet end, outside,
one SH280C   radiator cooling fan FOOT, rear, inside,
one SH280A   radiator cooling fan FOOT, rear, outside,
one SH278C   radiator cooling fan foot filler STRIP,''')
component(r,'*one SH276A radiator cooling fan HOUSING, blind side (1)',price='15.37')
component(r,'*one SH277A radiator cooling fan HOUSING, inlet side (1)',price='15.37')

r=start(112);continued(r,'HOUSING, radiator cooling fan, assembly—Continued.')
pieces(r,'''one SH282A    radiator cooling fan housing SPIDER,
seven (SH279D) radiator cooling fan housing spider STUD, assembly,''')
component(r,'*one SH283A radiator cooling fan scroll SHEET (1)',price='$15.00')
pieces(r,'''five —              RIVET, button head, ¼″ x ¾″,
eighteen —       RIVET, button head, ¼″ x ⅞″,
four —             SCREW, wood, flat head, No. 12 (7/32—″) x 1″.)''')
entry(r,'HOUSING, radiator cooling fan ball race',note='&',ord='SH282B',qty='1',price='4.98')
entry(r,'HOUSING, starting crank',note='&',ord='SH399B',qty='1',price='5.18')
assembly(r,'HOUSING, transmission pinion shaft bearing, assembly','136.29',note='&',ident='6',plate='23')
component(r,'two (MX99) air pressure pump STUD, assembly,')
component(r,'two {Timken} BEARING, roller, assembly,\n       {6454–6420}')
r[-1]['item_layout']=[dict(text='two',x=28,y=.5,width=15),dict(text='{Timken}\n{6454–6420}',x=43,width=38),dict(text='BEARING, roller, assembly,',x=81,y=.5,width=163)]
pieces(r,'''one —                 transmission bevel pinion SHAFT, assembly,
one M249           transmission bevel pinion shaft bearing distance PIECE,
(gd) thirteen MX35 transmission bevel pinion shaft bearing distance SHIM,
one M246           transmission bevel pinion shaft flange COUPLING,''')
component(r,'*one M250         transmission pinion shaft bearing HOUSING (1)',ident='56',plate='22',ord='708',price='20.75')
pieces(r,'''one M252           transmission pinion shaft bearing housing packing DISC,
one M253           transmission pinion shaft bearing housing oil retaining~                            WASHER,
one M251           transmission pinion shaft packing GLAND,
four (MX22)       transmission pinion shaft packing gland BOLT, assembly.)''')
entry(r,'HOUSING, ventilating fan',note='&',ord='SH957A',qty='1',price='8.00')
assembly(r,'HOUSING, voltage regulator, assembly','.92 P',note='&',mfr='D13865')
pieces(r,'''*one D30364 voltage regulator HOUSING,
three D30367 voltage regulator housing EYELET,''')

r=start(113)
pieces(r,'''three D30368 voltage regulator housing insulating BUSHING,
six D29240 voltage regulator housing insulating WASHER,
three D20915 WASHER, plain, .314″ x .625″ x .031″.)''')
entry(r,'HOUSING, water pump bevel driver, with driver, assembly',note='&',ident='8239\n—',plate='19\n34',mfr='8426',qty='(1)',price='17.32');stacked(r,ident='8239\n—',plate='19\n34');composed(r)
pieces(r,'''one LQ156A water pump bevel DRIVER,
two LQ159A water pump bevel driver BUSHING,
one —          water pump bevel driver HOUSING, assembly.)''')
assembly(r,'HOUSING, water pump bevel driver, assembly','8.34',note='&')
component(r,'*one LQ160A water pump bevel driver bushing HOUSING, (flywheel\n                      end) (1)',ident='8065',plate='19',mfr='B8065',price='3.80')
component(r,'*one —          water pump bevel driver HOUSING (distributor end),\n                      assembly (1)',price='4.54')
component(r,'two (LQ164A) BOLT, S. A. E., drilled, ¼″ x 15/16″, threaded 9/16″, assem-\n                        bly.)')
assembly(r,'HOUSING, water pump bevel driver (distributor end), assembly','4.54',note='*',ident='8426',plate='15')
component(r,'*one LQ162A water pump bevel driver HOUSING (distributor end) (1)',ident='8064',plate='19',mfr='B8064',price='4.53')
component(r,'*one LQ163A DOWEL, 3/16″ x ⅜″.)',mfr='174',price='.01')
entry(r,'HUB, radiator cooling fan',note='&',ord='SH278B',qty='1',price='5.72')
assembly(r,'HUB, spark and throttle control lever, assembly','3.22',note='&',qty='(2)')
pieces(r,'''one SH964D spark and throttle control LEVER,
one —           spark and throttle control engine lever CONNECTION,~                      assembly,
one SH964B spark and throttle control lever HUB,
one —           PIN, steel, ⅛″ x 15/16″.)''')
entry(r,'HUB, spark and throttle control lever',note='&',ord='SH964B',qty='2',price='1.08')
entry(r,'IMPELLER, water pump',note='&',ident='12517',plate='17',mfr='B12517',ord='LQ146A',qty='1',price='2.25')
for note,mfr,ord_,item,qty,price in [
 ('(gy)&','S23','','INSERT, distance recorder drive cable shaft','1','.22 P'),
 ('&','D29729','','INSULATOR, distributor connector plate','2','.02 P'),
 ('&','D29632','','INSULATOR, distributor ignition coil and distributor head','4','.06 P'),
 ('&','D30315','','INSULATOR, generator brush arm mounting stud','1','.03 P'),
 ('&','D30510','','INSULATOR, generator end cover','1','.06 P'),
 ('&','','LQ330A','INSULATOR, high tension cable','24','.05 P'),
 ('&','W–J46','','INSULATOR, ignition battery (rubber)','24','.22 P'),
 ('&','D30052','','INSULATOR, ignition switch contact','1','.02 P'),
 ('&','D25470','','INSULATOR, voltage regulator','2','.01 P')]:
 entry(r,item,note=note,mfr=mfr,ord=ord_,qty=qty,price=price)

r=start(114)
entry(r,'INSULATOR, voltage regulator clip, with contact (under)',note='&',mfr='D29480',qty='1',price='$0.02 P')
entry(r,'INTENSIFIER, spark',note='&',ord='SH1021E',qty='24',price='.20 P')
entry(r,'JAR, ignition battery (hard rubber)',note='&',qty='1',price='1.00 P')
entry(r,'JAR, starting and lighting battery (hard rubber)',note='&',mfr='W–B173',qty='6',price='1.00 P')
entry(r,'JAW, starting crank',note='&',ord='SH119B',qty='1',price='5.18')
assembly(r,'JET, carburetor cap, assembly','.23',note='&',qty='(4)')
component(r,'*one LQ518A carburetor cap JET (4)',mfr='13374',price='.22')
component(r,'one LQ517A carburetor cap jet and main jet WASHER.)')
assembly(r,'JET, carburetor compensating (army) 170, assembly','.10',note='&',qty='(4)')
component(r,'*one LQ529A carburetor compensating JET (army) 170 (4)',mfr='13379',price='.09')
component(r,'one LQ530A carburetor compensating jet needle valve seat fiber\n                     WASHER.)')
assembly(r,'JET, carburetor main (army), assembly','.25',note='&',qty='(4)')
component(r,'one LQ517A carburetor cap jet and main jet WASHER,')
component(r,'*one LQ543A carburetor main JET (4).)',mfr='13397',price='.24')
entry(r,'JOINT, air duct mudhole cover (between radiator and roof)',note='%X',brit='M1039',ord='197',qty='1',price='.45')
entry(r,'JOINT, gasoline filler flange',note='&',brit='M1766',ord='236',qty='3',price='.50')
entry(r,'KEEPER, fixed, ⅝″, for 1¼″ strap. (For strap SH285D (1); strap SH443C (1).)',note='&(mh)R',qty='2',price='.02')
entry(r,'KEEPER, fixed, 1″, for 1½″ strap. (For strap SH239F (1).)',note='&(mh)R',qty='1',price='.05')
entry(r,'KEY, camshaft lower driving shaft (3/16″ x ⅛″ x ⅝″). (For water pump (1);\nshaft LQ94A (2).)',note='&',ident='159',plate='17',mfr='159',ord='LQ105A',qty='5',price='.01')
entry(r,'KEY, camshaft upper driving shaft (⅜″ x ⅛″ x 13/16″). (For shaft LQ73A (2);\nshaft LQ386A (4).)',note='&',ident='160',plate='16',mfr='160',ord='LQ78A',qty='8',price='.01')
entry(r,'KEY, clutch (sliding collar)',note='&',ident='10',plate='21',ord='SH861D',qty='4',price='.45')
entry(r,'KEY, clutch throwout lever feather',note='&',brit='M4172',ord='955',qty='5',price='.28')
entry(r,'KEY, distributor cam',note='&',mfr='D30008',qty='2',price='.03 P')
entry(r,'KEY, fan bevel gear box spindle',note='&',ord='SH196A',qty='2',price='.09')

r=start(115)
entry(r,'KEY, fan spindle (steel, ¼″ x ¼″ x 2″)',note='&',ord='SH958N',qty='1',price='.05')
entry(r,'KEY (flywheel)',note='&',ord='SH136B',qty='1',price='.74')
entry(r,'KEY, governor spindle',note='&',ord='SH144C',qty='1',price='.09')
entry(r,'KEY, hand starter (shaft) (⅛″ x ⅝″)',note='&',ord='SH65E',qty='2',price='.06')
entry(r,'KEY, valve spring collar',note='&',mfr='8024',ord='LQ298A',qty='48',price='.03')
for no,desc,qty,price in [
 ('A','spindle SH144B (1); spindle SH282D (1)','2','.02 P'),
 ('C','shaft M305 (2)','2','.02 P'),('G','spindle SH282D (1)','1','.04 P'),
 ('2','shaft SH101H (1)','1','.01 P'),('5','shaft SH900D (1)','1','.01 P'),
 ('7','arm SH142E (1)','1','.01 P'),('9','flange SH204A (1); spindle SH958A (2)','3','.01 P'),
 ('15','shaft SH944D (2)','2','.02 P'),('18','spindle M1131 (1); spindle M1132 (1)','2','.02 P')]:
 entry(r,'KEY, Woodruff, No. '+no+'. (For '+desc+'.)',note='&(sh)R',qty=qty,price=price)
entry(r,'KEY, ½″ x ¾″ x 1 13/16″. (For shaft M1402 (1); shaft M1544 (1).)',note='&',brit='20297–D89',ord='53',qty='4',price='.12')
entry(r,'KNOB, peephole cover plate operating (on left sponson (4); right sponson (3);\noutlook turret (4); main turret (9).)',note='&',brit='4X90',ord='633',qty='20',price='.38')
assembly(r,'LEAD, battery to telephone switch panel, 24″, assembly','.40 P',note='%(gy)X',qty='(4)')
component(r,'*one A266 low tension CABLE, length 41″ (1)',price='.30')
component(r,'two —       low tension cable TERMINAL, with threaded ferrule, 1/16″\n                  hole.)')
entry(r,'LEDGE, gasoline tank case lid side',note='*',brit='M2113',ord='328',qty='(2)',price='.90')
assembly(r,'LEVER, camshaft rocker, left, assembly','7.40',ident='8424',plate='13',qty='(12)')
component(r,'*one LQ62A camshaft rocker LEVER, left (12)',mfr='B8019',price='6.50')
pieces(r,'''one LQ64A camshaft rocker lever ROLLER,
one (LQ67A) camshaft rocker lever TAPPET, assembly,
(gd) one LQ68A camshaft rocker lever tappet SHIM, medium,
(gd) one LQ70A camshaft rocker lever tappet SHIM, thick,
(gd) one LQ69A camshaft rocker lever tappet SHIM, thin,
(gd) one LQ65K camshaft rocker lever tappet SHIM, solid, .032″ thick,
(gd) one LQ65L camshaft rocker lever tappet SHIM, solid, .05″ thick,
one LQ65B camshaft rocker roller pin SLEEVE,
one LQ65C camshaft rocker roller sleeve PIN.)''')
assembly(r,'LEVER, camshaft rocker, right, assembly','7.40',ident='8425',plate='13',qty='(12)')
component(r,'*one LQ60A camshaft rocker LEVER, right (12)',mfr='B8020',price='6.50')
component(r,'one LQ64A camshaft rocker lever ROLLER,')

r=start(116)
entry(r,'LEVER, camshaft rocker, right, assembly—Continued.',note='%X',ident='8425',plate='13');composed(r)
pieces(r,'''one (LQ67A) camshaft rocker lever TAPPET, assembly,
(gd) one LQ68A camshaft rocker lever tappet SHIM, medium,
(gd) one LQ70A camshaft rocker lever tappet SHIM, thick,
(gd) one LQ69A camshaft rocker lever tappet SHIM, thin,
(gd) one LQ65K camshaft rocker lever tappet SHIM, solid, .032″ thick,
(gd) one LQ65L camshaft rocker lever tappet SHIM, solid, .05″ thick,
one LQ65B camshaft rocker roller pin SLEEVE,
one LQ65C camshaft rocker roller sleeve PIN.)''')
assembly(r,'LEVER, carburetor throttle control shaft, assembly','$0.69',ident='8493',plate='15')
component(r,'*one LQ111A carburetor throttle control shaft LEVER (1)',mfr='B8493',price='.60')
component(r,'one (LQ112A) BOLT, S. A. E., drilled, ¼″ x 1⅛″, assembly.)')
for brit,ord_,item,qty,price in [
 ('M772','213A','clutch operating','1','9.72'),
 ('M4162','952','clutch throwout, left','1','5.15'),
 ('M4163','952','clutch throwout, right','1','4.75'),
 ('','SH953B','clutch throwout auxiliary operating','2','3.25'),
 ('M4164','952','clutch throwout operating','1','4.50'),
 ('M640','170','control rod rocking. (For center control rods (8); bracket M641 (1).)','10','1.15'),
 ('M2429','415','driver’s turret flap locking','1','.38'),
 ('M2426','414','driver’s turret flap raising','1','1.95'),
 ('','SH965H','engine control connecting','2','1.35'),
 ('M4132','172','foot brake horizontal','2','3.18'),
 ('','SH144A','governor','1','1.19')]:
 if brit=='M2429': entry(r,'LEVER, distributor advance',note='&',mfr='D29899',qty='4',price='.28 P')
 entry(r,'LEVER, '+item,note='&',brit=brit,ord=ord_,qty=qty,price=price)
assembly(r,'LEVER, high and low speed control, left, assembly','17.14',note='&')
pieces(r,'''two —      control lever trigger PIN, assembly,
one M744 control lever trigger SPRING,''')

r=start(117)
component(r,'one M739       hand lever TRIGGER,')
component(r,'*one M738B    high and low speed control LEVER, left (1)',ord='221',price='13.09')
pieces(r,'''one (M776)    high and low speed control lever BOLT, assembly,
one M741       high and low speed control lever PAWL,
one M755       high and low speed control lever pawl STOP,
one M748       high and low speed control lever spring PIN,
one —             high and low speed control lever trigger ROD, assembly,
one M742       pawl GUIDE,
one M745       trigger spring PIN,
two —             RIVET, button head, 5/16″ x 1¾″.)''')
assembly(r,'LEVER, high and low speed control, right, assembly','17.14',note='&')
pieces(r,'''two —            control lever trigger PIN, assembly,
one M744       control lever trigger SPRING,
one M739       hand lever TRIGGER,''')
component(r,'*one M738A    high and low speed control LEVER, right (1)',ord='221',price='13.09')
pieces(r,'''one (M776)    high and low speed control lever BOLT, assembly,
one M741       high and low speed control lever PAWL,
one M755       high and low speed control lever pawl STOP,
one M748       high and low speed control lever spring PIN,
one —             high and low speed control lever trigger ROD, assembly,
one M742       pawl GUIDE,
one M745       trigger spring PIN,
two —             RIVET, button head, 5/16″ x 1¾″.)''')
for ident,plate,brit,ord_,item,price in [
 ('—','6','M759','223','high speed selector, left','9.50'),
 ('—','6','M758','223','high speed selector, right','9.50'),
 ('','','M4133','172','low speed brake horizontal, left','3.18'),
 ('','','M4134','172','low speed brake horizontal, right','3.18'),
 ('','','M756','225','low speed selector, left','4.50'),
 ('—','6','M757','225','low speed selector, right','4.50')]:
 entry(r,'LEVER, '+item,note='&',ident=ident,plate=plate,brit=brit,ord=ord_,qty='1',price=price)
assembly(r,'LEVER, periscope hole cover, assembly','.53',note='&',qty='(4)')
component(r,'*one M2410      periscope hole cover LEVER (4)',ord='438',price='.39')
component(r,'*one SH438D    periscope hole cover lever locking LUG',price='.05')
pieces(r,'''one SH438C     periscope lever RING,
one —               RIVET, button head, 5/16″ x ⅝″,~                          For outlook turret (2); roof door (1); driver’s turret~                       (1).)''')

r=start(118)
assembly(r,'LEVER, reverse operating, assembly','$13.17',note='&')
pieces(r,'''two —      control lever trigger PIN, assembly,
one M744 control lever trigger SPRING,
one M739 hand lever TRIGGER,
one M742 pawl GUIDE,
one M780 reverse lever PAWL,''')
component(r,'*one M177 reverse operating LEVER (1)',ord='214',price='10.45')
pieces(r,'''one —      reverse operating lever trigger ROD, assembly,
one M745 trigger spring PIN,
two —      RIVET, button head, 5/16″ x 1¾″.)''')
assembly(r,'LEVER, spark and throttle control, assembly','7.48',note='&',ident='50',plate='2',qty='(2)')
pieces(r,'''one SH964A spark and throttle control lever BRACKET,
one SH964C spark and throttle control lever friction DISC,
two SH964F spark and throttle control lever friction WASHER,
one —           spark and throttle control lever HUB, assembly,
one —           spark and throttle control lever STUD, assembly.)''')
for ident,plate,brit,ord_,item,qty,price in [
 ('','','','SH964D','spark and throttle control','2','1.75'),
 ('—','12','','SH970A','spark control bell crank, lower','1','1.45'),
 ('—','12','','SH970C','spark control bell crank, upper','1','1.35'),
 ('','','','SH67B','starting crank','1','3.15'),
 ('—','12','','SH966F','throttle control bell crank','1','1.25'),
 ('8','31–32','M330','686','transmission brake','4','4.12')]:
 entry(r,'LEVER, '+item,note='&',ident=ident,plate=plate,brit=brit,ord=ord_,qty=qty,price=price)
assembly(r,'LEVER, transmission high speed brake, assembly','3.14',note='&',ident='11',plate='30',qty='(2)')
component(r,'*one M355B transmission high speed brake LEVER, left (2)',ord='697',price='1.55')
component(r,'*one M355A transmission high speed brake LEVER, right (2)',ord='697',price='1.55')
component(r,'four —         RIVET, button head, ⅜″ x 1⅜″.)')
entry(r,'LEVER, transmission vertical shifter shaft, bottom',note='&',ident='21',plate='23',brit='M304',ord='714',qty='1',price='3.96')
entry(r,'LEVER, transmission vertical shifter shaft, top',note='&',ident='16',plate='23',brit='M303',ord='714',qty='1',price='2.68')

r=start(119)
assembly(r,'LID, accessories and ration box, assembly','6.53',note='&',qty='(2)')
component(r,'*one M4040A accessories and ration box LID (2)',ord='592',price='5.57')
pieces(r,'''two M2158    HINGE, butt, 2″ x 4¼″,
six —             RIVET, button head, ¼″ x ⅞″.)''')
assembly(r,'LID, ammunition storage, assembly','4.82',note='&',qty='(2)')
component(r,'*one SH576G ammunition storage LID (2)',price='3.68')
pieces(r,'''one SH576D ammunition storage lid BATTEN, long,
one SH576F ammunition storage lid BATTEN, short, left,
one SH576E ammunition storage lid BATTEN, short, right,
two SH576K HINGE, 2½″ x 2½″,
six —             RIVET, button head, ¼″ x 9/16″,
fourteen —    SCREW, wood, countersunk head, No. 10 (3/16+″) x ⅝″.)''')
entry(r,'LID, 6-pdr. gun box, left',note='&',ord='SH942E',qty='1',price='3.75')
entry(r,'LID, 6-pdr. gun box, right',note='&',ord='SH942D',qty='1',price='3.75')
entry(r,'LINING, brake, 1⅞″ wide, ¼″ thick, ft. (Raybestos or equal) (2 pieces 27⅜″ long\n   required for lining MX109; 2 pieces 13⅝″ long required for lining M364)',note='(mh)&',ident='3',plate='30',qty='—',price='.45 P')
entry(r,'LINING, brake, 2″ wide, 3/16″ thick, ft. (Raybestos or equal) (1 piece 27¾″ long\n   required for clutch throwout stop band M4158)',note='&(mh)',ord='—',qty='—',price='1.02')
entry(r,'LINING, brake, 2¾″ wide, 5/16″ thick ft. (Raybestos or equal) (4 pieces 36 7/16″\n   long required for lining MX107)',note='(mh)&',qty='—',price='.62 P')
entry(r,'LINING, brake, 3¾″ wide, 5/16″ thick, ft. (Raybestos or equal) (4 pieces 35⅞″\n   long required for lining MX108)',note='(mh)&',qty='—',price='.84 P')
entry(r,'LINING, clutch',note='&',ord='SH997C',qty='1',price='4.50')
entry(r,'LINING, clutch throwout stop',note='&',brit='M4159',ord='954',qty='1',price='.75')
for note,ident,plate,brit,ord_,item,qty,price in [
 ('%X','2','31','M337','686','brake band suspension','4','3.75'),
 ('&','—','6','M771','212','brake connecting','8','.32'),
 ('&','','','','SH944C','clutch swing, long','1','1.74'),
 ('&','','','','SH944B','clutch swing, short','1','1.24'),
 ('%X','—','6','M769','211','foot brake','2','3.25'),
 ('&','—','6','M770','212','foot brake suspension','1','1.95'),
 ('&','—','6','M784','211','front control swing','4','3.95'),
 ('%X','—','6','M763','211','low speed brake','2','3.25')]:
 entry(r,'LINK, '+item,note=note,ident=ident,plate=plate,brit=brit,ord=ord_,qty=qty,price=price)
assembly(r,'LINK, low speed brake suspension, assembly','2.05',note='&',qty='(2)')
component(r,'*one M760 low speed brake suspension LINK (2)',ord='212',price='1.56')
component(r,'one —       low speed brake suspension PIN, assembly.)')
entry(r,'LINK, low speed connecting',note='&',ident='—',plate='6',brit='M762',ord='210',qty='2',price='5.04')

r=start(120)
assembly(r,'LINK, track, assembly','$31.70',note='&',ord='SH50A',qty='(156)')
component(r,'*two M1265 track LINK, left half (312)',ident='1',plate='26',ord='51',price='6.50')
component(r,'*two M1261 track LINK, right half (312)',ord='51',price='6.50')
pieces(r,'''two M1263 track link BUSHING,
two —         track link PIN, assembly.)''')
entry(r,'LOCK, carburetor cap jet',note='&',mfr='13539',ord='LQ559A',qty='4',price='.01')
entry(r,'LOCK, carburetor to intake header stud nut',note='%X',mfr='L13151',ord='LQ423A',qty='1',price='.06')
entry(r,'LOCK, control lever',note='%X',ident='—',plate='6',brit='M749',ord='227',qty='1',price='.26')
entry(r,'LOCK, crank case oil filler cover',note='&',mfr='8163',ord='LQ219A',qty='2',price='.10')
assembly(r,'LOCK, door, left, assembly','2.23',note='&',ident='61',plate='2',qty='(4)')
pieces(r,'''one M719       door lock CATCH, left,
one E20/21195 door lock HANDLE,
one M721       door lock SPINDLE,
one M722       door lock SPRING,''')
component(r,'*one M715      lock BRACKET, left (4)',ord='546',price='.38')
component(r,'*one M717      lock packing PIECE, left (4)',ord='546',price='.22')
pieces(r,'''two —             RIVET, button head, ¼″ x ¾″,
two —             RIVET, button head, ¼″ x 1¼″,~                         For door lock, left (2); main turret side flap (1).)''')
assembly(r,'LOCK, door, right, assembly','2.23',note='&',qty='(2)')
pieces(r,'''one M720       door lock CATCH, right,
one E20/21195 door lock HANDLE,
one M721       door lock SPINDLE,
one M722       door lock SPRING,''')
component(r,'*one M716      lock BRACKET, right (4)',ord='546',price='.38')
component(r,'*one M718      lock packing PIECE, right (4)',ord='546',price='.22')
pieces(r,'''two —             RIVET, button head, ¼″ x ¾″,
two —             RIVET, button head, ¼″ x 1¼″.)''')

r=start(121)
assembly(r,'LOCK, gasoline tank cover, assembly','1.71',note='&',qty='(2)')
component(r,'one M722     door lock SPRING,')
component(r,'*one M1793  gasoline tank cover latch SPINDLE (2)',ord='538',price='.44')
component(r,'*one M716    lock BRACKET (4)',ord='546',price='.38')
component(r,'one M720     lock CATCH, right,')
component(r,'*one M718    lock packing PIECE, right (4)',ord='546',price='.22')
pieces(r,'''two —           RIVET, button head, ¼″ x ¾″,
two —           RIVET, button head, ¼″ x 1¼″.)''')
entry(r,'LOCK, lower crank case sump cover',note='%X',ident='31',plate='14',mfr='8130',ord='LQ201A',qty='1',price='.35')
entry(r,'LOCK, oil pump upper screen nut',note='%X',ident='—',plate='12',mfr='8536',ord='LQ459A',qty='1',price='.02')
entry(r,'LOCK, turret roof door chubb, with three keys',note='&',brit='M45/21421',ord='377',qty='1',price='1.50')
entry(r,'LOOP, strap, No. 1. (For strap fastener, No. 2 (1).)',note='(mh)&',ord='A8177',qty='4',price='.07 P')
assembly(r,'LUBRICATOR, transmission mechanical, assembly','37.32',note='&')
pieces(r,'''six SH102H     transmission mechanical lubricator adjusting BUTTON,
six (SH101Q) transmission mechanical lubricator BOLT, assembly,
one SH101P    transmission mechanical lubricator cam SHAFT,
six SH101G     transmission mechanical lubricator center piece~                           WASHER,
one SH105A    transmission mechanical lubricator COVER,
six SH101A     transmission mechanical lubricator cylinder pump~                           HEADER,
six SH102B     transmission mechanical lubricator delivery CONNEC-~                           TION,
six SH102D     transmission mechanical lubricator delivery screw CAP,
six SH102E     transmission mechanical lubricator delivery tube NUT,
six SH101L     transmission mechanical lubricator ECCENTRIC,
six SH101M    transmission mechanical lubricator eccentric PIN,
six SH102F     transmission mechanical lubricator feed adjusting CAM,
six SH103A     transmission mechanical lubricator feed pump HEADER,~                           M–G,
twelve SH101J transmission mechanical lubricator flat SPRING,
six SH102G     transmission mechanical lubricator force feed ECCEN-~                           TRIC,
six SH105C     transmission mechanical lubricator (lower plunger)~                           YOKE,
six SH105E     transmission mechanical lubricator oil PAN,''')

r=start(122)
continued(r,'LUBRICATOR, transmission mechanical, assembly—Continued.')
pieces(r,'''six SH101E    transmission mechanical lubricator PLUG,
six SH101K   transmission mechanical lubricator PLUNGER, lower,
six SH104B   transmission mechanical lubricator PLUNGER, upper,
six SH104F   transmission mechanical lubricator sight feed TUBE,
six SH105G   transmission mechanical lubricator snap PIN,
six SH104K   transmission mechanical lubricator suction screen BODY,
six SH104L   transmission mechanical lubricator suction screen~                         STRAINER,
six SH104D   transmission mechanical lubricator suction screen TOP,
six SH101B   transmission mechanical lubricator suction TUBE,
six SH104E   transmission mechanical lubricator suction tube screen~                         BOTTOM,
six SH104C   transmission mechanical lubricator suction tube~                         SPRING,
six SH105B   transmission mechanical lubricator upper plunger YOKE,
one SH103B  transmission mechanical lubricator worm GEAR,
one —            PACKING, 3/16″ x 6″,
six —             PIN, brass, 1/16″ x ⅛″,
six —             PIN, split, 3/32″ x ⅜″,
six —             SCREW, machine, headless, No. 7—32 x ¼″,
six —             SCREW, machine, round head, brass, No. 10—24 x ¼″,
six —             SCREW, machine, round head, No. 10—24 x ¼″.)''')
entry(r,'LUG, low speed brake band stop',note='&',brit='MX86',ord='681',qty='2',price='$0.42')
entry(r,'LUG, sponson. (For holding sponson in position.)',note='*',brit='M2839',qty='2',price='1.00')
entry(r,'LUG, track brake band stop',note='&',brit='MX87',ord='692',qty='2',price='.42')
entry(r,'MANIFOLD, cylinder water inlet',note='%X',ident='12123',plate='15',mfr='C12123',ord='LQ168A',qty='2',price='15.00')
assembly(r,'MANIFOLD, exhaust, left, assembly','33.32',note='%(go)X')

r=start(123)
component(r,'*one SH599A exhaust MANIFOLD, left (2)',price='27.50')
component(r,'*one SH402G manifold ELBOW (2)',price='5.75')
component(r,'one —           BOLT, U. S. Std., hexagon head, ½″ x 3″, with plain nut.)')
assembly(r,'MANIFOLD, exhaust, right, assembly','33.32',note='%(go)X')
component(r,'*one SH599A exhaust MANIFOLD, right (2)',price='27.50')
component(r,'*one SH402G manifold ELBOW (2)',price='5.75')
component(r,'one —           BOLT, U. S. Std., hexagon head, ½″ x 3″, with plain nut.)')
entry(r,'MANIFOLD, lower half crank case oil',note='&',ident='30',plate='14',mfr='B12038',ord='LQ181A',qty='1',price='4.70')
entry(r,'MOTOR, starting, 12 volt (Bijur Lighting Co.)',note='(gy)&',ord='SH133A',qty='1',price='50.00')
entry(r,'MOUNT, governor thrust bearing',note='&',ord='SH143B',qty='1',price='1.06')
assembly(r,'MOUNT, 7½″ ball (Browning tank machine gun), assembly','78.96',ident='40',plate='2',qty='(5)')
pieces(r,'''one —              Browning tank machine gun CRADLE, assembly,
one SH1711A 7½″ ball mount BALL,
one SH1711B 7½″ ball mount COUNTERWEIGHT,
two SH1712F 7½″ ball mount depression limit SCREW,
two —             SCREW, cap, U. S. Std., hexagon head, ½″ x 1¼″,
two —             WASHER, lock, ½″.)''')
entry(r,'NAIL, upholstering, ½″. (For driver’s seat (21).)',note='(mh)&',qty='21',price='.01')
entry(r,'NAIL, wire, 2d. (For carburetor throttle control connecting shaft, assembly (2);\n   throttle control shaft, assembly (2); rod LQ315A (2).)',note='(mh)&',qty='6',price='.01 P')
entry(r,'NAIL, wire finishing, 3d. (For funnel rack (12).)',note='(mh)&',qty='12',price='.01 P')
entry(r,'NAIL, wire finishing, 8d. (For cam shaft driving shaft upper housing (1).)',note='(mh)&',mfr='L186',ord='LQ83A',qty='2',price='.01 P')
entry(r,'NIPPLE, (engine) oil tank suction oil tube',note='%X',ord='SH207E',qty='1',price='.08 P')
entry(r,'NIPPLE, pipe, close, ¼″ x ⅞″ (black). (For tube C8015.)',note='(pf)X',ord='B6498B',qty='1',price='.03 P')
for note,size,qty,ending in [
 ('(pf)&','¼″ x 1⅛″','1',' (1).)'),('(pf)&','¼″ x 1¼″','2',' (2).)'),
 ('%(pf)X','¼″ x 1½″','3',')'),('(pf)&','¼″ x 2⅝″','1',' (1).)'),
 ('(pf)&','¼″ x 3½″','1',' (1).)'),('(pf)&','⅜″ x 1¼″','1',' (1).)')]:
 entry(r,'NIPPLE, pipe, W. I., '+size+'. (For combination valve to flexible tube con-\n   nection'+ending,note=note,qty=qty,price='.03 P')
entry(r,'NIPPLE, pipe, W. I., ½″ x 1¼″. (For pipe SH199C (1).)',note='(pf)&',ord='199',qty='1',price='.03 P')

r=start(124)
entry(r,'NIPPLE, pipe, W. I., ½″ x 2″. (For combination valve to flexible tube connec-\n   tion (1).)',note='(pf)&',qty='1',price='$0.03 P')
entry(r,'NIPPLE, pipe, W. I., ½″ x 3¼″. (For combination valve to flexible tube con-\n   nection (1).)',note='(pf)&',qty='1',price='.04 P')
entry(r,'NIPPLE, pipe, W. I., ½″ x 3½″. (For combination valve to flexible tube con-\n   nection (1).)',note='(pf)&',qty='1',price='.04 P')
entry(r,'NIPPLE, pipe, W. I., ¾″ x 2″. (For pipe M1229 (1).)',note='(pf)&',ident='—',plate='24',ord='169',qty='1',price='.04 P')
for size,qty in [('1″ x 1½″','3'),('1″ x 3″','1'),('1″ x 3½″','1')]:
 entry(r,'NIPPLE, pipe, W. I., '+size+'. (For pipe M1229 ('+qty+').)',note='(pf)&',ident='—',plate='24',qty=qty,price='.04 P')
entry(r,'NIPPLE, pipe, W. I., close, ¼″. (For regulating tank flexible connection (2).)',note='%(pf)X',qty='2',price='.03 P')
entry(r,'NIPPLE, pipe, W. I., close, ½″ x 1¾″. (For housing M250 (1).)',note='%(pf)X',qty='1',price='.03 P')
entry(r,'NIPPLE, short, ¼″ x 1½″ (G. I.). (For tube C8012 (1).)',note='(pf)X',ord='B6498QA',qty='3',price='.03 P')
entry(r,'NIPPLE, water tank filler pipe',note='%X',ord='SH199G',qty='1',price='.12 P')
entry(r,'NUT, air pressure pump check',note='%X',ord='SH901B',qty='4',price='.06')
entry(r,'NUT, air pressure pump stud (jam, S. A. E., ½″, ⅜″ thick)',note='%X',brit='MX102',ord='713',qty='2',price='.02 P')
entry(r,'NUT, ball bearing retaining. (For distributor lower bearing (1).)',note='&',mfr='D29734',qty='2',price='.10 P')
entry(r,'NUT, battery shelf support holding down bolt',note='%X',ord='SH996D',qty='6',price='.15')
entry(r,'NUT, cam shaft driving shaft housing packing',note='&',ident='8066',plate='13',mfr='B8066',ord='LQ91A',qty='2',price='.54')
entry(r,'NUT, cam shaft housing cover oil connection',note='&',mfr='B8122',ord='LQ57A',qty='2',price='.14')
entry(r,'NUT, cam shaft lower driving shaft',note='&',mfr='8142',ord='LQ106A',qty='2',price='.35')
entry(r,'NUT, carburetor altitude air valve and yoke end bolt',note='&',mfr='13362',ord='LQ514A',qty='6',price='.04')
entry(r,'NUT, carburetor float cover wing',note='%X',mfr='13386',ord='LQ585A',qty='4',price='.02')
entry(r,'NUT, castle, S. A. E., 7/16″. (For bolt MX26)',note='&(sh)R',qty='32',price='.01 P')
entry(r,'NUT, castle, S. A. E., ½″. (For stud MX14; stud MX98; bolt MX8; bolt MX11;\n   stud MX12.)',note='&(sh)R',qty='30',price='.01 P')
entry(r,'NUT, castle, S. A. E., ⅝″. (For stud A7681; shaft SH65L; bolt M317.)',note='%(sh)R',qty='9',price='.01 P')
entry(r,'NUT, castle, S. A. E., ¾″. (For stud MX10; Stud MX36; stud MX9; stud MX5;\n   stud MX25; spindle SH282D (2); spindle SH144B; bolt MX1.)',note='%(sh)R',qty='47',price='.01 P')
entry(r,'NUT, castle, S. A. E., ⅞″. (For bolt M318.)',note='%(sh)R',qty='6',price='.01 P')
