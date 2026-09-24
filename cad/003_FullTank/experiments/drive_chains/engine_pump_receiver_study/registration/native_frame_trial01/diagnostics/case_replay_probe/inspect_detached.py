import json
from pathlib import Path
import FreeCAD as App
import Part
OUT=Path('/home/cyapp/MarkVIIILiberty/cad/003_FullTank/experiments/drive_chains/engine_pump_receiver_study/registration/native_frame_trial01/diagnostics/case_replay_probe')
def shape(n):
 s=Part.Shape();s.read(str(OUT/(n+'.brep')));return s
final=shape('final');original=shape('original');current=shape('current');new=shape('new')
data=[]
for s in final.Solids:
 b=s.BoundBox
 data.append(dict(volume=s.Volume,center=list(s.CenterOfMass),bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                  old_base_contact=s.distToShape(original)[0],new_base_contact=s.distToShape(new)[0],
                  missing_from_current=s.cut(current).Volume))
(OUT/'detached.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
