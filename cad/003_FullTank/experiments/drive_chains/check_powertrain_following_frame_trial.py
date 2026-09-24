"""Measure both frame hypotheses against saved local geometry and the standard hull."""
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
p.add_argument('--standard-context', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
native, source = out / r['native_file'], ROOT / r['source_native']
assert sha(native) == r['native_sha256'] and sha(source) == r['source_native_sha256']
assert all(sha(ROOT / path) == digest for path, digest in r['input_hashes'].items())
m, old = [read(folder / 'isolated/manifest.json') for folder in [out, source.parent]]
assert m['native_sha256'] == sha(native) and old['native_sha256'] == sha(source)
standard_path = a.standard_context.resolve() / 'manifest.json'
standard = read(standard_path)
assert all(sha(ROOT / path) == digest for path, digest in standard['native_files'].items())
rows, prior, tank = [{v['name']: v for v in j['occurrences']} for j in [m, old, standard]]
assert len(rows) == len(m['occurrences']) and len(tank) == len(standard['occurrences'])
affected = {name for name,row in rows.items() if 'TransmissionMountingFrame' in row['owners']}
delta = np.asarray(r['frame_translation_mm'])
checks = []

def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))
    write(out / 'check_progress.json', checks)
    print(name, bool(passed), flush=True)

def near(name, actual, expected=0, tolerance=1e-5):
    ck(name, abs(actual-expected)<tolerance, actual=actual, expected=expected, tolerance=tolerance)

frames = []
for name, row in rows.items():
    before = prior[name]
    expected = np.asarray(before['frame']).reshape(4,4).copy()
    if name in affected:
        expected[:3,3] += delta
    error = float(np.max(np.abs(expected-np.asarray(row['frame']).reshape(4,4))))
    frames.append(dict(name=name, error=error, passed=error<1e-7 and
        {k:v for k,v in row.items() if k!='frame'}=={k:v for k,v in before.items() if k!='frame'}))
ck('All 2393 occurrence identities, owners and expected frames retained',
   len(rows)==2393 and rows.keys()==prior.keys() and all(v['passed'] for v in frames))
assembly_frames = []
for name, row in m['assemblies'].items():
    expected = dict(old['assemblies'][name])
    for key in ['world','local']:
        f = np.asarray(expected[key]).reshape(4,4).copy()
        if name=='TransmissionMountingFrame':
            f[:3,3] += delta
        expected[key] = list(f.ravel())
    error = max(float(np.max(np.abs(np.asarray(row[k])-np.asarray(expected[k])))) for k in ['world','local'])
    assembly_frames.append(dict(name=name,error=error,passed=error<1e-7 and
        {k:v for k,v in row.items() if k not in ['world','local']}==
        {k:v for k,v in expected.items() if k not in ['world','local']}))
ck('Only frame assembly placement changes among 191 assemblies',
   len(assembly_frames)==191 and all(v['passed'] for v in assembly_frames))
ck('Exactly 15 frame occurrences move',len(affected)==15)
preserved = [dict(name=name,exact_brep=v['brep_sha256']==old['definitions'][name]['brep_sha256'],
                 metadata_equal=v['properties']==old['definitions'][name]['properties'])
             for name,v in m['definitions'].items()]
ck('All 461 definition identities and source metadata retained',len(preserved)==461 and
   m['definitions'].keys()==old['definitions'].keys() and all(v['metadata_equal'] for v in preserved))
frame_defs = {rows[name]['definition'] for name in affected}
ck('Every frame definition retains exact source BRep',all(v['exact_brep'] for v in preserved if v['name'] in frame_defs))

import FreeCAD as App
import Part
V = App.Vector
cache = {}

def definition(name, scope='new'):
    key = scope,name
    if key not in cache:
        rec = {'new':m,'old':old,'standard':standard}[scope]['definitions'][name]
        path = Path(rec['brep_path'])
        assert sha(path)==rec['brep_sha256']
        shape = Part.Shape()
        shape.read(str(path))
        assert shape.Placement.isIdentity()
        cache[key] = shape
    return cache[key].copy()

