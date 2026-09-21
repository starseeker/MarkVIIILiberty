from pathlib import Path
import sys,subprocess
repo=Path.cwd();stage=repo/'cad/003_FullTank';here=stage/'experiments/drive_chains';out=repo/'.work/air-pump-installation'
sys.path[:0]=[str(stage),str(here)]
from lib import runtime
if '--worker' not in sys.argv:
 with (out/'probe_operations.log').open('w') as log:
  sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out/'operations_probe'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
 App,Gui=runtime.start_gui();import Part
 from air_pressure_pump_parts import cyl,xc,moved
 old=Part.Shape();old.read(str(out/'trial02_before_receiver_revision/inputs/parent_housing.brep'))
 for style in ['round','faceted']:
  s=old.copy();print(style,'initial',s.getTolerance(1),flush=True)
  for sign in [1,-1]:
   if style=='round':boss=moved(cyl(16,50,88),(340,sign*58,0))
   else:
    points=[(-16,-12),(-12,-16),(12,-16),(16,-12),(16,12),(12,16),(-12,16),(-16,12)]
    v=[App.Vector(340+x,sign*58+y,50) for x,y in points]
    boss=Part.Face(Part.makePolygon(v+v[:1])).extrude(App.Vector(0,0,38))
   boss=boss.cut(xc(74.7125,323,357));print('boss',boss.getTolerance(1),flush=True)
   s=s.fuse(boss);print('fuse',sign,s.getTolerance(1),flush=True)
   s=s.cut(moved(cyl(6.5,67.8,89),(340,sign*58,0)));print('bore',sign,s.getTolerance(1),flush=True)
  print('refine',s.removeSplitter().getTolerance(1),flush=True)
finally:runtime.close()
