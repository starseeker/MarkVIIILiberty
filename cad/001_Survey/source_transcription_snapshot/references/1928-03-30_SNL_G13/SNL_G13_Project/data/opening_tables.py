"""Transcription of newly supplied opening tables; literal source line structure.

Reviewed source readings and specific uncertainties are recorded in review.json.
"""
from .parts_tables import row
TABLES={}
def add(page,content):
 records=[]
 for line in content.strip().splitlines():
  fields=line.split('|');assert len(fields)==9,(page,line,len(fields))
  records.append(row(*fields))
 TABLES[page]=records
add(4,r'''
*||||M2379|420|ANGLE, main turret rear top, left side|(1)|$0.90
*||||M2378|420|ANGLE, main turret rear top, right side|(1)|.90
*||||M2384|422|ANGLE, main turret right top, rear|(1)|3.79
*||||M2390B|421|ANGLE, main turret side bottom, left|(1)|8.69
*||||M2390A|421|ANGLE, main turret side bottom, right|(1)|8.69
*||||M2383B|422|ANGLE, main turret side top, front, left|(1)|1.03
*||||M2383A|422|ANGLE, main turret side top, front, right|(1)|1.03
*||||M2395|422|ANGLE, main turret vertical, front|(2)|1.48
*||||M2397|422|ANGLE, main turret vertical, rear, left side|(1)|1.28
*||||M2396|422|ANGLE, main turret vertical, rear, right side|(1)|1.28
*||||M2371|437|ANGLE, outlook turret bottom, side|(2)|.82
*|||||SH279B|ANGLE, radiator cooling fan, outlet, bottom side|(1)|.75
*|||||SH279C|ANGLE, radiator cooling fan, outlet, outside|(1)|.85
*|||||SH279A|ANGLE, radiator cooling fan, outlet, rear side|(1)|.85
*||||M2045B|332|ANGLE, rear outside wing plate to engine room back plate vertical, left|(1)|1.08
*||||M2045A|332|ANGLE, rear outside wing plate to engine room back plate vertical, right|(1)|1.08
*||||M2044B|336|ANGLE, removable plate to engine room vertical, left|(1)|3.72
*||||M2044A|336|ANGLE, removable plate to engine room vertical, right|(1)|3.72
%(gk)X||||M2176|364|ANGLE, roller inner skirting plate, length 6⅝″|2|.50
%(gk)X||||M2175|364|ANGLE, roller inner skirting plate, length 32⅜″|2|1.35
%X|6|2||M2078|332|ANGLE, roller support, No. 1|4|.75
%X|7|2||M2079|334|ANGLE, roller support, No. 2|4|.75
%X|8|2||M2080|332|ANGLE, roller support, No. 3|4|.75
%X|9|2||M2081B|331|ANGLE, roller support, No. 4, left (outer left or inner right)|2|1.85
%X||||M2081A|331|ANGLE, roller support, No. 4, right (outer right or inner left)|2|1.85
%(gk)X|10|2||M2082B|331|ANGLE, roller support, No. 5, left (outer)|1|1.75
%(gk)X||||M2082A|331|ANGLE, roller support, No. 5, right (outer)|1|1.75
%X|11|2||M2083B|331|ANGLE, roller support, No. 6, left (outer left or inner right)|2|1.45
%X||||M2083A|331|ANGLE, roller support, No. 6, right (outer right or inner left)|2|1.45
%X|12|2||M2084B|331|ANGLE, roller support, No. 7, left (outer left or inner right)|2|1.45
''')
add(5,r'''
%X||||M2084A|331|ANGLE, roller support, No. 7, right (outer right or inner left)|2|1.45
%X|13|2||M2085|331|ANGLE, roller support, No. 8|4|.75
*||||M1913|525|ANGLE, roof (at back plate)|(1)|7.85
*||||M1897B|535|ANGLE, roof, left (behind front mud chute)|(1)|1.54
*||||M1897A|535|ANGLE, roof, right (behind front mud chute)|(1)|1.54
&||||M788|289|ANGLE, seat support plate|2|.88
%X||||M2087|327|ANGLE, side plate splash|2|.98
*||||M2102B|328|ANGLE, side sloping plate, top, left|(1)|1.45
*||||M2102A|328|ANGLE, side sloping plate, top, right|(1)|1.45
*||||M2103B|328|ANGLE, side sloping plate to hull, left|(1)|.90
*||||M2103A|328|ANGLE, side sloping plate to hull, right|(1)|.90
*||||M1972B|307|ANGLE, side to engine room back plate vertical, left|(1)|3.05
*||||M1972A|307|ANGLE, side to engine room back plate vertical, right|(1)|3.05
*||||M2030A|341|ANGLE, side to roof connecting, left|(1)|3.08
*||||M2019B|323|ANGLE, side to roof connecting, left|(1)|37.25
*||||M2030B|341|ANGLE, side to roof connecting, right|(1)|3.08
*||||M2019A|323|ANGLE, side to roof connecting, right|(1)|37.25
*||||M2015B|367|ANGLE, sloping plate connecting, inside, left|(1)|2.50
*||||M2015A|367|ANGLE, sloping plate connecting, inside, right|(1)|2.50
*||||M2016B|367|ANGLE, sloping plate connecting, outside, left|(1)|2.70
*||||M2016A|367|ANGLE, sloping plate connecting, outside, right|(1)|2.70
%X||||M2090B|327|ANGLE, splash, front of side door, left|1|1.08
%X||||M2090A|327|ANGLE, splash, front of side door, right|1|1.08
%X||||M2072|332|ANGLE, splash, front sloping plate|3|1.18
%X||||M2091B|327|ANGLE, splash, rear of side door, left|1|1.55
%X||||M2091A|327|ANGLE, splash, rear of side door, right|1|1.55
%X||||M2088|327|ANGLE, splash, sponson, front|2|1.15
%X||||M2089|327|ANGLE, splash, sponson, rear|2|5.50
%X||||M2794B|483|ANGLE, sponson bottom plate splash, left|1|6.50
%X||||M2794A|483|ANGLE, sponson bottom plate splash, right|1|6.50
*||||M2778|482|ANGLE, sponson, left side (below gun shield)|(1)|4.50
*||||M2805|484|ANGLE, sponson left wing plate cleat, left (lower front)|(1)|.88
*||||M2808|478|ANGLE, sponson left wing plate cleat, lower rear|(1)|.52
*||||M2806|484|ANGLE, sponson left wing plate cleat, right (upper front)|(1)|.88
*||||M2807|478|ANGLE, sponson left wing plate cleat, upper rear|(1)|.52
*||||M2777|482|ANGLE, sponson, right side (below gun shield)|(1)|4.50
*||||M2804|487|ANGLE, sponson right wing plate cleat, left (lower)|(1)|.88
*||||M2803|487|ANGLE, sponson right wing plate cleat, right (upper)|(1)|.88
*||||M2793|483|ANGLE, sponson roof plate splash|(2)|4.75
''')

