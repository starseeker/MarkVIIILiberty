"""Photograph-led transcription of printed pages 205–224.
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
def add(page,content):
 r=start(page);append_rows(r,content);return r
def append_rows(r,content):
 for line in content.strip().splitlines():
  values=line.split('|');assert len(values)==9,line
  r.append(row(*[v.replace('~','\n') for v in values]))

r=add(205,'''&|8101|13|8101||LQ27A|SCREW, special, No. 8 x ½″|48|.01
&|||8219||LQ30A|SCREW, special, No. 10 x 5/16″|8|.06
|||W-S1021|||SCREW, starting and lighting battery wood|16|.01 P
%X||||M1473|60|SCREW, tension adjusting (track)|4|6.79''')
stacked(r,ident='54\n11',plate='2\n28')
entry(r,'SCREW, track adjusting screw locking',note='%X',brit='M1475',ord='60',qty='4',price='.40')
stacked(r,ident='7\n5',plate='10\n28')
append_rows(r,'''%X||||MX60|712|SCREW, transmission brake anchor bracket end stop|10|.12
%X|3|31||M333|687|SCREW, transmission brake band adjusting|4|2.00
%X|3|32||MX38|712|SCREW, transmission brake band anchor to end|12|.06
%X||||MX76|712|SCREW, transmission brake band to anchor bracket|4|.10''')
assembly(r,'SCREW, transmission brake band stop, assembly','.12',qty='(4)',ident='9',plate='31, 32')
component(r,'*one M343 transmission brake band stop SCREW (4)',ord='687',price='.10')
component(r,' one —     NUT, plain, S. A. E., hexagon, ½″.)')
assembly(r,'SCREW, transmission brake stop bar set, assembly','.14',qty='(4)')
component(r,'*one MX88 transmission brake stop bar set SCREW (4)',ord='687',price='.12')
component(r,' one —     NUT, plain, S. A. E., hexagon, ½″.)')
append_rows(r,'''&||||M390|669|SCREW, transmission frame holding|4|1.12
%X|9|30||M358|698|SCREW, transmission high speed brake adjusting|2|1.15''')
assembly(r,'SCREW, transmission high speed brake stop set, assembly','.07',qty='(6)',ident='4',plate='30')
component(r,'*one M400 transmission high speed brake stop set SCREW (6)',ord='698',price='.05')
component(r,' one —     NUT, plain, S. A. E., ⅜″.)')
assembly(r,'SCREW, voltage regulator armature regulating spring adjusting, assembly','.11 P',note='&')
pieces(r,''' one D30531 voltage regulator armature regulating SPRING,
*one D30141 voltage regulator armature regulating spring adjusting~                   SCREW (1),
 one D30142 NUT, plain, brass, No. 8—36 x 19/64″ x .125″ thick.)''')
assembly(r,'SCREW, voltage regulator contact, assembly','.11 P',note='&')
pieces(r,'''*one D13795 voltage regulator contact SCREW,
 one D21748 NUT, plain, No. 5—50 x 7/32″ x 7/64″ thick.)''')
assembly(r,'SCREW, voltage regulator mounting terminal, with thick bushing, assembly','.06 P',note='&')
component(r,' one D25469 voltage regulator mounting terminal screw insulating\n                   BUSHING, thick,')

r=start(206)
entry(r,'SCREW, voltage regulator mounting terminal, with thick bushing assembly—Con.',note='&')
composed(r)
pieces(r,'''*one D30143 SCREW, slotted head, No. 6—40 x .358″,
 one D24336 WASHER, plain, brass, .147″ x .312″ x .0254″.)''')
assembly(r,'SCREW, voltage regulator mounting terminal, with thin bushing, assembly','$0.06 P',qty='(6)',note='&')
pieces(r,''' one D25468 voltage regulator mounting terminal screw insulating~                   BUSHING, thin,
*one D30143 SCREW, slotted head, No. 6—40 x .358″,
 one D24336 WASHER, plain, brass, .147″ x .312″ x .0254″.)''')
append_rows(r,'''&|41|14|154||LQ165A|SCREW, water pump bevel driver housing (⅜″ x 3¼″)|1|.20
%(sh)R||||||SCREW, wood, flathead, No. 6 (9/64−″) x ½″.  (For clip SH373J (2); rest SH550E~   (5); rest SH573K (5).)|12|.01 P
%(sh)R||||||SCREW, wood, flathead, brass, No. 8 (5/32+″) x ½″.  (For hinge M2444 (3).)|6|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 8 (5/32+″) x ¾″.  (For bracket A3997 (2); bracket~   A3998 (2); securing funnel rack, assembly (6).)|10|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 8 (5/32+″) x ⅞″.  (For funnel rack, assembly (2).)|2|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 8 (5/32+″) x 1″.  (For funnel rack, assembly (2).)|2|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 8 (5/32+″) x 1½″.  (For funnel rack, assembly (22).)|22|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 9 (11/64+″) x ⅝″.  (For hasp SH568M (8).)|16|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 10 (3/16+″) x ⅝″.  (For ammunition storage lid,~   assembly (14); packing M1753A (18).)|46|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 10 (3/16+″) x ¾″.  (For batten SH579B (3); plate~   SH571C (16).)|22|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 10 (3/16+″) x 1¼″.  (For batten SH568F (9); exten-~   sion B5877 (2).)|38|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 12 (7/32−″) x 1″.  (For securing spare parts container~   to strip SH278C (4).)|4|.01 P
%(sh)R||||||SCREW, wood, flathead, No. 14 (¼−″) x 2″.  (For block M3064B (1); block~   M3064A (1).)|2|.01 P''')

r=add(207,'''%(sh)R||||||SCREW, wood, round head, brass, No. 4 (7/64+″) x ¾″.  (For oil pressure gage (4).)|4|.01 P
%(sh)R||||||SCREW, wood, round head, No. 6 (9/64−″) x ½″.  (For air pressure gage (3).)|(gt) 12|.01 P
%(sh)R||||||SCREW, wood, round head, No. 6 (9/64−″) x 1″.  (For hinge SH373L (1); hinge~   SH373K (1).)|2|.01 P
%(sh)R||||||SCREW, wood, round head, No. 8 (5/32+″) x ¾″.  (For strap A3990 (2).)|2|.01 P
%(sh)R||||||SCREW, wood, round head, No. 8 (5/32+″) x 1″.  (For cleat A4025 (5).)|5|.01 P
%(sh)R||||||SCREW, wood, round head, brass, No. 10 (3/16+″) x ½″.  (For (Officer’s) map board~   hinge M2444 (6).)|6|.01 P
%(sh)R||||||SCREW, wood, round head, No. 10 (3/16+″) x ¾″.  (For box SH942A (28); box~   SH942B (28).)|56|.01 P
%(sh)R||||||SCREW, wood, No. 10 (3/16+″) x 1½″.  (For shelf SH992C (7).)|7|.01 P
%(sh)R||||||SCREW, wood, No. 18 (19/64−″) x 1¼″.  (For piece M1753B (5).)|5|.01 P
%(sh)R||||||SCREW, wood, No. 18 (19/64−″) x 1½″.  (For piece M1753C (5).)|5|.01 P
%X|||||SH1712F|SCREW, 7½″ ball mount depression limit|10|.04 P''')
assembly(r,'SCREW, 9″ ball mount gun locking set, assembly','.26',note='(c) %X',qty='(10)')
component(r,'*one B33N 9″ ball mount gun locking set SCREW (10)',price='.24')
component(r,' two —     NUT, jam, U. S. Std., 5/16″.)')
append_rows(r,'''(c)X|||||B33L|SCREW, 9″ ball mount key stop (A. S. M. E., flat fillister head, 1″ x 9/16″)|5|.31
&||||M1041|197|SEAL, air duct (between radiator and roof)|1|.48
&||||M1040|197|SEAL, air duct, corner (between radiator and roof)|1|.15''')
assembly(r,'SEAT, carburetor needle valve, assembly','.19',note='&',qty='(2)')
component(r,' one LQ530A carburetor compensating jet needle valve seat fiber\n                   WASHER,')
component(r,'*one LQ546A carburetor needle valve SEAT (2)',mfr='13400',price='.16')
component(r,'*one LQ547A carburetor needle valve seat WASHER.)',mfr='13401',price='.02')
assembly(r,'SEAT, driver’s (adjustable), assembly','5.64',ident='46',plate='2')
component(r,'*one M791    driver’s SEAT (adjustable) (1)',ord='291',price='1.75')
component(r,' four SH289E driver’s seat BEARING,')
component(r,'*two SH291X driver’s seat CLIP (2)',price='.18')
component(r,'twenty-one —     NAIL, upholstering, ½″,')
component(r,' eight —         RIVET, button head, ⅝″ x 1⅛″.)')
entry(r,'SEAT, oil pump relief valve',note='%X',ident='—',plate='33',mfr='8368',ord='LQ445A',qty='1',price='.14')
assembly(r,'SEAT, sponson, left, assembly','3.76',note='&')
component(r,'*one M2818B sponson SEAT, left (1)',ord='474',price='1.08')
component(r,' two M2815   sponson seat HINGE, male,')

r=start(208)
entry(r,'SEAT, sponson, left, assembly—Continued.',note='&');composed(r)
pieces(r,''' one M2819   sponson seat SUPPORT,
 four —      RIVET, button head, 7/16″ x 1″,
 two —       RIVET, button head, 7/16″ x 1⅛″.)''')
assembly(r,'SEAT, sponson, right, assembly','$3.76',note='&')
component(r,'*one M2818A sponson SEAT, right (1)',ord='474',price='1.08')
pieces(r,''' two M2815   sponson seat HINGE, male,
 one M2819   sponson seat SUPPORT,
 four —      RIVET, button head, 7/16″ x 1″,
 two —       RIVET, button head, 7/16″ x 1⅛″.)''')
entry(r,'SECTOR, carburetor gear',note='&',mfr='13392',ord='LQ539A',qty='2',price='.28')
assembly(r,'SEMAPHORE, assembly','62.34',note='&')
pieces(r,''' two —       semaphore ARM, assembly,
 two X261    semaphore arm WASHER,
 one —       semaphore bottom bearing BLOCK, grooved, assembly,
 one —       semaphore bottom bearing BLOCK, assembly,
 one X248    semaphore bottom bearing block BUSHING,
 one X252    semaphore bottom CAP,
 one —       semaphore bottom SHAFT, assembly,
 one X264    semaphore bottom SPROCKET, near side,
 one X265    semaphore bottom SPROCKET, off side,
 one SH802A  semaphore CHAIN,
 one X249    semaphore control RATCHET,
 one X287    semaphore control ratchet SPRING,
 one SH801B  semaphore locking SCREW,
 one —       semaphore POST, assembly,
 one X310    semaphore ratchet spring WASHER.''')

r=start(209)
pieces(r,''' one X267    semaphore register DISK,
 two SH801A  semaphore roller CHAIN,
 one —       semaphore sprocket HANDLE, near side, assembly,
 one —       semaphore sprocket HANDLE, off side, assembly,
 one X253    semaphore STIRRUP,
 two X256    semaphore top bearing BLOCK,
 one X250    semaphore top CAP,
 one X258    semaphore top SHAFT,
 two —       semaphore top SPROCKET, assembly,
 four —      SCREW, cap, U. S. Std., flathead, 3/16″ x ⅝″,
 two —       SCREW, cap, U. S. Std., round head, 3/16″ x ½″.)''')
entry(r,'SEPARATOR, high tension cable',note='%X',ord='LQ327A',qty='2',price='.14 P')
assembly(r,'SEPARATOR, jockey pulley arm, assembly','1.36')
component(r,'*one SH234G jockey pulley arm SEPARATOR (1)',ord='234',price='1.28')
pieces(r,''' two —       NUT, crown, U. S. Std., ½″,
 two —       PIN, split, ⅛″ x 1″.)''')
append_rows(r,'''&|||W-J50|||SEPARATOR, starting and lighting battery|72|.04 P
%X|||D14/21202||647|SHACKLE, towing|4|4.08''')
assembly(r,'SHAFT, air pressure pump, assembly','7.54',note='&',ident='3',plate='5')
component(r,'*one SH900D air pressure pump SHAFT (1)',price='7.52')
component(r,' one —     NUT, plain, U. S. Std., hexagon, ½″.)')
assembly(r,'SHAFT, cam, left, with bearings, assembly','37.05',note='&')
component(r,' one — cam SHAFT, left, assembly,')
for i in range(1,7):component(r,f' one — cam shaft BEARING, No. {i}, assembly,')
component(r,' one — cam shaft BEARING, flywheel end, assembly.)')
assembly(r,'SHAFT, cam, left, assembly','25.93',note='&')
component(r,'*one LQ7A cam SHAFT, left (1)',price='25.83')
component(r,'*one LQ8A cam shaft PLUG (2).)',ident='12105',plate='13',mfr='B12105',price='.10')

r=start(210)
assembly(r,'SHAFT, cam, right, with bearings, assembly','$37.05',note='&')
component(r,' one — cam SHAFT, right, assembly,')
for i in range(1,7):component(r,f' one — cam shaft BEARING, No. {i}, assembly,')
component(r,' one — cam shaft BEARING, flywheel end, assembly.)')
assembly(r,'SHAFT, cam, right, assembly','25.93',note='&')
component(r,'*one LQ6A cam SHAFT, right (1)',ident='12104',plate='13',mfr='C12104',price='25.83')
component(r,'*one LQ8A cam shaft PLUG (2).)',price='.10')
assembly(r,'SHAFT, cam shaft driving, lower, with container, assembly','24.63',note='&',qty='(2)')
component(r,'two {S. K. F. 1204} BEARING, ball, radial, dia. 1.8504″, bore .7874″,\n       {or equal}      height .5512″,')
r[-1]['item_layout']=[dict(text='two',x=28,y=.5,width=16),dict(text='{S. K. F. 1204}\n{or equal}',x=44,width=48),dict(text='BEARING, ball, radial, dia. 1.8504″, bore .7874″,\n    height .5512″,',x=92,width=155)]
pieces(r,''' one —        cam shaft driving SHAFT, lower, assembly,
 one LQ104A   cam shaft driving shaft GEAR, lower,
 one LQ97A    cam shaft driving shaft lower bearing CONTAINER,
 one LQ103A   cam shaft driving shaft lower bearing SPACER,
 two LQ105A   cam shaft lower driving KEY.)''')
assembly(r,'SHAFT, cam shaft driving, lower, assembly','5.36',note='&',qty='(2)',ident='—',plate='34',mfr='8208')
component(r,'*one LQ94A cam shaft driving SHAFT, lower (2)',price='5.00')
component(r,' one LQ106A cam shaft lower driving shaft NUT,',mfr='B8141')
component(r,' one —       PIN, split, ⅛″ x 1″.)')

r=start(211)
assembly(r,'SHAFT, cam shaft driving, upper, assembly','2.89',note='&',qty='(2)')
component(r,'*one LQ73A cam shaft driving SHAFT, upper (2)',ident='8102',plate='13',mfr='B8102',price='2.56')
pieces(r,''' one LQ77A cam shaft driving shaft GEAR, upper,
 two LQ78A cam shaft upper driving shaft KEY,
 one —     PIN, steel, ⅛″ x 1 5/16″.)''')
assembly(r,'SHAFT, carburetor butterfly, long, assembly','.75',note='&',qty='(2)')
component(r,'three LQ522A carburetor butterfly set SCREW,')
component(r,'*one LQ521A carburetor butterfly SHAFT, long (2).)',mfr='13371',price='.69')
assembly(r,'SHAFT, carburetor butterfly, short, assembly','.64',note='&',qty='(2)')
component(r,'three LQ522A carburetor butterfly set SCREW,')
component(r,'*one LQ520A carburetor butterfly SHAFT, short (2)',mfr='13372',price='.57')
component(r,' one —     PIN, split, 1/16″ x ½″.)')
assembly(r,'SHAFT, carburetor throttle control, assembly','.67',note='&')
component(r,' one LQ116A carburetor throttle control tube END,')
component(r,'*one LQ65H carburetor throttle TUBE (1)',price='.12')
component(r,'*one LQ65G tube END, short (3)',price='.03')
component(r,' two —     NAIL, wire, 2d.)')
assembly(r,'SHAFT, carburetor throttle control connecting, assembly','.32',note='%')
component(r,'*one LQ110A carburetor throttle control connection TUBE (1)',mfr='L12499',price='.24')
component(r,'*two LQ65G tube END, short (3)',price='.03')
component(r,' two —     NAIL, wire, 2d.)')
assembly(r,'SHAFT, center control intermediate, assembly','5.80',note='&')
component(r,'*one M638 (center control) intermediate SHAFT (1)',ord='171',price='5.78')
component(r,' two —     PIN, split, 3/16″ x 2″.)')
append_rows(r,'''&|24|21|||SH1000A|SHAFT, clutch cardan|1|24.50
&|||||SH944D|SHAFT (clutch control) swing link|1|.78
&|22|2||M4150|955|SHAFT, clutch throwout|1|18.50
&|||||SH953C|SHAFT, clutch throwout auxiliary operating|1|2.79''')
assembly(r,'SHAFT, crank, with gear and nut, assembly','386.94',note='&')
pieces(r,''' one —       crank SHAFT, assembly,
 one LQ275A  crank shaft flywheel hub thrust bearing retainer NUT,
 two LQ274A  crank shaft flywheel thrust bearing SLEEVE,''')

r=start(212)
entry(r,'SHAFT, crank, with gear and nut, assembly—Continued.',note='&');composed(r)
pieces(r,''' one LQ258A   crank shaft GEAR,
 six (LQ262A) crank shaft gear BOLT, assembly,
(gu) LQ260A   crank shaft gear SHIM, medium,
(gu) LQ261A   crank shaft gear SHIM, thick,
(gu) LQ259A   crank shaft gear SHIM, thin,
 one SH136A   crank shaft NUT,
 one LQ276A   crank shaft thrust bearing retaining nut lock SCREW,''')
component(r,'*one LQ277A crank shaft thrust bearing retaining nut lock WIRE',mfr='8519',price='$0.01')
pieces(r,''' one SH136B   flywheel KEY,
 one LQ273A   flywheel thrust BEARING,
 one —        PIN, split, ¼″ x 3″,
 one —        SCREW, machine, flathead, No. 10 (3/16″)—24 x ¾″.)''')
assembly(r,'SHAFT, crank, assembly','355.05',note='&')
component(r,'twelve LQ366A crank pin PLUG,')
component(r,'*one LQ255A   crank SHAFT (1)',price='345.58')
pieces(r,''' one LQ263A   crank shaft gear end PLUG,
 one LQ264A   crank shaft gear end plug GASKET,
 one (LQ269A) crank shaft gear end plug STUD, assembly,
eleven LQ265A crank shaft main bearing PLUG,''')
component(r,'*six LQ257A   crank shaft oil hole PLUG, small (6)',price='.10')
pieces(r,''' one LQ256A   crank shaft propeller end PLUG,
twelve —      GASKET, copper, asbestos, 1¼″,
eleven —      GASKET, copper, asbestos, 1⅜″,
 five LQ271A  STUD, ⅜″ x 4 1/32″, threaded U. S. Std., 11/16″ and S. A. E.~                   ½″, assembly,
 six (LQ270A) STUD, ⅜″ x 4 17/32″, threaded U. S. Std., 11/16″ and S. A. E.~                   ½″, assembly.)''')

r=add(213,'''(gy)&|||S30A||586|SHAFT, distance recorder drive cable, with gear|1|1.50
(gy)&|||S372A||586|SHAFT, distance recorder drive pinion, with gear|1|1.50''')
assembly(r,'SHAFT, distributor, with oil thrower, assembly','1.09 P',note='&',qty='(2)',mfr='D13899')
pieces(r,'''*one D30539 distributor SHAFT (2),
 one D30565 distributor shaft oil THROWER,
 one D26824 RIVET, button head, .107″ x .157″.)''')
entry(r,'SHAFT, engine control rocker',note='&',ord='SH965B',qty='2',price='.78')
assembly(r,'SHAFT, front control swing link, assembly','10.22',note='&')
component(r,'*one M783 front control swing link SHAFT (1)',ord='216',price='9.82')
pieces(r,''' two M314 small planet pinion NUT,
 two —    PIN, split, 3/16″ x 2″.)''')
assembly(r,'SHAFT, fulcrum, assembly','12.87',note='&')
component(r,'*one M782 fulcrum SHAFT (1)',ord='216',price='12.37')
pieces(r,''' two M313 large planet pinion NUT,
 two —    PIN, split, 3/16″ x 1½″.)''')
entry(r,'SHAFT, generator drive, assembly',mfr='8210',qty='(1)',price='34.07')
stacked(r,ident='39\n—',plate='14\n34');composed(r)
component(r,'one {H. B. 206} BEARING, ball, radial, dia. 2.4410″, bore 1.1811″, height\n       {or equal}    .6299″,')
r[-1]['item_layout']=[dict(text='one',x=28,y=.5,width=16),dict(text='{H. B. 206}\n{or equal}',x=44,width=43),dict(text='BEARING, ball, radial, dia. 2.4410″, bore 1.1811″, height\n    .6299″,',x=87,width=160)]
pieces(r,'''four LQ78A  cam shaft upper driving shaft KEY,
 one —      generator drive shaft BEARING, lower, with container,~              assembly,
 one LQ388A generator driving PLUG,''')
component(r,'*one LQ386A generator driving SHAFT (1)',ident='8146',plate='16',price='5.35')
pieces(r,''' one LQ399A generator driving shaft ball bearing oil retaining WASHER,
 one LQ390A generator driving shaft ball bearing RETAINER,
(gu) LQ391A generator driving shaft ball bearing SHIM,
 one LQ400A generator driving shaft GEAR, lower,
 one LQ395A generator driving shaft GEAR, upper,
 one LQ396A generator driving shaft gear SPACER, long,
 one LQ394A generator driving shaft gear SPACER, short,
 one LQ401A generator driving shaft NUT,
 one LQ392A generator driving shaft upper ball bearing CONTAINER,
 one —      PIN, taper, type A, No. 2 x 1½″.)''')
entry(r,'SHAFT, oil pump driving',note='&',ident='—',plate='33',mfr='B8184',ord='LQ444A',qty='1',price='.70')

r=start(214)
assembly(r,'SHAFT, semaphore bottom, assembly','$1.29',note='&')
component(r,'*one X266 semaphore bottom SHAFT (1)',ord='803',price='1.25')
pieces(r,''' one —    NUT, crown, U. S. Std., 7/16″,
 one —    PIN, split, ⅛″ x ⅝″.)''')
append_rows(r,'''&||||X258|803|SHAFT, semaphore top|1|.35
&||||M2833|478|SHAFT, sponson roller|2|1.12''')
assembly(r,'SHAFT, starting crank, assembly','4.90',note='&')
component(r,' one SH65L hand starter WASHER,')
component(r,'*one SH66C starting crank SHAFT (1)',price='4.82')
pieces(r,''' one —     NUT, castle, S. A. E., ⅝″,
 one —     PIN, split, ⅛″ x 1½″''')
assembly(r,'SHAFT, tachometer drive, assembly','.95 P',note='&')
pieces(r,'''*one D29847 tachometer drive SHAFT (1),
 one D29845 tachometer drive shaft GEAR,
 one D29846 tachometer drive shaft gear attaching PIN.)''')
append_rows(r,'''%(gy)X|||||585|SHAFT, tachometer driving, with casing (Johns-Manville Co. type, New Ro-~   chelle, N. Y.)|1|11.39
&|—|12|||SH966D|SHAFT, throttle control rocker|1|''')
assembly(r,'SHAFT, track adjusting wheel, assembly','102.32',note='&',qty='(2)')
pieces(r,''' two M1477 shaft NUT,
 two M1475 track adjusting screw locking SCREW,
 one M1474 track adjusting wheel SHAFT,
 two M1409 BUSHING, bronze, O. D. 5.118″, I. D. 4 7/16″, over all-length, 8″,
 two Q52C  PLUG, pipe, square head, ⅜″.)''')
entry(r,'SHAFT, track adjusting wheel',note='&',ident='8',plate='28',brit='M1474',qty='2',price='75.00')

r=start(215)
assembly(r,'SHAFT, track driving wheel, assembly','98.61',note='&',qty='(2)')
pieces(r,''' two M1477     shaft NUT,
 one M1402     track driving wheel SHAFT,
 two M1409     BUSHING, bronze, O. D. 5.118″, I. D. 4 7/16″, over-all~                length 8″,
 one 20297/D89 KEY, ½″ x ¾″ x 1 13/16″,
 one Q52C      PLUG, pipe, square head, ⅜″.)''')
entry(r,'SHAFT, track driving wheel',note='&',brit='M1402',ord='61',qty='2',price='72.00')
assembly(r,'SHAFT, track roller pinion, assembly','75.20',note='&',qty='(2)')
component(r,'*one M1544    track roller pinion SHAFT (2)',ord='53',price='75.00')
pieces(r,''' one 20297/D89 KEY, ½″ x ¾″ x 1 13/16″,
 two Q52E      PLUG, pipe, square head, ¾″.)''')
entry(r,'SHAFT, transmission bevel pinion, assembly',note='&',qty='(1)',price='85.49')
r[-1].update(ident='53\n2\n5',plate='22\n23\n2',space_before=1,space_after=1,cell_baseline_offsets=dict(ident=-1,plate=-1));composed(r)
component(r,'*one M247 transmission bevel pinion SHAFT (1)',ord='705',price='85.00')
pieces(r,''' one MX33 transmission bevel pinion shaft NUT,
 one M248 transmission bevel pinion shaft WASHER,
 one —    PIN, split, 3/16″ x 2½″.)''')
append_rows(r,'''&|18|23||M255|702|SHAFT, transmission cross|1|158.00
&|||||SH101P|SHAFT, transmission mechanical lubricator cam|1|.89
&|||||SH101H|SHAFT, transmission mechanical lubricator drive|1|1.48''')
entry(r,'SHAFT, transmission shifter fork, assembly',note='&',qty='(1)',price='6.95')
stacked(r,ident='48\n14',plate='22\n23');composed(r)
component(r,' one M314 small planet pinion NUT,')
component(r,'*one M302 transmission shifter fork SHAFT (1)',ord='679',price='6.75')
component(r,' one —    PIN, split, 3/16″ x 2″.)')
entry(r,'SHAFT, transmission sprocket',note='&',ident='10',plate='22',brit='M289',ord='706',qty='2',price='135.00')
assembly(r,'SHAFT, transmission vertical shifter, assembly','15.16',note='&',ident='62',plate='2')
pieces(r,''' one M304 transmission vertical shaft LEVER, bottom,
 one M303 transmission vertical shaft LEVER, top,''')
component(r,'*one M305 transmission vertical shifter SHAFT (1)',ident='17',plate='22',ord='714',price='8.50')
component(r,' two —    KEY, Woodruff, No. C.)')

r=start(216)
assembly(r,'SHAFT, water pump, with gear, assembly','$5.49',note='&',ident='8079',plate='17')
component(r,' one LQ105A cam shaft lower driving KEY,')
component(r,'*one LQ138A water pump SHAFT (1)',mfr='B8079',price='5.33')
pieces(r,''' one LQ147A water pump shaft NUT,
 one —      PIN, split, bronze, 3/32″ x ⅝″.)''')
assembly(r,'SHELF, battery, assembly','1.95')
pieces(r,''' one SH992C battery SHELF,
 one SH992E battery shelf retaining STRIP,
seven —     SCREW, wood, No. 10 (3/16+″) x 1½″.)''')
append_rows(r,'''%X|||||SH992C|SHELF, battery|1|1.50
&|||||SH278A|SHELL, runner|1|22.15
%X||||8X00|633|SHIELD (peep hole cover) spring|20|.18
&|||L14988||LQ86A|SHIM, cam shaft driving shaft housing flange, medium|(gu)|.08
&|||L14987||LQ85A|SHIM, cam shaft driving shaft housing flange, thick|(gu)|.08
&|||L14989||LQ87A|SHIM, cam shaft driving shaft housing flange, thin|(gu)|.08
&|||L13444||LQ101A|SHIM, cam shaft driving shaft lower bearing container, medium|(gu)|.01
&|||L13426||LQ100A|SHIM, cam shaft driving shaft lower bearing container, thick|(gu)|.01
&|||L13238||LQ99A|SHIM, cam shaft driving shaft lower bearing container, thin|(gu)|.01
&|||L13419||LQ38A|SHIM, cam shaft gear, medium|(gd) 2|.15
&|||L13420||LQ39A|SHIM, cam shaft gear, thick|(gd) 2|.15
&|||8509||LQ37A|SHIM, cam shaft gear, thin|(gd) 2|.12
&|||L14991||LQ504A|SHIM, cam shaft housing cylinder, medium|(gu)|.01
&|||L14992||LQ505A|SHIM, cam shaft housing cylinder, thick|(gu)|.01
&|||L14990||LQ503A|SHIM, cam shaft housing cylinder, thin|(gu)|.01
%X|||8086||LQ68A|SHIM, cam shaft rocker lever tappet, medium|(gd) 24|.01
%X|||8089||LQ70A|SHIM, cam shaft rocker lever tappet, thick|(gd) 24|.01
%X|||8087||LQ69A|SHIM, cam shaft rocker lever tappet, thin|(gd) 24|.01
%X|||||LQ65K|SHIM, cam shaft rocker lever tappet. solid, .032″ thick|(gd) 24|.01''')

r=add(217,'''%X|||||LQ65L|SHIM, cam shaft rocker lever tappet, solid, .05″ thick|(gd) 24|.01
&|||||LQ260A|SHIM, crank shaft gear, medium|(gu)|.01
&|||||LQ261A|SHIM, crank shaft gear, thick|(gu)|.01
&|||||LQ259A|SHIM, crank shaft gear, thin|(gu)|.01
&|||8544||LQ391A|SHIM, generator driving shaft ball bearing|(gu)|.01
&|||B13493||LQ405A|SHIM, generator driving shaft ball bearing upper container, medium|(gu)|.09
&|||B13492||LQ404A|SHIM, generator driving shaft ball bearing upper container, thick|(gu)|.10
&|8511|16|L8511||LQ403A|SHIM, generator driving shaft ball bearing upper container, thin|(gu)|.08
&|||||LQ65A|SHIM, oil pump pressure relief valve spring|(gd) 1|.01
&|52|22||M260|702|SHIM, transmission bevel gear, laminated|(gd) 2|.78
&||||M254|702|SHIM, transmission bevel pinion|(gd) 16|.35''')
stacked(r,ident='62\n9',plate='22\n23')
append_rows(r,'''&||||MX35|713|SHIM, transmission bevel pinion shaft bearing distance piece|(gd) 13|.08
&|||||A7682|SHIM, transmission pinion shaft bearing housing|(gd) 1|.42
&|||13495||LQ153A|SHIM, water pump shaft bearing retainer, medium|(gu) —|.10
&|||L13494||LQ152A|SHIM, water pump shaft bearing retainer, thick|(gu) —|.10
&|44|14|8510||LQ151A|SHIM, water pump shaft bearing retainer, thin|(gu) —|.01''')
entry(r,'SHOE, track, assembly',note='%X',qty='(156)',price='63.86')
r[-1].update(ident='1\n—\n20',plate='9\n26\n2',space_before=1,space_after=1,cell_baseline_offsets=dict(ident=-1,plate=-1));composed(r)
component(r,' one —    track LINK, assembly,')
component(r,'*one M1264 track SHOE (156)',ident='3',plate='26',ord='602',price='32.00')
component(r,'eight —    RIVET, button head, 11/16″ x 2¼″.)')
append_rows(r,'''&||||M2207|365|SHUTTER, ventilation fan discharge box|1|.98
&|||||LQ65B|SLEEVE, cam shaft rocker roller pin.  (For lever LQ62A (1); lever LQ60A (1).)|24|.05
&|32|21|||SH861B|SLEEVE, clutch|1|7.50
&|||D29609|||SLEEVE, distributor ball bearing spacing|2|.03 P
&|||B12252||LQ274A|SLEEVE, crank shaft flywheel thrust bearing|2|2.10
&|—|6||M795|217|SLEEVE, foot brake suspension link|1|1.05
&||||M4023|803|SLEEVE, semaphore stirrup ring|1|2.15''')
assembly(r,'SLEEVE, transmission flanged, assembly','21.00',note='&',qty='(2)',ident='60',plate='22')
component(r,'*one M259 transmission flanged SLEEVE (2)',ord='708',price='17.50')
component(r,' one M261 transmission flanged sleeve BUSHING, inner.)')
append_rows(r,'''&|||||SH958B|SLEEVE, ventilating fan coupling|1|.25
&|||||SH958C|SLEEVE, ventilating fan sprocket|1|.18
(cp) (d)&|||||A6941|SNAP, standard chain bolt, ⅝″.  (For chain JB5C (1).)|2|.10 P
&|—|24||M1230|168|SOCKET, radiator inlet pipe flange|1|1.25''')

r=add(218,'''X|||||A6578|SOCKET, surface toggle switch plug|1|
&|||8144||LQ103A|SPACER, cam shaft driving shaft lower bearing|2|$1.50
%X|||||SH586H|SPACER (distance recorder gear) (steel, 13/32″ x ⅝″ x ¼″)|3|.08 P
%X|||||SH154G|SPACER, exhaust manifold guard, ⅜″ x ⅜″|4|.03 P
%X|||||SH154H|SPACER, exhaust manifold guard, ⅜″ x ⅝″|4|.03 P
&|8150|16|8150||LQ396A|SPACER, generator driving shaft gear, long|1|1.50
&|8149|16|8149||LQ394A|SPACER, generator driving shaft gear, short|1|1.00
&|||||SH142F|SPACER, governor bearing|1|.98
%X|||||SH1021D|SPACER, intensifier board|16|.01 P
&||||MX82|682|SPACER, low speed brake band bracket (I. D. .189″, O. D. ½″, thickness ⅜″)|2|.05
%X|||||SH119C|SPACER, starting crank housing (bulk head to housing)|(gd) 6|.48
&|||W-AF179|||SPACER, starting and lighting battery|6|.15 P
&|||||SH687A|SPACER, transmission (brake adjusting spring) (W. I., 1″ x 1¼″)|4|.08
&|||||SH282A|SPIDER, radiator cooling fan housing|1|17.50''')
assembly(r,'SPINDLE, chain wheel, assembly','3.54',note='&',ident='10',plate='20')
component(r,' one SH196C bevel gear WASHER,')
component(r,'*one M1131   chain wheel SPINDLE',ord='196',price='3.45')
pieces(r,''' one SH196B NUT, special,
 one —      PIN, split, ⅛″ x ¾″.)''')
entry(r,'SPINDLE, door lock.  (For door lock, left, assembly (1); door lock, right, assem-\n   bly (1).)',note='&',brit='M721',ord='545',qty='6',price='.48')
assembly(r,'SPINDLE, fan bevel gear box pulley, assembly','4.21',note='&')
component(r,' one SH196C bevel gear WASHER,')
component(r,'*one M1132   fan bevel gear box pulley SPINDLE (1)',ord='196',price='4.12')
component(r,' one SH196B NUT, special,',ident='1',plate='20')
component(r,' one —      PIN, split, ⅛″ x 1¼″.)')
assembly(r,'SPINDLE, governor, assembly','8.85',note='&')

r=start(219)
component(r,'*one SH144B governor SPINDLE (1)',price='8.78')
pieces(r,''' one —      NUT, castle, S. A. E., ¾″,
 one —      PIN, split, 5/32″ x 1½″,
 one —      WASHER, plain, ¾″.)''')
assembly(r,'SPINDLE, radiator cooling fan, assembly','15.77',note='&')
component(r,'*one SH282D radiator cooling fan SPINDLE (1)',price='15.63')
pieces(r,''' two —      NUT, castle, S. A. E., ¾″,
 two —      PIN, split, 3/32″ x 1¼″,
 two —      WASHER, plain, ¾″.)''')
assembly(r,'SPINDLE, ventilating fan, assembly','7.12',note='&')
component(r,' two SH958E ventilating fan coupling NUT',price='6.93')
pieces(r,'''*one SH958A ventilating fan SPINDLE (1),
 two SH958F ventilating fan spindle NUT,
 one SH958D ventilating fan sprocket WASHER.)''')
append_rows(r,'''&|7|5|||SH901A|SPRING, air pressure pump|4|.78
&|||||SH642B|SPRING, Belleville, I. D. 13/16″, O. D. ½″, 1″ thick.  (For outlook turret (4);~   revolver hole cover swivel pin (3).)|31|.35
&|||||438|SPRING, Belleville, I. D. 29/32″, O. D. 1 21/32″, ⅛″ thick.  (For outlook turret (6);~   driver’s turret (3); roof door (3).)|12|.50
&||||MX81|687|SPRING, brake band pin retainer|4|.08
%X|||||SH98D|SPRING, brake pedal|1|2.00
%X|||||LQ578A|SPRING, carburetor air inlet scoup|4|.08
&||||M2172|363|SPRING, catch (engine room sliding door)|2|.28
&|23|21|||SH849B|SPRING, clutch|1|2.85
&|7|21|||SH861F|SPRING, clutch small (free length 4⅝″)|6|.75
&|||||SH955C|SPRING, clutch throwout stop|1|.41
%X|—|6||M753|228|SPRING, control lever|2|2.35
%X|—|6||M744|228|SPRING, control lever trigger|3|.09
&|||8160||LQ220A|SPRING, crank case oil filler cover|2|.10
&||||M722|545|SPRING, door lock (For door lock, left (1); right (1); gasoline tank cover lock (1).)|8|.15
&|||D29780|||SPRING, distributor condenser and breaker plate stud|6|.01 P
&|||D29728|||SPRING, distributor contact curved arm|2|.03 P''')
assembly(r,'SPRING, distributor contact (straight) arm, assembly','.06 P',note='&',qty='(4)',mfr='D13803')
pieces(r,'''*one D29770 distributor contact straight arm SPRING (4),
*one D29771 distributor contact straight arm spring CLIP,''')

r=start(220)
entry(r,'SPRING, distributor contact (straight) arm, assembly—Continued.',note='&',mfr='D13803');composed(r)
pieces(r,''' two D29767 RIVET, flathead, .061″ x .141″,
 two D29766 WASHER, plain, .0635″ x 5/32″ x .02″.)''')
append_rows(r,'''&|||D30534|||SPRING, distributor cup|8|$0.01 P
&|||D30111|||SPRING, distributor head clamp|8|.02 P
&|||||SH537D|SPRING, gasoline tank cover hinge|2|.28
&|||D29818|||SPRING, generator brush arm (large)|4|.03 P
&|||D30193|||SPRING, generator brush arm (small)|4|.03 P
%X|—|12|||SH993H|SPRING, governor|1|.75
%X|||||SH395G|SPRING, gun hanger compression|5|.04
%X|||||SH395K|SPRING, gun retaining|1|.51
%X|||||SH65D|SPRING, hand starter lock plunger|1|.08
&|||||SH434D|SPRING, hemispherical turret antisplash.  (For retainer SH434B (6); retainer~   SH434C (5).)|33|.22
%X|—|6||M563|219|SPRING, high speed brake rod|2|1.12
&|—|12|8191||LQ447A|SPRING, oil pressure relief valve|1|.06
%X||||9X90|633|SPRING (peep hole cover) (wire, 6 coils, free length ¾″)|20|.04
&|||D42/21221||642|SPRING, revolver hole cover handle|9|.08
%X||||X287|801|SPRING, semaphore control ratchet|1|.28
%X||||X274|802|SPRING, semaphore detent|1|.08
%X|||Q38/21192||551|SPRING, shell holder|44|.08
&|||D29844|||SPRING, tachometer drive shaft|1|.15 P
%X|—|6||M564|219|SPRING, tension.  (For control rod (4); fan jockey pulley (1).)|5|.58
%X|||||SH922B|SPRING, terminal cover|6|.10
%X|—|12|||SH993E|SPRING, throttle release|1|.28
&|3|29||M1336|62|SPRING, track roller|28|5.00
%X|4|||M335|687|SPRING, transmission brake adjusting|4|.78''')
stacked(r,plate='31\n32')
entry(r,'SPRING, transmission high speed brake adjusting',note='%X',ident='8',plate='30',brit='M369',ord='698',qty='2',price='.24')

r=add(221,'''&|||||SH101J|SPRING, transmission mechanical lubricator flat|12|.05
&|||||SH104C|SPRING, transmission mechanical lubricator suction tube|6|.02
&|||8357||LQ295A|SPRING, valve, exhaust, outside|12|.25
&|||8254||LQ294A|SPRING, valve, inlet, outside|12|.12
&|||8253||LQ293A|SPRING, valve, inside|24|.17
&|||D30531|||SPRING, voltage regulator armature regulating|1|.03 P
&|8058|17|8058||LQ143A|SPRING, water pump shaft gland|1|.04
&|20|21||M308|714|SPRING, wire, O. D. 11/16″, length 1½″.  (For clutch.)|2|.08 P
&|12|20|||SH193C|SPROCKET, fan bevel gear box chain|1|6.72
&|6|20|||SH193A|SPROCKET, fan double drive|1|7.27
&||||X264|801|SPROCKET, semaphore bottom, near side|1|3.00
&||||X265|801|SPROCKET, semaphore bottom, off side|1|1.75''')
assembly(r,'SPROCKET, semaphore top, assembly','2.30',note='&',qty='(2)')
component(r,'*one X257 semaphore top SPROCKET (2)',ord='801',price='2.25')
pieces(r,''' one —    NUT, crown, U. S. Std., 7/16″,
 one —    PIN, split, ⅛″ x 1″,
 one —    WASHER, plain, ½″.)''')
append_rows(r,'''&|||||SH193B|SPROCKET, ventilating fan|1|1.95
&|||||GB5K|STAPLE.  (For outside tool chest.)|2|.05''')
assembly(r,'STAPLE, track roller pin, assembly','.31',qty='(116)',ident='8',plate='29')
component(r,'*one M1338 track roller pin STAPLE (116)',ord='53',price='.25')
pieces(r,''' two —     NUT, plain, U. S. Std., hexagon, ½″,
 two —     WASHER, lock, ½″.)''')
assembly(r,'STARTER, hand, assembly','27.85 P',note='%',ident='31',plate='2')
pieces(r,''' two SH65F  hand starter (housing) DOWEL,
 one SH65C  hand starter lock PLUNGER,
 one SH65H  hand starter lock plunger GUIDE,
 one SH65D  hand starter lock plunger SPRING,
 two SH65K  hand starter retaining PLATE,
four SH65A  hand starter SCREW,
 two SH65E  hand starter (shaft) KEY,
 one —      starting CRANK, assembly,
 one SH66A  starting crank counter shaft GEAR,
 one SH399B starting crank HOUSING,
 one SH399A starting crank housing COVER,
 one SH119B starting crank JAW,''')

r=start(222)
entry(r,'STARTER, hand, assembly—Continued.',note='%',ident='31',plate='2');composed(r)
pieces(r,''' one —      starting crank SHAFT, assembly,
 one —      PIN, split, ⅛″ x 1½″,
 one Q52D   PLUG, pipe, square head, ½″,''')
component(r,'*one SH65B  WIRE, iron, W. & M. Ga., No. 18, 10″ long.)',price='$0.01')
append_rows(r,'''%X|||||SH289B|STAY, driver’s seat, front|2|.78
%X|||||SH289D|STAY, driver’s seat, rear|2|1.28
*||||M2066|340|STAY, gusset, floor and side plates|(4)|3.25
*||||M2069|335|STAY, gusset, roof in rear of sponson|(2)|1.05
*||||M2067A|340|STAY, gusset, side plate to roof, without holes|(1)|3.75
*||||M2067C|340|STAY, gusset, side plate to roof, with holes ⅜″|(1)|3.75
*||||M2067B|340|STAY, gusset, side plate to roof, with holes ½″|(1)|3.75''')
assembly(r,'STEM, regulating tank relief valve, assembly','.58',note='&')
component(r,'*one SH962G regulating tank relief VALVE (1)',price='.40')
component(r,'*one SH962F regulating tank relief valve STEM (1).)',price='.18')
append_rows(r,'''*||||M1922B|530|STIFFENER, front mud chute, side, left|(1)|1.76
*||||M1922A|530|STIFFENER, front mud chute, side, right|(1)|1.76
*||||M2035|330|STIFFENER, sponson|(2)|36.50
&|||||A7680|STIFFENER, transmission pinion shaft bearing housing|1|2.50
&||||X253|803|STIRRUP, semaphore|1|1.55''')
assembly(r,'STOP, clutch lever, assembly','.26')
component(r,'*one M799 clutch lever STOP (1)',ord='171',price='.24')
component(r,' one —    NUT, plain, U. S. Std., hexagon, ½″.)')
append_rows(r,'''&||||M1787|536|STOP, gasoline tank left cover|1|.69
%X|—|6||M755|227|STOP, high and low speed control lever pawl|2|''')
assembly(r,'STOP, selector lever, assembly','.23',note='X',qty='(2)')

r=start(223)
component(r,'*one A6900 selector lever STOP (2)',price='.18')
component(r,' one B5397 selector lever stop NUT.)')
append_rows(r,'''&|1|30||M398|698|STOP, transmission high speed brake band|2|1.00
&|12|30||M366|697|STOP, transmission high speed brake band, bottom|2|.98
&|2|30||M399|697|STOP, transmission high speed brake band, top|2|1.50''')
assembly(r,'STOP, water can, assembly','1.38',note='&',qty='(4)')
component(r,'four (NB1B) FASTENER, strap, No. 2, assembly,')
component(r,'*one SH293E water can STOP (4)',price='.62')
component(r,'eight —     RIVET, button head, ¼″ x ⅝″.)')
assembly(r,'STORAGE, ammunition (above rear shall storage), assembly','87.50',note='&',ident='32',plate='2')
component(r,'*twelve SS577B ammunition storage ANGLE, No. 1 (12)',price='.85')
component(r,'*two SS577D ammunition storage ANGLE, No. 2, left (2)',price='.85')
component(r,'*two SS577C ammunition storage ANGLE, No. 2, right (2)',price='.85')
component(r,'*eight SS577E ammunition storage ANGLE, No. 3 (8)',price='.28')
component(r,'*one SH576L ammunition storage hinge PLATE (1)',price='.58')
component(r,'*two SH576J ammunition storage hinge plate REINFORCE (2)',price='.58')
component(r,' two —       ammunition storage LID, assembly,')
component(r,'*one SH576C ammunition storage PARTITION, with hole (1)',price='1.95')
component(r,'*six SH576B ammunition storage PARTITION, without hole (6)',price='1.95')
component(r,'*one SH575A ammunition storage PLATE, bottom (1)',price='7.50')
component(r,'*one SH577F ammunition storage PLATE, bottom side (1)',price='12.85')
component(r,'*one SH577G ammunition storage PLATE, end, front (1)',price='1.82')
component(r,'*one SH577H ammunition storage PLATE, end, rear (1)',price='1.82')
component(r,'*three SH576A ammunition storage PLATE, middle and side (3)',price='3.48')
component(r,'*two SH577A ammunition storage PLATE, top (2)',price='3.62')
pieces(r,'''eighteen —   RIVET, button head, 3/16″ x ½″,
fifty-two —  RIVET, countersunk head, 3/16″ x ½″,''')
entry(r,'four hundred\nand twenty-\n         six — RIVET, countersunk head, 3/16″ x ⅝″.)')
r[-1]['item_layout']=[dict(text='four hundred\nand twenty-\n         six',x=0,width=42),dict(text='}—',x=43,y=1,width=12),dict(text='RIVET, countersunk head, 3/16″ x ⅝″.)',x=67,y=1,width=180)]
assembly(r,'STORAGE, platform ammunition (Browning machine gun), assembly','66.47',note='&',ident='18',plate='2')
component(r,'*eight SH574A platform ammunition STOP, end (8)',price='.28')
pieces(r,''' one SH571B  platform ammunition storage BATTEN, left,
 one SH571A  platform ammunition storage BATTEN, right,''')
component(r,'*one SH573G  platform ammunition storage bearing PLATE, left (1)',price='.32')
component(r,'*one SH573F  platform ammunition storage bearing PLATE, right (1)',price='.32')

r=start(224)
entry(r,'STORAGE, platform ammunition (Browning machine gun), assembly—Contd.',note='&',ident='48',plate='2');composed(r)
component(r,'*two SH573M platform ammunition storage connecting ANGLE (2)',price='$0.12')
component(r,'*eight SH574C platform ammunition storage front cross BRACE (8)',price='.55')
pieces(r,''' one SH573B  platform ammunition storage front support FOOT, left,
 one SH573A  platform ammunition storage front support FOOT, right,
 one SH574K  platform ammunition storage locking STRIP,
 one SH574L  platform ammunition storage locking strip RIVET,
 one SH574G  platform ammunition storage (locking strip) SCREW,
 one SH574M  platform ammunition storage PARTITION, center,''')
component(r,'*one SH571C  platform ammunition storage PLATE (1)',price='24.75')
component(r,'*one SH572D  platform ammunition storage PLATE, front (1)',price='2.35')
component(r,'*one SH572B  platform ammunition storage PLATE, middle (1)',price='3.48')
component(r,'*one SH572A  platform ammunition storage PLATE, rear (1)',price='3.48')
component(r,' two SH574B  platform ammunition storage rear center shell SUP-\n                   PORT,')
component(r,'*sixteen SH574N platform ammunition storage rear cross BRACE (16)',price='.16')
component(r,'*one SH572E  platform ammunition storage shelf PLATE, front',price='2.65')
component(r,'*one SH572C  platform ammunition storage shelf PLATE, rear',price='1.82')
pieces(r,''' one SH574D  platform ammunition storage SUPPORT, center,
 one SH573D  platform ammunition storage SUPPORT, front,
 one —       platform ammunition storage thumb screw CHAIN,~                   assembly,''')
component(r,'*one SH573E  platform ammunition storage top plate ANGLE (1)',price='1.08')
pieces(r,'''four —       BOLT, U. S. Std., hexagon head, ⅝″ x 1½″, with plain~                   nut and lock washer,
 one —       RIVET, button head, 3/16″ x ⅝″,
four —       RIVET, button head, ½″ x 1½″,
 six —       RIVET, button head, ½″ x 1⅞″,
thirty-one — RIVET, countersunk head, 3/16″ x ½″,''')
