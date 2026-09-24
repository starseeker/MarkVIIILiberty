"""Independently inspect saved casing stock, joints, frames and both physical contexts."""
import argparse
import itertools
import math
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--standard-context',type=Path,required=True)
p.add_argument('--reuse-material-from',type=Path)
a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');native=out/r['native_file'];source=ROOT/r['source_native']
assert sha(native)==r['native_sha256'] and sha(source)==r['source_native_sha256']
assert all(sha(ROOT/f)==digest for f,digest in r['input_hashes'].items())
m,old=[read(f/'isolated/manifest.json') for f in [out,source.parent]]
assert m['native_sha256']==sha(native) and old['native_sha256']==sha(source)
standard_path=a.standard_context.resolve()/'manifest.json';standard=read(standard_path)
assert sha(standard_path)==r['standard_manifest_sha256']
assert all(sha(ROOT/f)==digest for f,digest in r['standard_native_files'].items())
rows,prior,tank=[{v['name']:v for v in j['occurrences']} for j in [m,old,standard]]
affected=set(r['affected_occurrences']); replaced=set(r['replaced_definitions']);checks=[]

def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail))
    write(out/'check_progress.json',checks);print(name,bool(passed),flush=True)

def near(name,actual,expected=0,tolerance=1e-5):
    ck(name,abs(actual-expected)<tolerance,actual=actual,expected=expected,tolerance=tolerance)

frames=[]
for name,row in rows.items():
    before=prior[name];expected=r['expected_occurrence_frames'].get(name,before['frame'])
    error=float(np.max(np.abs(np.asarray(row['frame'])-expected)))
    frames.append(dict(name=name,error=error,passed=error<1e-7 and
        {k:v for k,v in row.items() if k!='frame'}=={k:v for k,v in before.items() if k!='frame'}))
ck('All 2393 occurrence identities, owners and joint frames retained',rows.keys()==prior.keys()
   and len(rows)==2393 and all(v['passed'] for v in frames))
assembly_errors=[]
for name,row in m['assemblies'].items():
    before=old['assemblies'][name]
    error=max(float(np.max(np.abs(np.asarray(row[k])-before[k]))) for k in ['local','world'])
    assembly_errors.append(dict(name=name,error=error,passed=error<1e-7 and
        {k:v for k,v in row.items() if k not in ['local','world']}==
        {k:v for k,v in before.items() if k not in ['local','world']}))
ck('Every assembly placement and child list unchanged',m['assemblies'].keys()==old['assemblies'].keys()
   and all(v['passed'] for v in assembly_errors))
ck('Exactly 12 rebuilt definitions and 157 affected occurrences',len(replaced)==12 and len(affected)==157)
preserved=[dict(name=name,exact_brep=d['brep_sha256']==old['definitions'][name]['brep_sha256'])
           for name,d in m['definitions'].items() if name not in replaced]
ck('All definition identities and source metadata retained',m['definitions'].keys()==old['definitions'].keys()
   and all(d['properties']==old['definitions'][name]['properties'] for name,d in m['definitions'].items()))

import FreeCAD as App
import Part
from casing_mount_parts import cutter
from casing_trim_parts import drill
V=App.Vector;cache={}

def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        rec={'new':m,'old':old,'standard':standard}[scope]['definitions'][name]
        f=Path(rec['brep_path']);assert sha(f)==rec['brep_sha256']
        s=Part.Shape();s.read(str(f));assert s.Placement.isIdentity();cache[key]=s
    return cache[key].copy()

def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name]
    s=definition(row['definition'],scope);s.Placement=App.Placement(App.Matrix(*row['frame']));return s

