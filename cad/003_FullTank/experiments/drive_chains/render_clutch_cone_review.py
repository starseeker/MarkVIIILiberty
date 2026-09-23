"""Render actual saved cone/spring geometry with full source figures for review."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_cone_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from PIL import Image,ImageDraw,ImageFont
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'TransmissionWithClutchCone.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(ConeSteel=(.57,.62,.64),Lining=(.38,.31,.22),Copper=(.72,.40,.23),Spring=(.30,.34,.37),Support=(.58,.56,.44),Plug=(.68,.53,.27),OtherClutch=(.60,.61,.58))
    def draw(names,name,title,direction,clip=None,rotate=False):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].copy();s.translate(-origin)
            if rotate:s.rotate(App.Vector(),App.Vector(1,0,0),-30)
            if clip:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            color='OtherClutch'
            if n=='ClutchCone_cone':color='ConeSteel'
            if n=='ClutchCone_lining':color='Lining'
            if n.startswith('ClutchCone_LiningRivet'):color='Copper'
            if n.startswith('ClutchCone_Spring'):color='Spring'
            if n=='ClutchStack_support':color='Support'
            if n=='ClutchCone_Plug':color='Plug'
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(selected,out/(name+'.svg'),direction,title,deflection=.06)
        print('Rendered',name,flush=True)
    assembly=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','ClutchThrust_','ClutchCone_','AirPump_','PumpMount_','InputHousing_')) or n=='CenterTransmissionCore_bevel_cover']
    clutch=[n for n in assembly if n.startswith(('ClutchStack_','ClutchCollar_','ClutchThrust_','ClutchCone_'))]
    draw(assembly,'isometric','Clutch cone and six spring sets | installed with input drive and air pump',(1,1,.65))
    draw(clutch,'cutaway','Clutch cutaway | separate cone, lining, keyed support and retained spring sets',(1,1,.65),Part.makeBox(500,540,270,App.Vector(700,-270,-270)))
    draw([n for n in clutch if n.startswith('ClutchCone_') or n=='ClutchStack_support'],'cone','Cone assembly | six support rivets, 43 recessed lining rivets, separate spring sets',(-1,1,.7))
    section=Part.makeBox(530,530,.4,App.Vector(600,-265,-.2))
    draw([n for n in assembly if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','ClutchThrust_','ClutchCone_'))],'section','Axial section through one plunger pair | model engine to the right',(0,0,1),section,True)
    detail=Part.makeBox(180,90,.4,App.Vector(865,80,-.2))
    draw(clutch,'spring_detail','Spring section | head, stop ring, cup, spring, rear ring and cone rivet',(0,0,1),detail,True)
    draw([n for n in r['new_ids'] if any(k in n for k in ['Plunger','Cup','Spring','_ring'])],'spring_sets','Six separate retained spring sets | shared definitions, actual receiver holes',(1,1,.65))
    src=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
    canvas=Image.new('RGB',(1800,1650),'#f6f4ed');pen=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    pen.text((30,20),'Clutch cone and spring arrangement: full SNL21 and actual native sections',fill='black',font=font)
    pen.text((30,60),'Independent panel scales; no calibrated overlay. Native sections are rotated 30 degrees about the shaft.',fill='black',font=small)
    def paste(path,rect):
        im=Image.open(path).convert('RGB');im.thumbnail(rect[2:]);canvas.paste(im,(rect[0]+(rect[2]-im.width)//2,rect[1]+(rect[3]-im.height)//2))
    pen.text((30,100),'Full source: engine left',fill='black',font=small);paste(src,(20,135,1030,750))
    pen.text((1080,100),'Native spring/cone connection',fill='black',font=small);paste(out/'spring_detail.png',(1055,135,725,750))
    pen.text((30,910),'Native clutch section: engine right',fill='black',font=small);paste(out/'section.png',(20,945,1750,530))
    notes=['Printed quantities and conditional HB cone dimensions; support profile and all axial stations remain estimates.',
           'Six cup guides and spring sets, six inclined support rivets, and43 lining rivets are separate installed solids.',
           'Flywheel/drum and crankshaft engagement are still missing. Free spring lengths conflict between HB and SNL.',
           'This is a static geometric reconstruction; rivet forming, threaded fits, spring preload and loads are unqualified.']
    for n,line in enumerate(notes):pen.text((30,1490+32*n),line,fill='black',font=small)
    canvas.save(out/'comparison.png')
    images=['isometric','cutaway','cone','section','spring_detail','spring_sets','comparison']
    receipt=dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),helper_sha256=sha(HERE/'detail_render.py'),
        base_renderer_sha256=sha(STAGE/'lib/visual_review.py'),source_path=str(src.relative_to(ROOT)),source_sha256=sha(src),
        deflection_mm=.06,metrology_claim=False,image_hashes={n+'.png':sha(out/(n+'.png')) for n in images},notes=notes)
    write(out/'render_receipt.json',receipt)
    (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch cone source review</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}</style><h1>Clutch cone and spring sets</h1><p>Source counts and conditional dimensions; explicit inferred profiles and interfaces.</p>'+''.join(f'<p>{n}</p><img src="{n}.png" alt="{n}">' for n in ['comparison','isometric','cutaway','cone','spring_sets'])+'<p><a href="render_receipt.json">Evidence and image hashes</a></p></html>')
finally:
    runtime.close()
