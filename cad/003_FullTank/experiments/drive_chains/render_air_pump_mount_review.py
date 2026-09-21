"""Preserve honest source/context comparisons and the conditional belt construction."""
import argparse,base64,math,subprocess,sys
from pathlib import Path
import fitz
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'air_pump_mount_build')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve();view=out/'source_review';view.mkdir(parents=True,exist_ok=True)
r=read(out/'report.json');d=r['details'];c=r['controls'];sources=read(HERE/'air_pump_mount_sources.json')
for path,h in sources['source_assets'].items():assert sha(REPO/path)==h,path
native=out/'TransmissionWithAirPump.FCStd';assert sha(native)==r['native_sha256']
from lib import runtime
if not a.worker:
    with (view/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],
            env=runtime.environment(view),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    selected=[];COLORS.update(Pump=(.66,.54,.30),Bracket=(.43,.57,.47),Hardware=(.66,.67,.69))
    for item in items:
        n=item['id']
        if n in r['new_ids'] or n.startswith(('InputHousing_','InputMount_','InputFeed_')) or n=='CenterTransmissionCore_bevel_cover':
            system='Pump' if n.startswith('AirPump_') else ('Bracket' if n.endswith('Bracket') else ('Hardware' if n.startswith('PumpMount_') else item['system']))
            selected.append(dict(item,system=system))
    shaded(selected,view/'source_orientation.svg',(1,-1,.65),
        'Pump installation | opposite isometric for handbook comparison; support geometry inferred')
finally:runtime.close()
def img(path,x,y,w,h):
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"/>'
def save(name,svg):
    path=view/(name+'.svg');path.write_text(svg)
    with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
hb=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate15.png'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1120"><rect width="1800" height="1120" fill="#f7f5ed"/>',
     '<g font-family="sans-serif" fill="#222"><text x="25" y="35" font-size="25">Pump installation | source view and current mounting hypothesis</text>',
     '<text x="25" y="65" font-size="17">Different perspectives and scales; source image is not warped or presented as dimensional verification.</text>',
     '<text x="25" y="110" font-size="20">Handbook Plate15: pump, drive belt and a partially visible support</text>',
     '<text x="840" y="110" font-size="20">Saved native model: inferred supports; driver and belt absent</text></g>',
     img(hb,25,130,760,810),img(view/'source_orientation.png',810,140,970,740),
     '<g font-family="sans-serif" font-size="18" fill="#333">',
     '<text x="30" y="975">Common features: four-cylinder pump, grooved pulley, longitudinal base ledges and downward belt route.</text>',
     '<text x="30" y="1008">Unresolved: source obscures the mounting frame; selected tall webs and stepped studs are inferred, not traced.</text>',
     '<text x="30" y="1041">The new height follows a conditional54-inch belt construction. Exact drive diameter, shaft datum and belt convention remain open.</text>',
     '<text x="30" y="1074">Pump barrel/casting profiles retain the core review discrepancies. Air lines and clutch-stop mechanism are still absent.</text></g></svg>']
save('source_comparison','\n'.join(svg))
# A diagram makes the unresolved drive dependency visible without creating a
# fake physical pulley or counting the belt as completed vehicle geometry.
b=d['belt'];cc=b['center_distance'];pr=b['pump_pitch_radius'];dr=b['drive_pitch_radius'];alpha=math.asin((dr-pr)/cc)
scale=1.65;ox=410;oy=910
def point(y,z):return ox+y*scale,oy-z*scale
def circle(radius,height,color):
    x,y=point(0,height)
    return f'<circle cx="{x}" cy="{y}" r="{radius*scale}" fill="none" stroke="{color}" stroke-width="2"/>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="1120"><rect width="1320" height="1120" fill="#f7f5ed"/>',
    '<g font-family="sans-serif" fill="#222"><text x="25" y="35" font-size="25">Conditional open-belt construction | not installed belt geometry</text>',
    '<text x="25" y="66" font-size="18">SNL18:011 gives54in length,5/8in width and28degrees. Length reference is unspecified.</text></g>',
    circle(pr,cc,'#945f1b'),circle(dr,0,'#5f6985')]
for sign in [-1,1]:
    p1=point(sign*dr*math.cos(alpha),dr*math.sin(alpha));p2=point(sign*pr*math.cos(alpha),cc+pr*math.sin(alpha))
    svg.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#333" stroke-width="3"/>')
svg += ['<g font-family="sans-serif" font-size="19" fill="#333">',
    f'<text x="690" y="180">Pump pitch radius assumed: {pr:.3f}mm</text>',
    f'<text x="690" y="214">Driver pitch radius assumed: {dr:.3f}mm</text>',
    f'<text x="690" y="248">Derived center distance: {cc:.3f}mm</text>',
    f'<text x="690" y="282">Provisional belt plane: coreX{b["plane_x"]:.3f}mm</text>',
    '<text x="690" y="330">Same radial shift on both reference circles:</text>']
for i,row in enumerate(b['radius_scenarios']):
    svg.append(f'<text x="690" y="365" transform="translate(0,{i*34})">{row["radial_shift"]:+.1f}mm gives center {row["center"]:.3f}mm</text>')
svg += ['<text x="690" y="510">These are sensitivity scenarios, not tolerances.</text>',
    '<text x="690" y="545">No belt or driver is counted as a physical part.</text>',
    '<text x="690" y="580">Clutch construction must resolve this dependency.</text></g></svg>']
save('belt_datum_study','\n'.join(svg))
write(view/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
    source_dossier_sha256=sha(HERE/'air_pump_mount_sources.json'),source_sha256=sha(hb),
    source_warped=False,matched_scale=False,rasters={p.name:sha(p) for p in view.glob('*.png')}))
print('Saved source comparison and conditional belt diagram.')
