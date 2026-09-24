"""Inspect saved MX1 joint frames, material, bearing areas and complete contexts."""
import argparse
import math
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--standard-context',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json')
native=out/r['native_file'];source=ROOT/r['source_native']
m=read(out/'isolated/manifest.json');old=read(source.parent/'isolated/manifest.json')
standard_path=a.standard_context.resolve()/'manifest.json';standard=read(standard_path)
assert sha(native)==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/f)==digest for f,digest in r['input_hashes'].items())
assert all(sha(ROOT/f)==digest for f,digest in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in data['occurrences']} for data in [m,old,standard]]
checks=[]
def ck(name,passed,**details):
    checks.append(dict(name=name,passed=bool(passed),**details))
    write(out/'check_progress.json',checks);print(name,bool(passed),flush=True)
def near(name,value,expected=0,tol=1e-5):
    ck(name,abs(value-expected)<tol,actual=value,expected=expected,tolerance=tol)
def error(first,second):return float(np.max(np.abs(np.array(first)-second)))
expected=r['expected_new_occurrences'];changed=set(r['changed_definitions']);newdefs=set(r['new_definitions'])
ck('Twenty complete four-component joints added',len(expected)==80 and len(r['joints'])==20
   and rows.keys()==prior.keys()|expected.keys() and len(rows)==2473)
frame_checks=[]
for name,row in rows.items():
    target=expected.get(name,prior.get(name))
    frame_checks.append(dict(name=name,error=error(row['frame'],target['frame']),
        passed=error(row['frame'],target['frame'])<1e-7 and row['definition']==target['definition']
        and row['owners']==target['owners']))
ck('All saved occurrence frames, definitions and owners match',all(v['passed'] for v in frame_checks))
assembly_checks=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name]
    added=[k for k in r['new_assemblies'] if k in after['children']]
    if name=='Definitions':added=sorted(newdefs)
    allowed_additions=(name=='PortInnerFixedBearing' or name=='PortOuterFixedBearing'
                       or name=='StarboardInnerFixedBearing' or name=='StarboardOuterFixedBearing')
    okay=error(before['local'],after['local'])<1e-7 and error(before['world'],after['world'])<1e-7
    okay=okay and set(after['children'])==set(before['children'])|set(added)
    okay=okay and (len(added)==2 if name=='Definitions' else len(added)==1 if allowed_additions else not added)
    assembly_checks.append(dict(name=name,passed=bool(okay)))
ck('Prior assembly frames retained with only four mounting groups appended',all(v['passed'] for v in assembly_checks)
   and len(m['assemblies'])==215 and m['assemblies'].keys()==old['assemblies'].keys()|set(r['new_assemblies']))
ck('Only two new physical definitions and original source metadata retained',len(m['definitions'])==463
   and m['definitions'].keys()==old['definitions'].keys()|newdefs
   and all(m['definitions'][name]['properties']==row['properties'] for name,row in old['definitions'].items()))
pending=[name for name,row in old['definitions'].items() if name not in changed
         and row['brep_sha256']!=m['definitions'][name]['brep_sha256']]

import FreeCAD as App
import Part
from transmission_stud_parts import cylinder_x
from transmission_support_parts import box
V=App.Vector;cache={}
def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        row={'new':m,'old':old,'standard':standard}[scope]['definitions'][name]
        path=Path(row['brep_path']);assert sha(path)==row['brep_sha256']
        shape=Part.Shape();shape.read(str(path));assert shape.Placement.isIdentity();cache[key]=shape
    return cache[key].copy()
def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name]
    s=definition(row['definition'],scope);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def shifted(s,vector):
    out=s.copy();out.translate(V(*vector));return out
def face_area(first,second):
    total=0.0
    for f in first.Faces:
        if not isinstance(f.Surface,Part.Plane):continue
        for g in second.Faces:
            if not isinstance(g.Surface,Part.Plane):continue
            if abs(abs(f.normalAt(0,0).dot(g.normalAt(0,0)))-1)>1e-7:continue
            if f.distToShape(g)[0]>1e-6:continue
            total+=f.common(g).Area
    return total

for name in sorted(changed|newdefs):
    s=definition(name)
    ck(name+' valid single solid',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,
       kernel_tolerance_mm=s.getTolerance(1))
