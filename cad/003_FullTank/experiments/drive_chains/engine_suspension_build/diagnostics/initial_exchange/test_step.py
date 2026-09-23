from pathlib import Path
import sys,subprocess,math
root=Path('/home/cyapp/MarkVIIILiberty');stage=root/'cad/003_FullTank';w=root/'.work/engine-suspension';sys.path.insert(0,str(stage))
from lib import runtime
if '--worker' not in sys.argv:
 sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(w/'step_trial')).returncode)
import FreeCAD,Part
from sys import path
path.insert(0,str(stage/'experiments/drive_chains'))
from case_joint_mass import calculator
mass=calculator(w/'step_trial/mass');src=stage/'experiments/drive_chains/engine_suspension_build/exchange_runtime/mass/Definitions_Def_EngineSuspension_bevel_washer_native.brep'
a=Part.Shape();a.read(str(src));ma=mass(a,'native')
print(Part.setStaticValue.__doc__,flush=True)
for mode in [0,1]:
 Part.setStaticValue('write.surfacecurve.mode',mode)
 p=w/'step_trial'/('mode%d.step'%mode);a.exportStep(str(p));b=Part.Shape();b.read(str(p));mb=mass(b,'mode%d'%mode)
 print('RESULT',mode,ma,mb,'tol',b.getTolerance(1),'valid',b.isValid(),'cut',a.cut(b).Volume,b.cut(a).Volume,flush=True)
runtime.close()