def start(p):
 TABLES[p]=[]
 return TABLES[p]
def entry(r,text,**kw):r.append(row(item=text,**kw))
def composed(r):entry(r,'     (Composed of:')
def component(r,text,**kw):entry(r,'          '+text,**kw)
def rivets(r,counts=('sixteen','sixteen','six'),first=False):
 if first:component(r,'three —      RIVET, countersunk head, ¼″ x 1 3/16″,')
 for count,desc in zip(counts,['⅜″ x 1⅜″,','copper, ¼″ x 1⅛″,','copper, ¼″ x 1⅜″.)']):
  component(r,f'{count} —      RIVET, countersunk head, {desc}')
def band_heading(r,desc,price,**kw):
 entry(r,'BAND, '+desc+', assembly',note='%X',qty=kw.pop('qty','(1)'),price=price,**kw);composed(r)
def low_band(r):component(r,'*one M344   low speed brake BAND (4)',ord='682',price='3.00')
def low_lining(r,price='2.75'):component(r,'*one MX108 low speed brake LINING (4)',ord='689',price=price)
def track_band(r):component(r,'*one M349   track brake BAND (4)',ord='691',price='2.25')
def track_lining(r):component(r,'*one MX107 track brake LINING (4)',ord='689',price='2.40')

r=start(8)
entry(r,'ARMATURE, voltage regulator, assembly',note='&',mfr='D13886',qty='(1)',price='$0.12 P');composed(r)
component(r,'*one D30192 voltage regulator armature CONTACT (1)',price='.06 P')
component(r,'*one D30144 voltage regulator armature PLATE (1).)',price='.06 P')
entry(r,'AXLE, carburetor float weight',note='&',mfr='13388',ord='LQ536A',qty='4',price='.03')
for desc,part,price,cp,nut,pin in [('jockey pulley','SH234L','.82','.78','one','one'),('jockey pulley arm','SH234K','1.36','1.28','two','two')]:
 entry(r,'AXLE, '+desc+', assembly',note='%X',qty='(1)',price=price);composed(r)
 component(r,f'*one {part} {desc} AXLE (1)',price=cp)
 component(r,f'{nut} —      NUT, crown, U. S. Std., ½″,')
 component(r,f'{pin} —      PIN, split, ⅛″ x 1″.)')
entry(r,'BALL, steel, ¼″.  (For retainer SH998C (30).)',note='(mh)&',qty='30',price='.01 P')
entry(r,'BALL, steel, 1″.  (For governor (4).)',note='(mh)&',qty='4',price='.10 P')
entry(r,'BALL, 7½″ ball mount',note='%X',ord='SH171A',qty='5',price='51.65')
band_heading(r,'clutch throwout stop','3.12')
component(r,'one M4160 clutch throwout stop anchor PLATE,')
component(r,'*one M4158 clutch throwout stop BAND (1)',ord='954',price='1.25')
component(r,'one M4159 clutch throwout stop LINING,')
component(r,'three —      RIVET, button head, ¼″ x ¾″,')
component(r,'six —        RIVET, button head, ¼″ x 1″,')
component(r,'fourteen —   RIVET, countersunk head, copper, 3/16″ x ½″.)')
band_heading(r,'high speed brake, long','3.50',qty='(2)',ident='7',plate='30')
component(r,'*one M359 high speed brake BAND, long (2)',ord='715',price='1.35')
component(r,'*one MX109 high speed brake LINING, long (2)',ord='689',price='2.00')

r=start(9)
component(r,'three —      RIVET, countersunk head, 5/16″ x 1⅛″,')
component(r,'one —        RIVET, countersunk head, copper, ¼″ x ¾″,')
component(r,'eleven —     RIVET, countersunk head, copper, ¼″ x 1″.)')
band_heading(r,'high speed brake, short','4.70',qty='(2)')
component(r,'one M361 high speed brake anchor END,')
component(r,'*one M360 high speed brake BAND (2)',ident='10',plate='30',ord='715',price='.95')
component(r,'*one M364 high speed brake LINING, short (2)',ord='715',price='1.02')
component(r,'six —        RIVET, countersunk head, 5/16″ x 1″,')
component(r,'three —      RIVET, countersunk head, 5/16″ x 1⅛″,')
component(r,'four —       RIVET, countersunk head, copper, ¼″ x 1″,')
component(r,'one —        RIVET, countersunk head, copper, ¼″ x 1¼″,')
component(r,'one —        SCREW, machine, flat head, brass, No. 14 (¼″ x ¾″).)')
band_heading(r,'low speed brake, lower half, left','8.83');low_band(r)
component(r,'one —      low speed brake band BRACKET, assembly,')
component(r,'one MX48   low speed brake band EAR,')
component(r,'one MX86   low speed brake band stop LUG,')
low_lining(r);rivets(r,first=True)
band_heading(r,'low speed brake, lower half, right','8.74');low_band(r)
component(r,'one MX48   low speed brake band EAR,')
component(r,'one MX86   low speed brake band stop LUG,')
component(r,'one MX49   low speed brake band support BRACKET,')
low_lining(r);rivets(r,first=True)
band_heading(r,'low speed brake, upper half, left','8.29');low_band(r)
component(r,'one MX48   low speed brake band EAR,')
component(r,'one MX49   low speed brake band support BRACKET,')

