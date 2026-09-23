import sys,json
from pathlib import Path
import FreeCAD as App
import Part
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(h))
from engine_oil_pump_lock import route,extend
r=json.loads((h/'engine_oil_pump_hardware_study/report.json').read_text());c=r['controls'];d=r['datums']
c.update(relief_lock_wire_diameter=1.2065,relief_lock_stock_length=203.2,relief_lock_pair_gap=.24,relief_lock_tail_turns=2,relief_lock_cage_hole_x=8.5,relief_lock_bend_radius=1.65,relief_lock_hole_radius=.8,upper_nut_access_radius=8.5)
path,details=route(c,d);print(json.dumps(details,indent=2),flush=True)
base=root/'.work/engine-oil-pump/relief_lock_variant_probe';base.mkdir(exist_ok=True)
(base/'controls.json').write_text(json.dumps(c,indent=2));path.exportBrep(str(base/'centerline.brep'))
doc=App.openDocument(str(h/'engine_oil_pump_hardware_study/OilPump.FCStd'));p={key:doc.getObject('Def_'+key).Shape.copy() for key in r['definition_order']};occ=list(r['occurrences']);extend(c,p,occ,r['groups'],d)
wire=p['relief_lock_wire'];wire.exportBrep(str(base/'wire.brep'));checks=[]
for row in occ[:-1]:
 s=p[row['key']].copy();s.Placement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation'])).multiply(s.Placement)
 if not wire.BoundBox.intersect(s.BoundBox):continue
 v=abs(wire.common(s).Volume);gap=wire.distToShape(s)[0];checks.append(dict(part=row['name'],overlap_mm3=v,gap_mm=gap,passed=v<1e-5));print(checks[-1],flush=True)
for key in ['relief_cage','lower_body']:p[key].exportBrep(str(base/(key+'.brep')))
(base/'report.json').write_text(json.dumps(dict(passed=all(x['passed'] for x in checks),checks=checks,details=details,datums=d),indent=2))
print('DONE',all(x['passed'] for x in checks),flush=True)
