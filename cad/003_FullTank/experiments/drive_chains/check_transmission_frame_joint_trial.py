"""Check saved formed-gusset contacts, rivet stock, retained interfaces and context."""
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
source=ROOT/r['source_native'];native=out/r['native_file']
m=read(out/'isolated/manifest.json');old=read(source.parent/'isolated/manifest.json')
sp=a.standard_context.resolve()/'manifest.json';standard=read(sp)
assert sha(native)==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/p)==v for p,v in r['input_hashes'].items())
assert all(sha(ROOT/p)==v for p,v in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in d['occurrences']} for d in [m,old,standard]]
checks=[]
def ck(name,passed,**details):
    checks.append(dict(name=name,passed=bool(passed),**details))
    write(out/'check_progress.json',checks);print(name,bool(passed),flush=True)
def near(name,v,expected=0,tol=1e-5):ck(name,abs(v-expected)<tol,actual=v,expected=expected,tolerance=tol)
def frame_error(a,b):return float(np.max(np.abs(np.array(a)-b)))
expected=r['expected_new_occurrences'];changed=set(r['changed_definitions']);newdefs=set(r['new_definitions'])
ck('Expected source-counted 32 rivets added',len(expected)==32 and rows.keys()==prior.keys()|expected.keys()
   and len(rows)==r['expected_physical_occurrences'])
frames=[]
for name,row in rows.items():
    target=expected.get(name,prior.get(name));error=frame_error(row['frame'],target['frame'])
    frames.append(dict(name=name,passed=error<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners'],error=error))
ck('All composed occurrence frames and owners correct',all(v['passed'] for v in frames))
assembly=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name]
    added=newdefs if name=='Definitions' else {'FrameGussetRivets'} if name=='TransmissionMountingFrame' else set()
    assembly.append(dict(name=name,passed=frame_error(before['local'],after['local'])<1e-7
        and frame_error(before['world'],after['world'])<1e-7 and set(after['children'])==set(before['children'])|added))
ck('Prior assembly frames retained and only intended groups added',all(v['passed'] for v in assembly)
   and m['assemblies'].keys()==old['assemblies'].keys()|set(r['new_assemblies']))
ck('Definition identities and source properties retained',m['definitions'].keys()==old['definitions'].keys()|newdefs
   and all(v['properties']==m['definitions'][n]['properties'] for n,v in old['definitions'].items()))
pending=[n for n,v in old['definitions'].items() if n not in changed and v['brep_sha256']!=m['definitions'][n]['brep_sha256']]
import FreeCAD as App
import Part
from transmission_support_parts import box
V=App.Vector;cache={}
def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        d={'new':m,'old':old,'standard':standard}[scope]['definitions'][name]
        p=Path(d['brep_path']);assert sha(p)==d['brep_sha256']
        s=Part.Shape();s.read(str(p));assert s.Placement.isIdentity();cache[key]=s
    return cache[key].copy()
def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name];s=definition(row['definition'],scope)
    s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def area(first,second,axis):
    total=0
    for f in first.Faces:
        if not isinstance(f.Surface,Part.Plane) or abs(abs(f.normalAt(0,0).dot(axis))-1)>1e-7:continue
        for g in second.Faces:
            if not isinstance(g.Surface,Part.Plane) or abs(abs(g.normalAt(0,0).dot(axis))-1)>1e-7:continue
            if f.distToShape(g)[0]<1e-6:total+=f.common(g).Area
    return total
