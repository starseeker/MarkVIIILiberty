import sys,subprocess,json,shutil
from pathlib import Path
import FreeCAD as A
import Part
R=Path('/home/cyapp/MarkVIIILiberty');sys.path.insert(0,str(R/'cad/003_FullTank'))
from lib.mass_properties import AdaptiveMass
from lib.step_matching import StepSolidMatcher
from lib.evidence import read,write,sha
out=R/'.work/high-brake-mechanism/lever_gk';out.mkdir();source=R/'.work/transmission-brake-front/mass-gk-probe/mass_probe.cpp';shutil.copy2(source,out/'mass_probe.cpp');mass=AdaptiveMass(out/'mass');root=mass.root;binary=out/'probe'
command=['g++','-std=c++17','-O2','-I'+str(root/'usr/include/opencascade'),str(out/'mass_probe.cpp'),'-L'+str(root/'usr/lib'),'-lTKTopAlgo','-lTKBRep','-lTKG3d','-lTKMath','-lTKernel','-o',str(binary)]
subprocess.run(command,env=mass.environment,check=True,capture_output=True)
p=R/'.work/cad-pipeline/high_brake_mechanism02/candidate';m=read(p/'isolated/manifest.json');step=Part.Shape();step.read(str(p/'HighBrakeMechanismDefinitions.step'));matcher=StepSolidMatcher(step.Solids);results=[]
for role in ['left','right']:
 d=m['definitions']['Def_HighBrakeMechanism_lever_'+role];s=Part.Shape();s.read(d['brep_path']);i,t=matcher.pop(s)
 for label,shape in [('native',s),('step',t)]:
  f=out/(role+'_'+label+'.brep');shape.exportBrep(str(f));v=json.loads(subprocess.check_output([str(binary),str(f)],env=mass.environment,text=True));results.append(dict(role=role,scope=label,brep_sha256=sha(f),result=v));write(out/'results.json',results);print(role,label,[(a['method'],a['requested_error'],a['reported_error'],a['volume']) for a in v['results']],flush=True)
write(out/'provenance.json',dict(source_sha256=sha(out/'mass_probe.cpp'),binary_sha256=sha(binary),compile_command=command,adaptive=mass.provenance))