r=start(10)
entry(r,'BAND, low speed brake, upper half, left, assembly—Continued.',note='%X');composed(r)
low_lining(r,'$2.75');rivets(r)
band_heading(r,'low speed brake, upper half, right','8.43');low_band(r)
component(r,'one MX48   low speed brake band EAR,')
component(r,'one —      low speed brake band BRACKET, assembly,')
low_lining(r);rivets(r)
band_heading(r,'track brake, lower half, left','7.62');track_band(r)
component(r,'one MX47   track brake band BRACKET,')
component(r,'one MX46   track brake band EAR,')
component(r,'one MX87   track brake band stop LUG,')
track_lining(r);rivets(r,('thirteen','eighteen','five'),True)
band_heading(r,'track brake, lower half, right','6.71');track_band(r)
component(r,'one —      track brake band BRACKET, assembly,')

r=start(11)
component(r,'one MX46   track brake band EAR,')
component(r,'one MX87   track brake band stop LUG,')
track_lining(r);rivets(r,('thirteen','eighteen','five'),True)
band_heading(r,'track brake, upper half, left','6.60',ident='1',plate='31');track_band(r)
component(r,'one —      track brake band BRACKET, assembly,')
component(r,'one MX46   track brake band EAR,')
track_lining(r);rivets(r,('thirteen','eighteen','five'))
band_heading(r,'track brake, upper half, right','7.17');track_band(r)
component(r,'one MX47   track brake band BRACKET,')
component(r,'one MX46   track brake band EAR,')
track_lining(r);rivets(r,('thirteen','eighteen','five'))
for note,brit,ord,desc,qty,price in [
('%X','','SH40AC','drive sprocket chain side, inside','50','2.00'),
('%X','','SH40AB','drive sprocket chain side, outside','50','1.50'),
('*','','SH203B','fan and radiator air duct front side plate (steel, 1″ x ⅛″ x 20⅞″)','1','.50'),
('*','','SH203A','fan and radiator air duct upper front plate (steel, 1″ x ⅛″ x 17⅞″)','1','.40'),
('%X','M3069B','450','forward ammunition storage stop No. 1, left (length 19 13/16″)','1','.58'),
('%X','M3069A','450','forward ammunition storage stop No. 1, right (length 19 13/16″)','1','.58'),
('%X','M3070','449','forward ammunition storage stop No. 2, (length 20⅛″)','2','.58'),
('%X','M3073','449','forward ammunition storage stop No. 3, (length 20⅛″)','2','.58'),
('%X','M3072','449','forward ammunition storage stop No. 4, (length 26 25/32″)','2','.48'),
('%X','M3071','449','forward ammunition storage stop No. 5, (length 23 7/16″)','2','.48'),
('*','','B5933','pyrene refill bracket, ½″ x 28⅞″ (front)','1','.56'),
('*','','B5934','pyrene refill bracket, ¾″ x 28⅞″ (bottom)','1','.72'),
('*','','B5935','pyrene refill bracket, ¾″ x 28⅞″ (rear)','1','.85'),
('%X','M3022','552','rear shell storage stop, length 21 3/16″','2','.50')]:
 entry(r,'BAR, '+desc,note=note,brit=brit,ord=ord,qty=qty,price=price)

r=start(12)
for note,b,o,desc,q,price in [
('%X','M3030','552','rear shell storage stop, length 25⅞″','4','$0.50'),
('&','M342','686','transmission brake band stop','2','3.78'),
('%X','M3803B','266','6-pdr. gun pedestal shell holder stop, left (rear lower)','1','.50'),
('%X','M3803A','266','6-pdr. gun pedestal shell holder stop, right (rear lower)','1','.50'),
('%X','M3805','266','6-pdr. gun pedestal stop, length 14¾″ (side)','2','.50'),
('%X','M3804','266','6-pdr. gun pedestal stop, length 27⅜″ (rear upper)','2','.30')]:entry(r,'BAR, '+desc,note=note,brit=b,ord=o,qty=q,price=price)
entry(r,'BARREL, carburetor butterfly, assembly',note='&',qty='(2)',price='9.30');composed(r)
for t in ['two LQ515A carburetor altitude air valve stop SCREW,','one —      carburetor altitude VALVE, assembly,','two LQ523A carburetor BUTTERFLY,']:component(r,t)
component(r,'*one LQ564A carburetor butterfly BARREL (2)',mfr='13369',price='5.05')
component(r,'*two LQ560A carburetor butterfly barrel screw BUSHING (4)',mfr='14379',price='.05')
for t in ['one —      carburetor butterfly SHAFT, long, assembly,','one —      carburetor butterfly SHAFT, short, assembly,','one LQ519A carburetor butterfly shaft WASHER,','one LQ539A carburetor gear SECTOR,','one LQ540A carburetor gear sector adjusting SCREW,','one LQ508A carburetor (gear sector adjusting screw clamping) SCREW,','two LQ558A carburetor gear sector set SCREW,','six LQ551A carburetor priming plug SCREW.)']:component(r,t)
entry(r,'BASE, air pressure pump',note='&',ident='5',plate='5',ord='SH903A',qty='1',price='9.03')
entry(r,'BASE, distributor adapter, with cup, assembly',qty='(2)',price='20.97 P');composed(r)
for t in ['one D29788 distributor adapter BASE,','two D28929 distributor ball bearing WASHER,','one D13733 distributor CAM, assembly,','one D30008 distributor cam KEY,','one D29579 distributor cam oil RETAINER, felt,','one D29571 distributor cam oil RETAINER, steel,']:component(r,t)

