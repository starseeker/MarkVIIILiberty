"""Run with Scribus 1.6.x, Script > Execute Script. Does not require OCR tools.
Writes fresh versioned SLA/PDF names from data/release.json. Save manual edits
under another name before rebuilding. JSON text and assets are authoritative.
"""
from pathlib import Path
import scribus as s
import json,os,re,traceback
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/transcription.json').read_text());A=json.loads((ROOT/'data/artwork.json').read_text())
R=json.loads((ROOT/'data/release.json').read_text());MET=json.loads((ROOT/'fonts/metrics.json').read_text())
W,H=396.,691.;SX=W/1893.;BODY=10.8;BW=304.;LEFT=46.
FONT={'Roman':'C059 Roman','Bold':'C059 Bold','Italic':'C059 Italic','Sans':'Nimbus Sans Bold'}
KEY={'Roman':'C059-Roman','Bold':'C059-Bold','Italic':'C059-Italic','Sans':'NimbusSans-Bold'}
frames=[];rules=[];styles={};serial=0;fits=[]
STYLE_PREFIX='Liberty b03 '
def measure(t,size,font='Roman'):return sum(MET[KEY[font]].get(c,.5) for c in t)*size
def text(t,x,y,w,size=BODY,font='Roman',align=0,scale=100,name=None):
 global serial
 serial+=1;name=name or f'scan{s.currentPage():04}-text-{serial:04}'
 natural=measure(t,size,font)
 scale=min(scale,(w-1.2)/max(natural,.1)*100)
 key=(size,font,align,round(scale,3))
 if key not in styles:
  sty=STYLE_PREFIX+str(len(styles)+1);lead=size*1.25
  s.createCharStyle(name=sty+' char',font=FONT[font],fontsize=size,fillcolor='Black',language='en_GB',scaleh=scale/100)
  s.createParagraphStyle(name=sty,charstyle=sty+' char',linespacingmode=0,linespacing=lead,alignment=align,gapbefore=0,gapafter=0)
  styles[key]=sty
 lead=size*1.25
 s.createText(x,y-lead,w,lead+size*.65+3,name);s.setText(t,name);s.setParagraphStyle(styles[key],name)
 s.setTextDistances(0,0,0,0,name);s.setFirstLineOffset(s.FLOP_LINESPACING,name);s.setTextFlowMode(name,0);s.layoutText(name)
 attempts=0
 while (s.textOverflows(name) or s.getTextLines(name)!=1) and attempts<8:
  scale*=.97;s.setTextScalingH(scale,name);s.layoutText(name);attempts+=1
 if 'vice versâ' in t and s.currentPage()!=53:
  s.selectText(t.index('vice versâ'),len('vice versâ'),name);s.setFont(FONT['Italic'],name);s.selectText(0,0,name)
 frames.append(dict(name=name,page=s.currentPage(),text=t,x=x,baseline=y,width=w,size=size,scale=scale))
 if scale<85:fits.append(dict(name=name,scale=scale,text=t))
 return name
def rule(x,y,x2,y2,width=.35):
 global serial
 serial+=1;o=s.createLine(x,y,x2,y2,f'scan{s.currentPage():04}-rule-{serial}');s.setLineColor('Black',o);s.setLineWidth(width,o);s.setTextFlowMode(o,0);rules.append(o);return o
def center(t,y,size=BODY,font='Roman'):return text(t,25,y,W-50,size,font,1)
def leader(t,ref,y,x=LEFT,w=BW,size=10.4,font='Roman',number=None,refwidth=29):
 if number is not None:
  nw=42 if len(number)>5 else 31
  text(number+'.',x-(nw-31),y,nw,size,font,2);x+=36;w-=36
 reserve=refwidth+5 if ref else 0
 o=text(t,x,y,w-reserve,size,font)
 if ref:
  text(ref,x+w-refwidth,y,refwidth,size,font,2)
  fr=frames[-2];start=x+measure(t,size,font)*fr['scale']/100+5;end=x+w-refwidth-8
  # Each leader dot is a native ellipse, separate from searchable text.
  while start+1<end:
   dot=s.createEllipse(start,y-2,.5,.5);s.setFillColor('Black',dot);s.setLineColor('None',dot);start+=4
 return o
def rich(t,x,y,w,size=BODY,align=0):
 if not re.search(r'\{\d+/\d+\}',t):return text(t,x,y,w,size,align=align)
 seg=re.split(r'(\{\d+/\d+\})',t);adv=[]
 for a in seg:adv.append(size*.74 if a.startswith('{') else measure(a,size))
 scale=min(1,(w-2)/sum(adv));pos=x
 for a,v in zip(seg,adv):
  if not a:continue
  if a.startswith('{'):
   num,den=a[1:-1].split('/');fw=v*scale
   text(num,pos,y-size*.46,fw,size*.56,align=1);rule(pos+.5,y-size*.36,pos+fw-.5,y-size*.36,.28)
   text(den,pos,y+size*.17,fw,size*.56,align=1)
  else:text(a,pos,y,v*scale+1.4,size,scale=scale*100)
  pos+=v*scale
