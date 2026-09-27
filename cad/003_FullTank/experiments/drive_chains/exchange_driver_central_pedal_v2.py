"""Strict central-group exchange using converged standard Gauss on unchanged STEP bytes."""
import argparse
import math
import shutil,tempfile
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part, Import
from lib.evidence import read, write, sha
from lib.mass_properties import AdaptiveMass
from lib.step_matching import StepSolidMatcher
from lib.camera_review import validate_native_bindings

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--receipt-directory', default='exchange02')
a = p.parse_args()
candidate = a.candidate.resolve()
r = read(candidate/'report.json')
m = read(candidate/'isolated/manifest.json')
native = candidate/r['native_file']
out=candidate/a.receipt_directory;out.mkdir(exist_ok=False)
assert sha(native) == m['native_sha256']
assert not (out/'exchange_checks.json').exists()
assert read(candidate/'checks03/independent_checks.json')['passed']
assert read(candidate/'context_audit/report.json')['passed']

validate_native_bindings(dict(native_file=str(native), render_occurrences=[v['name'] for v in m['occurrences']], landmarks=[]), m)
Part.setStaticValue('write.surfacecurve.mode', 1)
App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import').SetBool('ExportKeepPlacement', True)

masses=dict(default=AdaptiveMass(out/'mass_runtime'))
def measure(name,shape):
    result=masses['default'].measure(shape);result['selected_measurement']='default';return result
previous_folder=candidate/'exchange01';previous=read(previous_folder/'exchange_checks.json')
assert previous['native_sha256']==sha(native) and previous['checker_sha256']==sha(H/'exchange_driver_central_pedal.py')
for file,digest in previous['step_hashes'].items():assert sha(previous_folder/file)==digest
cached={(q['scope'],q['name']):q for q in previous['checks'] if q['passed']}
def brep_hash(q):
    with tempfile.TemporaryDirectory(dir=out) as name:
        file=Path(name)/'one.brep';q.exportBrep(str(file));return sha(file)
old=read((H.parents[3]/r['parent_native']).parent/'isolated/manifest.json');prior={v['name']:v for v in old['occurrences']}
definitions = {}
installed = {}

for key, d in m['definitions'].items():
    if key not in r['new_definitions'] and key not in r.get('changed_definitions',[]):continue
    assert sha(d['brep_path']) == d['brep_sha256']
    s = Part.Shape()
    s.read(d['brep_path'])
    definitions[key] = s

for row in m['occurrences']:
    if row['name'] not in r['new_occurrences'] and row['definition'] not in r.get('changed_definitions',[]) and max(abs(x-y) for x,y in zip(row['frame'],prior[row['name']]['frame']))<=1e-7:continue
    entry=m['definitions'][row['definition']]
    assert sha(entry['brep_path']) == entry['brep_sha256']
    s=Part.Shape();s.read(entry['brep_path'])
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    installed[row['name']] = s

checks = []
files = {}

for scope, shapes in [('Definitions', definitions), ('Installed', installed)]:
    path = out/('RebuiltControlAdditions'+scope+'.step')
    assert not path.exists()
    shutil.copy2(previous_folder/path.name,path)
    assert sha(path)==previous['step_hashes'][path.name]

    text = path.read_text()
    assert 'PCURVE(' in text and text.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE') == (0 if len(shapes)==1 else len(shapes))
    recovered = Part.Shape()
    recovered.read(str(path))
    assert recovered.isValid() and len(recovered.Solids) == len(shapes)
    matcher = StepSolidMatcher(recovered.Solids)

    for name, one in shapes.items():
        index, two = matcher.pop(one)
        reuse=cached.get((scope,name))
        if reuse:
            assert index==reuse['step_solid_index'] and brep_hash(one)==reuse['native_mass']['brep_sha256'] and brep_hash(two)==reuse['step_mass']['brep_sha256']
            checks.append(dict(reuse,reused_from_receipt_sha256=sha(previous_folder/'exchange_checks.json')))
            write(out/'exchange_progress.json',checks);print(scope,name,'verified cached pair',flush=True);continue
        ta, tb = one.getTolerance(1), two.getTolerance(1)
        fuzz = min(1e-4, max(1e-7, ta+tb))
        missing, added = one.cut(two), two.cut(one)
        fm, fa = len(one.cut(two, fuzz).Faces), len(two.cut(one, fuzz).Faces)
        ma, mb = measure(name,one), measure(name,two)
        distance = math.dist(ma['centroid_mm'], mb['centroid_mm'])
        passed = (one.isValid() and two.isValid() and len(one.Solids) == len(two.Solids) == 1 and
                  one.Solids[0].isClosed() and two.isClosed() and abs(missing.Volume) < 1e-5 and
                  abs(added.Volume) < 1e-5 and not fm and not fa and ta <= 1e-4 and
                  tb <= max(ta, 1e-7)+1e-10 and ma['converged'] and mb['converged'] and distance < 1e-5)
        checks.append(dict(scope=scope, name=name, passed=passed, step_solid_index=index,
                           missing_mm3=missing.Volume, added_mm3=added.Volume,
                           fuzzy_missing_faces=fm, fuzzy_added_faces=fa,
                           native_tolerance_mm=ta, step_tolerance_mm=tb,
                           native_mass=ma, step_mass=mb, centroid_error_mm=distance))
        write(out/'exchange_progress.json', checks)
        print(scope, name, passed, flush=True)
    assert not len(matcher)
    files[path.name] = sha(path)

write(out/'exchange_checks.json', dict(
    passed=all(v['passed'] for v in checks),
    checks=checks,
    native_sha256=sha(native),
    checker_sha256=sha(Path(__file__)),base_worker_sha256=sha(H/'exchange_driver_central_pedal.py'),prior_receipt_sha256=sha(previous_folder/'exchange_checks.json'),same_step_bytes=True,
    mass_provenance={k:v.provenance for k,v in masses.items()},
    scope='New/revised definitions and new installed occurrences; unchanged receivers preserved and covered by their existing parent qualification.',
    step_hashes=files,
    export_settings={'reused_exact_exports': True, 'write.surfacecurve.mode': 1, 'Mod/Import/ExportKeepPlacement': True, 'installed_export': 'Saved local definition and actual world placement'},
    historical_geometry_qualified=False,
    installation_qualified=False
))
print('Exchange check complete; all passed:', all(v['passed'] for v in checks), flush=True)
assert all(v['passed'] for v in checks)
