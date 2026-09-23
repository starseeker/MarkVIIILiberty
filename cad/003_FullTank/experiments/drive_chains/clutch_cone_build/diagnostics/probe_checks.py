from pathlib import Path
import json,sys
ROOT=Path('/home/cyapp/MarkVIIILiberty');stage=ROOT/'cad/003_FullTank';sys.path.insert(0,str(stage))
import FreeCAD as A,Part
from lib.cad_build import leaves
out=stage/'experiments/drive_chains/clutch_cone_build';r=json.loads((out/'report.json').read_text())
doc=A.openDocument(str(out/'TransmissionWithClutchCone.FCStd'));items={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
s={}
for n,i in items.items():s[n]=i['shape'].copy();s[n].translate(-origin)
spring=s['ClutchCone_Spring1'];bb=spring.optimalBoundingBox(False)
print('SPRING BOUND',bb.XMin,bb.XMax,flush=True)
for label,x,w in [('rear',880,r['datums']['ring_front']-880),('front',r['datums']['spring_front'],30)]:
 clip=Part.makeBox(w,60,60,A.Vector(x,75,30));common=spring.common(clip)
 print(label,'outside volume',common.Volume,'faces',len(common.Faces),flush=True)
for name in ['ClutchCone_LiningRivet08','ClutchCone_LiningRivet31']:
 j=next(a for a in r['datums']['rivet_joints'] if a['name']==name);p=A.Vector(*j['base'])+A.Vector(*j['normal'])
 print(name,list(p),flush=True)
 for target in [name,'ClutchCone_cone','ClutchCone_lining']:
  shape=s[target];b=Part.makeSphere(.01,p)
  print(target,'inside',shape.isInside(p,1e-7,False),'distance',Part.Vertex(p).distToShape(shape)[0],'small ball common',shape.common(b).Volume,flush=True)
A.closeDocument(doc.Name)
