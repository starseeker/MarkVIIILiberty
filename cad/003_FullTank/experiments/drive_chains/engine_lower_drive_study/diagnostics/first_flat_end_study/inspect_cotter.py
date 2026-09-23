import json
from pathlib import Path
import sys
import FreeCAD as App
ROOT=Path('/home/cyapp/MarkVIIILiberty');STAGE=ROOT/'cad/003_FullTank'
sys.path.insert(0,str(STAGE))
from lib.cad_build import leaves
p=STAGE/'experiments/drive_chains/engine_lower_drive_study/DrivetrainWithLowerDriveStudy.FCStd'
d=App.openDocument(str(p))
try:
    rows={r['id']:r for r in leaves(d.Root)}
    a=rows['EngineLowerDrive_ClampCotter1']['shape'];b=rows['EngineLowerDrive_DistributorHousing']['shape']
    s=a.common(b);s.Placement=d.EngineLowerDistributionDrive.getGlobalPlacement().inverse().multiply(s.Placement)
    bb=s.BoundBox
    result=dict(overlap_mm3=s.Volume,local_bounds={k:getattr(bb,k) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax']})
    (ROOT/'.work/engine-distribution/cotter_collision.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
finally:App.closeDocument(d.Name)
