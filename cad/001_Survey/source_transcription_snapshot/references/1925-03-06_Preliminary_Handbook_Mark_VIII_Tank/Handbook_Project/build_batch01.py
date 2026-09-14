#!/usr/bin/env python3
"""Run with Scribus 1.6.x: Script > Execute Script. Rebuild overwrites outputs.
Native text frames retain individual source lines, and tables use editable cells.
"""
from pathlib import Path
import json,sys,os,traceback,math,hashlib
import scribus as s
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from data.front_matter import TOC,PLATES,SPECS
W,H=396.,612. # 5.5 x 8.5 in working canvas; physical trim is unconfirmed.
SX=.225;YOFF=17.;TEXT_W=296.
metrics=json.loads((ROOT/'fonts/metrics.json').read_text());styles={};frames=[];fits=[];serial=0

def advance(text,size,font):return sum(metrics[font].get(c,.5) for c in text)*size

def txt(text,x,y,width,size=9.7,font='Roman',align=0,scale=100,name=None):
 global serial
 serial+=1;name=name or f'p{s.currentPage():03}-text-{serial:04}'
 natural=advance(text,size,font)
 if natural*scale/100>width-1.2:
  scale=min(scale,(width-1.2)/max(natural,.1)*100)
 scale=round(scale,2);key=(size,font,align,scale)
 if key not in styles:
  sty='Style '+str(len(styles)+1);leading=size*1.25
  s.createCharStyle(name=sty+' character',font='C059 '+font,fontsize=size,fillcolor='Black',language='en_US',scaleh=scale/100)
  s.createParagraphStyle(name=sty,charstyle=sty+' character',linespacingmode=0,linespacing=leading,alignment=align,gapbefore=0,gapafter=0)
  styles[key]=sty
 leading=size*1.25
 s.createText(x,y-leading,width,leading+size*.65+3,name);s.setText(text,name);s.setParagraphStyle(styles[key],name)
 s.setTextDistances(0,0,0,0,name);s.setFirstLineOffset(s.FLOP_LINESPACING,name);s.setTextFlowMode(name,0)
 s.layoutText(name)
 attempts=0
 while (s.textOverflows(name) or s.getTextLines(name)!=1) and attempts<8:
  scale*=.96;s.setTextScalingH(scale,name);s.layoutText(name);attempts+=1
 frames.append(dict(name=name,page=s.currentPage(),text=text,baseline=y,scale=scale))
 if scale<85:fits.append(dict(name=name,scale=scale,text=text))
 return name

def center(t,y,size=9,font='Roman'):return txt(t,40,y,316,size,font,1)
def rule(x,y,w,weight=.35,dashed=False):
 global serial
 serial+=1;n=s.createLine(x,y,x+w,y,f'p{s.currentPage():03}-rule-{serial}');s.setLineWidth(weight,n);s.setLineColor('Black',n)
 if dashed:s.setLineStyle(2,n)
def folio(n):
 if n in (1,2):return
 if n in (3,5):center(f'({n})',586,8.3)
 elif n==9:center('(9)',503,8.3)
 else:center(str(n),22,10)
def leaderrow(t,ref,y,size=7.6,x=45,width=306,num=None):
 if num is not None:txt(str(num)+'.',x,y,17,size,align=2);x+=20;width-=20
 refw=22;end=x+width-refw-5
 natural=advance(t,size,'Roman');usable=end-x-3
 scale=min(100,usable/max(natural,.1)*100)
 txt(t,x,y,max(usable,1),size,scale=scale)
 start=x+natural*scale/100+2
 # Discrete native dashes, so leaders do not become OCR-like text noise.
 if start+1.5<end:rule(start,y-1.8,end-start,.25,True)
 txt(ref,end+5,y,refw,size,align=2)
def art(name):
 a=next(r for r in ASSETS if r['name']==name);box=a['crop'];p=a['page']
 cx={1:725,8:880,10:905,12:890,13:823,14:880,16:865,17:809,18:889,19:807,20:905}[p]
 x=198+(box[0]-cx)*SX;y=YOFF+box[1]*SX;w=a['output_size'][0]*SX;h=a['output_size'][1]*SX
 n=s.createImage(x,y,w,h,f'p{p:03}-{name}');s.loadImage(str(ROOT/'assets'/f'{name}.png'),n);s.setScaleImageToFrame(True,True,n);s.setTextFlowMode(n,0)
 return n

