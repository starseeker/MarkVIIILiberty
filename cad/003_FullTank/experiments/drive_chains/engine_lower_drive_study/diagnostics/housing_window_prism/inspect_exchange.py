"""Diagnose the exact reason for housing STEP rejection without loosening checks."""
import json
from pathlib import Path
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty')
B=ROOT/'cad/003_FullTank/experiments/drive_chains/engine_lower_drive_study'
rows=[]
for key in ['housing_flywheel','housing_distributor']:
    shapes=[]
    for kind in ['native','step']:
        s=Part.Shape();s.read(str(B/'exchange_runtime/mass'/('Definitions_Def_EngineLowerDrive_'+key+'_'+kind+'.brep')))
        shapes.append(s)
    a,b=shapes;ta,tb=a.getTolerance(1),b.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
    ca,cb=a.cut(b,fuzzy),b.cut(a,fuzzy)
    edges=[]
    for n,e in enumerate(b.Edges):
        if e.getTolerance(1)>max(1e-7,ta)+1e-10:
            bb=e.BoundBox
            edges.append(dict(index=n,max_tolerance=e.getTolerance(1),curve=type(e.Curve).__name__,length=e.Length,
                              bounds=[getattr(bb,k) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax']]))
    rows.append(dict(part=key,native_tolerance_mm=ta,step_tolerance_mm=tb,fuzzy_tolerance_mm=fuzzy,
                     missing_faces=len(ca.Faces),added_faces=len(cb.Faces),missing_volume=ca.Volume,added_volume=cb.Volume,
                     increased_edges=edges))
    print(json.dumps(rows[-1],indent=2),flush=True)
(ROOT/'.work/engine-distribution/exchange_diagnosis.json').write_text(json.dumps(rows,indent=2)+'\n')
