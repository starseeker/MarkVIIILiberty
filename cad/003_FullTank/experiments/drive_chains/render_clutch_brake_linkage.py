"""Render actual saved brake solids beside retained source context."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_brake_linkage_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'TransmissionWithClutchBrake.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(Anchor=(.56,.44,.28),Carrier=(.42,.54,.40),Lever=(.30,.49,.60),Hardware=(.68,.70,.71),
        Spring=(.65,.46,.26),Lining=(.47,.39,.29),Floor=(.65,.65,.58),Context=(.49,.53,.54))
    def draw(names,name,title,direction,floor_patch=False,clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy();s.translate(-origin)
            if n=='hull_floor_7' and floor_patch:s=s.common(Part.makeBox(550,650,20,App.Vector(400,-325,-330)))
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if 'Lever' in n or n=='ClutchBrake_BellCrank':color='Lever'
            elif n=='ClutchBrake_Anchor':color='Anchor'
            elif n=='ClutchBrake_Carrier' or 'Bracket' in n:color='Carrier'
            elif n=='ClutchBrake_Spring':color='Spring'
            elif n=='ClutchStopBand_lining':color='Lining'
            elif n.startswith(('ClutchBrake_','ClutchSupport_')):color='Hardware'
            elif n=='hull_floor_7':color='Floor'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.035)
        print('Rendered',name,flush=True)
    brake=r['new_ids']+[n for n in byid if n.startswith('ClutchStopBand_')]
    receivers=['ClutchSupport_LeftBracket','ClutchThrowout_LeftLever','ClutchThrowout_Shaft']
    draw(brake+receivers,'mechanism','Clutch-stop brake | full inventory; provisional carrier and mounting',(1,1,.65))
    draw(brake,'linkage','Band anchor, spring and right-angle linkage | estimated profiles',(-1,1,.7))
    draw([n for n in brake if n not in ['ClutchBrake_StopRod','ClutchBrake_RodPin','ClutchBrake_RodCotter'] and 'RodNut' not in n]+['ClutchSupport_LeftBracket'],
        'end_view','View along clutch axis | source-sized band and adjusters',(1,0,0))
    draw(brake+receivers,'top_view','Carrier and rod connection | static arrangement hypothesis',(0,0,1))
    mechanism=[n for n in byid if n.startswith(('ClutchBrake_','ClutchStopBand_','ClutchSupport_','ClutchThrowout_'))]
    context=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_',
        'ClutchThrust_','ClutchCone_','ClutchRetention_','ClutchDrum_','AirPump_','PumpMount_','InputHousing_'))]
    draw(context+mechanism+['hull_floor_7'],'isometric','Clutch development | complete provisional stop mechanism',(1,1,.65),True)
    draw(brake+receivers+['ClutchDrive_drum'],'side_view','Engine left; transmission right | brake layout remains provisional',(0,1,0))
    for name in ['SNL2_full.png','SNL2_clutch_context.png']:
        (out/name).write_bytes((HERE/'clutch_support_build/source_review'/name).read_bytes())
    names=['mechanism','linkage','end_view','top_view','isometric','side_view','SNL2_full','SNL2_clutch_context']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        images={n+'.png':sha(out/(n+'.png')) for n in names},
        source_comparison='Qualitative only. Carrier, bell-crank orientation and shared mount are mechanical hypotheses, not traced source profiles.'))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Clutch-stop linkage development</title>'
        '<style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}</style>'
        '<h1>Clutch-stop linkage development</h1><p>Source identities and specified hardware sizes; inferred mechanism geometry. Historical mounting, source registration and motion remain unresolved.</p>'
        +''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
finally:
    runtime.close()
