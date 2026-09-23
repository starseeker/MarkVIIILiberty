"""Inspect saved support/auxiliary geometry and source context; no physical cuts."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_support_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'TransmissionWithClutchSupports.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(Support=(.39,.48,.39),Lever=(.30,.49,.60),Hardware=(.68,.70,.71),Floor=(.65,.65,.58),Context=(.49,.53,.54))
    def draw(names,name,title,direction,floor_patch=False,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy();s.translate(-origin)
            if n=='hull_floor_7' and floor_patch:
                s=s.common(Part.makeBox(550,650,20,App.Vector(400,-325,-330)))
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if 'Lever' in n:color='Lever'
            elif 'Bracket' in n:color='Support'
            elif n.startswith('ClutchSupport_'):color='Hardware'
            elif n=='hull_floor_7':color='Floor'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.04)
        print('Rendered',name,flush=True)
    mechanism=[n for n in byid if n.startswith(('ClutchSupport_','ClutchThrowout_'))]
    draw(mechanism+['hull_floor_7'],'supports','Clutch supports and auxiliary controls | provisional floor mounting',(1,1,.65),True)
    draw([n for n in r['new_ids'] if n!='hull_floor_7']+['ClutchThrowout_Shaft','ClutchThrowout_OperatingLever'],
         'auxiliary','SH953 controls | inferred profiles and transverse arrangement',(-1,1,.65))
    draw([n for n in r['new_ids'] if ('Bracket' in n or 'Mount' in n or n=='hull_floor_7')],
         'underside','Eight source-sized screws from below | attachment hypothesis',(1,1,-.9),True)
    context=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_',
        'ClutchThrust_','ClutchCone_','ClutchRetention_','ClutchDrum_','ClutchStopBand_','AirPump_','PumpMount_','InputHousing_'))]
    draw(context+mechanism+['hull_floor_7'],'isometric','Clutch development | supports populated; brake linkage pending',(1,1,.65),True)
    draw(mechanism+['FrontClutch_Coupling','hull_floor_7'],'side_view','Engine left; transmission right | support profiles remain approximate',(0,1,0),True)
    for name in ['SNL2_full.png','SNL2_clutch_context.png']:
        (out/name).write_bytes((HERE/'clutch_throwout_build/source_review'/name).read_bytes())
    names=['supports','auxiliary','underside','isometric','side_view','SNL2_full','SNL2_clutch_context']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        images={n+'.png':sha(out/(n+'.png')) for n in names},floor_patch='Display-only crop of actual revised M1937; native floor retains full extent',
        source_comparison='Qualitative inspection only; historical longitudinal registration and mount hypothesis remain unresolved'))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Clutch support development</title>'
        '<style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}</style>'
        '<h1>Clutch supports and auxiliary controls</h1><p>Source identities and specified hardware sizes; inferred geometry. Underside floor mounting is provisional. Full brake and engine frame remain pending.</p>'
        +''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
finally:
    runtime.close()
