"""Render saved intermediate receivers with transparent-purpose floor clipping."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,read,write,sha
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();saved=Saved(a.candidate);r=saved.report;c=r['details']['controls'];out=saved.folder
validate_native_bindings(dict(native_file=str(saved.native),render_occurrences=list(saved.rows),landmarks=[]),saved.manifest)
COLORS.update(Bracket=(.42,.56,.45),Rocker=(.33,.53,.63),Shaft=(.61,.64,.62),Strip=(.52,.53,.46),
    Keeper=(.74,.66,.44),Screw=(.70,.60,.39),Floor=(.61,.63,.61))
items=[];origin=App.Vector(*r['details']['shaft_origin_world_mm'])
for name,row in saved.rows.items():
    if name=='hull_floor_3':continue
    s=saved.world(name);local=saved.definition(row['definition'])
    items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=local),definition=row['definition'],
        system=r['specs'][name]['role'].title(),representation='assembly'))
clip=Part.makeBox(180,720,20,App.Vector(origin.x-90,-360,c['floor_top']-10))
floor=saved.world('hull_floor_3').common(clip)
items.append(dict(id='FloorDisplayPatch',shape=floor,target=SimpleNamespace(Shape=floor),definition='FloorDisplayPatch',system='Floor',representation='assembly'))
shaded(items,out/'isometric.svg',(-1,-1,.8),'Intermediate controls | eight single-ended rockers; estimated M639/M3019 floor mounting')
shaded(items,out/'front.svg',(-1,0,.08),'Intermediate controls | one reverse, two low, two high, two foot and one clutch rocker')
shaded(items,out/'plan.svg',(0,0,1),'Intermediate shaft | actual three bearing stations and six cap-screw receivers')
detail=[v for v in items if v['id'].startswith('IntermediateShaftMount2') or v['id'] in ['IntermediateControlShaft','RearIntermediateSupportStrip','FrontIntermediateSupportStrip','FloorDisplayPatch']]
section=[]
box=Part.makeBox(300,25,400,App.Vector(origin.x-150,-25,c['floor_top']-20))
for v in detail:
    s=v['shape'].common(box)
    if s.Faces:section.append(dict(v,shape=s,target=SimpleNamespace(Shape=s),definition=v['id']+'Section'))
shaded(section,out/'mount_section.svg',(0,1,.08),'Center mount section | source-length screw from floor underside into actual blind receiver')
write(out/'render_receipt.json',dict(native_sha256=sha(saved.native),parent_native_sha256=r['parent_native_sha256'],
    renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(out/'isolated/manifest.json'),
    images={n:sha(out/n) for n in ['isometric.png','front.png','plan.png','mount_section.png']},
    source_camera_refitted=False,scope='Actual saved prototype, display-only floor patch and section. Dimensional source fit not asserted; mounting hypothesis provisional.'))
print('Rendered intermediate receiver gang and physical screw-grip section.',flush=True)
