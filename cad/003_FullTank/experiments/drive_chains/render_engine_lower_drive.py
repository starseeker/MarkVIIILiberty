"""Native study views and unregistered source comparisons for lower distribution."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_lower_drive_study')
p.add_argument('--worker',action='store_true');a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    V=App.Vector
    r=read(base/'report.json');native=base/'DrivetrainWithLowerDriveStudy.FCStd';assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)}
    origin=doc.EngineLowerDistributionDrive.getGlobalPlacement().Base
    COLORS.update(Driver=(.63,.69,.73),Bush=(.76,.63,.36),Housing=(.61,.68,.64),Hardware=(.46,.53,.60),Context=(.46,.57,.65),Case=(.53,.60,.56))
    images=[]
    def draw(names,name,title,direction=(.7,1,.4),clip=None,exploded=False):
        rows=[]
        for n in names:
            row=byid[n];s=row['shape'].copy();color='Hardware'
            if 'IntegralDriver' in n or n=='EngineGear_DrivingBevel':color='Driver'
            elif n.endswith('Bush'):color='Bush'
            elif n.endswith('Housing'):color='Housing'
            elif n.startswith('EngineCase'):color='Case'
            if exploded:
                amount={'DistributorBush':45,'FlywheelBush':-45,'DistributorHousing':95,'FlywheelHousing':-95,'BushDowel':95}
                s.translate(V(amount.get(n.removeprefix('EngineLowerDrive_'),0),0,0))
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            rows.append(dict(row,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(rows,out/(name+'.svg'),direction,title,deflection=.04)
        images.append(name);print('Rendered',name,flush=True)
    new=r['new_ids'];basic=[n for n in new if any(n.endswith(s) for s in ['IntegralDriver','Bush','Housing','BushDowel'])]
    draw(new+['EngineGear_DrivingBevel'],'isometric','Lower distribution development | integral 22/21-tooth driver; casing fit remains open')
    draw(new,'unit','Lower driver study | source-counted split housing, bearing, dowel and clamp sets')
    draw(basic,'exploded','Lower driver study | display-only separation of five principal pieces and locating dowel',(.5,1,.35),exploded=True)
    draw(['EngineLowerDrive_IntegralDriver'],'driver','Integral lower driver | 22/21 teeth, hollow shaft and estimated six-slot oil-pump coupling')
    cut=Part.makeBox(250,80,230,origin+V(-80,0,-210))
    draw(new,'section','Lower driver section | source-range bearing clearance and endplay; estimated profiles',(.1,-1,.05),clip=cut)
    draw(new+['EngineGear_DrivingBevel','EngineCase_lower'],'case_section',
         'Installed study section | original casing retained; interference and pump-axis mismatch unresolved',(.1,-1,.05),clip=cut)
    comparisons='';assets={}
    for figure,view in [(22,'isometric'),(88,'exploded'),(93,'section'),(96,'case_section'),(107,'case_section')]:
        p=ROOT/f'references/1918-09_12_Cylinder_Liberty_Aero_Engine/Liberty_Project/assets/figure_{figure:03d}_original.png'
        assets[str(p.relative_to(ROOT))]=sha(p)
        comparisons+=f'<h2>Liberty figure{figure} / {view}</h2><div class="pair"><img src="{os.path.relpath(p,out)}"><img src="{view}.png"></div>'
    p=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p291-geometry.png';assets[str(p.relative_to(ROOT))]=sha(p)
    comparisons+=f'<h2>SNLplate19 (original caption retained) / component study</h2><div class="pair"><img src="{os.path.relpath(p,out)}"><img src="unit.png"></div>'
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Lower distribution study</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:16px}</style><h1>Lower distribution drive: unqualified installation study</h1><p>Source counts and printed bearing fits are retained.184mm pump-axis separation, profiles, spline count and screw support are provisional. Original casing is unchanged: visible overlaps and aperture mismatch remain unresolved. Views are not registered to source cameras; cuts and exploded offsets alter display only.</p>'+comparisons+''.join(f'<h2>{n}</h2><img src="{n}.png">' for n in images))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        images={n+'.png':sha(out/(n+'.png')) for n in images},source_assets=assets,model_modified=False,source_camera_fit=False))
finally:
    runtime.close()
