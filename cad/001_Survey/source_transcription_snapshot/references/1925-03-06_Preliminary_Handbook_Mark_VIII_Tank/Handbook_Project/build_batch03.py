#!/usr/bin/env python3
"""Append pages 41–60 to the preserved forty-page checkpoint in Scribus 1.6.x.
This rebuild overwrites the current master. Preserve manual edits before running.
Final PDF is exported after reopening by check_project.py.
"""
from pathlib import Path
import json,sys,os,traceback,hashlib
import scribus as s
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import layout_helpers as b
b.STYLE_PREFIX='Batch03 Style '
from data.batch03_tables import ENGINE_SPECS,OPENINGS,FIRING_ORDER,LEGENDS

def body(n):
 for r in BODY.get(str(n),[]):
  y=17+r['baseline']*.225;t=r['text']
  if r['heading']:b.center(t,y,r.get('size',6.5),r.get('font','Roman'));continue
  indent=r['indent'];obj=b.txt(t,50+indent,y,296-indent,9.7,align=4 if r['justify'] else 0,scale=92.5)
  if r.get('italic_prefix'):
   s.selectText(0,len(r['italic_prefix']),obj);s.setFont('C059 Italic',obj);s.selectText(0,0,obj);s.layoutText(obj)
   # A different run font may slightly increase the full line width.
   scale=b.frames[-1]['scale'];attempts=0
   while (s.textOverflows(obj) or s.getTextLines(obj)!=1) and attempts<8:
    scale*=.97;s.setTextScalingH(scale,obj);s.layoutText(obj);attempts+=1
   b.frames[-1]['scale']=scale

def art(a):
 x=198+(a['crop'][0]-a['content_center_px'])*.225;y=17+a['crop'][1]*.225
 name=s.createImage(x,y,a['output_size'][0]*.225,a['output_size'][1]*.225,f'p{a["page"]:03}-{a["name"]}')
 s.loadImage(str(ROOT/'assets'/f'{a["name"]}.png'),name);s.setScaleImageToFrame(True,True,name);s.setTextFlowMode(name,0)

def specs(rows,y,step,size,x=50,valuex=232,right=350):
 for label,value in rows:
  width=valuex-x-8;natural=b.advance(label,size,'Roman');scale=min(100,(width-1.2)/natural*100)
  b.txt(label,x,y,width,size,scale=scale)
  start=x+natural*scale/100+2;end=valuex-5
  if start+1<end:b.rule(start,y-1.8,end-start,.25,True)
  if value=='4 15/16 inches.':
   b.txt('4',valuex,y,6,size);b.txt('15',valuex+5,y-4,7,4.7,align=1)
   b.rule(valuex+5.4,y-2.9,5.8,.3);b.txt('16',valuex+5,y+1.7,7,4.7,align=1)
   b.txt('inches.',valuex+15,y,right-valuex-15,size)
  else:b.txt(value,valuex,y,right-valuex,size)
  y+=step

def legend(n):
 if n not in LEGENDS:return
 y0={41:376,44:405,48:514}[n];size=5.7;step=5.8
 for col,rows in enumerate(LEGENDS[n]):
  x=50+col*153;namex=x+(40 if n==48 else 15);right=x+145
  b.txt('Ref.',x,y0-12,12,size);b.txt('No.',x,y0-6,12,size)
  if n==48:b.txt('Part',x+17,y0-12,24,size);b.txt('No.',x+17,y0-6,24,size)
  b.txt('Name',namex+10,y0-6,right-namex-10,size)
  y=y0
  for ref,part,desc in rows:
   if ref:b.txt(ref,x,y,10,size,align=1)
   if part:b.txt(part,x+12,y,namex-x-14,size)
   if desc:b.txt(desc,namex,y,right-namex,size)
   y+=step
 name=s.createLine(198,y0-15,198,y0+(max(map(len,LEGENDS[n]))-1)*step+1)
 s.setLineWidth(.25,name);s.setLineColor('Black',name)

PLATEPOS={41:(32,273),43:(33,858),44:(34,576),48:(35,220),50:(36,125),52:(37,120),56:(39,99),58:(40,195),60:(41,100)}
CAPTIONS={41:('SIDE OF HULL',1485),43:('SIDE TOWING BRACKET',1533),44:('FRONT OF MACHINE',1614),48:('SIROCCO COOLING FAN',2113),52:('VALVE AND PUMP DRIVE',2307),60:('DISTRIBUTOR END OF ENGINE',2322)}
VERTICAL={50:('COOLING SYSTEM',369,391),54:('ENGINE-OIL SYSTEM',363,386),56:('CAMSHAFT ASSEMBLY',365,376),58:('LONGITUDINAL ENGINE SECTION',367,380)}

