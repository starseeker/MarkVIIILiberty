"""Native nomenclature columns, stacked fractions, captions, and signatures."""
from pathlib import Path
import json,re
import scribus as s
import layout_helpers as b
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/tables_batch12.json').read_text())
PLATES={222: [('131', 628, 50)], 224: [('132', 262, 51)], 226: [('133', 465, 49)], 228: [('134', 644, 34)], 230: [('135', 572, 48)], 232: [('136', 150, 39), ('137', 874, 37), ('138', 1763, 36)], 234: [('139', 198, 112), ('140', 1252, 129)], 236: [('141', 143, 96)], 238: [('142', 146, 128), ('143', 1306, 125)]}
CAPTIONS={222: [('GASOLINE TANK INSTALLATION', 1879)], 224: [('ROLLER SPROCKET AND ROAD TRACK DRIVING WHEEL', 2086)], 226: [('HIGH-SPEED BRAKE', 2122)], 228: [('LOW-SPEED BRAKE', 1858)], 230: [('TRACK BRAKE', 1738)], 232: [('THREE TYPES OF TRACK ROLLERS', 2518)], 234: [('WATER PUMP', 1136), ('COMBINATION TAP', 2238)], 238: [('PROPER WAY TO LIFT ENGINE', 1269), ('PROPER WAY TO LIFT ENGINE', 2460)]}

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
 if not text:return
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
   if r.get('part_group_codes'):
    for k,code in enumerate(r['part_group_codes']):
     py=y+(k-.5)*r['group_half_span_px']*2*.225
     b.txt(code,left,py,rule1-left-5,6.3)
     start=left+b.advance(code,6.3,'Roman')+1.2
     if start<rule1-5:b.rule(start,py-1.2,rule1-5-start,.2,True)
    right_brace(rule1-4,y-6,y+3)
   if r['part']:
    b.txt(r['part'],left,y,rule1-left-2,6.3)
    start=left+b.advance(r['part'],6.3,'Roman')*b.frames[-1]['scale']/100+1.2
    if start<rule1-2:b.rule(start,y-1.2,rule1-2-start,.2,True)
   if n==233 and r['part'] in ['M-858','M-874']:b.rule(rule1+1,y-1.2,rule2-rule1-3,.2,True)
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

 if n==239:b.rule(left,end+4,296,.3)
 for block in t.get('shared_blocks',[]):
  for j,line in enumerate(block['lines']):cell(line,block['x'],17+(block['baseline']+j*block['step'])*.225,block['width'])
  brace(block['brace_x'],17+block['brace_top']*.225,17+block['brace_bottom']*.225)

def extra(n):
 if str(n) in D:nomenclature(n)
 for num,y,x in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2)
 for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
 if n==236:
  x=198+(1405-945)*.225-6.1;cy=17+(1080+1447)/2*.225
  obj=b.txt('FUEL-SUPPLY SYSTEM',x,cy+48+6.1*1.25,96,6.1,align=1);s.rotateObjectAbs(90,obj)
 if n==225:b.txt('38285—25†——15',72,17+2505*.225,120,8.3)
 if n==240:nomenclature_index()

def right_brace(x,top,bottom):
 mid=(top+bottom)/2;h=bottom-top
 pts=[(x,top),(x+1.2,top+.025*h),(x+1.6,top+.1*h),(x+1.6,mid-.12*h),(x+2,mid),(x+1.6,mid+.12*h),(x+1.6,bottom-.1*h),(x+1.2,bottom-.025*h),(x,bottom)]
 for (xa,ya),(xb,yb) in zip(pts,pts[1:]):
  b.serial+=1;o=s.createLine(xa,ya,xb,yb,f'p{s.currentPage():03}-part-brace-{b.serial}');s.setLineWidth(.3,o);s.setLineColor('Black',o)

INDEX=[('A',291,[('Ammunition storage',184)]),('C',400,[('Carburetor',184),('Chain casing',185),('Clutch assembly',185),('Clutch shaft',188),('Control rods',188),('Control rods, engine',189),('Control units, center',189),('Control units, front',189),('Control units, rear',190),('Cooling system',191),('Cooling system, engine',191),('Cooling system, radiator',191)]),('D',965,[('Driving sprocket chain',192)]),('E',1075,[('Engine, cam-shaft housing',192),('Engine, cam-shaft lower shaft',196),('Engine, crank case',196),('Engine, crank shaft',199),('Engine, connecting rod',199),('Engine, cylinder',199),('Engine, electrical equipment',200),('Engine, flywheel',201),('Engine, generator drive shaft',201),('Engine, governor',201),('Engine, oilpump',203),('Engine, piston',203),('Engine, supports',205),('Engine, hand starter',205),('Epicyclic gear',205),('Exhaust system',209)]),('F',1811,[('Fan, bevel box',209),('Fan, large air ducts',211),('Fan, ventilating',211)]),('G',2008,[('Gasoline system, air pump',211),('Gasoline system, pressure-regulating tank',213),('Gasoline system, tanks',213),('Gun pedestal, 6-pounder',215)]),('H',2243,[('Hull, door',215),('Hull, floor',217)])]
def nomenclature_index():
 b.center('NOMENCLATURE INDEX',17+158*.225,10,'Bold');b.rule(174,17+218*.225,48,.35)
 b.txt('Page',325,17+291*.225,23,7.3,align=2)
 for letter,y,entries in INDEX:
  b.center(letter,17+y*.225,8.5)
  for j,(text,ref) in enumerate(entries):b.leaderrow(text,str(ref),17+(y+40+j*42)*.225,size=9.0,x=50,width=298)
 b.center('(240)',17+2373*.225,8.3)
