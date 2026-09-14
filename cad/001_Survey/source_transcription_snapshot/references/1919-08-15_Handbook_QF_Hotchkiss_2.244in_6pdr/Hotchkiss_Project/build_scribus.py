"""Run in Scribus 1.6.x via Script > Execute Script. Rebuilds versioned master.
The JSON data are authoritative; save manual layout edits under another name.
"""
import scribus as s
from pathlib import Path
import json,os,re,traceback
from xml.etree import ElementTree as ET
def median(a):
 a=sorted(a);n=len(a);return a[n//2] if n%2 else (a[n//2-1]+a[n//2])/2
ROOT=Path(__file__).resolve().parent
ROM='C059 Roman';BOLD='C059 Bold';ITA='C059 Italic'
MET=json.loads((ROOT/'data/font_widths.json').read_text())
D=json.loads((ROOT/'data/lines.json').read_text());ART={x['asset']:x for x in json.loads((ROOT/'data/artwork.json').read_text())}
FRAMES=[];SCALES=[];STYLES=set();INVENTORY=[];PAGES=[];RULES=[];OBJECT_PAGES={}
FONTKEY={ROM:'C059-Roman',BOLD:'C059-Bold',ITA:'C059-Italic'}
def measure(t,size,font=ROM):return sum(MET[FONTKEY[font]].get(str(ord(c)),.5) for c in t)*size

def text(name,x,y,w,t,size=10.8,font=ROM,align=0,italic=None):
 # y is baseline, retained in an editable single-line native frame.
 sty=f'{font}-{size}-{align}'
 lead=size*1.22
 if sty not in STYLES:
  s.createCharStyle(name=sty+' char',font=font,fontsize=size,fillcolor='Black',language='en_US')
  s.createParagraphStyle(name=sty,charstyle=sty+' char',linespacingmode=0,linespacing=lead,alignment=align,gapbefore=0,gapafter=0)
  STYLES.add(sty)
 o=s.createText(x,y-lead,w,lead+size*.7,name);s.setText(t,o);s.setParagraphStyle(sty,o)
 s.setTextDistances(0,0,0,0,o);s.setFirstLineOffset(s.FLOP_LINESPACING,o);s.setTextFlowMode(o,0)
 spans=[]
 if font==ROM:
  m=re.match(r'^\([a-z]\) (.+?\.—)',t)
  if m:spans.append((0,m.end()-1))
  elif re.match(r'^\([a-z]\)',t):spans.append((1,1))
 for term in italic or []:
  if term in t:spans.append((t.index(term),len(term)))
 for start,count in spans:s.selectText(start,count,o);s.setFont(ITA,o)
 s.selectText(0,0,o)
 natural=measure(t,size,font)
 for a,c in spans:natural+=measure(t[a:a+c],size,ITA)-measure(t[a:a+c],size,font)
 if natural>w-1:
  pct=min(100,(w-1)/natural*100);s.setTextScalingH(pct,o);SCALES.append(dict(frame=name,percent=round(pct,2)))
 FRAMES.append(o);OBJECT_PAGES[o]=len(PAGES)-1;return o

def rule(name,x1,y1,x2,y2,dashed=False,width=.35):
 o=s.createLine(x1,y1,x2,y2,name);s.setLineColor('Black',o);s.setLineWidth(width,o)
 if dashed:s.setLineStyle(2,o)
 s.setTextFlowMode(o,0);RULES.append(o);OBJECT_PAGES[o]=len(PAGES)-1

def leader(name,label,value,y,size=8.8,x=40,right=390,valuewidth=32,indent=0):
 a=text(name+'-label',x+indent,y,right-x-valuewidth-indent-4,label,size)
 text(name+'-value',right-valuewidth,y,valuewidth,value,size,align=2)
 start=x+indent+measure(label,size)+3
 if start<right-valuewidth-5:rule(name+'-leader',start,y-1.8,right-valuewidth-5,y-1.8,True)

def heading(name,y,t,size=9.5):return text(name,40,y,352,t,size,BOLD,1)
def image(name,asset,x,y,w,h):
 o=s.createImage(x,y,w,h,name);s.loadImage(str(ROOT/'assets'/asset),o);s.setScaleImageToFrame(True,True,o);s.setTextFlowMode(o,0);OBJECT_PAGES[o]=len(PAGES)-1;return o

def newpage(label,source,width=432,height=648,kind='text'):
 if PAGES:s.newPage(-1)
 PAGES.append([width,height]);s.gotoPage(len(PAGES))
 INVENTORY.append(dict(pdf_page=len(PAGES),label=label,source=source,width_points=width,height_points=height,treatment=kind))

def cover():
 newpage('Title','Primary PDF page 1')
 for x in [35,371]:text('docno'+str(x),x,35,25,'949',9,BOLD)
 for z in [('top',35,46,397,46),('left',35,46,35,614),('right',397,46,397,614),('bottom',35,614,397,614)]:rule('cover-'+z[0],*z[1:],width=.65)
 text('cover-title',45,105,342,'HANDBOOK',26,ROM,1)
 text('cover-for',45,135,342,'FOR THE',8.5,BOLD,1)
 text('cover-sub1',44,165,344,'Q. F. HOTCHKISS 2.244-INCH, 6-PDR., 6-CWT.',12,ROM,1)
 text('cover-sub2',44,185,344,'MARK II GUN WITH TANK MOUNTING',12,ROM,1)
 rule('cover-rule1',200,242,232,242)
 text('cover-prepared',45,261,342,'PREPARED IN THE OFFICE OF',9,BOLD,1)
 text('cover-chief',45,276,342,'THE CHIEF OF ORDNANCE',9,BOLD,1)
 rule('cover-rule2',200,290,232,290)
 text('cover-date',45,350,342,'August, 1919',12,ROM,1)
 image('cover-seal','printer_seal.png',176,422,80,81.8)
 for i,t in enumerate(['WASHINGTON','GOVERNMENT PRINTING OFFICE','1919']):text('cover-imprint'+str(i),45,578+i*11,342,t,7.5,BOLD,1)

def prelims():
 newpage('Document notice','Secondary PDF page 2')
 for i,t in enumerate(['WAR DEPARTMENT','Document No. 949','Office of The Adjutant General.']):text('notice'+str(i),45,303+i*15,342,t,9 if i==0 else 8.5,BOLD if i==0 else ROM,1)
 newpage('3','Secondary PDF page 3')
 text('authorization-dept',210,239,182,'WAR DEPARTMENT,',10,BOLD,2)
 text('authorization-date',130,253,262,'WASHINGTON, August 15, 1919.',10,ROM,2,italic=['August 15, 1919.'])
 ls=['The following publication, entitled “Handbook for the Q. F.', 'Hotchkiss 2.244-inch, 6-pounder, 6-hundredweight, Mark II Gun', 'with Tank Mounting,” is published for the information and guid-', 'ance of all concerned.']
 for i,t in enumerate(ls):text('authorization-body'+str(i),52 if i==0 else 40,274+i*13,340 if i==0 else 352,t,10.2,align=4 if i<3 else 0)
 text('authorization-code',40,327,352,'[062.11, A. G. O.]',8)
 text('authorization-order',40,347,352,'BY ORDER OF THE SECRETARY OF WAR:',9)
 text('authorization-march',195,364,197,'PEYTON C. MARCH,',10,BOLD,1)
 text('authorization-chief',185,378,207,'General, Chief of Staff.',9,ITA,1)
 text('authorization-official',40,397,352,'OFFICIAL:',9)
 text('authorization-harris',54,412,352,'P. C. HARRIS,',10)
 text('authorization-adjutant',66,426,300,'The Adjutant General.',9,ITA)
 text('authorization-folio',190,600,52,'3',10,align=1)
 newpage('5 / Contents','Primary PDF page 2')
 heading('toc-title',83,'TABLE OF CONTENTS.',12)
 text('toc-page',350,106,40,'Page.',7.8,align=2)
 entries=[('Table of weights, dimensions, etc. (gun)','7'),('Description of gun body','7'),('Breech and firing mechanism','8'),('Action of breech and firing mechanism','10'),('Drill hook','11'),('Dismounting and assembling breech mechanism','11'),('Spare parts and accessories','12'),('Care of gun and fittings','13'),('Mounting','14'),('Firing gear','16'),('Sighting gear','17'),('Adjustment of sights','17'),('Care of mounting','18'),('List of lubricators on the mounting','19'),('Assembling gun and mounting','19'),('Dismounting gun','20'),('Stowage for transport','21'),('Table of weights and measurements (mounting)','21'),('List of tools','21')]
 for i,(a,b) in enumerate(entries):leader('toc'+str(i),a,b,119+10.5*i,8.5)
 rule('toc-divider',191,326,241,326);heading('toc-plates',346,'PLATES.',11);rule('toc-plate-rule',199,358,233,358)
 y=379
 for section,rows in [('Gun:', [('End view of breech','A'),('Right-hand side of breech','B'),('Left-hand side of breech','C'),('Body','I'),('Breech mechanism','II'),('Dismantling parts of breech mechanism','III'),('Accessories','IV')]),('Mounting:', [('General arrangement','V and VI'),('Firing gear','VII')]),('Sighting:', [('General arrangement','VIII'),('Target for testing','IX'),('Arrangement for stowing for transport','X')])]:
  text('toc-'+section,40,y,352,section,8.5);y+=11
  for a,b in rows:leader('toc-plate-'+b,a,b,y,8.5,valuewidth=48,indent=12);y+=11
 text('toc-folio',190,593,52,'5',10,align=1)

def photos():
 captions={
 'A':['BREECH END OF GUN, BREECH OPEN, SHOWING EXTRACTOR, EXTRACTOR GROOVE, ROCKING SHAFT WITH RECOCKING HANDLE,','SEAR (IN LOWER RIGHT-HAND CORNER OF BREECHBLOCK), SEAT FOR THE BEND OF MAIN SPRING (LOWER CENTER OF','BREECHBLOCK), FIRING SHAFT BRACKET, ETC.'],
 'B':['RIGHT-HAND SIDE, BREECH END OF GUN, SHOWING CRANK HANDLES, LENGTHENING LEVER, COCKING CAM, RECOCKING HANDLE,','CRANK HANDLE LATCH, REVOLVING BRACKET, SHIELD, RECOIL BAND, RECOIL AND COUNTER-RECOIL CYLINDERS, ETC.'],
 'C':['LEFT-HAND SIDE, BREECH END OF GUN, SHOWING TRIGGER, PISTOL GRIP, SHOULDER PIECE, GUARD PLATE, SHIELD,','SIGHTING GEAR, ETC.']}
 for j,lab in enumerate('ABC'):
  newpage('Plate '+lab,f'Primary PDF page {j+3}',648,432,'grayscale photograph; native caption')
  asset='photo_'+lab+'.png';w,h=ART[asset]['pixels'];W=576;H=W*h/w;y=(388-H)/2
  image('photo'+lab,asset,36,y,W,H)
  for k,t in enumerate(captions[lab]):text('photo-caption'+lab+str(k),36,y+H+15+10*k,576,t,6.6,ROM,1)

def body():
 for leaf in range(6,21):
  p=D[leaf-1];folio=leaf+1;newpage(str(folio),f'Primary PDF page {leaf}')
  lines=p['lines'];bs=[l['box'] for l in lines if not (leaf==20 and l['index']>=46)]
  ymin=min(b[1] for b in bs);ymax=max(b[3] for b in bs);top=77 if leaf==6 else 32;bottom=592 if leaf==6 else 609
  def Y(l):return top+(l.get('baseline',l['box'][3])-ymin)/(ymax-ymin)*(bottom-top)
  bodylines=[l for l in lines if len(l['text'])>55 and not l['text'].isupper() and '_' not in l['text']]
  xmin=median(sorted(l['box'][0] for l in bodylines)[:max(1,len(bodylines)//2)])
  xmax=median(sorted(l['box'][2] for l in bodylines)[-max(1,len(bodylines)//2):])
  ys={l['index']:Y(l) for l in lines}
  skip=set()
  if leaf==6:skip.update(range(3,12))
  if leaf==11:skip.update(range(27,46))
  if leaf==12:skip.update([2,3])
  if leaf==18:skip.update(range(23,34))
  if leaf==20:skip.update(range(24,34));skip.update(range(35,48))
  for l in lines:
   i=l['index'];t=l['text'];y=ys[i]
   if i in skip:continue
   if i==0 and leaf!=6:
    text(f'p{folio}-running',82,32,270,'HANDBOOK FOR HOTCHKISS GUN.',8.8,BOLD,1)
    text(f'p{folio}-folio',40 if folio%2==0 else 364,32,28,str(folio),11.5,align=0 if folio%2==0 else 2);continue
   if leaf==6 and i==36:text('p7-folio',361,y,30,'7',10.8,align=2);continue
   if t.isupper() or t.startswith('(See Plate'):
    size=12.0 if leaf==6 and i<2 else (9.5 if re.match(r'^\d+\.',t) else 8.5)
    if leaf==13 and i in [1,2]:size=9.5
    heading(f'p{folio}-line{i}',y,t,size);continue
   if leaf==8 and i==46:text('p9-imprint',60,y,170,t,8.6);continue
   if leaf==18 and i==22:text('p19-table-title',40,y,352,t,9.2,ITA,1);continue
   indent=max(0,(l['box'][0]-xmin)/(xmax-xmin)*352)
   if indent<5:indent=0
   elif indent<18:indent=12
   elif indent<32:indent=24
   elif indent<53:indent=42
   # Single-line list indentation and original prose line endings are retained.
   x=40+indent;w=352-indent
   full=l['box'][2]>=xmax-42 and len(t)>45
   text(f'p{folio}-line{i}',x,y,w,t,10.8,align=4 if full else 0,italic=['slackened, not removed','must not'])
  if leaf==6:
   rows=[('Weight of gun, including breech mechanism','pounds','644'),('Caliber','inches','2.244'),('Total length','do','60'),('Length of bore, including chamber','do','52.12'),('Length of bore, including chamber, in calibers','','23'),('Rifling, uniform, 1 turn in 30 calibers:','',''),('Number of grooves','','24'),('Width of grooves','inch','.22'),('Depth of grooves','do','.012')]
   for j,(a,u,v) in enumerate(rows):
    y=ys[j+3];indent=12 if j>=6 else 0
    text(f'p7-row{j}-label',40+indent,y,277-indent,a,8.7)
    if v:
     text(f'p7-row{j}-unit',307,y,51,u,8.7,align=2);text(f'p7-row{j}-value',365,y,27,v,8.7,align=2)
     st=40+indent+measure(a,8.7)+3
     if st<300:rule(f'p7-row{j}-leader',st,y-1.5,302,y-1.5,True)
   rule('p7-title-rule',191,ys[1]+15,241,ys[1]+15)
  if leaf==11:
   heading('p12-parts-subtitle',ys[27],'IN SPARE PARTS BOX.',8.2)
   for k,t in enumerate(['Reference','letter on','Plate IV.']):text('p12-reference'+str(k),349,ys[27]+k*7.3,43,t,7.2,align=1)
   rows=[('2 rocking shafts',''),('2 extractors',''),('2 hammers, firing, complete',''),('4 firing pins',''),('4 firing pin housings',''),('2 sear springs',''),('4 main springs',''),('2 retaining springs for firing arm',''),('1 oil can','A'),('2 screw drivers','B'),('2 hand extractors','C'),('2 tommies','D'),('2 wrenches, screw driver, for sights (D)','E'),('2 sets of packing glands',''),('3 cloths for cleaning lens',''),('2 brushes, sponge','E')]
   for j,(a,b) in enumerate(rows):leader('p12-parts'+str(j),a,b,ys[30+j],8.7,valuewidth=20)
  if leaf==12:
   leader('p13-parts1','2 sponge rods','G',ys[2],8.8,valuewidth=20);leader('p13-parts2','1 cleaning brush','H',ys[3],8.8,valuewidth=20)
  if leaf==18:
   # Editable cells and rules, matching the source's three-column table.
   ytop=ys[22]+12;header=ytop+28;ystart=header+10;step=6.9;bottomtable=ystart+7*step+9
   for k,y in enumerate([ytop,header,bottomtable]):rule('p19-table-h'+str(k),40,y,392,y)
   for k,x in enumerate([221,257]):rule('p19-table-v'+str(k),x,ytop,x,bottomtable)
   text('p19-table-fit',43,ytop+17,175,'Fitting.',7.8,align=1)
   for k,t in enumerate(['Number','of lubri-','cators.']):text('p19-table-num'+str(k),222,ytop+8+k*8,34,t,7.2,align=1)
   text('p19-table-pos',260,ytop+17,130,'Position.',7.8,align=1)
   rows=[('Cradle','1','Right rear end.'),('    Do.','1','Top front end.'),('    Do.','1','Oil screw, left rear end.'),('Trunnion bearings','1','Oil screw, right hand.'),('    Do.','1','Oil screw, left hand.'),('Firing gear','2','Lever bearings.'),('Elevating and traversing clamps','2','1 on each clamp.'),('Pivot','1','Through center of pivot bolt.')]
   for j,(a,n,b) in enumerate(rows):
    y=ystart+j*step;text('p19-cell'+str(j)+'a',41,y,178,a,7.2);text('p19-cell'+str(j)+'b',224,y,29,n,7.2,align=2);text('p19-cell'+str(j)+'c',261,y,130,b,7.2)
    st=41+measure(a,7.2)+3
    if st<218:rule('p19-leader'+str(j),st,y-1.4,218,y-1.4,True,width=.25)
  if leaf==20:
   rows=[('Weight of pivot plate','pounds','68'),('Weight of revolving bracket','do','103'),('Weight of cradle complete, with piston, rod, counter-recoil springs,','',''),('    etc','pounds','203'),('Weight of shields (circular and inner)','do','406'),('Weight of shoulder piece, guard, and firing gear','do','60'),('Weight of sight without telescope','do','20'),('Weight of gun with mechanism','do','644'),('Weight of mounting complete, without gun','do','890'),('Mean height from base to center line of gun','inches','17.5')]
   for j,(a,u,v) in enumerate(rows):
    y=ys[24+j];text('p21-weight'+str(j)+'a',40,y,352 if not v else 282,a,8.5)
    if v:
     text('p21-weight'+str(j)+'u',310,y,43,u,8.5,align=2);text('p21-weight'+str(j)+'v',358,y,34,v,8.5,align=2)
     st=40+measure(a,8.5)+3
     if st<307:rule('p21-weight'+str(j)+'l',st,y-1.5,307,y-1.5,True)
   text('p21-wrenches',40,ys[35],352,'Wrenches, Q. F., 6-pounder, Mark II:',8.5)
   for j,t in enumerate(['Sighting gear.','Gland piston rod, compression rod, and clip ring.','Cylinder cap and stuffing box.','Compression rod and plate.','Compression rod and shoulder piece.','Guard and firing gear.','Shield stays.','Piston rod and pivot.']):
    y=ys[36+j];text('p21-toolno'+str(j),58,y,95,f'No. {136+j}',8.5);rule('p21-tooll'+str(j),93,y-1.5,170,y-1.5,True);text('p21-tool'+str(j),173,y,219,t,8.5)
   text('p21-drivers',40,ys[44],352,'Screw drivers, Q. F., 6-pounder, Mark II:',8.5)
   text('p21-driver-no',58,ys[45],95,'No. 144',8.5);rule('p21-driver-l',93,ys[45]-1.5,170,ys[45]-1.5,True);text('p21-driver',173,ys[45],219,'Steel, T-handled.',8.5)
   image('p21-printer-ornament','end_ornament.png',210,625,12,11.5)

def plates():
 srcmap={'I':21,'III':22,'IV':23,'VI':24,'VII':25,'VIII':26,'IX':27,'X':28}
 for lab in ['I','II','III','IV','V','VI','VII','VIII','IX','X']:
  asset='plate_'+lab+'.png';a=ART[asset];iw,ih=a['pixels']
  if lab in ['III','IV','IX']:pw,ph=432,648
  elif lab=='I':pw,ph=648,432
  else:pw,ph=864,648
  source=f'Primary PDF page {srcmap[lab]}' if lab in srcmap else f'Secondary PDF page {24 if lab=="II" else 27}'
  newpage('Plate '+lab,source,pw,ph,'source-pixel drawing; all labels retained in image')
  w=pw-48;h=w*ih/iw
  if h>ph-48:h=ph-48;w=h*iw/ih
  image('plate-'+lab,asset,(pw-w)/2,(ph-h)/2,w,h)

def main():
 missing={ROM,BOLD,ITA}-set(s.getFontNames())
 if missing:raise RuntimeError('Install fonts/ before rebuilding: '+str(missing))
 s.newDocument((864,648),(24,24,24,24),s.LANDSCAPE,1,s.UNIT_POINTS,s.PAGE_1,0,1)
 s.setInfo('United States War Department; digital reconstruction','Handbook for the Q. F. Hotchkiss Gun with Tank Mounting (1919) - v01','Composite archival reconstruction from two Internet Archive scans. Source wording and plate geometry retained. Modern 6 x 9 inch text pages with landscape plates; not a measured-scale reproduction.')
 s.setRedraw(False);cover();prelims();photos();body();plates();s.setRedraw(True)
 overflow=[n for n in FRAMES if s.textOverflows(n)]
 if overflow:raise RuntimeError('Overflow before save: '+str(overflow))
 path=ROOT/'Hotchkiss_Master_v01.sla';s.saveDocAs(str(path));s.closeDoc()
 # Scribus 1.6 has no public setPageSize scripter method. Modify only native
 # page dimensions, then reopen in Scribus for authoritative layout/export.
 tree=ET.parse(path);doc=tree.getroot().find('DOCUMENT');doc.set('PAGEWIDTH','432');doc.set('PAGEHEIGHT','648');doc.set('ORIENTATION','0');doc.set('PAGESIZE','Custom')
 oldorigins=[(float(p.get('PAGEXPOS')),float(p.get('PAGEYPOS'))) for p in doc.findall('PAGE')]
 neworigins=[];yy=20
 for p,(w,h) in zip(doc.findall('PAGE'),PAGES):
  p.set('PAGEWIDTH',str(w));p.set('PAGEHEIGHT',str(h));p.set('Size','Custom');p.set('Orientation','1' if w>h else '0')
  p.set('PAGEXPOS','100');p.set('PAGEYPOS',str(yy));neworigins.append((100,yy));yy+=h+40
 for o in doc.findall('PAGEOBJECT'):
  name=o.get('ANNAME');i=OBJECT_PAGES[name];ox,oy=oldorigins[i];nx,ny=neworigins[i]
  o.set('XPOS',str(float(o.get('XPOS'))+nx-ox));o.set('YPOS',str(float(o.get('YPOS'))+ny-oy));o.set('OwnPage',str(i))
 tree.write(path,encoding='UTF-8',xml_declaration=True)
 s.openDoc(str(path));overflow2=[n for n in FRAMES if s.textOverflows(n)]
 if overflow2:raise RuntimeError('Overflow after reopen: '+str(overflow2))
 s.saveDocAs(str(path))
 import tempfile
 export_path=Path(tempfile.gettempdir())/'Hotchkiss_Master_v01.pdf'
 pdf=s.PDFfile();pdf.file=str(export_path);pdf.pages=list(range(1,len(PAGES)+1));pdf.version=15;pdf.compress=True;pdf.compressmtd=3;pdf.quality=0;pdf.downsample=0;pdf.resolution=600;pdf.bookmarks=True;pdf.save()
 del pdf
 import shutil
 shutil.copyfile(export_path,ROOT/"Hotchkiss_Master_v01.pdf")
 (ROOT/'data/page_inventory.json').write_text(json.dumps(INVENTORY,indent=2))
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(scribus_version=s.scribus_version,pages=s.pageCount(),editable_text_frames=len(FRAMES),editable_rules=len(RULES),overflow_before=overflow,overflow_after=overflow2,horizontal_scaling=SCALES,page_sizes=PAGES),indent=2))
 s.closeDoc()
try:main()
except BaseException:
 (ROOT/'build_error.txt').write_text(traceback.format_exc());raise
finally:
 if os.environ.get('HOTCHKISS_BATCH')=='1':os._exit(0)
