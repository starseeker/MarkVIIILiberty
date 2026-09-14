"""Photograph-led transcription of printed pages 225–244.
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
def grouped(r,quantity,text):
 entry(r,quantity+' — '+text)
 r[-1]['item_layout']=[dict(text=quantity,x=0,width=55),dict(text='}—',x=56,y=.5,width=12),dict(text=text,x=82,y=.5,width=165)]

r=start(225)
grouped(r,'   three hundred\nand eighty-eight','RIVET, countersunk head, 3/16″ x ⅝″,')
pieces(r,'''     three —         RIVET, countersunk head, 3/16″ x ⅞″,
       six —         RIVET, countersunk head, 3/16″ x 1″,
       two —         RIVET, countersunk head, ¼″ x ⅞″,
     seven —         RIVET, countersunk head, ¼″ x 1″,
   sixteen —         SCREW, wood, flathead, No. 10 (3/16+″) x ¾″.)''')
assembly(r,'STORAGE, removable platform, assembly','41.68',note='%')
component(r,' two SH569P Officer’s chest fastening STRAP,')
component(r,'*sixteen SH578A removable platform ammunition storage ANGLE, No. 1 (16)',price='.38')
component(r,'*four SH578B removable platform ammunition storage ANGLE, No. 2 (4)',price='.28')
component(r,' two SH579B removable platform ammunition storage BATTEN,')
component(r,'*two SH579G removable platform ammunition storage PARTITION (2)',price='.89')
component(r,'*one SH579D removable platform ammunition storage PLATE, middle\n                   and bottom (1)',price='3.72')
component(r,'*one SH579E removable platform ammunition storage PLATE, middle\n                   and bottom (1)',price='3.72')
component(r,'*two SH579F removable platform ammunition storage PLATE, side (2)',price='3.48')
component(r,'*one SH579A removable platform ammunition storage PLATE, top (1)',price='14.32')
component(r,' four —         BOLT, U. S. Std., hexagon head, ¼″ x ⅞″, with plain nut\n                   and lock washer,')
component(r,'twelve —         RIVET, countersunk head, 3/16″ x ½″,')
grouped(r,' two hundred\n    and fifty','RIVET, countersunk head, 3/16″ x ⅝″,')
component(r,'   six —         SCREW, wood, flathead, No. 10 (3/16+″) x ¾″.)')
assembly(r,'STORAGE, shell, rear, assembly','167.95',note='&')
component(r,'*two M3019     intermediate shaft bracket STRIP (2)',ord='551',price='.80')
pieces(r,''' two M3022     rear shell storage BAR, length 21 9/16″,
 four M3030    rear shell storage BAR, length 25⅞″,''')
component(r,'*one M3031     rear shell storage BLOCK (1)',ord='552',price='2.00')
pieces(r,'''  six M3032    rear shell storage BRACKET,
 four M3026    rear shell storage BRACKET,''')
component(r,'*one M3017     rear shell storage cover PLATE (1)',ord='548',price='12.48')
component(r,'*one M3016     rear shell storage end PLATE (1)',ord='549',price='12.48')
component(r,'*one M3018     rear shell storage end PLATE (1)',ord='553',price='12.74')
component(r,'*one M3015B    rear shell storage side PLATE, left (1)',ord='548',price='8.04')
component(r,'*one M3015A    rear shell storage side PLATE, right (1)',ord='548',price='8.04')

r=start(226)
entry(r,'STORAGE, shell, rear, assembly—Continued.',note='&');composed(r)
component(r,'*one SH550B    removable platform ammunition storage SUPPORT (1)',price='$1.20')
pieces(r,''' one SH550E    removable platform REST, rear,
 twelve —         shell holder PIN, assembly,
 twelve M3023     shell holder PLUNGER,
 twelve Q38/21, 192 shell holder plunger SPRING,
 twelve M3020     shell holder spring CASE,
  sixty B37/21, 191 6-pdr. shell expansion TUBE,
  sixty A37/21, 191 6-pdr. shell TUBE,
 twenty-four —         BOLT, carriage, ¼″ x 1 9/16″, with nut and lock washer,
      three —         BOLT, U. S. Std., hexagon head, ½″ x 3 9/16″, with plain~                         nut and lock washer,
 twenty-four —         RIVET, button head, ¼″ x ⅞″,
      eight —         RIVET, button head, ¼″ x 1⅛″,
   eighteen —         RIVET, button head, 7/16″ x 1″,
 thirty-nine —         RIVET, button head, 7/16″ x 1½″,
      eight —         RIVET, button head, 7/16″ x 1¾″,
       five —         SCREW, wood, round head, No. 6 (9/64−″) x ½″.)''')
assembly(r,'STRAINER, crank case oil filler, assembly','.35',qty='(2)')
component(r,'*one LQ223A crank case oil filler strainer RING (2)',mfr='8164',price='.15')
component(r,'*one LQ224A crank case oil filler strainer SCREEN (2).)',mfr='B8165',price='.20')
assembly(r,'STRAINER, crank case oil sump, assembly','1.30',ident='33',plate='14')
component(r,'*one LQ203A crank case oil sump strainer HOUSING (1)',mfr='B8227',price='1.00')
component(r,' one LQ204A crank case oil sump strainer SCREEN, side,')
component(r,' one LQ205A crank case oil sump strainer SCREEN, top.)')
assembly(r,'STRAINER, gasoline tank, assembly','2.10',qty='(3)')

r=start(227)
component(r,' one SH188C gasoline tank strainer BOTTOM,')
component(r,'*one SH188A gasoline tank strainer RING (3)',price='.24')
component(r,'*one SH188B gasoline tank top STIFFENER (3)',price='.42')
pieces(r,''' two SH188D GAUZE, wire, brass, 7¼″ x 10⅝″, mesh 30, B. & S. gage 31,
 one SH188E GAUZE, wire, brass, 7¼″ x 10⅝″, mesh 80, B. & S. gage~                45.)''')
assembly(r,'STRAINER, oil pump, lower, assembly','2.75',note='%',ident='—',plate='33',mfr='8220')
pieces(r,''' one LQ452A oil pump lower SCREEN, top,
 one LQ451A oil pump SCREEN, side,''')
component(r,'*one LQ450A oil pump screen HOUSING, lower (1).)',mfr='8203',price='1.75')
assembly(r,'STRAINER, oil pump, upper, assembly','2.75',note='%',ident='—',plate='33',mfr='8531')
component(r,' one LQ451A oil pump SCREEN, side,')
component(r,'*one LQ456A oil pump screen HOUSING, upper (1)',mfr='B8534',price='1.75')
component(r,' one LQ457A oil pump oil upper SCREEN, top.)')
append_rows(r,'''&|||||SH104L|STRAINER, transmission mechanical lubricator suction screen|6|.06
*||||M1940|519|STRAP, butt (between floor plates 1 and 2)|(1)|12.35
*||||M2144|355|STRAP, butt, bulk head|(1)|2.75
*||||M2145|522|STRAP, butt, top and center bulk head plates|(2)|.48
*|—|7||M1982|344|STRAP, butt (at top of door)|(2)|1.05
*||||M1892|531|STRAP, butt, forward (roof)|(2)|2.48
*||||M1894B|531|STRAP, butt, left (behind turret)|(1)|2.48
*||||M1894A|531|STRAP, butt, right (behind turret)|(1)|2.48
*|—|7||M2048|338|STRAP, butt, front (under door)|(2)|1.05
*||||M1919|529|STRAP, butt, rear louvre, left side|(1)|3.60
*|—|7||M2049|338|STRAP, butt, rear (under door)|(2)|1.15
*||||M1980|309|STRAP, butt (sponson, front)|(2)|1.04
*||||M1981|309|STRAP, butt (sponson, rear)|(2)|.36
*||||M2006|315|STRAP, butt, exterior longitudinal, front|(2)|27.00
*||||M1994A|315|STRAP, butt, exterior longitudinal, rear, left|(1)|14.75
*|—|7||M1994B|315|STRAP, butt, exterior longitudinal, rear, right|(1)|14.75
*||||M1995|309|STRAP, butt, front interior|(2)|2.48
*||||M2000|313|STRAP, butt, front outside longitudinal|(2)|7.35
*||||M2399|421|STRAP, butt, main turret, center|(1)|.52
*|—|7||M2420B|416|STRAP, butt, main turret, front, left|(1)|1.18
*|—|7||M2420A|416|STRAP, butt, main turret, front, right|(1)|1.18
*||||M2398|423|STRAP, butt, main turret, front|(1)|2.19
*||||M2400|415|STRAP, butt, main turret, rear|(1)|.68''')

r=add(228,'''*||||M2422|417|STRAP, butt, main turret, side|(4)|$0.68
*||||M2099B|350|STRAP, butt, mud chute, left|(1)|2.40
*||||M2099A|350|STRAP, butt, mud chute, right|(1)|2.40
*||||M2783B|475|STRAP, butt, sponson floor, rear, left|(1)|1.75
*||||M2783A|475|STRAP, butt, sponson floor, rear, right|(1)|1.75
*||||M2784B|479|STRAP, butt, sponson, left (lower front)|(1)|1.92
*||||M2784A|479|STRAP, butt, sponson, right (lower front)|(1)|1.92
*||||M2784C|479|STRAP, butt, sponson, upper front|(2)|.40
*||||M2782|479|STRAP, butt, sponson, upper rear|(2)|.28
*||||M2788|475|STRAP, butt, sponson vertical, front, left|(1)|2.38
*||||M2787|475|STRAP, butt, sponson vertical, front, right|(1)|2.38
*||||M2781B|479|STRAP, butt, sponson vertical, rear, left|(1)|4.60
*||||M2781A|479|STRAP, butt, sponson vertical, rear, right|(1)|4.60
*||||M2786B|479|STRAP, butt, sponson vertical, left (lower rear)|(1)|1.08
*||||M2786A|479|STRAP, butt, sponson vertical, right (lower rear)|(1)|1.08
*||||M2789|476|STRAP, butt, sponson vertical, front, left|(1)|2.48
*||||M2780|479|STRAP, butt, sponson vertical, intermediate|(2)|3.22
*|—|7||M2046|335|STRAP, butt, vertical, left side (between engine room plates 1 and 2)|(1)|5.65
*|—|7||M2177|385|STRAP, butt, vertical, rear|(2)|4.36
*||||M2043|336|STRAP, butt, No. 2 and 3 engine room plate, right|(1)|2.80''')
assembly(r,'STRAP, funnel rack, buckle end, assembly','.20')
component(r,'*one A3990       funnel rack STRAP, buckle end (1)',price='.10')
pieces(r,''' one ZA1HCADA BUCKLE, barrel roller, 2″,
 two —           RIVET, belt, copper, No. 10 (.134″) x ½″, with burr.)''')
assembly(r,'STRAP, funnel rack, plain end, assembly','.71')
component(r,'*one B5900 funnel rack STRAP (cotton webbing) (1)',price='.30')
component(r,' one B4024 funnel rack strap END,')
component(r,' nine —      RIVET, belt, copper, No. 10 (.134″) x ½″, with burr.)')

r=add(229,'''&||||M367|699|STRAP, high speed brake|2|8.20''')
assembly(r,'STRAP, hot food container bracket, buckle end, assembly','.78',note='&')
component(r,'*one SH239F     hot food container bracket STRAP, buckle end (1)',price='.68')
pieces(r,''' one ZA1GAABA BUCKLE, barrel roller, 1½″,
 one —             KEEPER, fixed, 1″, for 1½″ strap.)''')
append_rows(r,'''&|||||SH239E|STRAP, hot food container bracket, plain end|1|.68
&|||W-G524|||STRAP, ignition battery negative plate connecting|4|.16 P
&|||W-G523|||STRAP, ignition battery positive plate connecting|4|.16 P
*||||M1993|309|STRAP, inner skirting plate rear connecting|(2)|1.84
*|—|7||M1998|309|STRAP, outside and inside skirting plates connecting|(6)|1.74''')
assembly(r,'STRAP, medical outfit bracket, buckle end, assembly','.79',note='&')
component(r,'*one SH365A medical outfit bracket STRAP, buckle end (1)',price='.74')
component(r,' one B6496F  BUCKLE, barrel roller, 1¼″.)')
append_rows(r,'''&|||||SH365B|STRAP, medical outfit bracket, plain end (lower)|1|1.08
%X|||||SH569P|STRAP, Officer’s chest fastening|2|.15
*||||M1916|529|STRAP, packing (above roller pinion)|(2)|1.00''')
assembly(r,'STRAP, spare fan belt holder, buckle end, assembly','.54',note='&')
component(r,'*one SH285D spare fan belt holder STRAP, buckle end (1)',price='.47')
pieces(r,''' one B6496F  BUCKLE, barrel roller, 1¼″,
 one —         KEEPER, fixed, ⅝″, for 1¼″ strap.)''')
append_rows(r,'''&|||||SH285C|STRAP, spare fan belt holder, plain end (upper)|1|.52
&|||W-G542|||STRAP, starting and lighting battery negative plate connecting|6|.16 P
&|||W-G541|||STRAP, starting and lighting battery positive plate connecting|6|.16 P''')
assembly(r,'STRAP, water bucket holder, buckle end, assembly','.58',note='&')
component(r,'*one SH443C water bucket holder STRAP, buckle end (1)',price='.50')
pieces(r,''' one B6496F  BUCKLE, barrel roller, 1¼″,
 one —         KEEPER, fixed, ⅝″, for 1¼″ strap.)''')
append_rows(r,'''&|||||SH443D|STRAP, water bucket holder, plain end|1|.28
|||||SH992E|STRIP, battery shelf retaining|1|.38
*||||M2037B|351|STRIP, bottom guide, left (outer left or inner right)|(2)|49.75
*||||M2037A|351|STRIP, bottom guide, right (inner left or outer right)|(2)|49.75
&||||M1584|222|STRIP, drive chain casing angle cleat packing|4|.22
&|||||SH978T|STRIP (engine), oil tank fastening|1|.48
&|||||SH978E|STRIP (engine), oil tank supporting|1|.85
&|||||SH978R|STRIP (engine oil tank), vertical fastening|2|.75''')

r=add(230,'''*||||M2150|522|STRIP, engine room (sliding) door wedging|(2)|$0.28
&|||||655|STRIP, felt, 4½″ x 24½″ x ¼″.  (For packing M1753M (3).)|3|.20
&|||||655|STRIP, felt, 4½″ x 25″ x ¼″.  (For packing M1753J (1).)|3|.20
&|||||654|STRIP, felt, 4½″ x 35″ x ¼″.  (For packing M1753A (1).)|3|.30
&|||||655|STRIP, felt, 4½″ x 36″ x ¼″.  (For packing M1753H (1).)|3|.30
&|||||653|STRIP, felt, 4½″ x 38″ x ¼″.  (For piece M1753C (1); piece M1753B (1).)|2|.30
&|||||655|STRIP, felt, 5″ x 26½″ x ¼″.  (For packing M1753L (1); packing M1753K (1).)|2|.25
&|||||655|STRIP, felt, 5″ x 30½″ x ¼″.  (For packing M1753L (1); packing M1753K (1).)|2|.30
&|||||655|STRIP, felt, 5″ x 36″ x ¼″.  (For packing M1753L (1); packing M1753K (1).)|2|.35
&|||||654|STRIP, felt, 9″ x 41½″ x ¼″.  (For packing M1753G (1).)|3|.60
*||||M1923|530|STRIP (front mud chute side plate), stiffener packing|(2)|.87
*||||M1788|536|STRIP, gasoline tank cover plate|(1)|1.23
&|||D30521|||STRIP, generator field coil insulating|4|.03 P
*||||M1005|500|STRIP, inlet louvre packing|(1)|.85''')
assembly(r,'STRIP, Officer’s map board hinge, assembly','1.44',note='&')
component(r,'*one M2446 Officer’s map board hinge STRIP (1)',ord='413',price='.48')
component(r,' two M2158 HINGE, butt, 2″ x 4¼″,')
component(r,'  six —      RIVET, countersunk head, ¼″ x ⅝″.)')
append_rows(r,'''*||||M2064|332|STRIP, packing (back floor plate)|(2)|.70
*||||M1920|528|STRIP, packing (rear of gasoline tank roof)|(1)|1.70
&|||||SH574K|STRIP, platform ammunition storage locking|1|.35
&|||||SH278C|STRIP, radiator cooling fan foot filler|2|.78
&|||||SH606D|STRIP, radiator reinforcing, left (rear)|1|5.00
&|||||SH606C|STRIP, radiator reinforcing, right (front)|1|5.00
*||||M1915B|526|STRIP (rear roof left plate), tapping, long (under track)|(1)|1.68
*||||M1915C|526|STRIP (rear roof left plate), tapping, short (under track)|(1)|.60
*||||M1904D|526|STRIP (rear roof right plate), tapping (under track)|(1)|1.35
*||||M1904C|526|STRIP (rear roof right plate), tapping, medium (under track)||1.68
*||||M1904B|526|STRIP (rear roof right plate), tapping, short|(1)|.60''')

r=add(231,'''*||||M2002|313|STRIP, removable plate bottom packing|(2)|2.95
*||||M1912C|528|STRIP (roof plate), tapping, long (side of back louvre)|(1)|1.68
*||||M1912B|528|STRIP (roof plate), tapping, short (side of back louvre)|(1)|.60
*||||M2074|343|STRIP, splash (plate under driver’s turret)|(1)|.56
*||||M2809|484|STRIP, sponson lower hinge packing|(2)|.88
*||||M2810|483|STRIP, sponson packing|(2)|1.74
*||||M2811|477|STRIP, sponson sloping bottom plate|(2)|1.08
*||||M2812B|484|STRIP, sponson sloping bottom plate, left|(1)|.98
*||||M2812A|484|STRIP, sponson sloping bottom plate, right|(1)|.98
*||||M2798|476|STRIP, sponson splash back|(2)|3.15
*||||M2797|475|STRIP, sponson wing plate splash, left side|(1)|1.06
*||||M2795|475|STRIP, sponson wing plate splash, right side|(1)|.79
&||||M2159|362|STRUT, machine gunner’s seat|2|2.25
||||M2121|378|STRUT, unditching gear, front, left|1|2.65
||||M2120|378|STRUT, unditching gear, front, right|1|2.65
||||M2125|360|STRUT, unditching gear, intermediate, left|1|2.65
||||M2124|360|STRUT, unditching gear, intermediate, right|1|2.65
&||||M2123|359|STRUT, unditching gear, rear, left|1|2.65
&|4|3||M2122|359|STRUT, unditching gear, rear, right|1|2.65''')
assembly(r,'STUD, air pressure pump, assembly','.34',qty='(2)')
component(r,'*one MX99 air pressure pump STUD (2)',ord='711',price='.25')
pieces(r,''' one MX102 air pressure pump stud NUT,
 one —       NUT, plain, S. A. E., hexagon, ⅜″,
 one —       NUT, plain, S. A. E., hexagon, ½″,
 two —       WASHER, lock, ⅜″.)''')
assembly(r,'STUD, bell crank lever, over all length 2⅛″, assembly','.24',note='&')
component(r,'*one SH970D bell crank lever STUD, over all length 2⅛″ (1)',ord='970',price='.22')
component(r,' one —         NUT, plain, U. S. Std., hexagon, ½″.)',ident='—',plate='12')
assembly(r,'STUD, bell crank lever, over all length 3 3/16″, assembly','.40',note='&')
component(r,'*one SH970B bell crank lever STUD, over all length 3 3/16″ (1)',ord='970',price='.38')
component(r,' one —         NUT, plain, U. S. Std., hexagon, ½″.)',ident='—',plate='12')
assembly(r,'STUD, crank shaft gear end plug, assembly','.41',note='&')
component(r,'*one LQ269A crank shaft gear end plug STUD (1)',mfr='B13487',price='.25')
component(r,' two —         GASKET, copper, asbestos, ⅜″,')
component(r,' one LQ198A NUT, special,')

r=start(232)
entry(r,'STUD, crank shaft gear end plug, assembly—Continued.',note='&');composed(r)
pieces(r,''' one LQ272A NUT, special,
 one —         PIN, split, 3/32″ x ⅝″,
 one LQ166A WASHER, special, ⅜″.)''')
assembly(r,'STUD, cylinder to crank case, with collar nut, assembly','$0.25',note='&',qty='(28)')
component(r,' one LQ248A cylinder to crank case NUT,')
component(r,'*one LQ247A STUD, special, ⅜″ x 1⅞″)',price='.19')
assembly(r,'STUD, cylinder to crank case, with plain nut, assembly','.25',note='&',qty='(72)')
component(r,'*one LQ247A STUD, special, ⅜″ x 1⅞″ (72)',mfr='B151',price='.19')
component(r,' one LQ248A NUT, special, ⅜″.)')
assembly(r,'STUD, distributor advance lever attaching, assembly','.09 P',note='&',qty='(4)')
pieces(r,'''*one D29896 distributor advance lever attaching STUD (4),
 one D29864 NUT, castle, No. 10—30 x .437″ x .218″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″.)''')
assembly(r,'STUD, distributor condenser and breaker plate, assembly','.09 P',note='&',qty='(2)')
pieces(r,'''*one D29595 distributor condenser and breaker plate STUD (2),
 one D30646 NUT, castle, No. 10—30 x .437″ x .406″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 one D30060 WASHER, lock, .195″ x .453″ x .046″,
 one D26503 WASHER, plain, .221″ x .468″ x .031″.)''')
assembly(r,'STUD, distributor condenser and breaker plate attaching, assembly','.05 P',note='&',qty='(6)')
pieces(r,''' one D29784 distributor condenser and breaker plate attaching STUD (6),
 one D29785 distributor condenser and breaker plate stud BUSHING,
 one D29780 distributor condenser and breaker plate stud SPRING,''')

r=start(233)
pieces(r,''' one —       PIN, split, brass, 1/16″ x ⅜″,
 two D29777 WASHER, plain, .194″ x .375″ x .031″.)''')
assembly(r,'STUD, distributor contact arm dismounting, assembly','.20 P',note='&',qty='(6)')
pieces(r,'''*one D29602 distributor contact arm dismounting STUD (6),
 one D29596 distributor contact arm dismounting stud insulating BUSH-~                ING,
 two D30146 distributor contact arm dismounting stud insulating WASH-~                ER,
 one D29494 distributor contact arm dismounting stud NUT.)''')
assembly(r,'STUD, distributor cup, assembly','.06 P',note='&',qty='(8)')
pieces(r,''' one D30373 distributor cup insulating WASHER,
 one D30534 distributor cup SPRING,
*one D30536 distributor cup STUD (8),
 one D30535 distributor cup stud NUT,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 one D26503 WASHER, plain, .221″ x .468″ x .031″.)''')
assembly(r,'STUD, distributor ignition coil and distributor head, with two plain washers, as-\n   sembly','.23 P',note='&',qty='(2)')
pieces(r,'''*one D29635 distributor ignition coil and distributor head STUD (2),
 one D29632 distributor ignition coil and distributor head stud INSULA-~                TOR,
 one D30274 distributor ignition coil and distributor head stud insulator~                GASKET,
 one D29765 distributor ignition coil and distributor head stud insulating~                WASHER, (large) (.26″ x .875″ x .062″),
 one D20791 distributor ignition coil and distributor head stud lock~                WASHER,
 one D29917 NUT, castle, ¼″—28 x .437″ x .281″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 two D29662 WASHER, plain, .257″ x .5″ x .031″.)''')
assembly(r,'STUD, distributor ignition coil and distributor head, assembly','.22 P',note='&',qty='(2)')
pieces(r,'''*one D29635 distributor ignition coil and distributor head STUD (2),
 one D29632 distributor ignition coil and distributor head stud INSULA-~                TOR,''')

r=start(234)
entry(r,'STUD, distributor ignition coil and distributor head, assembly—Continued.',note='&');composed(r)
pieces(r,''' one D30274 distributor ignition coil and distributor head stud insulator~                GASKET,
 one D29577 distributor ignition coil and distributor head stud insulator~                WASHER, (small) (.265″ x .562″ x .062″),
 one D29917 NUT, castle, ¼″—28 x .437″ x .281″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 one D21717 WASHER, lock, .256″ x .429″ x .062″,
 one D29662 WASHER, plain, .257″ x .5″ x .031″.)''')
assembly(r,'STUD, distributor resistance unit mounting, assembly','$0.09 P',note='&',qty='(2)')
pieces(r,'''*one D29663 distributor resistance unit mounting STUD (2),
 one D29578 distributor resistance unit mounting stud insulating~                WASHER,
 one D29573 NUT, castle, No. 6—32 x .218″ x .188″ thick,
 one D25116 WASHER, plain, .147″ x .313″ x .022″,
 two D29576 WASHER, plain, .144″ x .469″ x .022″.)''')
assembly(r,'STUD, engine control bell crank lever, assembly','.08 P',note='&')
component(r,'*one SH966G engine control bell crank lever STUD (1)',price='.06')
component(r,' one —         NUT, plain, U. S. Std., hexagon, ½″.)',ident='—',plate='12')
assembly(r,'STUD, generator brush arm mounting (grounded), assembly','.07 P',note='&',qty='(2)')
pieces(r,'''*one D30070 generator brush arm mounting STUD, grounded (2),
 one —       PIN, split, brass, 1/16″ x ⅜″.)''')
assembly(r,'STUD, generator brush and mounting (long terminal), assembly','.36 P',note='&')
pieces(r,'''*one D29811 generator brush arm mounting STUD (long terminal) (1),
 one D29869 generator brush arm mounting stud EYELET,''')

r=start(235)
pieces(r,''' one D30136 generator brush arm mounting stud insulating BUSHING,
 one D29868 generator brush arm mounting stud insulating BUSHING,
 one D29862 generator brush arm mounting stud insulating WASHER,~                .437″ x .75″ x .062″,
 one D29917 NUT, castle, ¼″—28 x .437″ x .281″ thick,
 one D29991 NUT, plain, ¼″—28 x .437″ x .125″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 one D21717 WASHER, lock, .256″ x .429″ x .062″,
 one D20915 WASHER, plain, .314″ x .625″ x .031″.)''')
assembly(r,'STUD, generator brush arm mounting, assembly','.17 P',note='&')
pieces(r,'''*one D30135 generator brush arm mounting STUD (1),
 one D30079 generator brush arm mounting stud insulating BUSHING,
 one D26715 NUT, plain, No. 10—30 x .437″ x .125″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 one D20495 WASHER, lock, .195″ x .393″ x .046″.)''')
entry(r,'STUD, generator brush arm spring',note='&',mfr='D29855',qty='4',price='.01 P')
assembly(r,'STUD, generator field coil, long, assembly','.37 P',note='&',mfr='(D29829)')
pieces(r,''' one D30262 generator field coil long stud BUSHING,
*one D29829 generator field coil STUD, long (1),
 one D30140 generator field coil stud insulating BUSHING,
 two D30085 generator field coil stud insulating WASHER,
 one D30313 generator field coil stud spacing COLLAR,
 one D22616 generator field coil stud WASHER (large),
 one D29864 NUT, castle, No. 10—30 x .437″ x .218″ thick,
 one D26715 NUT, plain, No. 10—30 x .437″ x .125″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 two D20495 WASHER, lock, .195″ x .393″ x .046″,
 one D30139 WASHER, plain, .194″ x .406″ x .031″.)''')
assembly(r,'STUD, generator field coil, short, assembly','.20 P',note='&',mfr='(D30383)')
pieces(r,'''*one D30383 generator field coil STUD, short (1),
 one D30140 generator field coil stud insulating BUSHING,
 one D30085 generator field coil stud insulating WASHER,
 one D29864 NUT, castle, No. 10—30 x .437″ x .218″ thick,
 one —       PIN, split, brass, 1/16″ x ⅜″,
 one D20495 WASHER, lock, .195″ x .393″ x .046″.)''')

r=start(236)
assembly(r,'STUD, ignition switch handle, with lever, left, assembly','$0.66 P',note='&',mfr='D13890')
pieces(r,'''*one D13772 ignition switch handle STUD (2),
*one D29752 ignition switch handle stud LEVER (2),
 one D23745 ignition switch lever SCREW.)''')
assembly(r,'STUD, ignition switch handle, with lever, right, assembly','.66 P',note='&',mfr='D13889')
component(r,'*one D13772 ignition switch handle STUD (2)',price='.18')
component(r,'*one D29752 ignition switch handle stud LEVER (2)',price='.46')
component(r,' one D23745 ignition switch lever SCREW.)')
assembly(r,'STUD, radiator cooling fan housing spider, assembly','.21',note='&',qty='(7)')
component(r,'*one SH279D radiator cooling fan housing spider STUD (7)',price='.18')
pieces(r,''' one —         NUT, plain, U. S. Std., hexagon, ½″,
 one —         WASHER, lock, ½″.)''')
assembly(r,'STUD, spark and throttle control lever, assembly','.90',note='&',qty='(2)')
component(r,'*one SH964E spark and throttle control lever STUD (2)',price='.78')
pieces(r,''' one —         NUT, plain, U. S. Std., hexagon, ⅝″,
 two —         NUT, plain, U. S. Std., hexagon, ¾″,
 one —         PIN, steel, 3/16″ x 1″.)''')
append_rows(r,'''(ge)&|||||LQ483A|STUD, special, oversize ¼″ x 1 3/16″|(ge)|.04
(ge)&|||||LQ484A|STUD, special, oversize ¼″ x 1 17/32″|(ge)|.04
(gf)&|||||LQ485A|STUD, special, oversize ⅜″ x 1¼″|(gf)|.05
(gi)&|||||LQ486A|STUD, special, oversize ⅜″ x 1⅞″|(gi)|.19
(gj)&|||||LQ487A|STUD, special, oversize ⅜″ x 1 15/16″|(gj)|.05''')
assembly(r,'STUD, switch and voltage regulator, assembly','.16 P',qty='(2)')
pieces(r,''' one D30385 switch and voltage regulator retaining WASHER,
*one D30369 switch and voltage regulator STUD (2),''')

r=start(237)
pieces(r,''' one D30360 switch and voltage regulator stud NUT,
 one D20495 WASHER, lock, .195″ x .393″ x .046″.)''')
assembly(r,'STUD, voltage regulator terminal, large, assembly','.23 P',note='&')
pieces(r,'''*one D30380 voltage regulator terminal STUD, large (1),
 one D29917 NUT, castle, ¼″—28 x .437″ x .281″ thick,
 one D29991 NUT, plain, ¼″—28 x .437″ x .125″ thick,
 one —       PIN, split, brass, 1/16″ x ⅝″,
 one D21717 WASHER, lock, .256″ x .429″ x .062″.)''')
assembly(r,'STUD, voltage regulator terminal, small, assembly','.22 P',note='&',qty='(2)')
pieces(r,'''*one D30366 voltage regulator terminal STUD, small (2),
 one D29864 NUT, castle, No. 10–30 x .437″ x .218″ thick,
 one D29991 NUT, plain, ¼″–28 x .437″ x .125″ thick,
 one —       PIN, split, brass, 1/16″ x ⅝″,
 one D21717 WASHER, lock, .256″ x .429″ x .062″,
 one D20495 WASHER, lock, .195″ x .393″ x .046″.)''')
entry(r,'STUD, ¼″ x 1 3/16″, threaded U. S. Std., 7/16″ and S. A. E., 9/16″, assembly',note='&',ident='131',qty='(28)',price='.08')
stacked(r,plate='13\n17');composed(r)
component(r,'*one LA88A STUD, ¼″ x 1 3/16″, threaded U. S. Std. 7/16″ and S. A. E.\n                   9/16″ (28)',mfr='131',price='.05')
pieces(r,''' one LQ89A NUT, special, S. A. E., ¼″,
 one —       PIN, split, 1/16″ x ½″.~                For water pump body, assembly (8); crank case, upper~                   half, assembly (12); to secure cam shaft driving shaft~                   upper housing, assembly (4).)''')
assembly(r,'STUD, ¼″ x 1 9/16″, threaded U. S. Std. 7/16″ and S. A. E. 9/16″, assembly','.07',note='&',ident='3',plate='14',qty='(21)')
component(r,'*one LQ196A STUD, ¼″ x 1 9/16″, threaded U. S. Std. 7/16″ and S. A. E.\n                   9/16″ (21)',mfr='132',price='.04')
pieces(r,''' one LQ89A NUT, special, S. A. E., ¼″,
 one —       PIN, split, 1/16″ x ½″.~                   For crank case, lower half, assembly (10); crank case,~                     upper half, assembly (3); intake header, assembly (2).)''')
assembly(r,'STUD, ¼″ x 2½″, threaded U. S. Std. 1 15/16″ and S. A. E. 9/16″, assembly','.13',note='&',ident='13154',plate='15',qty='(4)')
component(r,'*one LQ229A STUD, ¼″ x 2½″, threaded U. S. Std. 1 15/16″ and S. A. E.\n                   9/16″ (4)',mfr='B13154',price='.05')

r=start(238)
entry(r,'STUD, ¼″ x 2½″, threaded U. S. Std. 1 5/16″ and S. A. E. 9/16″, assembly—Con.',note='&',ident='1354',plate='15');composed(r)
pieces(r,''' two LQ89A  NUT, special, S. A. E., ¼″,
 two —         PIN, split, 1/16″ x ½″,
 two LQ113A WASHER, special, ¼″.~                   For securing filler LQ214A and plate LQ230A (4).)''')
assembly(r,'STUD, 5/16″ x 2½″, threaded U. S. Std. ½″ and S. A. E. ⅝″, assembly','$0.16',note='&',qty='(12)')
component(r,'*one LQ301A STUD, 5/16″ x 2½″, threaded U. S. Std. ½″ and S. A. E.\n                   ⅝″ (12)',mfr='301',price='.13')
pieces(r,''' one LQ51A  NUT, special, S. A. E., 5/16″,
 one —         PIN, split, 1/16″ x ⅝″.~                   For cylinder, assembly (1).)''')
assembly(r,'STUD, 5/16″ x 4⅛″, threaded U. S. Std. ½″ and ¾″, assembly','.14',note='&',qty='(2)')
component(r,' one X251 STUD, 5/16″ x 4⅛″, threaded U. S. Std. ½″ and ¾″ (2)',ord='803',price='.12')
component(r,' one —     NUT, plain, U. S. Std., hexagon, 5/16″.)')
assembly(r,'STUD, 5/16″ x 4⅜″, threaded U. S. Std. ½″ and S. A. E. ⅝″, assembly','.17',note='&',qty='(12)')
component(r,'*one LQ302A STUD, 5/16″ x 4⅜″, threaded U. S. Std. ½″ and S. A. E.\n                   ⅝″ (12)',mfr='180',price='.14')
pieces(r,''' one LQ51A  NUT, special, S. A. E., 5/16″,
 one —         PIN, split, 1/16″ x ⅝″.~                   For housing LQ45A (6).)''')
assembly(r,'STUD, ⅜″ x 1 7/16″, threaded U. S. Std. 13/32″ and S. A. E. ⅝″, assembly','.21',note='&',qty='(24)')
component(r,'*one LQ303A STUD, ⅜″ x 1 7/16″, threaded U. S. Std. 13/32″ and S. A. E.\n                   ⅝″ (24)',mfr='162',price='.15')
pieces(r,''' one LQ305A NUT, special, S. A. E. ⅜″, bronze,
 one —         PIN, split, 3/32″ x ⅝″.~                   For securing exhaust manifold (24).)''')

r=start(239)
assembly(r,'STUD, ⅜″ x 1½″, threaded U. S. Std. ½″, assembly','.10',note='&',qty='(2)')
component(r,'*one SH194D STUD, ⅜″ x 1½″, threaded U. S. Std. ½″ (2)',price='.07')
pieces(r,''' one —         NUT, plain, U. S. Std., hexagon, ⅜″,
 one —         WASHER, lock, ⅜″.)''')
assembly(r,'STUD, ⅜″ x 1 17/32″, threaded S. A. E. 13/32″ and 21/32″, assembly','.22',note='&',qty='(24)')
component(r,'*one LQ304A STUD, ⅜″ x 1 17/32″, threaded S. A. E. 13/32″ and 21/32″ (24)',mfr='B163',price='.15')
pieces(r,''' one LQ198A NUT, special, S. A. E., ⅜″,
 one —         PIN, split, 3/32″ x ⅝″.~                   For header LQ408A (2).)''')
assembly(r,'STUD, ⅜″ x 1 11/16″, threaded U. S. Std. 11/16″ and S. A. E. 27/32″, assembly','.08',note='&',qty='(6)')
component(r,'*one LQ233A STUD, ⅜″ x 1 11/16″, threaded U. S. Std. 11/16″ and S. A. E.\n                   27/32″ (6)',mfr='B263',price='.05')
pieces(r,''' one LQ198A NUT, special, S. A. E., ⅜″.~                   For securing governor in lower crank case (3); securing~                     governor in upper crank case (3).)''')
assembly(r,'STUD, ⅜″ x 1 31/32″, threaded U. S. Std. 21/32″ and S. A. E. ⅝″, assembly','.10',note='&',ident='43',plate='14',qty='(4)')
component(r,'*one LQ197A STUD, ⅜″ x 1 31/32″, threaded U. S. Std. 21/32″ and S. A. E.\n                   ⅝″ (4)',mfr='140',price='.05')
pieces(r,''' one LQ198A NUT, special, S. A. E., ⅜″,
 one —         PIN, split, 3/32″ x ⅝″,
 one LQ166A WASHER, special, ⅜″.~                   For securing water pump in lower crank case (4).)''')
assembly(r,'STUD, ⅜″ x 4 1/32″, threaded U. S. Std. 11/16″ and S. A. E. ½″, assembly','.41',note='&',qty='(5)')
component(r,'*one LQ271A STUD, ⅜″ x 4 1/32″, threaded U. S. Std. 11/16″ and S. A. E.\n                   ½″ (5)',mfr='B13489',price='.25')
pieces(r,''' two —         GASKET, copper, asbestos, ⅜″,
 one LQ198A NUT, special, S. A. E., ⅜″,
 one LQ272A NUT, special, S. A. E., ⅜″,
 one —         PIN, split, 3/32″ x ⅝″,
 one LQ166A WASHER, special, ⅜″.~                   For plug LQ265A (2 plug per stud).)''')

r=start(240)
assembly(r,'STUD, ⅜″ x 4 17/32″, threaded U. S. Std. 11/16″ and S. A. E. ½″, assembly','$0.41',note='&',qty='(6)')
component(r,'*one LQ270A STUD, ⅜″ x 4 17/32″, threaded U. S. Std. 11/16″ and S. A. E.\n                   ½″ (6)',mfr='13488',price='.25')
pieces(r,''' two —         GASKET, copper, asbestos, ⅜″,
 one LQ198A NUT, special, S. A. E., ⅜″,
 one LQ272A NUT, special, S. A. E., ⅜″,
 one —         PIN, split, 3/32″ x ⅝″,
 one LQ166A WASHER, special, ⅝″.~                   Used with plug LQ266A (1 for 2 plugs).)''')
assembly(r,'STUD, ½″ x 1 11/16″, threaded U. S. Std. ½″ and S. A. E. ⅞″, assembly','.14',note='&',qty='(4)')
component(r,'*one MX14 STUD, ½″ x 1 11/16″, threaded U. S. Std. ½″ and S. A. E. ⅞″\n                   (4)',ord='711',price='.10')
pieces(r,''' one —       NUT, castle, S. A. E., ½″,
 one —       PIN, split, 3/32″ x 1″.~                   For case M263 (4).)''')
assembly(r,'STUD, ½″ x 2 17/32″, threaded U. S. Std. 1″ and S. A. E. ⅞″, assembly','.35',note='&',qty='(4)')
component(r,'*one MX25 STUD, ½″ x 2 17/32″, threaded U. S. Std. 1″ and S. A. E. ⅞″\n                   (4)',ord='711',price='.31')
pieces(r,''' one —       NUT, castle, S. A. E., 1″,
 one —       PIN, split, 3/32″ x 1″.~                   For housing M250 to cover M264 (2).)''')
assembly(r,'STUD, ½″ x 2⅞″, threaded U. S. Std. 1″ and S. A. E. ⅞″, assembly','.37',note='&',qty='(2)')
component(r,'*one MX98 STUD, ½″ x 2⅞″, threaded U. S. Std. 1″ and S. A. E. ⅞″ (2)',ord='711',price='.33')
pieces(r,''' one —       NUT, castle, S. A. E., ½″,
 one —       PIN, split, 3/32″ x 1″.~                   For air pressure pump (2).)''')

r=start(241)
assembly(r,'STUD, ½″ x 3⅞″, threaded U. S. Std. 13/16″ and S. A. E. ⅞″, assembly','.41',note='&',qty='(2)')
component(r,'*one MX12 STUD, ½″ x 3⅞″, threaded U. S. Std. 13/16″ and S. A. E. ⅞″\n                   (2)',ord='711',price='.37')
pieces(r,''' one —       NUT, castle, S. A. E., ½″,
 one —       PIN, split, 3/32″ x 1″.~                   For securing bearing M306 to case M263.)''')
assembly(r,'STUD, ⅝″ x 2¼″, threaded U. S. Std. 1″ and S. A. E. 1″, assembly','.36',note='&',qty='(2)')
component(r,'*one A7681 STUD, ⅝″ x 2¼″, threaded U. S. Std. 1″ and S. A. E. 1″ (2)',price='.31')
pieces(r,''' one —       NUT, castle, S. A. E., ⅝″,
 one —       PIN, split, ⅛″ x 1¼″.~                   For securing cap A7679 to bracket B6205.)''')
assembly(r,'STUD, ¾″ x 3⅝″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″, assembly','.45',note='&',qty='(8)')
component(r,'*one MX9 STUD, ¾″ x 3⅝″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″\n                   (8)',ord='711',price='.40')
pieces(r,''' one —       NUT, castle, S. A. E., ¾″,
 one —       PIN, split, ⅛″ x 1⅜″.~                   For bracket M297 (4).)''')
assembly(r,'STUD, ¾″ x 4⅞″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″, assembly','.50',note='&',qty='(4)')
component(r,'*one MX10 STUD, ¾″ x 4⅞″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″\n                   (4)',ord='711',price='.45')
pieces(r,''' one —       NUT, castle, S. A. E., ¾″,
 one —       PIN, split, ⅛″ x 1⅜″.~                   For bracket M293 (2).)''')
assembly(r,'STUD, ¾″ x 5½″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″, assembly','.55',note='&',qty='(4)')
component(r,'*one MX36 STUD, ¾″ x 5½″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″\n                   (4)',ord='711',price='.50')
pieces(r,''' one —       NUT, castle, S. A. E., ¾″,
 one —       PIN, split, ⅛″ x 1⅜″.~                   For bracket M293 (2).)''')
assembly(r,'STUD, ¾″ x 5⅝″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″, assembly','.55',note='&',qty='(4)')
component(r,'*one MX5 STUD, ¾″ x 5⅝″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″\n                   (4)',ord='711',price='.50')
component(r,' one —       NUT, castle, S. A. E., ¾″,')

r=start(242)
entry(r,'STUD, ¾″ x 5⅝″, threaded U. S. Std. 1½″ and S. A. E. 1⅛″, assembly—Contd.',note='&');composed(r)
component(r,' one —     PIN, split, ⅛″ x 1⅜″.\n                   For case M263 (4).)')
append_rows(r,'''&|||||SH992D|SUPPORT, battery shelf|1|$1.36
&|||B180|||SUPPORT, driver’s switch|1|.72''')
assembly(r,'SUPPORT, engine, assembly','42.45',note='&')
pieces(r,''' one M184 engine double point suspension BRACKET,
 one M182 engine double point suspension BRACKET, left,
 one M183 engine double point suspension BRACKET, right,
 one M187 engine single point suspension PACKING,
 two M188 engine single point suspension PACKING,
 four M190 engine suspension bevel WASHER,
 one M179 engine suspension longitudinal SUPPORT, left,
 one M178 engine suspension longitudinal SUPPORT, right,
 one —     engine transverse CHANNEL, front, assembly,
 one —     engine transverse CHANNEL, rear, assembly,
 ten —     BOLT, U. S. Std., hexagon head, ½″ x 1¾″, with plain nut~              and lock washer,
 four —    BOLT, U. S. Std., hexagon head, ⅝″ x 2½″, with plain nut~              and lock washer,
 one —     BOLT, U. S. Std., hexagon head, ¾″ x 2½″, with plain nut~              and lock washer,
 two —     SCREW, cap, U. S. Std., hexagon head, ½″ x 1½″,
 two —     WASHER, lock, ½″.)''')
append_rows(r,'''&||||M179|71|SUPPORT, engine suspension longitudinal, left|1|4.07
&||||M178|71|SUPPORT, engine suspension longitudinal, right|1|4.07
*||||M2017B|345|SUPPORT, floor, inner, left (inside skirting plate)|(1)|35.65
*||||M2017A|345|SUPPORT, floor, inner, right (inside skirting plate)|(1)|35.65''')

r=add(243,'''*||||M2018B|320|SUPPORT, floor, outer, left (inside skirting plate)|(1)|29.60
*||||M2018A|320|SUPPORT, floor, outer, right (inside skirting plate)|(1)|29.60
&||||M2191|536|SUPPORT, gasoline tank cover|2|.48
%X|||B5930|||SUPPORT (machine gun) cleaning rod|1|.85
||||M2162|362|SUPPORT, machine gunner’s strut|2|.65
&|||B181|||SUPPORT, mechanic’s switch|1|.38
&||||M2820|473|SUPPORT, periscope spring clip|4|.24
&||||M898|177|SUPPORT, radiator, rear, No. 1|1|.78
&||||M899|177|SUPPORT, radiator, rear, No. 2|1|.78
&|—|24|||SH168G|SUPPORT (radiator) outlet pipe|1|.72
&|||||SH972A|SUPPORT, regulating tank|2|.78
&|||||SH962A|SUPPORT, regulating tank relief valve|1|.40
&|||||SH488C|SUPPORT, spare barrel (left sponson)|1|.38
&|||||SH372D|SUPPORT, spare barrel (main hull)|4|.25
&|||||SH286C|SUPPORT, spare parts container|2|.08
&||||M2819|473|SUPPORT, sponson seat|2|.62
(gy)&|||C69|||SUPPORT, switch panel box|1|1.00
%X|||||SH585B|SUPPORT, tachometer|1|.98
(gy)&|||C68|||SUPPORT, tank commander’s switch|1|.90
(gy)&|||C65|||SWITCH, driver’s telephone (complete)|1|7.50 P
(gy)&|||C66|||SWITCH, gunner’s telephone (complete)|2|6.00 P''')
assembly(r,'SWITCH, ignition, assembly','9.00 P',mfr='D1120')
pieces(r,''' one D30370 ignition switch ammeter terminal CONNECTOR (left),
 one D30620 ignition switch ammeter terminal connector SCREW,
 one D13741 ignition switch BASE, assembly,
 one D30052 ignition switch contact INSULATOR,
 one D13817 ignition switch COVER, with ammeter, assembly,
 one D30168 ignition switch cover plate SCREW (center),
 two D30169 ignition switch cover SCREW (side),
 two D30056 ignition switch handle contact ARM, left (lower), assembly,
 two D30053 ignition switch handle contact ARM, left (upper), assembly,
 two D30054 ignition switch handle contact ARM, right, assembly,
 one D13890 ignition switch handle STUD, with lever, left, assembly,
 one D13889 ignition switch handle STUD, with lever, right, assembly,
 two D30808 ignition switch resistance stud plain WASHER,
 one D13780 ignition switch resistance UNIT, left, assembly,
 one D13743 ignition switch resistance UNIT, right, assembly,''')

r=start(244)
entry(r,'SWITCH, ignition, assembly—Continued.',note='%X',mfr='D1120');composed(r)
pieces(r,''' one D30057 ignition switch terminal CONNECTOR (between amme-~                ter and contact stud),
 one D30055 ignition switch terminal CONNECTOR (between contact~                stud),
 one D30363 ignition switch terminal PLATE,
 nine D29864 NUT, castle, No. 10—30 x .437″ x .218″ thick,
 seven —       PIN, split, brass, 1/16″ x ⅜″,
 two —         PIN, split, brass, 1/16″ x ⅝″,
 one D26948 SCREW, slotted head, No. 6—38 x ¼″,
 one D27132 WASHER, lock, .140″ x 5/16″ x .031″,
 nine D20495 WASHER, lock, .195″ x .393″ x .046″.)''')
append_rows(r,'''(gy)&|||C64|||SWITCH, mechanic’s telephone (complete)|1|$7.50 P
(gy)&|||C63|||SWITCH, panel box (telephone) (complete)|1|10.00 P
%(gy)X|||||SH81A|SWITCH, starting (Bijur Co. type T461)|1|4.00 P''')
assembly(r,'SWITCH, surface toggle, assembly',note='&',qty='(3)')
pieces(r,'''*one A16054 surface toggle SWITCH,
 two —       SCREW, machine, round head, No. 8 (5/32″)—30 x 1″, with~                machine screw nut and plain washer.)''')
assembly(r,'SWITCH, surface toggle, with base, assembly',mfr='C5261')
pieces(r,''' one —       surface toggle switch BASE, assembly,
 three —     surface toggle SWITCH, assembly,
 one A6578 surface toggle switch plug SOCKET.)''')
append_rows(r,'''(gy)X|||C67|A&B||SWITCH, tank commander’s telephone (complete)|1|9.00 P
%(gy)X|||||SH585D|TACHOMETER, (Johns-Manville Co. type)|1|28.50 P''')
assembly(r,'TANK, engine oil, assembly','43.18',note='(gb)&')
