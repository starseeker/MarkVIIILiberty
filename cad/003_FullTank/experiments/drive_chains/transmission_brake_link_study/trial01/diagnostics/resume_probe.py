"""Read-only diagnosis of the interrupted M337 link candidate."""
from pathlib import Path
import hashlib,json
import FreeCAD as App
import Part
root=Path('/home/cyapp/MarkVIIILiberty');out=root/'cad/003_FullTank/experiments/drive_chains/transmission_brake_link_study/trial01'
m=json.loads((out/'isolated/manifest.json').read_text());r=json.loads((out/'report.json').read_text());q=json.loads((out/'independent_checks.json').read_text())
rows={v['name']:v for v in m['occurrences']}
def definition(name):
 f=Path(m['definitions'][name]['brep_path']);assert hashlib.file_digest(f.open('rb'),'sha256').hexdigest()==m['definitions'][name]['brep_sha256']
 s=Part.Shape();s.read(str(f));return s
cotter=definition('Def_BrakeLink_cotter');wire=r['cotter']['wire_radius_mm'];c=r['controls']
faces=[f for f in cotter.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-wire)<1e-7 and abs(abs(f.Surface.Axis.x)-1)<1e-7]
axes=sorted({(round(f.Surface.Center.y,7),round(f.Surface.Center.z,7)) for f in faces})
witnesses=[]
for sign in [-1,1]:
 leg=Part.makeCylinder(wire,r['cotter']['straight_length_mm'],App.Vector(r['cotter']['under_eye_y_mm'],0,sign*c['cotter_center_spacing']/2),App.Vector(1,0,0))
 missing=leg.cut(cotter);negative=cotter.cut(Part.makeBox(2,10,10,App.Vector(-1,-5,-5)))
 rejected=leg.cut(negative).Volume>1
 witnesses.append(dict(sign=sign,missing_mm3=missing.Volume,missing_faces=len(missing.Faces),cut_leg_negative_rejected=rejected))
assert len(axes)==2 and all(abs(v['missing_mm3'])<1e-5 and v['missing_faces']==0 and v['cut_leg_negative_rejected'] for v in witnesses)
collisions=[]
for pair in q['development_material_pairs']:
 if pair['passed']:continue
 def placed(name):
  row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
 common=placed(pair['first']).common(placed(pair['second']));b=common.BoundBox
 collisions.append(dict(**pair,intersection_bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
parent=root/r['source_native'];candidate=out/r['native_file']
assert hashlib.file_digest(parent.open('rb'),'sha256').hexdigest()==r['source_native_sha256']
assert hashlib.file_digest(candidate.open('rb'),'sha256').hexdigest()==r['native_sha256']
result=dict(date='2026-09-24',freecad=App.Version(),occ=Part.OCC_VERSION,readiness='Runtime and saved work recovered; candidate requires geometry revision before acceptance.',parent_native_sha256=r['source_native_sha256'],candidate_native_sha256=r['native_sha256'],previous_checker_terminal_exit_code=1,candidate_accepted=False,straight_cylindrical_face_count=len(faces),distinct_straight_leg_axes_yz_mm=axes,straight_leg_material_witnesses=witnesses,actual_interferences=collisions,next_step='Review lower M337/M348/M353 anchor geometry and source transverse placement jointly with the retained middle diaphragm. Preserve failed trial01. Do not cut the frame or shrink source dimensions merely to clear the candidate.')
f=root/'.work/transmission-brake-links/resume_readiness.json';f.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