def front(n):
 if n==1:
  for x,y,w in [(29,25,338),(29,566,338)]:rule(x,y,w,.65)
  for x in [29,367]:
   a=s.createLine(x,25,x,566);s.setLineColor('Black',a);s.setLineWidth(.65,a)
  center('No. 1977',52,11,'Bold');rule(181,60,34)
  center('PRELIMINARY HANDBOOK',99,14,'Bold');center('OF THE',125,10,'Bold')
  center('MARK VIII TANK',169,25,'Bold')
  rule(181,211,34);center('143 PLATES, ONE INSERT',228,10,'Italic');rule(181,240,34)
  center('NOVEMBER 15, 1918',282,9,'Bold');center('REPRINTED MARCH 6, 1925',296,9,'Bold')
  # Seal uses its original pixel aspect ratio, independently placed on title leaf.
  a=next(a for a in ASSETS if a['name']=='seal');w=78;h=w*a['output_size'][1]/a['output_size'][0]
  obj=s.createImage((W-w)/2,354,w,h,'p001-seal');s.loadImage(str(ROOT/'assets/seal.png'),obj);s.setScaleImageToFrame(True,True,obj)
  center('WASHINGTON',532,7.2,'Bold');center('GOVERNMENT PRINTING OFFICE',543,6.8,'Bold');center('1925',554,7,'Bold')
 elif n==2:
  txt('War Department,',183,241,150,10.5,align=1)
  txt('Office of the Chief of Ordnance,',132,253,206,10.1,align=1)
  txt('Washington, November 15, 1918.',172,265,174,10.1,'Italic',2)
  txt('This manual is published for the information and government of the',50,277,297,10.1,align=4,scale=94)
  txt('United States Army.',40,289,305,10.1,scale=94)
  txt('By order of the Secretary of War:',50,301,285,10.1)
  txt('C. C. Williams,',222,313,125,10.1,align=1)
  txt('Major General, Chief of Ordnance,',158,325,189,10.1,'Italic',2)
  txt('United States Army.',225,337,122,10.1,'Italic',2)
  center('(2)',346,8)
 elif n in TOC:
  if n==3:center('TABLE OF CONTENTS',36,12,'Bold');rule(174,46,48)
  y=61 if n==3 else 46;step=7.6 if n==3 else 8.1
  for roman,heading,rows in TOC[n]:
   center('Chapter '+roman,y,9);y+=11;center(heading,y,7.1,'Bold');y+=10
   for t,ref in rows:leaderrow(t,ref,y,7.6 if n==3 else 8);y+=step
   y+=10
  if n==4:center('Nomenclature List',y+3,9);center('(For contents see Nomenclature Index, page 240)',y+16,8.5)
 elif n in (5,6,7):
  limits={5:(1,56),6:(57,104),7:(105,143)};lo,hi=limits[n]
  steps={5:7.6,6:8.4,7:8.8};step=steps[n];size={5:7.4,6:7.9,7:8.2}[n]
  heads={1:'Chapter I',27:'Chapter II',35:'Chapter III',71:'Chapter IV',73:'Chapter V',82:'Chapter VI',84:'Chapter VII',92:'Chapter VIII',105:'Chapter IX',107:'Chapter X',110:'Chapter XI',111:'Nomenclature List'}
  if n==5:
   center('LIST OF PLATES',34,12,'Bold');rule(174,44,48);center('Chapter I',58,9);y=79
   txt('Plate',45,69,50,6.8);txt('Page',326,69,26,6.8,align=2)
   leaderrow('Insert.—Sectional view through 35-ton tank','Insert',y,size);y+=step
  else:
   y=49
   if n==7:center('Chapter IX',40,9);y=57
   txt('Plate',45,y-10,50,6.8);txt('Page',326,y-10,26,6.8,align=2)
  for num,t,ref in PLATES:
   if not lo<=num<=hi:continue
   if num in heads and num not in (1,105):center(heads[num],y+8,9);y+=24
   parts=t.split('/')
   if len(parts)>1:
    txt(str(num)+'.',45,y,17,size,align=2);txt(parts[0],65,y,264,size);y+=step
    leaderrow(parts[1],ref,y,size,x=73,width=278)
   else:leaderrow(t,ref,y,size,num=num)
   y+=step
 elif n==9:
  center('HANDBOOK OF THE MARK VIII TANK',62,12,'Bold');rule(173,74,50)
  center('CHAPTER I',95,11);center('GENERAL DESCRIPTION AND INSTRUCTIONS',114,8.8,'Bold')
  center('Table of weights and outline specifications',133,8.5,'Italic')
  y=150
  for row in SPECS.splitlines():
   t,ref=row.split('|');indent=12 if t.startswith(' ') else 0;t=t.strip();x=43+indent
   w=194-indent
   txt(t,x,y,w,8.25)
   if ref:
    start=x+advance(t,8.25,'Roman')+1;end=245
    if start+1.5<end:rule(start,y-1.8,end-start,.25,True)
    txt(ref,251,y,104,8.25)
   y+=9.75
  txt('38285—25†——2',62,503,102,7.5)