r=start(13)
for t in ['one D13779 distributor contact ARM, curved, assembly,','two D13737 distributor contact ARM, straight, assembly,','two (D29574) distributor contact arm spring SCREW, assembly,','one D29728 distributor contact curved arm SPRING,','three (D13687) distributor contact SCREW, assembly,','two D13803 distributor contact straight arm SPRING, assembly,','one D14180 distributor CUP, assembly,','*one D29783 distributor cup BEARING (2),','one D29782 distributor cup GASKET,','four D30111 distributor head clamp SPRING,','four D29802 distributor head clamp spring PIN,','one D29603 distributor ignition coil and distributor head stud and plate\n                         CONNECTOR,','one —      distributor ignition coil and head STUD, with two plain\n                         washers, assembly,','one —      distributor ignition coil and head STUD, assembly,','one D13747 distributor resistance UNIT, assembly,','one (D29663) distributor resistance unit mounting STUD, assembly,','one D13720 distributor ROTOR, assembly,','one D13899 distributor SHAFT, with oil thrower, assembly,','one D29611 distributor upper ball bearing RETAINER,','one D30061 WASHER, plain, .178″ x .504″ x .031″.)']:component(r,t)
entry(r,'BASE, distributor adapter',note='&',mfr='D29788',qty='2',price='.65 P')
entry(r,'BASE, ignition switch, assembly',note='(b)&',mfr='D13741',qty='(1)',price='2.55 P')
entry(r,'BASE, surface toggle switch, assembly',note='X',qty='(1)',price='1.12');composed(r)
component(r,'*one B101817 surface toggle switch BASE,')
component(r,'*one A16053 surface toggle switch STRIP,')
component(r,'two —      SCREW, cap, U. S. Std., button head, ¼″ x 2″, with plain\n                         nut, plain washer and lock washer.)')
for note,b,o,desc,q,price in [
('&','','SH576D','ammunition storage lid, long','2','.38'),
('&','','SH576F','ammunition storage lid, short, left','2','.20'),
('&','','SH576E','ammunition storage lid, short, right','2','.20'),
('*','M2386','420','main turret flap, bottom','(2)','.98'),
('*','M2385B','420','main turret flap, side, left (left front or right rear)','(2)','.82'),
('*','M2385A','420','main turret flap, side, right (right front or left rear)','(2)','.82'),
('*','M2359','420','main turret roof door, end','(4)','.28'),
('*','M2358','420','main turret roof door, side','(2)','.50'),
('&','','SH571B','platform ammunition storage, left','1','.55')]:entry(r,'BATTEN, '+desc,note=note,brit=b,ord=o,qty=q,price=price)

r=start(14)
entry(r,'BATTEN, platform ammunition storage, right',note='&',ord='SH571A',qty='1',price='$0.55')
entry(r,'BATTEN, removable platform ammunition storage',note='&',ord='SH579B',qty='2',price='.42')
entry(r,'BATTERY, ignition (Willard storage type, SYR–13), assembly',note='%X',qty='(1)',price='24.00 P');composed(r)
for t in ['one W–X899 ignition battery CASE, assembly,','three W–O–260 ignition battery CONNECTOR, top,','twenty-four W–J46 ignition battery INSULATOR (rubber),','one —       ignition battery JAR (hard rubber),','four W–C153 ignition battery jar COVER,','four —      ignition battery jar cover PLATE, bottom, assembly,','four W–E690 ignition battery PLATE, negative, assembly,','four W–E689 ignition battery PLATE, positive, assembly,','four —      ignition battery vent PLUG, assembly,']:component(r,t)
entry(r,'     Approx. ½ —      COMPOUND, sealing, lb.,')
entry(r,'  Approx. 1 pt. —     ELECTROLYTE, 1.255 S. G., qt.)')
entry(r,'BATTERY, starting and lighting (Willard type STR–4), assembly',note='%X',qty='(2)',price='18.00 P');composed(r)
for t in ['one W–P–24 starting and lighting battery CABLE, negative terminal,\n                         assembly,','one W–P–23 starting and lighting battery CABLE, positive terminal,\n                         assembly,','one W–X854 starting and lighting battery CASE, assembly,','two W–O–270 starting and lighting battery CONNECTOR, top,','six W–K103 starting and lighting battery holddown BLOCK,','three W–B173 starting and lighting battery JAR (hard rubber),','three W–C154 starting and lighting battery jar COVER (hard rubber),','three W–AF179 starting and lighting battery jar SPACER (rectangular\n                         5⅞″ x 7⅞″ x 1/16″),','three W–E712 starting and lighting battery PLATE, negative, assembly,','three W–E711 starting and lighting battery PLATE, positive, assembly,']:component(r,t)

r=start(15)
for t in ['six W–S1029 starting and lighting battery sealing NUT (lead, single\n                         thread),','thirty-six W–J50 starting and lighting battery SEPARATOR,','six W–AD18 starting and lighting battery terminal post WASHER\n                         (soft rubber),','three W–L11 starting and lighting battery vent PLUG,','two W–AF49 starting and lighting battery WEDGE,','eight W–S1021 starting and lighting battery wood SCREW,','one —      COMPOUND, sealing, lb.,','one —      ELECTROLYTE, 1.275 S. G. qt.)']:component(r,t)
entry(r,'BEADING, drive chain casing',note='*',brit='M1585',ord='232',qty='8',price='.75')
for b,o,desc,q,price in [
('M1900','533','channel roof (front of rear louvre)','(1)','8.98'),
('M1941','519','floor (between floor plates 2 and 3)','(1)','16.75'),
('M1927','520','floor (between floor plates 3 and 4)','(1)','15.75'),
('M1928','523','floor (between floor plates 4 and 5)','(1)','15.75'),
('M1929','523','floor (between floor plates 6 and 7)','(1)','15.75'),
('M1930','520','floor (between floor plates 7 and 8)','(1)','15.75'),
('M2039B','334','front diaphragm, side, left','(2)','8.25'),
('M2039A','334','front diaphragm, side, right','(2)','8.25'),
('M1898','531','removable roof (over engine)','(1)','6.52'),
('M1899','531','roof, left (at side of removable beam)','(1)','2.45'),
('M1925','531','roof, right (at side of removable beam)','(1)','2.45'),
('M2041','336','vertical, No. 1 and 2 engine room plate, right','(1)','7.08'),
('M2042','336','vertical, No. 2 and 3 engine room plate, right','(1)','6.08'),
('M2029','335','vertical, rear of sponson, left side','(1)','8.25'),
('M2047','335','vertical, rear of sponson, right side','(1)','8.25')]:entry(r,'BEAM, '+desc,note='*',brit=b,ord=o,qty=q,price=price)
entry(r,'BEARING, air pressure pump',note='&',ident='4',plate='5',ord='SH900A',qty='2',price='.75')
entry(r,'BEARING, ball, radial, dia. 1.1811″, bore .3937″, face .3543″.  (For distributor (4);\n  generator (1).)',note='(c)&',mfr='{Monarch 6200, N.\n  D. 1200 or equal}',qty='9',price='2.10 P')
entry(r,'BEARING, ball, radial, dia. 1.8504″, bore .6693″, thickness .5512″.  (For water\n  pump (1).)',note='(c)&',ident='8056',plate='17',mfr='HB303 or equal',qty='1',price='4.55 P')
entry(r,'BEARING, ball, radial, dia. 1.8504″, bore .7874″, height .5512″.  (For ventilating\n  fan (2); shaft LQ94A (2).)',note='(c)&',mfr='SKF1204 or equal',qty='6',price='3.70 P')
entry(r,'BEARING, ball, radial, dia. 2.0472″, bore .7874″, face .5906″.  (For jockey pulley\n  (1).)',note='(c)&',mfr='SKF1304 or equal',qty='1',price='6.00 P')
entry(r,'BEARING, ball, radial, dia. 2.8346″, bore 1.378″, height .6693″.  (For pin SH943A\n  (1).)',note='%(c)X',mfr='SKF1207 or equal',ord='943',qty='2',price='2.75 P')
entry(r,'BEARING, ball, radial, dia. 2.4410″, bore 1.1811″, height .6299″.  (For shaft\n  LQ386A (2).)',note='(c)&',ident='8060',plate='16',mfr='HB206 or equal',qty='2',price='7.30 P')

