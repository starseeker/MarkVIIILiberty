"""Editable captions, legends and tables for printed pages 101–120."""
import json
from pathlib import Path
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch06.json').read_text())
PLATES={108:[('66',626,50)],111:[('67',122,202)],112:[('68',313,59),('69',1361,104)],114:[('70',691,50)],116:[('71',453,50)],117:[('72',634,269)]}
CAPTIONS={108:[('TEST LAMPS AND CONNECTIONS',1784)],112:[('SECTION THROUGH GOVERNOR',1154),('MUFFLER',2045)],114:[('FAN BEVEL BOX',1549)],116:[('COMPOUND CLUTCH',1642)],117:[('PATTERN OF CLUTCH',1625)]}

def vertical_rule(x,y,h):
 obj=s.createLine(x,y,x,y+h);s.setLineWidth(.3,obj);s.setLineColor('Black',obj)

def legend(n):
 rows=D['legends'][str(n)]
 if n==111:
  # The source legend and caption run down the page beside the rotated drawing.
  def cell(t,u,v,w,align=0):
   o=b.txt(t,0,12,w,5.8,align=align);s.rotateObject(270,o);s.moveObjectAbs(117-v,154+u,o)
  for col,start in [(0,0),(1,3)]:
   u0=col*149
   for t,u,v,w in [('Ref.',0,0,16),('No.',0,5.7,16),('Part',18,0,30),('No.',18,5.7,30),('Name',52,5.7,94)]:cell(t,u0+u,v,w,1)
   for j,(ref,part,name) in enumerate(rows[start:start+3]):
    v=12+5.7*j;cell(ref,u0,v,16,1);cell(part,u0+18,v,30);cell(name,u0+50,v,96)
  b.rule(94,300,29,.3)
  o=b.txt('SECTION OF GOVERNOR AND LINKAGE',0,12,300,6.1,align=1);s.rotateObject(270,o);s.moveObjectAbs(127,154,o)
  return
 split={112:3,114:7,116:14}[n];base={112:501,114:389,116:411}[n]
 # Source legend headers are two lines, followed by one editable cell per column.
 for col,rr in enumerate([rows[:split],rows[split:]]):
  x=50+col*153
  for t,dx,y,w in [('Ref.',0,base-11.4,16),('No.',0,base-5.7,16),('Part',17,base-11.4,30),('No.',17,base-5.7,30),('Name' if n!=112 or col==0 else 'Name.',50,base-5.7,94)]:b.txt(t,x+dx,y,w,5.8,align=1)
  for j,(ref,part,name) in enumerate(rr):
   y=base+5.7*j
   if ref:b.txt(ref,x,y,16,5.8,align=1)
   if part:b.txt(part,x+18,y,30,5.8)
   if name:b.txt(name,x+50,y,96,5.8)
 vertical_rule(198.5,base-15,(max(split,len(rows)-split)-1)*5.7+18)

def specifications(n):
 if n==115:
  b.center('Chapter IV',59,9);b.center('COMPOUND CLUTCH',72,10,'Bold');b.center('Outline specifications',84.5,8.2,'Italic')
  y0=95.5;valuex=280
 else:
  b.center('Chapter V',65,9);b.center('EPICYCLIC TRANSMISSION',81,10,'Bold');b.center('General specifications',94,8.2,'Italic')
  y0=107;valuex=307
 for j,(label,value) in enumerate(D['specifications'][str(n)]):
  y=y0+9.5*j;size=8.2;end=valuex-6;w=end-50-1
  b.txt(label,50,y,w,size)
  start=50+b.advance(label,size,'Roman')+2
  if start<end:b.rule(start,y-1.8,end-start,.25,True)
  b.txt(value,valuex,y,348-valuex,size)

def clearances():
 b.center('Summary of clearances',49,8.2,'Italic')
 x=50;col1=220;col2=249;col3=278;right=346
 b.rule(x,58,right-x,.35);b.rule(x,82,right-x,.25)
 for t,c in [('Mini-',col1),('Maxi-',col2)]:b.txt(t,c,69,29,6.2,align=1);b.txt('mum',c,75,29,6.2,align=1)
 b.txt('Desired',col3,72,68,6.2,align=1)
 for j,(label,indent,src,minv,maxv,desired) in enumerate(D['clearances']):
  y=94+j*5.625
  if label:
   lx=x+indent*10.5;b.txt(label,lx,y,col1-lx-3,6.2)
   if minv:
    start=lx+b.advance(label,6.2,'Roman')+2
    if start<col1-2:b.rule(start,y-1.2,col1-2-start,.22,True)
  if minv:b.txt(minv,col1,y,29,6.0,align=1)
  if maxv:b.txt(maxv,col2,y,29,6.0,align=1)
  if desired:b.txt(desired,col3+3+(5 if not label else 0),y,65-(5 if not label else 0),6.0)
 bottom=94+(len(D['clearances'])-1)*5.625+7
 for cx in [col1,col2,col3]:vertical_rule(cx,58,bottom-58)
 b.rule(x,bottom,right-x,.35)

def extra(n):
 for num,y,x in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if str(n) in D['legends']:legend(n)
 if n==113:clearances()
 if n in [115,119]:specifications(n)
 if n==105:b.txt('38285—25†——8',72,562,102,7.5)
