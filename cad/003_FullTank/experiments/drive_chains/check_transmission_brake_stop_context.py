"""Compare all changed stop components with retained standard-tank material."""
import argparse
from pathlib import Path
import sys
import numpy as np
import FreeCAD as App
import Part

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--standard-manifest', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
m = read(out / 'isolated/manifest.json')
standard = read(a.standard_manifest)
assert sha(out / r['native_file']) == r['native_sha256'] == m['native_sha256']
assert all(sha(ROOT / f) == digest for f, digest in standard['native_files'].items())
rows, tank = [{v['name']: v for v in data['occurrences']} for data in (m, standard)]
cache = {}

def shape(row, manifest):
    rec = manifest['definitions'][row['definition']]
    path = Path(rec['brep_path'])
    assert sha(path) == rec['brep_sha256']
    if rec['brep_sha256'] not in cache:
        s = Part.Shape(); s.read(str(path))
        assert s.Placement.isIdentity()
        cache[rec['brep_sha256']] = s
    s = cache[rec['brep_sha256']].copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s

def bounds(s):
    b = s.BoundBox
    return np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])

# Same documented obsolete stand-ins as the qualified front-brake context.
excluded = (set(rows) & set(tank)) | {'PortPinion_Rotor_Casting', 'StarboardPinion_Rotor_Casting'}
context = {n: shape(row, standard) for n, row in tank.items()
           if n not in excluded and row['representation'] == 'assembly'}
names = sorted(context)
boxes = np.array([bounds(context[n]) for n in names])
records = []
for name in r['affected_occurrences']:
    one = shape(rows[name], m); box = bounds(one)
    possible = np.where(np.all(boxes[:, :3] <= box[3:]+1e-7, axis=1)
                        & np.all(boxes[:, 3:] >= box[:3]-1e-7, axis=1))[0]
    for i in possible:
        common = one.common(context[names[i]])
        valid = common.isNull() or common.isValid()
        volume = sum(abs(s.Volume) for s in common.Solids)
        records.append(dict(first=name, second=names[i], common_mm3=volume,
                            valid_common=valid, passed=valid and volume < 1e-5))
    write(out / 'standard_material_progress.json', records)
result = dict(passed=all(v['passed'] for v in records), pairs=records,
              standard_context_count=len(context), affected_count=len(r['affected_occurrences']),
              excluded_standard_occurrences=sorted(excluded & set(tank)),
              standard_manifest_sha256=sha(a.standard_manifest),
              native_sha256=r['native_sha256'], checker_sha256=sha(Path(__file__)),
              scope='All affected stop/bearing occurrences against retained standard tank011 material; excludes replaced stand-ins. Development-context and historical checks are separate.',
              standard_assembly_modified=False, installation_qualified=False)
write(out / 'standard_context_checks.json', result)
print('Retained standard', len(context), 'affected', len(r['affected_occurrences']),
      'nearby pairs', len(records), 'passed', result['passed'], flush=True)
assert result['passed']