for role in ['inner','outer']:
    name='Def_FixedBearing_'+role+'_bracket';before=definition(name,'old');after=definition(name)
    support=read(HERE/'transmission_frame_clearance_build/inputs/transmission_support_controls.json')['controls']
    radius=support[role+'_cast_radius']['value']
    # The broad original box also included the deliberately altered joining
    # web above/below the saddle. Name the functional annulus/backbone instead;
    # whole-casting differences are independently bounded below.
    length=r['bracket_dimensions'][role]['length_mm'];half=support['bracket_height']['value']/2
    witness=Part.makeCylinder(radius,length,V(0,-length/2,0),V(0,1,0)).fuse(
        box(-radius-8,-radius+12,-length/2,length/2,-half,half))
    near(role+' saddle material retained',before.common(witness).cut(after).Volume)
    near(role+' saddle voids retained',after.common(witness).cut(before).Volume)
    for i,(y,z) in enumerate(r['bracket_dimensions'][role]['stud_axes_yz_mm']):
        lug=cylinder_x(support['ear_radius']['value'],-220,100,y,z)
        near(role+' cap-stud lug material retained '+str(i),before.common(lug).cut(after).Volume)
        near(role+' cap-stud lug voids retained '+str(i),after.common(lug).cut(before).Volume)

# Cover the entire casting, including areas outside those named functional seats.
# Every material difference must belong to the declared pad/web revision or one
# of the joint bore/spotface tools, while all later detailed features are retained.
base={}
for key in ['inner_original_base','inner_revised_base']:
    path=out/'baseline_shapes'/(key+'.brep');assert sha(path)==r['baseline_brep_hashes'][path.name]
    s=Part.Shape();s.read(str(path));base[key]=s
for role in ['inner','outer']:
    name='Def_FixedBearing_'+role+'_bracket';before=definition(name,'old');after=definition(name)
    additions=[];removals=[]
    if role=='inner':
        additions=list(base['inner_revised_base'].cut(base['inner_original_base']).Solids)
        removals=list(base['inner_original_base'].cut(base['inner_revised_base']).Solids)
    for joint in [j for j in r['details']['joints'] if j['role']==role]:
        y,z=joint['y_local_mm'],joint['z_local_mm']
        removals.extend([cylinder_x(r['controls']['head_spotface_radius'],r['details']['head_seat_x_mm'],0,y,z),
               cylinder_x(9.525+r['controls']['receiver_radial_clearance'],
                          r['mount_controls']['frame_front_x']-1,r['details']['head_seat_x_mm']+1,y,z)])
    # Sequential subtraction from disconnected remainders raised Null shape on
    # this kernel. The equivalent set difference A \ (B union allowed) avoids
    # that failure; retain all whole-casting checks and the original tolerance.
    allowed=removals[0].multiFuse(removals[1:])
    retained=before.multiFuse(additions) if additions else before
    added=after.cut(retained);removed=before.cut(after.fuse(allowed))
    for label,result in [('added outside declared casting revision',added),
                         ('lost outside revision and joint tools',removed)]:
        ck(role+' no material '+label,result.isValid() and not result.Faces and abs(result.Volume)<1e-5,
           volume_mm3=result.Volume,faces=len(result.Faces),tolerance_mm3=1e-5)
    bad=after.cut(Part.makeBox(8,8,8,V(-30,-20,75)))
    loss=before.cut(bad.fuse(allowed)).Volume
    ck(role+' unapproved bearing cut is detected',loss>1,missing_mm3=loss)
    radius=r['bracket_dimensions'][role]['socket_radius_mm']
    bad=after.fuse(Part.makeBox(4,4,4,V(-radius+5,-2,-2)))
    extra=bad.cut(retained).Volume
    ck(role+' unapproved bore filling is detected',extra>1,added_mm3=extra)

c=r['controls'];mc=r['mount_controls'];detail=r['details']
bolt=definition(r['hardware_definitions']['bolt']);cotter=definition(r['hardware_definitions']['cotter'])
near('Estimated bolt under-head length retained',bolt.BoundBox.XMax,c['bolt_under_head_length'])
near('Estimated bolt head height retained',-bolt.BoundBox.XMin,c['bolt_head_height'])
ck('Nominal three-quarter inch shank has analytic cylindrical faces',any(
    isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-9.525)<1e-8 for f in bolt.Faces))
near('Printed MX1 pin leg stock length',sum(detail['cotter'][key] for key in
     ['straight_length_mm','bend_arc_length_mm','tail_length_mm']),38.1,1e-8)
near('MX1 uses distinct longer pin than inherited MX5',c['cotter_length']-34.925,3.175,1e-8)
pc=detail['pin_controls'];half=pc['cotter_center_spacing']/2;wire=(3.175-pc['cotter_center_spacing'])/2
for sign in [-1,1]:
    witness=Part.makeCylinder(wire-.01,26.5,V(0,-13,sign*half),V(0,1,0))
    near('Both formed-pin straight legs retained '+str(sign),witness.cut(cotter).Volume)
for endpoint in detail['cotter']['tail_endpoints']:
    near('Formed tail endpoint present '+str(endpoint),cotter.distToShape(Part.Vertex(V(*endpoint)))[0])

