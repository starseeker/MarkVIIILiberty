"""Saved-native casing views and fixed source projection, without source fitting."""
import argparse,os
from pathlib import Path
import subprocess,sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_case_build');p.add_argument('--worker',action='store_true');p.add_argument('--views',nargs='+',choices=['isometric','upper_casting','upper_underside','lower_casting','longitudinal_section','transverse_section','front_yoke_section','side_view'])
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker']+(['--views']+a.views if a.views else []),env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'DrivetrainWithEngineCase.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    prior_receipt_sha=None
    if a.views:
        previous=read(out/'render_receipt.json');assert previous['native_sha256']==sha(native)
        assert all(sha(out/n)==digest for n,digest in previous['images'].items())
        prior_receipt_sha=sha(out/'render_receipt.json')
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=App.Vector(*r['datums']['origin']);c=r['controls']
    COLORS.update(UpperCasting=(.63,.68,.67),LowerCasting=(.55,.61,.60),Support=(.42,.55,.64),Context=(.47,.51,.52),Floor=(.65,.65,.58))
    def draw(names,name,title,direction,clip=None):
        if a.views and name not in a.views:return
        selected=[]
        for n in names:
            row=byid[n];s=row['shape'].copy()
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if n=='EngineCase_upper':color='UpperCasting'
            elif n=='EngineCase_lower':color='LowerCasting'
            elif n.startswith(('EngineFrame_','EngineSuspension_')):color='Support'
            elif n.startswith('hull_floor_'):color='Floor'
            selected.append(dict(row,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.16);print('Rendered',name,flush=True)
    cases=['EngineCase_upper','EngineCase_lower'];frame=[n for n in byid if n.startswith(('EngineFrame_','EngineSuspension_'))]
    floors=['hull_floor_5','hull_floor_6','hull_floor_7'];clutch=[n for n in byid if n.startswith(('ClutchDrum_','ClutchBrake_','ClutchStopBand_','ClutchSupport_','ClutchThrowout_','FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','ClutchThrust_','ClutchCone_','ClutchRetention_'))]
    draw(cases+frame+floors+clutch,'isometric','Hollow Liberty crankcase installed | engine internals and mounting fasteners pending',(1,1,.75))
    draw(['EngineCase_upper'],'upper_casting','LQ207A upper casting | twelve V-bank openings; profiles and interface stock estimated',(1,1,.75))
    draw(['EngineCase_upper'],'upper_underside','Upper casting underside | eight webs, seven bearing seats and dry gear chamber',(.3,.1,-1))
    draw(['EngineCase_lower'],'lower_casting','LQ180A lower casting | integral saddles, oil trough, wells and pump receiver',(.35,.45,1))
    section=Part.makeBox(1600,320,650,origin+App.Vector(-40,0,-300))
    draw(cases+frame,'longitudinal_section','Longitudinal half-section | cast cavities and revised front-yoke clearance',(0,-1,.22),section)
    x=origin.x+c['nose_to_first_row']+2.5*c['cylinder_pitch']
    clip=Part.makeBox(30,600,600,App.Vector(x-15,-300,origin.z-270))
    draw(cases+frame,'transverse_section','Cylinder-bay transverse section | conditional45degree V and controlled cubic sump',(1,0,0),clip)
    cc=r['crossmember_controls'];sc=r['suspension_controls']
    yoke_x=cc['front_x']+cc['channel_depth']/2+cc['cleat_stock']+sc['front_hub_x_stock']/2
    yoke_clip=Part.makeBox(10,600,700,App.Vector(yoke_x-5,-300,cc['floor_top']-20))
    draw(cases+frame,'front_yoke_section','Front-yoke transverse section | dropped arms clear the sump; profile remains estimated',(1,0,0),yoke_clip)
    draw(cases+frame+['ClutchDrum_flywheel'],'side_view','Engine distribution end at left | axial registration remains provisional',(0,1,0))
    from PIL import Image,ImageDraw
    source=HERE/'clutch_stop_brake_sources/p277_foldout_original.jpg';crop=Image.open(source).crop((5440,1980,7250,3270)).convert('RGB');crop.save(out/'SNL2_engine_context.png')
    overlay=crop.copy();canvas=ImageDraw.Draw(overlay)
    def project(v):return ((1760-v.x/6.0269942196531785)*11072/2048-5440,(660-v.z/5.928273244781783)*5456/1009-1980)
    projected=cases+frame+['ClutchDrum_flywheel']
    for n in projected:
        for edge in byid[n]['shape'].Edges:
            points=[project(v) for v in edge.discretize(Deflection=.5)]
            if len(points)>1:canvas.line(points,fill='#087dc6' if n.startswith('EngineCase_') else '#ba622d',width=2)
    canvas.rectangle((0,0,1810,42),fill='#f5f3eb');canvas.text((10,12),'Blue: native crankcase; brown: supports/flywheel. Fixed SNL2 calibration, no fit. Profiles and registration provisional.',fill='#14405d');overlay.save(out/'source_overlay.png')
    names=['isometric','upper_casting','upper_underside','lower_casting','longitudinal_section','transverse_section','front_yoke_section','side_view','SNL2_engine_context','source_overlay']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),prior_render_receipt_sha256=prior_receipt_sha,refreshed_views=a.views or 'all',source_sha256=sha(source),source_crop=[5440,1980,7250,3270],projected_occurrences=projected,images={n+'.png':sha(out/(n+'.png')) for n in names}))
    source_dir=ROOT/'references/1918-09_12_Cylinder_Liberty_Aero_Engine/Liberty_Project/assets'
    comparisons=''
    for figure,view in [(14,'upper_casting'),(15,'upper_underside'),(16,'lower_casting')]:
        rel=os.path.relpath(source_dir/('figure_%03d_original.png'%figure),out)
        comparisons+='<h2>Liberty figure '+str(figure)+' / '+view+'</h2><div class="comparison"><img src="'+rel+'"><img src="'+view+'.png"></div>'
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Liberty crankcase development</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.comparison{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:16px}</style><h1>Liberty crankcase development</h1><p>Two source-informed hollow castings. Profiles, stock and registration are provisional; bearing inserts, rotating internals, cylinders, hardware and complete engine mounting remain pending. Source photographs include components not yet modeled; views are not photographically registered.</p>'+comparisons+''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
finally:
    runtime.close()
