"""Source transcription for the four supplied parts-table pages.

Cell order: note, identification, plate, manufacturer, British, Ordnance,
description (explicit source line breaks), quantity, price.
Uncertain details are recorded separately in review.json.
"""
def row(note='',ident='',plate='',mfr='',brit='',ord='',item='',qty='',price=''):
    return dict(note=note,ident=ident,plate=plate,mfr=mfr,brit=brit,ord=ord,item=item,qty=qty,price=price)

TABLES={2:[],3:[],6:[],7:[]}
r=TABLES[2]
r.extend([
row(note='X',ord='B101910A',item='ADAPTER, ½″-14 pipe thread, with ½″-14 male pipe thread end.  (For tube\n  SH981A (2); tube SH981B (2); tube SH981C (2); tube SH984A (2); tube SH984B\n  (2); tube SH984C (2); tube SH984D (2).)',qty='14',price='$0.40 P'),
row(note='X',ord='B101972A',item='ADAPTER, ½″-24 S. A. E., with ⅛″-27 male pipe thread end.  (For tube C8012\n  (1); tube C8013 (1); tube C8015 (1); tube C8016 (1).)',qty='6',price='.09 P'),
row(note='X',ord='B101972B',item='ADAPTER, 9/16″-24 S. A. E., with ¼″-18 male pipe thread end.  (For tube SH981E\n  (2); tube SH981F (2); tube SH981G (2); tube C8011 (2); tube SH984E (2); tube\n  SH984F (2).)',qty='18',price='.25 P'),
row(note='X',brit='T–A12–6',item='ADAPTER, ⅞″-18 U. S. F. and 1″-16 U. S. F. male thread (Titeflex type).  (For\n  tube SH207A (2); tube SH207B (2).)',qty='4',price='.55 P'),
row(brit='A16309',item='ADAPTER, elbow, 7/16″-22-NPS with ⅛″-27-NPT (brass).  (For tubes B101982A,\n  B, C, D, and E (1).)',qty='6',price='.12 P'),
row(note='X',item='AMMETER, (Delco type)',qty='1',price='5.00'),
row(note='(gy) X',ord='994',item='AMMETER (Bijur Co. type)',qty='1',price='5.00'),
])
for b,o,t,p in [
('M2023B','367','back plate connecting, front, left','1.60'),
('M2023A','367','back plate connecting, front, right','1.60'),
('M2022B','367','back plate connecting, rear, left','1.80'),
('M2022A','367','back plate connecting, rear, right','1.80'),
('M2024','307','back plate to cover connecting','4.75'),
('M2025','307','back plate to floor connecting','3.35'),
('M2107B','328','bottom sloping plate, bottom, left','1.35'),
('M2107A','328','bottom sloping plate, bottom, right','1.35'),
('M2105B','328','bottom sloping and side vertical plate, left','.75'),
('M2105A','328','bottom sloping and side vertical plate, right','.75'),
('M2141B','354','bulkhead, side, left','4.75'),
('M2141A','354','bulkhead, side, right','4.75'),
('M2142A','354','bulkhead plate vertical stiffening, left','4.75'),
('M2142B','354','bulkhead plate vertical stiffening, right','4.75'),
('M1896','535','bulkhead to roof behind bulkhead connecting','2.95'),
('M1895','535','bulkhead to roof connecting','6.30')]:
 r.append(row(note='*',brit=b,ord=o,item='ANGLE, '+t,qty='(1)',price=p))

