"""Review the real uninstalled driver shaft and its provisional end-retainer layout."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(Shaft=(.37,.51,.64),Nut=(.51,.55,.43),Keeper=(.8,.64,.34));items=[]
for n in s.rows:
 shape=s.world(n);system='Keeper' if 'Keeper' in n else 'Nut' if 'Nut' in n else 'Shaft';items.append(dict(id=n,shape=shape,target=SimpleNamespace(Shape=shape),definition=n,system=system,representation='assembly'))
shaded(items,s.folder/'isometric.svg',(1,-1,.8),'Uninstalled driver study | M782, two shared M313 nuts and two source-sized keepers')
center=App.Vector(*s.report['details']['controls']['center']);end=s.report['details']['shaft_half_length_mm'];clip=Part.makeBox(100,85,90,center+App.Vector(-50,end-85,-45));local=[]
for item in items:
 shape=item['shape'].common(clip)
 if shape.Faces:local.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape)))
shaded(local,s.folder/'end_detail.svg',(1,1,.8),'Provisional end arrangement | reduced journal, source-length keeper; mounting pending')
write(s.folder/'render_receipt.json',dict(native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),images={n:sha(s.folder/n) for n in ['isometric.png','end_detail.png']},scope='Uninstalled part study. No source-camera fit, floor mounting or full assembly promotion.'))
