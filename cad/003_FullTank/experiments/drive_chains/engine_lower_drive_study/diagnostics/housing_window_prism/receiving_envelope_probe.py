"""Contrast rejected and current housing diameters against the entire native driver."""
import hashlib
import json
from pathlib import Path
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty')
B=ROOT/'cad/003_FullTank/experiments/drive_chains/engine_lower_drive_study'
p=B/'DrivetrainWithLowerDriveStudy.FCStd';d=App.openDocument(str(p))
try:
    driver=d.Def_EngineLowerDrive_driver.Shape
    checks=[]
    for radius in [37.,43.]:
        envelope=Part.makeCylinder(radius-.25,250,App.Vector(0,0,-250),App.Vector(0,0,1))
        excluded=driver.cut(envelope)
        checks.append(dict(housing_radius_mm=radius,clearance_allowance_mm=.25,
                           driver_material_outside_envelope_mm3=excluded.Volume,
                           passes=abs(excluded.Volume)<1e-5))
    assert not checks[0]['passes'] and checks[1]['passes']
    result=dict(native_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checks=checks,
                meaning='Necessary condition for gear passage through a complete cylindrical housing lug; actual case and whole removal path remain unqualified.')
    (ROOT/'.work/engine-distribution/receiving_envelope.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
finally:App.closeDocument(d.Name)