def shape(name, scope='new'):
    rec = {'new':rows,'old':prior,'standard':tank}[scope][name]
    result = definition(rec['definition'],scope)
    result.Placement = App.Placement(App.Matrix(*rec['frame']))
    return result

def contact_area(first,second,plane_x):
    def faces(s):
        return [f for f in s.Faces if type(f.Surface).__name__=='Plane' and
                abs(f.BoundBox.XMin-plane_x)<1e-7 and abs(f.BoundBox.XMax-plane_x)<1e-7]
    return sum(one.common(two).Area for one in faces(first) for two in faces(second))

fc = {k:v['value'] for k,v in read(HERE/'transmission_frame_controls.json')['controls'].items()}
plane = fc['frame_front_x']+delta[0]
gap = 5.805714285714288
contacts = []
for hand,role in itertools.product(['Port','Starboard'],['inner','outer']):
    name = hand+'FixedBearing_'+role+'_bracket'
    bracket = shape(name)
    for end in ['Top','Bottom']:
        channel_name = 'TransmissionFrame_'+end+'Channel'
        channel = shape(channel_name)
        distance = bracket.distToShape(channel)[0]
        near(name+'/'+end+' restored distance',distance,gap if role=='inner' else 0,1e-6)
        near(name+'/'+end+' no material overlap',bracket.common(channel).Volume)
        aligned = bracket.copy()
        aligned.translate(V(-gap if role=='inner' else 0,0,0))
        original = shape(name,'old')
        original.translate(V(-delta[0]-(gap if role=='inner' else 0),0,-delta[2]))
        old_area = contact_area(original,shape(channel_name,'old'),fc['frame_front_x'])
        area = contact_area(aligned,channel,plane)
        ck(name+'/'+end+' complete original pad facing area',old_area>1000 and abs(area-old_area)<1e-3,
           area_mm2=area,baseline_area_mm2=old_area)
        contacts.append(dict(part=name,channel=channel_name,gap_mm=distance,area_mm2=area))
case = shape('CenterTransmissionCore_bevel_case')
for end in ['Top','Bottom']:
    frame = shape('TransmissionFrame_'+end+'Channel')
    near('Case/'+end+' restored channel seat',case.distToShape(frame)[0],0,1e-6)
    near('Case/'+end+' no overlap',case.common(frame).Volume)
    area = contact_area(case,frame,plane)
    ck('Case/'+end+' positive seated web area',area>1000,area_mm2=area)
    displaced = frame.copy()
    displaced.translate(V(-.01,0,0))
    near('Case/'+end+' lifted frame loses face contact',contact_area(case,displaced,plane),0,1e-6)
for joint,end in itertools.product(['Port','Starboard'],['Upper','Lower']):
    name = 'CaseMount_'+end+joint
    channel = shape('TransmissionFrame_'+('Top' if end=='Upper' else 'Bottom')+'Channel')
    stud,washer,nut = [shape(name+'_'+k) for k in ['stud','washer','nut']]
    near(name+' stud/channel bore gap',stud.distToShape(channel)[0],.15,1e-6)
    near(name+' washer seated on channel',washer.distToShape(channel)[0],0,1e-6)
    near(name+' nut seated on washer',nut.distToShape(washer)[0],0,1e-6)

def bounds(names,scope):
    result = []
    source_rows = {'new':rows,'standard':tank}[scope]
    for name in names:
        row = source_rows[name]
        b = definition(row['definition'],scope).BoundBox
        corners = np.asarray(list(itertools.product([b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax])))
        f = np.asarray(row['frame']).reshape(4,4)
        corners = corners@f[:3,:3].T+f[:3,3]
        result.append(np.r_[corners.min(axis=0),corners.max(axis=0)])
    return np.asarray(result)

