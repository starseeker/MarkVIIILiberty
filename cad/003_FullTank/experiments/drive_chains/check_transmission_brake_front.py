"""Check saved front-brake hierarchy, joint interfaces and retained material."""
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
standard=read(a.standard_manifest);prior_report=read(source.parent/'report.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
assert all(sha(ROOT/f)==v for f,v in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in data['occurrences']} for data in [m,old,standard]]
checks=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));write(out/'check_progress.json',checks);print(name,bool(passed),flush=True)
def near(name,value,expected=0,tol=1e-5):ck(name,abs(value-expected)<tol,actual=value,expected=expected,tolerance=tol)
def error(one,two):return float(np.max(np.abs(np.array(one)-two)))
expected=r['expected_new_occurrences'];revised=r['expected_revised_occurrences'];newdefs=set(r['new_definitions']);changed=set(r['changed_definitions'])
counts={suffix:sum(n.endswith(suffix) for n in expected) for suffix in ['FrontEar','FrontPin','FrontCotter','AdjustingScrew','AdjustingSpring','AdjustingNut','Swivel','Lever']}
ck('Source-counted 100 new components and no duplicate installed definitions',counts==dict(FrontEar=8,FrontPin=8,FrontCotter=8,AdjustingScrew=4,AdjustingSpring=4,AdjustingNut=4,Swivel=4,Lever=4)
   and sum('FrontSteelRivet' in n for n in expected)==56 and len(expected)==100
   and rows.keys()==prior.keys()|expected.keys() and len(rows)==2957,counts=counts)
ck('Only eight backings and 24 covered copper rivets revised',len(revised)==32 and len(r['affected_occurrences'])==132
   and set(r['affected_occurrences'])==set(expected)|set(revised)
   and set(revised)=={hand+role+'Brake'+half+suffix for hand in ['Port','Starboard'] for role in ['LowSpeed','Track']
       for half in ['Upper','Lower'] for suffix in ['Band','Segment1Rivet1','Segment1Rivet2','Segment1Rivet3']})
frames=[]
for name,row in rows.items():
    target=expected.get(name,revised.get(name,prior.get(name)));delta=error(row['frame'],target['frame'])
    frames.append(dict(name=name,error=delta,passed=delta<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners']))
ck('All saved occurrence definitions, composed frames and owning parents match',all(v['passed'] for v in frames))
ck('Every inherited occurrence retains its original world frame',all(error(rows[n]['frame'],v['frame'])<1e-7 for n,v in prior.items()))
assemblies=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name];added=set(r['added_children'].get(name,[]))|(newdefs if name=='Definitions' else set())
    assemblies.append(dict(name=name,passed=error(before['local'],after['local'])<1e-7 and error(before['world'],after['world'])<1e-7
        and set(after['children'])==set(before['children'])|added))
ck('Twelve new joint groups; inherited assembly frames preserved',not r['assembly_revisions'] and len(r['new_assemblies'])==12
   and all(v['passed'] for v in assemblies) and m['assemblies'].keys()==old['assemblies'].keys()|set(r['new_assemblies']) and len(m['assemblies'])==288)
ck('Eight new physical definitions; exactly two backings revised',len(newdefs)==8 and changed=={'Def_BrakeBand_low_band','Def_BrakeBand_track_band'}
   and m['definitions'].keys()==old['definitions'].keys()|newdefs and len(m['definitions'])==492
   and all(v['properties']==m['definitions'][n]['properties'] for n,v in old['definitions'].items()))
long_ids={n for n,v in rows.items() if v['definition']=='Def_BrakeAnchor_long_copper_rivet'}
prior_long={n for n,v in prior.items() if v['definition']=='Def_BrakeAnchor_long_copper_rivet'}
ck('Exactly 24 front rivets change to longer stock, preserving rear long rivets',long_ids==prior_long|{n for n in revised if 'Rivet' in n} and len(long_ids)==40)
import FreeCAD as App
import Part
V=App.Vector;cache={};c=r['controls'];d=r['details'];bc=read(HERE/'transmission_brake_band_study/controls.json')['controls'];ac=prior_report['controls'];ad=prior_report['details']
def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        record={'new':m,'old':old,'standard':standard}[scope]['definitions'][name];f=Path(record['brep_path']);assert sha(f)==record['brep_sha256']
        s=Part.Shape();s.read(str(f));assert s.Placement.isIdentity();cache[key]=s
    return cache[key].copy()
def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name];s=definition(row['definition'],scope);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def cylinders(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-7]
def coverage(fs,gs):
    result=[]
    for f in fs:
        matching=[g for g in gs if abs(f.Surface.Radius-g.Surface.Radius)<1e-7 and f.Surface.Axis.cross(g.Surface.Axis).Length<1e-7
            and (f.Surface.Center-g.Surface.Center).cross(g.Surface.Axis).Length<1e-7]
        if not matching:result.append(False);continue
        missing=f.cut(Part.makeCompound(matching));result.append(not missing.Faces and abs(missing.Area)<1e-5)
    return bool(result) and all(result)
