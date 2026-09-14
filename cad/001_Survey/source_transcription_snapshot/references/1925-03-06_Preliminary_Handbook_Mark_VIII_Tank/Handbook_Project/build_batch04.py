#!/usr/bin/env python3
"""Append printed pages 61–80 to the preserved sixty-page Scribus checkpoint.
Rebuild overwrites the working master; preserve later manual edits before running.
The release PDF is exported after reopening by check_project.py.
"""
from pathlib import Path
import json,sys,os,traceback,hashlib
import scribus as s
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import layout_helpers as b
b.STYLE_PREFIX="Batch04 Style "

def fraction_line(r,y):
 token=r['stacked_fraction'];prefix,suffix=r['text'].split(token,1);num,den=token.split('/')
 x=50+r['indent'];fx=x+(r['source_fraction_left']-r['source_box'][0])*.225;fw=8.7
 # Separate native frames reproduce the stacked source fraction without raster text.
 b.txt(prefix.rstrip(),x,y,fx-x-1.5,9.7,align=4 if r['justify'] and len(prefix.split())>1 else 0,scale=92.5)
 b.txt(num,fx,y-4.4,fw,5.4,align=1);b.rule(fx+.5,y-3.2,fw-1,.3)
 b.txt(den,fx,y+1.8,fw,5.4,align=1)
 sx=fx+fw+(0 if suffix.startswith('-') else 2)
 b.txt(suffix.lstrip(),sx,y,346-sx,9.7,align=4 if r['justify'] and len(suffix.split())>1 else 0,scale=92.5)

def body(n):
 for r in BODY.get(str(n),[]):
  y=17+r['baseline']*.225;t=r['text']
  if r['heading']:b.center(t,y,r.get('size',6.5),r.get('font','Roman'));continue
  if r.get('stacked_fraction'):fraction_line(r,y);continue
  indent=r['indent'];obj=b.txt(t,50+indent,y,296-indent,9.7,align=4 if r['justify'] else 0,scale=92.5)
  for phrase in r.get('italic_runs',[]):
   s.selectText(t.index(phrase),len(phrase),obj);s.setFont('C059 Italic',obj);s.selectText(0,0,obj)
  if r.get('smallcaps_prefix'):
   prefix=r['smallcaps_prefix'];b.frames[-1]['pdf_text']=prefix.upper()+t[len(prefix):]
   s.selectText(0,len(r['smallcaps_prefix']),obj);s.setCharacterStyle('Batch04 Note small capitals',obj);s.selectText(0,0,obj)
  if r.get('italic_runs') or r.get('smallcaps_prefix'):
   s.layoutText(obj);scale=b.frames[-1]['scale'];attempts=0
   while (s.textOverflows(obj) or s.getTextLines(obj)!=1) and attempts<8:
    scale*=.97;s.setTextScalingH(scale,obj);s.layoutText(obj);attempts+=1
   b.frames[-1]['scale']=scale

def art(a):
 x=198+(a['crop'][0]-a['content_center_px'])*.225;y=17+a['crop'][1]*.225
 name=s.createImage(x,y,a['output_size'][0]*.225,a['output_size'][1]*.225,f'p{a["page"]:03}-{a["name"]}')
 s.loadImage(str(ROOT/'assets'/f'{a["name"]}.png'),name);s.setScaleImageToFrame(True,True,name);s.setTextFlowMode(name,0)

# Native plate labels, captions and folios are outside the preserved illustration pixels.
# plate number, source baseline y, native x, alignment
PLATES={62:(42,126,50,0),64:(43,319,50,0),66:(44,369,104,0),68:(45,333,65,0),71:(46,710,267,2),73:(47,539,267,2),74:(48,555,50,0),75:(49,625,267,2),78:(50,459,50,0)}
CAPTIONS={62:('PROPELLER END OF ENGINE (AVIATION TYPE)',2364),68:('DIMENSIONS FRONT ELEVATION (AVIATION MOUNTING)',1996),71:('IGNITION SWITCH',1652),73:('SECTION THROUGH CARBURETOR',1897),74:('CARBURETOR JETS AND VALVES',1897),75:('OUTLINE OF CARBURETOR',1800),78:('VALVE ROCKER ARM',2057)}
VERTICAL={64:('OUTLINE DIMENSIONS (AVIATION MOUNT SHOWN)',347,416),66:('CRANK-CASE DIMENSIONS (AVIATION MOUNT SHOWN)',301,426)}

