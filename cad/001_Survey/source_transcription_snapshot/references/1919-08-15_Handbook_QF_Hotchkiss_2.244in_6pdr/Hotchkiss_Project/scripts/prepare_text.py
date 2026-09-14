"""Build reviewed line data from retained IA OCR; corrections are source readings."""
from pathlib import Path
from xml.etree import ElementTree as E
import json,re,shutil,statistics
ROOT=Path(__file__).resolve().parents[1]
pages=E.parse(ROOT/'sources/primary_djvu.xml').findall('.//OBJECT')
D=[]
for pi,p in enumerate(pages):
 ls=[]
 for j,l in enumerate(p.findall('.//LINE')):
  ws=l.findall('WORD');bs=[list(map(int,w.get('coords').split(','))) for w in ws]
  if not bs:continue
  ls.append(dict(index=j,text=' '.join(w.text or '' for w in ws).strip(),baseline=statistics.median(b[1] for b in bs),box=[min(b[0] for b in bs),min(b[3] for b in bs),max(b[2] for b in bs),max(b[1] for b in bs)]))
 D.append(dict(leaf=pi+1,size=[int(p.get('width')),int(p.get('height'))],lines=ls))
C={}
def fix(p,i,t):C[f'{p}:{i}']=t
# Printed page 7 (primary leaf 6).
fix(6,14,'(a) The gun is of British design and manufacture. The body')
fix(6,19,'(b) The recoil band is screwed on the exterior of the jacket just')
fix(6,21,'lugs for attaching to the recoil and counter-recoil mechanisms, re-')
fix(6,26,'locking ring being screwed and shrunk on both the tube and jacket')
fix(6,28,'(d) Two feathers are formed on the jacket, one on the top, the')
fix(6,34,'(f) A line locating the center of gravity (without mechanism)')
# Printed page 8.
fix(7,8,'(b) Breech recess.—The recess in the rear end of the jacket, called')
fix(7,15,'face of the breech recess, have their bearing, or guiding, faces par-')
fix(7,17,'(c) Breechblock.—The breechblock is a square hollowed steel')
fix(7,25,'cartridge when loading at high angles. By the movement of the')
fix(7,28,'(d) Breechblock plate.—That part of the front face of the breech-')
# Printed page 9.
fix(8,3,'(f) Crank-handle latch.—A latch is fitted to the outside of the')
fix(8,15,'is in the same vertical plane as the cocking cam on the crank handle')
fix(8,17,'cam of the crank handle meets the cocking toe of the rocking shaft,')
fix(8,21,'(h) Sear.—The hammer is held at full cock by means of a sear')
fix(8,22,'actuated by a spring, both being mounted in the bottom of the breech-')
fix(8,23,'block. A toe on the sear catches in a cock notch on the hammer')
fix(8,25,'(i) Firing arm and shaft.—The firing arm is keyed to the right')
fix(8,28,'firing position. The firing arm and shaft are retained in position')
fix(8,37,'(j) Main spring.—The main spring is a flat double-branched')
fix(8,40,'on one side of the axis and the other end in a stirrup on the other')
fix(8,42,'ing in a transverse slot cut into the shaft.')
fix(8,43,'(k) Extractor.—The extractor is a single piece of steel working')
# Printed page 10.
fix(9,4,'(l) Block-stop screw.—When the breechblock is thrown into the')
fix(9,6,'by the block-stop screw, which is screwed through the left cheek')
fix(9,11,'(b) After firing.—The breech is opened by pulling the crank han-')
fix(9,13,'stud is carried backward in the part of its groove which is concen-')
for i,t in enumerate('''tuated by its stud traveling in the vertical portion of extractor
groove CC in the block, at first moves slowly backward with a
powerful leverage, starting the cartridge case from its seat. The
motion of the extractor during this portion of its functioning is
caused by the rearward travel of the breechblock due to the inclina-
tion of its guides. This first movement, the loosening of the case,
is referred to as “primary extraction.” When the block has de-
scended so far as to unmask the bore the sharp change in direction
of the extractor groove in the block causes the extractor to take a
quick violent motion to the rear, throwing the cartridge case entirely
out of the gun and clear of the breech. This latter movement is
referred to as “final extraction.” At the end of this motion the
block is stopped in its descent by the block-stop screw meeting the
blind end of its groove in the block.'''.splitlines(),18):fix(9,i,t)
fix(9,32,'(c) Loading and closing the breech.—The cartridge having been')
fix(9,35,'reverse movement of the crank handle. As the breechblock rises')
# Printed page 11.
fix(10,3,'(d) Ready.—Firing.—When the breech is closed the cocking cam')
fix(10,9,'(e) Note.—Care should be taken to see that the crank is properly')
fix(10,13,'(f) Safety.—It is impossible to fire the gun before the breech is')
fix(10,21,'(g) The drill hook, Plate III, is designed to lengthen the stirrup,')
fix(10,23,'mechanism from strain when snapping the gun at drill. When the')
# Printed page 12.
fix(11,1,'(b) Main spring and hammer.—Insert the point of the screw')
fix(11,10,'(c) Sear.—With the point of the screw driver back out the sear')
fix(11,12,'(d) Crank.—Take out the set screw in the hub of the crank han-')
fix(11,14,'(e) Extractor.—Withdraw the extractor from its groove.')
fix(11,16,'(f) The mechanism is assembled in the reverse order. To facili-')
# Printed page 13.
fix(12,12,'(b) The breech and firing mechanisms should be dismounted from')
fix(12,17,'(c) The spare parts should be well coated with vaseline or heavy')
fix(12,20,'(d) Jammed cartridge.—If, in loading, a cartridge jams and so')
fix(12,24,'(e) Nonextraction.—If for any reason the cartridge case or car-')
fix(12,26,'pull it out.')
fix(12,27,'(f) Broken extractor.—If the hook of the extractor breaks, back')
fix(12,31,'cartridge already in the gun, as the hook will come on the wrong')
fix(12,33,'(g) Misfires—Hangfires.—“Misfires” and “hangfires” are of')
fix(12,39,'(h) Chamber disfigured.—If, after firing, the cartridge case')
fix(12,41,'chamber; careless loading may cause the hard point of the shell to')
fix(12,43,'exists, it must be filed off smooth.')
# Printed page 14.
fix(13,11,'(b) The principal parts of the mounting are:')
fix(13,17,'Counter-recoil mechanism.')
fix(13,25,'the upper surface receives the pivot. A projecting flange is provided')
fix(13,30,'plate and the revolving bracket together, while permitting the lat-')
fix(13,37,'receive the pivot which supports the whole system. The pivot can')
# Printed page 15.
fix(14,15,'(g) The hydraulic recoil cylinder is formed in the metal of the')
fix(14,16,'cradle itself. Its front end is closed by a gun-metal plug which is')
fix(14,18,'joint. On the inner face of the plug a chamber is formed to receive a')
fix(14,19,'projection on the front face of the piston. Internally the cylinder has')
fix(14,21,'the other on recoil and counter-recoil. Working in the cylinder is')
fix(14,24,'is formed on the front face of the piston which fits the recess in the')
fix(14,28,'the top of the rear end of the cylinder and is closed by a steel plug')
fix(14,29,'and leather washer.')
fix(14,30,'(h) For filling of recoil cylinder, see page 19.')
fix(14,32,'(i) The counter-recoil mechanism consists of two strong spiral')
fix(14,39,'counter-recoil lug on the underside of the recoil band. The rear')
# Printed page 16.
fix(15,1,'(j) Action of recoil and counter-recoil mechanism.—On firing, the')
fix(15,2,'gun recoils axially through the cradle, taking with it the piston')
fix(15,3,'rod and the counter-recoil spring rods. The oil in the recoil cylin-')
fix(15,4,'der passes from rear to front of the piston through the grooves,')
fix(15,5,'thus setting up a hydraulic resistance which absorbs the recoil energy,')
fix(15,7,'(k) As the counter-recoil rods are drawn back the springs are')
fix(15,8,'compressed against the cylinder-closing plugs, and when recoil has')
fix(15,10,'(l) During the last movement of counter-recoil, the projection')
fix(15,11,'on the recoil piston reenters its recess in the closing plug, and in')
fix(15,12,'displacing the oil gathered there acts as a hydraulic cushion to')
fix(15,14,'SHOULDER PIECE.')
fix(15,18,'(n) The shoulder piece is a steel bar fitted with a rubber pad')
fix(15,24,'from the recoiling gun.')
fix(15,25,'9. FIRING GEAR.')
fix(15,34,'SHIELDS.')
fix(15,35,'(b) A bullet-proof outer shield is fitted to the mounting. It is')
# Printed page 17.
fix(16,11,'chine is within 1½ calibers of the axis of the projectile, i. e., 3⅜')
fix(16,21,'the necessary fittings to allow for elevation and deflection of the')
fix(16,22,'telescope.')
fix(16,23,'(b) The rear holder is supported on a deflection screw which in')
# Printed page 18.
fix(17,0,'18 HANDBOOK FOR HOTCHKISS GUN.')
fix(17,4,'the chart about 25 yards from the gun on some convenient pole, wall,')
fix(17,22,'(c) The open sights are now tested on the extreme upper left-hand')
fix(17,26,'(d) Note.—The bore should be occasionally checked to see that the')
fix(17,34,'(f) Note.—With the chart method, the axis of the bore and the')
fix(17,38,'(a) Hydraulic recoil cylinder.—Before firing, it must be seen that')
# Printed page 19.
fix(18,1,'(b) To fill the recoil cylinder.—Fully depress the gun, remove the')
fix(18,5,'(c) To empty the recoil cylinder.—Depress the gun. Unscrew')
fix(18,8,'(d) Leakage of gland.—Should it be found that there is leakage')
fix(18,13,'(e) If it is found that leakage is taking place over the leather')
fix(18,16,'(f) Counter-recoil springs.—The counter-recoil rods must be')
fix(18,20,'(g) The whole of the working parts must be kept thoroughly')
fix(18,37,'(b) Place clip ring in position, see that keys on bracket take key-')
fix(18,38,'ways in ring, then secure with two bolts.')
fix(18,41,'(d) Assemble cradle. Screw stuffing box into rear end of recoil')
# Printed page 20.
fix(19,2,'end-plate on end of spring, place heads on counter-recoil spring rods,')
fix(19,4,'der, the screwed end of rod passing through plug. Screw nut on')
fix(19,5,'rod and compress spring until the nut comes up against shoulder')
fix(19,7,'(f) Place cradle in revolving bracket bearings, fit trunnion caps')
fix(19,9,'(g) Place shoulder piece with guard and firing gear assembled')
fix(19,12,'(h) Place elevating clamp screw with handle downward.')
fix(19,13,'(i) Place traversing clamp screw with handle upward.')
fix(19,17,'bracket.')
fix(19,18,'(l) Place gun and secure to piston rod and counter-recoil springs.')
fix(19,19,'(m) Place gun at extreme depression, fill recoil cylinder, and')
fix(19,25,'(b) Remove clip ring. (This must be done, as otherwise the')
fix(19,28,'(c) Remove nut from piston rod and nuts on counter-recoil rods.')
# Printed page 21.
fix(20,5,'(b) To enable this to be done, the gun has to be drawn back from')
fix(20,7,'(c) The guard should be detached by removing the securing bolts.')
for p in D:
 for l in p['lines']:
  key=f"{p['leaf']}:{l['index']}"
  if key in C:l['ocr_original']=l['text'];l['text']=C[key]
(ROOT/'data/lines.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
(ROOT/'data/corrections.json').write_text(json.dumps(C,ensure_ascii=False,indent=2))
print('prepared',len(D),'source pages;',len(C),'line corrections')
