"""Measure unchanged saved native/STEP case at successively tighter GK requests."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path('/home/cyapp/MarkVIIILiberty');STAGE=ROOT/'cad/003_FullTank';sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
from lib.kronrod_mass import KronrodMass
import FreeCAD as App
import Part
out=Path(__file__).resolve().parent;candidate=out.parents[1]
doc=App.openDocument(str(candidate/'ReceivingWebStudy.FCStd'))
try:native=doc.Def_case.Shape.copy()
finally:App.closeDocument(doc.Name)
step=Part.Shape();step.read(str(candidate/'ReceivingWebDefinitions.step'));step=max(step.Solids,key=lambda s:s.Volume)
mass=KronrodMass(out/'refinement_runtime')
source=out/'refined_probe.cpp';text=(STAGE/'lib/occt_kronrod_mass.cpp').read_text();assert text.count('{1e-10,1e-12}')==1
source.write_text(text.replace('{1e-10,1e-12}','{1e-11,1e-12,1e-13,1e-14}'))
command=mass.provenance['compile_command'][:];command[4]=str(source);command[-1]=str(out/'refinement_runtime/refined_probe')
subprocess.run(command,env=mass.environment,check=True,capture_output=True,text=True)
results={}
for label,shape in [('native',native),('step',step)]:
 path=out/(label+'_refinement_input.brep');shape.exportBrep(str(path))
 results[label]=json.loads(subprocess.check_output([command[-1],str(path)],env=mass.environment,text=True));print(label,results[label],flush=True)
write(out/'refinement_measurements.json',dict(results=results,source_sha256=sha(source),binary_sha256=sha(Path(command[-1])),compile_command=command))
