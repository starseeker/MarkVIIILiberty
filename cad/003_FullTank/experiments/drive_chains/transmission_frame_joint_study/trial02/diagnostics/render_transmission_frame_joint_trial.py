"""Render the actual saved frame and its hypothesized formed connections."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
import FreeCAD as App
import Part
from lib.cad_build import COLORS
from lib.visual_review import shaded
COLORS.update(Frame=(.70,.55,.36),Fastener=(.85,.68,.31),Bearing=(.51,.59,.68))
rows={v['name']:v for v in m['occurrences']};cache={}
def item(name,role):
    row=rows[name];key=row['definition']
    if key not in cache:
        d=m['definitions'][key];p=Path(d['brep_path']);assert sha(p)==d['brep_sha256']
        s=Part.Shape();s.read(str(p));cache[key]=SimpleNamespace(Shape=s)
    target=cache[key];shape=target.Shape.copy();shape.Placement=App.Placement(App.Matrix(*row['frame']))
    return dict(id=name,shape=shape,target=target,definition=key,system=role,representation='assembly')
frame=[];context=[]
for name,row in rows.items():
    if 'TransmissionMountingFrame' in row['owners']:
        frame.append(item(name,'Fastener' if name in r['expected_new_occurrences'] else 'Frame'))
    elif 'FixedTransmissionBearings' in row['owners'] or 'BracketMounts' in ''.join(row['owners']):
        context.append(item(name,'Bearing'))
detail=[];clip=Part.makeBox(260,300,240,App.Vector(1370,445,1030))
for obj in frame:
    s=obj['shape'].common(clip)
    if s.Faces:detail.append(dict(obj,shape=s,target=SimpleNamespace(Shape=s),definition=obj['id']+'_display_crop'))
views=[('isometric',frame,context,(-1,-.8,.6),'Frame connections trial | formed returns, diaphragm overlap and 32 channel rivets'),
       ('frame_front',frame,[],(1,-.25,.35),'Frame interior | mechanical joint hypothesis; remaining hardware unpopulated'),
       ('gusset_joint',detail,[],(-1,-.7,.65),'Upper inner corner | display crop; formed gusset and four source-sized rivets')]
for name,selected,outlined,direction,title in views:
    shaded(selected,out/(name+'.svg'),direction,title,context=outlined)
    print('Rendered',name,flush=True)
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],manifest_sha256=sha(out/'isolated/manifest.json'),
    renderer_sha256=sha(Path(__file__)),images={name+'.png':sha(out/(name+'.png')) for name,*_ in views},
    views={name:dict(direction=direction,solid_ids=[v['id'] for v in selected],context_ids=[v['id'] for v in outlined]) for name,selected,outlined,direction,title in views},
    display_only_crop=True,historical_joint_layout_qualified=False,installation_qualified=False))
