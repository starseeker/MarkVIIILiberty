#!/usr/bin/env python3
"""Append printed pages 81–100 to the preserved eighty-page Scribus checkpoint.
Rebuild overwrites the working master; preserve later manual edits before running.
The release PDF is exported after reopening by check_project.py.
"""
from pathlib import Path
import json,sys,os,traceback,hashlib
import scribus as s
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import layout_helpers as b
b.STYLE_PREFIX="Batch05 Style "

def fraction_line(r,y):
 token=r['stacked_fraction'];prefix,suffix=r['text'].split(token,1);num,den=token.split('/')
 x=r['x']+r['indent'];fx=x+(r['source_fraction_left']-r['source_box'][0])*.225;fw=8.7
 # Separate native frames reproduce the stacked source fraction without raster text.
 b.txt(prefix.rstrip(),x,y,fx-x-1.5,9.7,align=4 if r['justify'] and len(prefix.split())>1 else 0,scale=92.5)
 b.txt(num,fx,y-4.4,fw,5.4,align=1);b.rule(fx+.5,y-3.2,fw-1,.3)
 b.txt(den,fx,y+1.8,fw,5.4,align=1)
 sx=fx+fw+(0 if suffix.startswith('-') else 2)
 b.txt(suffix.lstrip(),sx,y,r['x']+r['width']-sx,9.7,align=4 if r['justify'] and len(suffix.split())>1 else 0,scale=92.5)

def body(n):
 for r in BODY.get(str(n),[]):
  y=17+r['baseline']*.225;t=r['text']
  if r['heading']:b.center(t,y,r.get('size',6.5),r.get('font','Roman'));continue
  if r.get('stacked_fraction'):fraction_line(r,y);continue
  indent=r['indent'];obj=b.txt(t,r['x']+indent,y,r['width']-indent,9.7,align=4 if r['justify'] else 0,scale=92.5)
  for phrase in r.get('italic_runs',[]):
   s.selectText(t.index(phrase),len(phrase),obj);s.setFont('C059 Italic',obj);s.selectText(0,0,obj)
  if r.get('smallcaps_prefix'):
   prefix=r['smallcaps_prefix'];b.frames[-1]['pdf_text']=prefix.upper()+t[len(prefix):]
   s.selectText(0,len(r['smallcaps_prefix']),obj);s.setCharacterStyle('Batch05 Note small capitals',obj);s.selectText(0,0,obj)
  if r.get('italic_runs') or r.get('smallcaps_prefix'):
   s.layoutText(obj);scale=b.frames[-1]['scale'];attempts=0
   while (s.textOverflows(obj) or s.getTextLines(obj)!=1) and attempts<8:
    scale*=.97;s.setTextScalingH(scale,obj);s.layoutText(obj);attempts+=1
   b.frames[-1]['scale']=scale

def art(a):
 x=198+(a['crop'][0]-a['content_center_px'])*.225;y=17+a['crop'][1]*.225
 name=s.createImage(x,y,a['output_size'][0]*.225,a['output_size'][1]*.225,f'p{a["page"]:03}-{a["name"]}')
 s.loadImage(str(ROOT/'assets'/f'{a["name"]}.png'),name);s.setScaleImageToFrame(True,True,name);s.setTextFlowMode(name,0)

# External labels are native; only original illustration interiors remain raster.
PLATES={82:[('51',171,50,0)],85:[('52',120,267,2)],87:[('53',1007,216,2)],89:[('54',313,232,1),('55',1520,91,1)],90:[('56',1484,63,1)],91:[('57',619,267,2)],93:[('58',189,42,0),('59',131,267,2),('60',856,52,0)],95:[('61',128,36,0),('62',945,267,2)],96:[('63',768,50,0)],97:[('64',587,87,0)],99:[('65.',568,267,2)]}
CAPTIONS={82:[('GENERATOR DRIVE SHAFT',2388,40,316)],87:[('CYLINDER ASSEMBLY',1681,40,316)],89:[('REMOVING PISTON PIN',723,200,146),('REMOVING PIN (ALTERNATIVE METHOD)',2265,44,169)],90:[('FITTING RINGS',2264,53,96)],91:[('CONNECTING RODS',1822,40,316)],93:[('ALIGNING RODS',856,218,134)],97:[('PIPE INSTALLATION',1881,40,316)],99:[('FAN BEVEL GEAR DRIVE',1977,40,316)]}
VERTICAL={85:[('WATER PUMP ASSEMBLY',140,48,230,270)],95:[('END OF CRANK SHAFT (PROPELLER HUB SHOWN DOES NOT APPLY TO ORDNANCE ENGINE',355,191,404,90),('JOCKEY PULLEY',100,357,432,90)]}

