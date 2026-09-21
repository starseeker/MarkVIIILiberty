"""Saved collar-joint fit, physical wire routing and STEP exchange checks."""
import argparse,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_collar_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/'TransmissionWithClutchCollar.FCStd';assert sha(native)==r['native_sha256']
    for path,h in r['input_hashes'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    s={}
    for n,i in byid.items():s[n]=i['shape'].copy();s[n].translate(-origin)
    c=r['controls'];dc=r['drive_controls'];d=r['details'];checks=[]
    def ck(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=passed))
        write(out/'check_progress.json',dict(last=name,completed=len(checks),failed=[x for x in checks if not x['passed']]))
    def zero(name,shape):ck(name,shape.Volume,0.0)
    def gap(name,a,b,want=0):ck(name,a.distToShape(b)[0],float(want))
    def shifted(shape,xyz):q=shape.copy();q.translate(App.Vector(*xyz));return q
    def xc(rad,a,b,y=0,z=0):return Part.makeCylinder(rad,b-a,App.Vector(a,y,z),App.Vector(1,0,0))
    def ids(i):return json.loads(getattr(i['object'],'SurveyIds',getattr(i['target'],'SurveyIds','[]')))
    records={row['record_id']:row for row in read(out/'inputs/clutch_collar_sources.json')['records']}
    expected=Counter()
    for rid,count in [('SNL:67:019',1),('SNL:43:014',1),('SNL:164:030',1),('SNL:200:002',6),('SNL:276:003',1)]:
        for pid in records[rid]['part_ids']:expected[pid]+=count
    ck('1540 unique physical leaves',len(byid),1540);ck('10 added physical occurrences',len(r['new_ids']),10)
    ck('20 affected valid single solids',all(s[n].isValid() and len(s[n].Solids)==1 for n in r['affected_ids']))
    ck('new source identity expansion',dict(Counter(pid for n in r['new_ids'] for pid in ids(byid[n]))),dict(expected))
    ck('all new pieces owned by drivetrain',all(byid[n]['system']=='Drivetrain' for n in r['new_ids']))
    ck('six screws reuse one definition',len({byid[f'ClutchCollar_Screw{n}']['target'].Name for n in range(1,7)}),1)
    coupling=s['FrontClutch_Coupling'];spring=s['FrontClutch_Spring'];shaft=s['ClutchDrive_shaft']
    upper=s['FrontClutch_UpperFlange'];lower=s['FrontClutch_LowerFlange'];collar=s['ClutchCollar_collar'];ring=s['ClutchCollar_ring'];bush=s['ClutchCollar_bush'];wire=s['ClutchCollar_wire']
    gap('moved spring seats on upper half',spring,upper);gap('moved spring seats on lower half',spring,lower)
    gap('moved spring seats on rear coupling flange',spring,coupling)
    gap('moved upper collar remains on shaft',upper,shaft);gap('moved lower collar remains on shaft',lower,shaft)
    ck('clamp retains four millimetres beyond old receiver',upper.BoundBox.XMin-s['ClutchDrive_box'].BoundBox.XMax,4.0)
    ground=[f for f in spring.Faces if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).x)>.999999]
    stations=sorted(f.CenterOfMass.x for f in ground)
    ck('external spring rear ground plane moved to627',stations[0],627.0);ck('external spring front ground plane moved to734.95',stations[-1],734.95)
    ck('external spring length retained',stations[-1]-stations[0],107.95)
    spine=Part.Shape();spine.read(str(out/'external_spring_spine.brep'));assert sha(out/'external_spring_spine.brep')==r['external_spring_spine_sha256']
    arr=np.array([[p.x,p.y,p.z] for p in spine.Edges[0].discretize(Number=1401)]);theta=np.unwrap(np.arctan2(arr[:,2],arr[:,1]))
    ck('shifted external spring still winds seven turns',float((theta[-1]-theta[0])/(2*math.pi)),7.0)
    ck('spring flange now aft of enlarged cardan shoulder',c['spring_seat']<dc['head_start']+dc['shaft_length']-dc['spline_length'])
    zero('rear spring flange retains solid annulus',xc(110,736,742).cut(xc(85,735,743)).cut(coupling))
    zero('forward collar flange has material beyond rear flange',xc(110,824,828).cut(xc(105,823,829)).cut(coupling))
    gap('revised female spline retains clearance',coupling,shaft,.15)
    turned=coupling.copy();turned.rotate(App.Vector(),App.Vector(1,0,0),1)
    ck('revised spline detects torque interference after clearance',turned.common(shaft).Volume>.01)
    gap('coupling and collar flange faces seat',coupling,collar)
    gap('end bush outer surface seats in coupling',bush,coupling)
    gap('end ring rear has an actual coupling stop',ring,coupling)
    gap('end ring front is captured by collar',ring,collar)
    gap('end bush front bears on ring shoulder',bush,ring)
    clip=xc(100,c['bearing_pocket_start']+5,c['ring_shoulder']-5)
    gap('end ring and bush cylindrical running gap',ring.common(clip),bush.common(clip),c['bush_running_gap'])
    gap('cardan tip clears end ring axially',shaft,ring,.2)
    ck('ring forward displacement catches collar',shifted(ring,[.2,0,0]).common(collar).Volume>.01)
    ck('ring rear displacement catches coupling stop',shifted(ring,[-.2,0,0]).common(coupling).Volume>.01)
    ck('bush forward displacement catches ring shoulder',shifted(bush,[.2,0,0]).common(ring).Volume>.01)
    zero('collar bore remains open for main internal stack',xc(52.64,c['joint_face']-.1,c['collar_front']+.1).common(collar))
    wire_spine=Part.Shape();wire_spine.read(str(out/'locking_wire_spine.brep'));assert sha(out/'locking_wire_spine.brep')==r['locking_wire_spine_sha256']
    ck('one continuous locking-wire centreline',len(wire_spine.Edges),1)
    ck('printed26in locking-wire cut length',wire_spine.Length,660.4,tol=1e-5)
    ck('wire is one open-ended physical solid',len(wire.Solids),1)
    endpoints=[v.Point for v in wire_spine.Vertexes];ck('paired twisted wire ends remain separate',len(endpoints),2)
    ck('paired end spacing matches two twist radii',(endpoints[0]-endpoints[-1]).Length,2*c['wire_twist_radius'],tol=1e-4)
    ck('wire retains round-section material volume',wire.Volume,math.pi*(c['wire_diameter']/2)**2*wire_spine.Length,tol=.05)
    for n in range(1,7):
        screw=s[f'ClutchCollar_Screw{n}'];theta=2*math.pi*(n-1)/6;y=c['bolt_circle']*math.cos(theta);z=c['bolt_circle']*math.sin(theta)
        under=c['joint_face']+c['collar_lip_stock'];x=under+c['bolt_head_height']/2
        point=App.Vector(x,y,z)
        gap(f'screw{n} head seats on collar',screw,collar)
        gap(f'screw{n} blind thread envelope gap',screw,coupling,c['thread_envelope_gap'])
        ck(f'screw{n} printed15.875 underhead length',screw.BoundBox.XLength-c['bolt_head_height'],15.875)
        ck(f'screw{n} has9.525 axial engagement',c['joint_face']-screw.BoundBox.XMin,9.525)
        ck(f'screw{n} wire passes through the actual head centre',wire.isInside(point,1e-5,True))
        ck(f'screw{n} head centre was drilled out',not screw.isInside(point,1e-5,True))
        zero(f'screw{n} routed wire clears head material',wire.common(screw))
        ck(f'screw{n} shifted wire detects head obstruction',shifted(wire,[.9,0,0]).common(screw).Volume>.001)
        bottom=under-c['bolt_length']-c['blind_tip_clearance']
        zero(f'screw{n} blind receiver retains solid bottom',xc(4.6,bottom-.5,bottom-.1,y,z).cut(coupling))
        zero(f'screw{n} blind receiver tip clearance',xc(4.6,bottom+.1,under-c['bolt_length']-.1,y,z).common(coupling))
        ck(f'screw{n} displaced head detects collar seat',shifted(screw,[-.2,0,0]).common(collar).Volume>.01)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__))))
    print('Independent',len(checks),'checks; failed',json.dumps([x for x in checks if not x['passed']]),flush=True)
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json');path=out/'ClutchCollarDefinitions.step';imported=Part.Shape();imported.read(str(path))
    assert sha(path)==r['definition_step_sha256'] and imported.isValid() and len(imported.Solids)==len(keys)
    remaining=list(imported.Solids);exchange=[]
    for key in keys:
        one=doc.getObject(key).Shape.Solids[0]
        idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length+abs(one.Volume-remaining[j].Volume)/max(one.Area,1))
        two=remaining.pop(idx);ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        rm=one.cut(two).Volume;ra=two.cut(one).Volume;missing=one.cut(two,fuzzy);added=two.cut(one,fuzzy)
        ma,mb=mass(one,key+'_native'),mass(two,key+'_step');dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        dcg=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;bound=(one.Area+two.Area)/2*(ta+tb)
        passed=rm<1e-5 and ra<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dcg<max(1e-6,ta+tb)
        exchange.append(dict(definition=key,passed=passed,raw_missing_mm3=rm,raw_added_mm3=ra,volume_difference_mm3=dv,
            centroid_difference_mm=dcg,surface_tolerance_bound_mm3=bound,native_tolerance=ta,step_tolerance=tb))
        write(out/'exchange_progress.json',dict(completed=len(exchange),last=key,failed=[x for x in exchange if not x['passed']]))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),checks=exchange,native_sha256=sha(native),step_sha256=sha(path),checker_sha256=sha(Path(__file__))))
    print('Definition STEP',len(exchange),'failed',json.dumps([x for x in exchange if not x['passed']]),flush=True)
    path=out/'ClutchCollarInstallation.step';assembly=Part.Shape();assembly.read(str(path))
    assert sha(path)==r['step_sha256'] and assembly.isValid() and len(assembly.Solids)==20
    remaining=list(assembly.Solids);placed=[]
    for n in r['step_ids']:
        one=byid[n]['shape'].Solids[0];idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length)
        two=remaining.pop(idx);ma,mb=mass(one,n+'_native'),mass(two,n+'_step')
        dcg=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placed.append(dict(id=n,passed=dcg<max(1e-6,one.getTolerance(1)+two.getTolerance(1)) and dv<bound,
            centroid_difference_mm=dcg,volume_difference_mm3=dv,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(x['passed'] for x in placed),checks=placed,native_sha256=sha(native),step_sha256=sha(path),
        scope='20affected placed solids:validity,count,mass and centroid;8definitions checked separately for geometry.',checker_sha256=sha(Path(__file__))))
    print('Placed STEP',len(placed),'failed',json.dumps([x for x in placed if not x['passed']]),flush=True)
    sys.exit(0 if all(x['passed'] for x in checks+exchange+placed) else 1)
finally:runtime.close()
