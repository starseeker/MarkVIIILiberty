"""Extract actual standard-tank leaves and definition shapes for read-only fit studies."""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(STAGE)]
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--native', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
native, out = a.native.resolve(), a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
assert not (out / 'manifest.json').exists(), 'Use a fresh output directory.'
inputs = {str(f.relative_to(ROOT)): sha(f) for f in native.parent.rglob('*.FCStd')}

import FreeCAD as App
import Part
from lib.cad_build import leaves

doc = App.openDocument(str(native))
items = leaves(doc.Root)
assert len(items) == 5341
definitions, rows = {}, []
breps = out / 'breps'
breps.mkdir()
for item in items:
    target = item['target']
    key = item['definition']
    if key not in definitions:
        shape = target.Shape.copy()
        # Extract a shape in its own coordinates; occurrence frames below retain
        # the fully composed placement supplied by the qualified tank traversal.
        shape.Placement = App.Placement()
        path = breps / (key + '.brep')
        shape.exportBrep(str(path))
        definitions[key] = dict(brep_path=str(path), brep_sha256=sha(path),
            source_document=str(Path(target.Document.FileName).relative_to(ROOT)),
            source_object=target.Name, solids=len(shape.Solids),
            representation=item['representation'], coverage=item['coverage'])
    shape = item['shape']
    b = shape.BoundBox
    rows.append(dict(name=item['id'], definition=key, frame=list(shape.Placement.toMatrix().A),
        system=item['system'], representation=item['representation'], coverage=item['coverage'],
        bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax], solids=len(shape.Solids)))
opened = {str(Path(d.FileName).relative_to(ROOT)): sha(Path(d.FileName))
          for d in App.listDocuments().values() if d.FileName}
assert all(path in inputs and inputs[path] == digest for path, digest in opened.items())
for name in list(App.listDocuments()):
    App.closeDocument(name)
assert all(sha(ROOT / f) == digest for f, digest in inputs.items())
write(out / 'manifest.json', dict(native_sha256=sha(native), native=str(native.relative_to(ROOT)),
    extractor_sha256=sha(Path(__file__)), traversal_sha256=sha(STAGE / 'lib/cad_build.py'),
    native_files=inputs, opened_documents=opened, definitions=definitions, occurrences=rows,
    scope='All saved standard leaves, including explicitly labeled layout envelopes; no native modification.'))
print('Extracted standard context:', len(items), 'leaves and', len(definitions), 'definitions', flush=True)
