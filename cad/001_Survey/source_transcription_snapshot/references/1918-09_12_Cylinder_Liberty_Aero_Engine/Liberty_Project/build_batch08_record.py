"""Append batch 08 to the preserved batch-07 SLA. Run inside Scribus 1.6.x.
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
OLD=json.loads((ROOT/'data/baseline_v07_release.json').read_text())
D=json.loads((ROOT/'data/batch08_transcription.json').read_text())
A=json.loads((ROOT/'data/batch08_artwork.json').read_text())
def main():
 for p in ['build_error.txt','data/build_success.json']:
  if (ROOT/p).exists():(ROOT/p).unlink()
 missing=set(h.FONT.values())-set(s.getFontNames())
 if missing:raise RuntimeError('Install bundled OpenType fonts: '+str(missing))
 import runpy
 runpy.run_path(str(ROOT/'scripts/prepare_batch08_seed.py'))
 s.openDoc(str(ROOT/'_batch08_seed.sla'));assert s.pageCount()==160
 s.setInfo('Ministry of Munitions; digital reconstruction','The Liberty 12-Cylinder Aero Engine Handbook (1918) — '+R['release_id'],'Batches 01–08: source scans 0001–0160, cover through printed page 151, including five foldouts and seven additional blank leaves. Editable transcription and original-pixel figures. Provisional trim and typography.')
 s.setRedraw(False)
 for p in D['pages']:
  n=p['leaf'];s.gotoPage(n)
  h.W,h.H=p['page_size_points']
  assert tuple(s.getPageNSize(n))==tuple(p['page_size_points']),(n,s.getPageNSize(n))
  if p['printed_page'] is not None:h.center(str(p['printed_page']),p['folio_baseline']*h.SX,11)
  for spec in p['headings']:
   y,t,*fmt=spec;size=fmt[0] if fmt else 11.5;font=fmt[1] if len(fmt)>1 else 'Roman'
   h.center(t,y*h.SX,size,font)
  for b in p['blocks']:
   for j,l in enumerate(b['lines']):
    ind=l['indent']*h.SX;t=l['text'];y=(b['y']+j*b['step'])*h.SX
    start=len(h.frames)
    align=l.get('align',4 if len(t)>(28 if n==140 and ind>=40 else 46) and '{' not in t and (j<len(b['lines'])-1 or not t.endswith(('.', '—'))) else 0)
    h.rich(t,h.LEFT+ind,y,h.BW-ind,h.BODY,align)
    for run in l.get('font_runs',[]):
     assert len(h.frames)==start+1
     o=h.frames[-1]['name'];s.selectText(t.index(run['text']),len(run['text']),o);s.setFont(h.FONT[run['font']],o);s.selectText(0,0,o);s.layoutText(o)
     if s.textOverflows(o) or s.getTextLines(o)!=1:
      scale=h.frames[-1]['scale']
      while (s.textOverflows(o) or s.getTextLines(o)!=1) and scale>85:
       scale*=.99;s.setTextScalingH(scale,o);s.layoutText(o)
      h.frames[-1]['scale']=scale
      if scale<85:h.fits.append(dict(name=o,scale=scale,text=t))
    for word in l.get('italic_words',[]):
     assert len(h.frames)==start+1,'Local italics expected in a plain line'
     o=h.frames[-1]['name'];s.selectText(t.index(word),len(word),o);s.setFont(h.FONT['Italic'],o);s.selectText(0,0,o)
    for token in l.get('small_digit_tokens',[]):
     assert len(h.frames)==start+1
     o=h.frames[-1]['name'];s.selectText(t.index(token)+1,len(token)-1,o);s.setFontSize(h.BODY*.75,o);s.selectText(0,0,o)

  for a in [a for a in A if a['leaf']==n]:
   x0,y0,x1,y1=a['crop'];cx=a['source_center']
   scale=min(h.SX,a.get('layout_max_width_points',h.W)/(x1-x0))
   geometry=a.get('layout_box_points',[h.W/2+(x0-cx)*scale,y0*h.SX,(x1-x0)*scale,(y1-y0)*scale])
   o=s.createImage(*geometry,'figure-'+str(a['figure']))
   s.loadImage(str(ROOT/'assets'/a['asset']),o);s.setScaleImageToFrame(True,True,o);s.setTextFlowMode(o,0)
  for y,t in p['captions']:h.center(t,y*h.SX,10.8)
  for legend in p['legends']:
   for j,t in enumerate(legend['lines']):
    o=h.rich(t,legend['x'],(legend['y']+j*legend['step'])*h.SX,legend['width'],legend['size'],align=legend.get('align',0))
    for word in legend.get('italic_words',[]):
     if word in t:s.selectText(t.index(word),len(word),o);s.setFont(h.FONT['Italic'],o);s.selectText(0,0,o)
    for token in legend.get('small_digit_tokens',[]):
     if token in t:s.selectText(t.index(token)+1,len(token)-1,o);s.setFontSize(legend['size']*.75,o);s.selectText(0,0,o)
  for x,y,t in p['subheads']:h.text(t,x,y*h.SX,300-x,10.8,'Italic')
  for v in p['vertical']:
   o=h.text(v['text'],v['x'],v['y']+13.5,v['width'],10.8,align=v['align'])
   s.setRotation(90,o,s.BASEPOINT_TOPLEFT);s.moveObjectAbs(v['x'],v['y'],o)
   h.frames[-1].update(rotation_degrees_counterclockwise=90,rotation_origin=[v['x'],v['y']])
  for v in p['positioned_text']:
   o=h.text(v['text'],v['x'],v['y']*h.SX,v['width'],v['size'],v.get('font','Roman'),align=v['align'])
   for word in v.get('italic_words',[]):
    s.selectText(v['text'].index(word),len(word),o);s.setFont(h.FONT['Italic'],o);s.selectText(0,0,o)
  for row in p.get('clearance_tables',[]):
   y=row['y']*h.SX;size=row['size'];font=row.get('label_font','Roman')
   h.text(row['label'],row['x'],y,row['label_width'],size,font)
   label=h.frames[-1];x=row['x']+h.measure(row['label'],size,font)*label['scale']/100+5
   while x+1<row['minimum_x']-8:
    dot=s.createEllipse(x,y-2,.5,.5);s.setFillColor('Black',dot);s.setLineColor('None',dot);x+=4
   h.text(row['minimum'],row['minimum_x'],y,row['minimum_width'],size)
   h.text(row['maximum'],row['maximum_x'],y,row['maximum_width'],size)
   for j,t in enumerate(row['desired']):h.text(t,row['desired_x'],y+j*row['desired_step']*h.SX,row['desired_width'],size,align=1)
  for v in p['native_rules']:h.rule(v['x'],v['y'],v['x2'],v['y2'],v['width'])
  for table in p['tables']:
   for j,(label,value) in enumerate(table['rows']):
    h.leader(label,value,(table['y']+j*table['step'])*h.SX,x=table['x'],w=table['width'],refwidth=table['refwidth'],size=10.8)
    s.setTextAlignment(s.ALIGN_LEFT,h.frames[-1]['name'])
 s.setRedraw(True)
 oldframes=json.loads((ROOT/'data/baseline_v07_native_frames.json').read_text());frames=oldframes+h.frames
 err=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
 if err:raise RuntimeError('Text layout errors: '+str(err))
 path=ROOT/R['sla'];s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
 err2=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1 or s.getAllText(f['name'])!=f['text']]
 if err2:raise RuntimeError('Reopen errors: '+str(err2))
 s.saveDocAs(str(path))
 pdf=s.PDFfile();pdf.file=str(ROOT/R['pdf']);pdf.pages=list(range(1,161));pdf.version=15;pdf.compress=True;pdf.compressmtd=2;pdf.quality=0;pdf.downsample=0;pdf.resolution=600;pdf.outdst=0;pdf.bookmarks=True;pdf.save();del pdf
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(scribus_version=s.scribus_version,pages=s.pageCount(),editable_text_frames=len(frames),new_text_frames=len(h.frames),new_fraction_rules=len(h.rules),overflow_before=err,overflow_after=err2,frames_below_85_percent=h.fits),indent=2))
 (ROOT/'data/native_frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
 s.closeDoc();(ROOT/'data/build_success.json').write_text(json.dumps(R,indent=2))
try:main()
except BaseException:
 (ROOT/'build_error.txt').write_text(traceback.format_exc());raise
finally:
 if os.environ.get('LIBERTY_BATCH')=='1':os._exit(0)
