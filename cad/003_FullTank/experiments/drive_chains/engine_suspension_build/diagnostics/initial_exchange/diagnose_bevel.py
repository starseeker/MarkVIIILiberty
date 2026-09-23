from pathlib import Path
import sys,subprocess,os,math,json
root=Path('/home/cyapp/MarkVIIILiberty');stage=root/'cad/003_FullTank';w=root/'.work/engine-suspension';sys.path.insert(0,str(stage))
from lib import runtime
if '--worker' not in sys.argv:
 sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(w/'diagnose')).returncode)
import FreeCAD,Part
h=stage/'experiments/drive_chains/engine_suspension_build/exchange_runtime/mass'
install=Path(os.environ['MARKVIII_RESOLVED_FREECAD']);exe=w/'diagnose_bevel'
subprocess.run(['g++','-std=c++17','-O2',str(w/'diagnose_bevel.cpp'),'-I'+str(install/'usr/include/opencascade'),'-L'+str(install/'usr/lib'),'-lTKTopAlgo','-lTKBRep','-lTKG3d','-lTKMath','-lTKernel','-o',str(exe)],check=True)
print('STEP DOC',Part.Shape.exportStep.__doc__,flush=True)
print('PART API',[n for n in dir(Part) if any(k in n.lower() for k in ['step','param','static','export'])],flush=True)
s=36;t=6.35;r=15.875/2+.1;m=math.tan(math.radians(6));area=s*s-math.pi*r*r;i=s**4/12-math.pi*r**4/4
print('ANALYTIC',area*t,[-m*i/(area*t),0,(t*t*area+m*m*i)/(2*area*t)],flush=True)
shapes=[]
for suffix in ['native','step']:
 p=h/('Definitions_Def_EngineSuspension_bevel_washer_'+suffix+'.brep');one=Part.Shape();one.read(str(p));shapes.append(one)
 print(suffix,'tolerance',one.getTolerance(1),'defaultVol',one.Volume,'area',one.Area,flush=True)
 subprocess.run([str(exe),str(p)],check=True)
 print('curves',[type(e.Curve).__name__ for e in one.Edges],flush=True)
a,b=shapes
print('fuzzy',len(a.cut(b,2e-7).Faces),len(b.cut(a,2e-7).Faces),flush=True)
runtime.close()
