import json,math
from pathlib import Path
import FreeCAD as App
import Part
import numpy as np
from scipy.spatial import cKDTree
root=Path('/home/cyapp/MarkVIIILiberty/.work/engine-oil-pump')
for name in ['relief_lock_variant_probe']:
 base=root/name;s=Part.Shape();s.read(str(base/'centerline.brep'));path=s.Wires[0];pts=np.array([list(p) for p in path.discretize(Distance=.1)]);chords=np.linalg.norm(np.diff(pts,axis=0),axis=1);stations=np.concatenate(([0.],np.cumsum(chords)));near=[float(np.linalg.norm(pts[i]-pts[j])) for i,j in cKDTree(pts).query_pairs(2.) if abs(stations[i]-stations[j])>4.]
 minimum=min(near);bend=min(e.Curve.Radius for e in path.Edges if isinstance(e.Curve,Part.Circle));wire=Part.Shape();f=base/'wire.brep'
 report=dict(path_length_mm=path.Length,maximum_chord_mm=float(max(chords)),minimum_nonlocal_center_distance_mm=minimum,minimum_bend_radius_mm=bend,self_clearance_passed=minimum>1.2065+.1 and max(chords)<.10001 and bend>1.2065)
 if f.exists():
  wire.read(str(f));expected=math.pi*(1.2065/2)**2*203.2;report.update(stock_volume_mm3=expected,actual_volume_mm3=wire.Volume,stock_volume_error_mm3=abs(wire.Volume-expected),stock_volume_passed=abs(wire.Volume-expected)<wire.Area*wire.getTolerance(1))
 (base/'path_checks.json').write_text(json.dumps(report,indent=2));print(name,report,flush=True)
