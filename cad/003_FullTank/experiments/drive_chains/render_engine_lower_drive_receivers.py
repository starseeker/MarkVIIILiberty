"""Saved-native receiving-case views; cuts change display only."""
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
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_lower_drive_installation')
p.add_argument('--worker',action='store_true');a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    V=App.Vector;r=read(base/'report.json');native=base/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=V(*r['engine_origin'])
    COLORS.update(Driver=(.63,.69,.73),Bush=(.76,.63,.36),Housing=(.61,.68,.64),Hardware=(.46,.53,.60),Case=(.60,.65,.59))
    images=[]
    def draw(name,title,direction,case_clip,unit_clip=None,case_only=False):
        rows=[]
        for n in ['EngineCase_lower']+([] if case_only else r['unit_ids']+['EngineGear_DrivingBevel']):
            row=byid[n];s=row['shape'].copy();color='Hardware'
            if 'IntegralDriver' in n or n=='EngineGear_DrivingBevel':color='Driver'
            elif n.endswith('Bush'):color='Bush'
            elif n.endswith('Housing'):color='Housing'
            elif n=='EngineCase_lower':color='Case'
            clip=case_clip if n=='EngineCase_lower' else unit_clip
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            rows.append(dict(row,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(rows,out/(name+'.svg'),direction,title,deflection=.04)
        images.append(name);print('Rendered',name,flush=True)
    region=Part.makeBox(370,240,300,origin+V(1050,-120,-270))
    half=Part.makeBox(370,120,300,origin+V(1050,0,-270))
    detail=Part.makeBox(210,80,135,origin+V(1180,0,-165))
    draw('isometric','Lower-drive receiver candidate | sectioned crankcase, integral lug and pump receivers',(.7,-1,.55),half)
    draw('longitudinal','Lower-drive receiver section | pump axis and casting profiles remain estimates',(.04,-1,.02),half,half)
    draw('underside','Crankcase from below | offset oil-pump opening; pump assemblies not yet populated',(.25,-.3,-1),region)
    draw('case_only','Receiving casting | cylindrical lug, screw support and two pump openings',(.7,-1,.55),half,case_only=True)
    draw('screw_support','Retaining-screw support | source screw length preserved; cast profile estimated',(.15,-1,.1),detail,detail)
    draw('pump_interface','Pump mounting region | rear retainer opening and bottom oil-pump rim',(.95,-.3,-.3),region)
    source=read(HERE/'engine_lower_drive_receiver_sources.json');pairs=[]
    for suffix,view in [('figure_096_original.png','underside'),('figure_107_original.png','longitudinal'),('p291-geometry.png','screw_support'),('p289-geometry.png','pump_interface')]:
        path=next(ROOT/k for k in source['source_assets'] if k.endswith(suffix))
        pairs.append(f'<h2>{suffix} / {view}</h2><div class="pair"><img src="{os.path.relpath(path,out)}"><img src="{view}.png"></div>')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Lower-drive receiving case</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center}</style><h1>Lower-drive receiving-case candidate</h1><p>Source views guide form; no camera registration or measured casting profile is claimed. The 184 mm pump-axis drop remains estimated. Pump internals, mounting hardware and historical dimensional reconciliation remain pending. Display cuts do not modify the saved model.</p>'+''.join(pairs)+''.join(f'<h2>{n}</h2><img src="{n}.png">' for n in images))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in images},source_assets=source['source_assets'],model_modified=False,source_camera_fit=False))
finally:
    runtime.close()
