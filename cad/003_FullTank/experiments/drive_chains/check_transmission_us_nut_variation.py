"""Verify revised nuts in the independently saved thicker-ear joint variation."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
variation=H/'transmission_controls_study/joint_stock_variation01';vr=read(variation/'report.json');vnative=variation/vr['native_file']
assert sha(vnative)==vr['native_sha256'] and read(variation/'independent_checks.json')['passed'] and read(variation/'exchange_checks.json')['passed']
assert vr['controls']['ear_stock']==5.2625
doc=App.openDocument(str(vnative));shapes={}
try:
    for name,spec in vr['specs'].items():
        if spec['role']=='nut':continue
        link=doc.getObject(name);s=link.LinkedObject.Shape.copy();pose=doc.getObject(spec['owner']).getGlobalPlacement().multiply(link.LinkPlacement)
        assert max(abs(x-y) for x,y in zip(pose.toMatrix().A,spec['frame']))<1e-7;s.Placement=pose;shapes[name]=s
finally:App.closeDocument(doc.Name)
d=m['definitions']['Def_USStdControlNut'];assert sha(d['brep_path'])==d['brep_sha256'];nut=Part.Shape();nut.read(d['brep_path']);rows={v['name']:v for v in m['occurrences']};checks=[]
def planes(s,q,n):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-q).dot(n))<1e-6]
for hand in ['Port','Starboard']:
    row=rows[hand+'HighSpeedBrakeControlNut'];pose=App.Placement(App.Matrix(*row['frame']));s=nut.copy();s.Placement=pose
    for name,t in shapes.items():
        if not name.startswith(hand):continue
        common=s.common(t);vol=sum(abs(v.Volume) for v in common.Solids)
        checks.append(dict(name=hand+' revised nut clears '+name,passed=(common.isNull() or common.isValid()) and vol<1e-5,common_mm3=vol))
    axis=pose.Rotation.multVec(App.Vector(0,0,1));area=sum(f.common(g).Area for f in planes(s,pose.Base,axis) for g in planes(shapes[hand+'Fork'],pose.Base,axis))
    checks.append(dict(name=hand+' revised nut retains thicker-fork seating',passed=area>200,area_mm2=area))
write(out/'variation_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=r['native_sha256'],variation_native_sha256=sha(vnative),variation_checks_sha256=sha(variation/'independent_checks.json'),variation_exchange_sha256=sha(variation/'exchange_checks.json'),checker_sha256=sha(Path(__file__)),scope='Revised source-size nut substituted into the existing+0.5mm ear-stock variation; all other varied joint geometry remains exactly as independently checked.'))
print(len(checks),'revised nut/ear variation checks passed',all(v['passed'] for v in checks));assert all(v['passed'] for v in checks)