def main():
 global BODY
 for f in ['build-status.txt','build-error.txt','check-error.txt']:(ROOT/f).unlink(missing_ok=True)
 available={r[0]:Path(r[5]) for r in s.getXFontNames()}
 for suffix in ['Roman','Bold','Italic']:
  actual=available.get('C059 '+suffix);bundled=ROOT/'fonts'/f'C059-{suffix}.otf'
  if actual is None or hashlib.sha256(actual.read_bytes()).digest()!=hashlib.sha256(bundled.read_bytes()).digest():raise RuntimeError('Use bundled C059 OpenType fonts; disable conflicting Type 1 copies.')
 BODY=json.loads((ROOT/'data/body_batch03.json').read_text());assets=json.loads((ROOT/'data/assets.json').read_text())
 previous=json.loads((ROOT/'data/batch02_native_validation.json').read_text())['frames']
 s.openDoc(str(ROOT/'Handbook_Checkpoint_001-040_v2.sla'))
 if s.pageCount()!=40:raise RuntimeError('Baseline must contain exactly 40 pages.')
 s.setInfo('Ordnance Department; digital reconstruction','Preliminary Handbook of the Mark VIII Tank — cumulative pages 1–60','1918 handbook, reprinted March 6, 1925. Review checkpoint 03; provisional C059 and 5.5 x 8.5 inch canvas. See PROJECT_STATUS.json.')
 s.setRedraw(False)
 for n in range(41,61):
  s.newPage(-1);s.gotoPage(n)
  if n not in (45,54):b.folio(n)
  body(n)
  for a in assets:
   if a['page']==n:art(a)
  if n in PLATEPOS:
   num,y=PLATEPOS[n];x=50 if n in (56,58,60) else 230 if n==43 else 267
   b.txt('Plate No. '+str(num)+('.' if n==58 else ''),x,17+y*.225,80,8.2,align=0 if n in (43,56,58,60) else 2)
  if n in CAPTIONS:
   t,y=CAPTIONS[n];b.center(t,17+y*.225,6.1)
  if n in VERTICAL:
   t,x,y=VERTICAL[n];obj=b.txt(t,0,12,185,6.1,align=1);s.rotateObject(90,obj);s.moveObjectAbs(x,y,obj)
  if n==41:b.txt('38285—25†——4',72,489,102,7.5)
  if n==43:specs(OPENINGS,487,9.4,7.8,valuex=212,right=350)
  if n==45:
   b.center('Chapter III',57,10);title='ENGINE AND ENGINE SYSTEMS';obj=b.center(title,75,9.5,'Bold')
   # Native superscript footnote marker, kept out of the centered title's alignment.
   b.txt('1',198+b.advance(title,9.5,'Bold')/2+1,71,5,5.5)
   b.center('Outline specifications',91,8.4,'Italic');specs(ENGINE_SPECS,104,9.4,7.9)
   b.txt('1 Much of this data deals with airplane type. Taken from Signal Corps book for preliminary handbook.',55,536,291,5.5)
   b.center('(45)',549,8.3)
  if n==47:
   for i,value in enumerate(FIRING_ORDER):
    x=49+i*25;b.txt(str(i+1),x,333.5,23,9.0,align=1);b.txt(value,x,344,23,9.0,align=1)
  if n==54:b.center('(54)',577,8.3)
  legend(n)
  print('Appended page',n,flush=True)
 validation=[]
 for row in previous+b.frames:
  name=row['name'];s.layoutText(name)
  validation.append({**row,'overflow':bool(s.textOverflows(name)),'line_count':s.getTextLines(name),'text_matches':s.getAllText(name)==row['text']})
 errors=[r for r in validation if r['overflow'] or r['line_count']!=1 or not r['text_matches']]
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(pages=s.pageCount(),frames=validation,errors=errors,new_text_frames=len(b.frames),compressed_below_85_percent=b.fits),ensure_ascii=False,indent=2))
 if errors:raise RuntimeError('Text validation failed: '+repr(errors[:3]))
 s.gotoPage(1);s.saveDocAs(str(ROOT/'Handbook_Rebuilt_001-060_v3.sla'))
 (ROOT/'build-status.txt').write_text(f'PASS: 60 cumulative pages; {len(validation)} native text frames, including {len(b.frames)} new frames; no overflow or text mismatches.\n')
 s.setRedraw(True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'build-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
