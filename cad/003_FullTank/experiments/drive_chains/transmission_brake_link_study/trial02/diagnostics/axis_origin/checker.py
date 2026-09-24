"""Independently inspect saved M337/M339 geometry, retention and full context."""
import argparse,math
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--standard-manifest',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
standard=read(a.standard_manifest)
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
assert all(sha(ROOT/f)==v for f,v in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in d['occurrences']} for d in [m,old,standard]];checks=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));write(out/'check_progress.json',checks);print(name,bool(passed),flush=True)
def near(name,value,expected=0,tol=1e-5):ck(name,abs(value-expected)<tol,actual=value,expected=expected,tolerance=tol)
def error(a,b):return float(np.max(np.abs(np.array(a)-b)))
expected=r['expected_new_occurrences'];repositioned=r['expected_repositioned_occurrences'];newdefs=set(r['new_definitions'])
ck('Exactly six support occurrences repositioned',set(repositioned)=={hand+role+suffix for hand in ['Port','Starboard'] for role,suffix in [('LowSpeed','Bracket'),('Track','Bracket'),('Track','Stop')]})
ck('Four links, four separate pivots and eight split pins added',len(expected)==16
    and sum(n.endswith('SuspensionLink') for n in expected)==4 and sum(n.endswith('SuspensionPin') for n in expected)==4
    and sum('SuspensionCotter' in n for n in expected)==8 and rows.keys()==prior.keys()|expected.keys()
    and len(rows)==r['expected_physical_occurrences'])
