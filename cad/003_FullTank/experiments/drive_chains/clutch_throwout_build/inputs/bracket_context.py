from pathlib import Path
import json,sys
ROOT=Path('/home/cyapp/MarkVIIILiberty');STAGE=ROOT/'cad/003_FullTank';HERE=STAGE/'experiments/drive_chains'
sys.path[:0]=[str(STAGE),str(HERE)]
import FreeCAD as A,Part
from lib.cad_build import leaves
from lib.worker import check_build
from lib import runtime
from lib.evidence import write
try:
 d=A.openDocument(str(HERE/'clutch_throwout_build/TransmissionWithClutchThrowout.FCStd'))
 origin=d.TransmissionCore.Placement.Base
 r=json.loads((HERE/'clutch_throwout_build/report.json').read_text());c=r['controls']
 shaft=origin+A.Vector(c['shaft_center_x'],0,c['shaft_center_z'])
 standard=check_build(STAGE/'build');t=A.openDocument(standard['build']['top_document']);items=leaves(t.Root)
 rows=[]
 box=Part.makeBox(260,650,180,A.Vector(shaft.x-130,-325,500)).BoundBox
 for i in items:
  b=i['shape'].copy().cleaned().BoundBox
  if b.intersect(box):
   rows.append(dict(id=i['id'],representation=i['representation'],bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],shaft_axis_to_material_mm=i['shape'].distToShape(Part.Vertex(shaft))[0]))
 result=dict(shaft_axis=list(shaft),nearby_standard=rows,standard_native_hashes=standard['native_hashes'],note='Geometric context only. No bracket foot station or load-bearing attachment established.')
 write(ROOT/'.work/clutch-throwout/bracket_context.json',result)
 print(json.dumps(result,indent=2),flush=True)
finally:runtime.close()
