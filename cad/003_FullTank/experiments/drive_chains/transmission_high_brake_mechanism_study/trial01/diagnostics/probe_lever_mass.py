"""Diagnose whole-face integration failures without changing native/STEP material."""
import sys,json
from pathlib import Path
import FreeCAD as A
import Part
R=Path('/home/cyapp/MarkVIIILiberty');S=R/'cad/003_FullTank';sys.path.insert(0,str(S))
from lib.mass_properties import AdaptiveMass
from lib.partitioned_mass import PartitionedMass
from lib.step_matching import StepSolidMatcher
from lib.evidence import read,write,sha
p=R/'.work/cad-pipeline/high_brake_mechanism02/candidate';out=R/'.work/high-brake-mechanism/lever_mass';out.mkdir(exist_ok=True)
m=read(p/'isolated/manifest.json');mass=AdaptiveMass(out/'mass');partition=PartitionedMass(mass,out/'partitioned');step=Part.Shape();step.read(str(p/'HighBrakeMechanismDefinitions.step'));matcher=StepSolidMatcher(step.Solids);records=[]
for role in ['left','right']:
 key='Def_HighBrakeMechanism_lever_'+role;d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);i,exported=matcher.pop(s)
 for scope,shape in [('native',s),('step',exported)]:
  initial=mass.measure(shape);print(role,scope,'whole',initial['converged'],flush=True)
  measured=partition.measure(shape);row=dict(role=role,scope=scope,whole=initial,partitioned=measured);records.append(row);write(out/'results.json',records);print(role,scope,'partition',measured['converged'],measured['volume_convergence_mm3'],flush=True)
assert all(v['partitioned']['converged'] for v in records)
