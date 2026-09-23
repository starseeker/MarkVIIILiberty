import sys,json,math
from pathlib import Path
root=Path('/home/cyapp/MarkVIIILiberty');sys.path[:0]=[str(root/'cad/003_FullTank')]
import FreeCAD as A, Part
from lib.cad_build import leaves
base=root/'cad/003_FullTank/experiments/drive_chains/clutch_thrust_build'
r=json.loads((base/'report.json').read_text());doc=A.openDocument(str(base/'TransmissionWithClutchThrust.FCStd'));doc.recompute();by={i['id']:i['shape'] for i in leaves(doc.Root)}
origin=doc.TransmissionCore.Placement.Base;rows=[]
for n in [1,6,11,16]:
 name=f'ClutchThrust_Ball{n:02}';ball=by[name];center=ball.Solids[0].CenterOfMass
 for race,sign in [('ClutchStack_thrust',-1),('ClutchThrust_Stop',1)]:
  contact=center+A.Vector(sign*3.175,0,0);vertex=Part.Vertex(contact);shift=ball.copy();shift.translate(A.Vector(sign*.01,0,0))
  row=dict(ball=name,race=race,whole_shape_distance=ball.distToShape(by[race])[0],point_race_distance=vertex.distToShape(by[race])[0],point_ball_distance=vertex.distToShape(ball)[0],penetrating_overlap=shift.common(by[race]).Volume,material_beyond=by[race].isInside(contact+A.Vector(sign*.01,0,0),1e-7,False))
  rows.append(row)
print(json.dumps(rows,indent=2));(root/'.work/clutch-thrust/contact_probe.json').write_text(json.dumps(rows,indent=2)+'\n')
A.closeDocument(doc.Name)