contact_records=[];checked_pads=set()
for j in r['joints']:
    name=j['name'];receiver=shape(j['receiver']);channel=shape(j['channel'])
    bolt,nut,pin,washer=[shape(name+'_'+k) for k in ['bolt','nut','cotter','washer']]
    head_x,axis_y,axis_z=[rows[name+'_bolt']['frame'][i] for i in [3,7,11]]
    tip=head_x-c['bolt_under_head_length']
    void=cylinder_x(9.525,tip,head_x,axis_y,axis_z)
    near(name+' complete receiver bore',void.common(receiver).Volume+void.common(channel).Volume)
    head_area=face_area(bolt,receiver);washer_area=face_area(washer,channel);nut_area=face_area(nut,washer)
    ck(name+' head and washer bearing areas',head_area>300 and washer_area>600 and nut_area>300,
       head_area_mm2=head_area,washer_area_mm2=washer_area,nut_area_mm2=nut_area)
    near(name+' head seat has no gap',bolt.distToShape(receiver)[0])
    near(name+' washer seat has no gap',washer.distToShape(channel)[0])
    near(name+' nut seat has no gap',nut.distToShape(washer)[0])
    near(name+' lifted head loses bearing area',face_area(shifted(bolt,(.01,0,0)),receiver),tol=1e-6)
    near(name+' lifted washer loses bearing area',face_area(shifted(washer,(-.01,0,0)),channel),tol=1e-6)
    moved=shifted(bolt,(0,.5,0))
    ck(name+' displaced shank catches receiver',moved.common(receiver).Volume>1)
    ck(name+' cotter retains withdrawn castle nut',shifted(nut,(-3,0,0)).common(pin).Volume>.01)
    rotated=nut.copy();rotated.rotate(V(head_x-detail['cotter_from_head_mm'],axis_y,axis_z),V(1,0,0),10)
    ck(name+' cotter prevents castle nut rotation',rotated.common(pin).Volume>.001)
    key=(j['receiver'],j['channel'])
    if key not in checked_pads:
        checked_pads.add(key);area=face_area(receiver,channel)
        width=r['bracket_dimensions'][j['role']]['foot_width_mm']
        count=len(c[j['role']+'_row_offsets'])
        expected_area=width*mc['channel_height']-count*math.pi*(9.525+c['receiver_radial_clearance'])**2
        ck(j['receiver']+' full pad on '+j['channel'],area>.99*expected_area,
           bearing_area_mm2=area,expected_pad_area_mm2=expected_area,gap_mm=receiver.distToShape(channel)[0])
    contact_records.append(dict(name=name,head_area_mm2=head_area,washer_area_mm2=washer_area,nut_area_mm2=nut_area))

affected=set(r['affected_occurrences']);all_shapes={n:shape(n) for n in rows}
def bounds(s):
    b=s.copy().cleaned().BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def collisions(other_shapes,label,same):
    names=sorted(other_shapes);boxes=np.array([bounds(other_shapes[n]) for n in names]);seen=set();results=[]
    for name in sorted(affected):
        one=all_shapes[name];bb=bounds(one)
        possible=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in possible:
            other=names[idx];pair=tuple(sorted([name,other])) if same else (name,other)
            if (same and name==other) or pair in seen:continue
            seen.add(pair);common=one.common(other_shapes[other]).Volume
            results.append(dict(first=name,second=other,common_mm3=common,passed=abs(common)<1e-5))
            write(out/(label+'_material_progress.json'),results)
    ck(label+' all nearby material pairs clear',all(v['passed'] for v in results),pair_count=len(results))
    return results
local=collisions(all_shapes,'development',True)
excluded=set(rows)&set(tank)
excluded.update(['PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'])
context={n:shape(n,'standard') for n,row in tank.items() if row['representation']=='assembly' and n not in excluded}
standard_pairs=collisions(context,'standard',False)
result=dict(local_joint_checks_passed=all(v['passed'] for v in checks),native_sha256=sha(native),
    source_native_sha256=sha(source),checker_sha256=sha(Path(__file__)),checks=checks,
    occurrence_frames=frame_checks,assembly_checks=assembly_checks,contacts=contact_records,
    development_material_pairs=local,standard_material_pairs=standard_pairs,
    standard_manifest_sha256=sha(standard_path),standard_context_count=len(context),
    excluded_standard_occurrences=sorted(excluded&set(tank)),
    pending_unchanged_definition_material=pending,
    historical_joint_layout_qualified=False,installation_qualified=False,standard_assembly_modified=False)
write(out/'independent_checks.json',result)
print('Completed',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_joint_checks_passed']
