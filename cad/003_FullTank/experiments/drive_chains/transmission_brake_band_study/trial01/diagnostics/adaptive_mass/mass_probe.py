import json,sys
from pathlib import Path
import FreeCAD as App
import Part
root=Path('/home/cyapp/MarkVIIILiberty/.work/transmission-brake-bands/probe01')
print('Mass/volume API:',[(n,getattr(Part.Shape,n).__doc__) for n in dir(Part.Shape) if any(w in n.lower() for w in ['mass','volume','center'])],flush=True)
for name in ['low_lining','track_lining','low_band','track_band']:
 a=Part.Shape();a.read(str(root/(name+'.brep')));b=Part.Shape();b.read(str(root/(name+'.step')))
 print(name,'native',a.Volume,list(a.Solids[0].CenterOfMass),'step',b.Volume,list(b.Solids[0].CenterOfMass),flush=True)
 for label,s in [('native',a),('step',b)]:
  t=s.copy().removeSplitter()
  print(label,'cleaned valid',t.isValid(),'tol',t.getTolerance(1),'vol',t.Volume,'com',list(t.Solids[0].CenterOfMass),flush=True)
  t.exportBrep(str(Path.cwd()/(name+'_'+label+'_cleaned.brep')))
