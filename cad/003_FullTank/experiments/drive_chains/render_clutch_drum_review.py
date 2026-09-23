"""Render actual drum/flywheel solids, sections and full original figures."""
import argparse
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib import runtime
from lib.evidence import read, write, sha

p = argparse.ArgumentParser()
p.add_argument('--candidate', type=Path, default=HERE/'clutch_drum_build')
p.add_argument('--worker', action='store_true')
a = p.parse_args()
base = a.candidate.resolve()
out = base/'source_review'
out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable, __file__, '--candidate', str(base), '--worker'],
            env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from PIL import Image, ImageDraw, ImageFont
    from lib.cad_build import leaves, COLORS
    from detail_render import shaded_detail

    native = base/'TransmissionWithClutchDrum.FCStd'
    r = read(base/'report.json')
    assert sha(native) == r['native_sha256']
    doc = App.openDocument(str(native))
    byid = {i['id']: i for i in leaves(doc.Root)}
    origin = doc.TransmissionCore.Placement.Base
    COLORS.update(Drum=(.49,.57,.58), Flywheel=(.34,.42,.47), Wire=(.9,.43,.12),
        Lining=(.40,.31,.23), Clutch=(.62,.64,.60), Screw=(.62,.54,.36))

    def draw(names, name, title, direction, clip=None):
        selected = []
        for n in names:
            i = byid[n]
            s = i['shape'].copy()
            s.translate(-origin)
            if clip is not None:
                s = s.common(clip)
            if s.isNull() or not s.Solids:
                continue
            color = 'Clutch'
            if n in ['ClutchDrum_wire', 'ClutchRetention_Wire']: color = 'Wire'
            elif n == 'ClutchDrum_flywheel': color = 'Flywheel'
            elif n == 'ClutchDrum_drum': color = 'Drum'
            elif n.startswith('ClutchDrum_Screw'): color = 'Screw'
            elif n == 'ClutchCone_lining': color = 'Lining'
            selected.append(dict(i, shape=s, target=SimpleNamespace(Shape=s), definition=n, system=color))
        shaded_detail(selected, out/(name+'.svg'), direction, title, deflection=.035)
        print('Rendered', name, flush=True)

    clutch = [n for n in byid if n.startswith(('FrontClutch_', 'ClutchCollar_',
        'ClutchStack_', 'ClutchDrive_', 'ClutchThrust_', 'ClutchCone_', 'ClutchRetention_', 'ClutchDrum_'))]
    context = [n for n in byid if n.startswith(('AirPump_', 'PumpMount_', 'InputHousing_'))
        or n == 'CenterTransmissionCore_bevel_cover']
    draw(clutch+context, 'isometric', 'Outer drum and flywheel installed | saved native geometry', (1,1,.65))
    section = Part.makeBox(700,320,640,App.Vector(400,0,-320))
    draw(clutch, 'axial_section', 'Axial half-section | engine shaft, key and retention still pending', (0,-1,0), section)
    draw(['ClutchDrum_flywheel'], 'flywheel', 'SH868A | tapered/keyed bore, positive-drive hub and starter teeth', (-1,-.6,.45))
    exposed = ['ClutchDrum_flywheel', 'ClutchDrum_wire', 'ClutchRetention_Wire']
    exposed += [f'ClutchDrum_Screw{n}' for n in range(1,7)]
    exposed += [f'ClutchCone_Plunger{n}' for n in range(1,7)]
    draw(exposed, 'wire_clearance', 'Both source-length wires | inward tails clear the dished wheel', (-1,-.18,.3))
    d = r['datums']
    tooth_box = Part.makeBox(48,30,100,App.Vector(d['flywheel_joint']-8,-260,-50))
    draw(['ClutchDrum_flywheel'], 'teeth', 'Starter tooth detail | count and involute form remain estimates', (-1,-1,.4), tooth_box)
    sources = {
        'HB111': ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate111.png',
        'HB71': ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png',
        'SNL21': ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png',
    }
    canvas = Image.new('RGB',(2200,1780),'#f6f4ed')
    pen = ImageDraw.Draw(canvas)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
    pen.text((30,18),'Drum and flywheel: source context and saved native sections',fill='black',font=font)
    def paste(path, rect):
        im = Image.open(path).convert('RGB')
        im.thumbnail(rect[2:])
        canvas.paste(im,(rect[0]+(rect[2]-im.width)//2,rect[1]+(rect[3]-im.height)//2))
    paste(sources['HB111'],(20,65,1080,770))
    paste(out/'axial_section.png',(1110,65,1070,770))
    paste(sources['SNL21'],(20,850,1080,730))
    paste(out/'wire_clearance.png',(1110,850,1070,730))
    notes = [
        'Full HB111 and SNL21; independent scales. SNL faces the opposite direction. No calibrated overlay claim.',
        'HB115 largest diameter 19.811in retained; SNL dashed flywheel outline is proportionally larger.',
        'Long removable splined hub is an interpretation; HB prose instead calls the positive teeth crankshaft teeth.',
        'Drum bend/stock, taper, wire route and 124 starter teeth are estimates. Complete crankshaft and retention remain pending.',
        'Orange highlights soft-metal locking wires; it does not indicate copper. Source cut lengths: 30in and 48in.',
    ]
    for n,line in enumerate(notes): pen.text((30,1600+31*n),line,fill='black',font=small)
    canvas.save(out/'comparison.png')
    images = ['isometric','axial_section','flywheel','wire_clearance','teeth','comparison']
    write(out/'render_receipt.json',dict(native_sha256=sha(native), renderer_sha256=sha(Path(__file__)),
        helper_sha256=sha(HERE/'detail_render.py'), base_renderer_sha256=sha(STAGE/'lib/visual_review.py'),
        source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sources.values()}, deflection_mm=.035,
        metrology_claim=False, image_hashes={n+'.png':sha(out/(n+'.png')) for n in images}, notes=notes))
    (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch drum and flywheel</title>'
        '<style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}</style>'
        '<h1>Clutch drum and flywheel</h1><p>Source-informed reconstruction with documented profile and interface estimates.</p>'
        +''.join(f'<p>{n}</p><img src="{n}.png" alt="{n}">' for n in ['comparison']+images[:-1])
        +'<p><a href="render_receipt.json">Evidence and image hashes</a></p></html>')
finally:
    runtime.close()