def body(n):
 rows=BODY[str(n)];norm=[r for r in rows if not r['heading']]
 left=sorted(r['box'][0] for r in norm if r['box'][0]>80)[max(0,len([r for r in norm if r['box'][0]>80])//4)]
 right=left+1315
 for r in rows:
  t=r['text'];x0,y0,x1,y1=r['box'];baseline=r.get('baseline',r.get('baseline_override',y1-7));y=YOFF+baseline*SX
  if r['heading']:
   size=8.9 if (n==11 and r['source_line_index']==14) else 8.1 if t in ('BRIEF OPERATING INSTRUCTIONS','LUBRICATING INSTRUCTIONS') else 6.5
   center(t,y,size,'Bold' if size>7 else 'Roman');continue
  indent=10 if 28<x0-left<95 else 0
  if t.startswith(('The exterior portion','Before running')):indent=10
  if n==13 and r['source_line_index'] in (13,15):indent=0
  width=TEXT_W-indent
  full=(x1>=right-70 or len(t)>64)
  if n==18 and r['source_line_index']==5:full=False
  txt(t,50+indent,y,width,9.7,align=4 if full else 0,scale=92.5)

def legends(n):
 if n==12:
  center('TOWING GEAR',YOFF+1187*SX,6.3)
  rows=[['Ref.','Ref.'],['No.     Name','No.     Name'],['1   Towing bracket.','3   Deflector plate.'],['2   Stern guide for haulage rope.','4   Rear strut unditching gear.']];y=295
 elif n==13:
  center('TOP OF MACHINE',YOFF+1975*SX,6.3)
  rows=[['Ref.','Ref.'],['No.     Name','No.     Name'],['1   Roof towing bracket.','3   Exhaust pipes.'],['2   Inlet louver.','4   Filler pipe for water-cooling system.']];y=473
 else:return
 for a,b in rows:txt(a,50,y,145,5.8);txt(b,204,y,144,5.8);y+=6.4

def pressure_table():
 center('Ground pressures',48,7.3,'Italic')
 x=127;top=59;cw=29;bottom=153
 heads=['Sub-\nmersion','Length of\ncontact','Area of\nground\ncontact\nin square\nfeet','Pressure\nin tons\nper\nsquare\nfoot','Pressure,\npounds\nper\nsquare\ninch']
 for j,t in enumerate(heads):
  parts=t.split('\n');y=61+(5-len(parts))*3.2
  for z in parts:txt(z,x+j*cw,y,cw,6.5,align=1);y+=6.4
 for j in range(6):
  o=s.createLine(x+j*cw,54,x+j*cw,bottom);s.setLineWidth(.25,o);s.setLineColor('Black',o)
 rule(x,98,cw*5,.25);rule(x,bottom,cw*5,.25)
 txt('Inches',x,109,cw,6.4,'Italic',1);txt('Inches',x+cw,109,cw,6.4,'Italic',1)
 vals=[['1','109','40.118','0.997','13.85'],['2','190','70','.5714','7.944'],['3','221','81.34','.4918','6.83'],['5','277','101.95','.3923','5.45'],['10','324','119.25','.335','4.66'],['15','350','130.49','.307','4.26']]
 for i,row in enumerate(vals):
  for j,t in enumerate(row):txt(t,x+j*cw,116+i*6.6,cw-3,6.8,align=2)

def main():
 global ASSETS,BODY
 (ROOT/'build-error.txt').unlink(missing_ok=True)
 (ROOT/'build-status.txt').unlink(missing_ok=True)
 available={r[0]:Path(r[5]) for r in s.getXFontNames()}
 for suffix in ['Roman','Bold','Italic']:
  actual=available.get('C059 '+suffix);bundled=ROOT/'fonts'/('C059-'+suffix+'.otf')
  if actual is None or hashlib.sha256(actual.read_bytes()).digest()!=hashlib.sha256(bundled.read_bytes()).digest():
   raise RuntimeError('Use the bundled C059 OpenType fonts; disable conflicting Type 1 copies in Scribus font preferences.')
 ASSETS=json.loads((ROOT/'data/assets.json').read_text());BODY=json.loads((ROOT/'data/body.json').read_text())
 s.newDocument((W,H),(40,40,22,25),s.PORTRAIT,1,s.UNIT_POINTS,s.PAGE_1,0,1)
 s.setInfo('Ordnance Department; digital reconstruction','Preliminary Handbook of the Mark VIII Tank — pilot pages 1–20','1918 handbook, reprinted March 6, 1925. Review draft. 5.5 x 8.5 inch provisional canvas; C059 font approximation. See README.md.')
 s.setRedraw(False)
 for n in range(1,21):
  if n>1:s.newPage(-1)
  s.gotoPage(n);folio(n)
  if n in [1,2,3,4,5,6,7,9]:front(n)
  if str(n) in BODY:body(n)
  for a in ASSETS:
   if a['page']==n and a['name']!='seal':art(a['name'])
  if n in [8,10]:
   txt('Plate No. '+str(1 if n==8 else 2),50,41,110,8.8)
   caption='RIGHT SIDE VIEW OF 35-TON TANK, MARK VIII' if n==8 else 'SECTIONAL VIEW THROUGH THE 35-TON TANK, MARK VIII'
   o=txt(caption,0,12,280,6.8,align=1);s.rotateObject(90,o);s.moveObjectAbs(318,421,o)
  if n in [12,13,14,16,17,18,19,20]:
   platepos={12:[(3,45)],13:[(4,228)],14:[(5,39)],16:[(6,37)],17:[(7,350)],18:[(8,90)],19:[(9,50)],20:[(10,45),(11,285)]}
   for num,y in platepos[n]:txt('Plate No. '+str(num),267,y,80,8.2,align=2)
  legends(n)
  captions={14:[('THREE-QUARTER FRONT VIEW OF MARK VIII MACHINE',799)],16:[('DRIVER’S SEAT AND CONTROLS, ALSO SHOWING AMMUNITION STORAGE',1320)],18:[],19:[('UPPER ROAD TRACK ROLLER',1305)],20:[('EPICYCLIC OILER',880),('EPICUCLIC CUP',2250)]}
  for cap,y in captions.get(n,[]):center(cap,YOFF+y*SX,6.1)
  if n==11:pressure_table()
  print('Built page',n,flush=True)
 validation=[]
 for f in frames:
  s.layoutText(f['name']);validation.append({**f,'overflow':bool(s.textOverflows(f['name'])),'line_count':s.getTextLines(f['name'])})
 errors=[f for f in validation if f['overflow'] or f['line_count']!=1]
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(pages=s.pageCount(),frames=validation,errors=errors,compressed_below_85_percent=fits),ensure_ascii=False,indent=2))
 s.gotoPage(1);s.saveDocAs(str(ROOT/'Handbook_Pilot_001-020_v1.sla'))
 if errors:raise RuntimeError('Text layout errors: '+repr(errors[:4]))
 pdf=s.PDFfile();pdf.file=str(ROOT/'Handbook_Pilot_001-020_v1.pdf');pdf.pages=list(range(1,21));pdf.version=15
 pdf.fonts=[];pdf.subsetList=['C059 Roman','C059 Bold','C059 Italic'];pdf.compress=1;pdf.quality=0;pdf.resolution=300;pdf.downsample=0;pdf.save()
 (ROOT/'build-status.txt').write_text(f'PASS: 20 pages; {len(frames)} native text frames; no overflow; one line in every text frame.\n')
 s.setRedraw(True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'build-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