r=start(16)
entry(r,'BEARING, ball, radial, dia. 3.5433″, bore 1.5748″, height .9055″.  (For housing\n  SH282B (2).)',note='(c)&',mfr='SKF1308 or equal',qty='2',price='$11.98 P')
entry(r,'BEARING, ball, thrust, dia. 2.8347″, bore 1.1811″, height .9449″.  (For governor\n  (1).)',note='(c)&',mfr='Gurney 306 or equal',qty='1',price='8.50 P')
entry(r,'BEARING, ball, thrust dia., 2.87″, bore 1.7717″, height .79″.  (For governor (1).)',note='(c)&',mfr='SKF1109F or equal',qty='1',price='9.50 P')
entry(r,'BEARING, ball, thrust, dia. 6.1024″, bore 4.1339″, height 1.5748″.  (For gear\n  M258A (1).)',note='(c)&',mfr='Fafnir 1821 or equal',qty='2',price='30.84 P')
for n,ident,price,lower,upper,m1,m2,cp in [
(1,'8480','3.02','LQ10A','LQ11A','B8111','B8112','1.49'),
(2,'8481','1.38','LQ13A','LQ14A','B8113','B8114','.67'),
(3,'8482','1.52','LQ17A','LQ16A','B8116','B8115','.74'),
(4,'8483','1.18','LQ20A','LQ19A','B8118','B8117','.57')]:
 entry(r,f'BEARING, cam shaft, No. {n}, assembly',note='&',ident=ident,plate='13',qty='(2)',price=price);composed(r)
 component(r,f'*one {lower} cam shaft BEARING, lower half, No. {n} (2)',mfr=m1,price=cp)
 component(r,f'*one {upper} cam shaft BEARING, upper half, No. {n} (2)',mfr=m2,price=cp)
 component(r,'four LQ27A SCREW, special, No. 8 x ½″.)')
entry(r,'BEARING, cam shaft, No. 5, assembly',note='&',ident='8484',plate='13',qty='(2)',price='1.12');composed(r)
component(r,'*one LQ23A cam shaft BEARING, lower half, No. 5 (2)',mfr='B8120',price='.54')

r=start(17)
component(r,'*one LQ22A cam shaft BEARING, upper half, No. 5 (2)',mfr='B8119',price='.54')
component(r,'four LQ27A SCREW, special, No. 8 x ½″.)')
entry(r,'BEARING, cam shaft, No. 6, assembly',note='&',ident='12485',plate='13',qty='(2)',price='1.48');composed(r)
component(r,'*one LQ26A cam shaft BEARING, lower half, No. 6 (2)',mfr='B12249',price='.72')
component(r,'*one LQ25A cam shaft BEARING, upper half, No. 6 (2)',mfr='B12248',price='.72')
component(r,'four LQ27A SCREW, special, No. 8 x ½″.)')
entry(r,'BEARING, cam shaft, flywheel end, assembly',note='&',qty='(2)',price='1.42');composed(r)
for t in ['one LQ28A cam shaft BEARING, flywheel end,','one LQ32A cam shaft bearing end GASKET,','one LQ29A cam shaft end PLATE,','four LQ30A SCREW, special, No. 10 x 5/16″,']:component(r,t)
component(r,'*one LQ31A WIRE, lock, W & M Ga. No. 18 x 8″.)',mfr='177',price='.01')
for note,ident,plate,m,b,o,desc,q,price in [
('&','12250','13','B12250','','LQ28A','cam shaft, flywheel end','2','.54'),
('&','33','21','','','SH998D','clutch','1','3.75'),
('(gaa)&','13235','18','B13461','','LQ128A','connecting rod crank shaft, lower half','6','1.70'),
('(gaa)&','13457','18','B13460','','LQ127A','connecting rod crank shaft, upper half','6','1.70'),
('&','','','B13418','','LQ238A','crank shaft, lower half, long','1','2.10'),
('&','','','B13459','','LQ240A','crank shaft, lower half, short','6','1.16'),
('&','','','B13417','','LQ239A','crank shaft, upper half, long','1','2.10'),
('&','','','B13435','','LQ241A','crank shaft, upper half, short','6','1.16'),
('(gy)&','','','S375','','','distance recorder drive pinion shaft','1','.38'),
('%X','','','','','SH289E','driver’s seat','4','.83'),
('&','','','','M2154','363','engine room sliding door catch','2','.88'),
('&','','','B12048','','LQ273A','flywheel thrust','1','8.92'),
('&','','','D13732','','','generator ball','1','2.10')]:entry(r,'BEARING, '+desc,note=note,ident=ident,plate=plate,mfr=m,brit=b,ord=o,qty=q,price=price)
entry(r,'BEARING, generator drive shaft, lower, with container, assembly',note='&',ident='8148',plate='16',qty='(1)',price='8.65');composed(r)
component(r,'*one HB206 or equal BEARING, ball, radial, dia. 2.4410″, bore 1.1811″,\n                         height .6299″ (2)',price='7.30')
component(r,'*one LQ398A       generator driving shaft lower ball bearing CON-\n                         TAINER (1).)',mfr='B1847',price='1.35')
entry(r,'BEARING, roller, (Timken type), assembly',note='(c)&',ident='3',plate='20',mfr='Timken 316–312 or\n  equal.',qty='(4)',price='2.90');composed(r)
component(r,'one 316 roller bearing CONE,')
component(r,'one 312 roller bearing CUP.')
entry(r,'                    For fan bevel gear box (4).)')