def rotated_legend():
 rows=json.loads((ROOT/'data/batch05_legend.json').read_text())
 def cell(t,u,v,w,align=0):
  o=b.txt(t,0,12,w,5.8,align=align);s.rotateObject(90,o);s.moveObjectAbs(232+v-7.25,193-u,o)
 for t,u,v,w in [('Ref.',0,8,16),('No.',0,14,16),('Part',20,8,24),('No.',20,14,24),('Name.',48,14,94)]:cell(t,u,v,w,1)
 for j,(ref,part,name) in enumerate(rows):
  v=23+5.7*j;cell(str(ref),0,v,16,1);cell(part,18,v,30);cell(name,50,v,92)

def main():
 global BODY
 for f in ['build-status.txt','build-error.txt','check-error.txt']:(ROOT/f).unlink(missing_ok=True)
 available={r[0]:Path(r[5]) for r in s.getXFontNames()}
 for suffix in ['Roman','Bold','Italic']:
  actual=available.get('C059 '+suffix);bundled=ROOT/'fonts'/f'C059-{suffix}.otf'
  if actual is None or hashlib.sha256(actual.read_bytes()).digest()!=hashlib.sha256(bundled.read_bytes()).digest():raise RuntimeError('Use bundled C059 OpenType fonts; disable conflicting Type 1 copies.')
 BODY=json.loads((ROOT/'data/body_batch05.json').read_text());assets=json.loads((ROOT/'data/assets.json').read_text())
 previous=json.loads((ROOT/'data/batch04_native_validation.json').read_text())['frames']
 s.openDoc(str(ROOT/'Handbook_Checkpoint_001-080_v4.sla'))
 if s.pageCount()!=80:raise RuntimeError('Baseline must contain exactly 80 pages.')
 s.setInfo('Ordnance Department; digital reconstruction','Preliminary Handbook of the Mark VIII Tank — cumulative pages 1–100','1918 handbook, reprinted March 6, 1925. Review checkpoint 05; provisional C059 and 5.5 x 8.5 inch canvas. See PROJECT_STATUS.json.')
 s.createCharStyle(name='Batch05 Note small capitals',font='C059 Roman',fontsize=9.7,scaleh=.925,features='smallcaps',fillcolor='Black',language='en_US')
 s.setRedraw(False)
 for n in range(81,101):
  s.newPage(-1);s.gotoPage(n);b.folio(n);body(n)
  for a in assets:
   if a['page']==n:art(a)
  for num,y,x,align in PLATES.get(n,[]):b.txt('Plate No. '+num,x,17+y*.225,80,8.2,align=align)
  for t,y,x,w in CAPTIONS.get(n,[]):b.txt(t,x,17+y*.225,w,6.1,align=1)
  for t,w,x,y,angle in VERTICAL.get(n,[]):
   obj=b.txt(t,0,12,w,6.1,align=1);s.rotateObject(angle,obj);s.moveObjectAbs(x,y,obj)
  if n==95:rotated_legend()
  if n==97:b.txt('38285—25†——7',72,550,102,7.5)
 validation=[]
 for row in previous+b.frames:
  name=row['name'];s.layoutText(name)
  validation.append({**row,'overflow':bool(s.textOverflows(name)),'line_count':s.getTextLines(name),'text_matches':s.getAllText(name)==row['text']})
 errors=[r for r in validation if r['overflow'] or r['line_count']!=1 or not r['text_matches']]
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(pages=s.pageCount(),frames=validation,errors=errors,new_text_frames=len(b.frames),compressed_below_85_percent=b.fits),ensure_ascii=False,indent=2))
 if errors:raise RuntimeError('Text validation failed: '+repr(errors[:3]))
 s.gotoPage(1);s.saveDocAs(str(ROOT/'Handbook_Checkpoint_001-100_v5.sla'))
 (ROOT/'build-status.txt').write_text(f'PASS: 100 cumulative pages; {len(validation)} native text frames, including {len(b.frames)} new frames; no overflow or text mismatches.\n')
 s.setRedraw(True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'build-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
