"""Independently reopen bow hypothesis and audit stock, joints and all context."""
import argparse
import itertools
import math
from pathlib import Path
import numpy as np
from control_rebuild_io_v2 import *

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();folder=a.candidate.resolve();r=read(folder/'report.json')
out=folder/'checks01';out.mkdir(exist_ok=False)
native=folder/r['native_file'];assert sha(native)==r['native_sha256']
assert all(sha(ROOT/f)==digest for f,digest in r['input_hashes'].items())
assert all(sha(ROOT/f)==digest for f,digest in r['standard_native_files'].items())
doc=App.openDocument(str(native))
checks=[];world={}


def ck(name, passed, **details):
    checks.append(dict(name=name,passed=bool(passed),**details))
    if not passed:print('CHECK FAILED',name,details,flush=True)


def volume(s):return sum(abs(q.Volume) for q in s.Solids)


def bounds(s):
    b=s.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


for name,row in r['occurrences'].items():
    link=doc.getObject(name);body=link.LinkedObject
    ck(name+' native link and identity definition',link.TypeId=='App::Link' and body.Name==row['definition'] and body.Placement.isIdentity())
    ck(name+' saved frame',max(abs(x-y) for x,y in zip(link.LinkPlacement.toMatrix().A,row['frame']))<1e-8)
    q=body.Shape.copy();q.Placement=link.LinkPlacement;world[name]=q
    ck(name+' valid closed stock',q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    ck(name+' identity owner frame',doc.getObject(row['group']).Placement.isIdentity())
ck('identity prototype root',doc.getObject('BowEnclosurePrototype').Placement.isIdentity())
App.closeDocument(doc.Name)
targets=[n for n,row in r['occurrences'].items() if row['candidate']]
main=[s for n,s in world.items() if n in targets and ('main_' in n or n=='upper_front_center')]
driver=[s for n,s in world.items() if n in targets and 'driver_' in n and n.startswith('upper_')]
mb=Part.makeCompound(main).BoundBox;db=Part.makeCompound(driver).BoundBox
ck('printed combined overall extent',abs(db.XMax-mb.XMin-3136.9)<1e-5,measured_mm=db.XMax-mb.XMin)
ck('printed main width',abs(mb.YLength-1028.7)<1e-5,measured_mm=mb.YLength)
ck('printed main height',abs(mb.ZLength-571.5)<1e-5,measured_mm=mb.ZLength)
for label,actual,expected in [('length',db.XLength,685.8),('width',db.YLength,482.6),('height',db.ZLength,330.2)]:
    ck('printed driver '+label,abs(actual-expected)<1e-5,measured_mm=actual)
front=world['hull_front_slope'];largest=max(front.Faces,key=lambda f:f.Area)
points=[v.Point for v in largest.Vertexes]
lo=min(points,key=lambda p:p.z);hi=max(points,key=lambda p:p.z)
ck('bow rises aft in actual material',hi.x<lo.x,upper_minus_lower_x_mm=hi.x-lo.x)
normal=largest.normalAt(0,0)
parallel=[f for f in front.Faces if isinstance(f.Surface,Part.Plane) and abs(abs(f.normalAt(0,0).dot(normal))-1)<1e-8]
separations=[abs((f.CenterOfMass-largest.CenterOfMass).dot(normal)) for f in parallel]
ck('actual front normal stock 12mm',any(abs(d-12)<1e-6 for d in separations),face_separations_mm=separations)

joint_pairs=[('hull_front_slope','hull_floor_1'),('hull_floor_1','hull_floor_2'),
             ('hull_floor_2','hull_floor_3'),('hull_front_slope','hull_port_roof_driver'),
             ('hull_front_slope','hull_starboard_roof_driver'),('hull_front_slope','upper_driver_front')]
joints=[]
for one,two in joint_pairs:
    s,t=world[one],world[two];common=s.common(t)
    record=dict(first=one,second=two,distance_mm=s.distToShape(t)[0],common_area_mm2=common.Area,
                common_volume_mm3=volume(common),common_valid=common.isNull() or common.isValid())
    record['passed']=record['distance_mm']<1e-5 and record['common_volume_mm3']<1e-5 and record['common_area_mm2']>1 and record['common_valid']
    joints.append(record)
    print('JOINT',one,two,record,flush=True)

# Reimport all exported solids. Match by world bounds and test actual material.
step=folder/'BowEnclosureHypothesis.step';assert sha(step)==r['step_sha256']
exchange=Part.read(str(step));remaining=list(exchange.Solids)
ck('STEP valid and correct solid count',exchange.isValid() and len(remaining)==len(targets),solid_count=len(remaining))
for name in targets:
    q=world[name]
    match=min(range(len(remaining)),key=lambda i:max(abs(x-y) for x,y in zip(bounds(q),bounds(remaining[i]))))
    s=remaining.pop(match)
    missing=volume(q.cut(s));added=volume(s.cut(q))
    ck(name+' STEP material and position',missing<1e-3 and added<1e-3 and max(abs(x-y) for x,y in zip(bounds(q),bounds(s)))<1e-5,
       missing_mm3=missing,added_mm3=added)

# Audit every proposed plate against every physical saved neighbor. Bounding
# boxes only prune disjoint pairs; no mating or part-family exemptions exist.
standard_path=H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard=read(standard_path);parent=Saved((ROOT/r['development_native']).parent)
sources={};cache={};local_bounds={}
for name,row in parent.rows.items():
    if name not in targets:sources['development:'+name]=(row,parent.manifest,'retained_development')
superseded=set(targets)|set(parent.rows)
for row in standard['occurrences']:
    if row['name'] not in superseded and row['representation']=='assembly':
        sources['standard:'+row['name']]=(row,standard,'retained_standard')


def definition(row, manifest):
    e=manifest['definitions'][row['definition']];digest=e['brep_sha256']
    if digest not in cache:
        assert sha(e['brep_path'])==digest
        q=Part.Shape();q.read(e['brep_path']);assert q.Placement.isIdentity();cache[digest]=q
    return cache[digest]


names=targets+list(sources);boxes=[]
for name in names:
    if name in targets:boxes.append(bounds(world[name]));continue
    row,manifest,_=sources[name];key=manifest['definitions'][row['definition']]['brep_sha256']
    if key not in local_bounds:
        b=definition(row,manifest).BoundBox
        local_bounds[key]=np.array(list(itertools.product((b.XMin,b.XMax),(b.YMin,b.YMax),(b.ZMin,b.ZMax))))
    f=np.array(row['frame']).reshape(4,4);pts=local_bounds[key]@f[:3,:3].T+f[:3,3]
    boxes.append(np.r_[pts.min(axis=0),pts.max(axis=0)])
boxes=np.array(boxes);pairs=[];seen=set()
for index,name in enumerate(targets):
    s=world[name];b=np.array(bounds(s))
    nearby=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
    for j in nearby:
        other=names[j];pair=tuple(sorted([name,other]))
        if other==name or pair in seen:continue
        seen.add(pair)
        if other in targets:t=world[other];origin='candidate'
        else:
            row,manifest,origin=sources[other];t=definition(row,manifest).copy();t.Placement=pose(row['frame'])
        try:
            common=s.common(t);v=volume(common);valid=common.isNull() or common.isValid()
            item=dict(first=name,second=other,origin=origin,common_volume_mm3=v,passed=v<1e-5 and valid)
        except Exception as exc:item=dict(first=name,second=other,origin=origin,passed=False,error=str(exc))
        pairs.append(item)
        if not item['passed']:print('INTERSECTION',item,flush=True)
    print('CONTEXT',index+1,len(targets),name,len(pairs),'pairs',flush=True)
    write(out/'context_progress.json',dict(completed=index+1,total=len(targets),pairs=len(pairs),findings=[v for v in pairs if not v['passed']]))

# Retained sample solids in the native prototype must match their authoritative
# parents, independently of the report's nominal frames.
for name,row in r['occurrences'].items():
    if row['candidate']:continue
    if name in parent.rows:q=parent.world(name)
    else:
        old=next(x for x in standard['occurrences'] if x['name']==name)
        q=definition(old,standard).copy();q.Placement=pose(old['frame'])
    ck(name+' retained native material',volume(q.cut(world[name]))<1e-5 and volume(world[name].cut(q))<1e-5)

from bow_reconstruction_parts import bow_parts
stocks={**r['stocks'],'wall_thickness':14.,'floor_thickness':8.}
variant,_=bow_parts(stocks,r['joint_datums']['outer'])
for role in ['front_slope','floor_1','floor_2']:
    q=variant[role];ck(role+' thicker-stock variation remains closed and grows',q.isValid() and len(q.Solids)==1 and q.Volume>world['hull_'+role].Volume)
for one,two in [('front_slope','floor_1'),('floor_1','floor_2')]:
    common=variant[one].common(variant[two]);ck(one+'/'+two+' varied miter',volume(common)<1e-5 and common.Area>1)

result=dict(native_sha256=sha(native),report_sha256=sha(folder/'report.json'),checker_sha256=sha(Path(__file__)),
            construction_checks=checks,construction_passed=all(c['passed'] for c in checks),
            joints=joints,joints_passed=all(c['passed'] for c in joints),
            context_pairs=pairs,context_passed=all(c['passed'] for c in pairs),
            context_findings=[c for c in pairs if not c['passed']],
            context_counts=dict(candidate=len(targets),retained_development=len(parent.rows),
                                retained_standard=sum(v[2]=='retained_standard' for v in sources.values()),pairs=len(pairs)),
            standard_replaced_occurrences=sorted(set(x['name'] for x in standard['occurrences'])&superseded),
            integration_accepted=False,historical_geometry_qualified=False,
            scope='Actual saved native plates, complete STEP reimport and all retained physical context. Layout envelopes excluded by representation; names replaced by development/candidate geometry use that saved replacement. No mating exemptions or context-driven cuts.')
write(out/'report.json',result)
print('RESULT',result['construction_passed'],result['joints_passed'],result['context_passed'],len(result['context_findings']),'findings',flush=True)
