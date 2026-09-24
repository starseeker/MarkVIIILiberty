from pathlib import Path
import sys,json
ROOT=Path('/home/cyapp/MarkVIIILiberty');sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
import FreeCAD as App
import Part
from lib.mass_properties import AdaptiveMass
from lib.partitioned_mass import PartitionedMass
from lib.evidence import read,write
out=ROOT/'.work/high-brake-joint/anchor_mass_probe';out.mkdir(exist_ok=True)
m=read(ROOT/'.work/cad-pipeline/high_brake_joints01/candidate/isolated/manifest.json');s=Part.Shape();s.read(m['definitions']['Def_HighBrake_anchor_end']['brep_path'])
a=AdaptiveMass(out/'adaptive');p=PartitionedMass(a,out/'partitioned')
r=p.measure(s,App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),90)))
write(out/'result.json',r);print({k:r[k] for k in ['converged','volume_mm3','centroid_mm']},flush=True);assert r['converged']
