"""Native oil-pump visual review; cutaways and exploded offsets are display only."""
import argparse,os,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from detail_render import shaded_detail
    from lib.cad_build import COLORS
    V=App.Vector;r=read(base/'report.json');native=base/r['native_file'];assert sha(native)==r['native_sha256'];doc=App.openDocument(str(native))
    COLORS.update(OilCast=(.64,.7,.64),OilSteel=(.58,.65,.72),OilBronze=(.78,.62,.32),OilSeal=(.56,.38,.26),OilGauze=(.76,.69,.45))
    names=[]
    for name,direction in [('isometric',(.7,-1,.55)),('cutaway',(.8,-1,.45)),('gear_core',(.7,-1,.5)),('exploded',(.7,-1,.4)),('relief',(.5,-1,.2)),('lower_service',(.4,-.7,-1))]:
        items=[]
        for row in r['occurrences']:
            key=row['key'];ident=row['name'];link=doc.getObject(ident);s=link.LinkedObject.Shape.copy();s.Placement=doc.getObject(row['assembly']).getGlobalPlacement().multiply(link.LinkPlacement).multiply(s.Placement);color='OilSteel'
            if key in ['lower_body','upper_body','cover']:color='OilCast'
            if 'bush' in key:color='OilBronze'
            if 'gasket' in key:color='OilSeal'
            if key.endswith('_screen'):color='OilGauze'
            cut_keys=['lower_body','upper_body','cover','upper_bush','lower_bush','relief_cage','cover_gasket','drain_plug','drain_gasket','upper_filter_frame','lower_filter_frame','upper_side_screen','lower_side_screen','upper_end_screen','lower_end_screen']
            if name=='cutaway' and key in cut_keys:s=s.common(Part.makeBox(200,400,400,V(-200,-200,-200)))
            if name=='cutaway' and row['assembly']=='EngineOilPumpFasteners' and row['xyz'][0]>0:continue
            if name=='lower_service' and key in ['cover','cover_gasket','drain_plug','drain_gasket','lower_filter_frame','lower_side_screen','lower_end_screen']:continue
            if name=='gear_core' and key not in ['lower_driving_gear','lower_idler_gear','upper_driving_gear','upper_idler_gear','shaft','long_pin','short_pin','partition','upper_bush','lower_bush']:continue
            if name=='exploded':
                dz=0
                if key.startswith('upper_') and ('filter' in key or 'screen' in key) or key in ['screen_nut','screen_lock']:dz=100
                elif key in ['upper_body','upper_bush','upper_plug']:dz=55
                elif key.startswith('upper_') and 'gear' in key:dz=25
                elif key.startswith('lower_') and ('filter' in key or 'screen' in key):dz=-85
                elif key in ['cover','cover_gasket','drain_plug','drain_gasket']:dz=-135
                elif key.startswith('relief_'):dz=-35
                elif ident.startswith('EngineOilPump_UpperJoint'):dz=55
                s.translate(V(0,0,dz))
            if name=='relief':
                if not key.startswith('relief_'):continue
                if key=='relief_cage':s=s.common(Part.makeBox(100,100,100,V(-30,r['controls']['relief_y'],-80)))
            if not s.Solids:continue
            items.append(dict(shape=s,target=SimpleNamespace(Shape=s),definition=ident,system=color,representation='assembly'))
        shaded_detail(items,out/(name+'.svg'),direction,'Oil-pump development | '+name+' | source-led estimates',deflection=.06);names.append(name);print('rendered',name,flush=True)
    assets=r['source_assets'];pairs=[]
    for suffix,view in [('figure_027_original.png','gear_core'),('figure_029_original.png','cutaway'),('figure_030_original.png','relief'),('figure_033_original.png','exploded'),('p305.jpg','exploded'),('figure_034_original.png','lower_service')]:
        path=next(ROOT/name for name in assets if name.endswith(suffix));pairs.append(f'<h2>{suffix} / {view}</h2><div class="pair"><img src="{os.path.relpath(path,out)}"><img src="{view}.png"></div>')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Oil-pump development review</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center}</style><h1>Oil-pump development</h1><p>'+str(r['physical_count'])+' constituents; '+ '; '.join(r['datums']['missing'])+'. Castings, dimensions, gears and passage routes contain explicit estimates. The separate screens use deliberately coarse open apertures; true gauze weave and filtration rating are unknown. Cutaways, selective omissions and exploded offsets affect display only, and are not service poses. Cameras are not registered to the source figures.</p>'+''.join(pairs)+''.join(f'<h2>{n}</h2><img src="{n}.png">' for n in names))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in names},model_modified=False,source_camera_fit=False))
finally:
    runtime.close()
