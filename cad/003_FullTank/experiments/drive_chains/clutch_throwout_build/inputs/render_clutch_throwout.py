"""Review saved clutch throwout geometry with source context and a bearing section."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent; STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_throwout_build');p.add_argument('--worker',action='store_true')
p.add_argument('--views',nargs='+',choices=['throwout','receiver_fit','isometric','bearing_section','side_view'])
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    args=[sys.executable,__file__,'--candidate',str(base),'--worker']
    if a.views:args+=['--views',*a.views]
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run(args,env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    r=read(base/'report.json');native=base/'TransmissionWithClutchThrowout.FCStd';assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(Fork=(.30,.49,.60),Shaft=(.61,.64,.66),Bearing=(.70,.72,.72),Cage=(.69,.52,.29),Context=(.48,.52,.53))
    previous=read(out/'render_receipt.json') if (out/'render_receipt.json').exists() else {}
    if a.views:assert previous.get('native_sha256')==sha(native),'Partial rerender requires matching native receipt'
    generators=previous.get('image_generators',{n:previous.get('renderer_sha256') for n in previous.get('images',{})})
    def draw(names,name,title,direction,clip=None):
        if a.views and name not in a.views:return
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy();s.translate(-origin)
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if n.startswith('ClutchThrowout_'):
                color='Shaft'
                if 'Lever' in n:color='Fork'
                elif 'BearingCage' in n:color='Cage'
                elif 'Bearing' in n or 'Ball' in n:color='Bearing'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.035)
        generators[name+'.png']=sha(Path(__file__))
        print('Rendered',name,flush=True)
    new=r['new_ids']
    draw(new,'throwout','Clutch release mechanism | brackets, retention and controls pending',(1,1,.6))
    draw(new+['FrontClutch_Coupling'],'receiver_fit','Source-sized bearings between coupling flanges | static freeplay',(1,-1,.5))
    context=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_',
        'ClutchThrust_','ClutchCone_','ClutchRetention_','ClutchDrum_','ClutchStopBand_','AirPump_','PumpMount_','InputHousing_'))]
    draw(context+new,'isometric','Clutch release development | shaft brackets and brake linkage pending',(1,1,.6))
    bearing=[n for n in new if n.startswith('ClutchThrowout_Left') and ('Bearing' in n or 'Ball' in n)]
    c=r['controls'];x=c['bearing_center_x'];y=c['bearing_center_y']
    clip=Part.makeBox(50,30,90,App.Vector(x,y-15,-45))
    draw(bearing,'bearing_section','SKF1207 envelope | estimated two-row internals',(-1,-1,.35),clip)
    draw(new+['FrontClutch_Coupling'],'side_view','Conditional shaft drop | longitudinal source registration unresolved',(0,1,0))
    source=HERE/'clutch_stop_band_build/source_review'
    for name in ['SNL2_full.png','SNL2_clutch_context.png']:(out/name).write_bytes((source/name).read_bytes())
    names=['throwout','receiver_fit','isometric','bearing_section','side_view','SNL2_full','SNL2_clutch_context']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        images={n+'.png':sha(out/(n+'.png')) for n in names},image_generators=generators,
        source_scales='independent; no calibrated overlay or historical-fit claim'))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Clutch release development</title>'
        '<style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}</style>'
        '<h1>Clutch release development</h1><p>Source-sized bearing envelopes; estimated internals, pins, forks and shaft. Brackets and complete linkage pending.</p>'
        +''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
finally:
    runtime.close()
