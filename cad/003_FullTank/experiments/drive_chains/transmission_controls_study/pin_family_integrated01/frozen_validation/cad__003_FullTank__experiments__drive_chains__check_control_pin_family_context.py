"""Whole-material comparison of the revised shared-pin family and unchanged low-speed receivers against retained tank geometry."""
import argparse
import itertools
from pathlib import Path
import sys
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==m['native_sha256']
parent=ROOT/r['parent_native'];old=read(parent.parent/'isolated/manifest.json');assert sha(parent)==old['native_sha256']==r['parent_native_sha256']
sp=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';standard=read(sp);assert all(sha(ROOT/f)==v for f,v in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in data['occurrences']} for data in (m,old,standard)];cache={}
def definition(key,data):
    d=data['definitions'][key];hash_=d['brep_sha256']
    if hash_ not in cache:
        assert sha(d['brep_path'])==hash_;s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[hash_]=s
    return cache[hash_]
def world(row,data):
    s=definition(row['definition'],data).copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def bounds(s):
    b=s.BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def overlap(a,b):return np.all(a[:3]<=b[3:]+1e-7) and np.all(b[:3]<=a[3:]+1e-7)
# Local canonical boxes transformed by all eight corners conservatively enclose
# every old occurrence. No regional cutoff excludes the under-floor bolt ends.
local_boxes={}
for key in old['definitions']:
    bb=bounds(definition(key,old));local_boxes[key]=np.array(list(itertools.product(*[(bb[i],bb[i+3]) for i in range(3)])))
boxes={}
for name,row in prior.items():
    f=np.array(row['frame']).reshape(4,4);pts=local_boxes[row['definition']]@f[:3,:3].T+f[:3,3];boxes[name]=np.r_[pts.min(axis=0),pts.max(axis=0)]
affected=list(rows);selected=[];pairs=[]
excluded=(set(prior)&set(tank))|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
targets={n:world(rows[n],m) for n in affected}
for name,one in targets.items():
    bb=bounds(one)
    for n,box in boxes.items():
        if n in rows or not overlap(bb,box):continue
        two=world(prior[n],old);common=one.common(two);valid=common.isNull() or common.isValid();volume=sum(abs(s.Volume) for s in common.Solids)
        pairs.append(dict(first=name,second=n,origin='development',common_mm3=volume,passed=valid and volume<1e-5));selected.append(n)
    for n,row in tank.items():
        if n in excluded or row['representation']!='assembly' or not overlap(bb,np.array(row['bounds_mm'])):continue
        two=world(row,standard);common=one.common(two);valid=common.isNull() or common.isValid();volume=sum(abs(s.Volume) for s in common.Solids)
        pairs.append(dict(first=name,second=n,origin='retained_standard',common_mm3=volume,passed=valid and volume<1e-5))
    write(out/'context_progress.json',dict(last=name,pairs=len(pairs),failed=[v for v in pairs if not v['passed']]))
for name, other in itertools.combinations(targets, 2):
    one, two = targets[name], targets[other]
    if not overlap(bounds(one), bounds(two)):
        continue
    common = one.common(two)
    valid = common.isNull() or common.isValid()
    volume = sum(abs(s.Volume) for s in common.Solids)
    pairs.append(dict(first=name, second=other, origin='revised_local', common_mm3=volume,
                      passed=valid and volume < 1e-5))
validate_native_bindings(dict(native_file=str(parent),render_occurrences=list(set(selected)),landmarks=[]),old)
validate_native_bindings(dict(native_file=str(native),render_occurrences=affected,landmarks=[]),m)
result=dict(passed=all(v['passed'] for v in pairs),pairs=pairs,affected_count=len(affected),tool_envelope_count=0,parent_occurrence_count=len(prior),retained_standard_count=sum(n not in excluded and row['representation']=='assembly' for n,row in tank.items()),native_sha256=sha(native),parent_native_sha256=sha(parent),standard_manifest_sha256=sha(sp),checker_sha256=sha(Path(__file__)),replaced_occurrences=sorted(set(rows)&set(prior)), scope='All16 trial components compared against each other and retained development/standard solids. Only replaced old versions of these same named occurrences are omitted; replacement material is included in local pairs.',historical_geometry_qualified=False,installation_qualified=False)
write(out/'context_checks.json',result);print('Whole surrounding material',len(pairs),'pairs;',result['passed'],flush=True)
if not result['passed']:print([v for v in pairs if not v['passed']],flush=True)
assert result['passed']