c=r['controls'];d=r['rivet'];rad=c['rivet_diameter']/2;headrad=d['head_radius_mm'];grip=d['grip_mm']
for name in sorted(changed|newdefs):
    s=definition(name);ck(name+' valid single solid',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
rivet=definition(r['new_definitions'][0])
stock=Part.makeCylinder(rad,grip)
near('Full cylindrical grip retained',stock.cut(rivet).Volume)
tail=rivet.common(box(-100,100,-100,100,grip,grip+100))
near('Upset head preserves unformed stock volume',tail.Volume,math.pi*rad*rad*(c['rivet_stock_length']-grip))
near('Printed shank diameter retained',max(f.Surface.Radius for f in rivet.Faces if isinstance(f.Surface,Part.Cylinder)),rad)
near('Total rivet stock volume plus estimated factory head',rivet.Volume,
     math.pi*rad*rad*c['rivet_stock_length']+math.pi*d['factory_head_height_mm']*(3*headrad*headrad+d['factory_head_height_mm']**2)/6)
joint_records=[];checked=set()
for j in r['joints']:
    name=j['name'];fastener=shape(name);channel=shape(j['channel']);gusset=shape(j['gusset'])
    fp=App.Placement(App.Matrix(*rows[name]['frame']));axis=fp.Rotation.multVec(V(0,0,1))
    tool=Part.makeCylinder(rad,grip);tool.Placement=fp
    near(name+' complete receiving bore',tool.common(channel).Volume+tool.common(gusset).Volume)
    head_area=area(fastener,channel,axis);tail_area=area(fastener,gusset,axis)
    expected_area=math.pi*(headrad*headrad-(rad+c['hole_radial_clearance'])**2)
    ck(name+' full bearing faces',head_area>.99*expected_area and tail_area>.99*expected_area,
       head_area_mm2=head_area,tail_area_mm2=tail_area,expected_area_mm2=expected_area)
    near(name+' factory head seated',fastener.distToShape(channel)[0])
    near(name+' upset head seated',fastener.distToShape(gusset)[0])
    moved=fastener.copy();moved.translate(axis*-.01)
    near(name+' lifted factory head loses bearing',area(moved,channel,axis))
    moved=fastener.copy();moved.translate(fp.Rotation.multVec(V(.5,0,0)))
    ck(name+' displaced shank hits receiver',moved.common(channel).Volume+moved.common(gusset).Volume>1)
    joint_records.append(dict(name=name,head_area_mm2=head_area,tail_area_mm2=tail_area))
    if j['kind']=='gusset_channel' and j['gusset'] not in checked:
        checked.add(j['gusset']);angle=j['gusset'].replace('TopGusset','Angle').replace('BottomGusset','Angle')
        old_area=area(shape(j['gusset'],'old'),shape(angle,'old'),V(1,0,0))
        contact=area(gusset,shape(angle),V(1,0,0))
        expect=c['angle_leg_y']*(c['return_height']-c['gusset_stock'])
        near(j['gusset']+' return-to-upright overlap',contact,expect)
        near(j['gusset']+' original return contact was absent',old_area)
        near(j['gusset']+' no upright penetration',gusset.common(shape(angle)).Volume)
for side in ['Left','Right']:
    name='TransmissionFrame_'+side+'InnerAngle';plate=shape('TransmissionFrame_MiddleDiaphragm');angle=shape(name)
    contact=area(plate,angle,V(1,0,0))
    height=definition('Def_TransmissionFrame_middle_diaphragm').BoundBox.ZLength
    expected_area=(c['angle_leg_y']-c['angle_stock'])*height-4*math.pi*(rad+c['hole_radial_clearance'])**2
    near(side+' diaphragm/upright overlap',contact,expected_area)
    near(side+' diaphragm has no upright penetration',plate.common(angle).Volume)
    near(side+' old diaphragm broad-face contact was absent',area(shape('TransmissionFrame_MiddleDiaphragm','old'),shape(name,'old'),V(1,0,0)))
# Explicitly preserve all twenty earlier MX1 bearing-pad/channel contacts.
prior_report=read(source.parent/'report.json');pairs=set()
for j in prior_report['joints']:
    pair=(j['receiver'],j['channel'])
    if pair in pairs:continue
    pairs.add(pair)
    near(j['receiver']+' retained MX1 pad area on '+j['channel'],
         area(shape(j['receiver']),shape(j['channel']),V(1,0,0)),
         area(shape(j['receiver'],'old'),shape(j['channel'],'old'),V(1,0,0)))
affected=set(r['affected_occurrences']);all_shapes={name:shape(name) for name in rows}
def bounds(s):
    b=s.copy().cleaned().BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def collisions(others,label,same):
    names=sorted(others);boxes=np.array([bounds(others[n]) for n in names]);seen=set();result=[]
    for name in sorted(affected):
        one=all_shapes[name];bb=bounds(one)
        possible=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in possible:
            other=names[index];pair=tuple(sorted([name,other])) if same else (name,other)
            if (same and name==other) or pair in seen:continue
            seen.add(pair);v=one.common(others[other]).Volume
            result.append(dict(first=name,second=other,common_mm3=v,passed=abs(v)<1e-5))
            write(out/(label+'_material_progress.json'),result)
    ck(label+' complete nearby material pairs clear',all(v['passed'] for v in result),pair_count=len(result))
    return result
development=collisions(all_shapes,'development',True)
excluded=(set(rows)&set(tank))|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
context={n:shape(n,'standard') for n,v in tank.items() if n not in excluded and v['representation']=='assembly'}
standard_pairs=collisions(context,'standard',False)
result=dict(local_frame_checks_passed=all(v['passed'] for v in checks),native_sha256=sha(native),source_native_sha256=sha(source),
    checker_sha256=sha(Path(__file__)),checks=checks,occurrence_frames=frames,assembly_checks=assembly,contacts=joint_records,
    development_material_pairs=development,standard_material_pairs=standard_pairs,standard_manifest_sha256=sha(sp),
    standard_context_count=len(context),excluded_standard_occurrences=sorted(excluded&set(tank)),
    pending_unchanged_definition_material=pending,historical_joint_layout_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result)
print('Finished',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_frame_checks_passed']
