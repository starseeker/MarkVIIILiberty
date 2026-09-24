import json,math,sys
from pathlib import Path
ROOT=Path('/home/cyapp/MarkVIIILiberty');sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
import FreeCAD as App
import Part
from lib.mass_properties import AdaptiveMass
p=ROOT/'cad/003_FullTank/experiments/drive_chains/transmission_brake_band_study/trial01'
m=json.loads((p/'isolated/manifest.json').read_text());rows={v['name']:v for v in m['occurrences']}
ex=json.loads((p/'exchange_checks.json').read_text());s=Part.Shape();s.read(str(p/'BrakeBandsInstallation.step'));imported=s.Solids
mass=AdaptiveMass(Path.cwd()/'runtime');results=[]
for r in ex['checks']:
 if r['scope']!='Installation' or r['name'] not in ['PortTransmissionCore_brake_case','StarboardTransmissionCore_brake_case','PortTransmissionOutput_drum','StarboardTransmissionOutput_drum']:continue
 row=rows[r['name']];one=Part.Shape();one.read(m['definitions'][row['definition']]['brep_path']);pose=App.Placement(App.Matrix(*row['frame']));one.Placement=pose
 two=imported[r['imported_solid_index']].copy()
 for variant in ['translate','full_inverse']:
  a,b=one.copy(),two.copy()
  transform=App.Placement(-pose.Base,App.Rotation()) if variant=='translate' else pose.inverse()
  a.Placement=transform.multiply(a.Placement);b.Placement=transform.multiply(b.Placement)
  ma,mb=mass.measure(a),mass.measure(b)
  result=dict(name=r['name'],variant=variant,volume_error=abs(ma['volume_mm3']-mb['volume_mm3']),
   centroid_error=math.dist(ma['centroid_mm'],mb['centroid_mm']),native=ma,step=mb)
  results.append(result);print(r['name'],variant,result['volume_error'],result['centroid_error'],flush=True)
Path('centered_mass_probe.json').write_text(json.dumps(results,indent=2))
