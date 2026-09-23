from pathlib import Path
import json,math
import FreeCAD as App,Part
w=Path('/home/cyapp/MarkVIIILiberty/.work/engine-crankshaft');out=w/'cage_step_probe';out.mkdir(exist_ok=True)
V=App.Vector;X=V(1,0,0);Z=V(0,0,1)
for path in w.glob('bad_step_*.brep'):
 s=Part.Shape();s.read(str(path));b=s.optimalBoundingBox(False);print('BAD_BOUNDS',path.name,[getattr(b,k) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax']],flush=True)
print(Part.makeSphere.__doc__,flush=True)
Part.setStaticValue('write.surfacecurve.mode',1);rows=[]
for radius in [6.,5.8]:
 for axis,label in [(Z,'Z'),(X,'X')]:
  s=Part.makeCylinder(54.5,3,V(-1.5,0,0),X).cut(Part.makeCylinder(40.5,5,V(-2.5,0,0),X))
  for i in range(20):
   a=i*2*math.pi/20;s=s.cut(Part.makeSphere(radius+.15,V(0,47.5*math.cos(a),47.5*math.sin(a)),axis))
  for scope,offset in [('definition',V()),('installed',V(2943.8055512712617,0,849.2335104357661))]:
   source=s.copy();source.translate(offset);key=f'{radius}_{label}_{scope}';path=out/(key+'.step');source.exportStep(str(path));back=Part.Shape();back.read(str(path))
   record=dict(key=key,native_valid=source.isValid(),step_valid=back.isValid(),native_volume=source.Volume,step_volume=back.Volume,solids=len(back.Solids),native_faces=len(source.Faces),step_faces=len(back.Faces))
   if back.isValid():record.update(missing=source.cut(back).Volume,added=back.cut(source).Volume)
   rows.append(record);print(json.dumps(record),flush=True)
(w/'cage_step_probe.json').write_text(json.dumps(rows,indent=2)+'\n')
