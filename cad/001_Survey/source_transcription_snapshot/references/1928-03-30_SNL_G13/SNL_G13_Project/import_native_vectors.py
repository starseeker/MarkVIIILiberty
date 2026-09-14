#!/usr/bin/env python3
"""Inside Scribus: import each preferred SVG into an isolated 6x9-inch document.

The main transcription document is not reserialized. integrate_native_vectors.py
transplants these named groups after validation. Hybrid pixel regions use ordinary
linked PNGs because the tested Scribus importer ignores embedded data URIs.
"""
from pathlib import Path
import scribus as s,json,os,traceback,tempfile
ROOT=Path(__file__).resolve().parent;D=ROOT/'restoration/native'
try:
 (D/'error.txt').unlink(missing_ok=True)
 placements=json.loads((D/'placements.json').read_text());checks={}
 for n,r in placements.items():
  if os.environ.get('SNL_IMPORT_ONLY') and n not in os.environ['SNL_IMPORT_ONLY'].split(','):continue
  s.newDocument((432,648),(0,0,0,0),s.PORTRAIT,1,s.UNIT_POINTS,s.NOFACINGPAGES,s.FIRSTPAGERIGHT,1);s.setRedraw(False)
  s.placeSVG(str(ROOT/r['import_svg']),0,0);name=s.getSelectedObject();w,h=s.getSize(name)
  print('import canvas',n,w,h,r['pixel_size'],flush=True)
  assert max(abs(w-r['pixel_size'][0]),abs(h-r['pixel_size'][1]))<.05  # SVG contour bounds may extend by hundredths of a pixel
  s.scaleGroup(r['width']/w,name)
  # Scribus API rotation is counterclockwise; SLA ROT is clockwise.
  s.rotateObjectAbs(-r['rotation'],name,s.BASEPOINT_TOPLEFT)
  s.moveObjectAbs(r['page_x'],r['page_y'],name)
  checks[n]={'size':s.getSize(name),'position':s.getPosition(name),'rotation':s.getRotation(name),'type':s.getObjectType(name)}
  print(n,checks[n],flush=True)
  s.saveDocAs(str(D/f'p{n}-native.sla'))
  with tempfile.TemporaryDirectory(prefix='snl-native-proof-') as temp:
   target=Path(temp)/'proof.pdf';pdf=s.PDFfile();pdf.file=str(target);pdf.pages=[1];pdf.version=15;pdf.quality=0;pdf.compress=1;pdf.compressmtd=2;pdf.downsample=0;pdf.save()
   (D/f'p{n}-native.pdf').write_bytes(target.read_bytes())
  s.closeDoc()
 (D/'import_validation.json').write_text(json.dumps(checks,indent=2))
except Exception:(D/'error.txt').write_text(traceback.format_exc())
finally:os._exit(0)
