from pathlib import Path
import json,math
import FreeCAD as App,Part
w=Path('/home/cyapp/MarkVIIILiberty/.work/engine-crankshaft');V=App.Vector;X=V(1,0,0);Z=V(0,0,1)
results=[]
for r in [6.,5.8]:
 shapes={}
 for axis,label in [(X,'X'),(Z,'Z')]:
  s=Part.makeCylinder(54.5,3,V(-1.5,0,0),X).cut(Part.makeCylinder(40.5,5,V(-2.5,0,0),X))
  for i in range(20):
   a=i*2*math.pi/20;s=s.cut(Part.makeSphere(r+.15,V(0,47.5*math.cos(a),47.5*math.sin(a)),axis))
  assert s.isValid() and len(s.Solids)==1;shapes[label]=s
 added=shapes['X'].cut(shapes['Z']);removed=shapes['Z'].cut(shapes['X'])
 analytic=math.pi*(54.5**2-40.5**2)*3-20*math.pi*((r+.15)**2*3-3**3/12)
 result=dict(ball_radius=r,added_volume_mm3=added.Volume,removed_volume_mm3=removed.Volume,added_faces=len(added.Faces),removed_faces=len(removed.Faces),analytic_volume_mm3=analytic,
  x_default_integration_mm3=shapes['X'].Volume,z_default_integration_mm3=shapes['Z'].Volume,note='Default native volume integration differs by parametrization; bidirectional material comparison and analytic band volume separate geometry from numerical integration.')
 results.append(result);print(json.dumps(result),flush=True)
 assert abs(added.Volume)<1e-5 and abs(removed.Volume)<1e-5 and not added.Faces and not removed.Faces
(w/'cage_material_probe.json').write_text(json.dumps(dict(passed=True,freecad=App.Version(),occ=Part.OCC_VERSION,results=results),indent=2)+'\n')
