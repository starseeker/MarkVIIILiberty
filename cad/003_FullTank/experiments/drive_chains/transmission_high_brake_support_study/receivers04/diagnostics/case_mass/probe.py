"""Span-aware mass probe after reported-error failures on unchanged case BReps."""
import json,sys
from pathlib import Path
ROOT=Path('/home/cyapp/MarkVIIILiberty');STAGE=ROOT/'cad/003_FullTank';sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
from lib.kronrod_mass import KronrodMass
out=Path(__file__).resolve().parent;candidate=out.parents[1]
r=read(candidate/'report.json');native=candidate/'ReceivingWebStudy.FCStd';assert sha(native)==r['prototype_native_sha256']
doc=App.openDocument(str(native))
try:
 definition=doc.Def_case.Shape.copy();installed=definition.copy();installed.Placement=doc.Case.LinkPlacement
finally:App.closeDocument(doc.Name)
mass=KronrodMass(out/'runtime');results=[]
for scope,shape in [('Definitions',definition),('Installed',installed)]:
 path=candidate/('ReceivingWeb'+scope+'.step');step=Part.Shape();step.read(str(path));solid=max(step.Solids,key=lambda s:s.Volume)
 a,b=mass.measure(shape),mass.measure(solid);results.append(dict(scope=scope,native=a,step=b))
 print(scope,a['converged'],b['converged'],flush=True)
write(out/'measurements.json',dict(native_sha256=sha(native),probe_sha256=sha(Path(__file__)),provenance=mass.provenance,results=results))