r=start(18)
entry(r,'BEARING, roller, (Timken type), assembly',note='(c)&',ident='54\n7',plate='22\n23',mfr='Timken 6454–6420\n  or equal.',qty='(2)',price='$11.90 P');composed(r)
component(r,'one 6454 roller bearing CONE,');component(r,'one 6420 roller bearing CUP.')
entry(r,'                    For transmission bevel pinion shaft (2).)')
for note,ident,plate,m,b,o,text,q,price in [
('&','','','','M1406','54','BEARING, shaft, inner.  (For track driving wheel shaft (1).)','2','12.00'),
('&','','','','M1546','54','BEARING, shaft, inner.  (For track roller pinion shaft (1).)','2','12.00'),
('&','7','27','','M1407','54','BEARING, shaft, outer.  (For track driving shaft track roller pinion (1).)','4','12.00'),
('&','','','D13830','','','BEARING, tachometer drive shaft','1','.88 P'),
('&','15\n22','23','','M306','714','BEARING, transmission vertical shifter shaft','2','1.89'),
('%X','','','','','SH900G','BELT, air pressure pump (link V type, 54″ long, ⅝″ wide, 28° angle)','1','5.35 P'),
('%X','','','','','SH233E','BELT, fan, endless','1','10.00 P'),
('%X','','','','','SH103E','BELT, transmission mechanical lubricator (link V type, 60″ long, ⅝″ wide, 28°\n  angle)','1','5.75 P'),
('(mh)&','','','','','','BELTING, leather, 3″ single ply, 3″ wide, ft. (one piece 32 11/16″ long required for\n  cover SH233B)','—','.60 P'),
('%X','2','4','','M987','501','BLADE, inlet louvre','34','4.00'),
('%X','','','','M994','504','BLADE, outlet louvre','28','6.00'),
('&','','','','','SH278A','BLADE, radiator cooling fan','64','.22'),
('%X','','','','','SH146C','BLOCK, (fan bevel gear) filler','1','1.32'),
('X','','','','M3065B','450','BLOCK, forward ammunition storage, left','1','2.00'),
('X','','','','M3065A','450','BLOCK, forward ammunition storage, right','1','2.00'),
('X','','','','M3064B','450','BLOCK, forward ammunition storage shell, left','1','2.65'),
('X','','','','M3064A','450','BLOCK, forward ammunition storage shell, right','1','2.65'),
('%X','','','','','SH396B','BLOCK, gun support, front, left','1','.85'),
('%X','','','','','SH396A','BLOCK, gun support, front, right','1','.85'),
('%X','','','','','SH396D','BLOCK, gun support, rear, left','1','.75'),
('%X','','','','','SH396C','BLOCK, gun support, rear, right','1','.75')]:entry(r,text,note=note,ident=ident,plate=plate,mfr=m,brit=b,ord=o,qty=q,price=price)

r=start(19)
for grooved,part in [(False,'X262'),(True,'X263')]:
 entry(r,'BLOCK, semaphore bottom bearing, '+('grooved, ' if grooved else '')+'assembly',note='&',qty='(1)',price='1.50');composed(r)
 component(r,f'*one {part} semaphore bottom bearing BLOCK'+(', grooved' if grooved else '')+' (1)',ord='801',price='1.46')
 component(r,'two —      NUT, plain, U. S. Std., hexagon, 5/16″.)')
entry(r,'BLOCK, semaphore top bearing',note='&',brit='X256',ord='801',qty='2',price='.74')
entry(r,'BLOCK, starting and lighting battery holddown',note='&',mfr='W–K103',qty='12',price='.05 P')
entry(r,'BLOCK, 6-pdr. gun pedestal shell, left',note='*',brit='M3806B',ord='267',qty='(1)',price='1.50')
entry(r,'BLOCK, 6-pdr. gun pedestal shell, right',note='*',brit='M3806A',ord='267',qty='(1)',price='1.50')
entry(r,'BOARD, instrument',note='%X',ord='SH980A',qty='1',price='.98')
entry(r,'BOARD, intensifier, assembly',note='%X',qty='(1)',price='3.00');composed(r)
for t in ['one SH1021B intensifier BOARD, lower,','one SH1021A intensifier BOARD, upper,','four SH1021D intensifier board SPACER,','two —      intensifier high tension CABLE, length 9½″, with intensi-\n                         fier, assembly,','two —      intensifier high tension CABLE, length 11″, with intensi-\n                         fier, assembly,','two —      intensifier high tension CABLE, length 12½″, with intensi-\n                         fier, assembly,','four —     BOLT, stove, round head, ¼″ x 1 7/16″, with stove bolt nut\n                         and washer.)']:component(r,t)
entry(r,'BOARD, intensifier, lower',note='&',ord='SH1021B',qty='4',price='.12 P')
entry(r,'BOARD, intensifier, upper',note='&',ord='SH1021A',qty='4',price='.12 P')
entry(r,'BOARD, map.  (For officer (1); driver’s (1).)',note='%X',brit='M2441',ord='425',qty='2',price='.88')
entry(r,'BOARD, switch',note='&',ident='25',plate='2',ord='SH994B',qty='1',price='1.25')
entry(r,'BODY, carburetor, assembly',note='&',qty='(2)',price='26.50');composed(r)
for t in ['two LQ513A carburetor air intake dowel PIN,','two LQ552A carburetor bail hook PIN,','two LQ553A carburetor bail hook pin taper PIN,']:component(r,t)
component(r,'*one LQ565A carburetor BODY (2)',mfr='13366',price='14.05')
for t in ['two LQ524A carburetor body PLUG,','two —      carburetor cap JET, assembly,','two LQ559A carburetor cap jet LOCK,']:component(r,t)

