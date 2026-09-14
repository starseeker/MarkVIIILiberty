"""Native plate captions, legends and specification tables for pages 141–160."""
import json
from pathlib import Path
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch08.json').read_text())
PLATES={143:[('89',799,278)],144:[('90',866,50)],145:[('91',368,278)],147:[('92',132,278)],149:[('93',707,278)],150:[('94',713,50)],151:[('95',589,278)],152:[('96',144,134),('97',1250,50)],153:[('98',178,278),('99',1230,278)],155:[('100',214,278)],156:[('101',412,50)],157:[('102',512,278)],158:[('103',828,126)],159:[('104',560,278)]}
CAPTIONS={143:[('LOWER ROAD-TRACK ROLLER WITH SPRING',1587)],144:[('ROAD TRACK WHEEL',1484)],145:[('LOWER TRACK ROLLLER WITHOUT SPRING',1226)],149:[('POSITIONS OF SPEED LEVER',1687)],150:[('POSITIONS OF REVERSING LEVER',1748)],151:[('BRAKE ADJUSTMENT',1785)],152:[('SPARK OR THROTTLE LEVER',1163),('LOW GEAR BRAKE LINING',2322)],153:[('TRACK BRAKE LINING',1064),('HIGH SPEED BRAKE LINING',2237)],155:[('HIGH-SPEED BRAKE',1880)],156:[('TRACK BRAKE',1586)],157:[('ARRANGEMENT OF LOW-GEAR BRAKE',1737)],158:[('BULKHEAD WITH INSTRUMENT BOARD REMOVED',2009)],159:[('CONTROL ROD ENDS WITH EPICYCLIC TRANSMISSION REMOVED FROM HULL',1845)]}

def vertical_rule(x,y,h):
 obj=s.createLine(x,y,x,y+h);s.setLineWidth(.3,obj);s.setLineColor('Black',obj)

def legend(n):
 rows=D['legends'][str(n)];split={143:4,144:4,145:4,155:8,156:4,157:6}[n]
 base={143:398,144:378,145:317,155:463,156:399,157:432}[n];step=5.7;size=5.8
 for col,rr in enumerate([rows[:split],rows[split:]]):
  x=50+col*153
  for t,dx,y,w in [('Ref.',0,base-11.4,16),('No.',0,base-5.7,16),('Part',17,base-11.4,32),('No.',17,base-5.7,32),('Name',50,base-5.7,96)]:b.txt(t,x+dx,y,w,size,align=1)
  for j,(ref,part,name) in enumerate(rr):
   y=base+step*j;b.txt(ref,x,y,16,size,align=1);b.txt(part,x+17,y,31,size);b.txt(name,x+50,y,96,size)
 vertical_rule(198.5,base-15,(max(split,len(rows)-split)-1)*step+18)

def specifications(n):
 y=68 if n==146 else 65.5
 b.center('Chapter VIII' if n==146 else 'Chapter IX',y,9)
 b.center('CONTROL SYSTEM' if n==146 else 'ELECTRICAL EQUIPMENT',y+16.5,10,'Bold')
 b.center('Outline specifications',y+33,8.2,'Italic')
 y0=y+46;valuex=251 if n==146 else 277
 for j,(label,value) in enumerate(D['specifications'][str(n)]):
  y=y0+9.4*j;size=8.0;end=valuex-6
  b.txt(label,50,y,end-51,size)
  scale=b.frames[-1]['scale']/100;start=50+b.advance(label,size,'Roman')*scale+2
  if start<end:b.rule(start,y-1.8,end-start,.25,True)
  b.txt(value,valuex,y,346-valuex,size)

def extra(n):
 for num,y,x in PLATES.get(n,[]):b.txt(('[' if n==157 else '')+'Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if str(n) in D['legends']:legend(n)
 if n in [146,160]:specifications(n)
 if n==147:
  o=b.txt('LAYOUT OF THE CONTROL SYSTEM SHOWING LINKAGE AND LEVERS',0,12,264,6.1,align=1);s.rotateObject(270,o);s.moveObjectAbs(50,179,o)
 if n==158:
  for j,(label,value) in enumerate(D['reductions']):
   y=17+(513+42*j)*.225;b.txt(label,75,y,198,8.2);start=75+b.advance(label,8.2,'Roman')+2
   b.rule(start,y-1.8,285-start,.25,True);b.txt(value,293,y,48,8.2)