frames=[]
for name,row in rows.items():
    target=expected.get(name,repositioned.get(name,prior.get(name)));delta=error(row['frame'],target['frame'])
    frames.append(dict(name=name,error=delta,passed=delta<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners']))
ck('Declared support shifts and new frames correct; other frames and all owners retained',all(v['passed'] for v in frames))
assemblies=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name];added=newdefs if name=='Definitions' else set(r['added_children'].get(name,[]))
    local=list(before['local']);world=list(before['world']);shift=r['assembly_shifts_mm'].get(name,[0,0,0])
    for index,delta in zip([3,7,11],shift):local[index]+=delta;world[index]+=delta
    assemblies.append(dict(name=name,passed=error(local,after['local'])<1e-7 and error(world,after['world'])<1e-7
        and set(after['children'])==set(before['children'])|added))
ck('Only specified support assembly translations and new children',all(v['passed'] for v in assemblies) and m['assemblies'].keys()==old['assemblies'].keys())
ck('All inherited definition identities retained',m['definitions'].keys()==old['definitions'].keys()|newdefs
    and all(v['properties']==m['definitions'][n]['properties'] for n,v in old['definitions'].items()) and not r['changed_definitions'])
for role,mark,rid in [('link','M337','SNL:119:023'),('pin','M339','SNL:137:024'),('cotter','Split pin 1/4 x 1-1/2','SNL:141:014')]:
    props=m['definitions']['Def_BrakeLink_'+role]['properties'];ck(mark+' source identity retained',props['SourcePartMark']==mark and rid in props['SourceRecords'])
import FreeCAD as App
import Part
V=App.Vector;cache={};c=r['controls'];d=r['dimensions']
def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        record={'new':m,'old':old,'standard':standard}[scope]['definitions'][name];path=Path(record['brep_path']);assert sha(path)==record['brep_sha256']
        s=Part.Shape();s.read(str(path));assert s.Placement.isIdentity();cache[key]=s
    return cache[key].copy()
def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name];s=definition(row['definition'],scope);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def cylinders(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-7]
link=definition('Def_BrakeLink_link');pin=definition('Def_BrakeLink_pin');cotter=definition('Def_BrakeLink_cotter')
for name,s in [('M337',link),('M339',pin),('split pin',cotter)]:
    ck(name+' valid single solid',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
upper_bores=[f for f in cylinders(link,c['suspension_pin_diameter']/2+c['upper_bore_allowance']) if abs(f.Surface.Center.z)<1e-7]
lower_bores=[f for f in cylinders(link,c['lower_pin_diameter']/2+c['lower_bore_allowance']) if abs(f.Surface.Center.z-d['lower_eye_relative_mm'][2])<1e-7]
ck('Upper fork has two coaxial bore faces; lower eye has one',len(upper_bores)==2 and len(lower_bores)==1)
for i,face in enumerate(upper_bores):near('Upper cheek '+str(i+1)+' stock',face.BoundBox.YLength,c['clevis_cheek_stock'])
near('Lower eye stock',lower_bores[0].BoundBox.YLength,c['lower_stock'])
actual=lower_bores[0].Surface.Center;near('Lower eye forward station',actual.x,d['lower_eye_relative_mm'][0]);near('Lower eye vertical station',actual.z,d['lower_eye_relative_mm'][2])
for label,center,rad in [('upper',V(),c['suspension_pin_diameter']/2+c['upper_bore_allowance']),
    ('lower',V(*d['lower_eye_relative_mm']),c['lower_pin_diameter']/2+c['lower_bore_allowance'])]:
    bore=Part.makeCylinder(rad,100,center+V(0,-50,0),V(0,1,0));near(label+' link bore completely open',link.common(bore).Volume)
    filled=link.fuse(Part.makeCylinder(rad,4,center+V(0,-2,0),V(0,1,0)))
    ck(label+' filled-bore negative control rejected',filled.common(bore).Volume>1)
near('Pin overall length',pin.BoundBox.YLength,d['pin_length_mm'])
ck('Pin retains the estimated 24 mm nominal shaft',len(cylinders(pin,c['suspension_pin_diameter']/2))==1)
cross=cylinders(pin,(.25*25.4)/2+c['cotter_hole_allowance']);ck('Two split-pin cross holes retained',len(cross)==2)
for y in [-d['cotter_y_mm'],d['cotter_y_mm']]:
    ck('Cross-hole axis at '+str(y),any(abs(f.Surface.Center.y-y)<1e-7 and abs(abs(f.Surface.Axis.x)-1)<1e-7 for f in cross))
    tool=Part.makeCylinder(.25*25.4/2+c['cotter_hole_allowance'],30,V(-15,y,0),V(1,0,0));near('Cross hole open at '+str(y),pin.common(tool).Volume)
near('Printed quarter-inch folded cotter envelope',c['cotter_diameter'],.25*25.4)
near('Printed one-and-half-inch cotter leg stock',r['cotter']['total_leg_centerline_mm'],1.5*25.4)
# Verify the actual two straight shanks and two splayed end locations; the eye
# joins and paired round sections remain explicit manufacturing approximations.
wire=r['cotter']['wire_radius_mm'];straight=[f for f in cylinders(cotter,wire) if abs(abs(f.Surface.Axis.x)-1)<1e-7]
axes={(round(f.Surface.Center.y,7),round(f.Surface.Center.z,7)) for f in straight}
ck('Cotter has two straight leg axes despite trimmed face splits',len(axes)==2,face_count=len(straight),axes_yz=sorted(axes))
for sign in [-1,1]:
    leg=Part.makeCylinder(wire,r['cotter']['straight_length_mm'],V(r['cotter']['under_eye_y_mm'],0,sign*c['cotter_center_spacing']/2),V(1,0,0))
    missing=leg.cut(cotter)
    ck('Complete straight cotter leg '+str(sign),abs(missing.Volume)<1e-5 and not missing.Faces)
    negative=cotter.cut(Part.makeBox(2,10,10,V(-1,-5,-5)))
    ck('Cut cotter leg negative rejected '+str(sign),leg.cut(negative).Volume>1)
near('Saved folded shank envelope across Z',max(f.BoundBox.ZMax for f in straight)-min(f.BoundBox.ZMin for f in straight),.25*25.4)
for i,xyz in enumerate(r['cotter']['tail_endpoints']):
    end=V(xyz[1],-xyz[0],xyz[2]);direction=V(math.cos(math.radians(c['cotter_bend_angle'])),0,math.copysign(math.sin(math.radians(c['cotter_bend_angle'])),xyz[2]))
    ck('Cotter splayed tail '+str(i+1)+' survives forming',cotter.isInside(end-direction*.2,1e-7,False))
contacts=[]
for prefix,interface in r['interfaces'].items():
    bracket=shape(interface['bracket']);one=shape(prefix+'SuspensionLink');pivot=shape(prefix+'SuspensionPin')
    pose=App.Placement(App.Matrix(*rows[interface['bracket']]['frame']));local=one.copy();local.Placement=pose.inverse().multiply(local.Placement)
    support=bracket.copy();support.Placement=pose.inverse().multiply(support.Placement)
    upper_radius=max(f.Surface.Radius for f in cylinders(support,12.15))
    near(prefix+' pivot centered on saved bracket bore',error(rows[prefix+'SuspensionPin']['frame'],rows[interface['bracket']]['frame']))
    near(prefix+' link centered on saved bracket bore',error(rows[prefix+'SuspensionLink']['frame'],rows[interface['bracket']]['frame']))
    near(prefix+' estimated pivot radial allowance',upper_radius-c['suspension_pin_diameter']/2,.15)
    gap=one.distToShape(bracket)[0];near(prefix+' fork cheek clearance to bracket',gap,c['clevis_side_gap'])
    near(prefix+' fork does not remove or intersect bracket stock',one.common(bracket).Volume)
    # The real saved pin/cotters prevent the assembled pin translating out of
    # the fork without removing a split pin. This is a static interference
    # witness, not a simulated load/kinematic qualification.
    retainers=[shape(prefix+'SuspensionCotter'+str(i)) for i in [1,2]]
    for sign in [-1,1]:
        moved=[s.copy() for s in retainers]
        for s in moved:s.translate(V(0,sign*4,0))
        common=sum(s.common(one).Volume for s in moved)
        ck(prefix+' axial retention witness '+str(sign),common>1,shift_mm=sign*4,interference_mm3=common)
    # The link now lies beside the band, rather than outside a full radial
    # envelope. Check actual saved band faces and the retained frame plate.
    band=shape(prefix+'BrakeUpperBand');plate=shape('TransmissionFrame_MiddleDiaphragm')
    axis=pose.multVec(actual);bb=band.BoundBox;sign=1 if prefix.startswith('Port') else -1
    side_gap=(bb.YMin-axis.y-c['lower_stock']/2) if sign==1 else (axis.y-c['lower_stock']/2-bb.YMax)
    near(prefix+' lower strap lies inboard of actual band side',side_gap,c['link_band_side_clearance'])
    near(prefix+' lower-eye rear envelope clears diaphragm plane',axis.x-c['lower_head_radius']-plate.BoundBox.XMax,c['lower_frame_clearance'])
    near(prefix+' upper station X retained',rows[prefix+'Bracket']['frame'][3],prior[prefix+'Bracket']['frame'][3])
    near(prefix+' upper station Z retained',rows[prefix+'Bracket']['frame'][11],prior[prefix+'Bracket']['frame'][11])
    if 'LowSpeed' in prefix:near(prefix+' actual link clears diaphragm',one.distToShape(plate)[0],c['lower_frame_clearance'])
    contacts.append(dict(name=prefix,bracket_clearance_mm=gap,lower_interface=interface['lower_mm']))
def seat_area(one,two):
    total=0
    for f in one.Faces:
        if not isinstance(f.Surface,Part.Plane) or abs(abs(f.normalAt(0,0).z)-1)>1e-7:continue
        for g in two.Faces:
            if not isinstance(g.Surface,Part.Plane) or abs(abs(g.normalAt(0,0).z)-1)>1e-7:continue
            if f.distToShape(g)[0]<1e-6:total+=f.common(g).Area
    return total
top=shape('TransmissionFrame_TopChannel')
for name in repositioned:
    old_seat=seat_area(shape(name,'old'),shape('TransmissionFrame_TopChannel','old'))
    one=shape(name);seat=seat_area(one,top)
    ck(name+' preserves complete prior foot bearing',old_seat>100 and abs(seat-old_seat)<1e-5,area_mm2=seat,prior_area_mm2=old_seat)
    shifted=one.copy();shifted.translate(V(0,0,-.01))
    near(name+' displaced seat loses bearing',seat_area(shifted,top))
    near(name+' does not penetrate channel',one.common(top).Volume)
affected=set(expected)|set(repositioned);all_shapes={n:shape(n) for n in rows}
def bounds(s):
    b=s.copy().cleaned().BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def collisions(others,label,same):
    names=sorted(others);boxes=np.array([bounds(others[n]) for n in names]);seen=set();records=[]
    for name in sorted(affected):
        one=all_shapes[name];bb=bounds(one)
        possible=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for i in possible:
            other=names[i];pair=tuple(sorted([name,other])) if same else (name,other)
            if (same and name==other) or pair in seen:continue
            seen.add(pair);v=one.common(others[other]).Volume
            records.append(dict(first=name,second=other,common_mm3=v,passed=abs(v)<1e-5));write(out/(label+'_material_progress.json'),records)
        print(label,name,len(records),'pairs',flush=True)
    ck(label+' all nearby material pairs clear',all(v['passed'] for v in records),pair_count=len(records));return records
development=collisions(all_shapes,'development',True)
excluded=(set(rows)&set(tank))|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
context={n:shape(n,'standard') for n,v in tank.items() if n not in excluded and v['representation']=='assembly'}
standard_pairs=collisions(context,'standard',False)
result=dict(local_link_checks_passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],source_native_sha256=sha(source),
    checker_sha256=sha(Path(__file__)),checks=checks,occurrence_frames=frames,assembly_checks=assemblies,contacts=contacts,
    development_material_pairs=development,standard_material_pairs=standard_pairs,standard_manifest_sha256=sha(a.standard_manifest),
    standard_context_count=len(context),excluded_standard_occurrences=sorted(excluded&set(tank)),
    historical_geometry_qualified=False,installation_qualified=False,lower_attachment_pending=True)
write(out/'independent_checks.json',result);print('Finished',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_link_checks_passed']
