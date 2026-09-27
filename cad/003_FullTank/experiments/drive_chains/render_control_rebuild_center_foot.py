"""Inspect actual saved center-foot geometry; floor clipping affects display only."""
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
COLORS.update(Bracket=(.42,.56,.45),Rocker=(.33,.53,.63),Rod=(.69,.51,.29),Rivet=(.65,.57,.37),
              Keeper=(.74,.66,.44),Fork=(.52,.58,.43),Pin=(.70,.60,.39),Cotter=(.73,.66,.49),Nut=(.55,.61,.60),
              Receiver=(.47,.53,.55),Floor=(.61,.63,.61))
items=[]
for name,row in saved.rows.items():
 if name=='hull_floor_6':continue
 s=saved.world(name);local=saved.definition(row['definition'])
 items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=local),definition=row['definition'],
                   system=r['specs'][name]['role'].title(),representation='assembly'))
for side in ['Port','Starboard']:
 center=pose(r['details'][side]['support_frame']).Base
 tool=Part.makeBox(210,230,20,center+App.Vector(-105,-115,-10))
 s=saved.world('hull_floor_6').common(tool)
 items.append(dict(id=side+'FloorDisplayPatch',shape=s,target=SimpleNamespace(Shape=s),definition=side+'FloorDisplayPatch',
                   system='Floor',representation='assembly'))
shaded(items,out/'isometric.svg',(-1,-1,.8),'Center foot controls | M641/M640 supports, full M578 rods; floor clipped for display')
detail=[v for v in items if v['id'].startswith('Port') and not any(w in v['id'] for w in ['RearFootRod','FootRearJoint','TrackHorizontalLever'])]
shaded(detail,out/'support_detail.svg',(-1,-1,.65),'Port support | riveted floor attachment and retained journal; estimated cast profiles')
section=[]
center=pose(r['details']['Port']['support_frame']).Base
clip=Part.makeBox(200,300,400,center+App.Vector(0,-150,-50))
for v in detail:
 s=v['shape'].cut(clip)
 if s.Faces:section.append(dict(v,shape=s,target=SimpleNamespace(Shape=s),definition=v['id']+'Section'))
shaded(section,out/'journal_section.svg',(1,0,.12),'Port journal section | display cut only; native material remains whole')
shaded(items,out/'plan.svg',(0,0,1),'Center foot controls | rear pin axes vertical, center pin axes transverse')
write(out/'render_receipt.json',dict(native_sha256=sha(saved.native),parent_native_sha256=r['parent_native_sha256'],
 renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(out/'isolated/manifest.json'),
 images={n:sha(out/n) for n in ['isometric.png','support_detail.png','journal_section.png','plan.png']},
 source_camera_refitted=False,
 scope='Actual saved prototype; two clipped floor patches and one display section. Source Plate6/HB92 have broken lengths, so no continuous whole-vehicle camera overlay is asserted.',
 historical_geometry_qualified=False))
print('Rendered complete rear foot connections, mounts, journal section and plan.',flush=True)
