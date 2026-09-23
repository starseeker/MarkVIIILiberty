"""Native water-pump views and source gallery; sections affect display only."""
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
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_water_pump_passage_study');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    V=App.Vector;r=read(base/'report.json');native=base/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items={i['id']:i for i in leaves(doc.Root)}
    inverse=doc.EngineWaterPump.getGlobalPlacement().inverse();rows={row['name']:row for row in r['occurrences']}
    COLORS.update(PumpCasting=(.63,.69,.65),PumpSteel=(.57,.65,.71),PumpBearing=(.72,.75,.77),PumpPacking=(.35,.38,.34),PumpGasket=(.65,.45,.31),PumpBronze=(.76,.62,.35))
    clip=Part.makeBox(400,150,300,V(-60,0,-150));names=[]
    def draw(name,title,direction,section=False,context=False,explode=False):
        rendered=[]
        for ident in r['new_ids']+(['EngineLowerDrive_IntegralDriver','EngineCase_lower'] if context else []):
            item=items[ident];shape=item['shape'].copy();shape.Placement=inverse.multiply(shape.Placement)
            key=rows.get(ident,{}).get('key','case');color='PumpSteel'
            if key in ['body','cover','retainer','case']:color='PumpCasting'
            if key.startswith('bearing'):color='PumpBearing'
            if key=='packing':color='PumpPacking'
            if 'gasket' in key or key=='shim':color='PumpGasket'
            if key in ['gland','impeller','impeller_cotter']:color='PumpBronze'
            if ident=='EngineCase_lower':
                shape=shape.common(Part.makeBox(280,150,300,V(-70,0,-90)))
            elif section and key in ['body','cover','retainer','packing','gland','bearing_inner','bearing_outer','bearing_cage','joint_gasket','cover_gasket','shim']:
                shape=shape.common(clip)
            if explode:
                shift=0
                if key in ['body','joint_gasket','plug','plug_gasket']:shift=80
                elif key in ['impeller','key','impeller_nut','impeller_cotter']:shift=150
                elif key=='cover' or key.startswith('cover_'):shift=220
                shape.translate(V(shift,0,0))
            if shape.isNull() or not shape.Solids:continue
            rendered.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=ident,system=color))
        shaded_detail(rendered,out/(name+'.svg'),direction,title,deflection=.04);names.append(name);print('Rendered',name,flush=True)
    draw('isometric','Water-pump development | casting profiles and attachment details under review',(.7,-1,.55))
    draw('section','Water-pump section | geared shaft, ball bearing, two glands and impeller',(.1,-1,.04),section=True)
    draw('section_iso','Water-pump cutaway | source-led estimated internals',(.6,-1,.5),section=True)
    draw('installed','Water pump and lower drive | receiver fit and mounting stack under review',(.7,-1,.45),section=True,context=True)
    draw('exploded','Water-pump component comparison | display separation only',(.3,-1,.3),explode=True)
    source=read(HERE/'engine_water_pump_sources.json');pairs=[]
    for suffix,view in [('figure_079_original.png','section_iso'),('p289-geometry.png','exploded'),('MarkVIII043.jpg','isometric')]:
        path=next(ROOT/k for k in source['source_assets'] if k.endswith(suffix))
        pairs.append(f'<h2>{suffix} / {view}</h2><div class="pair"><img src="{os.path.relpath(path,out)}"><img src="{view}.png"></div>')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Water-pump development review</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center}</style><h1>Water-pump development candidate</h1><p>Source-informed arrangement; casting profiles and commercial bearing internals estimated. Packing quantities, inlet-cover identity and case attachment stack remain under review. Source cameras are not registered. All sections and exploded offsets affect display only.</p>'+''.join(pairs)+''.join(f'<h2>{n}</h2><img src="{n}.png">' for n in names))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in names},source_assets=source['source_assets'],model_modified=False,source_camera_fit=False))
finally:
    runtime.close()
