"""Native static phase screen at the provisional source-picked pinion axis."""
from pathlib import Path
import math
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
STAGE = ROOT.parents[1]
OUT = ROOT / 'phase_build'
sys.path.insert(0, str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable, __file__, '--worker'],
                            env=environment(OUT)).returncode)

import FreeCAD as App
import Part
from lib.evidence import read, write, sha, fingerprint
from lib.model import load, point, datum_values
from lib.visual_review import shaded

lock = fingerprint()
data = load()
rotor_path = ROOT/'pin_build/PinionWithPins.FCStd'
library_path = STAGE/'build/native/library/RunningGear.FCStd'
assert sha(rotor_path) == read(ROOT/'pin_build/report.json')['native_sha256']
native_inputs = {str(p.relative_to(STAGE)): sha(p) for p in [rotor_path, library_path]}
rotor = App.openDocument(str(rotor_path))
library = App.openDocument(str(library_path))
rim = library.Def_drive_rim.Shape.copy()
rim.translate(App.Vector(0, 190, 0))
roller = rotor.Def_Roller.Shape.copy()
a = read(ROOT/'rotor_build/hypotheses.json')['values_mm']
source = point(data, 'snl_2', [1614, 422])
drive = datum_values('port_drive', data)['translation']
center = App.Vector(source[0]-drive[0], 0, source[1]-drive[2])

def bank(phase):
    for n in range(9):
        angle = math.radians(phase+n*40)
        s = roller.copy()
        s.translate(center+App.Vector(a['roller_circle']*math.sin(angle),
                                     a['bank_center'], a['roller_circle']*math.cos(angle)))
        yield n, s

rows = []
for phase in [n*.5 for n in range(80)]:
    pairs = []
    for n, s in bank(phase):
        if s.BoundBox.intersect(rim.BoundBox):
            volume = s.common(rim).Volume
            gap = s.distToShape(rim)[0] if volume < 1e-5 else 0.
            pairs.append(dict(roller=n, overlap_mm3=volume, material_gap_mm=gap))
    assert pairs
    row = dict(phase_deg=phase, overlap_mm3=sum(p['overlap_mm3'] for p in pairs),
               minimum_gap_mm=min(p['material_gap_mm'] for p in pairs), pairs=pairs)
    rows.append(row)
    if len(rows) % 10 == 0:
        print('Measured', len(rows), 'of 80 phases', flush=True)
        write(OUT/'partial.json', rows)

clear = [r for r in rows if r['overlap_mm3'] < 1e-5]
# A static pose with room for inferred/source uncertainty, not contact tuning.
selected = max(clear, key=lambda r:r['minimum_gap_mm']) if clear else min(rows, key=lambda r:r['overlap_mm3'])
doc = App.newDocument('PinionPhaseStudy')
items = []
def add(name, shape):
    o = doc.addObject('PartDesign::Body', name)
    o.newObject('PartDesign::Feature', 'Measured'+name).Shape = shape
    items.append(dict(id=name, definition=name, target=o, shape=shape,
                      system='RunningGear', representation='assembly'))
add('DriveRim', rim)
for n, s in bank(selected['phase_deg']):
    add('Roller'+str(n), s)
doc.recompute()
for item in items:
    item['shape'] = item['target'].Shape.copy()
path = OUT/'PinionPhaseStudy.FCStd'
doc.saveAs(str(path))
shaded(items, OUT/'axial.svg', (0, 1, 0),
       'Native static phase screen | source-picked axes | continuous engagement unqualified')
write(OUT/'report.json', dict(status='unaccepted_static_pinion_phase_screen',
    checks_completed=True, phase_samples=80, nonintersecting_samples=len(clear),
    selected=selected, samples=rows, relative_axis_mm=list(center),
    source_pixel=[1614, 422], pick_uncertainty_pixels=3,
    main_model_changed=False, source_pick_changed=False, native_inputs=native_inputs,
    authored_fingerprint=lock, script_sha256=sha(__file__), native_sha256=sha(path),
    render_sha256=sha(OUT/'axial.png'), visual_review_status='pending',
    selected_static_pose_qualified=False, complete_rotor_checked=False,
    continuous_engagement_qualified=False,
    limitations=['One bank against one aligned driving ring only.',
                 'The source 35/37 wheel-tooth conflict remains open.',
                 'Casting, pins, other wheel parts and hull are outside this screen.',
                 'A clear static sample is not evidence of continuous engagement.']))
shutil.copy2(__file__, OUT/'executed_probe.py')
assert fingerprint() == lock
for p, digest in native_inputs.items():
    assert sha(STAGE/p) == digest
for name in list(App.listDocuments()):
    App.closeDocument(name)
print('PASS static phase screen:', len(clear), 'clear samples;', selected, flush=True)
