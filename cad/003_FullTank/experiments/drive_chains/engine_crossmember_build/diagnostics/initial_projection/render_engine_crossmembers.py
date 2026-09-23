"""Review saved crossmember geometry and its source context without a GUI."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_crossmember_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'DrivetrainWithEngineCrossmembers.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};c=r['controls']
    COLORS.update(Channel=(.40,.54,.62),Cleat=(.65,.51,.31),Gusset=(.55,.62,.42),Rivet=(.66,.68,.70),Floor=(.65,.65,.58),Context=(.49,.53,.54))
    def draw(names,name,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy()
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if n.startswith('hull_floor_'):color='Floor'
            elif n.startswith('EngineFrame_'):
                color='Rivet'
                for kind in ['Channel','Cleat','Gusset']:
                    if n.endswith(kind):color=kind
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.06)
        print('Rendered',name,flush=True)
    frame=r['new_ids'];floors=['hull_floor_5','hull_floor_6','hull_floor_7']
    clutch=[n for n in byid if n.startswith(('ClutchBrake_','ClutchStopBand_','ClutchSupport_','ClutchThrowout_',
        'FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','ClutchThrust_','ClutchCone_','ClutchRetention_','ClutchDrum_'))]
    draw(frame+floors+clutch,'isometric','Engine crossmembers and clutch | development; engine rails and mounts pending',(1,1,.7))
    draw(frame,'crossmembers','M181 front cleat / M180 rear gussets | estimated profiles; source-sized rivets',(-1,1,.8))
    draw(frame+floors,'underside','14 direct floor rivets | inherited floor envelope and clutch holes preserved',(-1,1,-.6))
    front=Part.makeBox(300,200,180,App.Vector(c['front_x']-60,-100,c['floor_top']-30))
    draw(frame+floors,'front_joint','M189 cleat and two 5/8in rivets | channel/floor review section',(1,1,.65),front)
    rear=Part.makeBox(280,170,180,App.Vector(c['rear_x']-60,c['gusset_y']-85,c['floor_top']-30))
    draw(frame+floors,'rear_joint','M186 gusset | two channel and two floor rivets',(1,1,.6),rear)
    draw(frame+floors+clutch,'side_view','Engine forward at left | conditional SNL2 mounting stations',(0,1,0))
    from PIL import Image,ImageDraw
    source=HERE/'clutch_stop_brake_sources/p277_foldout_original.jpg'
    crop=Image.open(source).crop((5440,1980,7250,3270)).convert('RGB')
    crop.save(out/'SNL2_engine_context.png')
    # Fixed inherited calibration: no translation, rescaling or fit to this candidate.
    overlay=crop.copy();drawing=ImageDraw.Draw(overlay)
    def project(v):
        return ((1760-v.x/6.0269942196531785)*11072/2048-5440,
                (660-v.z/5.928273244781783)*5456/1009-1980)
    overlay_ids=frame+floors+[n for n in byid if n in ['ClutchDrive_drum','ClutchDrum_Flywheel']]
    for n in overlay_ids:
        for edge in byid[n]['shape'].Edges:
            pts=[project(v) for v in edge.discretize(Deflection=.3)]
            if len(pts)>1:drawing.line(pts,fill='#087dc6',width=2)
    drawing.rectangle((0,0,1810,42),fill='#f5f3eb')
    drawing.text((12,12),'Blue: saved native edges through fixed SNL2 calibration; no fitting. Profiles remain estimates.',fill='#14405d')
    overlay.save(out/'source_overlay.png')
    names=['isometric','crossmembers','underside','front_joint','rear_joint','side_view','SNL2_engine_context','source_overlay']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        images={n+'.png':sha(out/(n+'.png')) for n in names},source_sha256=sha(source),source_crop=[5440,1980,7250,3270],
        projected_occurrences=overlay_ids,
        source_comparison='Fixed inherited SNL2 calibration, no fitting. Conditional stations only; no historical profile qualification. Review clipping is display-only.'))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Engine crossmembers</title>'
        '<style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}</style>'
        '<h1>Engine crossmember development</h1><p>11 nested channel parts and14 direct floor rivets. Remaining suspension brackets, rails, packings, bevel washers, engine attachments and shared hull-angle joints are pending. Profiles and stations are estimated.</p>'
        +''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
finally:
    runtime.close()
