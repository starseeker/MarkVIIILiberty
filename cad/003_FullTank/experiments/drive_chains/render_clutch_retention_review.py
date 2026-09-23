"""Render the saved retention geometry and full original source for comparison."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_retention_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from PIL import Image,ImageDraw,ImageFont
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'TransmissionWithClutchRetention.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(RetentionWire=(.82,.42,.13),Plunger=(.38,.44,.47),Spring=(.30,.34,.37),Lining=(.38,.31,.22),Clutch=(.59,.61,.59))
    def draw(names,name,title,direction,clip=None,rotate=False):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy();s.translate(-origin)
            if rotate:s.rotate(App.Vector(),App.Vector(1,0,0),-30)
            if clip:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='Clutch'
            if n=='ClutchRetention_Wire':color='RetentionWire'
            elif 'Plunger' in n:color='Plunger'
            elif n.startswith('ClutchCone_Spring'):color='Spring'
            elif n=='ClutchCone_lining':color='Lining'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.035)
        print('Rendered',name,flush=True)
    assembly=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','ClutchThrust_','ClutchCone_','ClutchRetention_','AirPump_','PumpMount_','InputHousing_')) or n=='CenterTransmissionCore_bevel_cover']
    springs=[n for n in byid if n.startswith('ClutchCone_') and any(k in n for k in ['Plunger','Cup','Spring','_ring'])]+['ClutchRetention_Wire','ClutchThrust_Stop']
    draw(assembly,'isometric','Clutch retention installed | SH861K wire highlighted orange',(1,1,.65))
    draw(springs,'retention','Six spring sets | one wire through six tangential head passages',(1,.3,.4))
    detail=Part.makeBox(20,24,26,App.Vector(1008,102,-13))
    draw(['ClutchCone_Plunger1','ClutchRetention_Wire','ClutchThrust_Stop'],'head','Installed head and locking wire | actual saved solids',(1,.6,1),detail,True)
    # Remove the camera-facing half at the tangential bore's radial centre plane.
    section=Part.makeBox(13,13,24,App.Vector(1013,101,-12))
    draw(['ClutchCone_Plunger1','ClutchRetention_Wire'],'head_section','Head section | through bore, curved wire, axial wall stock',(0,1,0),section,True)
    src=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
    canvas=Image.new('RGB',(1800,1500),'#f6f4ed');pen=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    pen.text((30,20),'Plunger retention: full SNL21 and saved native geometry',fill='black',font=font)
    def paste(path,rect):
        im=Image.open(path).convert('RGB');im.thumbnail(rect[2:]);canvas.paste(im,(rect[0]+(rect[2]-im.width)//2,rect[1]+(rect[3]-im.height)//2))
    paste(src,(20,70,1050,780));paste(out/'retention.png',(1050,70,730,780))
    paste(out/'head_section.png',(20,855,900,440));paste(out/'head.png',(935,855,845,440))
    notes=['Catalogue SNL275: one SH861K, soft iron W.&M.No16,30in; SNL157: six SH861A plungers.',
        'Full plate establishes assembly context; wire route, twist,1.5mm diameter and2.7mm head bores are estimates.',
        'Independent panel scales. Orange highlights the wire; it does not identify a copper or brass material.',
        'Outer drum/flywheel are still missing; the projecting wire tail must be checked against their future geometry.']
    for n,line in enumerate(notes):pen.text((30,1330+33*n),line,fill='black',font=small)
    canvas.save(out/'comparison.png');images=['isometric','retention','head','head_section','comparison']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),helper_sha256=sha(HERE/'detail_render.py'),
        base_renderer_sha256=sha(STAGE/'lib/visual_review.py'),source_path=str(src.relative_to(ROOT)),source_sha256=sha(src),
        deflection_mm=.035,metrology_claim=False,image_hashes={n+'.png':sha(out/(n+'.png')) for n in images},notes=notes))
    (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch plunger retention</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}</style><h1>Plunger locking wire and head passages</h1><p>Source length and quantity; documented route and diameter approximations.</p>'+''.join(f'<p>{n}</p><img src="{n}.png" alt="{n}">' for n in ['comparison','isometric','retention','head_section'])+'<p><a href="render_receipt.json">Evidence and image hashes</a></p></html>')
finally:
    runtime.close()
