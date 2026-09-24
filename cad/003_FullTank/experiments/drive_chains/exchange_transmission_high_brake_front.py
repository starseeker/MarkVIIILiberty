"""Export and strictly compare twelve new/revised definitions and all 59 affected installed components."""
import argparse
import math
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
import Import
from lib.mass_properties import AdaptiveMass
from lib.step_matching import StepSolidMatcher
from lib.partitioned_mass import PartitionedMass
mass = AdaptiveMass(out / 'adaptive_mass_runtime')
partitioned = PartitionedMass(mass, out / 'partitioned_mass_runtime')
Part.setStaticValue('write.surfacecurve.mode', 1)

def definition(name):
    d = m['definitions'][name]
    f = Path(d['brep_path'])
    assert sha(f) == d['brep_sha256']
    s = Part.Shape()
    s.read(str(f))
    assert s.Placement.isIdentity()
    return s

definitions = {name: definition(name) for name in sorted(set(r['changed_definitions']) | set(r['new_definitions']))}
installed = {}
installed_names = set(r['affected_occurrences'])
assert len(definitions)==12 and len(installed_names)==59
for name in sorted(installed_names):
    row = rows[name]
    s = definition(row['definition'])
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    installed[name] = s
results = []
files = {}
representations = {}
for scope, shapes in [('Definitions', definitions), ('Installation', installed)]:
    path = out / ('HighBrakeFront' + scope + '.step')
    # Keep a representation per component. A flat TopoShape export shares one
    # uncertainty context; here that changed the track lug's imported tolerance.
    # The retained diagnostic verifies the same unchanged BReps as products.
    doc = App.newDocument('HighBrakeFrontExchange'+scope)
    try:
        features = []
        for name, s in shapes.items():
            obj = doc.addObject('PartDesign::Feature', name)
            obj.Label = name
            obj.Shape = s
            features.append(obj)
        doc.recompute()
        Import.export(features, str(path))
    finally:
        App.closeDocument(doc.Name)
    step_text = path.read_text()
    representations[path.name] = dict(component_uses=step_text.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE'),
                                     uncertainty_contexts=step_text.count('UNCERTAINTY_MEASURE_WITH_UNIT'),
                                     pcurves=step_text.count('PCURVE('))
    assert representations[path.name]['component_uses'] == len(shapes)
    assert representations[path.name]['pcurves'] > 0
    imported = Part.Shape()
    imported.read(str(path))
    assert imported.isValid() and len(imported.Solids) == len(shapes)
    matcher = StepSolidMatcher(imported.Solids)
    for name, one in shapes.items():
        assert len(one.Solids) == 1
        centroid = one.Solids[0].CenterOfMass
        # Do not assume that STEP preserves compound child order. Each selected
        # solid must subsequently pass complete bidirectional material checks.
        index, two = matcher.pop(one)
        ta, tb = one.getTolerance(1), two.getTolerance(1)
        missing, added = one.cut(two), two.cut(one)
        fuzzy = min(1e-4, max(1e-7, ta + tb))
        fm, fa = len(one.cut(two, fuzzy).Faces), len(two.cut(one, fuzzy).Faces)
        ma, mb = mass.measure(one), mass.measure(two)
        initial_mass = None
        if (name in ['Def_HighBrake_anchor_end','Def_HighBrakeFront_long_end'] or name.endswith(('HighSpeedBrakeAnchorEnd','HighSpeedBrakeLongFrontEnd'))) and not (ma['converged'] and mb['converged']):
            initial_mass = dict(native=ma, step=mb)
            frame = App.Placement() if scope == 'Definitions' else App.Placement(App.Matrix(*rows[name]['frame']))
            ma, mb = partitioned.measure(one, frame), partitioned.measure(two, frame)
        dc = math.dist(ma['centroid_mm'], mb['centroid_mm'])
        row = dict(native_mass=ma, step_mass=mb, initial_whole_mass=initial_mass, adaptive_centroid_error_mm=dc, scope=scope, name=name, imported_solid_index=index,
                   missing_mm3=missing.Volume, added_mm3=added.Volume,
                   fuzzy_missing_faces=fm, fuzzy_added_faces=fa,
                   native_tolerance_mm=ta, step_tolerance_mm=tb,
                   centroid_error_mm=(centroid - two.CenterOfMass).Length,
                   passed=one.isValid() and two.isValid() and len(one.Solids) == len(two.Solids) == 1 and
                          abs(missing.Volume) < 1e-5 and abs(added.Volume) < 1e-5 and not fm and not fa and
                          ta <= 1e-4 and tb <= max(ta, 1e-7) + 1e-10 and
                          ma['converged'] and mb['converged'] and dc < 1e-5)
        results.append(row)
        write(out / 'exchange_progress.json', results)
        print(scope, name, row['passed'], flush=True)
    assert not len(matcher)
    files[path.name] = sha(path)
assert len(results) == 71
write(out / 'exchange_checks.json', dict(passed=all(v['passed'] for v in results),
    native_sha256=sha(native), checker_sha256=sha(Path(__file__)), checks=results,
    step_hashes=files, mass_provenance=mass.provenance, partitioned_mass_provenance=partitioned.provenance, export_settings={'write.surfacecurve.mode': 1,
        'writer': 'Import.export', 'input': 'one named PartDesign::Feature per component'},
    step_representations=representations,
    scope='Twelve new/revised definitions and all 59 affected occurrences; adaptive converged mass integration and unchanged strict material/tolerance criteria. Not a complete brake mechanism or full-tank export.',
    installation_qualified=False))
assert all(v['passed'] for v in results), 'Preserve failed STEP evidence and diagnose without relaxing tolerances.'
