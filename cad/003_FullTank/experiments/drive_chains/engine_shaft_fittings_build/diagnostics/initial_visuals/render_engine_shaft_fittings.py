"""Render native closure geometry and sections alongside original source assets."""
import argparse
import os
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

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, default=HERE/'engine_shaft_fittings_build')
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
    from lib.cad_build import leaves, COLORS
    from detail_render import shaded_detail

    V = App.Vector
    native = base/'DrivetrainWithEngineShaftFittings.FCStd'
    r = read(base/'report.json')
    assert sha(native) == r['native_sha256']
    doc = App.openDocument(str(native))
    byid = {i['id']: i for i in leaves(doc.Root)}
    origin = doc.TankLibertyEngine.Placement.Base
    COLORS.update(Casting=(.62, .68, .67), Shaft=(.44, .49, .53), Bearing=(.77, .67, .41),
                  Cap=(.66, .69, .71), Gasket=(.78, .51, .27), Stud=(.36, .43, .48),
                  Hardware=(.61, .64, .67), Context=(.43, .54, .60))
    names = []

    def draw(selected, name, title, direction, clip=None):
        items = []
        for n in selected:
            row = byid[n]
            s = row['shape'].copy()
            if clip is not None:
                s = s.common(clip)
            if s.isNull() or not s.Solids:
                continue
            color = 'Context'
            if n.startswith('EngineCase_'):
                color = 'Casting'
            elif n == 'EngineCrank_Forging':
                color = 'Shaft'
            elif n.startswith('EngineCrank_'):
                color = 'Bearing'
            elif n.startswith('ShaftClosure_'):
                color = 'Gasket' if ('Gasket' in n or 'Seal' in n) else ('Stud' if 'Stud' in n else ('Cap' if 'Cap' in n or 'Plug' in n else 'Hardware'))
            items.append(dict(row, shape=s, target=SimpleNamespace(Shape=s), definition=n, system=color))
        shaded_detail(items, out/(name+'.svg'), direction, title, deflection=.06)
        names.append(name)
        print('Rendered', name, flush=True)

    closures = r['new_ids']
    crank = [n for n in byid if n.startswith('EngineCrank_')]
    frame = [n for n in byid if n.startswith(('EngineFrame_', 'EngineSuspension_'))]
    draw(crank+closures+['EngineCase_lower']+frame, 'isometric',
         'Crankshaft closures installed | upper case hidden for review; cylinders and gear pending', (.45, .6, 1))
    draw(['EngineCrank_Forging']+closures, 'shaft',
         'Hollow shaft with 139 closure and retaining constituents | profiles and recesses estimated', (.4, 1, .65))
    for name in ['Pin6', 'Main2', 'Gear']:
        pair = next(x for x in r['datums']['pairs'] if x['name'] == name)
        lo, hi = pair['outer_faces']
        clip = Part.makeBox(hi-lo+40, 150, 220, V(lo-20, 0, -110))
        rotation = App.Rotation(V(1, 0, 0), pair['roll_deg'])
        clip.Placement = App.Placement(origin+V(*pair['center']), rotation).multiply(clip.Placement)
        selection = ['EngineCrank_Forging']+[n for n in closures if n.startswith('ShaftClosure_'+name+'_')]
        if name == 'Pin6':
            selection.append('ShaftClosure_OilPlug6')
        draw(selection, name.lower()+'_section', name+' retaining set | section exposes cap seats, gaskets and source-length stud',
             tuple(rotation.multVec(V(.06, -1, .3))), clip)
    pd = r['parent_datums']
    tip = pd['taper']['rear']-r['parent_controls']['output_thread_length']
    clip = Part.makeBox(35-tip, 100, 160, origin+V(tip-5, 0, -80))
    draw(['EngineCrank_Forging', 'ShaftClosure_NosePlug', 'EngineCrank_FlywheelKey',
          'EngineCrank_FlywheelKeyScrew', 'EngineCrank_OutputNut', 'EngineCrank_OutputCotter'],
         'nose_section', 'Nose section | plug clears cotter; reduced cavity leaves a blind key-screw receiver', (0, -1, .3), clip)
    # Cut in the radial plane of the first throw to expose its rear-web drill.
    pin = pd['crankpin_stations'][0]
    rotation = App.Rotation(V(1, 0, 0), -pin['phase_deg'])
    wx = next(x['start'][0] for x in pd['oil_passages'] if x['kind'] == 'rear_web')
    clip = Part.makeBox(80, 150, 180, V(wx-40, 0, -25))
    clip.Placement = App.Placement(origin, rotation).multiply(clip.Placement)
    selection = ['EngineCrank_Forging', 'ShaftClosure_OilPlug6']+[n for n in closures if n.startswith(('ShaftClosure_Pin6_', 'ShaftClosure_Main2_'))]
    draw(selection, 'oil_web_section', 'Rear-web oil route | shallow rear cap leaves passage open; external access plugged', tuple(rotation.multVec(V(.12, -1, .18))), clip)
    sources = ROOT/'references/1918-09_12_Cylinder_Liberty_Aero_Engine/Liberty_Project/assets'
    comparisons = ''
    source_hashes = {}
    for figure, view in [(17, 'isometric'), (107, 'shaft')]:
        path = sources/('figure_%03d_original.png' % figure)
        source_hashes[str(path.relative_to(ROOT))] = sha(path)
        comparisons += '<h2>Liberty figure '+str(figure)+' / '+view+'</h2><div class="comparison"><img src="'+os.path.relpath(path, out)+'"><img src="'+view+'.png"></div>'
    for page in [156, 212, 239, 240]:
        path = ROOT/('references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p%03d.jpg' % page)
        source_hashes[str(path.relative_to(ROOT))] = sha(path)
        comparisons += '<p><a href="'+os.path.relpath(path, out)+'">Original SNL page '+str(page)+'</a></p>'
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Liberty shaft closures</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.comparison{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:16px}</style><h1>Liberty shaft closure development</h1><p>Source-owned inventory with provisional profiles, recesses and thread envelopes. SNL supplies piece identities and stud sizes; the aviation photographs do not establish every hidden cap profile. Source/model cameras are not registered. Review cuts and hidden upper case do not modify the physical model. Source conflicts and fit assumptions are retained in the dossier. Driving gear, shims, thrust lock, cylinders, rods and engine services remain pending.</p>'+comparisons+''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
    write(out/'render_receipt.json', dict(native_sha256=sha(native), renderer_sha256=sha(Path(__file__)),
        images={n+'.png': sha(out/(n+'.png')) for n in names}, source_assets=source_hashes,
        model_modified=False, source_camera_fit=False))
finally:
    runtime.close()
