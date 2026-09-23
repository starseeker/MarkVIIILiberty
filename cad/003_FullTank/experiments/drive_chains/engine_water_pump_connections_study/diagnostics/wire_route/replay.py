"""Replay a crossing rejection and the corrected source-length wire route."""
from pathlib import Path
import json,sys
import FreeCAD as App
import Part
import numpy as np
from scipy.spatial import cKDTree
base=Path(__file__).resolve().parent;paths=[Path(p) for p in sys.argv[1:]] or [base/'crossing_centerline.brep',base/'corrected_centerline.brep'];results=[]
assert len(paths)==2
for label,filename in zip(['crossing','corrected'],paths):
 shape=Part.Shape();shape.read(str(filename));path=shape.Wires[0];points=np.array([list(p) for p in path.discretize(Distance=.1)]);length=np.concatenate(([0.],np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))))
 minimum=min(float(np.linalg.norm(points[i]-points[j])) for i,j in cKDTree(points).query_pairs(2.) if abs(length[i]-length[j])>4.)
 results.append(dict(label=label,length_mm=path.Length,sample_spacing_mm=.1,nonlocal_arc_separation_mm=4.,minimum_sampled_center_distance_mm=minimum,diameter_mm=1.2065,clears=minimum>1.2065+.1))
print(json.dumps(results,indent=2),flush=True);Path('clearance_checks.json').write_text(json.dumps(dict(passed=not results[0]['clears'] and results[1]['clears'],results=results),indent=2)+'\n');assert not results[0]['clears'] and results[1]['clears']
