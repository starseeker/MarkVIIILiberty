"""Check saved transmission castings, retained details, frame seats and neighbors."""
import argparse
import itertools
from pathlib import Path
import sys
import numpy as np

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
native, source = out / r['native_file'], ROOT / r['source_native']
assert sha(native) == r['native_sha256'] and sha(source) == r['source_native_sha256']
assert all(sha(ROOT / path) == digest for path, digest in r['input_hashes'].items())
m, old = [read(p / 'isolated/manifest.json') for p in [out, source.parent]]
assert m['native_sha256'] == sha(native) and old['native_sha256'] == sha(source)
assert m['extractor_sha256'] == old['extractor_sha256'] == sha(HERE / 'pump_integration_worker.py')
rows, prior = [{v['name']: v for v in j['occurrences']} for j in [m, old]]
affected = {name for names in r['replacement_definitions'].values() for name in names}
mount_names = {name for name, row in prior.items() if 'TransmissionCaseMounting' in row['owners']}
affected.update(mount_names)
delta = np.asarray(r['shaft_axis_mm']) - np.asarray(r['original_axis_mm'])
checks, pairs = [], []

def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))
    write(out / 'check_progress.json', checks)
    print(name, bool(passed), flush=True)

def near(name, value, expected=0, tolerance=1e-5):
    ck(name, abs(value - expected) < tolerance, actual=value, expected=expected, tolerance=tolerance)

frame_results = []
for name, row in rows.items():
    before = prior[name]
    expected = np.asarray(before['frame']).reshape(4, 4).copy()
    if name in mount_names:
        expected[:3, 3] -= delta
    error = float(np.max(np.abs(expected - np.asarray(row['frame']).reshape(4, 4))))
    frame_results.append(dict(name=name, frame_error=error,
        passed=error < 1e-7 and {k:v for k,v in row.items() if k!='frame'} == {k:v for k,v in before.items() if k!='frame'}))
ck('All 2393 frames and owners match retained parts or reset frame joints',
   rows.keys() == prior.keys() and len(rows) == 2393 and all(v['passed'] for v in frame_results))
assembly_results = []
for name, row in m['assemblies'].items():
    before = old['assemblies'][name]
    ew = np.asarray(before['world']).reshape(4, 4).copy()
    el = np.asarray(before['local']).reshape(4, 4).copy()
    if name == 'TransmissionCaseMounting' or name.startswith('CaseMount_'):
        ew[:3, 3] -= delta
    if name == 'TransmissionCaseMounting':
        el[:3, 3] -= delta
    err = max(float(np.max(np.abs(ew-np.asarray(row['world']).reshape(4,4)))),
              float(np.max(np.abs(el-np.asarray(row['local']).reshape(4,4)))))
    assembly_results.append(dict(name=name,error=err,passed=err<1e-7 and row['children']==before['children']))
ck('All 191 assembly frames and children follow the joint reset', len(assembly_results)==191 and all(v['passed'] for v in assembly_results))
ck('Three rebuilt casting definitions and 16 retained MX5 joint constituents',
   len(affected) == 21 and len(r['replacement_definitions']) == 3 and len(mount_names) == 16)

import FreeCAD as App
import Part
from transmission_support_parts import box
V = App.Vector
cache = {}

def definition(name, before=False):
    key = name, before
    if key not in cache:
        row = (old if before else m)['definitions'][name]
        path = Path(row['brep_path'])
        assert sha(path) == row['brep_sha256']
        s = Part.Shape()
        s.read(str(path))
        assert s.Placement.isIdentity()
        cache[key] = s
    return cache[key].copy()

def shape(name, before=False):
    row = (prior if before else rows)[name]
    s = definition(row['definition'], before)
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s

def baseline(name):
    path = out / 'baseline_shapes' / (name + '.brep')
    assert sha(path) == r['baseline_brep_hashes'][path.name]
    s = Part.Shape()
    s.read(str(path))
    return s

def remainder(first, second):
    return first.cut(second) if first.Solids and second.Solids else first

def contact_area(a, b, plane_x):
    def faces(s):
        return [f for f in s.Faces if type(f.Surface).__name__ == 'Plane'
                and abs(f.BoundBox.XMin - plane_x) < 1e-7 and abs(f.BoundBox.XMax - plane_x) < 1e-7]
    return sum(x.common(y).Area for x in faces(a) for y in faces(b))

