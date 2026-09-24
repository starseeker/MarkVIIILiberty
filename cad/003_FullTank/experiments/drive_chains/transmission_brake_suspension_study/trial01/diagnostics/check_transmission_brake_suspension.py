"""Independently inspect saved brake support shapes, seats, frames and context."""
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
p.add_argument('--standard-manifest',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json')
m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
standard=read(a.standard_manifest);native=out/r['native_file']
assert sha(native)==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
assert all(sha(ROOT/f)==v for f,v in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in d['occurrences']} for d in [m,old,standard]]
checks=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));write(out/'check_progress.json',checks)
    print(name,bool(passed),flush=True)
def near(name,value,expected=0,tol=1e-5):ck(name,abs(value-expected)<tol,actual=value,expected=expected,tolerance=tol)
def error(a,b):return float(np.max(np.abs(np.array(a)-b)))
expected=r['expected_new_occurrences'];newdefs=set(r['new_definitions'])
ck('Exactly four M338 and two M385 occurrences added',len(expected)==6 and rows.keys()==prior.keys()|expected.keys()
   and len(rows)==r['expected_physical_occurrences']
   and sum(v['definition']=='Def_BrakeSuspension_bracket' for v in expected.values())==4
   and sum(v['definition']=='Def_BrakeSuspension_stop' for v in expected.values())==2)
frames=[]
for name,row in rows.items():
    target=expected.get(name,prior.get(name));delta=error(row['frame'],target['frame'])
    frames.append(dict(name=name,error=delta,passed=delta<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners']))
ck('All prior frames and owners retained; new composed frames correct',all(v['passed'] for v in frames))
assemblies=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name]
    added=newdefs if name=='Definitions' else {'TransmissionBrakeSuspension'} if name=='TransmissionMountingFrame' else set()
    assemblies.append(dict(name=name,passed=error(before['local'],after['local'])<1e-7 and error(before['world'],after['world'])<1e-7
        and set(after['children'])==set(before['children'])|added))
ck('Prior assembly frames and children retained',all(v['passed'] for v in assemblies)
   and m['assemblies'].keys()==old['assemblies'].keys()|set(r['new_assemblies']))
ck('Existing definition identities and source properties retained',m['definitions'].keys()==old['definitions'].keys()|newdefs
   and all(v['properties']==m['definitions'][n]['properties'] for n,v in old['definitions'].items()) and not r['changed_definitions'])
for role,mark,rid in [('bracket','M338','SNL:96:017'),('stop','M385','SNL:96:018')]:
    props=m['definitions']['Def_BrakeSuspension_'+role]['properties']
    ck(mark+' source identity retained',props['SourcePartMark']==mark and rid in props['SourceRecords'])
import FreeCAD as App
import Part
V=App.Vector;cache={}
def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        d={'new':m,'old':old,'standard':standard}[scope]['definitions'][name];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));assert s.Placement.isIdentity();cache[key]=s
    return cache[key].copy()
def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name];s=definition(row['definition'],scope)
    s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def area(one,two,axis):
    total=0
    for f in one.Faces:
        if not isinstance(f.Surface,Part.Plane) or abs(abs(f.normalAt(0,0).dot(axis))-1)>1e-7:continue
        for g in two.Faces:
            if not isinstance(g.Surface,Part.Plane) or abs(abs(g.normalAt(0,0).dot(axis))-1)>1e-7:continue
            if f.distToShape(g)[0]<1e-6:total+=f.common(g).Area
    return total