for name in sorted(replaced):
    s=definition(name)
    ck(name+' valid single solid and bounded kernel tolerance',s.isValid() and len(s.Solids)==1
       and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
c,wallc,cap,trimc,front=[r['controls'][k] for k in ['casing','mount','cap','trim','front']]
details=r['revised_details'];body=definition('Def_Casing_body');cover=definition('Def_Casing_cap')
near('Printed maximum casing width retained',c['outside_width'],6.625*25.4,1e-9)
near('Body/cap split retained',body.distToShape(cover)[0],c['cap_split_gap'],1e-6)
route=r['revised_route'];big=np.asarray(route['roller_pinion_axis_xz_mm']);small=np.asarray(route['candidate_transmission_axis_xz_mm'])
near('Casing small-axis X follows saved transmission',small[0],m['assemblies']['TransmissionCore']['world'][3],1e-7)
near('Casing small-axis Z follows saved transmission',small[1],m['assemblies']['TransmissionCore']['world'][11],1e-7)
radii=[route['pitch_mm']/(2*math.sin(math.pi/route[k]))+c['chain_radial_envelope']+c['radial_gap']+c['sheet_stock']
       for k in ['large_teeth','small_teeth']]
u=(small-big)/np.linalg.norm(small-big);q=(radii[0]-radii[1])/np.linalg.norm(small-big)
normals=[np.array([q*u[0]-sign*math.sqrt(1-q*q)*u[1],q*u[1]+sign*math.sqrt(1-q*q)*u[0]]) for sign in [1,-1]]
stock_checks=[]
def thickness(name,s,point,normal):
    point,normal=V(*point),V(*normal);normal.normalize()
    lengths=[e.Length for e in s.common(Part.makeLine(point+normal,point-normal*(c['sheet_stock']+1))).Edges]
    passed=len(lengths)==1 and abs(lengths[0]-c['sheet_stock'])<1e-6
    ck(name+' 3mm normal stock',passed,lengths_mm=lengths)
    stock_checks.append(dict(name=name,lengths_mm=lengths,passed=passed))
for label,n in zip(['upper','lower'],normals):
    for x in [1150.,1570.]:
        z=big[1]+(radii[0]-n[0]*(x-big[0]))/n[1]
        thickness(label+' tangent at '+str(x),body,[x,0,z],[n[0],0,n[1]])
for center,rad,angle,label in [(big,radii[0],math.pi+.3,'large rear'),(small,radii[1],0,'small front')]:
    nx,nz=math.cos(angle),math.sin(angle)
    thickness(label,body,[center[0]+nx*rad,0,center[1]+nz*rad],[nx,0,nz])
for x,z,owner in [(600.,900.,body),(550.,1160.,cover),(1200.,1000.,body),(small[0],small[1]+130,body)]:
    half=c['outside_width']/2 if x<front['taper_start_x'] else front['front_outside_width']/2
    for sign in [-1,1]:thickness('side '+str((x,z,sign)),owner,[x,sign*half,z],[0,sign,0])
slope=(front['front_outside_width']-c['outside_width'])/2/(front['taper_end_x']-front['taper_start_x'])
x=(front['taper_start_x']+front['taper_end_x'])/2
half=c['outside_width']/2+slope*(x-front['taper_start_x'])
for sign in [-1,1]:thickness('taper '+str(sign),body,[x,sign*half,small[1]+130],[-slope,sign,0])

def translated(tool,cy):
    s=tool.copy();s.translate(V(0,cy,0));return s

joint_checks=[]
def bore_and_seats(name,tool,receivers,fastener,expected_gaps=None):
    remaining=sum(s.common(tool).Volume for s in receivers)
    distances=[fastener.distToShape(s)[0] for s in receivers]
    overlap=sum(fastener.common(s).Volume for s in receivers)
    expected_gaps=expected_gaps if expected_gaps is not None else [0]*len(distances)
    passed=abs(remaining)<1e-5 and max(abs(x-y) for x,y in zip(distances,expected_gaps))<1e-6 and abs(overlap)<1e-5
    ck(name+' bore and fastener interfaces',passed,remaining_mm3=remaining,gaps_mm=distances,
       expected_gaps_mm=expected_gaps,overlap_mm3=overlap)
    joint_checks.append(dict(name=name,remaining_mm3=remaining,gaps_mm=distances,passed=passed))

for hand,cy in r['centers'].items():
    wall=shape('hull_engine_back');cbody=shape(hand+'Casing_Body');ccap=shape(hand+'Casing_Cap')
    angle=shape(hand+'CasingWall_Angle')
    near(hand+' collar on bulkhead',angle.distToShape(wall)[0],0,1e-6)
    ck(hand+' casing passage clearance',cbody.distToShape(wall)[0]>=c['passage_minimum_gap']-1e-6,
       distance_mm=cbody.distToShape(wall)[0])
    for role in ['wall','case']:
        for n,s in enumerate(details['wall_stations'][role]):
            name=hand+'CasingWall_'+role.title()+'Rivet%02d'%n
            tool=translated(cutter(s,wallc[role+'_rivet_diameter']+wallc['hole_diameter_clearance']),cy)
            bore_and_seats(name,tool,[angle,wall if role=='wall' else cbody],shape(name))
    for s in details['cap_stations']['rivets']:
        name=hand+'CasingCap_'+s['name']
        receivers=[shape(hand+'CasingCap_'+s['cleat']),cbody if s['owner']=='Body' else ccap]
        expected=[0,0]
        if s.get('packing'):
            packing_name=hand+'CasingCap_'+s['packing']
            receivers.append(shape(packing_name))
            expected.append(cap['hole_diameter_clearance']/2)
            near(name+' original packing-bore clearance',shape(name,'old').distToShape(shape(packing_name,'old'))[0],expected[-1],1e-6)
        bore_and_seats(name,translated(cutter(s,cap['rivet_diameter']+cap['hole_diameter_clearance']),cy),receivers,shape(name),expected)
    def faces_at_y(s,y):
        return [f for f in s.Faces if type(f.Surface).__name__=='Plane' and
                abs(f.BoundBox.YMin-y)<1e-7 and abs(f.BoundBox.YMax-y)<1e-7]
    def contact_at_y(first,second,y):
        return sum(x.common(yface).Area for x in faces_at_y(first,y) for yface in faces_at_y(second,y))
    for face,sign in [('Inner',-1),('Outer',1)]:
        packing=shape(hand+'CasingCap_'+face+'Packing')
        cleat=shape(hand+'CasingCap_Body'+face+'Cleat')
        for receiver,offset,label in [(cbody,0,'sheet'),(cleat,cap['packing_stock'],'cleat')]:
            y=cy+sign*(c['outside_width']/2+offset)
            area=contact_at_y(packing,receiver,y)
            expected_area=sum(f.Area for f in faces_at_y(packing,y))
            ck(hand+face+' packing complete '+label+' bearing face',expected_area>1000 and abs(area-expected_area)<1e-3,
               contact_area_mm2=area,packing_face_area_mm2=expected_area)
            lifted=packing.copy();lifted.translate(V(0,sign*.01,0))
            near(hand+face+' displaced packing loses '+label+' contact',contact_at_y(lifted,receiver,y),0,1e-6)
    for s in details['cap_stations']['bolts']:
        prefix=hand+'CasingCap_'+s['name'];tool=translated(cutter(s,cap['bolt_diameter']+cap['hole_diameter_clearance']),cy)
        receivers=[shape(hand+'CasingCap_'+s[key]) for key in ['body','cap']]
        near(prefix+' complete cleat bores',sum(one.common(tool).Volume for one in receivers))
        bolt,nut,washer=[shape(prefix+suffix) for suffix in ['Bolt','Nut','Washer']]
        near(prefix+' bolt head seated',bolt.distToShape(receivers[0])[0],0,1e-6)
        near(prefix+' washer seated',washer.distToShape(receivers[1])[0],0,1e-6)
        near(prefix+' nut seated',nut.distToShape(washer)[0],0,1e-6)
    for s in details['trim_stations']:
        name=hand+'CasingTrim_'+s['name']
        receivers=[shape(hand+'CasingTrim_'+s['part']),cbody if s['owner']=='Body' else ccap]
        bore_and_seats(name,translated(drill(s,trimc),cy),receivers,shape(name))
    for j in r['support_joints']:
        if j['hand']!=hand:continue
        prefix=hand+'CasingSupport_'+j['face'];bracket=shape(prefix+'Bracket')
        near(prefix+' bracket on casing',bracket.distToShape(cbody)[0],0,1e-6)
        for n,s in enumerate(j['stations']['case_rivets']):
            name=prefix+'Rivet%02d'%n
            tool=translated(cutter(s,r['controls']['support']['case_rivet_diameter']+r['controls']['support']['hole_diameter_clearance']),cy)
            bore_and_seats(name,tool,[bracket,cbody],shape(name))

def bbox(s):
    b=s.BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def bounds(names,scope):
    source_rows=rows if scope=='new' else tank
    result=[]
    for name in names:
        row=source_rows[name];b=definition(row['definition'],scope).BoundBox
        corners=np.asarray(list(itertools.product([b.XMin,b.XMax],[b.YMin,b.YMax],[b.ZMin,b.ZMax])))
        f=np.asarray(row['frame']).reshape(4,4);corners=corners@f[:3,:3].T+f[:3,3]
        result.append(np.r_[corners.min(axis=0),corners.max(axis=0)])
    return np.asarray(result)
local_pairs=[];standard_pairs=[]
material_reuse=None
if a.reuse_material_from:
    folder=a.reuse_material_from.resolve();status=read(folder/'status.json')
    assert status['native_sha256']==sha(native) and status['standard_manifest_sha256']==sha(standard_path)
    assert all(sha(folder/name)==digest for name,digest in status['files'].items())
    material_reuse=read(folder/'independent_checks.json')
    assert material_reuse['native_sha256']==sha(native) and material_reuse['source_native_sha256']==sha(source)
# Local saved receivers supersede standard occurrences with the same identity.
# These two standard pinion castings are already represented by the chain rotors.
superseded=set(rows)|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
standard_names=[name for name,row in tank.items() if row['representation']=='assembly' and name not in superseded]
for scope,names,results in [('new',list(rows),local_pairs),('standard',standard_names,standard_pairs)]:
    boxes=bounds(names,scope);pairs=set()
    for name in affected:
        b=bbox(shape(name));indices=np.flatnonzero(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))
        for i in indices:
            other=names[i]
            if scope=='new' and other==name:continue
            pairs.add(tuple(sorted([name,other])) if scope=='new' else (name,other))
    print('Material',scope,len(pairs),'pairs',flush=True)
    cached={}
    if material_reuse:
        records=material_reuse['local_material_pairs' if scope=='new' else 'standard_material_pairs']
        cached={(v['first'],v['second']):v for v in records}
        assert len(cached)==len(records) and set(cached)==pairs
    for first,second in sorted(pairs):
        if (first,second) in cached:
            volume=cached[first,second]['common_mm3']
        else:
            one,two=shape(first),shape(second,scope)
            volume=one.common(two).Volume if one.BoundBox.intersect(two.BoundBox) else 0.
        results.append(dict(first=first,second=second,common_mm3=volume,passed=abs(volume)<1e-5))
        write(out/(scope+'_material_progress.json'),results)
    ck(scope+' full-context affected material clearance',all(v['passed'] for v in results),
       pairs=len(results),failures=[v for v in results if not v['passed']])

