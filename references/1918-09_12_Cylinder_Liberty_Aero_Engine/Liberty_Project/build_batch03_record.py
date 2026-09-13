"""Append batch 03 to the preserved batch-02 SLA. Run inside Scribus 1.6.x.
The current master is not an input: rerunning never duplicates new pages.
Save user edits to a separate file before rebuilding from authoritative JSON.
"""
from pathlib import Path
import sys,os,json,traceback
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import scribus as s
import layout_helpers as h
R=json.loads((ROOT/'data/release.json').read_text())
OLD=json.loads((ROOT/'data/batch02_release.json').read_text())
D=json.loads((ROOT/'data/batch03_transcription.json').read_text())
A=json.loads((ROOT/'data/batch03_artwork.json').read_text())
def main():
 for p in ['build_error.txt','data/build_success.json']:
  if (ROOT/p).exists():(ROOT/p).unlink()
 missing=set(h.FONT.values())-set(s.getFontNames())
 if missing:raise RuntimeError('Install bundled OpenType fonts: '+str(missing))
 s.openDoc(str(ROOT/OLD['sla']));assert s.pageCount()==40
 s.setInfo('Ministry of Munitions; digital reconstruction','The Liberty 12-Cylinder Aero Engine Handbook (1918) — '+R['release_id'],'Batches 01–03: source scans 0001–0060, cover through printed page 58. Editable transcription and original-pixel figures. Provisional trim and typography.')
 s.setRedraw(False)
 for p in D['pages']:
  n=p['leaf'];s.newPage(-1);s.gotoPage(n)
  h.center(str(n-2),p['folio_baseline']*h.SX,11)
  for spec in p['headings']:
   y,t,*fmt=spec;size=fmt[0] if fmt else 11.5;font=fmt[1] if len(fmt)>1 else 'Roman'
   h.center(t,y*h.SX,size,font)
  for b in p['blocks']:
   for j,l in enumerate(b['lines']):
    ind=l['indent']*h.SX;t=l['text'];y=(b['y']+j*b['step'])*h.SX
    h.rich(t,h.LEFT+ind,y,h.BW-ind,h.BODY,4 if len(t)>(28 if n in [51,52,53,58] and ind>=40 else 46) and '{' not in t and (j<len(b['lines'])-1 or not t.endswith(('.', '—'))) else 0)
  for a in [a for a in A if a['leaf']==n]:
   x0,y0,x1,y1=a['crop'];cx=a['source_center']
   o=s.createImage(h.W/2+(x0-cx)*h.SX,y0*h.SX,(x1-x0)*h.SX,(y1-y0)*h.SX,'figure-'+str(a['figure']))
   s.loadImage(str(ROOT/'assets'/a['asset']),o);s.setScaleImageToFrame(True,True,o);s.setTextFlowMode(o,0)
  for y,t in p['captions']:h.center(t,y*h.SX,10.8)
  for legend in p['legends']:
   for j,t in enumerate(legend['lines']):
    o=h.text(t,legend['x'],(legend['y']+j*legend['step'])*h.SX,legend['width'],legend['size'])
    # Small baseline numerals in the original legends remain real searchable characters.
    if len(t)>1 and t[1].isdigit():
     s.selectText(1,1,o);s.setFontSize(legend['size']*.75,o);s.selectText(0,0,o)
  for table in p['tables']:
   for j,(label,value) in enumerate(table['rows']):
    h.leader(label,value,(table['y']+j*table['step'])*h.SX,x=table['x'],w=table['width'],refwidth=table['refwidth'],size=10.8)
    s.setTextAlignment(s.ALIGN_LEFT,h.frames[-1]['name'])
 s.setRedraw(True)
 oldframes=json.loads((ROOT/'data/batch02_native_frames.json').read_text());frames=oldframes+h.frames
 err=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
 if err:raise RuntimeError('Text layout errors: '+str(err))
 path=ROOT/R['sla'];s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
 err2=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1 or s.getAllText(f['name'])!=f['text']]
 if err2:raise RuntimeError('Reopen errors: '+str(err2))
 s.saveDocAs(str(path))
 pdf=s.PDFfile();pdf.file=str(ROOT/R['pdf']);pdf.pages=list(range(1,61));pdf.version=15;pdf.compress=True;pdf.compressmtd=2;pdf.quality=0;pdf.downsample=0;pdf.resolution=600;pdf.outdst=0;pdf.bookmarks=True;pdf.save();del pdf
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(scribus_version=s.scribus_version,pages=s.pageCount(),editable_text_frames=len(frames),new_text_frames=len(h.frames),new_fraction_rules=len(h.rules),overflow_before=err,overflow_after=err2,frames_below_85_percent=h.fits),indent=2))
 (ROOT/'data/native_frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
 s.closeDoc();(ROOT/'data/build_success.json').write_text(json.dumps(R,indent=2))
try:main()
except BaseException:
 (ROOT/'build_error.txt').write_text(traceback.format_exc());raise
finally:
 if os.environ.get('LIBERTY_BATCH')=='1':os._exit(0)
