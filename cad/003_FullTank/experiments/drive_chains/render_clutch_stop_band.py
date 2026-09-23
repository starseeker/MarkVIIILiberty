"""Render saved band geometry and retain full source context for visual review."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_stop_band_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from PIL import Image,ImageDraw,ImageFont
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    r=read(base/'report.json');native=base/'TransmissionWithClutchStopBand.FCStd'
    assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(Band=(.37,.48,.53),Lining=(.45,.31,.21),Copper=(.77,.46,.25),Steel=(.64,.67,.65),Context=(.48,.52,.53))
    def draw(names,name,title,direction,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy();s.translate(-origin)
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if n=='ClutchStopBand_band':color='Band'
            elif n=='ClutchStopBand_lining':color='Lining'
            elif n.startswith('ClutchStopBand_LiningRivet'):color='Copper'
            elif n.startswith('ClutchStopBand_FoldRivet'):color='Steel'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.035)
        print('Rendered',name,flush=True)
    band=r['new_ids']
    draw(band,'band','M4158 band and M4159 lining | anchor and actuator still required',(1,.7,-.65))
    draw(band+['ClutchDrive_drum','ClutchDrive_box','ClutchDrive_belt'],'drum_fit',
         'Development brake band on source-sized drum | opening clock inferred',(1,1,-.55))
    context=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_',
        'ClutchThrust_','ClutchCone_','ClutchRetention_','ClutchDrum_','AirPump_','PumpMount_','InputHousing_'))]
    draw(context+band,'isometric','Clutch-stop band development | linkage and anchor pending',(1,1,.6))
    clip=Part.makeBox(100,160,200,App.Vector(510,-160,-190))
    draw(band,'returned_eye','Inferred rolled pin ears and riveted return | saved native section',(-1,-1,-.4),clip)
    draw(band+['ClutchDrive_drum'],'end_view','Drum and lining clearance | actual native end view',(1,0,0))
    source=HERE/'clutch_stop_brake_sources/p277_foldout_original.jpg'
    im=Image.open(source).convert('RGB');im.thumbnail((2200,1100));im.save(out/'SNL2_full.png')
    original=Image.open(source).convert('RGB');original.crop((6643,2346,7972,3219)).save(out/'SNL2_clutch_context.png')
    notes=[
        'The full SNL2 original was inspected before the viewing crop; crop pixels are unchanged.',
        'Band stock, returned eye, rivet layout and bottom opening are inferred; this figure does not resolve them.',
        'Printed drum diameter9.25in; lining2in wide,3/16in thick,27-3/4in cut length.',
        'The sharper source places the transverse throwout shaft lower than the earlier visual reading.',
        'Anchor, six anchor rivets, pin/eyebolt and operating linkage remain required. No complete brake claim.',
        'Source and native images have independent scales; no calibrated overlay or historical-fit claim.'
    ]
    images=['band','drum_fit','isometric','returned_eye','end_view','SNL2_full','SNL2_clutch_context']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        source_sha256=sha(source),crop_bounds=[6643,2346,7972,3219],deflection_mm=.035,
        notes=notes,image_hashes={n+'.png':sha(out/(n+'.png')) for n in images}))
    (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch stop band development</title>'
        '<style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}</style>'
        '<h1>Clutch stop band development</h1>'+''.join('<p>'+v+'</p>' for v in notes)
        +''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in images)+'<p>Native hash: '+sha(native)+'</p></html>')
finally:
    runtime.close()
