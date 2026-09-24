"""Inspect saved rear brake joints, changed backing material and entire context."""
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
ck('Source-counted new components: 8 brackets, 60 steel rivets, 4 pins, 4 springs, 4 retainer rivets, 2 spacers',
   len(expected)==82 and [sum(n.endswith(s) for n in expected) for s in ['AnchorBracket','AnchorPin','RetainerSpring','RetainerRivet','RetainerSpacer']]==[8,4,4,4,2]
   and sum('AnchorSteelRivet' in n for n in expected)==60 and rows.keys()==prior.keys()|expected.keys() and len(rows)==2857)
ck('Exactly 248 band/lining/rivet occurrences revised; total 330 affected',len(revised)==248 and len(r['affected_occurrences'])==330
   and set(r['affected_occurrences'])==set(expected)|set(revised))
frames=[]
for name,row in rows.items():
    target=expected.get(name,revised.get(name,prior.get(name)));delta=error(row['frame'],target['frame'])
    frames.append(dict(name=name,error=delta,passed=delta<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners']))
ck('All occurrence definitions, composed frames and owning parents match',all(v['passed'] for v in frames))
assemblies=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name];target=r['assembly_revisions'].get(name,before)
    added=newdefs if name=='Definitions' else set(r['added_children'].get(name,[]))
    assemblies.append(dict(name=name,passed=error(target['local'],after['local'])<1e-7 and error(target['world'],after['world'])<1e-7
        and set(after['children'])==set(before['children'])|added))
ck('Only 24 lining-group frames revised and eight anchor groups added',len(r['assembly_revisions'])==24 and len(r['new_assemblies'])==8
   and all(v['passed'] for v in assemblies) and m['assemblies'].keys()==old['assemblies'].keys()|set(r['new_assemblies']) and len(m['assemblies'])==276)
ck('Ten new definitions; exactly two backings revised',len(newdefs)==10 and changed=={'Def_BrakeBand_low_band','Def_BrakeBand_track_band'}
   and m['definitions'].keys()==old['definitions'].keys()|newdefs and len(m['definitions'])==484
   and all(v['properties']==m['definitions'][n]['properties'] for n,v in old['definitions'].items()))
long_ids={n for n,v in rows.items() if v['definition']=='Def_BrakeAnchor_long_copper_rivet'}
ck('Only sixteen covered lining rivets use longer stock',long_ids=={hand+role+'Brake'+half+'Segment3Rivet'+str(i)
   for hand in ['Port','Starboard'] for role in ['LowSpeed','Track'] for half in ['Upper','Lower'] for i in [8,9]})
import FreeCAD as App
import Part
V=App.Vector;cache={};c=r['controls'];d=r['details'];bc=read(HERE/'transmission_brake_band_study/controls.json')['controls']
phase=App.Placement(V(),App.Rotation(V(0,1,0),c['rear_split_half_gap_deg']-bc['rear_split_half_gap_deg']))
phase_checks=[]
for name in r['assembly_revisions']:
    required=phase.multiply(App.Placement(App.Matrix(*old['assemblies'][name]['local'])))
    phase_checks.append(error(list(required.toMatrix().A),m['assemblies'][name]['local'])<1e-7)
ck('All lining groups advance only by independently computed split-angle change',all(phase_checks))
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
        # The bearing surface can be split into several patches by the
        # restored lining-rivet pockets. Require full coverage by their union;
        # no single supporting face has to span the whole receiving face.
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
spacer=definition('Def_BrakeAnchor_spacer')
ck('MX82 printed 0.189 inch bore and half-inch outside diameter',len(cylinders(spacer,.189*25.4/2))==1 and len(cylinders(spacer,.5*25.4/2))==1)
near('MX82 printed three-eighth-inch thickness',spacer.BoundBox.YLength,.375*25.4)
for role,diam,length in [('steel_rivet',.375,1.375),('long_copper_rivet',.25,1.375),('low_retainer_rivet',.1875,1.375),('track_retainer_rivet',.1875,.875)]:
    s=definition('Def_BrakeAnchor_'+role);ck(role+' source nominal shank diameter',bool(cylinders(s,diam*25.4/2)))
    key='steel_stock_length' if role=='steel_rivet' else 'lining_long_stock' if role=='long_copper_rivet' else 'retainer_rivet_'+role.split('_')[0]+'_stock'
    near(role+' source listed stock length',c[key],length*25.4)
for role,mark in [('low','MX49'),('track','MX47')]:
    dr=d['brakes'][role];band=definition('Def_BrakeBand_'+role+'_band');bracket=definition('Def_BrakeAnchor_'+role+'_bracket')
    rad=(11.75 if role=='low' else 12)*25.4+5/16*25.4+bc['steel_stock']
    foot=cylinders(bracket,rad);back=cylinders(band,rad)
    ck(mark+' complete cylindrical foot seat',coverage(foot,back))
    moved=bracket.copy();moved.translate(V(.05,0,0));ck(mark+' displaced-foot negative rejected',not coverage(cylinders(moved,rad),back))
    bore=cylinders(bracket,12+c['lug_bore_allowance']);ck(mark+' one coaxial anchor bore',len(bore)==1)
    near(mark+' lug stock',bore[0].BoundBox.YLength,c['lug_stock'])
    near(mark+' anchor X',bore[0].Surface.Center.x,-prior_report['dimensions']['lower_anchor_radius_mm'])
    near(mark+' anchor Z',bore[0].Surface.Center.z)
    tool=Part.makeCylinder(12+c['lug_bore_allowance'],150,V(-dr['anchor_radius_mm'],-75,0),V(0,1,0))
    near(mark+' complete anchor bore open',bracket.common(tool).Volume)
    plugged=bracket.fuse(Part.makeCylinder(12+c['lug_bore_allowance'],c['lug_stock'],V(-dr['anchor_radius_mm'],dr['lug_y_mm']-c['lug_stock']/2,0),V(0,1,0)))
    ck(mark+' plugged-bore negative rejected',plugged.common(tool).Volume>1)
    # Band changes are permitted only in the declared new steel holes and in
    # the old lining-rivet upset pockets covered by the rear foot.
    oldband=definition('Def_BrakeBand_'+role+'_band','old')
    oldband.rotate(V(),V(0,1,0),c['rear_split_half_gap_deg']-bc['rear_split_half_gap_deg'])
    steel_tools=[]
    for joint in dr['steel_joints']:
        pose=App.Placement(App.Matrix(*joint['frame']));rr=c['steel_shank_diameter']/2+c['steel_hole_clearance'];k=math.tan(math.radians(c['steel_countersink_angle_deg']/2))
        tool=Part.makeCylinder(rr,60,V(0,0,-5)).fuse(Part.makeCone(c['steel_head_radius']+5*k,rr,d['steel_rivet']['head_depth_mm']+5,V(0,0,-5)));tool.Placement=pose;steel_tools.append(tool)
        near(mark+' open steel joint '+str(joint['index']),band.common(tool).Volume+bracket.common(tool).Volume)
    removed=oldband.cut(band);extra=band.cut(oldband);allowed=Part.makeCompound(steel_tools)
    remainder=removed.cut(allowed) if removed.Faces else removed
    ck(mark+' removed backing stock confined to new steel holes',not remainder.Faces and abs(remainder.Volume)<1e-5)
    pockets=[]
    old_grip=bc['lining_stock']+bc['steel_stock']-bc['tail_spotface_depth']-bc['rivet_head_recess']
    for joint in dr['lining_joints']:
        tool=Part.makeCylinder(bc['rivet_tail_radius']+.05,10,V(0,0,old_grip));tool.Placement=App.Placement(App.Matrix(*joint['frame']));pockets.append(tool)
    remainder=extra.cut(Part.makeCompound(pockets)) if extra.Faces else extra
    ck(mark+' added backing stock confined to covered upset pockets',not remainder.Faces and abs(remainder.Volume)<1e-5)
    ck(mark+' correct rear-foot steel-rivet count',len(dr['steel_joints'])==(8 if role=='low' else 7))
    # Each formed rivet must bear on the actual spotface; overlap is checked
    # separately across all affected occurrences below.
    seats=[]
    for joint in dr['steel_joints']:
        rivet=definition('Def_BrakeAnchor_steel_rivet');rivet.Placement=App.Placement(App.Matrix(*joint['frame']))
        seats.append(planar_contact(rivet,bracket))
    ck(mark+' all steel upset heads seat on the foot',all(area>10 for area in seats),areas_mm2=seats)
contacts=[]
for hand in ['Port','Starboard']:
    sign=1 if hand=='Port' else -1
    for role,label in [('low','LowSpeed'),('track','Track')]:
        prefix=hand+label+'Brake';half=('Lower' if hand=='Port' else 'Upper') if role=='low' else ('Upper' if hand=='Port' else 'Lower')
        hp=prefix+half;pin=shape(prefix+'AnchorPin');spring=shape(hp+'RetainerSpring');link=shape(hand+label+'SuspensionLink')
        ck(hp+' source-handed spring present',hp+'RetainerSpring' in expected)
        near(prefix+' anchor height matches lower M337 eye',rows[prefix+'AnchorPin']['frame'][11],prior_report['interfaces'][hand+label]['lower_mm'][2])
        near(prefix+' anchor X matches lower M337 eye',rows[prefix+'AnchorPin']['frame'][3],prior_report['interfaces'][hand+label]['lower_mm'][0])
        near(prefix+' pin head clearance at link',pin.distToShape(link)[0],c['link_axial_allowance'])
        moved=pin.copy();moved.translate(V(0,sign*1,0));ck(prefix+' outward pin motion stopped by head at link',moved.common(link).Volume>1)
        moved=pin.copy();moved.translate(V(0,-sign*1,0));ck(prefix+' inward pin motion stopped by spring',moved.common(spring).Volume>1)
        target=shape(hp+'RetainerSpacer') if role=='low' else shape(hp+'AnchorBracket')
        area=planar_contact(spring,target);ck(prefix+' spring has a physical seat',area>10,area_mm2=area)
        rivet=shape(hp+'RetainerRivet');ck(prefix+' retainer upset head bears on spring',planar_contact(rivet,spring)>10)
        if role=='low':ck(prefix+' spacer bears on bracket',planar_contact(target,shape(hp+'AnchorBracket'))>10)
        if role=='track':
            gap=pin.distToShape(shape(hand+'Casing_Body'))[0];ck(prefix+' anchor clears chain case',gap>0.1,gap_mm=gap)
        contacts.append(dict(name=prefix,spring_seat_area_mm2=area))
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
result=dict(local_anchor_checks_passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],source_native_sha256=sha(source),
    checker_sha256=sha(Path(__file__)),checks=checks,occurrence_frames=frames,assembly_checks=assemblies,contacts=contacts,
    development_material_pairs=development,standard_material_pairs=standard_pairs,standard_manifest_sha256=sha(a.standard_manifest),
    standard_context_count=len(context),excluded_standard_occurrences=sorted(excluded&set(tank)),historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result);print('Finished',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_anchor_checks_passed']
