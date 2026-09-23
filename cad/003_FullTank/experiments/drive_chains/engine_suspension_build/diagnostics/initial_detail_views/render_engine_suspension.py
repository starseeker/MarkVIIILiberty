"""Saved-native suspension review and fixed SNL2 source projection."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_suspension_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'DrivetrainWithEngineSuspension.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};c=r['controls'];cc=r['crossmember_controls'];d=r['datums']
    COLORS.update(Channel=(.40,.54,.62),Rail=(.43,.60,.69),Bracket=(.57,.65,.43),Packing=(.67,.49,.29),Hardware=(.66,.68,.70),Floor=(.65,.65,.58),Context=(.49,.53,.54))
    def draw(names,name,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy()
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if n.startswith('hull_floor_'):color='Floor'
            elif n.startswith(('EngineFrame_','EngineSuspension_')):
                color='Hardware'
                if n.endswith('Rail'):color='Rail'
                elif n.endswith(('Bracket','Gusset')):color='Bracket'
                elif n.endswith(('Packing','Cleat')) or 'Bevel' in n:color='Packing'
                elif n.endswith('Channel'):color='Channel'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.06)
        print('Rendered',name,flush=True)
    frame=[n for n in byid if n.startswith(('EngineFrame_','EngineSuspension_'))];floors=['hull_floor_5','hull_floor_6','hull_floor_7']
    clutch=[n for n in byid if n.startswith(('ClutchBrake_','ClutchStopBand_','ClutchSupport_','ClutchThrowout_',
        'FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','ClutchThrust_','ClutchCone_','ClutchRetention_','ClutchDrum_'))]
    draw(frame+floors+clutch,'isometric','Engine support inventory and clutch | static development; engine interfaces pending',(1,1,.7))
    draw(frame,'suspension','72 catalogue support children +14 floor rivets | profiles and joint arrangement inferred',(-1,1,.8))
    front=Part.makeBox(300,600,430,App.Vector(cc['front_x']-60,-300,cc['floor_top']-20))
    draw(frame+floors,'front_mount','M184 yoke, M187 packing, M189 cleat | proposed longitudinal pivot and mixed rail fasteners',(1,1,.7),front)
    rear=Part.makeBox(260,220,420,App.Vector(cc['rear_x']-100,c['rail_half_spacing']-110,cc['floor_top']-20))
    draw(frame+floors,'rear_mount','M182 double-point bracket | four rail bolts and two base bolts',(1,1,.6),rear)
    # Half-section through one rear base bolt reveals the sloping washer seat.
    bevel=Part.makeBox(110,65,130,App.Vector(cc['rear_x']-48,c['rail_half_spacing']+c['rear_base_bolt_y'][1],cc['floor_top']+30))
    draw(frame,'bevel_section','Rear base half-section | M190 inferred tapered-channel seat; nominal thread envelopes',(-1,1,.45),bevel)
    draw(frame+floors,'front_end','Front suspension end view |17in conditional engine mounting-row spacing',(1,0,0),front)
    draw(frame+floors+clutch,'side_view','Engine forward at left | source-sized support hardware and conditional engine plane',(0,1,0))
    from PIL import Image,ImageDraw
    source=HERE/'clutch_stop_brake_sources/p277_foldout_original.jpg'
    crop=Image.open(source).crop((5440,1980,7250,3270)).convert('RGB');crop.save(out/'SNL2_engine_context.png')
    overlay=crop.copy();drawing=ImageDraw.Draw(overlay)
    def project(v):return ((1760-v.x/6.0269942196531785)*11072/2048-5440,(660-v.z/5.928273244781783)*5456/1009-1980)
    projection=frame+floors+['ClutchDrum_flywheel']
    for n in projection:
        for edge in byid[n]['shape'].Edges:
            pts=[project(v) for v in edge.discretize(Deflection=.3)]
            if len(pts)>1:drawing.line(pts,fill='#087dc6',width=2)
    drawing.rectangle((0,0,1810,42),fill='#f5f3eb')
    drawing.text((12,12),'Blue: saved native edges through fixed SNL2 calibration; no fitting. Engine interfaces are conditional.',fill='#14405d')
    overlay.save(out/'source_overlay.png')
    names=['isometric','suspension','front_mount','rear_mount','bevel_section','front_end','side_view','SNL2_engine_context','source_overlay']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in names},source_sha256=sha(source),source_crop=[5440,1980,7250,3270],projected_occurrences=projection,
        source_comparison='Fixed inherited SNL2 calibration without fitting. Aircraft interface transfer, cast profiles, rail attachment and channel taper remain hypotheses. Display sections do not modify saved parts.'))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Engine suspension development</title>'
        '<style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}</style>'
        '<h1>Engine suspension development</h1><p>The72 support-assembly children and14 direct floor rivets are populated. Castings and joint arrangement remain estimated. Engine case receivers,12 rail bolt sets and7 shared hull-angle rivets are pending; no complete tank-engine installation is claimed.</p>'
        +''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
finally:
    runtime.close()
