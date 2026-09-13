"""Native nomenclature columns, stacked fractions, captions, and signatures."""
from pathlib import Path
import json,re
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch10.json').read_text())
PLATES={186:[('111',210,50),('112',1495,134)],187:[('113',154,270)],193:[('114',447,270)],195:[('115',174,278),('116',1608,270)],197:[('117',405,270),('118.',1350,260)]}
CAPTIONS={186:[('COMPOUND CLUTCH',1378),('TOP OF ROAD TRACK',2218)],193:[('REGULATING TANK ASSEMBLY',2008)],195:[('AIR-PRESSURE PUMP',1567),('JOCKEY PULLEY',2421)],197:[('MUFFLER',983),('GASOLINE TANK',1947)]}

def vertical(x,y0,y1):
 b.serial+=1;obj=s.createLine(x,y0,x,y1,f'p{s.currentPage():03}-column-rule-{b.serial}');s.setLineWidth(.3,obj);s.setLineColor('Black',obj)

def cell(text,x,y,width,size=6.3):
 """Keep special source fractions as native numerator, bar, denominator."""
 matches=list(re.finditer(r'\d+/\d+',text))
 if not matches:return b.txt(text,x,y,width,size)
 segments=[];last=0;fw=4.8
 for m in matches:
  segments.append(('text',text[last:m.start()]));segments.append(('fraction',m.group()));last=m.end()
 segments.append(('text',text[last:]))
 natural=sum(b.advance(t,size,'Roman') if kind=='text' else fw for kind,t in segments)
 f=min(1,(width-1.3)/natural);cur=x
 for kind,t in segments:
  if kind=='text':
   advance=b.advance(t,size,'Roman')*f
   if t.strip():b.txt(t,cur,y,advance+1.3,size,scale=f*100)
   cur+=advance
  else:
   num,den=t.split('/');w=fw*f
   b.txt(num,cur,y-2.5,w,3.1,align=1,scale=f*100);b.rule(cur+.25,y-2.3,w-.5,.22)
   b.txt(den,cur,y+.1,w,3.1,align=1,scale=f*100);cur+=w

def nomenclature(n):
 t=D[str(n)];secs=t['sections'];left=50;rule1=98;rule2=129;dx=133;dw=213
 if n==184:
  b.center(t['title'],17+t['title_baseline']*.225,8.2,'Bold')
  b.center('PROPERTY CLASSIFICATION, PART I, CLASS 4, SECTION II',79.8,8.0,'Bold')
  top=91;bottom=118.0
 else:
  b.center(t['title'],17+t['title_baseline']*.225,6.8)
  top=17+t['title_baseline']*.225+7;bottom=top+28
 y=(top+bottom)/2+2
 b.txt('Part No.',left,y,rule1-left,6.7,align=1)
 for j,word in enumerate(['Number','per','machine']):b.txt(word,rule1+2,y-7+j*6,rule2-rule1-4,6.5,align=1)
 b.txt('Description and Location' if n==198 else 'Description and location',dx,y,dw,6.7,align=1)
 b.rule(left,top,296,.3);b.rule(left,bottom,296,.3)
 last=max(r['lines'][-1]['baseline'] for sec in secs for r in sec['rows']);end=17+last*.225+2
 vertical(rule1,top,end);vertical(rule2,top,end)
 for sec in secs:
  for h in sec['headings']:b.txt(h['text'],dx,17+h['baseline']*.225,dw,h['size'],align=1)
  grouped=[]
  for r in sec['rows']:
   y=17+r['lines'][0]['baseline']*.225
   if r['part']:
    b.txt(r['part'],left,y,rule1-left-2,6.3)
    start=left+b.advance(r['part'],6.3,'Roman')*b.frames[-1]['scale']/100+1.2
    if start<rule1-2:b.rule(start,y-1.2,rule1-2-start,.2,True)
   if r.get('split_quantities'):
    for k,q in enumerate(r['split_quantities']):b.txt(q,rule1+3,y-2.9+5.8*k,rule2-rule1-5,5.7,align=2)
    b.txt('{',rule1+.5,y+1.2,5,12);b.txt('}',rule2-3,y+1.2,5,12)
   elif r['quantity']:b.txt(r['quantity'],rule1+3,y,rule2-rule1-6,6.3,align=2)
   if r.get('part_group'):grouped.append(y)
   for j,line in enumerate(r['lines']):cell(line['text'],dx+(5 if j else 0),17+line['baseline']*.225,dw-(5 if j else 0))
   if n==196 and r['part']=='12243':
    start=dx+b.advance(r['lines'][0]['text'],6.3,'Roman')+1.5
    if start<346:b.rule(start,y-1.2,346-start,.2,True)
  if grouped:
   gy=sum(grouped)/len(grouped);b.txt('No numbers',left,gy,rule1-left-2,6.3)
   b.txt('{',rule1+1,gy+3,8,18)

def extra(n):
 if str(n) in D:nomenclature(n)
 for num,y,x in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if n==187:
  obj=b.txt('CONTROL SYSTEM',57,293,90,6.1,align=1)
  s.rotateObjectAbs(270,obj)
 if n==193:b.txt('38285—25†——13',73,17+2059*.225,120,8.3)