r=start(20)
entry(r,'BODY, carburetor, assembly—Continued.',note='&');composed(r)
for t in ['two (LQ525A) carburetor channel SCREW, assembly,','two LQ528A carburetor CHOKE, No. 36 (army),','two (LQ529A) carburetor compensating JET, assembly,','one LQ530A carburetor, compensating jet and needle valve seat fiber\n                         WASHER,','two (LQ526A) carburetor float cover clamp BOLT, assembly,','two (LQ533A) carburetor float cover clamp bolt PIN, assembly,','one (LQ537A) carburetor gasoline PLUG, assembly,','four (LQ541A) carburetor internal body PLUG, assembly,','two —      carburetor main JET, assembly,','one —      carburetor needle valve SEAT, assembly,','one —      PIN, split, 1/16″ x ⅜″,']:component(r,t)
component(r,'*two —Q512B WIRE, lock, soft iron, W. & M. Ga. No. 18 x 5″ (4)',price='$0.01')
component(r,'*one LQ512A WIRE, lock, soft iron, W. & M. Ga. No. 18 x 8″ (2).)',mfr='264',price='.01')
entry(r,'BODY, oil pump, lower half, assembly',note='%X',qty='(1)',price='3.69');composed(r)
component(r,'*one LQ427A oil pump BODY, lower half (1)',mfr='D8190–33',price='3.53')
for t in ['one LQ432A oil pump driving shaft BUSHING, lower,','one LQ428A oil pump lower half body PLUG,','one LQ163A DOWEL, 3/16″ x ⅜″.)']:component(r,t)
entry(r,'Body, oil pump, upper half, assembly',note='%X',qty='(1)',price='4.77');composed(r)
component(r,'*one LQ400A oil pump BODY, upper half (1)',plate='33',mfr='C8189',price='4.12')
component(r,'one LQ442A oil pump driving shaft BUSHING, upper,')
component(r,'*two LQ441A oil pump upper half body PLUG',price='.05')
component(r,'one LQ458A oil pump upper screen NUT,')
component(r,'one LQ459A oil pump upper screen nut LOCK.)')
entry(r,'BODY, transmission mechanical lubricator suction screen',note='&',ord='SH101K',qty='6',price='.06')

def bolt(r,desc,qty,price,note='%X',**kw):
 entry(r,'BOLT, '+desc+', assembly',note=note,qty=qty,price=price,**kw);composed(r)
def cotter(r,size,end=True):component(r,'one —      PIN, split, '+size+('.)' if end else ','))

r=start(21)
entry(r,'BODY, triple combination tap',note='&',ident='2',plate='7',ord='SH951C',qty='1',price='7.25')
entry(r,'BODY, water pump, assembly',note='&',ident='12071',plate='17',qty='(1)',price='6.48');composed(r)
component(r,'*one LQ144A water pump BODY (1)',mfr='C14332',price='5.76')
component(r,'eight (LQ88A) STUD, ¼″ x 1 3/16″, threaded U. S. Std. 7/16″ and S. A. E.\n                         9/16″, assembly,')
component(r,'eight LQ113A WASHER, special, ¼″.)')
bolt(r,'battery shelf support holding down, length 8⅜″','(2)','.22')
component(r,'*one SH996G battery shelf support holding down BOLT, length 8⅜″ (2)',price='.06')
component(r,'one SH996D battery shelf support holding down bolt NUT,')
component(r,'one —      WASHER, plain, 5/16″.)')
entry(r,'Bolt, battery shelf support holding down, length 12¼″, assembly',note='%X',qty='(4)',price='.24');composed(r)
component(r,'*one SH996C battery shelf support holding down BOLT, length 12¼″',price='.08')
component(r,'one SH996D battery shelf support holding down bolt NUT,')
component(r,'one —      WASHER, plain, 5/16″.)')
bolt(r,'cam shaft','(14)','.05',note='&',ident='171',plate='13')
component(r,'*one LQ40A cam shaft BOLT (14)',mfr='B171',price='.02')
component(r,'one LQ41A NUT, special, S. A. E., ¼″,');cotter(r,'1/16″ x ½″')
bolt(r,'cam shaft housing','(36)','.24',ident='178',plate='13')
component(r,'*one LQ50A cam shaft housing BOLT',mfr='B178',price='.18')
component(r,'one LQ51A NUT, special, S. A. E., 5/16″,');cotter(r,'1/16″ x ⅝″',False)
component(r,'two LQ52A WASHER, special, 5/16″.)')
bolt(r,'carburetor float cover clamp','(4)','.25',note='&')
component(r,'*one LQ526A carburetor float cover clamp BOLT',mfr='13383',price='.15')
component(r,'one LQ585A carburetor float cover wing NUT.')
bolt(r,'carburetor throttle control shaft bracket','(2)','.09')
component(r,'*one LQ114A carburetor throttle control shaft bracket BOLT (2)',mfr='B211',price='.05')
component(r,'one LQ89A NUT, special, S. A. E., ¼″,');cotter(r,'1/16″ x ½″',False)
component(r,'one LQ113A WASHER, special, ¼″.)')

