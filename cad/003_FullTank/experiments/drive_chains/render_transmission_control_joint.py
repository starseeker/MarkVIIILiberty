"""Render the saved joint, preserving canonical meshes and fixed view directions."""
import argparse,sys
from pathlib import Path
from types import SimpleNamespace
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.visual_review import shaded
from lib.cad_build import COLORS
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
parent=H/'transmission_high_brake_support_study/integrated_upper01';m=read(parent/'isolated/manifest.json');rows={v['name']:v for v in m['occurrences']}
doc=App.openDocument(str(native));items=[]
COLORS.update(Control=(.72,.49,.27),Hardware=(.65,.68,.72),Receiver=(.48,.56,.60))
try:
    for name,spec in r['specs'].items():
        link=doc.getObject(name);target=link.LinkedObject.Shape.copy();pose=doc.getObject(spec['owner']).getGlobalPlacement().multiply(link.LinkPlacement)
        s=target.copy();s.Placement=pose
        items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=target),definition=spec['role'],system='Control' if spec['role']=='fork' else 'Hardware',representation='assembly'))
finally:App.closeDocument(doc.Name)
context=[]
for hand in ['Port','Starboard']:
    for side in ['Left','Right']:
        name=hand+'HighSpeedBrakeLever'+side;row=rows[name];d=m['definitions'][row['definition']];assert sha(d['brep_path'])==d['brep_sha256']
        target=Part.Shape();target.read(d['brep_path']);s=target.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
        context.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=target),definition=row['definition'],system='Receiver',representation='assembly'))
shaded(items,out/'joint_isometric.svg',(1,-1,.45),'Rear high-speed control joints | M569B / M568A interpretation',context=context)
port=[v for v in items if v['id'].startswith('Port')];clip=Part.makeBox(120,100,100,App.Vector(2035,175,560));details=[]
for item in context[:2]:
    s=item['shape'].common(clip)
    # A display cut has its own identity; never reuse a whole-part mesh key.
    details.append(dict(id=item['id']+'DisplayCut',shape=s,target=SimpleNamespace(Shape=s),definition=item['id']+'DisplayCut',system='Receiver',representation='assembly'))
shaded(port+details,out/'joint_detail.svg',(1,-1,.45),'Rear fork, pin, split pin and shared plain nut | receiver shown cut')
shaded(port+details,out/'joint_retention.svg',(1,1,.45),'Rear control joint | cotter retention and receiver display cut')
write(out/'render_receipt.json',dict(native_sha256=sha(native),parent_native_sha256=r['parent_native_sha256'],renderer_sha256=sha(Path(__file__)),
    images={v.name:sha(v) for v in [out/'joint_isometric.png',out/'joint_detail.png',out/'joint_retention.png']},camera_refit=False,
    scope='Saved prototype geometry. The close-up cuts only displayed receiver stock. No historical camera registration is claimed.'))
