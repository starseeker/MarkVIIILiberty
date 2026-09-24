import json,sys
from pathlib import Path
import FreeCAD as App
import Part
root=Path('/home/cyapp/MarkVIIILiberty');sys.path.insert(0,str(root/'cad/003_FullTank'));from lib.mass_properties import AdaptiveMass;from lib.partitioned_mass import PartitionedMass
p=root/'.work/cad-pipeline/high_brake_front01/candidate';m=json.loads((p/'isolated/manifest.json').read_text());s=Part.Shape();s.read(m['definitions']['Def_HighBrakeFront_long_end']['brep_path'])
w=root/'.work/high-brake-front/long_end_mass_probe';mass=AdaptiveMass(w/'mass');part=PartitionedMass(mass,w/'partition')
r=part.measure(s);(w/'result.json').write_text(json.dumps(r,indent=2));print('Partitioned converged',r['converged'],r['volume_mm3'],r['centroid_mm'],flush=True)