r=start(22)
bolt(r,'carburetor throttle shaft yoke end','(4)','$0.16')
component(r,'one LQ514A carburetor altitude air valve and yoke end bolt NUT,')
component(r,'*one LQ555A carburetor throttle shaft yoke end BOLT (4)',mfr='13414',price='.08')
component(r,'one LQ556A carburetor throttle shaft yoke end bolt WASHER,');cotter(r,'1/16″ x ½″')
bolt(r,'carburetor to intake header','(2)','.42')
component(r,'one LQ421A carburetor to intake header bolt HEAD,')
component(r,'*one LQ422A carburetor to intake header bolt SHANK',mfr='8398',price='.38')
component(r,'one —      PIN, steel, ⅛″ x ⅜″.)')
entry(r,'BOLT, carriage, ¼″ x 1 9/16″, with nut and lock washer.  (For holder SH550H (1);\n  case M3020 (2).)',note='%(sh)R',qty='(86)',price='.02 P')
entry(r,'BOLT, carriage, ⅜″ x 1½″, with nut.  (For support SH992D (4).)',note='%(sh)R',qty='4',price='.02 P')
entry(r,'BOLT, carriage, ⅜″ x 1½″, with nut and plain washer.  (For block SH396D (1);\n  block SH396C (1).)',note='%(sh)R',qty='2',price='.02 P')
bolt(r,'connecting forked end rod','(24)','.21',note='&',ident='12550',plate='18')
component(r,'*one LQ125A connecting forked end rod BOLT (24)',mfr='12550',price='.17')
component(r,'one LQ126A connecting forked end rod bolt NUT,');cotter(r,'1/16″ x ½″')
bolt(r,'connecting plain end rod','(12)','.25',ident='13422',plate='18')
component(r,'*one LQ133A connecting plain end rod BOLT (12)',mfr='13422',price='.20')
component(r,'one LQ134A connecting plain end rod bolt NUT,');cotter(r,'3/32″ x ¾″')
bolt(r,'crank case upper to lower','(50)','.14')
component(r,'*one LQ243A crank case upper to lower BOLT (50)',price='.05')
component(r,'one LQ244A crank case upper to lower bolt NUT,')

r=start(23)
component(r,'two LQ113A WASHER, special, ¼″.)')
for desc,qty,price,part,mfr,cp,kw in [('long','(2)','.29','LQ246A','B165','.20',dict(ident='165',plate='15')),('short','(2)','.59','LQ245A','B187','.50',{})]:
 bolt(r,'crank case upper to lower, '+desc,qty,price,**kw)
 component(r,f'*one {part} crank case upper to lower BOLT, {desc} (2)',mfr=mfr,price=cp)
 component(r,'one LQ198A NUT, special, ⅜″,');cotter(r,'3/32″ x ⅝″',False)
 component(r,'two LQ166A WASHER, special, ⅜″.)')
bolt(r,'crank shaft gear','(6)','.06',note='&')
component(r,'*one LQ262A BOLT, special (6)',mfr='B6270',price='.03')
component(r,'one LQ51A NUT, special, S. A. E., 5/16″,');cotter(r,'1/16″ x ⅝″')
bolt(r,'foot brake bridle','(1)','1.32')
component(r,'*one M767 foot brake bridle BOLT (1)',ord='217',price='1.25')
component(r,'one M768 NUT, special, ⅞″,');cotter(r,'3/16″ x 1½″')
entry(r,'BOLT, generator drive shaft end housing binding',note='%X',mfr='D29848',qty='4',price='1.13 P')
bolt(r,'high and low speed control lever','(2)','.85')
component(r,'*one M776 high and low speed control lever BOLT (2)',ord='224',price='.78')
component(r,'one M768 NUT, special, ⅞″,')
component(r,'one —      PIN, split, 3/16″ x 1″.')
entry(r,'                    For high and low speed control lever, left (1); right (1).)')
bolt(r,'ignition switch and voltage regulator binding','(2)','.19 P',mfr='D30369')
component(r,'*one D30369 ignition switch and voltage regulator binding BOLT (2)',price='.15')
component(r,'one D30360 ignition switch and voltage regulator binding bolt NUT,')
component(r,'one D30385 ignition switch and voltage regulator binding bolt retaining\n                         WASHER,')
component(r,'one D20495 WASHER, lock, .195″ x .393″ x .046″.)')

r=start(24)
bolt(r,'large planet pinion ring','(6)','$0.54',note='&',ident='15',plate='22')
component(r,'*one M318 large planet pinion ring BOLT (6)',ord='679',price='.48')
component(r,'one —      NUT, castle, S. A. E., ⅞″,');cotter(r,'⅛″ x 1¾″')
for desc,qty,price,part,mfr,cp in [('long','(14)','1.90','LQ189A','8033','1.70'),('short','(2)','1.80','LQ190A','105','1.60')]:
 bolt(r,'lower crank case bearing, '+desc,qty,price,note='&')
 component(r,f'*one {part} lower crank case bearing BOLT, {desc} {qty}',mfr=mfr,price=cp)
 component(r,'two LQ192A lower crank case bearing bolt NUT,')
 component(r,'two —      PIN, split, 3/32″ x ⅞″,')
 component(r,'one LQ471A WASHER, special, I. D. 33/64″, O. D. 15/16″, 1/16″ thick,')
 component(r,'one LQ191A WASHER, special, I. D. 33/64″, O. D. 1 1/16″, ⅛″ thick.)')
bolt(r,'main turret flap ring','(2)','.40')
component(r,'one M2391 main turret flap RING,')
component(r,'*one M2392 main turret flap ring BOLT (2).)',ord='423',price='.28')
bolt(r,'oil pump upper half body','(4)','.10')
component(r,'*one LQ443A oil pump upper half body BOLT (S. A. E., hexagon, ¼″ x\n                         15/16″ (4)',ident='—',plate='33',mfr='B118',price='.05')
component(r,'one LQ89A NUT, special, S. A. E., ¼″,');cotter(r,'1/16″ x ½″',False)
component(r,'two LQ113A WASHER, special, ¼″.)')

# Extra clearance surrounding the two stacked identification numbers on p18.
for record in TABLES[18]:
 if record["item"]=="BEARING, transmission vertical shifter shaft":
  record.update(space_before=0.5,space_after=0.5)
