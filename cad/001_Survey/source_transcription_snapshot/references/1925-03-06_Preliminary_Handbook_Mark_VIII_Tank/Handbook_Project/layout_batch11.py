"""Native nomenclature columns, stacked fractions, captions, and signatures."""
from pathlib import Path
import json,re
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch11.json').read_text())
PLATES={202:[('119',461,61)],204:[('120',149,50),('121',1068,50)],206:[('122',573,60)],208:[('123',63,50)],210:[('124',343,50),('125',1385,50)],214:[('127',570,50)],216:[('128',737,59)],218:[('129',116,80)],220:[('130',185,60)]}
CAPTIONS={202:[('ROAD TRACK DRIVING WHEEL',2008)],204:[('ROAD TRACK ADJUSTING WHEEL',939),('ARRANGEMENT OF EPICYCLIC BEVEL DRIVE',2326)],206:[('EPICYCLIC TRAIN',1884)],210:[('FAN BEVEL BOX',1167),('ROAD TRACK DRIVING WHEEL SECTION',2085)],212:[('CHARACTERISTIC SPEED AND GOVERNOR CURVES OF ENGINE IN 35-TON TANK',2337),('MARK VIII',2362)],214:[('OIL TANK',1950)],216:[('UPPER PART OF HULL',1854)],220:[('SPONSON ROLLED BACK FOR SHIPPING PURPOSES',2260)]}

def brace(x,top,bottom):
 """A slim native vector brace; no font substitution or raster text."""
 mid=(top+bottom)/2;h=bottom-top
 pts=[(x+2,top),(x+.8,top+.025*h),(x+.4,top+.10*h),(x+.4,mid-.12*h),(x,mid),(x+.4,mid+.12*h),(x+.4,bottom-.10*h),(x+.8,bottom-.025*h),(x+2,bottom)]
 for (xa,ya),(xb,yb) in zip(pts,pts[1:]):
  b.serial+=1;obj=s.createLine(xa,ya,xb,yb,f'p{s.currentPage():03}-brace-{b.serial}');s.setLineWidth(.3,obj);s.setLineColor('Black',obj)

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
 b.center(t['title'],17+t['title_baseline']*.225,6.8)
 top=17+t['title_baseline']*.225+7;bottom=top+28
 y=(top+bottom)/2+2
 b.txt('Part No.',left,y,rule1-left,6.7,align=1)
 for j,word in enumerate(['Number','per','Machine' if n==219 else 'machine']):b.txt(word,rule1+2,y-7+j*6,rule2-rule1-4,6.5,align=1)
 b.txt('Description and Location' if n==219 else 'Description and location',dx,y,dw,6.7,align=1)
 b.rule(left,top,296,.3);b.rule(left,bottom,296,.3)
 last=max(r['lines'][-1]['baseline'] for sec in secs for r in sec['rows']);end=17+last*.225+2
 vertical(rule1,top,end);vertical(rule2,top,end)
 for sec in secs:
  for h in sec['headings']:b.txt(h['text'],dx,17+h['baseline']*.225,dw,h['size'],align=1)
  grouped=[]
  for r in sec['rows']:
   y=17+(sum(l['baseline'] for l in r['lines'])/len(r['lines']) if r.get('description_brace') else r['lines'][0]['baseline'])*.225
   if r['part']:
    b.txt(r['part'],left,y,rule1-left-2,6.3)
    start=left+b.advance(r['part'],6.3,'Roman')*b.frames[-1]['scale']/100+1.2
    if start<rule1-2:b.rule(start,y-1.2,rule1-2-start,.2,True)
   if r.get('split_quantities'):
    for k,q in enumerate(r['split_quantities']):b.txt(q,rule1+3,y-2.9+5.8*k,rule2-rule1-5,5.7,align=2)
    b.txt('{',rule1+.5,y+1.2,5,12);b.txt('}',rule2-3,y+1.2,5,12)
   elif r['quantity']:b.txt(r['quantity'],rule1+3,y,rule2-rule1-6,6.3,align=2)
   if r.get('part_group'):grouped.append(y)
   for j,line in enumerate(r['lines']):
    indent=line.get('indent',5 if j or r.get('description_brace') else 0)
    width=r['short_width'] if 'short_width' in r and j==0 else line.get('width',dw-indent)
    ly=17+line['baseline']*.225
    cell(line['text'],dx+indent,ly,width)
    if r.get('description_leader'):
     start=dx+b.advance(line['text'],6.3,'Roman')+1
     if start<dx+width:b.rule(start,ly-1.2,dx+width-start,.2,True)
   if r.get('description_brace'):brace(dx,17+r['lines'][0]['baseline']*.225-5,17+r['lines'][-1]['baseline']*.225+1)
  if grouped:
   gy=sum(grouped)/len(grouped);b.txt('No numbers',left,gy,rule1-left-2,6.3)
   b.txt('{',rule1+1,gy+3,8,18)

 for block in t.get('shared_blocks',[]):
  for j,line in enumerate(block['lines']):cell(line,block['x'],17+(block['baseline']+j*block['step'])*.225,block['width'])
  brace(block['brace_x'],17+block['brace_top']*.225,17+block['brace_bottom']*.225)

def extra(n):
 if str(n) in D:nomenclature(n)
 for num,y,x in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if n in [208,218]:
  text='EPICYCLIC DRIVE' if n==208 else 'HULL PLATING'
  x=198+((1614 if n==208 else 1560)-(880 if n==208 else 942))*.225-6.1
  cy=17+((1126+1423)/2 if n==208 else (1129+1378)/2)*.225
  obj=b.txt(text,x,cy+45+6.1*1.25,90,6.1,align=1)
  s.rotateObjectAbs(90,obj)
 if n==201:b.txt('38285—25†——14',72,17+2505*.225,120,8.3)
