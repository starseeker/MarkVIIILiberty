from pathlib import Path
import sys,json,math,subprocess
ROOT=Path('/home/cyapp/MarkVIIILiberty');HERE=ROOT/'cad/003_FullTank/experiments/drive_chains'
sys.path[:0]=[str(HERE),str(HERE.parents[1])]
from lib import runtime
if '--worker' not in sys.argv:
 with (ROOT/'.work/front-clutch/diagnose_spring.log').open('w') as log:
  sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(ROOT/'.work/front-clutch/diagnostic_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
App,Gui=runtime.start_gui()
try:
 import Part
 from lib.cad_build import leaves
 from front_clutch_parts import spring
 base=HERE/'front_clutch_build'
 doc=App.openDocument(str(base/'TransmissionWithFrontClutch.FCStd'));doc.recompute()
 items={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
 c=json.loads((base/'report.json').read_text())['controls']
 shapes={}
 for k in ['Spring','UpperFlange','LowerFlange','Coupling']:
  shapes[k]=items['FrontClutch_'+k]['shape'].copy();shapes[k].translate(-origin)
  print(k,'placed/local',shapes[k].BoundBox,'definition',items['FrontClutch_'+k]['target'].Shape.BoundBox,flush=True)
 s=shapes['Spring']
 print('ground faces',[(type(f.Surface).__name__,f.Area,str(f.BoundBox)) for f in s.Faces if type(f.Surface).__name__=='Plane'],flush=True)
 slab=Part.makeBox(c['spring_length'],400,400,App.Vector(c['spring_rear_seat'],-200,-200))
 remainder=s.cut(slab)
 print('outside actual seats',len(remainder.Faces),remainder.Volume,flush=True)
 for angle in [-18]:
  q=s.copy();q.rotate(App.Vector(),App.Vector(1,0,0),angle)
  print('phase',angle,[(k,q.distToShape(shapes[k])[0],q.common(shapes[k]).Volume) for k in ['UpperFlange','LowerFlange','Coupling']],flush=True)
 alt=dict(c);alt['spring_inside_radius']-=alt['spring_wire_radius'];q,_,_=spring(alt)
 print('alternative',q.BoundBox,q.isValid(),len(q.Solids),flush=True)
 for label,other in [('local',shapes['Coupling']),('target',items['FrontClutch_Coupling']['target'].Shape)]:
  common=q.common(other)
  print('alternate overlap',label,common.Volume,len(common.Solids),common.isValid(),q.distToShape(other)[0],flush=True)
finally:runtime.close()