c=r['controls'];d=r['dimensions'];bracket=definition('Def_BrakeSuspension_bracket');stop=definition('Def_BrakeSuspension_stop')
for name,s in [('M338',bracket),('M385',stop)]:
    ck(name+' saved shape valid single solid',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
rad=c['pin_bore_diameter']/2+c['pin_bore_clearance'];rr=d['lug_radius_mm'];stock=c['lug_stock']
foot_length=d['foot_front_mm']-d['foot_rear_mm'];crown=d['pin_drop_mm']-d['foot_stock_mm']
expected_volume=(2*rr*crown+math.pi*rr*rr/2-math.pi*rad*rad)*stock+foot_length*c['foot_width']*d['foot_stock_mm']
near('Bracket retains complete foot and rounded bored lug volume',bracket.Volume,expected_volume)
near('Stop retains continuous L-section stock',stop.Volume,c['stop_width']*c['stop_stock']*(d['stop_height_mm']+c['stop_toe_depth']-c['stop_stock']))
bore=Part.makeCylinder(rad,stock+2,V(0,-stock/2-1,0),V(0,1,0))
near('M339 receiving bore is completely open',bracket.common(bore).Volume)
cylinders=[f for f in bracket.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7]
ck('Analytic pin bore and rounded lower end retained',any(abs(f.Surface.Radius-rad)<1e-7 for f in cylinders)
   and any(abs(f.Surface.Radius-rr)<1e-7 for f in cylinders))
filled=bracket.fuse(Part.makeCylinder(rad,stock,V(0,-stock/2,0),V(0,1,0)))
ck('Filled-bore negative control rejected',filled.common(bore).Volume>100)
top=shape('TransmissionFrame_TopChannel');contacts=[]
for name in expected:
    one=shape(name);is_bracket=name.endswith('Bracket')
    target_area=foot_length*c['foot_width'] if is_bracket else c['stop_toe_depth']*c['stop_width']
    seat=area(one,top,V(0,0,1))
    near(name+' complete foot bearing on channel',seat,target_area)
    near(name+' no channel penetration',one.common(top).Volume)
    shifted=one.copy();shifted.translate(V(0,0,-.01))
    near(name+' lifted seat loses bearing',area(shifted,top,V(0,0,1)))
    key=name.removesuffix('Bracket').removesuffix('Stop');interface=r['interfaces'][key]
    drum=shape(interface['occurrence']);faces=[f for f in drum.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7]
    face=max(faces,key=lambda f:(f.Surface.Radius,f.Area));center=(face.BoundBox.YMin+face.BoundBox.YMax)/2
    sign=1 if name.startswith('Port') else -1
    near(name+' centered on saved brake friction face',rows[name]['frame'][7],center+sign*c['axial_offset'])
    axis=face.Surface.Center;envelope=Part.makeCylinder(face.Surface.Radius,face.BoundBox.YLength,V(axis.x,face.BoundBox.YMin,axis.z),V(0,1,0))
    gap=one.distToShape(envelope)[0];ck(name+' clears complete rotating drum envelope',gap>1,clearance_mm=gap)
    contacts.append(dict(name=name,channel_area_mm2=seat,drum_envelope_clearance_mm=gap))
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
    ck(label+' all nearby material pairs clear',all(v['passed'] for v in records),pair_count=len(records));return records
development=collisions(all_shapes,'development',True)
excluded=(set(rows)&set(tank))|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
context={n:shape(n,'standard') for n,v in tank.items() if n not in excluded and v['representation']=='assembly'}
standard_pairs=collisions(context,'standard',False)
pending=[n for n,v in old['definitions'].items() if v['brep_sha256']!=m['definitions'][n]['brep_sha256']]
result=dict(local_suspension_checks_passed=all(v['passed'] for v in checks),native_sha256=sha(native),source_native_sha256=sha(source),
    checker_sha256=sha(Path(__file__)),checks=checks,occurrence_frames=frames,assembly_checks=assemblies,contacts=contacts,
    development_material_pairs=development,standard_material_pairs=standard_pairs,standard_manifest_sha256=sha(a.standard_manifest),
    standard_context_count=len(context),excluded_standard_occurrences=sorted(excluded&set(tank)),
    pending_unchanged_definition_material=pending,source_axis_residual=r['source_axis_residual'],
    historical_geometry_qualified=False,installation_qualified=False,fastening_pending=True)
write(out/'independent_checks.json',result)
print('Finished',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_suspension_checks_passed']
