"""Independent positive and negative controls for a folded round-wire solid."""
import json,math
from pathlib import Path
import FreeCAD
import Part
import numpy as np
from scipy.spatial import cKDTree

base=Path(__file__).resolve().parent
for name,expected_pass in [('rejected_three_turns',False),('accepted_two_turns',True)]:
    path_shape=Part.Shape();path_shape.read(str(base/name/'centerline.brep'));path=path_shape.Wires[0]
    wire=Part.Shape();wire.read(str(base/name/'wire.brep'))
    points=np.array([list(p) for p in path.discretize(Distance=.1)])
    chords=np.linalg.norm(np.diff(points,axis=0),axis=1);stations=np.concatenate(([0.],np.cumsum(chords)))
    nearest=min(float(np.linalg.norm(points[i]-points[j])) for i,j in cKDTree(points).query_pairs(2.) if abs(stations[i]-stations[j])>4.)
    bend=min(e.Curve.Radius for e in path.Edges if isinstance(e.Curve,Part.Circle))
    expected=math.pi*(1.2065/2)**2*203.2;error=abs(wire.Volume-expected)
    passed=nearest>1.2065+.1 and max(chords)<=.10001 and bend>1.2065 and error<wire.Area*wire.getTolerance(1)
    result=dict(case=name,valid=wire.isValid(),solids=len(wire.Solids),stock_length_mm=path.Length,
                nearest_nonlocal_distance_mm=nearest,minimum_bend_mm=bend,stock_volume_error_mm3=error,passed=passed)
    print(json.dumps(result),flush=True)
    assert wire.isValid() and len(wire.Solids)==1 and abs(path.Length-203.2)<1e-5 and passed==expected_pass
