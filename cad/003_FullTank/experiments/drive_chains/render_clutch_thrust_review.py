"""Render saved thrust geometry finely and compare its section with the full source."""
import argparse
import base64
import html
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_thrust_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,fitz
    from PIL import Image
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    native=base/'TransmissionWithClutchThrust.FCStd';r=read(base/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    COLORS.update(Clutch=(.67,.61,.46),Ball=(.72,.75,.79),Cage=(.68,.52,.28),Stop=(.54,.58,.64),Shaft=(.64,.66,.70),Spring=(.42,.46,.48),Belt=(.24,.25,.23))
    def draw(names,name,title,direction,clip=None):
        items=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            color=i['system']
            if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_')):color='Clutch'
            if n=='FrontClutch_Spring':color='Spring'
            if n=='ClutchDrive_belt':color='Belt'
            if n.startswith('ClutchThrust_Ball'):color='Ball'
            if n=='ClutchThrust_Cage':color='Cage'
            if n=='ClutchThrust_Stop':color='Stop'
            items.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n,system=color))
        shaded_detail(items,out/(name+'.svg'),direction,title)
    new=r['new_ids'];affected=r['affected_ids']
    surrounding=[n for n in byid if n.startswith(('FrontClutch_','ClutchCollar_','ClutchStack_','ClutchDrive_','AirPump_','PumpMount_','InputHousing_')) or n=='CenterTransmissionCore_bevel_cover']
    draw(surrounding+new,'isometric','Clutch thrust mechanism | installed with transmission input and air pump',(1,1,.65))
    draw(affected,'mechanism','Clutch spring-stop ring and thrust bearing | reconstructed profiles',(1,1,.6))
    draw([n for n in affected if n!='ClutchThrust_Stop'],'race_open','Spring-stop ring hidden | 30 analytic balls in their separate retainer',(1,1,.6))
    draw(['ClutchThrust_Cage'],'cage','SH998C retainer | 30 ball pockets; cage section estimated',(1,1,.6))
    names=affected+['ClutchCollar_collar','ClutchStack_bearing','ClutchStack_snap']
    clip=Part.makeBox(42,260,1,origin+App.Vector(985,-130,-.5))
    draw(names,'section','Axial section | separate thrust collar, ball retainer and spring-stop ring',(0,0,1),clip)
    clip=Part.makeBox(34,58,.4,origin+App.Vector(990,70,-.2))
    draw(names,'contact_detail','Upper race section | nominal contact; inferred grooves and clearances',(0,0,1),clip)
    snl=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
    with Image.open(snl) as src:src.crop((320,635,590,800)).save(out/'source_detail.png')
    def embed(path,x,y,w,h):
        data=base64.b64encode(path.read_bytes()).decode()
        return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'
    def text(x,y,value,size=20):return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}">{html.escape(value)}</text>'
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1690">','<rect width="1800" height="1690" fill="#f6f4ed"/>',
        text(30,38,'Clutch thrust mechanism | catalogue arrangement and native reconstruction',26),
        text(30,72,'Independent panel scales; original source orientation retained. Ball count/diameter printed; race and cage dimensions estimated.',18),
        text(30,120,'Full SNL Plate21: engine left, transmission right'),embed(snl,20,140,1010,740),
        text(1060,120,'Source detail: 28 collar, 29 balls, 4 stop ring'),embed(out/'source_detail.png',1050,140,720,500),
        text(30,920,'Native upper section: engine right'),embed(out/'contact_detail.png',20,940,880,495),
        text(930,920,'Native mechanism with spring-stop ring hidden'),embed(out/'race_open.png',910,940,870,495)]
    notes=['The native retains separate SH998B collar, SH998C retainer,30steel balls and SH998A stop ring. Assembly headings are not extra solids.',
        'The source-informed annular arrangement now has opposing axial race surfaces. The rounded groove section and thin perforated cage are estimates.',
        'The stop ring has a provisional six-hole pattern for future spring plungers. That receiving system, cone attachments and preload remain unfinished.',
        'No drawing calibration is inferred from this comparison. Ball diameter is the printed quarter inch; pitch circle and axial stations remain assumptions.',
        'Static geometry and exchange checks do not qualify bearing loads, historic fits, cage manufacture, assembly sequence or full clutch operation.']
    for n,note in enumerate(notes):svg.append(text(30,1475+34*n,note,18))
    svg.append('</svg>');path=out/'comparison.svg';path.write_text(''.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as page:page[0].get_pixmap().save(str(path.with_suffix('.png')))
    images=['isometric','mechanism','race_open','cage','section','contact_detail','comparison']
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        helper_sha256=sha(HERE/'detail_render.py'),base_renderer_sha256=sha(STAGE/'lib/visual_review.py'),
        source_sha256=sha(snl),source_path=str(snl.relative_to(ROOT)),inspection_viewport=[320,635,590,800],
        deflection_mm=.04,metrology_claim=False,image_hashes={n+'.png':sha(out/(n+'.png')) for n in images},
        notes=notes))
    (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch thrust source comparison</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}</style><h1>Clutch thrust mechanism</h1><p>Catalogue identities and count; estimated race and cage geometry. Opposite source/model orientations and independent scales are preserved.</p><img src="comparison.png" alt="Full SNL figure, source detail, native axial section and exposed balls"><p><a href="render_receipt.json">Evidence, hashes and limits</a></p></html>')
    print('Rendered seven fine native/source review images; native geometry unchanged.',flush=True)
finally:
    runtime.close()