for name in r['replacement_definitions']:
    before, after = definition(name, True), definition(name)
    label = 'case' if name.endswith('bevel_case') else 'inner' if '_inner_' in name else 'outer'
    original, revised = baseline(label + '_original_base'), baseline(label + '_revised_base')
    ck(name + ' valid single solid within native tolerance', after.isValid() and len(after.Solids) == 1 and after.getTolerance(1) <= 1e-4,
       tolerance_mm=after.getTolerance(1))
    removed, added = before.cut(after), after.cut(before)
    allowed_removed, allowed_added = original.cut(revised), revised.cut(original)
    near(name + ' no material removed outside changed base webs', remainder(removed, allowed_removed).Volume)
    near(name + ' no material added outside changed base webs', remainder(added, allowed_added).Volume)
    late_added, late_removed = before.cut(original), original.cut(before)
    near(name + ' later bosses and mounting lands retained', remainder(late_added, after).Volume)
    near(name + ' later pockets and blind bores retained', late_removed.common(after).Volume if late_removed.Solids else 0)
    ck(name + ' substantive web change', abs(removed.Volume) + abs(added.Volume) > 100,
       removed_mm3=removed.Volume, added_mm3=added.Volume)
    if label != 'case':
        radius = r['support_controls'][label + '_cast_radius']
        guard = box(-radius + 12, 300, -300, 300, -200, 200)
        one, two = before.common(guard), after.common(guard)
        near(name + ' full saddle material retained', one.cut(two).Volume)
        near(name + ' no extra saddle material', two.cut(one).Volume)

fc = r['frame_controls']
plane = rows['TransmissionFrame_TopChannel']['frame'][3]
near('Frame X plane unchanged', plane, old['assemblies']['TransmissionMountingFrame']['world'][3] + fc['frame_front_x'])
gap = (r['original_bracket_dimensions']['inner']['foot_aft_x_mm'] -
       r['original_bracket_dimensions']['outer']['foot_aft_x_mm'])
for hand in ['Port', 'Starboard']:
    for role in ['inner', 'outer']:
        ident = hand + 'FixedBearing_' + role + '_bracket'
        s = shape(ident)
        for end in ['Top', 'Bottom']:
            frame = shape('TransmissionFrame_' + end + 'Channel')
            expected_gap = gap if role == 'inner' else 0
            near(ident + '/' + end + ' original mounting gap', s.distToShape(frame)[0], expected_gap, 1e-6)
            near(ident + '/' + end + ' no channel overlap', s.common(frame).Volume)
            aligned = s.copy()
            aligned.translate(V(-expected_gap, 0, 0))
            area = contact_area(aligned, frame, plane)
            expected_area = r['original_bracket_dimensions'][role]['foot_width_mm'] * fc['channel_height']
            near(ident + '/' + end + ' complete pad facing area', area, expected_area, 1e-3)
            previous_gap = shape(ident, True).distToShape(frame)[0]
            ck(ident + '/' + end + ' predecessor fails retained seat', abs(previous_gap - expected_gap) > 1,
               old_gap_mm=previous_gap, expected_gap_mm=expected_gap)
        prefix = hand + 'FixedBearing_' + role + '_'
        near(ident + ' liner seating', s.distToShape(shape(prefix + 'lining_back'))[0], 0, 1e-6)
        near(ident + ' cap split retained', s.distToShape(shape(prefix + 'cap'))[0], .1, 1e-6)
        lifted = s.copy()
        lifted.translate(V(.01, 0, 0))
        if role == 'outer':
            near(ident + ' lift removes planar contact', contact_area(lifted, shape('TransmissionFrame_TopChannel'), plane), 0, 1e-6)

case = shape('CenterTransmissionCore_bevel_case')
former_case = shape('CenterTransmissionCore_bevel_case', True)
former_case.translate(V(*(-delta)))
for end in ['Top', 'Bottom']:
    frame = shape('TransmissionFrame_' + end + 'Channel')
    near('Bevel case/' + end + ' contact gap', case.distToShape(frame)[0], 0, 1e-6)
    near('Bevel case/' + end + ' no channel overlap', case.common(frame).Volume)
    near('Bevel case/' + end + ' complete web and boss facing area', contact_area(case, frame, plane),
         contact_area(former_case, frame, plane), 1e-3)

