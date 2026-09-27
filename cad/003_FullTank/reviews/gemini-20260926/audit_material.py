"""Read-only review: measure all contacts, including pairs excluded by candidates.

No mating exemptions are applied. Numerical positive intersections are findings
for review, not assertions that every designed contact is invalid. No source
native, BRep, checker or existing receipt is modified.
"""
import argparse
import itertools
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path('/home/cyapp/MarkVIIILiberty')
H = ROOT/'cad/003_FullTank/experiments/drive_chains'
C = H/'transmission_controls_study'
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings

p = argparse.ArgumentParser()
p.add_argument('--scope', choices=['branch', 'front'], required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
candidate = C/('forward_rods_integrated01' if a.scope == 'branch' else 'front_controls01')
r, m = read(candidate/'report.json'), read(candidate/'isolated/manifest.json')
native = candidate/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
base = C/('pin_family_integrated01' if a.scope == 'branch' else 'forward_rods_integrated01')
br, bm = read(base/'report.json'), read(base/'isolated/manifest.json')
assert sha(base/br['native_file']) == bm['native_sha256'] == br['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
oldrows = {v['name']: v for v in bm['occurrences']}
standard_path = H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
assert all(sha(ROOT/f) == h for f, h in standard['native_files'].items())
targets = sorted(set(rows)-set(oldrows))
if a.scope == 'branch':
    changed_defs = {'Def_RearControlFulcrum_lever_low_right', 'Def_RearControlFulcrum_lever_low_left'}
    targets += sorted(n for n, v in rows.items() if n in oldrows and
        (v['definition'] in changed_defs or max(abs(x-y) for x,y in zip(v['frame'],oldrows[n]['frame'])) > 1e-7))
else:
    assert set(targets) == set(r['new_occurrences'])
validate_native_bindings(dict(native_file=str(native), render_occurrences=targets, landmarks=[]), m)
records = {n: (row, m, 'candidate') for n,row in rows.items()}
for n,row in oldrows.items():
    if n not in records:
        records[n] = row, bm, 'retained_development'
excluded_standard = set(oldrows)|set(rows)|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
for row in standard['occurrences']:
    if row['name'] not in excluded_standard and row['representation'] == 'assembly':
        records['standard:'+row['name']] = row, standard, 'retained_standard'
cache, world_cache, local_bounds = {}, {}, {}


def definition(row,data):
    entry = data['definitions'][row['definition']]
    digest = entry['brep_sha256']
    if digest not in cache:
        assert sha(entry['brep_path']) == digest
        s = Part.Shape()
        s.read(entry['brep_path'])
        assert s.Placement.isIdentity()
        cache[digest] = s
    return cache[digest]


def world(name):
    if name not in world_cache:
        row, data, _ = records[name]
        s = definition(row,data).copy()
        s.Placement = App.Placement(App.Matrix(*row['frame']))
        world_cache[name] = s
    return world_cache[name]


names = list(records)
boxes = []
for name in names:
    row,data,origin = records[name]
    entry = data['definitions'][row['definition']]
    digest = entry['brep_sha256']
    if digest not in local_bounds:
        b = definition(row,data).BoundBox
        local_bounds[digest] = np.array(list(itertools.product((b.XMin,b.XMax),(b.YMin,b.YMax),(b.ZMin,b.ZMax))))
    f = np.array(row['frame']).reshape(4,4)
    pts = local_bounds[digest] @ f[:3,:3].T + f[:3,3]
    boxes.append(np.r_[pts.min(axis=0),pts.max(axis=0)])
boxes = np.array(boxes)
seen, checked, findings = set(), [], []
began = time.time()
for index,name in enumerate(targets):
    s = world(name)
    b = s.BoundBox
    lo,hi = np.array([b.XMin,b.YMin,b.ZMin]),np.array([b.XMax,b.YMax,b.ZMax])
    nearby = np.where(np.all(boxes[:,:3] <= hi+1e-7,axis=1) & np.all(boxes[:,3:] >= lo-1e-7,axis=1))[0]
    for j in nearby:
        other = names[j]
        pair = tuple(sorted((name,other)))
        if name == other or pair in seen:
            continue
        seen.add(pair)
        two = world(other)
        try:
            common = s.common(two)
            volume = sum(abs(v.Volume) for v in common.Solids)
            valid = common.isNull() or common.isValid()
            item = dict(first=name,second=other,origin=records[other][2],common_mm3=volume,
                        common_valid=valid,overlap_above_1e5=volume>1e-5)
            if volume>1e-5 or not valid:
                cb=common.BoundBox
                item['intersection_bounds_mm']=[cb.XMin,cb.YMin,cb.ZMin,cb.XMax,cb.YMax,cb.ZMax]
                findings.append(item)
                print('INTERSECTION',name,other,volume,flush=True)
        except Exception as exc:
            item=dict(first=name,second=other,error=repr(exc))
            findings.append(item)
        checked.append(item)
    write(out/'progress.json',dict(last=name,completed=index+1,total=len(targets),pairs=len(checked),findings=findings,elapsed_seconds=time.time()-began))
    print('Progress',index+1,len(targets),name,'pairs',len(checked),'findings',len(findings),flush=True)
write(out/'report.json',dict(scope=a.scope,native_sha256=sha(native),base_native_sha256=bm['native_sha256'],
      manifest_sha256=sha(candidate/'isolated/manifest.json'),standard_manifest_sha256=sha(standard_path),
      worker_sha256=sha(Path(__file__)),targets=targets,context_occurrences=len(records),
      pairs=checked,findings=findings,no_mating_pair_exemptions=True,
      semantic_disposition='Independent overlap measurements; review design contacts separately. No geometry accepted or changed.'))
print('FINISHED',a.scope,len(checked),'pairs',len(findings),'findings',flush=True)