r=TABLES[3]
for b,o,t,q,p,n in [
('M2031','333','chain casing bracket, left','(2)','.95','*'),
('M2032','333','chain casing bracket, right','(2)','.95','*'),
('M2415B','421','driver’s turret side bottom, left','(1)','3.50','*'),
('M2415A','421','driver’s turret side bottom, right','(1)','3.50','*'),
('','SH978C','(engine) oil tank supporting','1','1.25','&'),
('M1943','518','engine room back plate to floor connecting','(1)','7.85','*'),
('M1942A','518','floor, front (at bulkhead)','(1)','7.85','*'),
('M1942B','518','floor rear (at bulkhead)','(1)','7.85','*'),
('M1592','231','drive chain casing hull back plate','2','1.79',''),
('M2419B','416','driver’s turret vertical, left','(1)','.92','*'),
('M2419A','416','driver’s turret vertical, right','(1)','.92','*'),
('M2026B','307','floor plate to hull connecting, left','(1)','3.50','*'),
('M2026A','307','floor plate to hull connecting, right','(1)','3.50','*'),
('M2040B','341','front diaphragm, left','(1)','1.05','*'),
('M2040A','341','front diaphragm, right','(1)','1.05','*'),
('M1921B','530','front mud chute, side, left','(1)','1.70','*'),
('M1921A','530','front mud chute, side, right','(1)','1.70','*'),
('M2060B','341','front mud chute back plate, left','(1)','1.50','*'),
('M2060A','341','front mud chute back plate, right','(1)','1.50','*'),
('M2063B','341','front mud chute bottom plate, left','(1)','1.50','*'),
('M2063A','341','front mud chute bottom plate, right','(1)','1.50','*'),
('M2061B','332','front mud chute side plate, left','(2)','1.90','*'),
('M2062B','332','front mud chute side plate, left','(1)','1.63','*'),
('M2061A','332','front mud chute side plate, right','(2)','1.90','*'),
('M2062A','332','front mud chute side plate, right','(1)','1.63','*'),
('M1950','519','front sloping plate to floor','(1)','7.50','*'),
('M1893B','535','front sloping plate to roof plate connecting, left','(1)','2.75','*'),
('M1893A','535','front sloping plate to roof plate connecting, right','(1)','2.75','*'),
('M1999B','306','front wing, left (outer left or inner right)','2','8.65',''),
('M1999A','306','front wing, right (outer right or inner left)','2','8.65',''),
('M2007B','321','longitudinal side, left','(1)','22.60','*'),
('M2008B','312','longitudinal side, lower, left','(1)','22.60','*'),
('M2008A','312','longitudinal side, lower, right','(1)','22.60','*'),
('M2007A','321','longitudinal side, right','(1)','22.60','*'),
('M2417','416','main turret front center plate, top','(1)','1.53','*'),
('M2418B','417','main turret front wing plate, top, left','(1)','.59','*'),
('M2418A','417','main turret front wing plate, top, right','(1)','.59','*'),
('M2408','421','main turret left side, top','(1)','3.79','*'),
('M2381','422','main turret rear bottom','(1)','2.85','*')]:
 r.append(row(note=n,brit=b,ord=o,item=('ANFLE, ' if b=='M2418B' else 'ANGLE, ')+t,qty=q,price=p))

r=TABLES[6]
for b,o,t,q,p,n,plate in [
('M2792B','488','sponson splash, back, left','1','3.92','%X',''),
('M2792A','488','sponson splash, back, right','1','3.92','%X',''),
('','SH485B','sponson splash (bottom edge of gun shield)','2','2.58','%X',''),
('M2791B','483','sponson splash, front, left','1','1.49','%X','7'),
('M2791A','483','sponson splash, front, right','1','1.49','%X','7'),
('M2790B','476','sponson splash, left (at hinge)','1','3.60','%X',''),
('M2790A','476','sponson splash, right (at hinge)','1','3.60','%X',''),
('M785','220','spring anchor','1','1.32','&',''),
('M2101B','339','top bottom and side sloping plate, left','(1)','2.98','*',''),
('M2101A','339','top bottom and side sloping plate, right','(1)','2.98','*',''),
('M2104B','328','top sloping plate and side vertical plate, left','(1)','.90','*',''),
('M2104A','328','top sloping plate and side vertical plate, right','(1)','.90','*',''),
('M2106B','328','top sloping plate, top, left','(1)','1.70','*',''),
('M2106A','328','top sloping plate, top, right','(1)','1.70','*',''),
('M2027B','377','top to hull connecting, left','(1)','3.98','*',''),
('M2027A','377','top to hull connecting, right','(1)','3.98','*',''),
('M2005A','322','track, bottom, left (inner left or outer right)','2','45.25','','7'),
('M2005B','322','track, bottom, right (outer left or inner right)','2','45.25','','7'),
('M2004B','306','track, rear, left','2','7.50','',''),
('M2004A','306','track, rear, right','2','7.50','',''),
('M2020B','320','track, top, left','(1)','35.00','*',''),
('M2020A','320','track, top, right','(1)','35.00','*',''),
('M2118','378','unditching gear, side, left','1','14.00','',''),
('M2119','378','unditching gear, side, right','1','14.00','',''),
('M3789B','510','6-pdr. gun pedestal back plate, left','(1)','2.97','*',''),
('M3795B','270','6-pdr. gun pedestal back plate, left, length 16⅜″','(1)','.98','*',''),
('M3790B','270','6-pdr. gun pedestal back plate, left, length 18⅜″','(1)','.98','*',''),
('M3789A','510','6-pdr. gun pedestal back plate, right','(1)','2.97','*',''),
('M3795A','270','6-pdr. gun pedestal back plate, right, length 16⅜″','(1)','.98','*',''),
('M3790A','270','6-pdr. gun pedestal back plate, right, length 18⅜″','(1)','.98','*','')]:
 r.append(row(note=n,plate=plate,brit=b,ord=o,item='ANGLE, '+t,qty=q,price=p))