def contents(n):
 if n==5:
  center('The Liberty Aero Engine.',178,23,'Bold');rule(143,210,253,210,.7)
  center('TABLE OF CONTENTS.',261,14);rule(173,284,223,284)
  text('PAGE.',309,311,40,10.4,align=2)
  for j,(a,b) in enumerate([('Introductory Note','5'),('Index of Illustrations','6'),('Leading Particulars','8')]):leader(a,b,325+j*11.3)
  settings=[(371,389,409),(526,544,564)]
 else:settings=[(78,91,103),(129,140,154),(332,345,359),(491,505,520)]
 for (roman,title,rows),(chapter,head,ystart) in zip(D['contents'][str(n)],settings):
  center('CHAPTER '+roman+'.',chapter,11.5);text(title,LEFT,head,BW,10.3,'Sans')
  for j,(a,b) in enumerate(rows):leader(a,b,ystart+11.3*j,x=LEFT+21,w=BW-21)
def contents_tail():
 for title,y in [('CHAPTER VII.',69),('CHAPTER VIII.',96),('CHAPTER IX.',122),('CHAPTER X.',149)]:center(title,y,11.5)
 text('PAGE.',310,69,40,10,align=2)
 for label,val,y in [('POSSIBLE TROUBLES','130',83),('INSTALLATION NOTES','133',110),('C.C. GEAR ON LIBERTY ENGINES','138',136),('CLEARANCES','140',173),('APPENDIX','142',185)]:
  leader(label,val,y,size=9.9,font='Sans',x=LEFT+26 if label=='CLEARANCES' else LEFT,w=BW-26 if label=='CLEARANCES' else BW)
 text('TABLE OF STANDARD FITS AND',LEFT,161,BW,9.9,'Sans')
 center('Introductory Note.',213,21,'Bold')
def index(n):
 rows=D['illustration_index'][str(n)]
 if n==8:center('INDEX OF ILLUSTRATIONS.',71,14,'Bold');rule(175,77,221,77);y=98
 elif n==9:y=99
 else:y=97
 header=y-13;text('Fig. No.',LEFT,header,45,9.6,'Bold');text('Subject.',100,header,200,9.6,'Bold',1);text('Page.',310,header,40,9.6,'Bold',2)
 for entry in rows:
  for j,t in enumerate(entry['text']):
   last=j==len(entry['text'])-1;ref=entry['reference'] if last else ''
   if j==0:
    rw=80 if ref=='Frontispiece' else 40 if len(ref)>4 else 29
    leader(t,ref,y,x=42,w=312,size=10.0,number=entry['number'],refwidth=rw)
   else:leader(t,ref,y,x=86,w=268,size=10.0)
   y+=11.2
 if n==10:center('Leading Particulars.',353,21,'Bold');rule(178,361,218,361)
def cover():
 for x in [43,353]:rule(x,55,x,638,.65)
 rule(43,55,353,55,.65);rule(43,638,353,638,.65)
 text('H.B. 809.',287,99,59,10.5,'Sans',2)
 center('MINISTRY OF MUNITIONS.',129,14,'Bold')
 center('Technical Department—Aircraft Production.',153,11.6)
 text('CENTRAL HOUSE,',196,184,149,9.5,align=1);text('KINGSWAY, W.C.2.',210,197,136,9.5,align=2)
 center('THE',240,13);center('12 CYLINDER',265,13)
 center('Liberty Aero Engine.',309,27,'Bold')
 center('CONFIDENTIAL',346,15,'Bold');rule(119,350,277,350,.5)
 center('Attention is called to the penalties attaching to any',387,10.3)
 center('infringement of the Official Secrets Act.',402,10.3)
 center('SEPTEMBER, 1918.',445,12,'Sans')
 center('FOR USE OF MEMBERS OF THE',495,11.5);center('ROYAL AIR FORCE.',514,11.5)
 text('J. G. WEIR, Brigadier-General,',142,573,204,10.7,align=2)
 text('Controller, Technical Department.',142,590,204,9.4,align=2)
 text('T. 5.—372/4131.—2000/9/18.   P. 34.',43,648,307,7.5)
def special(n):
 if n==1:cover()
 elif n==3:
  for t,y,sz in [('THE',251,16),('LIBERTY',317,37),('12-Cylinder Aero Engine',371,24),('Handbook.',423,25)]:center(t,y,sz)
 elif n==4:center('The Liberty Engine.',610,11)
 elif n in [5,6]:contents(n)
 elif n==7:contents_tail()
 elif n in [8,9,10]:index(n)
 elif n==11:
  # Two source braces and their shared Propeller labels are native editable text.
  text('}',207,400,12,23);text('Propeller.',221,396,103,10.8)
  text('}',310,422,12,23);text('Propeller.',322,418,69,10.2)
 elif n==13:
  rule(113,136,283,136);center('CHAPTER I.',164,12);center('General Description.',200,21,'Bold')
 elif n==14:center('CYLINDERS.',90,11.5)
 elif n==15:center('PISTONS.',544,11.5)
 elif n==17:center('CONNECTING RODS.',516,11.5)
 elif n==19:center('CRANKSHAFT.',366,11.5)
 elif n==20:center('BASE CHAMBER.',520,11.5)
CAP={12:[(2,2470,'Cylinders.')],13:[(3,2828,'Section of a Cylinder','(showing welded joints).')],14:[(4,2190,'Cylinder Head (plan view).')],15:[(5,2320,'Side View of a Cylinder.')],16:[(6,2515,'Cylinder: Section through Valve Gear.')],17:[(7,2280,'Broken View of “Army” Piston.')],18:[(8,1720,'Pistons and Gudgeon Pins.'),(9,2935,'Connecting Rods.')],19:[(10,1500,'Pair of Connecting Rods (dismantled).')],20:[(11,790,'Lower Half of Main Bearing.'),(12,2240,'Crankshaft Taper and Key.')]}