def main():
 global BODY
 for f in ['build-status.txt','build-error.txt','check-error.txt']:(ROOT/f).unlink(missing_ok=True)
 available={r[0]:Path(r[5]) for r in s.getXFontNames()}
 for suffix in ['Roman','Bold','Italic']:
  actual=available.get('C059 '+suffix);bundled=ROOT/'fonts'/f'C059-{suffix}.otf'
  if actual is None or hashlib.sha256(actual.read_bytes()).digest()!=hashlib.sha256(bundled.read_bytes()).digest():raise RuntimeError('Use bundled C059 OpenType fonts; disable conflicting Type 1 copies.')
 BODY=json.loads((ROOT/'data/body_batch04.json').read_text());assets=json.loads((ROOT/'data/assets.json').read_text())
 previous=json.loads((ROOT/'data/batch03_native_validation.json').read_text())['frames']
 s.openDoc(str(ROOT/'Handbook_Checkpoint_001-060_v3.sla'))
 if s.pageCount()!=60:raise RuntimeError('Baseline must contain exactly 60 pages.')
 s.setInfo('Ordnance Department; digital reconstruction','Preliminary Handbook of the Mark VIII Tank — cumulative pages 1–80','1918 handbook, reprinted March 6, 1925. Review checkpoint 04; provisional C059 and 5.5 x 8.5 inch canvas. See PROJECT_STATUS.json.')
 s.createCharStyle(name='Batch04 Note small capitals',font='C059 Roman',fontsize=9.7,scaleh=.925,features='smallcaps',fillcolor='Black',language='en_US')
 s.setRedraw(False)
 for n in range(61,81):
  s.newPage(-1);s.gotoPage(n);b.folio(n);body(n)
  for a in assets:
   if a['page']==n:art(a)
  if n in PLATES:
   num,y,x,align=PLATES[n];b.txt('Plate No. '+str(num),x,17+y*.225,80,8.2,align=align)
  if n in CAPTIONS:
   t,y=CAPTIONS[n];b.center(t,17+y*.225,6.1)
  if n in VERTICAL:
   t,x,y=VERTICAL[n];obj=b.txt(t,0,12,260,6.1,align=1);s.rotateObject(90,obj);s.moveObjectAbs(x,y,obj)
  if n==65:b.txt('38285—25†——5',72,549,102,7.5)
  if n==73:b.txt('38285—25†——6',72,563,102,7.5)
  print('Appended page',n,flush=True)
 validation=[]
 for row in previous+b.frames:
  name=row['name'];s.layoutText(name)
  validation.append({**row,'overflow':bool(s.textOverflows(name)),'line_count':s.getTextLines(name),'text_matches':s.getAllText(name)==row['text']})
 errors=[r for r in validation if r['overflow'] or r['line_count']!=1 or not r['text_matches']]
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(pages=s.pageCount(),frames=validation,errors=errors,new_text_frames=len(b.frames),compressed_below_85_percent=b.fits),ensure_ascii=False,indent=2))
 if errors:raise RuntimeError('Text validation failed: '+repr(errors[:3]))
 s.gotoPage(1);s.saveDocAs(str(ROOT/'Handbook_Rebuilt_001-080_v4.sla'))
 (ROOT/'build-status.txt').write_text(f'PASS: 80 cumulative pages; {len(validation)} native text frames, including {len(b.frames)} new frames; no overflow or text mismatches.\n')
 s.setRedraw(True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'build-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