r=TABLES[7]
for b,o,t,p in [
('M3791B','508','6-pdr. gun pedestal, corner, left','1.14'),
('M3791A','508','6-pdr. gun pedestal, corner, right','1.14'),
('M3794B','511','6-pdr. gun pedestal front plate, left (lower)','1.72'),
('M3794A','511','6-pdr. gun pedestal front plate, right (lower)','1.72'),
('M3793','270','6-pdr. gun pedestal front plate, left (upper)','1.78'),
('M3792','270','6-pdr. gun pedestal front plate, right (upper)','1.78'),
('M3796B','508','6-pdr. gun pedestal side plate, left','.90'),
('M3799B','511','6-pdr. gun pedestal side plate, left','.60'),
('M3797B','511','6-pdr. gun pedestal side plate, left','.98'),
('M3796A','508','6-pdr. gun pedestal side plate, right','.90'),
('M3799A','511','6-pdr. gun pedestal side plate, right','.60'),
('M3797A','511','6-pdr. gun pedestal side plate, right','.98'),
('M3800','508','6-pdr. gun pedestal top plate, left','4.32'),
('M3788','508','6-pdr. gun pedestal top plate, right','4.32')]:
 r.append(row(note='*',brit=b,ord=o,item='ANGLE, '+t,qty='(1)',price=p))
r.extend([
row(note='X',ord='SH523A',item='ANGLE, 24″ fan supporting (radiator cooling fan)',qty='1',price='1.35'),
row(note='(b)&',mfr='D13779',item='ARM, distributor contact (curved), assembly',qty='(2)',price='.78 P'),
row(note='(b)&',mfr='D13737',item='ARM, distributor contact, assembly',qty='(4)',price='.78 P'),
row(note='&',mfr='D13829',item='ARM, generator brush, assembly',qty='(4)',price='.12 P'),
row(item='     (Composed of:'),
row(item='          *one D29821 generator brush ARM (4)',price='.04 P'),
row(item='          *one D30386 generator brush arm CLIP (4)',price='.03 P'),
row(item='          *one D29820 generator brush arm HUB (4)',price='.03 P'),
row(item='           two D23298 RIVET, button head, brass, .078″ x .144″.)'),
row(note='&',ord='SH142E',item='ARM, governor',qty='1',price='2.29'),
row(note='(b)&',mfr='D30056',item='ARM, ignition switch handle contact, left (lower) assembly',qty='(2)',price='.02 P'),
row(note='(b)&',mfr='D30053',item='ARM, ignition switch handle contact, left (upper) assembly',qty='(2)',price='.02 P'),
row(note='(b)&',mfr='D30054',item='ARM, ignition switch handle contact, right, assembly',qty='(2)',price='.02 P'),
row(note='%X',ord='SH234H',item='ARM, jockey pulley',qty='2',price='.90'),
row(note='%X',item='ARM, semaphore, assembly',qty='(2)',price='3.92'),
row(item='     (Composed of:'),
row(item='           one X259 semaphore ARM,'),
row(ord='803',item='          *one X260 semaphore arm DISK',price='1.40'),
row(item='           four — RIVET, countersunk head, 3/16″ x 9/16″.)'),
row(note='%X',brit='X259',ord='803',item='ARM, semaphore',qty='2',price='2.48'),
row(note='&',plate='12',ord='SH966C',item='ARM, throttle control rocker, long',qty='1',price='.75'),
row(note='&',plate='12',ord='SH966B',item='ARM, throttle control rocker, short',qty='1',price='.65'),
row(note='&',mfr='D13754',item='ARMATURE, generator',qty='1',price='11.40 P'),
])
