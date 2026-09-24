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
expected=r['expected_new_occurrences'];newdefs=set(r['new_definitions'])
ck('Four links, four separate pivots and eight split pins added',len(expected)==16
    and sum(n.endswith('SuspensionLink') for n in expected)==4 and sum(n.endswith('SuspensionPin') for n in expected)==4
    and sum('SuspensionCotter' in n for n in expected)==8 and rows.keys()==prior.keys()|expected.keys()
    and len(rows)==r['expected_physical_occurrences'])
frames=[]
for name,row in rows.items():
    target=expected.get(name,prior.get(name));delta=error(row['frame'],target['frame'])
    frames.append(dict(name=name,error=delta,passed=delta<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners']))
ck('Inherited frames and owners retained; new composed frames correct',all(v['passed'] for v in frames))
assemblies=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name];added=newdefs if name=='Definitions' else set(r['added_children'].get(name,[]))
    assemblies.append(dict(name=name,passed=error(before['local'],after['local'])<1e-7 and error(before['world'],after['world'])<1e-7
        and set(after['children'])==set(before['children'])|added))
ck('Prior assembly frames retained with only specified new children',all(v['passed'] for v in assemblies) and m['assemblies'].keys()==old['assemblies'].keys())
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
ck('Cotter has two actual straight cylindrical legs',len(straight)==2)
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
    # Lower eye is reserved outside the planned rear-bracket footprint. No
    # missing anchor pin or bracket is counted as an installed component.
    sphere=Part.makeCylinder(d['lower_anchor_radius_mm']-c['lower_head_radius']-c['lower_head_radial_clearance'],
        c['lower_stock']+2,V(r['interfaces']['PortTrack']['lower_mm'][0]+d['lower_anchor_radius_mm'],interface['lower_mm'][1]-c['lower_stock']/2-1,interface['lower_mm'][2]),V(0,1,0))
    eye=Part.makeCylinder(c['lower_head_radius'],c['lower_stock'],V(*interface['lower_mm'])+V(0,-c['lower_stock']/2,0),V(0,1,0))
    near(prefix+' lower-eye radial reservation',eye.distToShape(sphere)[0],c['lower_head_radial_clearance'])
    contacts.append(dict(name=prefix,bracket_clearance_mm=gap,lower_interface=interface['lower_mm']))
affected=set(expected);all_shapes={n:shape(n) for n in rows}
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