mc = r['mount_controls']
axis = V(*r['shaft_axis_mm'])
for joint in r['mount_datums']['mounts']:
    name = 'CaseMount_' + joint['name']
    frame = shape('TransmissionFrame_' + ('Top' if joint['channel']=='Upper' else 'Bottom') + 'Channel')
    stud, nut, pin, washer = [shape(name+'_'+key) for key in ['stud','nut','cotter','washer']]
    for tag, one, two, expected in [('case bore',stud,case,.15),('channel bore',stud,frame,.15),
                                   ('nut clearance',stud,nut,.15),('cotter clearance',stud,pin,.15),
                                   ('washer on frame',washer,frame,0),('nut on washer',nut,washer,0)]:
        near(name+' '+tag,one.distToShape(two)[0],expected,1e-6)
    local = definition(rows[name+'_stud']['definition'])
    near(name+' printed stud length',local.BoundBox.XLength,142.875,1e-6)
    near(name+' printed stud diameter',local.BoundBox.YLength,19.05,1e-6)
    y,z=joint['y'],joint['z']
    end=r['mount_datums']['stud_embedded_end_x']
    bore=mc['stud_diameter']/2+mc['receiver_gap']
    void=Part.makeCylinder(bore-.0001,end+mc['blind_gap']-mc['frame_front_x'],
                          axis+V(mc['frame_front_x'],y,z),V(1,0,0))
    near(name+' complete receiver bore',void.common(case).Volume)
    floor=Part.makeCylinder(bore-.01,mc['blind_stock']-.002,
                           axis+V(end+mc['blind_gap']+.001,y,z),V(1,0,0))
    near(name+' retained 4mm blind floor',floor.cut(case).Volume)
    near(name+' source-derived stud frame',float(np.max(np.abs(np.asarray(rows[name+'_stud']['frame'])-
         np.asarray(r['mount_occurrence_frames'][name+'_stud'])))),0,1e-7)

unchanged = []
for name, item in m['definitions'].items():
    if name not in r['replacement_definitions']:
        unchanged.append(dict(name=name, exact_brep=item['brep_sha256'] == old['definitions'][name]['brep_sha256'],
                              metadata_equal=item['properties'] == old['definitions'][name]['properties']))
ck('All 461 definition identities and source metadata retained', m['definitions'].keys() == old['definitions'].keys() and
   all(v['properties'] == old['definitions'][name]['properties'] for name, v in m['definitions'].items()))
frame_defs = {row['definition'] for row in rows.values() if 'TransmissionMountingFrame' in row['owners']}
ck('All frame member BReps unchanged', all(m['definitions'][name]['brep_sha256'] == old['definitions'][name]['brep_sha256'] for name in frame_defs))

local = {}
for name in m['definitions']:
    b = definition(name).BoundBox
    local[name] = np.asarray(list(itertools.product([b.XMin, b.XMax], [b.YMin, b.YMax], [b.ZMin, b.ZMax])))
names, bounds = list(rows), []
for name in names:
    row = rows[name]
    f = np.asarray(row['frame']).reshape(4, 4)
    corners = local[row['definition']] @ f[:3, :3].T + f[:3, 3]
    bounds.append(np.r_[corners.min(axis=0), corners.max(axis=0)])
boxes = np.asarray(bounds)
selected = set()
for name in affected:
    b = boxes[names.index(name)]
    indices = np.flatnonzero(np.all(boxes[:, :3] <= b[3:] + 1e-7, axis=1) & np.all(boxes[:, 3:] >= b[:3] - 1e-7, axis=1))
    selected.update(tuple(sorted([name, names[i]])) for i in indices if name != names[i])
print('Checking material against full 2393-occurrence context:', len(selected), 'nearby pairs', flush=True)
for first, second in sorted(selected):
    one, two = shape(first), shape(second)
    volume = one.common(two).Volume if one.BoundBox.intersect(two.BoundBox) else 0.0
    pairs.append(dict(first=first, second=second, common_mm3=volume, passed=abs(volume) < 1e-5))
    write(out / 'material_progress.json', pairs)
ck('Rebuilt castings clear saved neighbors', all(v['passed'] for v in pairs), pairs=len(pairs), failures=[v for v in pairs if not v['passed']])
write(out / 'independent_checks.json', dict(local_frame_checks_passed=all(v['passed'] for v in checks),
    native_sha256=sha(native), source_native_sha256=sha(source), checker_sha256=sha(Path(__file__)),
    checks=checks, material_pairs=pairs, affected_occurrences=sorted(affected), preserved_definitions=unchanged,
    occurrence_frames=frame_results, assembly_frames=assembly_results,
    pending_definition_material=[v['name'] for v in unchanged if not v['exact_brep']],
    inner_packing_gap_mm=gap, frame_fasteners_and_packing_complete=False,
    installation_qualified=False, historical_station_qualified=False, standard_assembly_modified=False))
assert all(v['passed'] for v in checks), 'Retain failures; repair geometry or diagnosis without weakening criteria.'