def measure_pairs(scope):
    names = list(rows) if scope=='new' else [n for n,v in tank.items() if v['representation']=='assembly']
    boxes = bounds(names,scope)
    selected = set()
    for name in affected:
        b = bounds([name],'new')[0]
        indices = np.flatnonzero(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))
        for i in indices:
            other = names[i]
            if scope=='new' and other==name:
                continue
            selected.add(tuple(sorted([name,other])) if scope=='new' else (name,other))
    records = []
    print('Measuring',scope,len(selected),'nearby pairs from',len(names),'occurrences',flush=True)
    for first,second in sorted(selected):
        one,two = shape(first),shape(second,scope)
        volume = one.common(two).Volume if one.BoundBox.intersect(two.BoundBox) else 0.
        records.append(dict(first=first,second=second,common_mm3=volume,passed=abs(volume)<1e-5))
        write(out/(scope+'_material_progress.json'),records)
    return records

local_pairs = measure_pairs('new')
standard_pairs = measure_pairs('standard')
ck('Moved frame clears full development context',all(v['passed'] for v in local_pairs),
   pairs=len(local_pairs),failures=[v for v in local_pairs if not v['passed']])
ck('Moved frame clears all 5326 physical standard occurrences',all(v['passed'] for v in standard_pairs),
   pairs=len(standard_pairs),failures=[v for v in standard_pairs if not v['passed']])

# Attachment gaps are observations, never recast as successful installation.
attachment_measurements = []
for name in ['TransmissionFrame_TopChannel','TransmissionFrame_BottomChannel','TransmissionFrame_MiddleDiaphragm']:
    for receiver in ['hull_engine_back','hull_floor_8']:
        target = shape(receiver,'standard')
        entry = dict(frame=name,receiver=receiver)
        for scenario,scope in [('fixed_frame','old'),('following_frame','new')]:
            frame = shape(name,scope)
            entry[scenario] = dict(gap_mm=frame.distToShape(target)[0],common_mm3=frame.common(target).Volume)
        attachment_measurements.append(entry)

cal = read(HERE/'transmission_input_calibration.json')
source_projection = []
axis_z = r['shaft_axis_mm'][2]
for end,key,band in [('Top','top_web_z',[151,164]),('Bottom','bottom_web_z',[768,790])]:
    # Channel occurrence origin is its documented web face; independently verify
    # that the saved native placement carries that plane.
    row = rows['TransmissionFrame_'+end+'Channel']
    z = row['frame'][11]
    near(end+' saved web plane from frame datum',z,fc[key]+delta[2],1e-7)
    y = cal['origin_px'][1]-(z-axis_z)/cal['mm_per_pixel']
    fixed_y = cal['origin_px'][1]-(fc[key]-axis_z)/cal['mm_per_pixel']
    source_projection.append(dict(feature=end+'_web',source_band_y_px=band,
        following_y_px=y,fixed_y_px=fixed_y,
        following_residual_band_mm=[(y-v)*cal['mm_per_pixel'] for v in band]))

write(out/'independent_checks.json',dict(local_frame_checks_passed=all(v['passed'] for v in checks),
    native_sha256=sha(native),source_native_sha256=sha(source),checker_sha256=sha(Path(__file__)),
    standard_manifest_sha256=sha(standard_path),standard_native_files=standard['native_files'],
    checks=checks,occurrence_frames=frames,assembly_frames=assembly_frames,
    affected_occurrences=sorted(affected),preserved_definitions=preserved,
    pending_definition_material=[v['name'] for v in preserved if not v['exact_brep']],
    contacts=contacts,local_material_pairs=local_pairs,standard_material_pairs=standard_pairs,
    attachment_measurements=attachment_measurements,source_projection=source_projection,
    source_calibration_sha256=sha(HERE/'transmission_input_calibration.json'),
    scope='Only 15 moved frame occurrences checked against both complete saved contexts. Layout envelopes are not physical collision targets.',
    attachment_qualified=False,historical_station_qualified=False,installation_qualified=False,
    standard_assembly_modified=False))
assert all(v['passed'] for v in checks), 'Retain diagnostic failures; do not weaken fit criteria.'
