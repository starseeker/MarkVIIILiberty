from pathlib import Path
import sys,subprocess
repo=Path.cwd();stage=repo/'cad/003_FullTank';here=stage/'experiments/drive_chains';out=repo/'.work/air-pump-installation'
sys.path[:0]=[str(stage),str(here)]
from lib import runtime
from lib.evidence import read
if '--worker' not in sys.argv:
 with (out/'probe_bosses.log').open('w') as log:
  sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out/'boss_probe'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
 App,Gui=runtime.start_gui();import Part
 from air_pump_mount_parts import build
 c=read(here/'air_pump_mount_controls.json')['controls'];pc=read(here/'air_pressure_pump_controls.json')['controls'];pc['foot_hole_y']=c['pump_foot_hole_y'];pc['foot_extension']=c['pump_foot_extension']
 old=[]
 for key in ['cover','housing']:
  s=Part.Shape();s.read(str(out/'trial02_before_receiver_revision/inputs'/('parent_'+key+'.brep')));old.append(s)
 print('PARENT tolerances',[(k,s.getTolerance(1)) for k,s in zip(['cover','housing'],old)],flush=True)
 parts,occ,rev,d=build(c,pc,*old)
 for k,s in rev.items():
  print(k,s.isValid(),len(s.Solids),'tolerance',s.getTolerance(1),flush=True)

  for j,e in enumerate(s.Edges):
   if e.getTolerance(1)>1e-4:print('HIGH EDGE',j,str(e.Curve),str(e.BoundBox),e.getTolerance(1),flush=True)
  s.exportStep(str(out/(k+'_boss_probe.step')))
  t=Part.Shape();t.read(str(out/(k+'_boss_probe.step')))
  print('STEP',k,'tol',t.getTolerance(1),'raw',s.cut(t).Volume,t.cut(s).Volume,flush=True)
finally:runtime.close()
