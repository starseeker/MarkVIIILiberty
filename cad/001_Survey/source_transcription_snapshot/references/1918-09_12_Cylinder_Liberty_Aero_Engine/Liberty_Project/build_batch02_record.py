"""Append batch 02 to the preserved batch-01 SLA. Run inside Scribus 1.6.x.
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
OLD=json.loads((ROOT/'data/batch01_release.json').read_text())
D=json.loads((ROOT/'data/batch02_transcription.json').read_text())
A=json.loads((ROOT/'data/batch02_artwork.json').read_text())
CAP={
22:[(None,1297,'Fig. 14.    Top Half of Crankcase.'),(None,2970,'Fig. 15.    Top Half of Crankcase, viewed from beneath.')],
23:[(16,2043,'Bottom Half of Crankcase.')],
26:[(18,1754,'Valve and Fittings.'),(19,2916,'Camshaft and Bearings.')],
27:[(20,1115,'Camcase.')],28:[(21,2336,'Valve Rockers.')],
29:[(22,2597,'Diagram of Distribution Gear.')],31:[(23,2964,'Water Pump (shown dismantled).')],
32:[(24,2197,'Broken View of Oil Pump Unit.')],
34:[(25,1593,'Diagram of Oil Pump unit, showing leads.','(N.B.—This sketch is purely diagrammatic.)')],
36:[(27,1620,'Plan View of Scavenge Pumps.'),(28,3004,'Plan View of Pressure Pump.')],
37:[(29,1353,'Cross Section of Pump Unit','(showing rear half).'),(30,2857,'Cross Section of Oil Pump Unit','(showing front half).')],
39:[(31,2014,'Front Main Bearing, showing oil leads.','Top: Bearing shell.','Bottom: Bearing housing.')],
40:[(32,2111,'Oil Connection to Camshaft.')]}
HEAD={25:[(2557,'VALVES.')],27:[(1311,'CAMSHAFTS AND VALVE GEAR.')],28:[(2544,'DISTRIBUTION GEAR.')],30:[(1979,'COOLING SYSTEM.')],32:[(456,'STARTER.')],33:[(639,'CHAPTER II.'),(2133,'OIL PUMPS.')],38:[(2035,'LUBRICATION OF THE MAIN AND BIG END'),(2121,'BEARINGS.')],39:[(774,'LUBRICATION OF THE GUDGEON PINS.'),(2328,'LUBRICATION OF THE CAMSHAFTS.')]}
def vertical(t,ox,oy,width,angle):
 o=h.text(t,ox,oy+13.5,width,10.8,align=1)
 s.setRotation(angle,o,s.BASEPOINT_TOPLEFT)
 s.moveObjectAbs(ox,oy,o)
 h.frames[-1].update(rotation_degrees_counterclockwise=angle,rotation_origin=[ox,oy])
 return o
def main():
 for p in ['build_error.txt','data/build_success.json']:
  if (ROOT/p).exists():(ROOT/p).unlink()
 missing=set(h.FONT.values())-set(s.getFontNames())
 if missing:raise RuntimeError('Install bundled OpenType fonts: '+str(missing))
 s.openDoc(str(ROOT/OLD['sla']));assert s.pageCount()==20
 s.setInfo('Ministry of Munitions; digital reconstruction','The Liberty 12-Cylinder Aero Engine Handbook (1918) — '+R['release_id'],'Batches 01–02: source scans 0001–0040, cover through printed page 38. Editable transcription and original-pixel figures. Provisional trim and typography.')
 s.setRedraw(False)
 for p in D['pages']:
  n=p['leaf'];s.newPage(-1);s.gotoPage(n)
  h.center(str(n-2),53,11)
  if n==33:h.center('Lubrication.',497*h.SX,21,'Bold')
  for y,t in HEAD.get(n,[]):h.center(t,y*h.SX,11.5)
  for b in p['blocks']:
   for j,l in enumerate(b['lines']):
    ind=l['indent']*h.SX;t=l['text'];y=(b['y']+j*b['step'])*h.SX
    h.rich(t,h.LEFT+ind,y,h.BW-ind,h.BODY,4 if len(t)>46 and '{' not in t and (j<len(b['lines'])-1 or not t.endswith(('.', '—'))) else 0)
  for a in [a for a in A if a['leaf']==n]:
   x0,y0,x1,y1=a['crop'];cx=a['source_center']
   o=s.createImage(h.W/2+(x0-cx)*h.SX,y0*h.SX,(x1-x0)*h.SX,(y1-y0)*h.SX,'figure-'+str(a['figure']))
   s.loadImage(str(ROOT/'assets'/a['asset']),o);s.setScaleImageToFrame(True,True,o);s.setTextFlowMode(o,0)
  for cap in CAP.get(n,[]):
   fig,yp,*ls=cap
   if fig is None:
    h.text(ls[0],15,yp*h.SX,366,10.4,align=1);continue
   h.center('Fig. '+str(fig)+'.',yp*h.SX,10.8)
   for k,t in enumerate(ls):
    offset=86+k*(54 if n==39 else 86)
    h.center(t,(yp+offset)*h.SX,10.8)
  if n==21:
   vertical('Fig. 13.',41,222,220,-90)
   vertical('Three-quarter Side View of Engine.',28,222,220,-90)
  if n==24:
   vertical('Fig. 17.',350,510,320,90)
   vertical('Bottom Half of Crankcase, with Crankshaft in position.',364,510,320,90)
  if n==35:
   vertical('Fig. 26.',332,519,320,90)
   vertical('Diagram of Lubrication System. (Purely diagrammatic).',346,519,320,90)
 s.setRedraw(True)
 oldframes=json.loads((ROOT/'data/batch01_native_frames.json').read_text());frames=oldframes+h.frames
 err=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
 if err:raise RuntimeError('Text layout errors: '+str(err))
 path=ROOT/R['sla'];s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
 err2=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1 or s.getAllText(f['name'])!=f['text']]
 if err2:raise RuntimeError('Reopen errors: '+str(err2))
 s.saveDocAs(str(path))
 pdf=s.PDFfile();pdf.file=str(ROOT/R['pdf']);pdf.pages=list(range(1,41));pdf.version=15;pdf.compress=True;pdf.compressmtd=2;pdf.quality=0;pdf.downsample=0;pdf.resolution=600;pdf.outdst=0;pdf.bookmarks=True;pdf.save();del pdf
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(scribus_version=s.scribus_version,pages=s.pageCount(),editable_text_frames=len(frames),new_text_frames=len(h.frames),new_fraction_rules=len(h.rules),overflow_before=err,overflow_after=err2,frames_below_85_percent=h.fits),indent=2))
 (ROOT/'data/native_frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
 s.closeDoc();(ROOT/'data/build_success.json').write_text(json.dumps(R,indent=2))
try:main()
except BaseException:
 (ROOT/'build_error.txt').write_text(traceback.format_exc());raise
finally:
 if os.environ.get('LIBERTY_BATCH')=='1':os._exit(0)
