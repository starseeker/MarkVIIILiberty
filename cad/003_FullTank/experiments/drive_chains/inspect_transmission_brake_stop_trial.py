"""Saved-artifact diagnostic for a brake-stop hypothesis, not release qualification."""
import argparse
import itertools
from pathlib import Path
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path[:0]=[str(H),str(H.parents[1])]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};cache={};world={};validity={};checks=[]
for key,d in m['definitions'].items():
    path=Path(d['brep_path']);assert sha(path)==d['brep_sha256']
    s=Part.Shape();s.read(str(path));cache[key]=s
    if key in r['new_definitions']:
        validity[key]=dict(valid=s.isValid(),solid_count=len(s.Solids),closed=s.isClosed(),max_tolerance_mm=s.getTolerance(1),identity_frame=s.Placement.isIdentity())
for name,row in rows.items():
    s=cache[row['definition']].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));world[name]=s
for key,actual in [('expected_physical_occurrences',len(rows)),('expected_definition_count',len(m['definitions'])),('expected_assembly_count',len(m['assemblies']))]:
    checks.append(dict(name=key,actual=actual,expected=r[key],passed=actual==r[key]))
for name,expected in {**r['expected_new_occurrences'],**r['expected_revised_occurrences']}.items():
    actual=rows[name];error=max(abs(x-y) for x,y in zip(actual['frame'],expected['frame']))
    checks.append(dict(name=name,definition=actual['definition'],frame_error=error,
        passed=actual['definition']==expected['definition'] and actual['owners']==expected['owners'] and error<1e-7))
changed=set(r['affected_occurrences']);pairs=set();collisions=[];invalid=[]
def overlaps(a,b):
    return all(min(getattr(a,k+'Max'),getattr(b,k+'Max'))-max(getattr(a,k+'Min'),getattr(b,k+'Min'))>1e-6 for k in ['X','Y','Z'])
for name in changed:
    box=world[name].BoundBox
    for other,shape in world.items():
        if other!=name and overlaps(box,shape.BoundBox):pairs.add(tuple(sorted([name,other])))
for i,(left,right) in enumerate(sorted(pairs),1):
    common=world[left].common(world[right])
    if not common.isNull() and not common.isValid():invalid.append([left,right])
    if common.Solids:
        volume=sum(abs(s.Volume) for s in common.Solids)
        if volume>1e-5:collisions.append(dict(left=left,right=right,overlap_mm3=volume))
    if i%50==0:write(out/'trial_progress.json',dict(done=i,total=len(pairs),collisions=len(collisions)))
contacts=[]
def contact(left,right):
    a,b=world[left],world[right];area=0.
    for f in a.Faces:
        if not isinstance(f.Surface,Part.Plane):continue
        for g in b.Faces:
            if not isinstance(g.Surface,Part.Plane):continue
            if abs(abs(f.normalAt(0,0).dot(g.normalAt(0,0)))-1)>1e-7:continue
            if f.distToShape(g)[0]>1e-6:continue
            area+=f.common(g).Area
    return dict(left=left,right=right,distance_mm=a.distToShape(b)[0],planar_contact_area_mm2=area)
for hand in ['Port','Starboard']:
    contacts.append(contact(hand+'BrakeStopBar',hand+'BrakeStopBracket'))
    for label in ['LowSpeed','Track']:
        prefix=hand+label+'Brake'
        contacts.append(contact(prefix+'StopScrew',hand+'BrakeStopBar'))
        contacts.append(contact(prefix+'StopBarSetScrew',prefix+'StopLug'))
        contacts.append(contact(prefix+'StopScrewNut',prefix+'StopLug'))
        contacts.append(contact(prefix+'StopBarSetScrewNut',hand+'BrakeStopBar'))
result=dict(native_sha256=m['native_sha256'],checker_sha256=sha(Path(__file__)),definition_validity=validity,
    counts_and_frames=checks,broad_phase_pairs=len(pairs),collisions=collisions,invalid_common_results=invalid,
    planar_contacts=contacts,diagnostic_clear=not collisions and not invalid and all(x['passed'] for x in checks)
        and all(v['valid'] and v['solid_count']==1 and v['closed'] and v['identity_frame'] for v in validity.values()),
    scope='Development-context diagnostic only. No full material preservation, standard tank, STEP, parameter or reproduction qualification.',
    historical_geometry_qualified=False,installation_qualified=False)
write(out/'trial_diagnostics.json',result)
print('Diagnostic pairs',len(pairs),'collisions',len(collisions),'invalid',len(invalid),flush=True)
for hit in collisions:print(hit,flush=True)
