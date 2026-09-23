"""Explain the four pairs removed by tighter cage bounding boxes after STEP repair."""
import hashlib
import json
from pathlib import Path
import sys

import FreeCAD as App

root = Path('/home/cyapp/MarkVIIILiberty')
stage = root / 'cad/003_FullTank'
sys.path.insert(0, str(stage))
from lib.cad_build import leaves

work = root / '.work/engine-crankshaft'
current = stage / 'experiments/drive_chains/engine_crankshaft_build'
previous = work / 'spherical_cage_exchange_diagnostic'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())
delta = read(work / 'pair_change.json')
assert delta['old_pairs'] == 521 and delta['new_pairs'] == 517
assert len(delta['removed']) == 4 and not delta['added']
docs = []
try:
    maps = []
    hashes = []
    for folder in [previous, current]:
        native = folder / 'DrivetrainWithEngineCrankshaft.FCStd'
        assert sha(native) == read(folder / 'report.json')['native_sha256']
        hashes.append(sha(native))
        doc = App.openDocument(str(native)); docs.append(doc)
        maps.append({item['id']: item['shape'] for item in leaves(doc.Root)})
    results = []
    for pair in delta['removed']:
        a, b = pair['a'], pair['b']
        first, second = maps[1][a], maps[1][b]
        expected_gap = .5 if 'Sleeve' in a + b else 3.5
        gap = first.distToShape(second)[0]
        material = abs(first.common(second).Volume)
        assert abs(gap - expected_gap) < 1e-6 and material < 1e-5
        cage = a if 'Cage' in a else b
        old = maps[0][cage].BoundBox
        new = maps[1][cage].BoundBox
        exact = maps[1][cage].optimalBoundingBox(False)
        assert abs(new.XLength - 3) < 1e-5
        assert abs(exact.XLength - 3) < 1e-5
        assert old.XLength > new.XLength + 1
        results.append(dict(a=a, b=b, gap_mm=gap, expected_gap_mm=expected_gap,
                            overlap_mm3=material, old_cage_bbox_x_mm=[old.XMin, old.XMax],
                            current_cage_bbox_x_mm=[new.XMin, new.XMax],
                            current_cage_trimmed_x_mm=[exact.XMin, exact.XMax]))
    receipt = dict(passed=True, previous_native_sha256=hashes[0], native_sha256=hashes[1],
                   old_pairs=521, new_pairs=517, checks=results,
                   explanation='Same spherical pocket material, tighter conservative axial cage bounds. All four removed candidate pairs are geometrically separated; no interference was skipped.')
    (work / 'cage_pair_bounds.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)
finally:
    for doc in reversed(docs):
        App.closeDocument(doc.Name)
