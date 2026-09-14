"""Native captions, parts legend, specification tables and printer signatures."""
import json
from pathlib import Path
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch09.json').read_text())
PLATES={161:[('105',567,278)],162:[('106',795,50)],163:[('107',668,278)],172:[('108',590,50)],173:[('109',803,218)],178:[('110.',177,50)]}
CAPTIONS={161:[('WIRING OF LIGHTING, STARTING, AND IGNITION',1837)],162:[('STARTER PINION SHIFT',1515)],163:[('THIRD BRUSH REGULATION',1725)],172:[('SIX-POUNDER GUN SHOWING ALSO AMMUNITION STORAGE',1821)],173:[('AMMUNITION STORAGE BOX',1660)],178:[('LAYOUT OF VENTILATING SYSTEM',2230)]}

def legend():
 rows=D['legends']['162'];base=374.9;step=5.8;size=6.2
 for col,rr in enumerate([rows[:10],rows[10:]]):
  x=50+col*153
  b.txt('Ref. No.',x,base-6.7,33,size);b.txt('Name.',x+37,base-6.7,106,size)
  for j,(ref,name) in enumerate(rr):
   y=base+j*step;b.txt(ref,x,y,23,size,align=1);b.txt(name,x+37,y,108,size)
 obj=s.createLine(198.5,base-12,198.5,base+9*step+2);s.setLineWidth(.3,obj);s.setLineColor('Black',obj)

def specifications(n):
 y=56 if n==171 else 58.6
 b.center('Chapter X' if n==171 else 'Chapter XI',y,9)
 b.center('AMMUNITION AND ARMAMENT' if n==171 else 'MISCELLANEOUS FITTINGS AND EQUIPMENT',y+17,10,'Bold')
 b.center('OUTLINE SPECIFICATIONS' if n==171 else 'Ventilating system specifications',y+36,8.2,'Roman' if n==171 else 'Italic')
 y0=110 if n==171 else 107.5;valuex=284 if n==171 else 222;size=7.6
 for j,(label,value) in enumerate(D['specifications'][str(n)]):
  y=y0+9.4*j;end=valuex-6
  b.txt(label,50,y,end-51,size)
  scale=b.frames[-1]['scale']/100;start=50+b.advance(label,size,'Roman')*scale+2
  if start<end:b.rule(start,y-1.8,end-start,.25,True)
  if n==176 and j==6:
   prefix='1 foot 9';b.txt(prefix,valuex,y,35,size);fx=valuex+b.advance(prefix,size,'Roman')+1;fw=7.2
   b.txt('5',fx,y-3.9,fw,4.8,align=1);b.rule(fx+.4,y-2.7,fw-.8,.25);b.txt('16',fx,y+1.7,fw,4.8,align=1)
   b.txt('inches.',fx+fw+2,y,346-fx-fw-2,size)
  else:b.txt(value,valuex,y,346-valuex,size)

def extra(n):
 for num,y,x in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if n==162:legend()
 if n in [171,176]:specifications(n)
 if n in [161,169]:b.txt('38285—25†——'+('11' if n==161 else '12'),73,17+(2326 if n==161 else 2321)*.225,120,8.3)
