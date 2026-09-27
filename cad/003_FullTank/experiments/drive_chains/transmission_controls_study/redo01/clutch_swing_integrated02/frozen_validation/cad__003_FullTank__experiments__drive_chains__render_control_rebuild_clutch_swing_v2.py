"""Actual saved SH944/M581 parts; context and an explicitly cut keyway review."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(New=(.25,.46,.67),Casting=(.45,.57,.42),Key=(.78,.6,.29),Context=(.68,.68,.63))
selected=set(s.rows)|{n for n in parent.rows if any(v in n for v in ['ClutchBrake_Carrier','ClutchBrake_StopRod','PortRearHighRod','ClutchSupport_Aux','ClutchSupport_LeftBracket','EngineFrame_RearChannel','EngineSuspension_LeftBracket','PortCenterFoot','PortFootCenterJoint'])};items=[]
for n in sorted(selected):
 if n=='hull_floor_6':continue
 provider=s if n in s.rows else parent;shape=provider.world(n)
 system='Key' if 'ClutchSwingKey' in n else 'Casting' if 'ClutchSwingBracket' in n or 'ClutchSwing' in n and 'Link' in n else 'New' if n in s.report['new_occurrences'] else 'Context'
 items.append(dict(id=n,shape=shape,target=SimpleNamespace(Shape=shape),definition=n,system=system,representation='assembly'))
clip=Part.makeBox(3800,700,330,App.Vector(2300,-50,515));local=[]
for item in items:
 shape=item['shape'].common(clip)
 if shape.Faces:local.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape)))
shaded(local,s.folder/'isometric.svg',(-1,-1,.8),'Rear clutch linkage | SH944, M581 and source-length SH229A; estimated floor mounting')
shaded(local,s.folder/'plan.svg',(0,0,1),'Clutch routes | 93-inch center rod sets swing-bracket station; retained receivers')
pivot=App.Vector(*s.report['details']['pivot_world_mm']);detail=[v for v in items if v['id'].startswith('ClutchSwing') or v['id'].startswith('ClutchRearRodForward')]
shaded(detail,s.folder/'swing_detail.svg',(-1,-1,.8),'SH944 | separate keyed short/long links and complete source-sized fasteners')
# Remove the positive-X halves of each hub only for this review image.
keyitems=[];tool=Part.makeBox(100,200,200,pivot+App.Vector(0,-100,-100))
for item in detail:
 shape=item['shape']
 if item['id'] in ['ClutchSwingShortLink','ClutchSwingLongLink']:shape=shape.cut(tool)
 if item['id'].startswith('ClutchSwing') and any(v in item['id'] for v in ['Shaft','Key','Link']):keyitems.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape)))
shaded(keyitems,s.folder/'keyway_section.svg',(1,-1,.8),'Display cut only | axial Woodruff segments and actual shaft/hub receiving stock')
write(s.folder/'render_receipt.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),images={n:sha(s.folder/n) for n in ['isometric.png','plan.png','swing_detail.png','keyway_section.png']},scope='Actual saved shapes; local crops and explicit display-only hub section. No source camera fit or historical qualification.'))
