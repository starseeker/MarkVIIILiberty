"""Views of actual saved long controls and their nearest mechanical context."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(New=(.25,.46,.67),Receiver=(.48,.59,.42),Context=(.69,.68,.63),High=(.69,.48,.25))
selected=set(s.rows)|{n for n in parent.rows if any(v in n for v in ['RearHighRod','RearFootRod','CenterFootRivet','CenterFootBracket','CenterFootKeeper','FootCenterJoint','IntermediateSupport','IntermediateShaft','EngineSuspension_','EngineWaterPump_BodyCasting'])}
items=[]
for n in sorted(selected):
 provider=s if n in s.rows else parent;shape=provider.world(n)
 system='High' if 'RearHighRod' in n else 'Receiver' if 'Rocker' in n or 'Bracket' in n else 'New' if n in s.report['new_occurrences'] else 'Context'
 items.append(dict(id=n,shape=shape,target=SimpleNamespace(Shape=shape),definition=n,system=system,representation='assembly'))
shaded(items,s.folder/'isometric.svg',(-1,-1,.8),'Complete low-speed and center-foot routes | saved parts; estimated paths')
shaded(items,s.folder/'plan.svg',(0,0,1),'Plan | low-speed rods remain outside engine supports before converging')
for stem,lo,size,direction,title in [('foot_detail',(3200,350,527),(350,260,203),(-1,-1,1),'Center-foot receiver | both physical clevis joints'),('route_detail',(2700,-400,570),(1500,550,170),(-1,-1,.6),'Starboard engine corridor | water pump and support clearance')]:
 clip=Part.makeBox(*size,App.Vector(*lo));detail=[]
 for item in items:
  shape=item['shape'].common(clip)
  if shape.Faces:detail.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape)))
 shaded(detail,s.folder/(stem+'.svg'),direction,title)
write(s.folder/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),images={n:sha(s.folder/n) for n in ['isometric.png','plan.png','foot_detail.png','route_detail.png']},scope='Saved geometry, cropped detail views. No whole-length source registration or historical-accuracy claim.'))
