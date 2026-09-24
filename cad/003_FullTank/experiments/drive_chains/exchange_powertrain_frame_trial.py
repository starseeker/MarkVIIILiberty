"""Export and strictly compare rebuilt transmission castings and installed frame joints."""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
m = read(out / 'isolated/manifest.json')
native = out / r['native_file']
assert sha(native) == m['native_sha256'] == r['native_sha256']
rows = {v['name']: v for v in m['occurrences']}

import FreeCAD as App
import Part
Part.setStaticValue('write.surfacecurve.mode', 1)

def definition(name):
    d = m['definitions'][name]
    f = Path(d['brep_path'])
    assert sha(f) == d['brep_sha256']
    s = Part.Shape()
    s.read(str(f))
    assert s.Placement.isIdentity()
    return s

definitions = {name: definition(name) for name in r['replacement_definitions']}
installed = {}
installed_names = {name for names in r['replacement_definitions'].values() for name in names}
installed_names.update(r['mount_occurrence_frames'])
installed_names.update(['TransmissionFrame_TopChannel', 'TransmissionFrame_BottomChannel'])
assert len(installed_names) == 23
for name in sorted(installed_names):
    row = rows[name]
    s = definition(row['definition'])
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    installed[name] = s
results = []
files = {}
for scope, shapes in [('Definitions', definitions), ('Installation', installed)]:
    path = out / ('TransmissionSupports' + scope + '.step')
    Part.makeCompound(list(shapes.values())).exportStep(str(path))
    imported = Part.Shape()
    imported.read(str(path))
    assert imported.isValid() and len(imported.Solids) == len(shapes)
    available = list(enumerate(imported.Solids))
    for name, one in shapes.items():
        assert len(one.Solids) == 1
        centroid = one.Solids[0].CenterOfMass
        # Do not assume that STEP preserves compound child order. Each selected
        # solid must subsequently pass complete bidirectional material checks.
        i, (index, two) = min(enumerate(available), key=lambda pair:
            (pair[1][1].CenterOfMass - centroid).Length + abs(pair[1][1].Volume - one.Volume) / max(one.Volume, 1))
        available.pop(i)
        ta, tb = one.getTolerance(1), two.getTolerance(1)
        missing, added = one.cut(two), two.cut(one)
        fuzzy = min(1e-4, max(1e-7, ta + tb))
        fm, fa = len(one.cut(two, fuzzy).Faces), len(two.cut(one, fuzzy).Faces)
        row = dict(scope=scope, name=name, imported_solid_index=index,
                   missing_mm3=missing.Volume, added_mm3=added.Volume,
                   fuzzy_missing_faces=fm, fuzzy_added_faces=fa,
                   native_tolerance_mm=ta, step_tolerance_mm=tb,
                   centroid_error_mm=(centroid - two.CenterOfMass).Length,
                   passed=one.isValid() and two.isValid() and len(one.Solids) == len(two.Solids) == 1 and
                          abs(missing.Volume) < 1e-5 and abs(added.Volume) < 1e-5 and not fm and not fa and
                          ta <= 1e-4 and tb <= max(ta, 1e-7) + 1e-10 and
                          (centroid - two.CenterOfMass).Length < 1e-5)
        results.append(row)
        write(out / 'exchange_progress.json', results)
        print(scope, name, row['passed'], flush=True)
    assert not available
    files[path.name] = sha(path)
assert len(results) == 26
write(out / 'exchange_checks.json', dict(passed=all(v['passed'] for v in results),
    native_sha256=sha(native), checker_sha256=sha(Path(__file__)), checks=results,
    step_hashes=files, export_settings={'write.surfacecurve.mode': 1},
    scope='Three rebuilt casting definitions plus five installed castings, 16 MX5 joint constituents and two retained frame channels; not a full-tank export.',
    installation_qualified=False))
assert all(v['passed'] for v in results), 'Preserve failed STEP evidence and diagnose without relaxing tolerances.'