rotor_gaps=[]
for hand in ['Port','Starboard']:
    one=shape(hand+'Casing_Body');rotor=shape(hand+'TransmissionOutput_drum')
    distance=one.distToShape(rotor)[0]
    ck(hand+' source-control rotor clearance',distance>=front['minimum_rotor_gap']-1e-6,distance_mm=distance)
    chain=[(one.distToShape(shape(name))[0],name) for name in rows if name.startswith(hand+'Chain_')]
    closest=min(chain)
    ck(hand+' positive body/chain clearance',closest[0]>0,closest=closest)
    rotor_gaps.append(dict(hand=hand,drum_gap_mm=distance,closest_body_chain_gap_mm=closest[0],closest_body_chain_occurrence=closest[1]))

write(out/'independent_checks.json',dict(local_casing_checks_passed=all(v['passed'] for v in checks),
    native_sha256=sha(native),source_native_sha256=sha(source),checker_sha256=sha(Path(__file__)),
    checks=checks,occurrence_frames=frames,assembly_frames=assembly_errors,preserved_definitions=preserved,
    pending_definition_material=[v['name'] for v in preserved if not v['exact_brep']],
    joint_checks=joint_checks,stock_checks=stock_checks,local_material_pairs=local_pairs,
    standard_material_pairs=standard_pairs,standard_context_count=len(standard_names),
    standard_manifest_sha256=sha(standard_path),
    material_reuse_status_sha256=sha(a.reuse_material_from.resolve()/'status.json') if material_reuse else None,
    superseded_standard_occurrences=sorted(set(tank)&superseded),rotor_gaps=rotor_gaps,
    historical_station_qualified=False,installation_qualified=False,standard_assembly_modified=False))
assert all(v['passed'] for v in checks),'Preserve failures and diagnose without relaxing stock, bores or clearance.'