def planar_contact(one,two):
    area=0.
    for f in one.Faces:
        if not isinstance(f.Surface,Part.Plane):continue
        for g in two.Faces:
            if not isinstance(g.Surface,Part.Plane):continue
            if f.normalAt(0,0).cross(g.normalAt(0,0)).Length<1e-7 and abs((f.CenterOfMass-g.CenterOfMass).dot(f.normalAt(0,0)))<1e-7:
                area+=f.common(g).Area
    return area
for name in sorted(newdefs|changed):
    s=definition(name);ck(name+' valid single solid',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
for role,mark in [('low','MX48'),('track','MX46')]:
    dr=d['brakes'][role];band=definition('Def_BrakeBand_'+role+'_band');ear=definition('Def_BrakeFront_'+role+'_ear')
    rad=(11.75 if role=='low' else 12)*25.4+5/16*25.4+bc['steel_stock']
    foot=cylinders(ear,rad);back=cylinders(band,rad)
    ck(mark+' complete cylindrical foot seat',coverage(foot,back))
    moved=ear.copy();moved.translate(V(.05,0,0));ck(mark+' displaced-foot negative rejected',not coverage(cylinders(moved,rad),back))
    bore=cylinders(ear,c['pin_diameter']/2+c['pin_bore_allowance']);ck(mark+' paired coaxial pivot bores',len(bore)==2
        and all(f.Surface.Axis.cross(V(0,1,0)).Length<1e-7 for f in bore))
    for i,f in enumerate(bore):
        near(mark+' lug stock '+str(i),f.BoundBox.YLength,c['lug_stock'])
        near(mark+' pivot height '+str(i),f.Surface.Center.z,c['pin_height'])
    tool=Part.makeCylinder(c['pin_diameter']/2+c['pin_bore_allowance'],150,V(dr['pin_x_mm'],-75,c['pin_height']),V(0,1,0))
    near(mark+' complete pivot bore open',ear.common(tool).Volume)
    plugged=ear.fuse(Part.makeCylinder(c['pin_diameter']/2+c['pin_bore_allowance'],c['lug_stock'],V(dr['pin_x_mm'],c['lug_y']-c['lug_stock']/2,c['pin_height']),V(0,1,0)))
    ck(mark+' plugged-bore negative rejected',plugged.common(tool).Volume>1)
    oldband=definition('Def_BrakeBand_'+role+'_band','old');tools=[];seats=[]
    for joint in dr['steel_joints']:
        pose=App.Placement(App.Matrix(*joint['frame']));rr=ac['steel_shank_diameter']/2+ac['steel_hole_clearance'];k=math.tan(math.radians(ac['steel_countersink_angle_deg']/2))
        tool=Part.makeCylinder(rr,60,V(0,0,-5)).fuse(Part.makeCone(ac['steel_head_radius']+5*k,rr,ad['steel_rivet']['head_depth_mm']+5,V(0,0,-5)));tool.Placement=pose;tools.append(tool)
        near(mark+' open steel joint '+str(joint['index']),band.common(tool).Volume+ear.common(tool).Volume)
        rivet=definition('Def_BrakeAnchor_steel_rivet');rivet.Placement=pose;seats.append(planar_contact(rivet,ear))
    ck(mark+' source front steel rivet count',len(dr['steel_joints'])==(8 if role=='low' else 6))
    ck(mark+' all steel upset heads seat on the foot',all(area>10 for area in seats),areas_mm2=seats)
    removed=oldband.cut(band);extra=band.cut(oldband);allowed=Part.makeCompound(tools)
    remainder=removed.cut(allowed) if removed.Faces else removed
    ck(mark+' removed backing stock confined to steel holes',not remainder.Faces and abs(remainder.Volume)<1e-5)
    pockets=[];old_grip=ad['band_details']['rivet']['grip_mm']
    for joint in dr['lining_joints']:
        tool=Part.makeCylinder(bc['rivet_tail_radius']+.05,10,V(0,0,old_grip));tool.Placement=App.Placement(App.Matrix(*joint['frame']));pockets.append(tool)
    remainder=extra.cut(Part.makeCompound(pockets)) if extra.Faces else extra
    ck(mark+' added backing stock confined to covered upset pockets',not remainder.Faces and abs(remainder.Volume)<1e-5)
contacts=[]
for hand in ['Port','Starboard']:
    sign=1 if hand=='Port' else -1
    for role,label in [('low','LowSpeed'),('track','Track')]:
        prefix=hand+label+'Brake'
        for half,member in [('Upper','AdjustingScrew'),('Lower','Lever')]:
            hp=prefix+half;ear=shape(hp+'FrontEar');pin=shape(hp+'FrontPin');cotter=shape(hp+'FrontCotter');eye=shape(prefix+member)
            near(hp+' head clearance at ear',pin.distToShape(ear)[0],c['pin_axial_clearance'])
            near(hp+' eye side/radial clearance',eye.distToShape(ear)[0],c['eye_side_clearance'])
            moved=pin.copy();moved.translate(V(0,sign*1,0));ck(hp+' outward pin motion stopped by head',moved.common(ear).Volume>1)
            moved=pin.copy();moved.translate(V(0,-sign*1,0));ck(hp+' inward pin motion stopped by cotter',moved.common(cotter).Volume>1)
            center=V(*[rows[hp+'FrontPin']['frame'][i] for i in [3,7,11]])
            axis=V(0,1,0);bore=Part.makeCylinder(c['pin_diameter']/2,150,center-V(0,75,0),axis)
            near(hp+' pin axis passes through both ear lugs and eye',bore.common(ear).Volume+bore.common(eye).Volume)
        screw=shape(prefix+'AdjustingScrew');spring=shape(prefix+'AdjustingSpring');swivel=shape(prefix+'Swivel');nut=shape(prefix+'AdjustingNut');lever=shape(prefix+'Lever')
        rotation=App.Placement(App.Matrix(*rows[prefix+'AdjustingScrew']['frame'])).Rotation;axis=rotation.multVec(V(0,0,1))
        areas={key:planar_contact(one,two) for key,one,two in [('screw_spring',screw,spring),('spring_swivel',spring,swivel),('swivel_nut',swivel,nut)]}
        ck(prefix+' spring and nut have actual planar bearing contacts',all(v>1 for v in areas.values()),areas_mm2=areas)
        lifted=spring.copy();lifted.translate(axis*.1)
        ck(prefix+' lifted-spring negative loses shoulder contact',planar_contact(lifted,screw)<1e-5)
        near(prefix+' swivel journal radial clearance',swivel.distToShape(lever)[0],c['swivel_bore_allowance'])
        # Measure the saved screw axis at the saved swivel center independently
        # of the layout recipe; nominal thread interfaces remain cylindrical.
        top=V(*[rows[prefix+'AdjustingScrew']['frame'][i] for i in [3,7,11]])
        sw=V(*[rows[prefix+'Swivel']['frame'][i] for i in [3,7,11]])
        near(prefix+' screw and swivel bore coaxial',(sw-top).cross(axis).Length)
        drill=Part.makeCylinder(c['screw_radius'],100,sw-axis*50,axis)
        near(prefix+' screw passage through swivel is open',swivel.common(drill).Volume)
        contacts.append(dict(name=prefix,areas_mm2=areas))
all_shapes={n:shape(n) for n in rows}
def bounds(s):
    bb=s.copy().cleaned().BoundBox;return [bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax]
def collisions(others,label,same):
    names=sorted(others);boxes=np.array([bounds(others[n]) for n in names]);seen=set();records=[]
    for name in r['affected_occurrences']:
        one=all_shapes[name];bb=np.array(bounds(one));possible=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for i in possible:
            other=names[i];pair=tuple(sorted([name,other])) if same else (name,other)
            if (same and name==other) or pair in seen:continue
            seen.add(pair);v=one.common(others[other]).Volume;records.append(dict(first=name,second=other,common_mm3=v,passed=abs(v)<1e-5))
        write(out/(label+'_material_progress.json'),records);print(label,name,len(records),'pairs',flush=True)
    ck(label+' all nearby material pairs clear',all(v['passed'] for v in records),pair_count=len(records));return records
development=collisions(all_shapes,'development',True)
excluded=(set(rows)&set(tank))|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
context={n:shape(n,'standard') for n,v in tank.items() if n not in excluded and v['representation']=='assembly'}
standard_pairs=collisions(context,'standard',False)
result=dict(local_front_checks_passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],source_native_sha256=sha(source),
    checker_sha256=sha(Path(__file__)),checks=checks,occurrence_frames=frames,assembly_checks=assemblies,contacts=contacts,
    development_material_pairs=development,standard_material_pairs=standard_pairs,standard_manifest_sha256=sha(a.standard_manifest),
    standard_context_count=len(context),excluded_standard_occurrences=sorted(excluded&set(tank)),historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result);print('Finished',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_front_checks_passed']
