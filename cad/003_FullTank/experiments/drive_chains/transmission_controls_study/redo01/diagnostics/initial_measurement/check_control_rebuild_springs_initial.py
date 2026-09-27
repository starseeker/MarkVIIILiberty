"""Inspect actual reopened washer/spring stock, interfaces and negative controls."""
import argparse,math
from pathlib import Path
import numpy as np
from control_rebuild_io import App,Part,H,ROOT,Saved,pose,read,write,sha
from lib.camera_review import validate_native_bindings
from lib.mass_properties import AdaptiveMass

V=App.Vector;X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();current=Saved(out)
r,m=current.report,current.manifest;parent=Saved((ROOT/r['parent_native']).parent)
assert not (out/'independent_checks.json').exists()
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
validate_native_bindings(dict(native_file=str(current.native),render_occurrences=list(current.rows),landmarks=[]),m)
checks=[];interfaces=[]
mass=AdaptiveMass(out/'mass_runtime')
def ck(name,passed,**kw):
    checks.append(dict(name=name,passed=bool(passed),**kw))
    if not passed:print('FAILED',name,kw,flush=True)
    write(out/'check_progress.json',checks)
def volume(s):return sum(abs(v.Volume) for v in s.Solids)
def empty(s):return not s.Faces and not s.Solids
def shifted(s,delta):
    t=s.copy();t.translate(delta);return t
def cylinders(s,axis,radius):
    return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and
            abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7]
def bearing(one,two,point,axis):
    def faces(s):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and
        f.normalAt(0,0).cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
    return sum(f.common(g).Area for f in faces(one) for g in faces(two))

ck('Exactly eight washers and four return springs',len(r['new_occurrences'])==12 and
   sum(r['specs'][n]['role']=='washer' for n in r['new_occurrences'])==8 and
   sum(r['specs'][n]['role']=='spring' for n in r['new_occurrences'])==4)
doc=App.openDocument(str(current.native))
try:
    for key,d in m['definitions'].items():
        body=doc.getObject(key);s=body.Shape
        ck(key+' canonical closed valid stock',body.Placement.isIdentity() and s.Placement.isIdentity()
           and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4,
           maximum_kernel_tolerance_mm=s.getTolerance(1))
    for n in r['new_occurrences']:
        role=r['specs'][n]['role'];body=doc.getObject(current.rows[n]['definition'])
        ck(n+' correct source identity',body.SourcePartMark==('M567' if role=='washer' else 'M564'))
finally:App.closeDocument(doc.Name)
for n,spec in r['specs'].items():
    if spec['role']=='receiver':
        old=parent.world(n);new=current.world(n)
        ck(n+' inherited frame and complete material retained',
           max(abs(x-y) for x,y in zip(current.rows[n]['frame'],parent.rows[n]['frame']))<1e-7
           and empty(new.cut(old)) and empty(old.cut(new)))

