"""Photograph-led transcription of printed pages 145–164.
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
 r=start(page)
 append_rows(r,content)
 return r
def append_rows(r,content):
 for line in content.strip().splitlines():
  values=line.split('|');assert len(values)==9,line
  r.append(row(*[v.replace('~','\n') for v in values]))

r=start(145)
assembly(r,'PIPE, radiator drain, short, front, assembly','1.33 P',note='X')
pieces(r,'''one —           COCK, drain, tee handle, ½″,
one Q51DE   ELBOW, street, M. I., 90°, ½″,''')
component(r,'*one SH976K PIPE, W. I., ½″ x 10¾″ (1).)',ident='—',plate='24',price='.09')
assembly(r,'PIPE, radiator drain, short, rear, assembly','1.36 P')
component(r,'one —           COCK, drain, tee handle, ½″,')
component(r,'*one SH976V PIPE, W. I., ½″ x 12½″ (1)',ident='—',plate='24',price='.12')
component(r,'one SH976W radiator drain pipe ELBOW.)')
entry(r,'PIPE, radiator inlet',note='&',ident='—',plate='24',brit='M1229',ord='169',qty='1',price='2.48')
entry(r,'PIPE, radiator outlet',note='&',ident='—',plate='24',ord='SH975B',qty='1',price='7.50')
assembly(r,'PIPE, track roller pinion bearing oil, assembly','.18 P',qty='(2)')
component(r,'*one M1830 track roller pinion bearing oil PIPE (2)',ord='57',price='.15')
component(r,'one Q51A   REDUCER, pipe, M. I., ¼″ x ⅛″.)')
entry(r,'PIPE, vapor outlet',note='%X',ident='—',plate='24',ord='SH199C',qty='1',price='.18')
entry(r,'PIPE, ventilating fan inner bearing grease, length 4¼″',note='%X',ord='SH959H',qty='1',price='.12 P')
entry(r,'PIPE, ventilating fan inner bearing grease, length 5″',note='%X',ord='SH959G',qty='1',price='.12 P')
entry(r,'PIPE, ventilating fan outer bearing grease',note='%X',ord='SH959F',qty='1',price='.12 P')
entry(r,'PIPE, water tank filler, assembly',note='%X',qty='(1)',price='.99');stacked(r,ident='4\n—',plate='4\n24');composed(r)
component(r,'one Q51MC ELBOW, M. I., 90°, beaded, 2″,')
component(r,'*one SH199F PIPE, W. I., 2″ x 10½″ (1)',price='.37')
component(r,'one SH199G water tank filler pipe NIPPLE.)')
assembly(r,'PIPE, water (under engine), assembly','1.19')
component(r,'*one SH976B water PIPE (1)',ident='—',plate='24',price='.90')
pieces(r,'''one —           water pipe drain PLUG, assembly,
one SH976L water pipe drain plug COUPLING.)''')
entry(r,'PIPE, W. I., ⅛″ x 7″. (For transmission bevel gear case cover (2).)',note='%X',ord='SH671A',qty='2',price='.02 P')
for code,size,price in [('SH169J','¾″ x 10½″','.12 P'),('SH169K','¾″ x 12½″','.12 P'),('SH169K','¾″ x 12½″','.12 P'),('SH169L','¾″ x 19″','.20 P'),('SH169M','¾″ x 30″','.30 P'),('SH169R','1″ x 5¼″','.10 P'),('SH169S','1″ x 5½″, threaded one end','.10 P')]:
 entry(r,'PIPE, W. I., '+size+'. (For radiator inlet pipe (1).)',note='&',ident='—',plate='24',ord=code,qty='1',price=price)

r=start(146)
entry(r,'PISTON (old type in first 100 tanks)',note='&',ord='LQ466A',qty='12',price='$11.00')
assembly(r,'PISTON, assembly','12.55',note='(gaj)&',qty='12')
pieces(r,'''one SH1020A PISTON,
one LQ467A   piston PIN,
two LQ470A   piston pin RETAINER,
one LQ469A   piston RING, bottom,
one SH1020B piston RING, lower (oil),
one LQ468A   piston RING, intermediate.)''')
entry(r,'PISTON',note='(gaj)&',ord='SH1020A',qty='12',price='11.00')
entry(r,'PISTON, air pressure pump',note='&',ident='8',plate='5',ord='SH901D',qty='4',price='.98')
entry(r,'PLATE, air duct (between radiator and roof)',note='&',brit='M1037',ord='197',qty='1',price='.92')
for code,ord_,item,qty,price in [
 ('M2021','301','back','(1)','220.00'),('M1966','298','back (under sponson)','(2)','28.00'),
 ('M2139','357','bulk head, bottom','(1)','21.75'),('M2138','355','bulk head, center','(1)','42.40'),
 ('M2140','355','bulk head, side','(2)','1.28'),('M2137','353','bulk head, top','(1)','38.60')]:
 entry(r,'PLATE, '+item,note='*',brit=code,ord=ord_,qty=qty,price=price)
entry(r,'PLATE, butt, sponson, left',note='*',ord='SH492A',qty='(1)',price='75.00')
entry(r,'PLATE, butt, sponson, right',note='*',ord='SH491A',qty='(1)',price='75.00')
entry(r,'PLATE, cam shaft end',note='&',mfr='8376',ord='LQ29A',qty='2',price='.10')
entry(r,'PLATE, clutch throwout bell crank carrier',note='&',brit='M4153',ord='954',qty='1',price='.88')
entry(r,'PLATE, clutch throwout stop anchor',note='&',brit='M4160',ord='954',qty='1',price='.89')
entry(r,'PLATE, cover (behind mud chute)',note='*',ident='—',plate='7',brit='M1979',ord='385',qty='(2)',price='5.18')
entry(r,'PLATE, cover (exhaust)',note='(gb)*',ord='SH294B',qty='(2)',price='4.25')
entry(r,'PLATE, cover (hole in floor plate, No. 2)',note='&',brit='M1949',qty='1',price='4.50')
entry(r,'PLATE, cover (removable platform rest plate, rear)',note='&',ord='SH550F',qty='1',price='.18')
entry(r,'PLATE, cover (top roller)',note='(gb)*',ord='SH294A',qty='(2)',price='4.25')
entry(r,'PLATE, crank case oil filler baffle',note='&',mfr='B13153',ord='LQ230A',qty='2',price='.42')
entry(r,'PLATE, deflector',note='%X',brit='M2116',ord='380',qty='1',price='12.38');stacked(r,ident='3\n19',plate='3\n2')

r=add(147,'''%X||||M2065|530|PLATE, detachable (above roller pinions)|2|2.96
*|—|7||M1908|527|PLATE, detachable (over engine)|(1)|117.65
*||||M2038|334|PLATE, diaphragm, front|(2)|188.60''')
assembly(r,'PLATE, distributor condenser and breaker, with contact arms stud, assembly','1.65 P',note='&',mfr='D14181',qty='(2)')
pieces(r,'''*one    D13736 distributor condenser and breaker PLATE, assembly (2),
three (D29602) distributor contact arm dismounting STUD, assembly.)''')
append_rows(r,'''&||||M1581|232|PLATE, drive chain casing register|4|.52
&||||M1594B|232|PLATE, drive chain casing removable cap register, left|2|.52
&||||M1594A|232|PLATE, drive chain casing removable cap register, right|2|.52
&||||M786|287|PLATE, (driver’s) seat support, left|1|12.34
&|—|7||M787|287|PLATE, (driver’s) seat support, right|1|12.34
*|52|2||M2388|408|PLATE, driver’s turret, side, left|(1)|56.78
*||||M2387|408|PLATE, driver’s turret, side, right|(1)|56.78''')
assembly(r,'PLATE, driver’s turret flap (front), assembly','43.88',note='&',ident='4',plate='10')
pieces(r,'''two M2427 driver’s turret flap EYEBOLT,
two M2403 driver’s turret flap HINGE,''')
component(r,'*one M2352 driver’s turret flap PLATE, front (1)',ident='51',plate='2',ord='407',price='39.72')
component(r,'*one M2401 driver’s turret splash flap PLATE, top (1)',ord='425',price='.49')
component(r,'*one M2404 driver’s turret splash PLATE, left side (1)',ord='415',price='.49')
component(r,'*one M2402 driver’s turret splash PLATE, right side (1)',ord='413',price='.49')
component(r,'*one M2845 peep hole splash PLATE (1)',ord='437',price='.86')
pieces(r,'''nine —         RIVET, button head, 7/16″ x 2″,
two —         RIVET, button head, 7/16″ x 2⅜″,
four —        RIVET, countersunk head, ⅜″ x 1½″.)''')
append_rows(r,'''*|—|7||M2389|410|PLATE, driver’s turret roof|(1)|22.78
&||||M186|71|PLATE, engine bearer gusset, left|1|.82
&||||M185|71|PLATE, engine bearer gusset, right|1|.82
*||||M2003|310|PLATE, engine room back|(1)|91.25''')
assembly(r,'PLATE, engine room removable, left side, assembly','176.99',note='&')
component(r,'*one M1991   engine room removable PLATE, left side (1)',ord='303',price='170.00')
component(r,'*one M2001   engine room removable plate butt STRAP (2)',ord='313',price='4.80')
pieces(r,'''twenty-four SH303B BOLT, tap, ¾″ x 1¼″, threaded 1″,
three —           RIVET, button head, ¾″ x 1⅝″,
seven —          RIVET, button head, ¾″ x 2⅛″,
twenty-four —          WASHER, lock, ¾″.)''')

r=start(148)
assembly(r,'PLATE, engine room removable, right side, assembly','$171.80',note='&')
component(r,'*one M2077   engine room removable PLATE, right side (1)',ord='344',price='165.00')
component(r,'*one M2001   engine room removable plate butt STRAP (2)',ord='313',price='4.80')
pieces(r,'''twenty-two SH303B BOLT, tap, ¾″ x 1¼″, threaded 1″,
six —             RIVET, button head, ¾″ x 1⅝″,
four —           RIVET, button head, ¾″ x 2⅛″,
twenty-two —           WASHER, lock, ¾″.)''')
append_rows(r,'''*|—|7||M1971B|297|PLATE, engine room side, No. 1, left|(1)|332.00
*|—|7||M1971A|297|PLATE, engine room side, No. 1, right|(1)|332.00
*|—|7||M1973|299|PLATE, engine room side, No. 2, left|(1)|339.72
*||||M2070|342|PLATE, engine room side, No. 2, right|(1)|340.00
*|—|7||M1990|303|PLATE, engine room side, No. 3|(2)|112.00
&||||M1034|202|PLATE, fan and radiator air duct, front|1|2.75
&||||M1035A|203A|PLATE, fan and radiator air duct, front side|1|1.28
&||||M1035B|203A|PLATE, fan and radiator air duct, front upper|1|.98
&||||M1033|200|PLATE, fan and radiator air duct, rear bottom|1|7.48
&||||M1032|201|PLATE, fan and radiator air duct, side|1|3.50
&|7|20||M1126|196|PLATE, fan bevel gear box bearing cover|1|.38
*||||M1931|516|PLATE, floor, No. 1|(1)|346.00
*||||M1932|513|PLATE, floor, No. 2|(1)|396.75
*||||M1933|515|PLATE, floor, No. 3|(1)|191.17
*||||M1934|514|PLATE, floor, No. 4|(1)|199.76
*||||M1935|566|PLATE, floor, No. 5|(1)|267.90
*||||M1936|564|PLATE, floor, No. 6|(1)|237.00
*||||M1937|562|PLATE, floor, No. 7|(1)|255.00
*||||M1938|563|PLATE, floor, No. 8|(1)|267.90
*||||M3063B|448|PLATE, forward ammunition storage shell tube, left|(1)|38.00
*||||M3063A|448|PLATE, forward ammunition storage shell tube, right|(1)|38.00
*||||M1964B|304|PLATE, front inside upper, left|(1)|112.75''')

r=add(149,'''*||||M1964A|304|PLATE, front inside upper, right|(1)|112.75
*||||M1988|300|PLATE, front mud chute, bottom|(2)|84.00
*||||M1987|300|PLATE, front mud chute, side (front)|(2)|42.50
*||||M1986|295|PLATE, front mud chute, side (rear)|(2)|51.37
*||||M1989B|309|PLATE, front mud chute back, left|(1)|2.76
*||||M1989A|309|PLATE, front mud chute back, right|(1)|2.76
*|—|7||M2033|333|PLATE, front sloping|(1)|238.00
*||||M1965|301|PLATE, front (under sponson)|(2)|53.40
*||||M2094|348|PLATE, front wing lower, inside|(2)|168.00
*||||M1961B|305|PLATE, front wing lower, outside, left|(1)|138.50
*||||M1961A|305|PLATE, front wing lower, outside, right|(1)|138.50
*||||M2093|347|PLATE, front wing upper, inside|(2)|102.75
*|—|7||M1962B|302|PLATE, front wing upper, outside, left|(1)|102.75
*|—|7||M1962A|302|PLATE, front wing upper, outside, right|(1)|102.75
*|—|7||M1911|527|PLATE, gasoline tank roof|(1)|172.00
&||||M1479|62|PLATE, guard in hull (track adjusting screw)|4|.95
&|||||SH395D|PLATE, gun rest (main turret)|1|.98
&|||||SH65K|PLATE, hand starter retaining|2|.08
&||||M2134B|360|PLATE, helmet compartment division, left|1|4.80
&||||M2134A|360|PLATE, helmet compartment division, right|1|4.80''')
assembly(r,'PLATE, ignition battery, negative, assembly','1.76 P',note='&',mfr='W–E690',qty='(4)')
pieces(r,'''one W–G524 ignition battery negative plate connecting STRAP,
four W–F94  ignition battery PLATE, negative.)''')
entry(r,'PLATE, ignition battery, negative',note='&',mfr='W–F94',qty='16',price='.40 P')
assembly(r,'PLATE, ignition battery, positive, assembly','1.36 P',note='&',mfr='W–E689',qty='(4)')
pieces(r,'''three W–F93  ignition battery PLATE, positive,
one    W–G523 ignition battery positive plate connecting STRAP.)''')
entry(r,'PLATE, ignition battery, positive',note='&',mfr='W–F93',qty='12',price='.40 P')
assembly(r,'PLATE, ignition battery jar cover, bottom, assembly','.26 P',note='&',qty='(4)')
component(r,'*one —          ignition battery jar cover PLATE, bottom (4)',price='.20')
component(r,'two W–AD17 ignition battery jar cover plate WASHER, (soft rubber).)')
append_rows(r,'''&|||D30363|||PLATE, ignition switch terminal|1|.04 P
*||||M986|501|PLATE, inlet louvre cover|(1)|1.78
&||||M995A|500|PLATE, inlet louvre retaining, front|1|.88
&||||995B|500|PLATE, inlet louvre retaining, rear|1|.88
*||||M1977|376|PLATE, inside (side of gasoline tank)|(2)|238.00''')

r=add(150,'''*||||M1983A|325|PLATE, inside skirting, front half|(2)|$108.00
*||||M1983B|325|PLATE, inside skirting, rear half|(2)|75.00
%X||||M2034|333|PLATE, (inspection and fan hole) cover|3|7.00
&||||M1047|234|PLATE, jockey pulley cover|1|.38
%X||||M1000|501|PLATE, louvre packing|4|.22''')
assembly(r,'PLATE, machine gunner’s seat, assembly','2.53',qty='(2)')
component(r,'two M2158 HINGE, butt, 2″ x 4¼″,')
component(r,'*one M2157 machine gunner’s seat PLATE (2)',ord='370',price='.85')
pieces(r,'''two M2163 machine gunner’s seat strut fulcrum BRACKET,
one M2437 spring CLIP,
eight —       RIVET, button head, ¼″ x 11/16″,
four —        RIVET, button head, ¼″ x ⅞″.)''')
entry(r,'PLATE, main turret, front, left side',note='*',brit='M2350',ord='405',qty='(1)',price='58.40');stacked(r,ident='3\n—',plate='10\n7')
entry(r,'PLATE, main turret, front, right side',note='*',brit='M2348',ord='408',qty='(1)',price='58.40')
entry(r,'PLATE, main turret, rear, left side',note='*',brit='M2351',ord='409',qty='(1)',price='230.54');stacked(r,ident='43\n—',plate='2\n7')
append_rows(r,'''*|43|2||M2407|405|PLATE, main turret, rear, left side|(1)|80.69
*||||M2349|409|PLATE, main turret, rear, right side|(1)|230.54
*||||M2406|405|PLATE, main turret, rear, right side|(1)|80.69
&||||M2377|414|PLATE, main turret flap catch|2|.28
&||||M2375|420|PLATE, main turret flap splash, bottom|2|.50
&||||M2374|420|PLATE, main turret flap splash, side|4|.36
&|||||SH420A|PLATE, main turret flap splash, top|2|.68
*|—|7||M2362|407|PLATE, main turret front, center|(1)|38.27
(gb)*|||||SH409A|PLATE, main turret machine gun hole cover (side)|(2)|20.00
&||||M2364|423|PLATE, main turret rear peep hole splash|1|.98
*|—|7||M2373|411|PLATE, main turret roof, left side|(1)|127.50
*|—|7||M2372|411|PLATE, main turret roof, right side|(1)|127.50''')

r=add(151,'''&||||M2357|420|PLATE, main turret roof door apron|1|.75
*||||M2394|423|PLATE, main turret splash, top|(2)|.30
*|—|7||M2363|405|PLATE, main turret wing, front|(2)|57.39
&|||||FF55HC|PLATE, name|1|1.00
&|—|33|8188||LQ435A|PLATE, oil pump separating|1|.60
&|||L15001||LQ252A|PLATE, Ordnance engine name (Liberty 12)|(1)|1.10''')
assembly(r,'PLATE, outlet louvre frame side (left), assembly','4.86',note='&')
component(r,'two M1000 louvre packing PLATE,')
component(r,'*one M993   outlet louvre cover PLATE (1)',ord='503',price='2.08')
component(r,'*one M989   outlet louvre frame side PLATE (left) (1)',ord='505',price='2.28')
pieces(r,'''five —        RIVET, button head, ½″ x 1″,
one —        RIVET, countersunk head, ½″ x 1″.)''')
append_rows(r,'''(gm)*|—|7||M2361|435|PLATE, outlook turret roof|(1)|29.32
*||||M1963B|296|PLATE, outside, left (front of sponson)|(1)|235.08
*||||M1963A|296|PLATE, outside, right (front of sponson)|(1)|235.08
*|—|7||M1984|319|PLATE, outside skirting, front half|(2)|450.00
*|—|7||M1985|318|PLATE, outside skirting, rear half|(2)|236.00''')
assembly(r,'PLATE, peep hole cover, assembly','3.10',qty='(20)')
component(r,'*one 3X90   packing PLATE (20)',ord='632',price='.80')
component(r,'*one 14X90 cover plate packing PIECE (20)',ord='633',price='.38')
component(r,'*one 1X90   peep hole cover PLATE (20)',ord='632',price='1.05')
pieces(r,'''one 4X90   peep hole cover plate operating KNOB,
one —        peep hole cover plate operating BOLT, assembly,
two —       RIVET, countersunk head, 3/16″ x 1″,''')
component(r,'two —       RIVET, countersunk head, ⅜″ x 1¼″.\n                  For left sponson (4); right sponson (3); outlook turret (4);\n                     main turret (9).)')
entry(r,'PLATE, (peep hole cover) revolving. (On left sponson (4) right sponson (3); out-\n   look turret (4); main turret (9).)',note='&',ident='3',plate='9',brit='2X90',ord='362',qty='20',price='3.67')
append_rows(r,'''*||||M2424|438|PLATE, periscope hole cover|(1)|.98
&|||||SH571D|PLATE, platform ammunition storage, bottom|1|8.50
&|||||SH573L|PLATE, platform ammunition storage cover|1|.30
&|||||SH612A|PLATE, radiator, left side|1|4.75
&|||||SH612B|PLATE, radiator, right side|1|4.75
&|||||SH278D|PLATE, radiator cooling fan|1|5.12
&|||||SH281C|PLATE, radiator cooling fan housing spider cover|1|.46
&|||||SH608A|PLATE, radiator drain pipe connection stiffening (tapped ¼″)|1|.35''')

r=add(152,'''&||||M880|608|PLATE, radiator drain pipe connection stiffening (tapped ½″)|2|$0.45
&||||M897|608|PLATE, radiator steam pipe connection stiffening (tapped ¾″)|1|.45
&||||M887|608|PLATE, radiator steam pipe connection stiffening (tapped 1″)|1|.58
&|||||SH608B|PLATE, radiator drain pipe connection stiffening (tapped for countersunk head~   bolt)|1|.35
&||||M886|608|PLATE, radiator water connection stiffening|1|.98
*||||M2096|349|PLATE, rear mud chute sloping side|(2)|25.50
*||||M2095|349|PLATE, rear mud chute vertical side|(2)|55.65''')
entry(r,'PLATE, revolver hole cover. (On sponson, left (3); sponson, right (2).)',note='&',brit='C128/20384',ord='642',qty='7',price='2.80');stacked(r,ident='2\n58',plate='9\n2')
append_rows(r,'''*||||M1909A|533|PLATE, roof (back of front louvre)|(1)|2.25
*||||M1905|528|PLATE, roof (in front of front louvre)|(1)|17.72
*||||M1902|528|PLATE, roof (over driver)|(2)|19.00
*||||M1918|529|PLATE, roof (rear of mud chute)|(2)|2.45
*||||M1914|531|PLATE, roof (rear of mud chute)|(2)|1.96
*||||M1912A|529|PLATE, roof (side of back louvre)|(1)|23.48
&||||M1901B|534|PLATE, roof, front, left (without holes for cable clips)|1|58.80
&||||M1901A|534|PLATE, roof, front, right (with holes for cable clips)|1|58.80
*||||M1917|529|PLATE, roof, rear (under track)|(2)|2.35
*||||M1924|530|PLATE, roof stiffening (at towing bracket)|(1)|4.30
*||||M1915A|526|PLATE, roof (under track, rear, left side)|(1)|42.00
*||||M1904A|526|PLATE, roof (under track, rear, right side)|(1)|42.00
X|6|27||M1552|63|PLATE, shaft bearing. (For shaft M402 (2); shaft M1544 (2).)|4|6.32
X|1|27||M1411|62|PLATE, shaft nut locking|4|.48
*||||M2028|377|PLATE, side (above rear mud chute)|(2)|16.50
*|—|7||M1968B|300|PLATE, side, left (at side door)|(1)|8.50
*|—|7||M1968A|300|PLATE, side, right (at side door)|(1)|8.50
*||||M1967B|385|PLATE, side, left (top of door)|(1)|108.72
*|—|7||M1967A|385|PLATE, side, right (top of door)|(1)|108.72
*|—|7||M1992|350|PLATE, side (top of sponson)|(2)|62.30''')

r=add(153,'''*|—|7||M1970B|298|PLATE, side, rear, left (sponson)|(1)|149.25
*|—|7||M1970A|298|PLATE, side, rear, right (sponson)|(1)|149.25
*||||M710|541|PLATE, side door splash, bottom|(2)|1.80
*||||M713|541|PLATE, side door splash, front, left|(1)|2.12
*||||M714|541|PLATE, side door splash, front, right|(1)|2.12
*||||M712|541|PLATE, side door splash, rear|(2)|2.12
*||||M711|541|PLATE, side door splash, top|(2)|1.80
*||||M2098|350|PLATE, sloping, bottom|(2)|35.40
*||||M2014|345|PLATE, sloping front|(1)|98.00
*||||M2097|350|PLATE, sloping, top|(2)|49.20
*|—|7||M2738|457|PLATE, sponson back|(2)|78.12
*|—|7||M2750|463|PLATE, sponson back, left side|(1)|145.27
*||||M2739|461|PLATE, sponson back, right side|(1)|145.27
*|—|7||M2744|464|PLATE, sponson back wing, left side|(1)|27.81
*||||M2742|456|PLATE, sponson back wing, right side|(1)|24.60
&||||M2799|485|PLATE, sponson back wing plate splash, right side|1|2.50
*||||M2801|456|PLATE, sponson back wing splash, left side|(1)|11.94
*||||M2757B|466|PLATE, sponson floor, left|(1)|65.97
*||||M2757A|466|PLATE, sponson floor, right|(1)|65.97
*|—|7||M2733B|451|PLATE, sponson front lower, left|(1)|68.05
*|—|7||M2733A|451|PLATE, sponson front lower, right|(1)|68.05
*|—|7||M2734B|451|PLATE, sponson front upper, left|(1)|16.95
*|—|7||M2734A|451|PLATE, sponson front upper, right|(1)|16.95
*||||M2732A|457|PLATE, sponson front vertical, left|(1)|25.50
*||||M2732B|457|PLATE, sponson front vertical, right|(1)|25.50
*|—|7||M2745|462|PLATE, sponson front wing, left side|(1)|43.78
*||||M2743|462|PLATE, sponson front wing, right side|(1)|44.65
&||||M2802|474|PLATE, sponson front wing plate splash, left side|1|3.00
&||||M2800|474|PLATE, sponson front wing plate splash, right side|1|3.00
*||||M2844|471|PLATE, sponson peep hole splash, left side|(1)|.98
*|—|7||M2756B|467|PLATE, sponson roof, left|(1)|104.57
*|—|7||M2756A|467|PLATE, sponson roof, right|(1)|104.57
*|—|7||M2766|468|PLATE, sponson shield, bottom, left side (front)|(1)|15.91
*|—|7||M2768|468|PLATE, sponson shield, bottom, left side (rear)|(1)|8.63
*|—|7||M2767|468|PLATE, sponson shield, bottom, left side (intermediate)|(1)|8.63
*||||M2762|468|PLATE, sponson shield, bottom, right side (front)|(1)|4.75
*||||M2760|470|PLATE, sponson shield, bottom, right side (intermediate)|(1)|2.98
*||||M2761|467|PLATE, sponson shield, bottom, right side (rear)|(1)|3.96
*||||M2763|470|PLATE, sponson shield, top, left side (front)|(1)|8.63''')

r=add(154,'''*||||M2765|469|PLATE, sponson shield, top, left side (rear)|(1)|$8.63
*||||M2759|469|PLATE, sponson shield, top, right side (front)|(1)|8.63
*||||M2764|469|PLATE, sponson shield, top, right side (intermediate)|(1)|8.63
*||||M2758|467|PLATE, sponson shield, top, right side (rear)|(1)|18.37
*|—|7||M2748|465|PLATE, sponson side, left side|(1)|96.92
*||||M2737|465|PLATE, sponson side, right side|(1)|102.05
*|—|7||M2747|464|PLATE, sponson side lower, left side (rear)|(1)|27.20
*||||M2736|456|PLATE, sponson side lower, right side (rear)|(1)|18.23
*|—|7||M2746|464|PLATE, sponson side upper, left side|(1)|10.00
*||||M2735|456|PLATE, sponson side upper, right side|(1)|7.50
*||||M2740B|458|PLATE, sponson sloping bottom, left|(1)|163.27
*||||M2740A|458|PLATE, sponson sloping bottom, right|(1)|163.27
*|—|7||M2749|459|PLATE, sponson sloping side, left side|(1)|182.37
*||||M2741|460|PLATE, sponson sloping side, right side|(1)|182.37
&|||||SH485C|PLATE, sponson splash (upper edge of gun shield, left side)|1|3.50
*|||||SH487A|PLATE, sponson top shield plate splash, right side|(1)|1.48''')
assembly(r,'PLATE, starting and lighting battery, negative, assembly','1.42',note='&',mfr='W–E712',qty='(6)')
component(r,'one W–G542 starting and lighting battery negative plate connecting\n                     STRAP,')
component(r,'seven W–F82  starting and lighting battery PLATE, negative.)')
entry(r,'PLATE, starting and lighting battery, negative',note='&',mfr='W–F82',qty='42',price='.18')
assembly(r,'PLATE, starting and lighting battery, positive, assembly','1.24',note='&',mfr='W–E711',qty='(6)')
component(r,'six W–F81  starting and lighting battery PLATE, positive,')
component(r,'one W–G541 starting and lighting battery positive plate connecting\n                     STRAP.)')
entry(r,'PLATE, starting and lighting battery, positive',note='&',mfr='W–F81',qty='36',price='.18')
entry(r,'PLATE, track adjusting bracket',note='&',ident='9',plate='28',brit='M1484',ord='60',qty='4',price='1.50')
entry(r,'PLATE, turret roof, rear',note='*',ident='—',plate='7',brit='M1903',ord='525',qty='(1)',price='115.75')

r=add(155,'''&||||M2414|414|PLATE, turret roof door lock|1|.31
*|—|7||M1969|300|PLATE (under door)|(2)|51.00
*||||M2073|343|PLATE (under driver’s turret)|(1)|11.00
*||||M1939|517|PLATE (under gasoline tank)|(1)|156.00
*||||M2174|364|PLATE, vertical beam inner skirting|(2)|1.48
*||||M1978|381|PLATE, wing inside, rear|(2)|148.26
*||||M1975B|294|PLATE, wing outside, back, left|(1)|264.35
*||||M1975A|294|PLATE, wing outside, back, right|(1)|264.35
*|—|7||M1976B|295|PLATE, wing outside, rear, left|(1)|203.89
*|—|7||M1976A|295|PLATE, wing outside, rear, right|(1)|203.89
*|—|7||M3784B|510|PLATE, 6-pdr. gun pedestal, left|(1)|4.20
*|—|7||M3784A|510|PLATE, 6-pdr. gun pedestal, right|(1)|4.20
*||||M3781B|507|PLATE, 6-pdr. gun pedestal, front, left|(1)|6.52
*||||M3781A|507|PLATE, 6-pdr. gun pedestal, front, right|(1)|6.52
*||||M3782|507|PLATE, 6-pdr. gun pedestal, side|(2)|5.76
*||||M3780B|510|PLATE, 6-pdr. gun pedestal back, left|(1)|8.29
*||||M3780A|510|PLATE, 6-pdr. gun pedestal back, right|(1)|8.29
*||||M3779B|507|PLATE, 6-pdr. gun pedestal base, left|(1)|15.75
*||||M3779A|507|PLATE, 6-pdr. gun pedestal base, right|(1)|15.75
*||||M3783B|510|PLATE, 6-pdr. gun pedestal shell, left|(1)|4.20
*||||M3783A|510|PLATE, 6-pdr. gun pedestal shell, right|(1)|4.20
*||||M3778|268|PLATE, 6-pdr. gun pedestal top, left|(1)|31.00
*||||M3777|269|PLATE, 6-pdr. gun pedestal top, right|(1)|31.00
%X|6|5|||SH901E|PLUG, air pressure pump displacement|4|.72
&|8133|13|L8133||LQ48A|PLUG, cam shaft housing|2|.05
&|||13363||LQ568A|PLUG, carburetor air valve|2|.04
&|||13367||LQ524A|PLUG, carburetor body|4|.10''')
assembly(r,'PLUG, carburetor gasoline, assembly','.11',note='&',qty='(2)')
component(r,'*one LQ537A carburetor gasoline PLUG (2)',mfr='13390',price='.10')
component(r,'one LQ538A carburetor gasoline plug fiber WASHER.)')
assembly(r,'PLUG, carburetor internal body, assembly','.14',note='&',qty='(8)')
component(r,'one LQ542A carburetor internal body fiber WASHER,')
component(r,'*one LQ541A carburetor internal body PLUG (8).)',mfr='13395',price='.13')
assembly(r,'PLUG, carburetor priming, assembly','.12',note='&',qty='(4)')
component(r,'*one LQ549A carburetor priming PLUG (4)',mfr='13403',price='.09')
component(r,'*one LQ550A carburetor priming plug TUBE (4).)',mfr='13404',price='.03')

r=add(156,'''&|||13484||LQ266A|PLUG, crank pin|12|$0.10
&|||13481||LQ263A|PLUG, crank shaft gear end|1|.15
&|||13483||LQ265A|PLUG, crank shaft main bearing|11|.12
&|||8136||LQ256A|PLUG, crank shaft propeller end|1|.03
%X|||||SH978N|PLUG, engine oiled tank filler flange (square head, 1″ drilled)|1|.04
&(pf)R||||||PLUG, expansion, ½″.  (For pin M284 (1); pin M274 (1).)|12|.01
%X||||E152/21255|187|PLUG, gasoline tank drain|3|.78
&|8501|16|8501||LQ388A|PLUG, generator driving|1|.01''')
entry(r,'PLUG, hexagon head, ⅝″.  (For water pump (1); oil pump (1); outlet LQ413A (1).)',note='%X',mfr='8133',ord='LQ145A',qty='3',price='.03 P');stacked(r,ident='250\n8133\n—',plate='15\n17\n12')
assembly(r,'PLUG, ignition battery vent, assembly','.08 P',qty='(4)')
component(r,'*one L–12 ignition battery vent PLUG (4)',price='.05')
component(r,'one M–8  ignition battery vent plug WASHER (soft rubber).)')
entry(r,'PLUG (manifold).  (For manifold LQ181A (2); tube LQ186A (1).)',note='&',mfr='161',ord='LQ188A',qty='3',price='.05');stacked(r,ident='36\n—',plate='14\n34')
append_rows(r,'''&|28|14|6275||LQ182A|PLUG (manifold drain), special|1|.13
%X|||B14375||LQ428A|PLUG, oil pump lower half body|1|.05
%(pf)R|||||Q52A|PLUG, pipe, square head, ⅛″.  (For governor housing, assembly (1); collar~   SH869A (1); cylinder SH900C (1); base SH903A (3).)|9|.02 P
%(pf)R||||||PLUG, pipe, square head, ⅛″, brass.  (For pin M1543 (1).)|36|.06 P
%(pf)R|||||Q52B|PLUG, pipe, square head, ¼″.  (For cap M3305A (1); cover M1124 (1); cap~   M3305A (1); cover M1124 (1); cap M3305B (1).)|3|.02 P
%(pf)R|||||Q52C|PLUG, pipe, square head, ⅜″.  (For shaft M1402 (1); shaft M1474 (2); pin M1337~   (1).)|64|.02 P
%(pf)R|||||Q52D|PLUG, pipe, square head, ½″.  (For filler cap flange SH951B (1); hand starter,~   assembly (1).)|4|.02 P
%(pf)R|||||Q52E|PLUG, pipe, square head, ¾″.  (For shaft M1544 (2); flange M3315 (1).)|5|.03 P
%X|||||LQ299A|PLUG, spark, with gasket||.90 P
%X|||W–L11|||PLUG, starting and lighting battery vent|6|.05 P''')

r=add(157,'''%X||||M1476|53|PLUG, track locking screw adjusting screw|4|.04
%X|29|22||M311B|672|PLUG, transmission gear case oil filling, bronze|1|.78
%X|11|23||M311A|672|PLUG, transmission gear case oil filling, C. I.|2|.22
%X|||||SH101E|PLUG, transmission mechanical lubricator|6|.06''')
assembly(r,'PLUG, triple combination valve, assembly','1.21',note='&',qty='(3)')
component(r,'*one SH951E triple combination valve PLUG (3)',price='1.18')
component(r,'one —          NUT, plain, U. S. Std., hexagon, bronze, 5/16″.)')
assembly(r,'PLUG, water pipe drain, assembly','.27',note='&',qty='(2)')
component(r,'*one SH976D water pipe drain PLUG (2)',ident='—',plate='24',price='.02')
component(r,'one SH976S   cooling system drain plug CHAIN,')
component(r,'*one SH976M cooling system drain plug chain RING (2)',price='.05')
component(r,'*one SH976N cooling system drain plug RING (2)',price='.05')
pieces(r,'''one SH976P  cooling system drain plug swivel PIN,
one SH976R  cooling system drain plug swivel pin WASHER.)''')
append_rows(r,'''&||||||PLUG, 12 volt generator voltage regulator polarity reversing switch|1|.12
&|5|21|||SH861A|PLUNGER, clutch spring|6|.48
%X|||||SH395F|PLUNGER, gun hanger|5|.08
%X|||||SH65C|PLUNGER, hand starter lock|1|.44''')
assembly(r,'PLUNGER, semaphore detent, assembly','.39')
component(r,'*one X273 semaphore detent PLUNGER',ord='802',price='.38')
component(r,'one —     PIN, split, 1/16″ x ⅜″.)')
append_rows(r,'''%X||||M3023|550|PLUNGER, shell holder|44|.22
&|||||SH101K|PLUNGER, transmission mechanical lubricator, lower|6|.42
&|||||SH104B|PLUNGER, transmission mechanical lubricator, upper|6|.18
&||||M307|714|PLUNGER, transmission shifter shaft detent|1|.22''')
assembly(r,'POST, semaphore, assembly','19.87',note='&')
component(r,'*one M4022 semaphore POST (1)',ord='802',price='15.75')
pieces(r,'''two X254   semaphore stirrup RING,
two X255   semaphore stirrup ring RIVET,
one X319   semaphore tube RIVET,
one —        BOLT, U. S. Std., hexagon head, ⅜″ x 3½″, with plain nut,
two —       STUD, 5/16″ x 4⅛″, threaded U. S. Std., ½″ and ¾″, assem-~                  bly.)''')

r=start(158)
entry(r,'PULLEY, air pressure pump',note='%X',ident='1',plate='5',ord='SH900B',qty='1',price='$1.78')
assembly(r,'PULLEY, jockey, with arms, assembly','14.61')
pieces(r,'''one —          jockey PULLEY, assembly,
two SH234H jockey pulley ARM,
one —          jockey pulley arm AXLE, assembly,
one —          jockey pulley arm SEPARTATOR, assembly,
one —          jockey pulley AXLE, assembly,
one SH234F jockey pulley distance TUBE,
one SH234E jockey pulley long distance TUBE,
one SH234D jockey pulley short distance TUBE.)''')
assembly(r,'PULLEY, jockey, assembly','7.85',ident='27',plate='2')
component(r,'one {SKF1304} BEARING, ball, radial, dia. 2.0472″, bore .7874″, face\n       {or equal}   .5906″.')
r[-1]['item_layout']=[dict(text='one',x=28,y=.5,width=16),dict(text='{SKF1304}\n{or equal}',x=44,width=43),dict(text='BEARING, ball, radial, dia. 2.0472″, bore .7874″, face\n    .5906″.',x=87,width=160)]
pieces(r,'''one SH234D   jockey PULLEY,
one M1047     jockey pulley cover PLATE,
four —           SCREW, cap, U. S. Std., hexagon head, ¼″ x ⅞″,~                       drilled head.''')
component(r,'*one —          WIRE, lock, W. & M. Ga. No. 20, 10″ long (1).)',price='.01 P')
entry(r,'PULLEY, jockey',note='&',ord='SH234D',qty='1',price='1.38')
assembly(r,'PULLEY, radiator cooling fan, assembly','9.57')
component(r,'*one SH233C radiator cooling fan PULLEY (1)',price='7.48')
component(r,'one SH233D radiator cooling fan pulley COVER,')
entry(r,'       eleven—          RIVET, belt, brass, No. 8 x 1″.)')
assembly(r,'PULLEY, radiator cooling fan driving, assembly','10.84')
component(r,'*one SH233A radiator cooling fan driving PULLEY (1)',price='8.48')
component(r,'one SH233B radiator cooling fan driving pulley COVER,')
entry(r,'       eleven—          RIVET, belt, brass, No. 8 x 1″.)')

r=add(159,'''%X|||||SH102A|PULLEY, transmission mechanical lubricator|1|1.38
%X|||||SH971C|PULLEY, transmission mechanical lubricator driving|1|1.75''')
entry(r,'PUMP, air pressure, assembly',note='%X',qty='(1)',price='32.69');stacked(r,ident='—\n4',plate='5\n2');composed(r)
pieces(r,'''one SH901F air pressure pump air hole COVER,
one SH903A air pressure pump BASE,
two SH900A air pressure pump BEARING,
two SH901C air pressure pump BUSHING,
four SH901B air pressure pump check NUT,
four SH900C air pressure pump CYLINDER,
four SH901E air pressure pump displacement PLUG,
four SH901D air pressure pump PISTON,
one SH900B air pressure pump PULLEY,
one —          air pressure pump SHAFT, assembly,
four SH901A air pressure pump SPRING,
four —          BOLT, U. S. Std., hexagon head, ⅜″ x 1¼″, with plain~                      nut and lock washer,
one —          KEY, Woodruff, No. 5,
seven Q52A    PLUG, pipe, square head, ⅛″,
eight —          SCREW, cap, U. S. Std., hexagon head, 5/16″ x ¾″,
six —             SCREW, cap, U. S. Std., hexagon head, ⅜″ x ¾″.)''')
entry(r,'PUMP, hand pressure',note='%X',ident='16',plate='8',ord='SH980B',qty='1',price='4.50')
entry(r,'PUMP, oil, assembly',note='%X',qty='(1)',price='28.98 P');stacked(r,ident='8200\n—\n—',plate='15\n33\n34');composed(r)
pieces(r,'''one LQ447A   oil pressure relief valve SPRING,
one —            oil pump BODY, lower half, assembly,
one —            oil pump BODY, upper half, assembly,
one LQ434A   oil pump driven GEAR, lower,
two LQ438A   oil pump driven GEAR, upper,
one LQ433A   oil pump driving GEAR, lower,
one LQ439A   oil pump driving GEAR, upper,
one LQ436A   oil pump driven PIN, long,
one LQ437A   oil pump driven PIN, short,
one LQ444A   oil pump driving SHAFT,
one LQ453A   oil pump lower half body COVER,
one LQ454A   oil pump lower half body cover GASKET,''')

r=start(160)
entry(r,'PUMP, oil, assembly—Continued.',note='%X');stacked(r,ident='8200\n—\n—',plate='15\n33\n34');composed(r)
pieces(r,'''one LQ448A    oil pump pressure relief VALVE,
one LQ446A    oil pump pressure relief valve GUIDE,''')
entry(r,'   (gd) one LQ65A     oil pump pressure relief valve spring SHIM,')
pieces(r,'''one LQ445A    oil pump relief valve SEAT,
one LQ435A    oil pump separating PLATE,
one —             oil pump STRAINER, lower, assembly,
one —             oil pump STRAINER, upper, assembly,
four (LQ443A) oil pump upper half body BOLT, assembly,
ten (LQ164A)  BOLT, S. A. E., drilled, ¼″ x 15/16″, threaded 9/16″,~                       assembly,
one —             GASKET, copper asbestos, ⅝″,
one LQ145A    PLUG, hexagon head, ⅝″,''')
component(r,'*two LQ31A    WIRE, lock, W. & M. Ga. No. 18 x 8″ (22)',mfr='177',price='$0.01 P')
component(r,'*one LQ167A   WIRE, lock, W. & M. Ga. No. 18 x 10″ (6).)',mfr='L209',price='.01 P')
entry(r,'PUMP, water, assembly',note='&',qty='(1)',price='29.67 P');stacked(r,ident='12211\n42',plate='15\n14');composed(r)
component(r,'one {H. B. 303} BEARING, ball, radial, dia. 1.8504″, bore .6693″, thick-\n       {or equal}     ness .5512″,')
r[-1]['item_layout']=[dict(text='one',x=28,y=.5,width=16),dict(text='{H. B. 303}\n{or equal}',x=44,width=43),dict(text='BEARING, ball, radial, dia. 1.8504″, bore .6693″, thick-\n    ness .5512″,',x=87,width=160)]
pieces(r,'''one —            water pump BODY, assembly,
one LQ150A   water pump COVER,
one LQ149A   water pump cover GASKET,
one LQ146A   water pump IMPELLER,''')
component(r,'*three LQ141A water pump PACKING (3)',ident='8213',plate='17',price='.10');stacked(r,mfr='15004\nor\n14334')
pieces(r,'''one —            water pump SHAFT, with gear, assembly,
one LQ140A   water pump shaft bearing RETAINER,''')

r=start(161)
pieces(r,'''one LQ151A  water pump shaft bearing retainer GASKET,
two LQ142A  water pump shaft GLAND,
one LQ143A  water pump shaft gland SPRING,
one —           GASKET, copper asbestos, ⅝″,
one LQ145A  PLUG, hexagon head, ⅝″,''')
component(r,'*one LQ167A  WIRE, lock, W. & M. Ga. No. 18 x 10″ (6).)',mfr='L209',price='.01')
entry(r,'QUADRANT, reverse lever',note='&',brit='M779',ord='217',qty='1',price='.78')
assembly(r,'RACK, funnel, assembly','4.07')
pieces(r,'''one A3997 funnel rack BRACKET, (front),
one A3998 funnel rack BRACKET, (rear),
one A4025 funnel rack CLEAT,
one —       funnel rack STRAP, buckle end, assembly,
one —       funnel rack STRAP, plain end, assembly,''')
for code,price in [('A3999','.15'),('A4000','.22'),('A4001','.22'),('A4002','.44'),('A4003','.28'),('A4004','.22'),('A4005','.08'),('A4006','.06'),('A4007','.06')]:
 component(r,'*one '+code+' PACKING (1)',price=price)
entry(r,'        seven —      BURR, copper, No. 8,')
entry(r,'       twelve —     NAIL, finishing, 3d,')
pieces(r,'''four —         SCREW, wood, flat head, No. 8 (5/32+″) x ¾″,
two —         SCREW, wood, flat head, No. 8 (5/32+″) x ⅞″,
two —         SCREW, wood, flat head, No. 8 (5/32+″) x 1″,''')
entry(r,'  twenty-two —     SCREW, wood, flat head, No. 8 (5/32+″) x 1½″,')
pieces(r,'''two —         SCREW, wood, round head, No. 8 (5/32+″) x ¾″,
five —         SCREW, wood, round head, No. 8 (5/32+″) x 1″.)''')
assembly(r,'RADIATOR, assembly','302.48',note='&',ident='1',plate='2')
pieces(r,'''one —          radiator CORE, front, assembly,
one —          radiator CORE, rear, assembly,
one SH607A radiator core GASKET,
one —          radiator HEADER, front, assembly,
one —          radiator HEADER, rear, assembly,
two M888    radiator header GASKET,''')

r=start(162)
entry(r,'RADIATOR, assembly—Continued.',note='&',ident='1',plate='2');composed(r)
pieces(r,'''two SH607B radiator intermediate tube plate REINFORCE,
one SH612A radiator PLATE, left side,
one SH612B radiator PLATE, right side,
one SH606D radiator reinforcing STRIP, left,
one SH606C radiator reinforcing STRIP, right,''')
entry(r,'    thirteen —       BOLT, U. S. Std., countersunk head, ⅜″ x 1½″, with\n                              plain nut and lock washer,')
entry(r,'      twelve —       BOLT, U. S. Std., hexagon head, 5/16″ x ¾″ with plain nut\n                              and lock washer,')
entry(r,'   forty-two —       BOLT, U. S. Std., hexagon head, 5/16″ x 1″, with plain nut\n                              and lock washer,')
entry(r,' forty-three —       BOLT, U. S. Std., hexagon head, ⅜″ x 1⅜″, with plain\n                              nut and lock washer,')
entry(r,'      sixteen —       BOLT, U. S. Std., hexagon head, ⅜″ x 1½″.)')
for number,code,price in [(1,'M2009','8.35'),(2,'M2010','18.75'),(3,'M2011','18.75'),(4,'M2012','18.75'),(5,'M2013','17.60')]:
 for suffix,side,inner in [('B','left','right'),('A','right','left')]:
  entry(r,f'RAIL, track bulb, No. {number}, {side} (outer {side} or inner {inner})',note='&',ident='4' if number==1 and suffix=='B' else '',plate='25' if number==1 and suffix=='B' else '',brit=code+suffix,ord='308',qty='2',price=('$' if number==1 and suffix=='B' else '')+price)
append_rows(r,'''&||||X249|801|RATCHET, semaphore control|1|.84
%(gy)X|||||586|RECORDER, distance (Johns-Manville Co. type, M–26)|1|20.00 P
(ee)&||||||REDUCER, conduit, 1″ to ¾″.  (For conduit A8405 (1).)|1|.09 P
(ee)&||||||REDUCER, conduit, 1½″ to 1″.  (For conduit A8403 (1).)|1|.13 P''')

r=start(163)
entry(r,'REDUCER, pipe, M. I., ¼″ x ⅛″.  (For pipe M1830 (1).)',note='%(pf)R',ord='Q51A',qty='2',price='.02 P')
assembly(r,'REGULATOR, voltage, with housing, assembly','6.11 P',mfr='D5721')
pieces(r,'''one D5718  voltage REGULATOR, assembly,
one D13865 voltage regulator HOUSING, assembly,
one D30380 voltage regulator terminal STUD, large, assembly,
two D30366 voltage regulator terminal STUD, small, assembly.)''')
assembly(r,'REGULATOR, voltage, assembly','4.52 P',note='&',mfr='D5718')
pieces(r,'''*one  D30101  terminal CLIP, long (1),
*two  D30100  terminal CLIP, short (2),
one   D13886  voltage regulator ARMATURE, assembly,
*one  D25401  voltage regulator armature CLIP (1),
one (D30141) voltage regulator armature regulating spring adjusting~                     screw, assembly,
one   D30898  voltage regulator armature regulating spring GUARD,
one   D24082  voltage regulator armature retaining PIN,
*one  D30109  voltage regulator BRACKET (1),
one   D13611  voltage regulator CLIP, with contact, assembly,
one   D29480  voltage regulator clip INSULATOR, with contact (under),
one (D13795) voltage regulator contact SCREW, assembly,
six —             voltage regulator mounting terminal SCREW, with thin~                      bushing, assembly,
one —            voltage regulator mounting terminal SCREW, with thick~                      bushing, assembly,
*one —           voltage regulator SPOOL, assembly (1),
*one  D25394  voltage regulator support PLATE (1),
two   D25470  voltage regulator terminal INSULATOR,
*two  D30532  voltage regulator terminal SEPARATOR (2),
one   D30527  NUT, castle, ¼″—28 x 7/16″ x .281″ thick,
one   D30515  PIN, brass, .09″ x .210″,
one   D25461  RIVET, button head, brass, .091″ x .191″,
two   D30108  SCREW, slotted head, No. 2—64 x .215″,
one   D24953  WASHER, lock, .275″ x .454″ x .031″,
one   D30528  WIRE, copper, .0403″ x 1 1/16″.)''')
append_rows(r,'''&|||||SH607B|REINFORCE, radiator intermediate tube plate|2|2.58
%X||||5X90|633|REST, head, padded|20|.55
&|||||SH573K|REST, removable platform (forward)|1|.40
&|||||SH550E|REST, removable platform, rear|1|.30''')

r=start(164)
entry(r,'REST, sponson foot (on floor plate)',note='&',brit='M2842',ord='489',qty='2',price='$0.42')
assembly(r,'RETAINER, clutch ball, assembly','2.30',note='&',ident='29',plate='21')
component(r,'*one SH998C clutch ball RETAINER (1)',price='2.00')
entry(r,'        thirty —         BALL, steel, ¼″.)')
append_rows(r,'''&|6|21|||SH861C|RETAINER, clutch spring|6|.38
&|||D29579|||RETAINER, distributor cam oil, felt|2|.01 P
&|||D29571|||RETAINER, distributor cam oil, steel|2|.01 P
&|||D29611|||RETAINER, distributor upper ball bearing|2|.01 P
&|||D30134|||RETAINER, generator ball bearing (inner)|1|.05 P
&|8524|16|8524||LQ390A|RETAINER, generator driving shaft ball bearing|1|.25''')
assembly(r,'RETAINER, hemispherical turret antisplash, long, assembly','1.94',note='&',qty='(3)')
component(r,'*one SH434B hemispherical turret antisplash RETAINER, long (3)',price='.50')
component(r,'six SH434D hemispherical turret antisplash SPRING,')
entry(r,'       twelve —          RIVET, countersunk head, copper, 3/16″ x ¼″.)')
assembly(r,'RETAINER, hemispherical turret antisplash, short, assembly','1.60',note='&',qty='(3)')
component(r,'*one SH434C hemispherical turret antisplash RETAINER, short (3)',price='.40')
component(r,'five SH434D hemispherical turret antisplash SPRING,')
component(r,'ten —            RIVET, countersunk head, copper, 3/16″ x ¼″.)')
append_rows(r,'''&|||12547||LQ470A|RETAINER, piston pin|24|.07
(ga)&|||||SH61A|RETAINER, track driving shaft (shipping)|4|.48
&|58|22||M310|706|RETAINER, transmission flanged sleeve outer bushing oil|2|.48
&|8069|17|B14333||LQ140A|RETAINER, water pump shaft bearing|1|4.50
&|||||SH278E|RIM, radiator cooling fan|1|2.95
*||||M1401|52|RIM, track driving wheel|4|65.75
&||||M1036A|156|RING, air duct mud hole|1|1.28
%X|||D/20793||637|RING (ball mount), splash.  (For hemispherical turret (1); side door (1).)|5|1.28
&|15|21|||SH997A|RING, clutch end bearing|1|3.57''')
