"""Native captions, parts legends and specifications for printed pages 121–140."""
import json
from pathlib import Path
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch07.json').read_text())
PLATES={121:[('73',96,278)],123:[('74',228,278),('75',1300,50)],124:[('76',290,50),('77',1383,50)],125:[('78',443,278)],126:[('79',850,50)],128:[('80',588,50)],129:[('81',164,230)],131:[('82',187,278)],133:[('83',529,278)],137:[('84',693,278)],138:[('85',679,50)],139:[('86',369,278)],140:[('87',156,50),('88',1602,50)]}
CAPTIONS={122:[('EPICYCLIC TRANSMISSION',515)],123:[('HIGH-SPEED FORWARD',1150),('HIGH-SPEED REVERSE',2236)],124:[('LOW-SPEED FORWARD',1185),('LOW-SPEED REVERSE',2290)],125:[('EPICYCLIC DRIVE',1615)],126:[('EXTERIOR VIEW EPICYCLIC TRANSMISSION',1588),('DRIVING-MEMBER SPECIFICATIONS',2171)],128:[('EPICYCLIC PLANETARY RING',1922)],131:[('ROLLER PINION AND TRACK DRIVE',1996)],133:[('ROAD TRACK DRIVING WHEEL',1777)],137:[('ROAD-TRACK LINK',1577)],138:[('TOP TRACK RAIL UPON WHICH TRACK SLIDES. TRACK SHOWN BROKEN',1886)],139:[('ROAD-TRACK DRIVING WHEEL',1890)],140:[('ROAD-TRACK ADJUSTING WHEEL',899),('TOP ROAD-TRACK ROLLER',2274)]}

def vertical_rule(x,y,h):
 obj=s.createLine(x,y,x,y+h);s.setLineWidth(.3,obj);s.setLineColor('Black',obj)

def legend(n):
 rows=D['legends'][str(n)];split={122:35,125:12,126:6,131:8,133:7,137:2,139:7,140:7,'140b':3}[n]
 base={122:159,125:409,126:534,131:493,133:439,137:396,139:468,140:245,'140b':554}[n]
 step=5.7;size=5.8
 heights=[]
 for col,rr in enumerate([rows[:split],rows[split:]]):
  x=50+col*153;partx=0 if n==133 else 17;namex=38 if n==133 else 50;namew=146-namex
  headers=[('Part',partx,base-11.4,35),('No.',partx,base-5.7,35),('Specifications' if n==126 else 'Name',namex,base-5.7,namew)]
  if n!=133:headers=[('Ref.',0,base-11.4,16),('letter' if n==126 else 'No.',0,base-5.7,16)]+headers
  for t,dx,y,w in headers:b.txt(t,x+dx,y,w,size,align=1)
  j=0
  for ref,part,name in rr:
   y=base+step*j
   if ref:b.txt(ref,x,y,16,size,align=1)
   if part:b.txt(part,x+partx,y,namex-partx-2,size)
   for k,line in enumerate(name.split('~')):b.txt(line,x+namex+(4 if k else 0),y+step*k,namew-(4 if k else 0),size)
   j+=len(name.split('~'))
  heights.append(j)
 vertical_rule(198.5,base-15,(max(heights)-1)*step+18)

def specifications(n):
 y=66 if n==130 else 69.5
 b.center('Chapter VI' if n==130 else 'Chapter VII',y,9)
 b.center('CHAIN DRIVE' if n==130 else 'ROAD TRACK AND TRACK DRIVE',y+16.5,10,'Bold')
 b.center('Outline specifications',y+33,8.2,'Italic')
 y0=y+46;valuex=257 if n==130 else 273
 for j,(label,value) in enumerate(D['specifications'][str(n)]):
  y=y0+9.0*j;size=8.0;end=valuex-6
  obj=b.txt(label,50,y,end-51,size)
  scale=b.frames[-1]['scale']/100
  start=50+b.advance(label,size,'Roman')*scale+2
  if start<end:b.rule(start,y-1.8,end-start,.25,True)
  b.txt(value,valuex,y,346-valuex,size)

def extra(n):
 for num,y,x in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if str(n) in D['legends']:legend(n)
 if n==140:legend('140b')
 if n in [130,136]:specifications(n)
 if n==129:
  lines=['PROGRESS OF DRIVE THROUGH THE VARIOUS PROPELLING UNITS OF THE 35-TON TANK, MARK VIII. THE DRIVE PASSES FROM THE CLUTCH','TO THE BEVEL GEARS, THEN TO THE EPICYCLIC TRANSMISSION, FROM WHICH IT PASSES TO THE TRACK BY MEANS OF THE CHAIN,','ROLLER SPROCKET, AND ROAD TRACK DRIVING WHEEL.']
  for i,t in enumerate(lines):
   o=b.txt(t,0,12,505,6.1,align=0);s.rotateObject(90,o);s.moveObjectAbs(296+7*i,565,o)
  b.txt('38285—25†——9',53,568.25,100,7.5)
 if n==137:b.txt('38285—25†——10',72,553.4,102,7.5)
