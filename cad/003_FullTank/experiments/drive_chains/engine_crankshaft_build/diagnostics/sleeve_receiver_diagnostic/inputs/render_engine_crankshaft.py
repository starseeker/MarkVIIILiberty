"""Source-linked review views of the saved crankshaft installation."""
import argparse,os
from pathlib import Path
import subprocess,sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'engine_crankshaft_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'DrivetrainWithEngineCrankshaft.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=App.Vector(*r['datums']['origin']);c=r['controls'];cc=r['case_controls'];names=[]
    COLORS.update(Casting=(.62,.68,.67),Shaft=(.44,.49,.53),Bearing=(.77,.67,.41),Balls=(.69,.73,.76),Cage=(.73,.56,.28),Context=(.43,.54,.60),Hardware=(.54,.56,.58))
    def draw(selected,name,title,direction,clip=None):
        items=[]
        for n in selected:
            row=byid[n];s=row['shape'].copy()
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Context'
            if n.startswith('EngineCase_'):color='Casting'
            elif n=='EngineCrank_Forging':color='Shaft'
            elif 'Ball' in n:color='Balls'
            elif 'Cage' in n:color='Cage'
            elif n.startswith('EngineCrank_'):color='Bearing' if ('Main' in n or 'Race' in n or 'Center' in n) else 'Hardware'
            items.append(dict(row,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(items,out/(name+'.svg'),direction,title,deflection=.08)
        names.append(name);print('Rendered',name,flush=True)
    new=r['new_ids'];cases=['EngineCase_upper','EngineCase_lower'];frame=[n for n in byid if n.startswith(('EngineFrame_','EngineSuspension_'))]
    draw(new+['EngineCase_lower']+frame,'isometric','Crankshaft and bearings installed | upper case hidden for review; cylinders and shaft plugs pending',(.45,.6,1))
    draw(['EngineCrank_Forging'],'shaft','One hollow crankshaft forging | six paired throws; unprinted web profiles estimated',(.4,1,.65))
    draw(['EngineCrank_Main1_lower'],'front_bearing','Long lower bearing | 115 mm source length; oil-entry and dowel detail approximated',(.4,.45,1))
    draw(['EngineCrank_Main2_lower'],'short_bearing','Short lower bearing | 49 mm source length; joint oil notches and locating hole',(.45,.4,1))
    half=Part.makeBox(1700,350,650,origin+App.Vector(-300,0,-300))
    draw(new+cases,'longitudinal_section','Longitudinal half-section | hollow journals, pin cavities and bearing seats',(0,-1,.15),half)
    thrust=[n for n in new if 'Thrust' in n]
    clip=Part.makeBox(90,150,200,origin+App.Vector(5,0,-100))
    draw(thrust+['EngineCrank_Forging']+cases,'thrust_section','Double thrust section | three races, two ball rows/cages and two sleeves; dimensions/count estimated',(.2,-1,.4),clip)
    t=r['datums']['taper'];clip=Part.makeBox(t['front']-t['rear']+35,100,130,origin+App.Vector(t['rear']-30,0,-65))
    draw(['EngineCrank_Forging','EngineCrank_FlywheelKey','EngineCrank_FlywheelKeyScrew','EngineCrank_OutputNut','EngineCrank_OutputCotter','ClutchDrum_flywheel'],
         'output_section','Output taper, key and retention | section through existing clutch flywheel; registration conditional',(0,-1,.4),clip)
    # A transverse projection tests the three crank planes without photograph fitting.
    draw(['EngineCrank_Forging'],'throw_planes','Gear-end view | paired throws 1/6, 2/5, 3/4 in the documented timing position',(1,0,0))
    sources=ROOT/'references/1918-09_12_Cylinder_Liberty_Aero_Engine/Liberty_Project/assets'
    comparisons=''
    for figure,view in [(31,'front_bearing'),(11,'short_bearing'),(85,'thrust_section'),(12,'output_section'),(93,'throw_planes')]:
        rel=os.path.relpath(sources/('figure_%03d_original.png'%figure),out)
        comparisons+='<h2>Liberty figure '+str(figure)+' / '+view+'</h2><div class="comparison"><img src="'+rel+'"><img src="'+view+'.png"></div>'
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Liberty crankshaft development</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.comparison{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:16px}</style><h1>Liberty crankshaft development</h1><p>Static reconstruction with conditional aviation evidence. The source topology and printed constraints guide this development, but the web profiles, oil groove sizes, ball count, thrust dimensions and axial engine registration are estimated. Source/model cameras are not registered. Review cuts and hidden upper case do not alter the native assembly. Shaft plugs, driving gear, additional locking hardware, cylinders, rods and engine services remain pending.</p>'+comparisons+''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in names},source_assets={str((sources/('figure_%03d_original.png'%n)).relative_to(ROOT)):sha(sources/('figure_%03d_original.png'%n)) for n in [11,12,31,85,93]},model_modified=False,source_camera_fit=False))
finally:
    runtime.close()
