"""Expose the actual complete mounting stack on an upward-facing display section."""
import argparse
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.visual_review import shaded
from lib.cad_build import COLORS
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);out=s.folder/'section02';out.mkdir(exist_ok=False)
x,z=s.report['details']['joints'][0]['center_xz_world_mm'];box=Part.makeBox(36,88,20,App.Vector(x-18,-330,z-20));items=[]
COLORS.update(Quadrant=(.33,.52,.67),Support=(.43,.48,.53),Bolt=(.70,.60,.36),Distance=(.67,.40,.22),Nut=(.74,.66,.47),Lock=(.58,.60,.64))
names=['DriverReverseQuadrant','DriverStarboardSupportPlate']+['DriverReverseQuadrantForward'+r for r in ['Bolt','Distance','Lock','Nut']]
for name in names:
 q=s.world(name).common(box)
 if q.Faces:
  role='Quadrant' if name=='DriverReverseQuadrant' else 'Support' if name=='DriverStarboardSupportPlate' else name.removeprefix('DriverReverseQuadrantForward')
  items.append(dict(id=name+'Section',definition=name+'Section',shape=q,target=SimpleNamespace(Shape=q),system=role,representation='assembly'))
shaded(items,out/'bolt_section.svg',(-1,1,.9),'Actual mounting stack | full bolt through quadrant, distance piece, support, lock and nut | display section only')
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),images={p.name:sha(p) for p in out.glob('*.png')},cut_box_mm=[x-18,-330,z-20,36,88,20],scope='Lower half retained so the actual axial section faces the viewer. Original physical geometry unchanged. Supersedes the obscured visual01 bolt-section camera for section inspection.'))