for name in r['new_occurrences']:
    row=current.rows[name];s=current.world(name);local=current.definition(row['definition'])
    if r['specs'][name]['role']=='washer':
        stem=name[:-6];pin=current.world(stem+'Pin');fork=current.world(stem+'Fork');cotter=current.world(stem+'Cotter')
        pp=pose(current.rows[stem+'Pin']['frame']);axis=pp.Rotation.multVec(Y)
        faces=cylinders(local,Y,6.5)
        ck(name+' real 13 mm through bore',len(faces)==1 and (faces[0].Surface.Center.cross(Y)).Length<1e-6)
        bore_center=pose(row['frame']).Base
        ck(name+' washer bore and actual pin axis coaxial',
           (bore_center-pp.Base).cross(axis).Length<1e-6 and
           bool(cylinders(pin,axis,6.35)))
        area=bearing(s,fork,bore_center,axis)
        ck(name+' real fork-face bearing and displaced negative',area>150 and
           bearing(shifted(s,axis*.1),fork,bore_center,axis)<1e-6,area_mm2=area)
        ck(name+' pin fork cotter remain clear',all(volume(s.common(t))<1e-5 for t in [pin,fork,cotter]))
        ck(name+' moving into fork is rejected',volume(shifted(s,-axis*.2).common(fork))>1e-3)
        ck(name+' outward withdrawal caught by cotter',volume(shifted(s,axis*1).common(cotter))>1e-3)
        cfg=r['details']['controls']['washer'];expected=math.pi*((cfg['diameter']/2)**2-(cfg['bore']/2)**2)*cfg['thickness']
        ck(name+' complete annulus stock',abs(local.Volume-expected)<1e-5)
        interfaces.append(dict(occurrence=name,fork_seat_area_mm2=area,seat_center_mm=list(bore_center),axis=list(axis)))
    else:
        base=name[:-12];side='Port' if name.startswith('Port') else 'Starboard'
        nut=current.world(base+'BrakeJointNut');fork=current.world(base+'BrakeJointFork')
        bracket=current.world(side+'LowSpringBracket');detail=r['details'][name]
        wr=detail['wire_diameter_mm']/2
        path=Part.Shape();path.read(str(out/(row['definition']+'_centerline.brep')))
        measured=mass.measure(local)
        expected=math.pi*wr**2*path.Length
        ck(name+' adaptive mass converges',measured['converged'],mass=measured)
        ck(name+' retained wire stock',abs(measured['volume_mm3']-expected)<1e-3,
           expected_mm3=expected,measured_mm3=measured['volume_mm3'],difference_mm3=measured['volume_mm3']-expected)
        ck(name+' both physical end contacts',s.distToShape(nut)[0]<1e-6 and s.distToShape(bracket)[0]<1e-6,
           nut_distance_mm=s.distToShape(nut)[0],bracket_distance_mm=s.distToShape(bracket)[0])
        ck(name+' no material occupied in either receiver',volume(s.common(nut))<1e-5 and volume(s.common(bracket))<1e-5)
        ck(name+' nut retains eye under spring pull',volume(shifted(s,X*.2).common(nut))>1e-3)
        ck(name+' bore retains rear hook under spring pull',volume(shifted(s,-X*.2).common(bracket))>1e-3)
        ck(name+' lifted receiving nut loses contact',s.distToShape(shifted(nut,X*.1))[0]>.05)
        ck(name+' eye has socket running clearance',.09<s.distToShape(fork)[0]<.11)
        # Check an actual wire crossing through the bore, not just a bounding box.
        endpoints=[V(*v) for v in detail['rear_crosswire_endpoints_world_mm']]
        anchor=V(*detail['rear_anchor_world_mm']);cross=(endpoints[1]-endpoints[0]);length=cross.Length;cross.normalize()
        witness=Part.makeCylinder(wr-.01,length-.02,endpoints[0]+cross*.01,cross)
        ck(name+' full crosswire stock is present',empty(witness.cut(s)))
        bores=[f for f in cylinders(bracket,Y,3.325) if (f.Surface.Center-anchor).cross(Y).Length<1e-6]
        ck(name+' actual supporting bracket bore found',len(bores)==1)
        radii=[]
        for edge in path.Edges:
            for u in np.linspace(edge.FirstParameter,edge.LastParameter,151)[1:-1]:
                k=edge.curvatureAt(float(u))
                if k>1e-10:radii.append(1/k)
        ck(name+' wire bends do not fold inside tube',min(radii)>wr+.1,minimum_sampled_centerline_radius_mm=min(radii))
        pts=[];stations=[];length=0.
        for edge in path.Edges:
            data=edge.discretize(Number=max(3,math.ceil(edge.Length/.5)+1))
            for j,v in enumerate(data):
                if j==0 and pts:continue
                if pts:length+=(v-V(*pts[-1])).Length
                pts.append(tuple(v));stations.append(length)
        pts=np.array(pts);stations=np.array(stations);nearest=float('inf')
        for begin in range(0,len(pts),128):
            delta=pts[begin:begin+128,None,:]-pts[None,:,:]
            distance=np.linalg.norm(delta,axis=2)
            distance[np.abs(stations[begin:begin+128,None]-stations[None,:])<10]=float('inf')
            nearest=min(nearest,float(distance.min()))
        ck(name+' nonlocal wire clearance with sampling allowance',nearest-.5>2*wr,
           minimum_sampled_distance_mm=nearest,sampling_allowance_mm=.5,local_arclength_exclusion_mm=10)
        interfaces.append(dict(occurrence=name,front_receiver=base+'BrakeJointNut',rear_receiver=side+'LowSpringBracket',
                               stock_measurement=measured,wire_stock_volume_mm3=expected,details=detail))
result=dict(passed=all(c['passed'] for c in checks),checks=checks,interfaces=interfaces,
    native_sha256=sha(current.native),parent_native_sha256=sha(parent.native),checker_sha256=sha(Path(__file__)),
    mass_provenance=mass.provenance,historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result)
print(len(checks),'checks;',result['passed'],flush=True)
assert result['passed']
