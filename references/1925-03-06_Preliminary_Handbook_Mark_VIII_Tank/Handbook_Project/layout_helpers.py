#!/usr/bin/env python3
"""Native Scribus helpers for cumulative checkpoints; import from build_project.py.
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
STYLE_PREFIX='Batch13 Style '
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
  sty=STYLE_PREFIX+str(len(styles)+1);leading=size*1.25
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
