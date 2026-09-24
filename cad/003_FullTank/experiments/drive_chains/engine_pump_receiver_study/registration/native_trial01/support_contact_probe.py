"""Measure actual rail/bracket contacts, separately from floor packing datums."""
import json
import hashlib
from pathlib import Path
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent
RECEIVER = OUT.parents[1]

def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()

def read(path):
    return json.loads(path.read_text())

r = read(OUT / 'report.json')
current = read(OUT / 'isolated/manifest.json')
source = read(RECEIVER / 'assembly_trial02/isolated/candidate/manifest.json')
assert current['native_sha256'] == digest(OUT / r['native_file'])
assert source['native_sha256'] == r['source_native_sha256']
pairs = [('EngineSuspension_LeftRail', 'EngineSuspension_LeftBracket'),
         ('EngineSuspension_RightRail', 'EngineSuspension_RightBracket'),
         ('EngineSuspension_LeftRail', 'EngineSuspension_FrontBracket'),
         ('EngineSuspension_RightRail', 'EngineSuspension_FrontBracket')]
rows = []
for scope, m in [('source', source), ('candidate', current)]:
    items = {v['name']: v for v in m['occurrences']}
    def shape(name):
        row = items[name]
        d = m['definitions'][row['definition']]
        f = Path(d['brep_path'])
        assert digest(f) == d['brep_sha256']
        s = Part.Shape()
        s.read(str(f))
        s.Placement = App.Placement(App.Matrix(*row['frame']))
        return s
    for left, right in pairs:
        one, two = shape(left), shape(right)
        volume = one.common(two).Volume if one.BoundBox.intersect(two.BoundBox) else 0
        rows.append(dict(scope=scope, rail=left, bracket=right,
                         gap_mm=one.distToShape(two)[0], common_mm3=volume))
(OUT / 'support_contacts.json').write_text(json.dumps(dict(
    script_sha256=digest(Path(__file__)), source_native_sha256=source['native_sha256'],
    candidate_native_sha256=current['native_sha256'], contacts=rows,
    installation_qualified=False), indent=2) + '\n')
print(json.dumps(rows), flush=True)
